from typing import Dict, Any, List
from datetime import datetime, timedelta
from .hipaa_compliant_agent import HIPAACompliantAgent

class MedicalRecordsAgent(HIPAACompliantAgent):
    """HIPAA-compliant agent for managing medical records."""
    
    def __init__(self, name: str = "MedicalRecords"):
        system_message = """You are a medical records management specialist.
        Your responsibilities include:
        1. Managing and organizing medical records while maintaining strict HIPAA compliance
        2. Processing record requests and transfers securely
        3. Ensuring proper documentation of all record access
        4. Maintaining data retention policies
        5. Coordinating with other healthcare providers for record sharing
        """
        
        # Define medical records specific tools
        tools = [
            {
                "name": "retrieve_records",
                "description": "Retrieve medical records for a patient",
                "func": self.retrieve_records
            },
            {
                "name": "update_records",
                "description": "Update medical records with new information",
                "func": self.update_records
            },
            {
                "name": "process_record_request",
                "description": "Process a request for medical records transfer",
                "func": self.process_record_request
            }
        ]
        
        super().__init__(name=name, system_message=system_message, tools=tools)
    
    async def generate_response(self, task: str, context: Dict[str, Any]) -> str:
        """Generate a response for medical records tasks."""
        # Add records-specific context
        context.update({
            "request_type": context.get("request_type", "view"),
            "record_type": context.get("record_type", "general"),
            "requesting_provider": context.get("requesting_provider", None)
        })
        
        # Ensure proper authorization level for the request type
        required_level = self._get_required_access_level(context["request_type"])
        if context.get("access_level", "") != required_level:
            return f"Error: This operation requires {required_level} access level."
        
        # Process the records request
        response = await self.chat(
            task,
            context=context,
            max_consecutive_auto_reply=1
        )
        
        return response
    
    async def retrieve_records(
        self,
        patient_id: str,
        record_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve medical records for a patient."""
        # Verify authorization first
        if not await self.verify_authorization(context):
            return {"error": "Unauthorized access"}
        
        # This would typically connect to a secure medical records system
        # For now, return mock data structure
        records = {
            "patient_id": patient_id,
            "record_type": record_type,
            "timestamp": datetime.utcnow().isoformat(),
            "records": "[REDACTED PHI] Medical records would appear here"
        }
        
        # Log the access
        await self.log_phi_access(
            f"Retrieved {record_type} records for patient",
            context
        )
        
        return records
    
    async def update_records(
        self,
        patient_id: str,
        record_type: str,
        update_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update medical records with new information."""
        # Verify authorization and access level
        if not await self.verify_authorization(context):
            return {"error": "Unauthorized access"}
        
        if context.get("access_level") != "write":
            return {"error": "Write access required for this operation"}
        
        # This would typically update a secure medical records system
        update_result = {
            "patient_id": patient_id,
            "record_type": record_type,
            "update_timestamp": datetime.utcnow().isoformat(),
            "status": "updated"
        }
        
        # Log the update
        await self.log_phi_access(
            f"Updated {record_type} records for patient",
            context
        )
        
        return update_result
    
    async def process_record_request(
        self,
        request_id: str,
        requesting_provider: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a request for medical records transfer."""
        # Verify authorization
        if not await self.verify_authorization(context):
            return {"error": "Unauthorized access"}
        
        # This would typically process through a secure records transfer system
        transfer_result = {
            "request_id": request_id,
            "requesting_provider": requesting_provider,
            "status": "processing",
            "estimated_completion": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Log the transfer request
        await self.log_phi_access(
            f"Processed records transfer request to {requesting_provider}",
            context
        )
        
        return transfer_result
    
    def _get_required_access_level(self, request_type: str) -> str:
        """Determine required access level for different request types."""
        access_levels = {
            "view": "read",
            "update": "write",
            "transfer": "admin",
            "delete": "admin"
        }
        return access_levels.get(request_type, "read") 