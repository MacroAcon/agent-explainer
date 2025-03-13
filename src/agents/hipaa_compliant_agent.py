from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseBusinessAgent
from ..security.audit_logger import AuditLogger
from ..monitoring.metrics_collector import MetricsCollector
from ..config.config import settings

class HIPAACompliantAgent(BaseBusinessAgent):
    """Agent with enhanced HIPAA compliance and security features."""
    
    def __init__(
        self,
        name: str,
        system_message: str,
        tools: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        # Add HIPAA compliance to system message
        hipaa_message = """
        HIPAA Compliance Requirements:
        1. All data must be handled according to HIPAA privacy standards
        2. PHI must be identified and protected
        3. Access must be logged and authorized
        4. Data must be encrypted in transit and at rest
        5. Minimum necessary principle must be followed
        
        """
        full_message = hipaa_message + system_message
        
        super().__init__(
            name=name,
            system_message=full_message,
            tools=tools,
            **kwargs
        )
        
        # Initialize HIPAA compliance tracking
        self.access_logs = []
        
        # Initialize audit logger with encryption
        self.audit_logger = AuditLogger(
            encryption_key=settings.AUDIT_ENCRYPTION_KEY,
            retention_days=90,
            max_events=10000
        )
        
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector(
            collection_interval=60,
            storage_backend="timeseries",
            alert_thresholds={
                "response_time": 1000,  # ms
                "error_rate": 0.01,
                "memory_usage": 0.8
            }
        )
        
        # Initialize security state
        self.security_state = {
            "last_audit": datetime.now().isoformat(),
            "failed_attempts": 0,
            "locked_until": None,
            "active_sessions": set()
        }
    
    async def generate_response(self, message: Dict[str, Any]) -> str:
        """Generate a HIPAA-compliant response."""
        try:
            # Log access attempt
            self._log_access(message)
            
            # Verify authorization
            if not self._verify_authorization(message["context"]):
                return "Access denied: Insufficient authorization"
            
            # Process with HIPAA compliance
            response = await self._process_hipaa_compliant(message)
            
            return response
            
        except Exception as e:
            self._log_error(str(e), message["context"])
            return f"Error in HIPAA-compliant processing: {str(e)}"
    
    def _log_access(self, message: Dict[str, Any]) -> None:
        """Log access to PHI data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "action": "data_access",
            "user_id": message["context"].get("user_id"),
            "access_level": message["context"].get("access_level"),
            "data_type": message["context"].get("data_type", "business_data")
        }
        self.access_logs.append(log_entry)
    
    def _verify_authorization(self, context: Dict[str, Any]) -> bool:
        """Verify user authorization for data access."""
        access_level = context.get("access_level", "none")
        user_id = context.get("user_id")
        
        if not user_id:
            return False
            
        # Basic access level verification
        return access_level in ["admin", "write", "read"]
    
    async def _process_hipaa_compliant(self, message: Dict[str, Any]) -> str:
        """Process request with HIPAA compliance measures."""
        try:
            # Check security state
            if not self._check_security_state():
                return self._create_security_error("Account locked")
            
            # Start timing for metrics
            start_time = datetime.now()
            
            # Log access attempt
            self.audit_logger.log_event(
                event_type="access_attempt",
                agent_id=self.name,
                action="process_task",
                details={
                    "task": message["content"],
                    "context": self._sanitize_context(message["context"]),
                    "ip_address": message["context"].get("ip_address"),
                    "user_id": message["context"].get("user_id")
                },
                severity="info"
            )
            
            # Process the task using parent class
            result = await super().process_task(message["content"], message["context"])
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            # Record metrics
            self.metrics_collector.record_agent_metrics(
                agent_id=self.name,
                tasks_processed=1,
                errors=0 if result.get("status") == "completed" else 1,
                avg_response_time=processing_time,
                memory_usage=self._get_memory_usage()
            )
            
            # Log successful processing
            self.audit_logger.log_event(
                event_type="task_completed",
                agent_id=self.name,
                action="process_task",
                details={
                    "task": message["content"],
                    "processing_time": processing_time,
                    "status": result.get("status")
                },
                severity="info"
            )
            
            return result.get("response", "No response generated")
            
        except Exception as e:
            # Log error
            self.audit_logger.log_event(
                event_type="error",
                agent_id=self.name,
                action="process_task",
                details={
                    "error": str(e),
                    "task": message["content"],
                    "context": self._sanitize_context(message["context"])
                },
                severity="error"
            )
            
            # Record error metrics
            self.metrics_collector.record_agent_metrics(
                agent_id=self.name,
                tasks_processed=0,
                errors=1,
                avg_response_time=0,
                memory_usage=self._get_memory_usage()
            )
            
            return self._create_error_response(str(e))
    
    def _check_security_state(self) -> bool:
        """Check if the agent is in a secure state to process tasks."""
        now = datetime.now()
        
        # Check if account is locked
        if self.security_state["locked_until"]:
            locked_until = datetime.fromisoformat(self.security_state["locked_until"])
            if now < locked_until:
                return False
        
        # Reset failed attempts if enough time has passed
        if self.security_state["failed_attempts"] > 0:
            last_audit = datetime.fromisoformat(self.security_state["last_audit"])
            if (now - last_audit).total_seconds() > 3600:  # Reset after 1 hour
                self.security_state["failed_attempts"] = 0
        
        return True
    
    def _create_security_error(self, message: str) -> Dict[str, Any]:
        """Create a security-related error response."""
        return {
            "agent": self.name,
            "role": self.__class__.__name__,
            "status": "security_error",
            "error": message,
            "timestamp": datetime.now().isoformat(),
            "security_state": self.security_state
        }
    
    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create a general error response."""
        return {
            "agent": self.name,
            "role": self.__class__.__name__,
            "status": "error",
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize context data to remove sensitive information."""
        if not context:
            return {}
        
        sanitized = context.copy()
        
        # Remove sensitive fields
        sensitive_fields = [
            "password", "token", "api_key", "secret",
            "credit_card", "ssn", "phone_number", "address"
        ]
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        return sanitized
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage of the agent."""
        # In a production environment, implement proper memory tracking
        return 0.0  # Placeholder
    
    async def get_security_report(self) -> Dict[str, Any]:
        """Get a security report for the agent."""
        return {
            "security_state": self.security_state,
            "audit_metrics": self.audit_logger.get_security_metrics(),
            "performance_metrics": self.metrics_collector.get_metrics_summary(),
            "last_audit": self.security_state["last_audit"]
        }
    
    async def perform_security_audit(self) -> Dict[str, Any]:
        """Perform a security audit of the agent."""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.name,
            "checks": {
                "memory_usage": self._get_memory_usage() < 0.8,
                "failed_attempts": self.security_state["failed_attempts"] < 5,
                "active_sessions": len(self.security_state["active_sessions"]) < 10,
                "audit_logging": len(self.audit_logger.get_events()) > 0,
                "metrics_collection": len(self.metrics_collector.get_metrics_summary()["alerts"]) == 0
            },
            "recommendations": []
        }
        
        # Generate recommendations based on audit results
        if not audit_results["checks"]["memory_usage"]:
            audit_results["recommendations"].append("High memory usage detected")
        
        if not audit_results["checks"]["failed_attempts"]:
            audit_results["recommendations"].append("Multiple failed access attempts detected")
        
        if not audit_results["checks"]["active_sessions"]:
            audit_results["recommendations"].append("Too many active sessions")
        
        if not audit_results["checks"]["audit_logging"]:
            audit_results["recommendations"].append("No audit logs found")
        
        if not audit_results["checks"]["metrics_collection"]:
            audit_results["recommendations"].append("Performance alerts detected")
        
        # Update security state
        self.security_state["last_audit"] = audit_results["timestamp"]
        
        return audit_results
    
    def get_access_logs(self) -> List[Dict[str, Any]]:
        """Get the HIPAA compliance access logs."""
        return self.access_logs 