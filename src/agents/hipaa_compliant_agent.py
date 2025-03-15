from typing import Dict, Any, List
from datetime import datetime
import logging
from .base_agent import BaseBusinessAgent

logger = logging.getLogger(__name__)

class HIPAACompliantAgent(BaseBusinessAgent):
    """Agent class with HIPAA compliance features"""
    
    def __init__(self, name: str, system_message: str = None, tools: List[Dict[str, Any]] = None):
        super().__init__(name, system_message, tools)
        self.phi_access_log = []
        
    def log_phi_access(self, data_type: str, action: str, reason: str):
        """Log access to Protected Health Information (PHI)"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "data_type": data_type,
            "action": action,
            "reason": reason
        }
        self.phi_access_log.append(log_entry)
        logger.info(f"PHI Access: {action} - {data_type} by {self.name}")
        
    def get_phi_access_log(self) -> List[Dict[str, Any]]:
        """Get the PHI access log"""
        return self.phi_access_log
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with PHI logging"""
        try:
            # Log PHI access if the tool handles sensitive data
            if any(phi_term in tool_name.lower() for phi_term in ["health", "medical", "patient", "phi"]):
                self.log_phi_access(
                    data_type=tool_name,
                    action="tool_execution",
                    reason=kwargs.get("reason", "Business operation")
                )
            
            return await super().execute_tool(tool_name, **kwargs)
        except Exception as e:
            logger.error(f"HIPAA-compliant tool execution error: {str(e)}")
            raise 