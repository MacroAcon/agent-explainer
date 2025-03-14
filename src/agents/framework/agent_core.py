from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

# Define agent states for structured state management
class AgentState(str, Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"

# Define agent roles for better organization
class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"
    INTERFACE = "interface"
    MONITOR = "monitor"

# Define memory types
class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    WORKING = "working"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

# Define structured memory entry
class MemoryEntry(BaseModel):
    id: str = Field(default_factory=lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest())
    content: Any
    memory_type: MemoryType
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ttl: Optional[int] = None  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if memory entry has expired based on TTL"""
        if self.ttl is None:
            return False
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl

# Define structured tool interface
class Tool(BaseModel):
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define structured conversation message
class Message(BaseModel):
    id: str = Field(default_factory=lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest())
    content: str
    role: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define structured conversation
class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest())
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_message(self, content: str, role: str, metadata: Dict[str, Any] = None) -> Message:
        """Add a message to the conversation"""
        metadata = metadata or {}
        message = Message(content=content, role=role, metadata=metadata)
        self.messages.append(message)
        return message
    
    def get_history(self, limit: Optional[int] = None) -> List[Message]:
        """Get conversation history with optional limit"""
        if limit is None:
            return self.messages
        return self.messages[-limit:]

# Core agent class with structured components
class StructuredAgent:
    """
    Core agent class implementing the structured agent architecture.
    This provides a consistent framework for all agents in the system.
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        system_message: str,
        config: Dict[str, Any] = None
    ):
        self.name = name
        self.role = role
        self.system_message = system_message
        self.config = config or {}
        
        # Initialize state
        self.state = AgentState.IDLE
        self.state_history = []
        
        # Initialize memory systems
        self.memories = {
            MemoryType.SHORT_TERM: [],
            MemoryType.WORKING: [],
            MemoryType.LONG_TERM: [],
            MemoryType.EPISODIC: [],
            MemoryType.SEMANTIC: []
        }
        
        # Initialize tools
        self.tools = {}
        
        # Initialize conversation
        self.conversation = Conversation()
        
        # Initialize metrics
        self.metrics = {
            "tasks_processed": 0,
            "errors": 0,
            "average_response_time": 0,
            "total_response_time": 0,
            "last_activity": datetime.now()
        }
    
    def add_tool(self, tool: Tool) -> None:
        """Register a tool with the agent"""
        self.tools[tool.name] = tool
    
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent"""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def add_memory(self, content: Any, memory_type: MemoryType, metadata: Dict[str, Any] = None, ttl: Optional[int] = None) -> MemoryEntry:
        """Add a memory entry to the specified memory system"""
        metadata = metadata or {}
        memory_entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            ttl=ttl
        )
        self.memories[memory_type].append(memory_entry)
        return memory_entry
    
    def get_memories(self, memory_type: MemoryType, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Get memories from the specified memory system with optional limit"""
        memories = [m for m in self.memories[memory_type] if not m.is_expired()]
        if limit is None:
            return memories
        return memories[-limit:]
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 5) -> List[MemoryEntry]:
        """Search memories based on a query string"""
        # This is a simple implementation - in a real system, you would use vector embeddings
        results = []
        memory_types = [memory_type] if memory_type else list(MemoryType)
        
        for mem_type in memory_types:
            for memory in self.memories[mem_type]:
                if not memory.is_expired() and query.lower() in str(memory.content).lower():
                    results.append(memory)
        
        # Sort by relevance (simple implementation)
        results.sort(key=lambda x: str(x.content).lower().count(query.lower()), reverse=True)
        return results[:limit]
    
    def update_state(self, new_state: AgentState) -> None:
        """Update agent state and record in history"""
        self.state_history.append((self.state, datetime.now()))
        self.state = new_state
        self.metrics["last_activity"] = datetime.now()
    
    async def process_message(self, message: str, metadata: Dict[str, Any] = None) -> str:
        """Process a message and return a response"""
        metadata = metadata or {}
        start_time = datetime.now()
        
        try:
            self.update_state(AgentState.PROCESSING)
            
            # Add message to conversation
            self.conversation.add_message(message, "user", metadata)
            
            # Process message (to be implemented by subclasses)
            response = await self._process_message_impl(message, metadata)
            
            # Add response to conversation
            self.conversation.add_message(response, "assistant", metadata)
            
            # Update metrics
            self.metrics["tasks_processed"] += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics["total_response_time"] += processing_time
            self.metrics["average_response_time"] = (
                self.metrics["total_response_time"] / self.metrics["tasks_processed"]
            )
            
            self.update_state(AgentState.IDLE)
            return response
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.update_state(AgentState.ERROR)
            error_response = f"Error processing message: {str(e)}"
            self.conversation.add_message(error_response, "system", {"error": str(e)})
            return error_response
    
    async def _process_message_impl(self, message: str, metadata: Dict[str, Any]) -> str:
        """Implementation of message processing (to be overridden by subclasses)"""
        raise NotImplementedError("Subclasses must implement _process_message_impl")
    
    def get_state_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get state transition history with timestamps"""
        history = [
            {"state": state.value, "timestamp": timestamp}
            for state, timestamp in self.state_history
        ]
        if limit is None:
            return history
        return history[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return self.metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization"""
        return {
            "name": self.name,
            "role": self.role.value,
            "state": self.state.value,
            "system_message": self.system_message,
            "metrics": self.metrics,
            "tools": [t.name for t in self.tools.values()],
            "memory_counts": {k.value: len(v) for k, v in self.memories.items()},
            "conversation_length": len(self.conversation.messages)
        } 