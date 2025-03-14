from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid

from .agent_core import StructuredAgent, AgentRole, MemoryType
from .tool_framework import ToolRegistry, tool, ToolCategory

# Setup logging
logger = logging.getLogger(__name__)

# Define business types
class BusinessType(str, Enum):
    RETAIL = "retail"
    RESTAURANT = "restaurant"
    SERVICE = "service"
    HEALTHCARE = "healthcare"
    PROFESSIONAL = "professional"
    OTHER = "other"

# Define business profile
class BusinessProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: BusinessType
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    hours: Dict[str, str] = Field(default_factory=dict)
    social_media: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define customer model
class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    notes: str = ""
    purchase_history: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define inventory item model
class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    cost: Optional[float] = None
    quantity: int
    reorder_point: Optional[int] = None
    supplier: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define appointment model
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    service_id: str
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Define transaction model
class TransactionType(str, Enum):
    SALE = "sale"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    PAYMENT = "payment"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    MOBILE_PAYMENT = "mobile_payment"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    OTHER = "other"

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: Optional[str] = None
    type: TransactionType
    amount: float
    payment_method: PaymentMethod
    items: List[Dict[str, Any]] = Field(default_factory=list)
    notes: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Business Agent class
class BusinessAgent(StructuredAgent):
    """
    Extended agent class with business-specific capabilities
    """
    
    def __init__(
        self,
        name: str,
        business_profile: BusinessProfile,
        role: AgentRole = AgentRole.SPECIALIST,
        system_message: str = None
    ):
        # Generate appropriate system message based on business type
        if system_message is None:
            system_message = f"You are a specialized assistant for {business_profile.type.value} businesses. You help manage {business_profile.name}."
        
        super().__init__(name, role, system_message)
        
        # Add business-specific attributes
        self.business_profile = business_profile
        self.customers: Dict[str, Customer] = {}
        self.inventory: Dict[str, InventoryItem] = {}
        self.appointments: Dict[str, Appointment] = {}
        self.transactions: Dict[str, Transaction] = {}
    
    def add_customer(self, customer: Customer) -> str:
        """Add a customer to the business"""
        self.customers[customer.id] = customer
        
        # Add to memory
        self.add_memory(
            content=f"Added customer: {customer.first_name} {customer.last_name}",
            memory_type=MemoryType.LONG_TERM,
            metadata={"customer_id": customer.id}
        )
        
        return customer.id
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get a customer by ID"""
        return self.customers.get(customer_id)
    
    def add_inventory_item(self, item: InventoryItem) -> str:
        """Add an inventory item to the business"""
        self.inventory[item.id] = item
        
        # Add to memory
        self.add_memory(
            content=f"Added inventory item: {item.name}",
            memory_type=MemoryType.LONG_TERM,
            metadata={"item_id": item.id}
        )
        
        return item.id
    
    def get_inventory_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get an inventory item by ID"""
        return self.inventory.get(item_id)
    
    def add_appointment(self, appointment: Appointment) -> str:
        """Add an appointment to the business"""
        self.appointments[appointment.id] = appointment
        
        # Add to memory
        self.add_memory(
            content=f"Added appointment for customer {appointment.customer_id}",
            memory_type=MemoryType.EPISODIC,
            metadata={"appointment_id": appointment.id}
        )
        
        return appointment.id
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get an appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def add_transaction(self, transaction: Transaction) -> str:
        """Add a transaction to the business"""
        self.transactions[transaction.id] = transaction
        
        # Add to memory
        self.add_memory(
            content=f"Added {transaction.type.value} transaction for ${transaction.amount}",
            memory_type=MemoryType.EPISODIC,
            metadata={"transaction_id": transaction.id}
        )
        
        return transaction.id
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction by ID"""
        return self.transactions.get(transaction_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert business agent to dictionary for serialization"""
        base_dict = super().to_dict()
        
        business_dict = {
            "business_profile": self.business_profile.dict(),
            "customer_count": len(self.customers),
            "inventory_count": len(self.inventory),
            "appointment_count": len(self.appointments),
            "transaction_count": len(self.transactions)
        }
        
        return {**base_dict, **business_dict} 