from typing import Dict, List, Any, Optional, Union, Callable, Type
import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from collections import defaultdict

from .agent_core import StructuredAgent, AgentRole, AgentState, MemoryType
from .tool_framework import ToolRegistry
from .conversation_manager import ConversationManager, MessageRole, MessageType
from .monitoring import MonitoringSystem, EventType, EventSeverity, log_agent_activity, record_response_time, record_task_completion, record_error

# Setup logging
logger = logging.getLogger(__name__)

# Define task priority
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Define task status
class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Define structured task
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def update_status(self, status: TaskStatus) -> None:
        """Update task status and timestamp"""
        self.status = status
        self.updated_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dependencies": self.dependencies,
            "data": self.data,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }

# Define agent capability
class AgentCapability(BaseModel):
    name: str
    description: str
    score: float = 1.0  # 0.0 to 1.0, higher is better
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Agent Coordinator
class AgentCoordinator:
    """Coordinator for managing and coordinating multiple agents"""
    
    def __init__(
        self,
        name: str,
        tool_registry: Optional[ToolRegistry] = None,
        conversation_manager: Optional[ConversationManager] = None,
        monitoring_system: Optional[MonitoringSystem] = None
    ):
        self.name = name
        self.agents: Dict[str, StructuredAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = defaultdict(list)
        
        # Initialize supporting systems
        self.tool_registry = tool_registry or ToolRegistry()
        self.conversation_manager = conversation_manager or ConversationManager()
        self.monitoring_system = monitoring_system or MonitoringSystem()
        
        # Initialize task queues by priority
        self.task_queues: Dict[TaskPriority, List[str]] = {
            priority: [] for priority in TaskPriority
        }
        
        # Initialize dependency tracking
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)  # task_id -> [dependent_task_ids]
        
        # Initialize agent load tracking
        self.agent_loads: Dict[str, int] = {}  # agent_id -> current task count
    
    def register_agent(self, agent: StructuredAgent, capabilities: List[AgentCapability] = None) -> None:
        """Register an agent with the coordinator"""
        if agent.name in self.agents:
            logger.warning(f"Agent {agent.name} already registered, overwriting")
        
        self.agents[agent.name] = agent
        self.agent_loads[agent.name] = 0
        
        # Register capabilities
        if capabilities:
            self.agent_capabilities[agent.name] = capabilities
        
        # Log agent registration
        if self.monitoring_system:
            self.monitoring_system.record_event(
                event_type=EventType.AGENT_CREATED,
                source=f"coordinator:{self.name}",
                data={
                    "agent_name": agent.name,
                    "agent_role": agent.role.value,
                    "capabilities_count": len(capabilities) if capabilities else 0
                }
            )
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent from the coordinator"""
        if agent_name in self.agents:
            # Reassign tasks
            self._reassign_agent_tasks(agent_name)
            
            # Remove agent
            del self.agents[agent_name]
            del self.agent_loads[agent_name]
            
            if agent_name in self.agent_capabilities:
                del self.agent_capabilities[agent_name]
            
            # Log agent unregistration
            if self.monitoring_system:
                self.monitoring_system.record_event(
                    event_type=EventType.AGENT_DESTROYED,
                    source=f"coordinator:{self.name}",
                    data={"agent_name": agent_name}
                )
            
            return True
        
        return False
    
    def _reassign_agent_tasks(self, agent_name: str) -> None:
        """Reassign tasks from an agent being unregistered"""
        for task_id, task in self.tasks.items():
            if task.assigned_agent == agent_name and task.status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
                # Reset task to pending
                task.update_status(TaskStatus.PENDING)
                task.assigned_agent = None
                
                # Add back to queue
                if task_id not in self.task_queues[task.priority]:
                    self.task_queues[task.priority].append(task_id)
    
    def register_agent_capability(self, agent_name: str, capability: AgentCapability) -> bool:
        """Register a capability for an agent"""
        if agent_name not in self.agents:
            return False
        
        self.agent_capabilities[agent_name].append(capability)
        return True
    
    def create_task(
        self,
        name: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: List[str] = None,
        data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> Task:
        """Create a new task"""
        dependencies = dependencies or []
        data = data or {}
        metadata = metadata or {}
        
        task = Task(
            name=name,
            description=description,
            priority=priority,
            dependencies=dependencies,
            data=data,
            metadata=metadata
        )
        
        self.tasks[task.id] = task
        
        # Add to task queue if no dependencies or all dependencies are completed
        if not dependencies or all(
            self.tasks.get(dep_id, Task(id=dep_id, name="", description="")).status == TaskStatus.COMPLETED
            for dep_id in dependencies
        ):
            self.task_queues[priority].append(task.id)
        else:
            # Update dependency graph
            for dep_id in dependencies:
                self.dependency_graph[dep_id].append(task.id)
        
        # Log task creation
        if self.monitoring_system:
            self.monitoring_system.record_event(
                event_type=EventType.TASK_STARTED,
                source=f"coordinator:{self.name}",
                data={
                    "task_id": task.id,
                    "task_name": task.name,
                    "priority": priority.value,
                    "dependencies_count": len(dependencies)
                }
            )
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None) -> bool:
        """Update task status"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        old_status = task.status
        task.update_status(status)
        
        if result is not None:
            task.result = result
        
        if error is not None:
            task.error = error
        
        # If task is completed or failed, update agent load and process dependencies
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            if task.assigned_agent and task.assigned_agent in self.agent_loads:
                self.agent_loads[task.assigned_agent] = max(0, self.agent_loads[task.assigned_agent] - 1)
            
            # Process dependent tasks
            if status == TaskStatus.COMPLETED:
                self._process_dependent_tasks(task_id)
            
            # Log task completion
            if self.monitoring_system:
                event_type = EventType.TASK_COMPLETED if status == TaskStatus.COMPLETED else EventType.TASK_FAILED
                self.monitoring_system.record_event(
                    event_type=event_type,
                    source=f"coordinator:{self.name}",
                    data={
                        "task_id": task_id,
                        "task_name": task.name,
                        "agent": task.assigned_agent,
                        "error": error
                    }
                )
                
                if task.assigned_agent:
                    record_task_completion(
                        self.monitoring_system,
                        task.assigned_agent,
                        task_id,
                        status == TaskStatus.COMPLETED
                    )
        
        # If task is cancelled, add back to queue
        elif old_status in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS] and status == TaskStatus.PENDING:
            if task.assigned_agent and task.assigned_agent in self.agent_loads:
                self.agent_loads[task.assigned_agent] = max(0, self.agent_loads[task.assigned_agent] - 1)
            
            task.assigned_agent = None
            
            if task_id not in self.task_queues[task.priority]:
                self.task_queues[task.priority].append(task_id)
        
        return True
    
    def _process_dependent_tasks(self, completed_task_id: str) -> None:
        """Process tasks that depend on a completed task"""
        dependent_task_ids = self.dependency_graph.get(completed_task_id, [])
        
        for task_id in dependent_task_ids:
            task = self.get_task(task_id)
            if not task:
                continue
            
            # Check if all dependencies are completed
            all_deps_completed = True
            for dep_id in task.dependencies:
                dep_task = self.get_task(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            
            # If all dependencies are completed, add to queue
            if all_deps_completed and task.status == TaskStatus.PENDING:
                if task_id not in self.task_queues[task.priority]:
                    self.task_queues[task.priority].append(task_id)
    
    def assign_tasks(self) -> int:
        """Assign pending tasks to available agents"""
        assigned_count = 0
        
        # Process tasks in priority order
        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.MEDIUM, TaskPriority.LOW]:
            # Get pending tasks for this priority
            task_ids = self.task_queues[priority].copy()
            
            for task_id in task_ids:
                task = self.get_task(task_id)
                if not task or task.status != TaskStatus.PENDING:
                    # Remove from queue if not pending
                    if task_id in self.task_queues[priority]:
                        self.task_queues[priority].remove(task_id)
                    continue
                
                # Find best agent for task
                agent_name = self._find_best_agent_for_task(task)
                if not agent_name:
                    continue  # No suitable agent found
                
                # Assign task to agent
                task.assigned_agent = agent_name
                task.update_status(TaskStatus.ASSIGNED)
                
                # Update agent load
                self.agent_loads[agent_name] += 1
                
                # Remove from queue
                self.task_queues[priority].remove(task_id)
                
                assigned_count += 1
                
                # Log task assignment
                if self.monitoring_system:
                    log_agent_activity(
                        self.monitoring_system,
                        agent_name,
                        "task_assigned",
                        {"task_id": task_id, "task_name": task.name}
                    )
        
        return assigned_count
    
    def _find_best_agent_for_task(self, task: Task) -> Optional[str]:
        """Find the best agent for a task based on capabilities and load"""
        best_agent = None
        best_score = -1
        
        for agent_name, agent in self.agents.items():
            # Skip agents that are not idle
            if agent.state != AgentState.IDLE:
                continue
            
            # Calculate capability score
            capability_score = self._calculate_capability_score(agent_name, task)
            
            # Calculate load score (inverse of current load)
            max_load = 5  # Maximum reasonable load
            current_load = self.agent_loads.get(agent_name, 0)
            load_score = 1.0 - (current_load / max_load)
            load_score = max(0.1, load_score)  # Ensure minimum score
            
            # Calculate combined score
            combined_score = capability_score * load_score
            
            # Update best agent if this one is better
            if combined_score > best_score:
                best_agent = agent_name
                best_score = combined_score
        
        return best_agent
    
    def _calculate_capability_score(self, agent_name: str, task: Task) -> float:
        """Calculate how well an agent's capabilities match a task"""
        if agent_name not in self.agent_capabilities:
            return 0.5  # Default score if no capabilities defined
        
        # Extract keywords from task
        keywords = set()
        keywords.update(task.name.lower().split())
        keywords.update(task.description.lower().split())
        
        # Calculate match score
        total_score = 0
        max_score = 0
        
        for capability in self.agent_capabilities[agent_name]:
            # Calculate keyword match
            capability_keywords = set()
            capability_keywords.update(capability.name.lower().split())
            capability_keywords.update(capability.description.lower().split())
            
            # Count matching keywords
            matching_keywords = keywords.intersection(capability_keywords)
            match_ratio = len(matching_keywords) / max(1, len(keywords))
            
            # Calculate weighted score
            score = match_ratio * capability.score
            total_score += score
            max_score += capability.score
        
        # Normalize score
        if max_score > 0:
            return total_score / max_score
        return 0.5  # Default score
    
    async def process_tasks(self) -> Dict[str, Any]:
        """Process assigned tasks with agents"""
        results = {
            "processed": 0,
            "completed": 0,
            "failed": 0,
            "details": []
        }
        
        # Find tasks that are assigned but not yet in progress
        assigned_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.ASSIGNED and task.assigned_agent
        ]
        
        for task in assigned_tasks:
            agent_name = task.assigned_agent
            agent = self.agents.get(agent_name)
            
            if not agent:
                # Agent no longer exists, reset task
                task.update_status(TaskStatus.PENDING)
                task.assigned_agent = None
                if task.id not in self.task_queues[task.priority]:
                    self.task_queues[task.priority].append(task.id)
                continue
            
            # Update task status
            task.update_status(TaskStatus.IN_PROGRESS)
            
            # Process task with agent
            try:
                start_time = datetime.now()
                
                # Create message for agent
                message = json.dumps({
                    "task_id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "data": task.data
                })
                
                # Process message with agent
                response = await agent.process_message(message, {"task_id": task.id})
                
                # Parse response
                try:
                    result = json.loads(response)
                except json.JSONDecodeError:
                    result = {"response": response}
                
                # Update task as completed
                task.update_status(TaskStatus.COMPLETED)
                task.result = result
                
                # Record metrics
                if self.monitoring_system:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    record_response_time(self.monitoring_system, agent_name, processing_time)
                
                results["processed"] += 1
                results["completed"] += 1
                results["details"].append({
                    "task_id": task.id,
                    "agent": agent_name,
                    "status": "completed",
                    "processing_time": (datetime.now() - start_time).total_seconds()
                })
                
            except Exception as e:
                logger.exception(f"Error processing task {task.id} with agent {agent_name}")
                
                # Update task as failed
                task.update_status(TaskStatus.FAILED)
                task.error = str(e)
                
                # Record error
                if self.monitoring_system:
                    record_error(
                        self.monitoring_system,
                        f"agent:{agent_name}",
                        f"Error processing task {task.id}: {str(e)}"
                    )
                
                results["processed"] += 1
                results["failed"] += 1
                results["details"].append({
                    "task_id": task.id,
                    "agent": agent_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        status = {}
        
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                "state": agent.state.value,
                "role": agent.role.value,
                "current_load": self.agent_loads.get(agent_name, 0),
                "capabilities_count": len(self.agent_capabilities.get(agent_name, [])),
                "metrics": agent.get_metrics()
            }
        
        return status
    
    def get_task_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        status = {}
        
        for task_id, task in self.tasks.items():
            status[task_id] = {
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.value,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "dependencies_count": len(task.dependencies),
                "has_result": task.result is not None,
                "has_error": task.error is not None
            }
        
        return status
    
    def get_queue_status(self) -> Dict[str, List[str]]:
        """Get status of task queues"""
        return {priority.value: queue.copy() for priority, queue in self.task_queues.items()}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert coordinator to dictionary for serialization"""
        return {
            "name": self.name,
            "agents_count": len(self.agents),
            "tasks_count": len(self.tasks),
            "pending_tasks": sum(len(queue) for queue in self.task_queues.values()),
            "agent_capabilities": {
                agent_name: [cap.name for cap in capabilities]
                for agent_name, capabilities in self.agent_capabilities.items()
            }
        }

# Factory for creating agent coordinators
class AgentCoordinatorFactory:
    """Factory for creating and managing agent coordinators"""
    
    _instances: Dict[str, AgentCoordinator] = {}
    
    @classmethod
    def create_coordinator(
        cls,
        name: str,
        tool_registry: Optional[ToolRegistry] = None,
        conversation_manager: Optional[ConversationManager] = None,
        monitoring_system: Optional[MonitoringSystem] = None
    ) -> AgentCoordinator:
        """Create a new agent coordinator"""
        if name in cls._instances:
            logger.warning(f"Coordinator {name} already exists, returning existing instance")
            return cls._instances[name]
        
        coordinator = AgentCoordinator(
            name=name,
            tool_registry=tool_registry,
            conversation_manager=conversation_manager,
            monitoring_system=monitoring_system
        )
        
        cls._instances[name] = coordinator
        return coordinator
    
    @classmethod
    def get_coordinator(cls, name: str) -> Optional[AgentCoordinator]:
        """Get an existing coordinator by name"""
        return cls._instances.get(name)
    
    @classmethod
    def delete_coordinator(cls, name: str) -> bool:
        """Delete a coordinator"""
        if name in cls._instances:
            del cls._instances[name]
            return True
        return False
    
    @classmethod
    def get_all_coordinators(cls) -> Dict[str, AgentCoordinator]:
        """Get all coordinators"""
        return cls._instances.copy() 