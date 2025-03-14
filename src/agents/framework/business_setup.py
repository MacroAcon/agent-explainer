from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .conversation_manager import (
    ConversationManager, ConversationFlow, MessageRole, MessageType,
    create_linear_flow, create_branching_flow
)
from .business_domain import BusinessType, BusinessProfile
from .tool_framework import ToolRegistry
from .business_tools import register_business_tools
from .agent_core import AgentRole
from .business_domain import BusinessAgent

# Setup logging
logger = logging.getLogger(__name__)

# Define setup steps
class SetupStep(str, Enum):
    WELCOME = "welcome"
    BUSINESS_TYPE = "business_type"
    BUSINESS_DETAILS = "business_details"
    HOURS_SETUP = "hours_setup"
    INTEGRATION_SETUP = "integration_setup"
    TEMPLATE_SELECTION = "template_selection"
    COMPLETION = "completion"

# Define business templates
class BusinessTemplate(str, Enum):
    RETAIL_BASIC = "retail_basic"
    RETAIL_ADVANCED = "retail_advanced"
    RESTAURANT_BASIC = "restaurant_basic"
    RESTAURANT_ADVANCED = "restaurant_advanced"
    SERVICE_BASIC = "service_basic"
    SERVICE_ADVANCED = "service_advanced"
    CUSTOM = "custom"

# Define template details
TEMPLATE_DETAILS = {
    BusinessTemplate.RETAIL_BASIC: {
        "name": "Retail Basic",
        "description": "Basic template for retail businesses with inventory management and point-of-sale features.",
        "features": [
            "Customer management",
            "Inventory tracking",
            "Basic sales analytics",
            "Simple point-of-sale"
        ],
        "recommended_for": "Small retail shops, boutiques, and stores with simple inventory needs."
    },
    BusinessTemplate.RETAIL_ADVANCED: {
        "name": "Retail Advanced",
        "description": "Advanced template for retail businesses with comprehensive inventory, customer, and marketing features.",
        "features": [
            "Advanced customer management with purchase history",
            "Comprehensive inventory tracking with reorder alerts",
            "Detailed sales analytics and forecasting",
            "Marketing campaign management",
            "Supplier management",
            "Employee scheduling"
        ],
        "recommended_for": "Medium to large retail businesses with complex inventory and customer needs."
    },
    BusinessTemplate.RESTAURANT_BASIC: {
        "name": "Restaurant Basic",
        "description": "Basic template for restaurants with table management and menu features.",
        "features": [
            "Table management",
            "Basic menu management",
            "Simple order tracking",
            "Customer management"
        ],
        "recommended_for": "Small cafes, food trucks, and restaurants with simple operations."
    },
    BusinessTemplate.RESTAURANT_ADVANCED: {
        "name": "Restaurant Advanced",
        "description": "Advanced template for restaurants with comprehensive menu, inventory, and reservation features.",
        "features": [
            "Advanced table and reservation management",
            "Comprehensive menu management with modifiers",
            "Inventory tracking for ingredients",
            "Employee scheduling and time tracking",
            "Detailed sales analytics by menu item",
            "Online ordering integration"
        ],
        "recommended_for": "Full-service restaurants, bars, and food service businesses with complex operations."
    },
    BusinessTemplate.SERVICE_BASIC: {
        "name": "Service Basic",
        "description": "Basic template for service businesses with appointment scheduling and client management.",
        "features": [
            "Appointment scheduling",
            "Client management",
            "Basic service tracking",
            "Simple invoicing"
        ],
        "recommended_for": "Small service providers like consultants, salons, and repair shops."
    },
    BusinessTemplate.SERVICE_ADVANCED: {
        "name": "Service Advanced",
        "description": "Advanced template for service businesses with comprehensive scheduling, client, and billing features.",
        "features": [
            "Advanced appointment scheduling with reminders",
            "Comprehensive client management with history",
            "Service package and subscription management",
            "Employee scheduling and performance tracking",
            "Detailed service analytics",
            "Online booking integration"
        ],
        "recommended_for": "Professional service providers, medical practices, and service businesses with complex operations."
    },
    BusinessTemplate.CUSTOM: {
        "name": "Custom Template",
        "description": "Build a custom template with exactly the features you need.",
        "features": [
            "Select individual features based on your needs",
            "Customize terminology for your industry",
            "Add industry-specific tools and integrations",
            "Scale as your business grows"
        ],
        "recommended_for": "Businesses with unique requirements or those that don't fit standard categories."
    }
}

