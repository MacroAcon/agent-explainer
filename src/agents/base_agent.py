from typing import List, Dict, Any, Optional
from ag2 import SwarmAgent, UserProxyAgent, Memory, ToolChain
from ..config.config import settings
from ..config.enhanced_settings import enhanced_settings
import asyncio
from datetime import datetime, timedelta
import json
import hashlib

class BaseBusinessAgent(SwarmAgent):
    """Base agent class for business automation tasks with enhanced memory and performance."""
    
    def __init__(
        self,
        name: str,
        system_message: str,
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config={
                "model": settings.MODEL_NAME,
                "temperature": settings.TEMPERATURE,
                "api_key": settings.API_KEY,
            },
            **kwargs
        )
        
        # Initialize enhanced memory systems with compression and pruning
        self.long_term_memory = Memory(
            memory_type="long_term",
            capacity=enhanced_settings.memory.long_term_capacity,
            compression_strategy=enhanced_settings.memory.compression_strategy,
            pruning_threshold=enhanced_settings.memory.pruning_threshold
        )
        
        self.working_memory = Memory(
            memory_type="working",
            ttl=enhanced_settings.memory.working_memory_ttl
        )
        
        self.episodic_memory = Memory(
            memory_type="episodic",
            index_strategy="temporal",
            max_entries=enhanced_settings.memory.max_episodic_entries
        )
        
        # Initialize enhanced tool chain with parallel execution and caching
        self.tool_chain = ToolChain(
            validation_strategy="strict",
            error_handling="graceful",
            metrics_enabled=True,
            parallel_execution=enhanced_settings.performance.parallel_execution,
            result_caching=enhanced_settings.performance.result_caching,
            cache_ttl=enhanced_settings.performance.cache_ttl
        )
        
        # Initialize response cache
        self.response_cache = {}
        self.last_cleanup = datetime.now()
        
        if tools:
            self.register_tools(tools)
    
    def _compress_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress memory data using semantic compression."""
        if not enhanced_settings.memory.compression_strategy == "semantic":
            return data
            
        # Create semantic hash for deduplication
        content_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        # Store only essential information
        compressed_data = {
            "hash": content_hash,
            "timestamp": datetime.now().isoformat(),
            "type": data.get("type", "unknown"),
            "summary": self._generate_summary(data)
        }
        
        return compressed_data
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a semantic summary of the data."""
        # Implement semantic summarization logic here
        # This could use the LLM to generate concise summaries
        return str(data.get("content", ""))[:200] + "..."
    
    async def _cleanup_memory(self):
        """Clean up memory based on settings."""
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() < enhanced_settings.memory.memory_cleanup_interval:
            return
            
        # Clean up working memory
        await self.working_memory.cleanup()
        
        # Clean up episodic memory if over capacity
        if len(self.episodic_memory) > enhanced_settings.memory.max_episodic_entries:
            await self.episodic_memory.prune(
                keep_count=enhanced_settings.memory.max_episodic_entries
            )
        
        # Clean up response cache
        self._cleanup_response_cache()
        
        self.last_cleanup = now
    
    def _cleanup_response_cache(self):
        """Clean up expired response cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, (response, timestamp) in self.response_cache.items()
            if (now - timestamp).total_seconds() > enhanced_settings.performance.cache_ttl
        ]
        for key in expired_keys:
            del self.response_cache[key]
    
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a business task with enhanced performance and memory management."""
        try:
            # Initialize context if none provided
            context = context or {}
            
            # Add business info to context
            context.update({
                "business_name": settings.BUSINESS_NAME,
                "business_description": settings.BUSINESS_DESCRIPTION,
                "agent_name": self.name,
                "agent_role": self.__class__.__name__,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check response cache first
            cache_key = self._generate_cache_key(task, context)
            if cache_key in self.response_cache:
                cached_response, timestamp = self.response_cache[cache_key]
                if (datetime.now() - timestamp).total_seconds() <= enhanced_settings.performance.cache_ttl:
                    return cached_response
            
            # Create message for AG2 processing
            message = {
                "content": task,
                "context": context,
                "role": "user"
            }
            
            # Store in working memory with compression
            compressed_message = self._compress_memory(message)
            self.working_memory.add(compressed_message)
            
            # Check long-term memory for relevant past experiences
            relevant_memories = await self.long_term_memory.search(
                query=task,
                limit=5
            )
            
            if relevant_memories:
                context["relevant_history"] = relevant_memories
            
            # Generate response using AG2's processing
            response = await self.generate_response(message)
            
            # Format response for swarm coordinator
            formatted_response = {
                "agent": self.name,
                "role": self.__class__.__name__,
                "status": "completed",
                "response": response,
                "context": context,
                "timestamp": context["timestamp"],
                "memory_snapshot": await self.get_memory_snapshot()
            }
            
            # Cache the response
            self.response_cache[cache_key] = (formatted_response, datetime.now())
            
            # Store interaction in episodic memory with compression
            episodic_data = self._compress_memory({
                "task": task,
                "response": response,
                "context": context
            })
            self.episodic_memory.add(episodic_data)
            
            # Store important information in long-term memory with compression
            if self._should_store_long_term(response):
                long_term_data = self._compress_memory({
                    "knowledge": response,
                    "context": context,
                    "source": "task_processing"
                })
                self.long_term_memory.add(long_term_data)
            
            # Perform memory cleanup
            await self._cleanup_memory()
            
            return formatted_response
            
        except Exception as e:
            error_response = {
                "agent": self.name,
                "role": self.__class__.__name__,
                "status": "error",
                "error": str(e),
                "context": context,
                "timestamp": context.get("timestamp", datetime.now().isoformat())
            }
            return error_response
    
    def _generate_cache_key(self, task: str, context: Dict[str, Any]) -> str:
        """Generate a unique cache key for the task and context."""
        key_data = {
            "task": task,
            "context": {k: v for k, v in context.items() if k not in ["timestamp"]}
        }
        return hashlib.sha256(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
    
    async def get_memory_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of the agent's current memory state."""
        return {
            "working_memory": await self.working_memory.get_current_state(),
            "episodic_memory": await self.episodic_memory.get_recent(
                limit=5
            ),
            "long_term_memory": await self.long_term_memory.get_summary(),
            "cache_size": len(self.response_cache)
        }
    
    def _should_store_long_term(self, response: str) -> bool:
        """Determine if response should be stored in long-term memory."""
        importance_factors = [
            len(response) > 100,  # Complex enough to be worth storing
            "important" in response.lower(),
            "remember" in response.lower(),
            "critical" in response.lower(),
            "policy" in response.lower(),
            "procedure" in response.lower()
        ]
        return any(importance_factors)
    
    async def generate_response(self, message: Dict[str, Any]) -> str:
        """Generate a response using AG2's processing capabilities."""
        raise NotImplementedError("Subclasses must implement generate_response()") 