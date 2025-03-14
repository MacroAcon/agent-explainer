import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.framework import (
    # Core components
    StructuredAgent, AgentRole, AgentState, MemoryType,
    
    # Tool framework
    ToolRegistry, tool, ToolCategory, ToolChain, ToolParameter,
    
    # Monitoring
    MonitoringSystem, EventType, EventSeverity, create_performance_monitoring,
    
    # Agent coordination
    AgentCoordinator, TaskPriority, AgentCapability,
    
    # Visualization
    VisualizationAdapter
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tool registry
registry = ToolRegistry()

# Define tools
@tool(
    name="calculator",
    description="Performs basic arithmetic operations",
    category=ToolCategory.UTILITY,
    parameters=[
        ToolParameter(
            name="operation",
            description="The operation to perform (add, subtract, multiply, divide)",
            type="string",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        ToolParameter(
            name="a",
            description="First number",
            type="number",
            required=True
        ),
        ToolParameter(
            name="b",
            description="Second number",
            type="number",
            required=True
        )
    ]
)
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic arithmetic operations"""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

@tool(
    name="text_analyzer",
    description="Analyzes text for sentiment and statistics",
    category=ToolCategory.ANALYTICS
)
def text_analyzer(text: str) -> dict:
    """Analyze text for sentiment and statistics"""
    # Simple implementation - in a real system, you would use NLP
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    # Very simple sentiment analysis
    positive_words = ["good", "great", "excellent", "happy", "positive"]
    negative_words = ["bad", "terrible", "sad", "negative", "poor"]
    
    positive_count = sum(1 for word in words if word.lower() in positive_words)
    negative_count = sum(1 for word in words if word.lower() in negative_words)
    
    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "sentiment": sentiment,
        "positive_words": positive_count,
        "negative_words": negative_count
    }

# Register tools
registry.register_tool(calculator.tool)
registry.register_tool(text_analyzer.tool)

# Create monitoring system
monitoring = MonitoringSystem()
create_performance_monitoring(monitoring)

# Create agent coordinator
coordinator = AgentCoordinator(
    name="simple_coordinator",
    tool_registry=registry,
    monitoring_system=monitoring
)

# Create math agent
class MathAgent(StructuredAgent):
    async def _process_message_impl(self, message: str, metadata: dict) -> str:
        """Process a message and return a response"""
        try:
            # Parse the message as a math operation
            data = json.loads(message)
            operation = data.get("operation", "add")
            a = float(data.get("a", 0))
            b = float(data.get("b", 0))
            
            # Use the calculator tool
            calculator_tool = self.tools.get("calculator")
            if not calculator_tool:
                return "Calculator tool not available"
            
            result = await calculator_tool.execute({
                "operation": operation,
                "a": a,
                "b": b
            })
            
            if result.error:
                return f"Error: {result.error}"
            
            # Add to memory
            self.add_memory(
                content=f"Calculated {a} {operation} {b} = {result.result}",
                memory_type=MemoryType.EPISODIC,
                metadata={"operation": operation, "a": a, "b": b, "result": result.result}
            )
            
            return json.dumps({
                "result": result.result,
                "operation": operation,
                "a": a,
                "b": b
            })
            
        except Exception as e:
            logger.exception("Error in MathAgent")
            return f"Error processing message: {str(e)}"

# Create text analysis agent
class TextAnalysisAgent(StructuredAgent):
    async def _process_message_impl(self, message: str, metadata: dict) -> str:
        """Process a message and return a response"""
        try:
            # Use the text analyzer tool
            text_analyzer_tool = self.tools.get("text_analyzer")
            if not text_analyzer_tool:
                return "Text analyzer tool not available"
            
            result = await text_analyzer_tool.execute({
                "text": message
            })
            
            if result.error:
                return f"Error: {result.error}"
            
            # Add to memory
            self.add_memory(
                content=f"Analyzed text: {message[:50]}...",
                memory_type=MemoryType.EPISODIC,
                metadata={"text": message, "analysis": result.result}
            )
            
            analysis = result.result
            
            return json.dumps({
                "analysis": analysis,
                "summary": f"The text contains {analysis['word_count']} words and has a {analysis['sentiment']} sentiment."
            })
            
        except Exception as e:
            logger.exception("Error in TextAnalysisAgent")
            return f"Error processing message: {str(e)}"

# Create coordinator agent
class CoordinatorAgent(StructuredAgent):
    async def _process_message_impl(self, message: str, metadata: dict) -> str:
        """Process a message and return a response"""
        try:
            # Determine which agent to use
            if "calculate" in message.lower() or any(op in message.lower() for op in ["add", "subtract", "multiply", "divide"]):
                # This is a math request
                return json.dumps({
                    "agent": "math",
                    "message": "This appears to be a math request. Forwarding to the math agent."
                })
            elif "analyze" in message.lower() or "sentiment" in message.lower():
                # This is a text analysis request
                return json.dumps({
                    "agent": "text",
                    "message": "This appears to be a text analysis request. Forwarding to the text analysis agent."
                })
            else:
                # Not sure, ask for clarification
                return json.dumps({
                    "agent": "unknown",
                    "message": "I'm not sure what you're asking for. Please specify if you want to calculate something or analyze text."
                })
            
        except Exception as e:
            logger.exception("Error in CoordinatorAgent")
            return f"Error processing message: {str(e)}"

async def main():
    """Main function to demonstrate the framework"""
    logger.info("Starting simple agent system example")
    
    # Create agents
    math_agent = MathAgent(
        name="math_agent",
        role=AgentRole.SPECIALIST,
        system_message="You are a math specialist that can perform calculations."
    )
    
    text_agent = TextAnalysisAgent(
        name="text_agent",
        role=AgentRole.SPECIALIST,
        system_message="You are a text analysis specialist that can analyze text."
    )
    
    coordinator_agent = CoordinatorAgent(
        name="coordinator_agent",
        role=AgentRole.COORDINATOR,
        system_message="You are a coordinator that routes requests to the appropriate specialist."
    )
    
    # Add tools to agents
    math_agent.add_tool(registry.get_tool("calculator"))
    text_agent.add_tool(registry.get_tool("text_analyzer"))
    
    # Register agents with coordinator
    coordinator.register_agent(
        math_agent,
        capabilities=[
            AgentCapability(
                name="math",
                description="Can perform mathematical calculations",
                score=0.9
            )
        ]
    )
    
    coordinator.register_agent(
        text_agent,
        capabilities=[
            AgentCapability(
                name="text_analysis",
                description="Can analyze text for sentiment and statistics",
                score=0.9
            )
        ]
    )
    
    coordinator.register_agent(
        coordinator_agent,
        capabilities=[
            AgentCapability(
                name="coordination",
                description="Can route requests to appropriate specialists",
                score=0.9
            )
        ]
    )
    
    # Create visualization adapter
    adapter = VisualizationAdapter(
        coordinator=coordinator,
        tool_registry=registry,
        monitoring_system=monitoring
    )
    
    # Create some tasks
    math_task = coordinator.create_task(
        name="Calculate budget",
        description="Calculate the monthly budget based on income and expenses",
        priority=TaskPriority.HIGH,
        data={
            "operation": "subtract",
            "a": 5000,  # Income
            "b": 3500   # Expenses
        }
    )
    
    text_task = coordinator.create_task(
        name="Analyze feedback",
        description="Analyze customer feedback for sentiment",
        priority=TaskPriority.MEDIUM,
        data={
            "text": "I really enjoyed the product. It was great quality and arrived quickly. The customer service was excellent too!"
        }
    )
    
    # Assign tasks to agents
    assigned_count = coordinator.assign_tasks()
    logger.info(f"Assigned {assigned_count} tasks to agents")
    
    # Process tasks
    results = await coordinator.process_tasks()
    logger.info(f"Processed {results['processed']} tasks, {results['completed']} completed, {results['failed']} failed")
    
    # Print task results
    for task_id, task in coordinator.tasks.items():
        if task.result:
            logger.info(f"Task {task.name} result: {task.result}")
    
    # Generate visualization
    agent_graph = adapter.generate_agent_graph()
    logger.info(f"Generated agent graph with {len(agent_graph.nodes)} nodes and {len(agent_graph.edges)} edges")
    
    # Generate dashboard data
    dashboard_data = adapter.generate_dashboard_data()
    logger.info(f"Generated dashboard data: {json.dumps(dashboard_data, indent=2)}")
    
    # Interactive demo
    print("\n=== Interactive Demo ===")
    print("Enter messages to interact with the system (type 'exit' to quit):")
    
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break
        
        # First, ask the coordinator which agent to use
        coordinator_response = await coordinator_agent.process_message(user_input)
        coordinator_data = json.loads(coordinator_response)
        
        print(f"Coordinator: {coordinator_data['message']}")
        
        # Route to the appropriate agent
        if coordinator_data["agent"] == "math":
            # Parse the math request
            # Simple parsing for demo purposes
            parts = user_input.split()
            operation = "add"
            a = 0
            b = 0
            
            for i, part in enumerate(parts):
                if part.lower() in ["add", "plus", "sum"]:
                    operation = "add"
                elif part.lower() in ["subtract", "minus", "difference"]:
                    operation = "subtract"
                elif part.lower() in ["multiply", "times", "product"]:
                    operation = "multiply"
                elif part.lower() in ["divide", "division", "quotient"]:
                    operation = "divide"
                
                if part.isdigit() and a == 0:
                    a = float(part)
                elif part.isdigit() and a != 0:
                    b = float(part)
            
            math_response = await math_agent.process_message(json.dumps({
                "operation": operation,
                "a": a,
                "b": b
            }))
            
            math_data = json.loads(math_response)
            print(f"Math Agent: The result of {a} {operation} {b} is {math_data['result']}")
            
        elif coordinator_data["agent"] == "text":
            text_response = await text_agent.process_message(user_input)
            text_data = json.loads(text_response)
            print(f"Text Agent: {text_data['summary']}")
            
        else:
            print("Please specify if you want to calculate something or analyze text.")
    
    print("Exiting demo.")

if __name__ == "__main__":
    asyncio.run(main()) 