# Define setup context
class SetupContext(BaseModel):
    business_profile: Optional[BusinessProfile] = None
    selected_template: Optional[BusinessTemplate] = None
    integrations: Dict[str, bool] = Field(default_factory=dict)
    custom_features: List[str] = Field(default_factory=list)
    setup_complete: bool = False
    agent: Optional[BusinessAgent] = None

# Setup wizard handlers
async def welcome_handler(conversation, message):
    """Welcome the user and explain the setup process"""
    # Initialize setup context if not exists
    if "setup_context" not in conversation.context:
        conversation.context["setup_context"] = SetupContext().dict()
    
    response = """
# Welcome to the Business Setup Wizard!

I'll guide you through setting up your business in our system. This will help us customize the AI assistant to your specific needs.

The setup process includes:
1. Selecting your business type
2. Entering basic business details
3. Setting up business hours
4. Configuring integrations with other tools
5. Selecting a template that fits your business

Let's get started! What type of business do you have?
- Retail (stores, shops)
- Restaurant (cafes, bars, food service)
- Service (salons, consultants, professionals)
- Healthcare (medical, dental, wellness)
- Professional (law, accounting, real estate)
- Other (please specify)
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.BUSINESS_TYPE

async def business_type_handler(conversation, message):
    """Determine the business type"""
    setup_context = conversation.context.get("setup_context", {})
    
    # Parse business type from message
    business_type = None
    message_content = message.content.lower()
    
    if "retail" in message_content:
        business_type = BusinessType.RETAIL
    elif "restaurant" in message_content:
        business_type = BusinessType.RESTAURANT
    elif "service" in message_content:
        business_type = BusinessType.SERVICE
    elif "healthcare" in message_content:
        business_type = BusinessType.HEALTHCARE
    elif "professional" in message_content:
        business_type = BusinessType.PROFESSIONAL
    else:
        business_type = BusinessType.OTHER
    
    # Create initial business profile
    if not setup_context.get("business_profile"):
        setup_context["business_profile"] = BusinessProfile(
            name="",
            type=business_type
        ).dict()
    else:
        setup_context["business_profile"]["type"] = business_type
    
    # Update context
    conversation.context["setup_context"] = setup_context
    
    # Suggest templates based on business type
    suggested_templates = []
    if business_type == BusinessType.RETAIL:
        suggested_templates = [BusinessTemplate.RETAIL_BASIC, BusinessTemplate.RETAIL_ADVANCED]
    elif business_type == BusinessType.RESTAURANT:
        suggested_templates = [BusinessTemplate.RESTAURANT_BASIC, BusinessTemplate.RESTAURANT_ADVANCED]
    elif business_type == BusinessType.SERVICE:
        suggested_templates = [BusinessTemplate.SERVICE_BASIC, BusinessTemplate.SERVICE_ADVANCED]
    else:
        suggested_templates = [BusinessTemplate.CUSTOM]
    
    # Prepare response
    response = f"""
Great! You've selected a {business_type.value} business.

Now, let's get some basic details about your business:
1. What is the name of your business?
2. What is your business address?
3. What is your business phone number?
4. What is your business email?
5. Do you have a website? If so, what is the URL?
6. Please provide a brief description of your business.

You can provide this information in any format, and I'll extract the details.
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.BUSINESS_DETAILS

