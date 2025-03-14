from typing import Dict, List, Any, Optional, Union, Callable
import json
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .agent_core import StructuredAgent, AgentRole, AgentState
from .agent_coordinator import AgentCoordinator, Task, TaskStatus, TaskPriority
from .tool_framework import ToolRegistry, Tool, ToolCategory
from .monitoring import MonitoringSystem, EventType, EventSeverity

# Setup logging
logger = logging.getLogger(__name__)

# Define node types for visualization
class NodeType(str, Enum):
    AGENT = "agent"
    TASK = "task"
    TOOL = "tool"
    CONVERSATION = "conversation"
    MEMORY = "memory"
    EVENT = "event"
    METRIC = "metric"
    SYSTEM = "system"

# Define edge types for visualization
class EdgeType(str, Enum):
    ASSIGNMENT = "assignment"  # Agent to Task
    DEPENDENCY = "dependency"  # Task to Task
    USES = "uses"  # Agent to Tool
    COMMUNICATES = "communicates"  # Agent to Agent
    MONITORS = "monitors"  # System to Agent/Task
    CONTAINS = "contains"  # System to Agent/Task/Tool
    CUSTOM = "custom"

# Define visualization node
class VisualizationNode(BaseModel):
    id: str
    type: NodeType
    label: str
    data: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=dict)
    style: Dict[str, Any] = Field(default_factory=dict)

# Define visualization edge
class VisualizationEdge(BaseModel):
    id: str
    source: str
    target: str
    type: EdgeType
    label: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    style: Dict[str, Any] = Field(default_factory=dict)

