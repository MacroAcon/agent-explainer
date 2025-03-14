from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

from .tool_framework import tool, ToolCategory, ToolRegistry
from .business_domain import (
    Customer, InventoryItem, Appointment, Transaction,
    AppointmentStatus, TransactionType, PaymentMethod
)

# Setup logging
logger = logging.getLogger(__name__)

# Define business tool category
class BusinessToolCategory(str, Enum):
    CUSTOMER = "customer"
    INVENTORY = "inventory"
    APPOINTMENT = "appointment"
    TRANSACTION = "transaction"
    MARKETING = "marketing"
    ANALYTICS = "analytics"

# Customer management tools
@tool(
    name="customer_search",
    description="Search for customers by name, email, or phone",
    category=ToolCategory.UTILITY
)
async def customer_search(
    business_agent: Any,
    query: str,
    search_field: str = "name",  # name, email, phone
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search for customers in the business database"""
    results = []
    count = 0
    
    query = query.lower()
    
    for customer_id, customer in business_agent.customers.items():
        if search_field == "name":
            full_name = f"{customer.first_name} {customer.last_name}".lower()
            if query in full_name:
                results.append(customer.dict())
                count += 1
        elif search_field == "email" and customer.email:
            if query in customer.email.lower():
                results.append(customer.dict())
                count += 1
        elif search_field == "phone" and customer.phone:
            if query in customer.phone:
                results.append(customer.dict())
                count += 1
        
        if count >= limit:
            break
    
    return results

@tool(
    name="customer_add",
    description="Add a new customer to the business",
    category=ToolCategory.UTILITY
)
async def customer_add(
    business_agent: Any,
    first_name: str,
    last_name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    tags: List[str] = None,
    notes: str = ""
) -> Dict[str, Any]:
    """Add a new customer to the business database"""
    tags = tags or []
    
    customer = Customer(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        tags=tags,
        notes=notes
    )
    
    customer_id = business_agent.add_customer(customer)
    
    return {
        "success": True,
        "customer_id": customer_id,
        "customer": customer.dict()
    }

# Inventory management tools
@tool(
    name="inventory_search",
    description="Search for inventory items by name, SKU, or category",
    category=ToolCategory.UTILITY
)
async def inventory_search(
    business_agent: Any,
    query: str,
    search_field: str = "name",  # name, sku, category
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Search for inventory items in the business database"""
    results = []
    count = 0
    
    query = query.lower()
    
    for item_id, item in business_agent.inventory.items():
        if search_field == "name":
            if query in item.name.lower():
                results.append(item.dict())
                count += 1
        elif search_field == "sku":
            if query in item.sku.lower():
                results.append(item.dict())
                count += 1
        elif search_field == "category":
            if query in item.category.lower():
                results.append(item.dict())
                count += 1
        
        if count >= limit:
            break
    
    return results

@tool(
    name="inventory_add",
    description="Add a new inventory item to the business",
    category=ToolCategory.UTILITY
)
async def inventory_add(
    business_agent: Any,
    sku: str,
    name: str,
    category: str,
    price: float,
    quantity: int,
    description: Optional[str] = None,
    cost: Optional[float] = None,
    reorder_point: Optional[int] = None,
    supplier: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """Add a new inventory item to the business database"""
    item = InventoryItem(
        sku=sku,
        name=name,
        description=description,
        category=category,
        price=price,
        cost=cost,
        quantity=quantity,
        reorder_point=reorder_point,
        supplier=supplier,
        location=location
    )
    
    item_id = business_agent.add_inventory_item(item)
    
    return {
        "success": True,
        "item_id": item_id,
        "item": item.dict()
    }

@tool(
    name="inventory_update",
    description="Update inventory quantity",
    category=ToolCategory.UTILITY
)
async def inventory_update(
    business_agent: Any,
    item_id: str,
    quantity_change: int,
    reason: str = "manual adjustment"
) -> Dict[str, Any]:
    """Update inventory quantity for an item"""
    item = business_agent.get_inventory_item(item_id)
    
    if not item:
        return {
            "success": False,
            "error": f"Item with ID {item_id} not found"
        }
    
    old_quantity = item.quantity
    item.quantity += quantity_change
    item.updated_at = datetime.now()
    
    # Add to memory
    business_agent.add_memory(
        content=f"Updated inventory for {item.name}: {old_quantity} -> {item.quantity} ({reason})",
        memory_type="EPISODIC",
        metadata={"item_id": item_id, "change": quantity_change, "reason": reason}
    )
    
    return {
        "success": True,
        "item_id": item_id,
        "old_quantity": old_quantity,
        "new_quantity": item.quantity,
        "change": quantity_change
    }

# Appointment management tools
@tool(
    name="appointment_schedule",
    description="Schedule a new appointment",
    category=ToolCategory.UTILITY
)
async def appointment_schedule(
    business_agent: Any,
    customer_id: str,
    service_id: str,
    start_time: str,  # ISO format: YYYY-MM-DDTHH:MM:SS
    duration_minutes: int,
    notes: str = ""
) -> Dict[str, Any]:
    """Schedule a new appointment"""
    # Validate customer exists
    customer = business_agent.get_customer(customer_id)
    if not customer:
        return {
            "success": False,
            "error": f"Customer with ID {customer_id} not found"
        }
    
    # Parse start time
    try:
        start_datetime = datetime.fromisoformat(start_time)
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid start time format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
        }
    
    # Calculate end time
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    
    # Create appointment
    appointment = Appointment(
        customer_id=customer_id,
        service_id=service_id,
        start_time=start_datetime,
        end_time=end_datetime,
        notes=notes
    )
    
    appointment_id = business_agent.add_appointment(appointment)
    
    return {
        "success": True,
        "appointment_id": appointment_id,
        "appointment": appointment.dict()
    }

@tool(
    name="appointment_update",
    description="Update an appointment status",
    category=ToolCategory.UTILITY
)
async def appointment_update(
    business_agent: Any,
    appointment_id: str,
    status: str,  # scheduled, confirmed, completed, cancelled, no_show
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Update an appointment status"""
    appointment = business_agent.get_appointment(appointment_id)
    
    if not appointment:
        return {
            "success": False,
            "error": f"Appointment with ID {appointment_id} not found"
        }
    
    try:
        new_status = AppointmentStatus(status)
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid status. Use one of: {', '.join([s.value for s in AppointmentStatus])}"
        }
    
    old_status = appointment.status
    appointment.status = new_status
    appointment.updated_at = datetime.now()
    
    if notes:
        appointment.notes += f"\n{datetime.now().isoformat()}: {notes}"
    
    # Add to memory
    business_agent.add_memory(
        content=f"Updated appointment {appointment_id} status: {old_status} -> {new_status}",
        memory_type="EPISODIC",
        metadata={"appointment_id": appointment_id, "old_status": old_status, "new_status": new_status}
    )
    
    return {
        "success": True,
        "appointment_id": appointment_id,
        "old_status": old_status,
        "new_status": new_status
    }

# Transaction management tools
@tool(
    name="transaction_create",
    description="Create a new transaction",
    category=ToolCategory.UTILITY
)
async def transaction_create(
    business_agent: Any,
    type: str,  # sale, refund, adjustment, payment
    amount: float,
    payment_method: str,  # cash, credit_card, debit_card, mobile_payment, bank_transfer, check, other
    customer_id: Optional[str] = None,
    items: List[Dict[str, Any]] = None,
    notes: str = ""
) -> Dict[str, Any]:
    """Create a new transaction"""
    items = items or []
    
    # Validate customer if provided
    if customer_id:
        customer = business_agent.get_customer(customer_id)
        if not customer:
            return {
                "success": False,
                "error": f"Customer with ID {customer_id} not found"
            }
    
    # Validate transaction type
    try:
        transaction_type = TransactionType(type)
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid transaction type. Use one of: {', '.join([t.value for t in TransactionType])}"
        }
    
    # Validate payment method
    try:
        payment = PaymentMethod(payment_method)
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid payment method. Use one of: {', '.join([p.value for p in PaymentMethod])}"
        }
    
    # Create transaction
    transaction = Transaction(
        customer_id=customer_id,
        type=transaction_type,
        amount=amount,
        payment_method=payment,
        items=items,
        notes=notes
    )
    
    transaction_id = business_agent.add_transaction(transaction)
    
    # Update inventory if this is a sale or refund
    if transaction_type == TransactionType.SALE or transaction_type == TransactionType.REFUND:
        for item in items:
            if "item_id" in item and "quantity" in item:
                item_id = item["item_id"]
                quantity = item["quantity"]
                
                # For sales, decrease inventory; for refunds, increase inventory
                quantity_change = -quantity if transaction_type == TransactionType.SALE else quantity
                
                await inventory_update(
                    business_agent=business_agent,
                    item_id=item_id,
                    quantity_change=quantity_change,
                    reason=f"{transaction_type.value} transaction {transaction_id}"
                )
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "transaction": transaction.dict()
    }

# Analytics tools
@tool(
    name="sales_analytics",
    description="Generate sales analytics for a time period",
    category=ToolCategory.ANALYTICS
)
async def sales_analytics(
    business_agent: Any,
    start_date: str,  # ISO format: YYYY-MM-DD
    end_date: str,  # ISO format: YYYY-MM-DD
    group_by: str = "day"  # day, week, month
) -> Dict[str, Any]:
    """Generate sales analytics for a time period"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        return {
            "success": False,
            "error": "Invalid date format. Use ISO format: YYYY-MM-DD"
        }
    
    # Filter transactions within date range
    transactions = [
        t for t in business_agent.transactions.values()
        if start <= t.timestamp <= end and t.type == TransactionType.SALE
    ]
    
    # Group by time period
    grouped_data = {}
    
    for transaction in transactions:
        if group_by == "day":
            key = transaction.timestamp.strftime("%Y-%m-%d")
        elif group_by == "week":
            # ISO week format: YYYY-WW
            key = f"{transaction.timestamp.isocalendar()[0]}-{transaction.timestamp.isocalendar()[1]:02d}"
        elif group_by == "month":
            key = transaction.timestamp.strftime("%Y-%m")
        else:
            return {
                "success": False,
                "error": "Invalid group_by parameter. Use 'day', 'week', or 'month'"
            }
        
        if key not in grouped_data:
            grouped_data[key] = {
                "total_sales": 0,
                "transaction_count": 0,
                "item_count": 0
            }
        
        grouped_data[key]["total_sales"] += transaction.amount
        grouped_data[key]["transaction_count"] += 1
        grouped_data[key]["item_count"] += len(transaction.items)
    
    # Calculate overall metrics
    total_sales = sum(data["total_sales"] for data in grouped_data.values())
    total_transactions = sum(data["transaction_count"] for data in grouped_data.values())
    total_items = sum(data["item_count"] for data in grouped_data.values())
    
    average_transaction = total_sales / total_transactions if total_transactions > 0 else 0
    
    return {
        "success": True,
        "period": {
            "start": start_date,
            "end": end_date,
            "group_by": group_by
        },
        "overall": {
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "total_items": total_items,
            "average_transaction": average_transaction
        },
        "data": grouped_data
    }

# Register all business tools
def register_business_tools(registry: ToolRegistry) -> None:
    """Register all business tools with the tool registry"""
    # Customer tools
    registry.register_tool(customer_search.tool)
    registry.register_tool(customer_add.tool)
    
    # Inventory tools
    registry.register_tool(inventory_search.tool)
    registry.register_tool(inventory_add.tool)
    registry.register_tool(inventory_update.tool)
    
    # Appointment tools
    registry.register_tool(appointment_schedule.tool)
    registry.register_tool(appointment_update.tool)
    
    # Transaction tools
    registry.register_tool(transaction_create.tool)
    
    # Analytics tools
    registry.register_tool(sales_analytics.tool) 