async def business_details_handler(conversation, message):
    """Collect basic business information"""
    setup_context = conversation.context.get("setup_context", {})
    business_profile = setup_context.get("business_profile", {})
    
    # Extract business details from message
    message_content = message.content
    
    # Simple parsing for demo purposes
    # In a real implementation, you would use NLP or more sophisticated parsing
    lines = message_content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to extract business name
        if not business_profile.get("name") and ("name" in line.lower() or line.startswith("1.")):
            # Extract text after colon or period
            if ":" in line:
                business_profile["name"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["name"] = line.split(".", 1)[1].strip()
        
        # Try to extract address
        elif not business_profile.get("address") and ("address" in line.lower() or line.startswith("2.")):
            if ":" in line:
                business_profile["address"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["address"] = line.split(".", 1)[1].strip()
        
        # Try to extract phone
        elif not business_profile.get("phone") and ("phone" in line.lower() or line.startswith("3.")):
            if ":" in line:
                business_profile["phone"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["phone"] = line.split(".", 1)[1].strip()
        
        # Try to extract email
        elif not business_profile.get("email") and ("email" in line.lower() or line.startswith("4.")):
            if ":" in line:
                business_profile["email"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["email"] = line.split(".", 1)[1].strip()
        
        # Try to extract website
        elif not business_profile.get("website") and ("website" in line.lower() or "url" in line.lower() or line.startswith("5.")):
            if ":" in line:
                business_profile["website"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["website"] = line.split(".", 1)[1].strip()
        
        # Try to extract description
        elif not business_profile.get("description") and ("description" in line.lower() or line.startswith("6.")):
            if ":" in line:
                business_profile["description"] = line.split(":", 1)[1].strip()
            elif "." in line:
                business_profile["description"] = line.split(".", 1)[1].strip()
    
    # Update context
    setup_context["business_profile"] = business_profile
    conversation.context["setup_context"] = setup_context
    
    # Prepare response
    response = f"""
Thank you for providing your business details!

Now, let's set up your business hours. Please provide your hours of operation for each day of the week.
For example:
- Monday: 9:00 AM - 5:00 PM
- Tuesday: 9:00 AM - 5:00 PM
- Wednesday: 9:00 AM - 5:00 PM
- Thursday: 9:00 AM - 5:00 PM
- Friday: 9:00 AM - 5:00 PM
- Saturday: 10:00 AM - 3:00 PM
- Sunday: Closed

You can copy this template and fill in your hours, or provide them in any format that's convenient for you.
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.HOURS_SETUP

async def hours_setup_handler(conversation, message):
    """Set up business hours"""
    setup_context = conversation.context.get("setup_context", {})
    business_profile = setup_context.get("business_profile", {})
    
    # Extract business hours from message
    message_content = message.content
    
    # Initialize hours dictionary if not exists
    if "hours" not in business_profile:
        business_profile["hours"] = {}
    
    # Simple parsing for demo purposes
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    lines = message_content.split("\n")
    
    for line in lines:
        line = line.strip().lower()
        if not line:
            continue
        
        for day in days:
            if day in line:
                # Extract hours after colon
                if ":" in line:
                    hours_part = line.split(":", 1)[1].strip()
                    business_profile["hours"][day] = hours_part
                    break
    
    # Update context
    setup_context["business_profile"] = business_profile
    conversation.context["setup_context"] = setup_context
    
    # Prepare response
    response = f"""
Great! I've recorded your business hours.

Now, let's talk about integrations. Would you like to integrate with any of the following systems?
- Point of Sale (POS) systems like Square, Shopify, or Clover
- Accounting software like QuickBooks or Xero
- Appointment scheduling systems like Calendly or Acuity
- Customer relationship management (CRM) systems like Salesforce or HubSpot
- Marketing platforms like Mailchimp or Constant Contact
- E-commerce platforms like Shopify, WooCommerce, or Etsy

Please let me know which systems you currently use and would like to integrate with.
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.INTEGRATION_SETUP

async def integration_setup_handler(conversation, message):
    """Set up integrations with existing tools"""
    setup_context = conversation.context.get("setup_context", {})
    
    # Initialize integrations dictionary if not exists
    if "integrations" not in setup_context:
        setup_context["integrations"] = {}
    
    # Extract integration preferences from message
    message_content = message.content.lower()
    
    # Check for common integrations
    integrations = {
        "pos": any(pos in message_content for pos in ["pos", "point of sale", "square", "shopify", "clover"]),
        "accounting": any(acc in message_content for acc in ["accounting", "quickbooks", "xero"]),
        "scheduling": any(sch in message_content for sch in ["appointment", "scheduling", "calendly", "acuity"]),
        "crm": any(crm in message_content for crm in ["crm", "customer relationship", "salesforce", "hubspot"]),
        "marketing": any(mkt in message_content for mkt in ["marketing", "mailchimp", "constant contact"]),
        "ecommerce": any(eco in message_content for eco in ["ecommerce", "e-commerce", "shopify", "woocommerce", "etsy"])
    }
    
    # Update context
    setup_context["integrations"] = integrations
    conversation.context["setup_context"] = setup_context
    
    # Determine business type for template suggestions
    business_type = setup_context.get("business_profile", {}).get("type", BusinessType.OTHER)
    
    # Suggest templates based on business type
    template_options = ""
    if business_type == BusinessType.RETAIL:
        template_options = f"""
1. {TEMPLATE_DETAILS[BusinessTemplate.RETAIL_BASIC]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.RETAIL_BASIC]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.RETAIL_BASIC]["features"])}

2. {TEMPLATE_DETAILS[BusinessTemplate.RETAIL_ADVANCED]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.RETAIL_ADVANCED]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.RETAIL_ADVANCED]["features"])}
"""
    elif business_type == BusinessType.RESTAURANT:
        template_options = f"""
1. {TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_BASIC]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_BASIC]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_BASIC]["features"])}

2. {TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_ADVANCED]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_ADVANCED]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.RESTAURANT_ADVANCED]["features"])}
"""
    elif business_type == BusinessType.SERVICE:
        template_options = f"""
1. {TEMPLATE_DETAILS[BusinessTemplate.SERVICE_BASIC]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.SERVICE_BASIC]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.SERVICE_BASIC]["features"])}

2. {TEMPLATE_DETAILS[BusinessTemplate.SERVICE_ADVANCED]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.SERVICE_ADVANCED]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.SERVICE_ADVANCED]["features"])}
"""
    else:
        template_options = f"""
1. {TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["features"])}
"""
    
    # Prepare response
    response = f"""
Thank you for sharing your integration preferences. I've noted the systems you'd like to connect with.

Now, let's select a template that best fits your business needs. Based on your business type, here are some recommended templates:

{template_options}

3. {TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["name"]}: {TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["description"]}
   Features: {", ".join(TEMPLATE_DETAILS[BusinessTemplate.CUSTOM]["features"])}

Please select a template by number or name, or let me know if you'd like more information about any of them.
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.TEMPLATE_SELECTION

async def template_selection_handler(conversation, message):
    """Select and customize a business template"""
    setup_context = conversation.context.get("setup_context", {})
    
    # Extract template selection from message
    message_content = message.content.lower()
    
    # Determine selected template
    selected_template = None
    
    if "1" in message_content or "basic" in message_content:
        business_type = setup_context.get("business_profile", {}).get("type", BusinessType.OTHER)
        if business_type == BusinessType.RETAIL:
            selected_template = BusinessTemplate.RETAIL_BASIC
        elif business_type == BusinessType.RESTAURANT:
            selected_template = BusinessTemplate.RESTAURANT_BASIC
        elif business_type == BusinessType.SERVICE:
            selected_template = BusinessTemplate.SERVICE_BASIC
        else:
            selected_template = BusinessTemplate.CUSTOM
    elif "2" in message_content or "advanced" in message_content:
        business_type = setup_context.get("business_profile", {}).get("type", BusinessType.OTHER)
        if business_type == BusinessType.RETAIL:
            selected_template = BusinessTemplate.RETAIL_ADVANCED
        elif business_type == BusinessType.RESTAURANT:
            selected_template = BusinessTemplate.RESTAURANT_ADVANCED
        elif business_type == BusinessType.SERVICE:
            selected_template = BusinessTemplate.SERVICE_ADVANCED
        else:
            selected_template = BusinessTemplate.CUSTOM
    elif "3" in message_content or "custom" in message_content:
        selected_template = BusinessTemplate.CUSTOM
    else:
        # Default to custom if unclear
        selected_template = BusinessTemplate.CUSTOM
    
    # Update context
    setup_context["selected_template"] = selected_template
    setup_context["setup_complete"] = True
    conversation.context["setup_context"] = setup_context
    
    # Create business agent
    business_profile = BusinessProfile(**setup_context["business_profile"])
    business_agent = BusinessAgent(
        name=f"{business_profile.name}_agent",
        business_profile=business_profile,
        role=AgentRole.SPECIALIST
    )
    
    # Store agent in context
    setup_context["agent"] = business_agent
    conversation.context["setup_context"] = setup_context
    
    # Prepare response
    template_name = TEMPLATE_DETAILS[selected_template]["name"]
    response = f"""
# Setup Complete!

Thank you for completing the setup process. You've selected the **{template_name}** template.

Here's a summary of your business setup:
- **Business Name**: {business_profile.name}
- **Business Type**: {business_profile.type.value}
- **Address**: {business_profile.address or "Not provided"}
- **Phone**: {business_profile.phone or "Not provided"}
- **Email**: {business_profile.email or "Not provided"}
- **Website**: {business_profile.website or "Not provided"}

Your AI business assistant is now configured and ready to help you manage your business. You can start using it right away by asking questions or giving commands related to your business operations.

For example, you can:
- Add customers and inventory items
- Schedule appointments
- Process transactions
- View analytics and reports

Is there anything specific you'd like help with now?
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.COMPLETION

async def completion_handler(conversation, message):
    """Handle post-setup interactions"""
    # At this point, the setup is complete and we're in normal operation mode
    # We can access the business agent from the context
    setup_context = conversation.context.get("setup_context", {})
    business_agent = setup_context.get("agent")
    
    if not business_agent:
        # Something went wrong, restart setup
        conversation.context["setup_context"] = SetupContext().dict()
        
        response = """
I'm sorry, but there seems to be an issue with your setup. Let's start over.

# Welcome to the Business Setup Wizard!

I'll guide you through setting up your business in our system. This will help us customize the AI assistant to your specific needs.

What type of business do you have?
- Retail (stores, shops)
- Restaurant (cafes, bars, food service)
- Service (salons, consultants, professionals)
- Healthcare (medical, dental, wellness)
- Professional (law, accounting, real estate)
- Other (please specify)
"""
        
        conversation.add_message(
            content=response,
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT
        )
        
        return SetupStep.BUSINESS_TYPE
    
    # Process the message with the business agent
    # In a real implementation, you would use the agent to process the message
    # For now, we'll just provide a simple response
    
    response = """
Your business is fully set up and your AI assistant is ready to help you manage your operations.

You can now use all the features of your selected template, including customer management, inventory tracking, appointment scheduling, and analytics.

Is there anything specific you'd like to do with your business assistant?
"""
    
    conversation.add_message(
        content=response,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.TEXT
    )
    
    return SetupStep.COMPLETION

# Create setup wizard flow
def create_setup_wizard_flow() -> ConversationFlow:
    """Create the setup wizard conversation flow"""
    return create_linear_flow(
        name="business_setup_wizard",
        steps=[
            {
                "name": SetupStep.WELCOME,
                "handler": welcome_handler,
                "description": "Welcome the user and explain the setup process"
            },
            {
                "name": SetupStep.BUSINESS_TYPE,
                "handler": business_type_handler,
                "description": "Determine the business type"
            },
            {
                "name": SetupStep.BUSINESS_DETAILS,
                "handler": business_details_handler,
                "description": "Collect basic business information"
            },
            {
                "name": SetupStep.HOURS_SETUP,
                "handler": hours_setup_handler,
                "description": "Set up business hours"
            },
            {
                "name": SetupStep.INTEGRATION_SETUP,
                "handler": integration_setup_handler,
                "description": "Set up integrations with existing tools"
            },
            {
                "name": SetupStep.TEMPLATE_SELECTION,
                "handler": template_selection_handler,
                "description": "Select and customize a business template"
            },
            {
                "name": SetupStep.COMPLETION,
                "handler": completion_handler,
                "description": "Complete the setup and provide next steps"
            }
        ],
        description="Guide the user through setting up their business",
        metadata={
            "purpose": "business_setup",
            "version": "1.0"
        }
    )

# Initialize setup wizard
def initialize_setup_wizard(conversation_manager: ConversationManager) -> str:
    """Initialize the setup wizard and return the conversation ID"""
    # Create setup wizard flow
    setup_flow = create_setup_wizard_flow()
    
    # Register flow with conversation manager
    conversation_manager.register_flow(setup_flow)
    
    # Create a new conversation with the flow
    conversation = conversation_manager.create_conversation(
        flow_id=setup_flow.id,
        context={},
        metadata={
            "purpose": "business_setup",
            "created_at": datetime.now().isoformat()
        }
    )
    
    return conversation.id 