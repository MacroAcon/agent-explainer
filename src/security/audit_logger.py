from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
import hmac
from dataclasses import dataclass
from ..config.enhanced_settings import enhanced_settings

@dataclass
class AuditEvent:
    """Represents a security audit event."""
    event_type: str
    timestamp: str
    agent_id: str
    action: str
    details: Dict[str, Any]
    severity: str
    ip_address: Optional[str] = None
    user_id: Optional[str] = None

class AuditLogger:
    """Handles security audit logging with encryption and retention policies."""
    
    def __init__(
        self,
        encryption_key: str,
        retention_days: int = 90,
        max_events: int = 10000
    ):
        self.encryption_key = encryption_key
        self.retention_days = retention_days
        self.max_events = max_events
        self.events = []
        self.last_cleanup = datetime.now()
    
    def _generate_hmac(self, data: str) -> str:
        """Generate HMAC for data integrity verification."""
        return hmac.new(
            self.encryption_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt sensitive data using the encryption key."""
        # In a production environment, use proper encryption (e.g., AES)
        # This is a simplified version for demonstration
        data_str = json.dumps(data, sort_keys=True)
        return self._generate_hmac(data_str)
    
    def _decrypt_data(self, encrypted_data: str) -> Optional[Dict[str, Any]]:
        """Decrypt data and verify integrity."""
        # In a production environment, implement proper decryption
        # This is a placeholder for demonstration
        return {"encrypted": True, "data": encrypted_data}
    
    def log_event(
        self,
        event_type: str,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        severity: str = "info",
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Log a security audit event."""
        # Create audit event
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            action=action,
            details=details,
            severity=severity,
            ip_address=ip_address,
            user_id=user_id
        )
        
        # Encrypt sensitive data
        encrypted_details = self._encrypt_data(event.details)
        
        # Store event
        self.events.append({
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "agent_id": event.agent_id,
            "action": event.action,
            "details": encrypted_details,
            "severity": event.severity,
            "ip_address": event.ip_address,
            "user_id": event.user_id
        })
        
        # Cleanup if needed
        self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up old events based on retention policy."""
        now = datetime.now()
        
        # Check if cleanup is needed
        if (now - self.last_cleanup).total_seconds() < 3600:  # Cleanup every hour
            return
        
        # Remove events older than retention period
        cutoff_date = now - timedelta(days=self.retention_days)
        self.events = [
            event for event in self.events
            if datetime.fromisoformat(event["timestamp"]) > cutoff_date
        ]
        
        # Remove excess events if over max_events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        self.last_cleanup = now
    
    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve filtered audit events."""
        filtered_events = self.events
        
        if start_date:
            filtered_events = [
                event for event in filtered_events
                if datetime.fromisoformat(event["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_events = [
                event for event in filtered_events
                if datetime.fromisoformat(event["timestamp"]) <= end_date
            ]
        
        if event_type:
            filtered_events = [
                event for event in filtered_events
                if event["event_type"] == event_type
            ]
        
        if severity:
            filtered_events = [
                event for event in filtered_events
                if event["severity"] == severity
            ]
        
        if agent_id:
            filtered_events = [
                event for event in filtered_events
                if event["agent_id"] == agent_id
            ]
        
        # Decrypt details for each event
        for event in filtered_events:
            event["details"] = self._decrypt_data(event["details"])
        
        return filtered_events
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security-related metrics."""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [
            event for event in self.events
            if datetime.fromisoformat(event["timestamp"]) > last_24h
        ]
        
        return {
            "total_events": len(self.events),
            "events_last_24h": len(recent_events),
            "events_by_type": self._count_by_type(recent_events),
            "events_by_severity": self._count_by_severity(recent_events),
            "events_by_agent": self._count_by_agent(recent_events)
        }
    
    def _count_by_type(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for event in events:
            counts[event["event_type"]] = counts.get(event["event_type"], 0) + 1
        return counts
    
    def _count_by_severity(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count events by severity."""
        counts = {}
        for event in events:
            counts[event["severity"]] = counts.get(event["severity"], 0) + 1
        return counts
    
    def _count_by_agent(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count events by agent."""
        counts = {}
        for event in events:
            counts[event["agent_id"]] = counts.get(event["agent_id"], 0) + 1
        return counts 