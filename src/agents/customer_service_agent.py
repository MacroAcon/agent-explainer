from typing import Dict, Any
from .base_agent import BaseBusinessAgent

class CustomerServiceAgent(BaseBusinessAgent):
    """Specialized agent for handling customer service tasks."""
    
    def __init__(self, name: str = "CustomerServiceAgent"):
        system_message = """You are a professional customer service representative for {business_name}.
        Your role is to handle customer inquiries, complaints, and requests efficiently and professionally.
        Always maintain a helpful and friendly tone while representing the business values."""
        
        # Define customer service specific tools
        tools = [
            {
                "name": "format_response",
                "description": "Format the response according to business guidelines",
                "func": self.format_response
            },
            {
                "name": "categorize_inquiry",
                "description": "Categorize the customer inquiry for proper handling",
                "func": self.categorize_inquiry
            }
        ]
        
        super().__init__(name=name, system_message=system_message, tools=tools)
    
    async def generate_response(self, task: str, context: Dict[str, Any]) -> str:
        """Generate a customer service response."""
        # Categorize the inquiry
        category = await self.categorize_inquiry(task)
        
        # Add category to context
        context["inquiry_category"] = category
        
        # Generate appropriate response based on category and context
        response = await self.chat(
            task,
            context=context,
            max_consecutive_auto_reply=1
        )
        
        # Format the response according to business guidelines
        formatted_response = await self.format_response(response, context)
        
        return formatted_response
    
    async def format_response(self, response: str, context: Dict[str, Any]) -> str:
        """Format the response according to business guidelines."""
        formatted = f"Thank you for contacting {context['business_name']}.\n\n"
        formatted += response
        formatted += "\n\nIs there anything else I can help you with?"
        return formatted
    
    async def categorize_inquiry(self, inquiry: str) -> str:
        """Categorize the customer inquiry."""
        # This would typically use more sophisticated categorization
        # For now, we'll use basic keyword matching
        inquiry = inquiry.lower()
        
        if any(word in inquiry for word in ["refund", "money", "payment"]):
            return "billing"
        elif any(word in inquiry for word in ["broken", "issue", "problem"]):
            return "technical_support"
        elif any(word in inquiry for word in ["delivery", "shipping", "track"]):
            return "shipping"
        else:
            return "general_inquiry" 