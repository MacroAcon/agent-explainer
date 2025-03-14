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
    ToolRegistry, tool, ToolCategory,
    
    # Conversation management
    ConversationManager, MessageRole, MessageType,
    
    # Monitoring
    MonitoringSystem, EventType, EventSeverity, create_performance_monitoring
)

# Import business-specific modules
from src.agents.framework.business_domain import (
    BusinessType, BusinessProfile, BusinessAgent,
    Customer, InventoryItem, Appointment, Transaction,
    AppointmentStatus, TransactionType, PaymentMethod
)
from src.agents.framework.business_tools import register_business_tools
from src.agents.framework.business_setup import (
    initialize_setup_wizard, SetupStep, BusinessTemplate, TEMPLATE_DETAILS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_interactive_demo():
    """Run an interactive demo of the business framework"""
    print("\n=== A&A Calhoun Automation Consultancy - Business AI Framework Demo ===\n")
    print("This demo shows how the business framework can be used to create a customized")
    print("AI assistant for local businesses.\n")
    
    # Create tool registry
    registry = ToolRegistry()
    
    # Register business tools
    register_business_tools(registry)
    
    # Create monitoring system
    monitoring = MonitoringSystem()
    create_performance_monitoring(monitoring)
    
    # Create conversation manager
    conversation_manager = ConversationManager()
    
    # Initialize setup wizard
    print("Initializing setup wizard...\n")
    conversation_id = initialize_setup_wizard(conversation_manager)
    
    # Simulate setup process
    print("=== Setup Wizard Demo ===\n")
    
    # Welcome step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="Hi, I'd like to set up my business.",
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Business type step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="I have a retail business, a small clothing boutique.",
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Business details step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="""
1. Name: Trendy Threads Boutique
2. Address: 123 Main Street, Anytown, USA 12345
3. Phone: (555) 123-4567
4. Email: info@trendythreads.com
5. Website: www.trendythreads.com
6. Description: A small boutique clothing store specializing in trendy, affordable fashion for young adults.
        """,
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Hours setup step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="""
- Monday: 10:00 AM - 7:00 PM
- Tuesday: 10:00 AM - 7:00 PM
- Wednesday: 10:00 AM - 7:00 PM
- Thursday: 10:00 AM - 7:00 PM
- Friday: 10:00 AM - 8:00 PM
- Saturday: 9:00 AM - 8:00 PM
- Sunday: 12:00 PM - 5:00 PM
        """,
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Integration setup step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="""
I currently use Square for point of sale, QuickBooks for accounting, and Mailchimp for marketing emails.
I'd also like to set up an online store with Shopify in the future.
        """,
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Template selection step
    await conversation_manager.process_message(
        conversation_id=conversation_id,
        content="I'd like to use the Retail Advanced template since I need comprehensive inventory management.",
        role=MessageRole.USER
    )
    
    # Print assistant response
    conversation = conversation_manager.get_conversation(conversation_id)
    print(conversation.messages[-1].content)
    print("\n" + "-" * 80 + "\n")
    
    # Get the business agent from the setup context
    setup_context = conversation.context.get("setup_context", {})
    business_agent = setup_context.get("agent")
    
    if not business_agent:
        print("Error: Business agent not created during setup.")
        return
    
    print("=== Business Operations Demo ===\n")
    print("Now that setup is complete, let's demonstrate some business operations.\n")
    
    # Add tools to the business agent
    for tool_name, tool in registry.tools.items():
        business_agent.add_tool(tool)
    
    # Demo 1: Add a customer
    print("Demo 1: Adding a customer\n")
    customer_result = await business_agent.tools["customer_add"].execute({
        "business_agent": business_agent,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "(555) 987-6543",
        "tags": ["regular", "vip"]
    })
    
    customer_id = customer_result.result["customer_id"]
    print(f"Added customer: {customer_result.result['customer']['first_name']} {customer_result.result['customer']['last_name']}")
    print(f"Customer ID: {customer_id}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 2: Add inventory items
    print("Demo 2: Adding inventory items\n")
    
    # Add first item
    item1_result = await business_agent.tools["inventory_add"].execute({
        "business_agent": business_agent,
        "sku": "TS-001",
        "name": "Graphic T-Shirt",
        "category": "Tops",
        "price": 24.99,
        "quantity": 50,
        "description": "Cotton graphic t-shirt with trendy design",
        "cost": 12.50,
        "reorder_point": 10
    })
    
    item1_id = item1_result.result["item_id"]
    print(f"Added item: {item1_result.result['item']['name']}")
    print(f"Item ID: {item1_id}")
    print(f"Quantity: {item1_result.result['item']['quantity']}")
    print()
    
    # Add second item
    item2_result = await business_agent.tools["inventory_add"].execute({
        "business_agent": business_agent,
        "sku": "JN-001",
        "name": "Designer Jeans",
        "category": "Bottoms",
        "price": 79.99,
        "quantity": 25,
        "description": "Premium denim jeans with modern fit",
        "cost": 35.00,
        "reorder_point": 5
    })
    
    item2_id = item2_result.result["item_id"]
    print(f"Added item: {item2_result.result['item']['name']}")
    print(f"Item ID: {item2_id}")
    print(f"Quantity: {item2_result.result['item']['quantity']}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 3: Process a sale transaction
    print("Demo 3: Processing a sale transaction\n")
    
    transaction_result = await business_agent.tools["transaction_create"].execute({
        "business_agent": business_agent,
        "type": "sale",
        "amount": 104.98,
        "payment_method": "credit_card",
        "customer_id": customer_id,
        "items": [
            {
                "item_id": item1_id,
                "quantity": 1,
                "price": 24.99
            },
            {
                "item_id": item2_id,
                "quantity": 1,
                "price": 79.99
            }
        ],
        "notes": "First purchase by Jane Smith"
    })
    
    transaction_id = transaction_result.result["transaction_id"]
    print(f"Created transaction: {transaction_id}")
    print(f"Amount: ${transaction_result.result['transaction']['amount']}")
    print(f"Payment method: {transaction_result.result['transaction']['payment_method']}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 4: Check inventory after sale
    print("Demo 4: Checking inventory after sale\n")
    
    # Check first item
    item1 = business_agent.get_inventory_item(item1_id)
    print(f"Item: {item1.name}")
    print(f"Quantity before sale: 50")
    print(f"Quantity after sale: {item1.quantity}")
    print()
    
    # Check second item
    item2 = business_agent.get_inventory_item(item2_id)
    print(f"Item: {item2.name}")
    print(f"Quantity before sale: 25")
    print(f"Quantity after sale: {item2.quantity}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 5: Schedule an appointment
    print("Demo 5: Scheduling an appointment\n")
    
    appointment_result = await business_agent.tools["appointment_schedule"].execute({
        "business_agent": business_agent,
        "customer_id": customer_id,
        "service_id": "personal-shopping",
        "start_time": "2023-06-15T14:00:00",
        "duration_minutes": 60,
        "notes": "Personal shopping session for summer wardrobe"
    })
    
    appointment_id = appointment_result.result["appointment_id"]
    appointment = appointment_result.result["appointment"]
    print(f"Scheduled appointment: {appointment_id}")
    print(f"Customer: {business_agent.get_customer(appointment['customer_id']).first_name} {business_agent.get_customer(appointment['customer_id']).last_name}")
    print(f"Service: {appointment['service_id']}")
    print(f"Time: {appointment['start_time']} to {appointment['end_time']}")
    print(f"Status: {appointment['status']}")
    print("\n" + "-" * 80 + "\n")
    
    # Demo 6: Generate sales analytics
    print("Demo 6: Generating sales analytics\n")
    
    # Set date range to include our transaction
    today = datetime.now().strftime("%Y-%m-%d")
    
    analytics_result = await business_agent.tools["sales_analytics"].execute({
        "business_agent": business_agent,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "group_by": "month"
    })
    
    print("Sales Analytics:")
    print(f"Period: {analytics_result.result['period']['start']} to {analytics_result.result['period']['end']}")
    print(f"Total Sales: ${analytics_result.result['overall']['total_sales']}")
    print(f"Total Transactions: {analytics_result.result['overall']['total_transactions']}")
    print(f"Average Transaction: ${analytics_result.result['overall']['average_transaction']}")
    print("\n" + "-" * 80 + "\n")
    
    print("=== Demo Complete ===\n")
    print("This demo showed how the business framework can be used to:")
    print("1. Guide a business owner through setup with a user-friendly wizard")
    print("2. Create a customized business agent based on the business type and needs")
    print("3. Manage customers, inventory, transactions, and appointments")
    print("4. Generate analytics and insights for the business")
    print("\nThe framework provides a solid foundation for building AI assistants")
    print("tailored to local businesses, with a low technical barrier to entry.")

if __name__ == "__main__":
    asyncio.run(run_interactive_demo()) 