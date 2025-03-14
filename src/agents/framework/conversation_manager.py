from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid

# Setup logging
logger = logging.getLogger(__name__)

# Define conversation message types
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    ACTION = "action"
    SYSTEM = "system"
    ERROR = "error"

# Define conversation message roles
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"

# Define conversation states
class ConversationState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_SYSTEM = "waiting_for_system"

# Define structured message
class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: Any
    type: MessageType = MessageType.TEXT
    role: MessageRole
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value,
            "role": self.role.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

# Define conversation flow step
class ConversationStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    handler: Optional[Callable] = None
    next_steps: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

# Define conversation flow
class ConversationFlow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    steps: Dict[str, ConversationStep] = Field(default_factory=dict)
    initial_step: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_step(self, name: str, handler: Callable, description: str = "", next_steps: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Add a step to the conversation flow"""
        next_steps = next_steps or []
        metadata = metadata or {}
        
        step_id = str(uuid.uuid4())
        self.steps[step_id] = ConversationStep(
            id=step_id,
            name=name,
            description=description,
            handler=handler,
            next_steps=next_steps,
            metadata=metadata
        )
        
        # Set as initial step if none set
        if self.initial_step is None:
            self.initial_step = step_id
        
        return step_id
    
    def set_next_steps(self, step_id: str, next_steps: List[str]) -> None:
        """Set the next steps for a step"""
        if step_id in self.steps:
            self.steps[step_id].next_steps = next_steps
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": {
                step_id: {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "next_steps": step.next_steps,
                    "metadata": step.metadata
                }
                for step_id, step in self.steps.items()
            },
            "initial_step": self.initial_step,
            "metadata": self.metadata
        }

# Define conversation
class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ConversationMessage] = Field(default_factory=list)
    state: ConversationState = ConversationState.ACTIVE
    flow: Optional[ConversationFlow] = None
    current_step: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_message(
        self,
        content: Any,
        role: MessageRole,
        message_type: MessageType = MessageType.TEXT,
        metadata: Dict[str, Any] = None
    ) -> ConversationMessage:
        """Add a message to the conversation"""
        metadata = metadata or {}
        
        message = ConversationMessage(
            content=content,
            type=message_type,
            role=role,
            metadata=metadata
        )
        
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        return message
    
    def get_history(self, limit: Optional[int] = None, roles: Optional[List[MessageRole]] = None) -> List[ConversationMessage]:
        """Get conversation history with optional limit and role filtering"""
        messages = self.messages
        
        if roles:
            messages = [m for m in messages if m.role in roles]
        
        if limit is not None:
            messages = messages[-limit:]
        
        return messages
    
    def get_last_message(self, role: Optional[MessageRole] = None) -> Optional[ConversationMessage]:
        """Get the last message with optional role filtering"""
        messages = self.messages
        
        if role:
            messages = [m for m in messages if m.role == role]
        
        if not messages:
            return None
        
        return messages[-1]
    
    def update_state(self, new_state: ConversationState) -> None:
        """Update conversation state"""
        self.state = new_state
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for serialization"""
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
            "state": self.state.value,
            "flow": self.flow.to_dict() if self.flow else None,
            "current_step": self.current_step,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Conversation Manager for handling conversations
class ConversationManager:
    """Manager for handling conversations"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.flows: Dict[str, ConversationFlow] = {}
    
    def create_conversation(
        self,
        flow_id: Optional[str] = None,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Conversation:
        """Create a new conversation"""
        context = context or {}
        metadata = metadata or {}
        
        flow = None
        current_step = None
        
        if flow_id and flow_id in self.flows:
            flow = self.flows[flow_id]
            current_step = flow.initial_step
        
        conversation = Conversation(
            flow=flow,
            current_step=current_step,
            context=context,
            metadata=metadata
        )
        
        self.conversations[conversation.id] = conversation
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def register_flow(self, flow: ConversationFlow) -> None:
        """Register a conversation flow"""
        self.flows[flow.id] = flow
    
    def unregister_flow(self, flow_id: str) -> None:
        """Unregister a conversation flow"""
        if flow_id in self.flows:
            del self.flows[flow_id]
    
    async def process_message(
        self,
        conversation_id: str,
        content: Any,
        role: MessageRole = MessageRole.USER,
        message_type: MessageType = MessageType.TEXT,
        metadata: Dict[str, Any] = None
    ) -> Optional[ConversationMessage]:
        """Process a message in a conversation"""
        metadata = metadata or {}
        
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return None
        
        # Add message to conversation
        message = conversation.add_message(
            content=content,
            role=role,
            message_type=message_type,
            metadata=metadata
        )
        
        # If conversation has a flow, process it
        if conversation.flow and conversation.current_step:
            try:
                # Get current step
                step = conversation.flow.steps.get(conversation.current_step)
                if not step:
                    logger.error(f"Step {conversation.current_step} not found in flow {conversation.flow.id}")
                    return message
                
                # Update state
                conversation.update_state(ConversationState.ACTIVE)
                
                # Execute step handler
                if step.handler:
                    result = await step.handler(conversation, message)
                    
                    # Determine next step
                    if isinstance(result, str) and result in conversation.flow.steps:
                        # Explicit next step
                        conversation.current_step = result
                    elif step.next_steps:
                        # Default to first next step
                        conversation.current_step = step.next_steps[0]
                    else:
                        # No next steps, conversation is completed
                        conversation.update_state(ConversationState.COMPLETED)
                
            except Exception as e:
                logger.exception(f"Error processing message in conversation {conversation_id}")
                conversation.update_state(ConversationState.FAILED)
                conversation.add_message(
                    content=f"Error processing message: {str(e)}",
                    role=MessageRole.SYSTEM,
                    message_type=MessageType.ERROR,
                    metadata={"error": str(e)}
                )
        
        return message
    
    def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        return list(self.conversations.values())
    
    def get_active_conversations(self) -> List[Conversation]:
        """Get all active conversations"""
        return [c for c in self.conversations.values() if c.state == ConversationState.ACTIVE]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

# Utility functions for creating conversation flows
def create_linear_flow(
    name: str,
    steps: List[Dict[str, Any]],
    description: str = "",
    metadata: Dict[str, Any] = None
) -> ConversationFlow:
    """Create a linear conversation flow from a list of steps"""
    metadata = metadata or {}
    
    flow = ConversationFlow(
        name=name,
        description=description,
        metadata=metadata
    )
    
    step_ids = []
    for step in steps:
        step_id = flow.add_step(
            name=step["name"],
            handler=step["handler"],
            description=step.get("description", ""),
            metadata=step.get("metadata", {})
        )
        step_ids.append(step_id)
    
    # Connect steps linearly
    for i in range(len(step_ids) - 1):
        flow.set_next_steps(step_ids[i], [step_ids[i + 1]])
    
    return flow

def create_branching_flow(
    name: str,
    steps: Dict[str, Dict[str, Any]],
    connections: List[Dict[str, Any]],
    initial_step: str,
    description: str = "",
    metadata: Dict[str, Any] = None
) -> ConversationFlow:
    """Create a branching conversation flow from steps and connections"""
    metadata = metadata or {}
    
    flow = ConversationFlow(
        name=name,
        description=description,
        metadata=metadata
    )
    
    # Add steps
    step_ids = {}
    for step_name, step in steps.items():
        step_id = flow.add_step(
            name=step_name,
            handler=step["handler"],
            description=step.get("description", ""),
            metadata=step.get("metadata", {})
        )
        step_ids[step_name] = step_id
    
    # Add connections
    for connection in connections:
        from_step = connection["from"]
        to_steps = connection["to"]
        
        if from_step in step_ids:
            flow.set_next_steps(
                step_ids[from_step],
                [step_ids[to_step] for to_step in to_steps if to_step in step_ids]
            )
    
    # Set initial step
    if initial_step in step_ids:
        flow.initial_step = step_ids[initial_step]
    
    return flow 