# Define visualization graph
class VisualizationGraph(BaseModel):
    nodes: List[VisualizationNode] = Field(default_factory=list)
    edges: List[VisualizationEdge] = Field(default_factory=list)
    
    def add_node(
        self,
        id: str,
        type: NodeType,
        label: str,
        data: Dict[str, Any] = None,
        position: Dict[str, float] = None,
        style: Dict[str, Any] = None
    ) -> VisualizationNode:
        """Add a node to the graph"""
        data = data or {}
        position = position or {}
        style = style or {}
        
        node = VisualizationNode(
            id=id,
            type=type,
            label=label,
            data=data,
            position=position,
            style=style
        )
        
        self.nodes.append(node)
        return node
    
    def add_edge(
        self,
        source: str,
        target: str,
        type: EdgeType,
        label: Optional[str] = None,
        data: Dict[str, Any] = None,
        style: Dict[str, Any] = None
    ) -> VisualizationEdge:
        """Add an edge to the graph"""
        data = data or {}
        style = style or {}
        
        edge_id = f"{source}-{target}-{type.value}"
        
        edge = VisualizationEdge(
            id=edge_id,
            source=source,
            target=target,
            type=type,
            label=label,
            data=data,
            style=style
        )
        
        self.edges.append(edge)
        return edge
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization"""
        return {
            "nodes": [node.dict() for node in self.nodes],
            "edges": [edge.dict() for edge in self.edges]
        }
    
    def to_json(self) -> str:
        """Convert graph to JSON for visualization"""
        return json.dumps(self.to_dict())

# Visualization adapter for agent system
class VisualizationAdapter:
    """Adapter for visualizing agent system components"""
    
    def __init__(
        self,
        coordinator: Optional[AgentCoordinator] = None,
        tool_registry: Optional[ToolRegistry] = None,
        monitoring_system: Optional[MonitoringSystem] = None
    ):
        self.coordinator = coordinator
        self.tool_registry = tool_registry
        self.monitoring_system = monitoring_system
    
    def generate_agent_graph(self) -> VisualizationGraph:
        """Generate a graph of agents and their relationships"""
        if not self.coordinator:
            return VisualizationGraph()
        
        graph = VisualizationGraph()
        
        # Add coordinator node
        graph.add_node(
            id=f"coordinator:{self.coordinator.name}",
            type=NodeType.SYSTEM,
            label=f"Coordinator: {self.coordinator.name}",
            data={
                "type": "coordinator",
                "name": self.coordinator.name,
                "agents_count": len(self.coordinator.agents),
                "tasks_count": len(self.coordinator.tasks)
            },
            style={
                "backgroundColor": "#f0f0f0",
                "borderColor": "#000000",
                "borderWidth": 2,
                "width": 200,
                "height": 100
            }
        )
        
        # Add agent nodes
        for agent_name, agent in self.coordinator.agents.items():
            node_id = f"agent:{agent_name}"
            
            # Determine node style based on agent state
            style = {
                "width": 150,
                "height": 80,
                "borderWidth": 2
            }
            
            if agent.state == AgentState.IDLE:
                style["backgroundColor"] = "#e6f7ff"
                style["borderColor"] = "#1890ff"
            elif agent.state == AgentState.PROCESSING:
                style["backgroundColor"] = "#fff7e6"
                style["borderColor"] = "#fa8c16"
            elif agent.state == AgentState.ERROR:
                style["backgroundColor"] = "#fff1f0"
                style["borderColor"] = "#f5222d"
            else:
                style["backgroundColor"] = "#f9f0ff"
                style["borderColor"] = "#722ed1"
            
            graph.add_node(
                id=node_id,
                type=NodeType.AGENT,
                label=agent_name,
                data={
                    "name": agent_name,
                    "role": agent.role.value,
                    "state": agent.state.value,
                    "metrics": agent.get_metrics(),
                    "capabilities": [
                        cap.name for cap in self.coordinator.agent_capabilities.get(agent_name, [])
                    ]
                },
                style=style
            )
            
            # Add edge from coordinator to agent
            graph.add_edge(
                source=f"coordinator:{self.coordinator.name}",
                target=node_id,
                type=EdgeType.CONTAINS,
                label="manages"
            )
        
        # Add task nodes and assignment edges
        for task_id, task in self.coordinator.tasks.items():
            node_id = f"task:{task_id}"
            
            # Determine node style based on task status
            style = {
                "width": 120,
                "height": 60,
                "borderWidth": 1
            }
            
            if task.status == TaskStatus.PENDING:
                style["backgroundColor"] = "#f5f5f5"
                style["borderColor"] = "#d9d9d9"
            elif task.status == TaskStatus.ASSIGNED:
                style["backgroundColor"] = "#e6f7ff"
                style["borderColor"] = "#1890ff"
            elif task.status == TaskStatus.IN_PROGRESS:
                style["backgroundColor"] = "#fff7e6"
                style["borderColor"] = "#fa8c16"
            elif task.status == TaskStatus.COMPLETED:
                style["backgroundColor"] = "#f6ffed"
                style["borderColor"] = "#52c41a"
            elif task.status == TaskStatus.FAILED:
                style["backgroundColor"] = "#fff1f0"
                style["borderColor"] = "#f5222d"
            else:
                style["backgroundColor"] = "#f9f0ff"
                style["borderColor"] = "#722ed1"
            
            graph.add_node(
                id=node_id,
                type=NodeType.TASK,
                label=task.name,
                data={
                    "id": task_id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "assigned_agent": task.assigned_agent,
                    "created_at": task.created_at.isoformat(),
                    "dependencies": task.dependencies
                },
                style=style
            )
            
            # Add edge from coordinator to task
            graph.add_edge(
                source=f"coordinator:{self.coordinator.name}",
                target=node_id,
                type=EdgeType.CONTAINS,
                label="manages"
            )
            
            # Add assignment edge if task is assigned
            if task.assigned_agent:
                graph.add_edge(
                    source=f"agent:{task.assigned_agent}",
                    target=node_id,
                    type=EdgeType.ASSIGNMENT,
                    label="assigned to"
                )
            
            # Add dependency edges
            for dep_id in task.dependencies:
                graph.add_edge(
                    source=f"task:{dep_id}",
                    target=node_id,
                    type=EdgeType.DEPENDENCY,
                    label="depends on"
                )
        
        return graph
    
    def generate_tool_graph(self) -> VisualizationGraph:
        """Generate a graph of tools and their relationships"""
        if not self.tool_registry:
            return VisualizationGraph()
        
        graph = VisualizationGraph()
        
        # Add tool registry node
        graph.add_node(
            id="tool_registry",
            type=NodeType.SYSTEM,
            label="Tool Registry",
            data={
                "type": "tool_registry",
                "tools_count": len(self.tool_registry.get_all_tools())
            },
            style={
                "backgroundColor": "#f0f0f0",
                "borderColor": "#000000",
                "borderWidth": 2,
                "width": 150,
                "height": 80
            }
        )
        
        # Add category nodes
        for category in ToolCategory:
            category_id = f"category:{category.value}"
            
            graph.add_node(
                id=category_id,
                type=NodeType.SYSTEM,
                label=f"Category: {category.value}",
                data={
                    "type": "tool_category",
                    "category": category.value
                },
                style={
                    "backgroundColor": "#f9f0ff",
                    "borderColor": "#722ed1",
                    "borderWidth": 1,
                    "width": 120,
                    "height": 60
                }
            )
            
            # Add edge from registry to category
            graph.add_edge(
                source="tool_registry",
                target=category_id,
                type=EdgeType.CONTAINS,
                label="contains"
            )
        
        # Add tool nodes
        for tool in self.tool_registry.get_all_tools():
            tool_id = f"tool:{tool.name}"
            category_id = f"category:{tool.category.value}"
            
            graph.add_node(
                id=tool_id,
                type=NodeType.TOOL,
                label=tool.name,
                data={
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category.value,
                    "parameters_count": len(tool.parameters),
                    "required_permissions": tool.required_permissions
                },
                style={
                    "backgroundColor": "#e6f7ff",
                    "borderColor": "#1890ff",
                    "borderWidth": 1,
                    "width": 100,
                    "height": 50
                }
            )
            
            # Add edge from category to tool
            graph.add_edge(
                source=category_id,
                target=tool_id,
                type=EdgeType.CONTAINS,
                label="contains"
            )
            
            # Add edges from agents to tools if coordinator is available
            if self.coordinator:
                for agent_name, agent in self.coordinator.agents.items():
                    if tool.name in agent.tools:
                        graph.add_edge(
                            source=f"agent:{agent_name}",
                            target=tool_id,
                            type=EdgeType.USES,
                            label="uses"
                        )
        
        return graph
    
    def generate_monitoring_graph(self) -> VisualizationGraph:
        """Generate a graph of monitoring events and metrics"""
        if not self.monitoring_system:
            return VisualizationGraph()
        
        graph = VisualizationGraph()
        
        # Add monitoring system node
        graph.add_node(
            id="monitoring_system",
            type=NodeType.SYSTEM,
            label="Monitoring System",
            data={
                "type": "monitoring_system",
                "events_count": len(self.monitoring_system.events),
                "metrics_count": sum(len(m) for m in self.monitoring_system.metrics.values())
            },
            style={
                "backgroundColor": "#f0f0f0",
                "borderColor": "#000000",
                "borderWidth": 2,
                "width": 150,
                "height": 80
            }
        )
        
        # Add event type nodes
        for event_type in EventType:
            event_type_id = f"event_type:{event_type.value}"
            
            graph.add_node(
                id=event_type_id,
                type=NodeType.SYSTEM,
                label=f"Event: {event_type.value}",
                data={
                    "type": "event_type",
                    "event_type": event_type.value
                },
                style={
                    "backgroundColor": "#fff7e6",
                    "borderColor": "#fa8c16",
                    "borderWidth": 1,
                    "width": 120,
                    "height": 60
                }
            )
            
            # Add edge from monitoring system to event type
            graph.add_edge(
                source="monitoring_system",
                target=event_type_id,
                type=EdgeType.CONTAINS,
                label="tracks"
            )
        
        # Add recent events (limit to 10)
        events = list(self.monitoring_system.events)[-10:]
        
        for i, event in enumerate(events):
            event_id = f"event:{event.id}"
            event_type_id = f"event_type:{event.type.value}"
            
            # Determine style based on severity
            style = {
                "width": 100,
                "height": 50,
                "borderWidth": 1
            }
            
            if event.severity == EventSeverity.INFO:
                style["backgroundColor"] = "#e6f7ff"
                style["borderColor"] = "#1890ff"
            elif event.severity == EventSeverity.WARNING:
                style["backgroundColor"] = "#fff7e6"
                style["borderColor"] = "#fa8c16"
            elif event.severity == EventSeverity.ERROR:
                style["backgroundColor"] = "#fff1f0"
                style["borderColor"] = "#f5222d"
            elif event.severity == EventSeverity.CRITICAL:
                style["backgroundColor"] = "#ff4d4f"
                style["borderColor"] = "#a8071a"
                style["borderWidth"] = 2
            else:
                style["backgroundColor"] = "#f9f0ff"
                style["borderColor"] = "#722ed1"
            
            graph.add_node(
                id=event_id,
                type=NodeType.EVENT,
                label=f"Event: {event.type.value}",
                data={
                    "id": event.id,
                    "type": event.type.value,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "data": event.data
                },
                style=style
            )
            
            # Add edge from event type to event
            graph.add_edge(
                source=event_type_id,
                target=event_id,
                type=EdgeType.CONTAINS,
                label="instance"
            )
            
            # Add edge from source to event if source is an agent or task
            source = event.source
            if source.startswith("agent:") and self.coordinator:
                agent_name = source.split(":", 1)[1]
                if agent_name in self.coordinator.agents:
                    graph.add_edge(
                        source=f"agent:{agent_name}",
                        target=event_id,
                        type=EdgeType.CUSTOM,
                        label="generated"
                    )
        
        # Add aggregated metrics
        for name, metric_data in self.monitoring_system.aggregated_metrics.items():
            metric_id = f"metric:{name}"
            
            graph.add_node(
                id=metric_id,
                type=NodeType.METRIC,
                label=f"Metric: {name}",
                data={
                    "name": name,
                    "value": metric_data.get("value"),
                    "timestamp": metric_data.get("timestamp"),
                    "window": metric_data.get("window"),
                    "metric_count": metric_data.get("metric_count")
                },
                style={
                    "backgroundColor": "#f6ffed",
                    "borderColor": "#52c41a",
                    "borderWidth": 1,
                    "width": 100,
                    "height": 50
                }
            )
            
            # Add edge from monitoring system to metric
            graph.add_edge(
                source="monitoring_system",
                target=metric_id,
                type=EdgeType.CONTAINS,
                label="tracks"
            )
        
        return graph
    
    def generate_complete_graph(self) -> VisualizationGraph:
        """Generate a complete graph of the agent system"""
        # Start with agent graph
        graph = self.generate_agent_graph()
        
        # Add tool graph
        tool_graph = self.generate_tool_graph()
        graph.nodes.extend(tool_graph.nodes)
        graph.edges.extend(tool_graph.edges)
        
        # Add monitoring graph
        monitoring_graph = self.generate_monitoring_graph()
        graph.nodes.extend(monitoring_graph.nodes)
        graph.edges.extend(monitoring_graph.edges)
        
        return graph
    
    def generate_agent_details(self, agent_name: str) -> Dict[str, Any]:
        """Generate detailed information about an agent for visualization"""
        if not self.coordinator or agent_name not in self.coordinator.agents:
            return {}
        
        agent = self.coordinator.agents[agent_name]
        
        # Get assigned tasks
        assigned_tasks = [
            task.to_dict() for task in self.coordinator.tasks.values()
            if task.assigned_agent == agent_name
        ]
        
        # Get agent capabilities
        capabilities = [
            {
                "name": cap.name,
                "description": cap.description,
                "score": cap.score
            }
            for cap in self.coordinator.agent_capabilities.get(agent_name, [])
        ]
        
        # Get agent tools
        tools = [
            {
                "name": tool_name,
                "description": agent.tools[tool_name].description if hasattr(agent.tools[tool_name], "description") else ""
            }
            for tool_name in agent.tools
        ]
        
        # Get agent metrics
        metrics = agent.get_metrics()
        
        # Get agent state history
        state_history = agent.get_state_history(limit=10)
        
        return {
            "name": agent_name,
            "role": agent.role.value,
            "state": agent.state.value,
            "system_message": agent.system_message,
            "assigned_tasks": assigned_tasks,
            "capabilities": capabilities,
            "tools": tools,
            "metrics": metrics,
            "state_history": state_history,
            "current_load": self.coordinator.agent_loads.get(agent_name, 0)
        }
    
    def generate_task_details(self, task_id: str) -> Dict[str, Any]:
        """Generate detailed information about a task for visualization"""
        if not self.coordinator or task_id not in self.coordinator.tasks:
            return {}
        
        task = self.coordinator.tasks[task_id]
        
        # Get dependency tasks
        dependencies = [
            self.coordinator.tasks[dep_id].to_dict()
            for dep_id in task.dependencies
            if dep_id in self.coordinator.tasks
        ]
        
        # Get dependent tasks
        dependents = [
            self.coordinator.tasks[dep_task_id].to_dict()
            for dep_task_id, dep_tasks in self.coordinator.dependency_graph.items()
            if task_id in dep_tasks and dep_task_id in self.coordinator.tasks
        ]
        
        return {
            "id": task_id,
            "name": task.name,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "dependencies": dependencies,
            "dependents": dependents,
            "data": task.data,
            "result": task.result,
            "error": task.error,
            "metadata": task.metadata
        }
    
    def generate_tool_details(self, tool_name: str) -> Dict[str, Any]:
        """Generate detailed information about a tool for visualization"""
        if not self.tool_registry:
            return {}
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {}
        
        # Get agents using this tool
        using_agents = []
        if self.coordinator:
            for agent_name, agent in self.coordinator.agents.items():
                if tool_name in agent.tools:
                    using_agents.append(agent_name)
        
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "parameters": [param.to_dict() for param in tool.parameters],
            "required_permissions": tool.required_permissions,
            "metadata": tool.metadata,
            "using_agents": using_agents
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for a monitoring dashboard"""
        result = {
            "agents": {},
            "tasks": {
                "total": 0,
                "pending": 0,
                "assigned": 0,
                "in_progress": 0,
                "completed": 0,
                "failed": 0
            },
            "tools": {
                "total": 0,
                "by_category": {}
            },
            "metrics": {},
            "events": {
                "recent": [],
                "by_type": {},
                "by_severity": {}
            }
        }
        
        # Agent statistics
        if self.coordinator:
            result["agents"] = {
                "total": len(self.coordinator.agents),
                "by_role": {},
                "by_state": {}
            }
            
            # Count agents by role and state
            for agent_name, agent in self.coordinator.agents.items():
                role = agent.role.value
                state = agent.state.value
                
                if role not in result["agents"]["by_role"]:
                    result["agents"]["by_role"][role] = 0
                result["agents"]["by_role"][role] += 1
                
                if state not in result["agents"]["by_state"]:
                    result["agents"]["by_state"][state] = 0
                result["agents"]["by_state"][state] += 1
            
            # Task statistics
            result["tasks"]["total"] = len(self.coordinator.tasks)
            
            for task in self.coordinator.tasks.values():
                status = task.status.value
                if status == TaskStatus.PENDING.value:
                    result["tasks"]["pending"] += 1
                elif status == TaskStatus.ASSIGNED.value:
                    result["tasks"]["assigned"] += 1
                elif status == TaskStatus.IN_PROGRESS.value:
                    result["tasks"]["in_progress"] += 1
                elif status == TaskStatus.COMPLETED.value:
                    result["tasks"]["completed"] += 1
                elif status == TaskStatus.FAILED.value:
                    result["tasks"]["failed"] += 1
        
        # Tool statistics
        if self.tool_registry:
            tools = self.tool_registry.get_all_tools()
            result["tools"]["total"] = len(tools)
            
            # Count tools by category
            for tool in tools:
                category = tool.category.value
                if category not in result["tools"]["by_category"]:
                    result["tools"]["by_category"][category] = 0
                result["tools"]["by_category"][category] += 1
        
        # Metrics
        if self.monitoring_system:
            result["metrics"] = self.monitoring_system.get_aggregated_metrics()
            
            # Event statistics
            events = list(self.monitoring_system.events)
            
            # Recent events (last 10)
            result["events"]["recent"] = [
                {
                    "id": event.id,
                    "type": event.type.value,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source
                }
                for event in events[-10:]
            ]
            
            # Count events by type and severity
            for event in events:
                event_type = event.type.value
                severity = event.severity.value
                
                if event_type not in result["events"]["by_type"]:
                    result["events"]["by_type"][event_type] = 0
                result["events"]["by_type"][event_type] += 1
                
                if severity not in result["events"]["by_severity"]:
                    result["events"]["by_severity"][severity] = 0
                result["events"]["by_severity"][severity] += 1
        
        return result 