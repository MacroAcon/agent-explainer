# Local Business AI Framework

A comprehensive framework for building AI assistants tailored to local businesses, with a focus on simplicity, usability, and practical features.

## Key Features

- **Simplified Setup and Onboarding**: User-friendly setup wizard that guides business owners through the configuration process
- **Business-Specific Tools**: Tools for appointment scheduling, inventory tracking, customer management, and more
- **Pre-Configured Templates**: Templates for different business types (retail, restaurant, service providers)
- **Visual Business Insights**: Analytics and reporting tools for business metrics
- **Integration with Popular Tools**: Connections to common business software (QuickBooks, Shopify, Square)
- **Low Technical Barrier**: No-code configuration and plain language interface

## Components

### Business Domain Models

The business domain models provide structured data models for business entities:

```python
from src.agents.framework import BusinessProfile, BusinessType, Customer, InventoryItem

# Create a business profile
profile = BusinessProfile(
    name="Trendy Threads Boutique",
    type=BusinessType.RETAIL,
    address="123 Main Street, Anytown, USA",
    phone="(555) 123-4567",
    email="info@trendythreads.com",
    website="www.trendythreads.com"
)

# Create a customer
customer = Customer(
    first_name="Jane",
    last_name="Smith",
    email="jane.smith@example.com",
    phone="(555) 987-6543",
    tags=["regular", "vip"]
)

# Create an inventory item
item = InventoryItem(
    sku="TS-001",
    name="Graphic T-Shirt",
    category="Tops",
    price=24.99,
    quantity=50,
    description="Cotton graphic t-shirt with trendy design",
    cost=12.50,
    reorder_point=10
)
```

### Business Agent

The business agent extends the structured agent with business-specific capabilities:

```python
from src.agents.framework import BusinessAgent, AgentRole

# Create a business agent
agent = BusinessAgent(
    name="boutique_agent",
    business_profile=profile,
    role=AgentRole.SPECIALIST
)

# Add a customer
customer_id = agent.add_customer(customer)

# Add an inventory item
item_id = agent.add_inventory_item(item)

# Get a customer
customer = agent.get_customer(customer_id)

# Get an inventory item
item = agent.get_inventory_item(item_id)
```

### Business Tools

The business tools provide functionality for common business operations:

```python
from src.agents.framework import ToolRegistry, register_business_tools

# Create a tool registry
registry = ToolRegistry()

# Register business tools
register_business_tools(registry)

# Add tools to the business agent
for tool_name, tool in registry.tools.items():
    agent.add_tool(tool)

# Use a tool to add a customer
result = await agent.tools["customer_add"].execute({
    "business_agent": agent,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "(555) 555-5555"
})

# Use a tool to process a transaction
result = await agent.tools["transaction_create"].execute({
    "business_agent": agent,
    "type": "sale",
    "amount": 104.98,
    "payment_method": "credit_card",
    "customer_id": customer_id,
    "items": [
        {
            "item_id": item_id,
            "quantity": 1,
            "price": 24.99
        }
    ]
})
```

### Setup Wizard

The setup wizard guides users through the business setup process:

```python
from src.agents.framework import ConversationManager, initialize_setup_wizard

# Create a conversation manager
conversation_manager = ConversationManager()

# Initialize setup wizard
conversation_id = initialize_setup_wizard(conversation_manager)

# Process user messages through the wizard
await conversation_manager.process_message(
    conversation_id=conversation_id,
    content="I have a retail business, a small clothing boutique.",
    role=MessageRole.USER
)
```

## Business Templates

The framework includes pre-configured templates for different business types:

- **Retail Basic**: For small retail shops with simple inventory needs
- **Retail Advanced**: For retail businesses with complex inventory and customer needs
- **Restaurant Basic**: For small cafes and restaurants with simple operations
- **Restaurant Advanced**: For full-service restaurants with complex operations
- **Service Basic**: For small service providers like consultants and salons
- **Service Advanced**: For professional service providers with complex operations
- **Custom**: For businesses with unique requirements

## Integration with Existing Systems

The business framework is designed to integrate with popular business software:

- **Point of Sale**: Square, Shopify, Clover
- **Accounting**: QuickBooks, Xero
- **Scheduling**: Calendly, Acuity
- **CRM**: Salesforce, HubSpot
- **Marketing**: Mailchimp, Constant Contact
- **E-commerce**: Shopify, WooCommerce, Etsy

## Example Usage

See the `examples/business_example.py` file for a complete example of using the business framework, including:

1. Setting up a business with the setup wizard
2. Adding customers and inventory items
3. Processing transactions
4. Scheduling appointments
5. Generating analytics

## Best Practices

1. **Start with the Setup Wizard**: Use the setup wizard to configure the business agent
2. **Choose the Right Template**: Select a template that matches the business type and needs
3. **Customize as Needed**: Add additional tools and features as the business grows
4. **Monitor Performance**: Use the analytics tools to track business metrics
5. **Integrate with Existing Tools**: Connect with the business's existing software

## Next Steps

To further enhance the business framework, consider:

1. **Vector Embeddings**: Add vector embeddings for more sophisticated customer and product search
2. **LLM Integration**: Integrate with specific LLM providers for enhanced natural language understanding
3. **Web Interface**: Create a web interface for the business dashboard
4. **Mobile App**: Develop a mobile app for on-the-go business management
5. **Compliance Tools**: Add tools for privacy and regulatory compliance 