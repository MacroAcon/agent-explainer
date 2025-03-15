from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class BaseBusinessAgent:
    """Base class for all business agents"""
    
    def __init__(self, name: str, system_message: str = None, tools: List[Dict[str, Any]] = None):
        self.name = name
        self.system_message = system_message or "I am a business agent."
        self.tools = tools or []
        self.memory: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}
        
    def add_memory(self, content: str, memory_type: str = "general", metadata: Dict[str, Any] = None):
        """Add an item to agent's memory"""
        memory_item = {
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "type": memory_type,
            "metadata": metadata or {}
        }
        self.memory.append(memory_item)
        
    def get_memories(self, memory_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories, optionally filtered by type"""
        if memory_type:
            filtered = [m for m in self.memory if m["type"] == memory_type]
        else:
            filtered = self.memory
        
        return sorted(filtered, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def update_state(self, key: str, value: Any):
        """Update agent's state"""
        self.state[key] = value
        self.add_memory(
            f"State updated: {key} = {value}",
            memory_type="state_change",
            metadata={"key": key, "value": value}
        )
    
    def get_state(self, key: str) -> Any:
        """Get value from agent's state"""
        return self.state.get(key)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        try:
            result = await tool["func"](self, **kwargs)
            self.add_memory(
                f"Executed tool: {tool_name}",
                memory_type="tool_execution",
                metadata={"tool": tool_name, "result": result}
            )
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

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