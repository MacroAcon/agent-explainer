# Structured Agent Framework

A comprehensive framework for building, managing, and monitoring AI agents with structured patterns inspired by Manus AI.

## Features

- **Structured Agent Architecture**: Well-defined agent framework with consistent patterns
- **Tool Integration Framework**: Easy connection of agents with various tools and APIs
- **Memory and Context Management**: Sophisticated memory capabilities for maintaining context
- **Conversation Flow Management**: Structured conversation handling between agents and users/systems
- **Monitoring and Observability**: Tools for tracking agent performance and behaviors
- **Visual Development Interface**: Support for visual tools for creating and managing agents
- **Agent Coordination**: Sophisticated coordination of multiple agents with task management

## Components

### Core Agent Components

The core agent architecture provides a consistent structure for all agents:

```python
from src.agents.framework import StructuredAgent, AgentRole, AgentState, MemoryType

# Create a structured agent
agent = StructuredAgent(
    name="my_agent",
    role=AgentRole.WORKER,
    system_message="You are a helpful assistant."
)

# Add memory to the agent
agent.add_memory(
    content="Important information to remember",
    memory_type=MemoryType.LONG_TERM,
    metadata={"source": "user", "importance": "high"}
)

# Process a message
response = await agent.process_message("Hello, can you help me?")
```

### Tool Framework

The tool framework allows agents to use various tools:

```python
from src.agents.framework import ToolRegistry, tool, ToolCategory, ToolChain

# Create a tool registry
registry = ToolRegistry()

# Define a tool using the decorator
@tool(
    name="calculator",
    description="Performs basic arithmetic operations",
    category=ToolCategory.UTILITY
)
def calculator(operation: str, a: float, b: float) -> float:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Register the tool
registry.register_tool(calculator.tool)

# Create a tool chain
chain = ToolChain(name="math_chain", description="Chain of math operations")
chain.add_step(
    tool_name="calculator",
    parameters={"operation": "add", "a": 5, "b": 3}
)
chain.add_step(
    tool_name="calculator",
    parameters={"operation": "multiply", "a": "${calculator}", "b": 2}
)

# Execute the chain
result = await chain.execute(registry)
print(result)  # Output: {"context": {"calculator": 16.0}, "results": [...], "success": true}
```

### Conversation Management

The conversation management system handles structured conversations:

```python
from src.agents.framework import (
    ConversationManager, MessageRole, MessageType,
    create_linear_flow, create_branching_flow
)

# Create a conversation manager
manager = ConversationManager()

# Define conversation steps
async def greeting_handler(conversation, message):
    return "introduction"

async def introduction_handler(conversation, message):
    return "question"

async def question_handler(conversation, message):
    return "farewell"

async def farewell_handler(conversation, message):
    return None

# Create a linear conversation flow
flow = create_linear_flow(
    name="customer_service",
    steps=[
        {"name": "greeting", "handler": greeting_handler},
        {"name": "introduction", "handler": introduction_handler},
        {"name": "question", "handler": question_handler},
        {"name": "farewell", "handler": farewell_handler}
    ]
)

# Register the flow
manager.register_flow(flow)

# Create a conversation with the flow
conversation = manager.create_conversation(flow_id=flow.id)

# Process messages in the conversation
await manager.process_message(
    conversation_id=conversation.id,
    content="Hello!",
    role=MessageRole.USER
)
```

### Monitoring and Observability

The monitoring system tracks agent performance and behaviors:

```python
from src.agents.framework import (
    MonitoringSystem, EventType, EventSeverity,
    create_performance_monitoring, log_agent_activity
)

# Create a monitoring system
monitoring = MonitoringSystem()

# Setup performance monitoring
create_performance_monitoring(monitoring)

# Record events
monitoring.record_event(
    event_type=EventType.TASK_STARTED,
    source="agent:my_agent",
    data={"task_id": "123", "task_name": "Process customer request"},
    severity=EventSeverity.INFO
)

# Record metrics
monitoring.record_metric(
    name="response_time",
    value=0.45,
    metric_type=MetricType.HISTOGRAM,
    labels={"agent_id": "my_agent"}
)

# Log agent activity
log_agent_activity(
    monitoring_system=monitoring,
    agent_id="my_agent",
    activity="processing_request",
    data={"request_id": "123"}
)

# Get aggregated metrics
metrics = monitoring.get_aggregated_metrics()
print(metrics)
```

### Agent Coordination

The agent coordination system manages multiple agents and tasks:

```python
from src.agents.framework import (
    AgentCoordinator, AgentCoordinatorFactory,
    TaskPriority, AgentCapability
)

# Create a coordinator
coordinator = AgentCoordinatorFactory.create_coordinator(
    name="my_coordinator",
    monitoring_system=monitoring
)

# Register agents with capabilities
coordinator.register_agent(
    agent=agent,
    capabilities=[
        AgentCapability(
            name="math",
            description="Can perform mathematical calculations",
            score=0.9
        ),
        AgentCapability(
            name="writing",
            description="Can write creative content",
            score=0.7
        )
    ]
)

# Create tasks
task = coordinator.create_task(
    name="Calculate budget",
    description="Calculate the monthly budget based on income and expenses",
    priority=TaskPriority.HIGH
)

# Assign tasks to agents
coordinator.assign_tasks()

# Process tasks
results = await coordinator.process_tasks()
print(results)
```

### Visualization

The visualization adapter provides data for visual tools:

```python
from src.agents.framework import VisualizationAdapter

# Create a visualization adapter
adapter = VisualizationAdapter(
    coordinator=coordinator,
    tool_registry=registry,
    monitoring_system=monitoring
)

# Generate a graph of agents and their relationships
agent_graph = adapter.generate_agent_graph()

# Generate a complete graph of the system
complete_graph = adapter.generate_complete_graph()

# Generate dashboard data
dashboard_data = adapter.generate_dashboard_data()

# Export as JSON for visualization
json_data = complete_graph.to_json()
```

## Integration with Existing Systems

This framework is designed to integrate with your existing agent systems. You can:

1. Gradually migrate existing agents to the structured framework
2. Use the tool framework with existing agents
3. Add monitoring to existing agents
4. Visualize existing agents using the visualization adapter

## Best Practices

1. **Consistent Agent Design**: Use the structured agent architecture for all agents
2. **Tool Reusability**: Design tools to be reusable across different agents
3. **Conversation Flows**: Define clear conversation flows for complex interactions
4. **Monitoring**: Always monitor agent performance and behavior
5. **Coordination**: Use the coordinator for complex multi-agent systems
6. **Visualization**: Use visualization tools to understand and debug agent systems 