from typing import Dict, Any
from datetime import datetime, timedelta
from .hipaa_compliant_agent import HIPAACompliantAgent

class AppointmentSchedulerAgent(HIPAACompliantAgent):
    """HIPAA-compliant agent for handling appointment scheduling."""
    
    def __init__(self, name: str = "AppointmentScheduler"):
        system_message = """You are a professional appointment scheduler for healthcare and personal services.
        Your responsibilities include:
        1. Scheduling and managing appointments while maintaining HIPAA compliance
        2. Handling scheduling conflicts and rescheduling requests
        3. Sending appointment reminders (through secure channels only)
        4. Managing cancellations and wait lists
        5. Ensuring proper spacing between appointments for cleaning/preparation
        """
        
        # Define appointment-specific tools
        tools = [
            {
                "name": "check_availability",
                "description": "Check available time slots",
                "func": self.check_availability
            },
            {
                "name": "schedule_appointment",
                "description": "Schedule a new appointment",
                "func": self.schedule_appointment
            },
            {
                "name": "send_secure_reminder",
                "description": "Send a HIPAA-compliant appointment reminder",
                "func": self.send_secure_reminder
            }
        ]
        
        super().__init__(name=name, system_message=system_message, tools=tools)
    
    async def generate_response(self, task: str, context: Dict[str, Any]) -> str:
        """Generate a response for appointment-related tasks."""
        # Add appointment-specific context
        context.update({
            "service_type": context.get("service_type", "general"),
            "duration_minutes": context.get("duration_minutes", 30),
            "provider_id": context.get("provider_id", "any")
        })
        
        # Process the appointment request
        response = await self.chat(
            task,
            context=context,
            max_consecutive_auto_reply=1
        )
        
        return response
    
    async def check_availability(self, date: str, service_type: str = "general") -> Dict[str, Any]:
        """Check available time slots for a given date."""
        # This would typically connect to a real scheduling system
        # For now, return mock data
        return {
            "date": date,
            "available_slots": [
                "09:00 AM",
                "10:00 AM",
                "02:00 PM",
                "03:00 PM"
            ],
            "service_type": service_type
        }
    
    async def schedule_appointment(
        self,
        date: str,
        time: str,
        service_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule a new appointment."""
        # Verify authorization first
        if not await self.verify_authorization(context):
            return {"error": "Unauthorized access"}
        
        # This would typically connect to a real scheduling system
        appointment = {
            "appointment_id": "AP" + datetime.now().strftime("%Y%m%d%H%M"),
            "date": date,
            "time": time,
            "service_type": service_type,
            "status": "confirmed"
        }
        
        # Log the scheduling action
        await self.log_phi_access(
            f"Scheduled appointment for {date} {time}",
            context
        )
        
        return appointment
    
    async def send_secure_reminder(
        self,
        appointment_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a HIPAA-compliant appointment reminder."""
        # This would typically connect to a secure messaging system
        reminder = {
            "sent": True,
            "method": "secure_message",
            "appointment_id": appointment_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the reminder
        await self.log_phi_access(
            f"Sent reminder for appointment {appointment_id}",
            context
        )
        
        return reminder 