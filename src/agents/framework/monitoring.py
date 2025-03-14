from typing import Dict, List, Any, Optional, Union, Callable
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import threading
from collections import defaultdict, deque

# Setup logging
logger = logging.getLogger(__name__)

# Define event types
class EventType(str, Enum):
    AGENT_CREATED = "agent_created"
    AGENT_DESTROYED = "agent_destroyed"
    AGENT_STATE_CHANGED = "agent_state_changed"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TOOL_EXECUTED = "tool_executed"
    MEMORY_ADDED = "memory_added"
    MEMORY_RETRIEVED = "memory_retrieved"
    CONVERSATION_CREATED = "conversation_created"
    CONVERSATION_MESSAGE_ADDED = "conversation_message_added"
    CONVERSATION_STATE_CHANGED = "conversation_state_changed"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CUSTOM = "custom"

# Define event severity
class EventSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Define structured event
class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    severity: EventSeverity = EventSeverity.INFO
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }

# Define metric types
class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

# Define structured metric
class Metric(BaseModel):
    name: str
    type: MetricType
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    labels: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for serialization"""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "metadata": self.metadata
        }

# Define event handler
class EventHandler(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    event_types: List[EventType]
    handler: Callable
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

# Define metric aggregation
class MetricAggregation(BaseModel):
    name: str
    metric_name: str
    aggregation_type: str  # sum, avg, min, max, count
    window: timedelta
    labels: Dict[str, str] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregation to dictionary for serialization"""
        return {
            "name": self.name,
            "metric_name": self.metric_name,
            "aggregation_type": self.aggregation_type,
            "window": self.window.total_seconds(),
            "labels": self.labels
        }

# Monitoring system
class MonitoringSystem:
    """System for monitoring agent performance and behaviors"""
    
    def __init__(self, max_events: int = 10000, max_metrics: int = 10000):
        self.events: deque = deque(maxlen=max_events)
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self.event_handlers: Dict[str, EventHandler] = {}
        self.metric_aggregations: Dict[str, MetricAggregation] = {}
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Setup background aggregation thread
        self.running = True
        self.aggregation_thread = threading.Thread(target=self._aggregate_metrics_loop)
        self.aggregation_thread.daemon = True
        self.aggregation_thread.start()
    
    def record_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any] = None,
        severity: EventSeverity = EventSeverity.INFO,
        metadata: Dict[str, Any] = None
    ) -> Event:
        """Record an event"""
        data = data or {}
        metadata = metadata or {}
        
        event = Event(
            type=event_type,
            severity=severity,
            source=source,
            data=data,
            metadata=metadata
        )
        
        self.events.append(event)
        
        # Process event handlers
        for handler in self.event_handlers.values():
            if event_type in handler.event_types:
                try:
                    handler.handler(event)
                except Exception as e:
                    logger.exception(f"Error in event handler {handler.name}: {str(e)}")
        
        return event
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ) -> Metric:
        """Record a metric"""
        labels = labels or {}
        metadata = metadata or {}
        
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels,
            metadata=metadata
        )
        
        self.metrics[name].append(metric)
        
        return metric
    
    def register_event_handler(
        self,
        name: str,
        event_types: List[EventType],
        handler: Callable,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Register an event handler"""
        metadata = metadata or {}
        
        event_handler = EventHandler(
            name=name,
            event_types=event_types,
            handler=handler,
            metadata=metadata
        )
        
        self.event_handlers[event_handler.id] = event_handler
        return event_handler.id
    
    def unregister_event_handler(self, handler_id: str) -> bool:
        """Unregister an event handler"""
        if handler_id in self.event_handlers:
            del self.event_handlers[handler_id]
            return True
        return False
    
    def register_metric_aggregation(
        self,
        name: str,
        metric_name: str,
        aggregation_type: str,
        window: timedelta,
        labels: Dict[str, str] = None
    ) -> None:
        """Register a metric aggregation"""
        labels = labels or {}
        
        aggregation = MetricAggregation(
            name=name,
            metric_name=metric_name,
            aggregation_type=aggregation_type,
            window=window,
            labels=labels
        )
        
        self.metric_aggregations[name] = aggregation
    
    def unregister_metric_aggregation(self, name: str) -> bool:
        """Unregister a metric aggregation"""
        if name in self.metric_aggregations:
            del self.metric_aggregations[name]
            if name in self.aggregated_metrics:
                del self.aggregated_metrics[name]
            return True
        return False
    
    def get_events(
        self,
        event_types: Optional[List[EventType]] = None,
        sources: Optional[List[str]] = None,
        severity: Optional[EventSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """Get events with filtering"""
        events = list(self.events)
        
        # Apply filters
        if event_types:
            events = [e for e in events if e.type in event_types]
        
        if sources:
            events = [e for e in events if e.source in sources]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply limit
        if limit is not None:
            events = events[:limit]
        
        return events
    
    def get_metrics(
        self,
        names: Optional[List[str]] = None,
        metric_types: Optional[List[MetricType]] = None,
        labels: Optional[Dict[str, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Dict[str, List[Metric]]:
        """Get metrics with filtering"""
        result = {}
        
        # Determine which metrics to include
        metric_names = names if names else list(self.metrics.keys())
        
        for name in metric_names:
            if name not in self.metrics:
                continue
            
            metrics = list(self.metrics[name])
            
            # Apply filters
            if metric_types:
                metrics = [m for m in metrics if m.type in metric_types]
            
            if labels:
                metrics = [
                    m for m in metrics 
                    if all(m.labels.get(k) == v for k, v in labels.items())
                ]
            
            if start_time:
                metrics = [m for m in metrics if m.timestamp >= start_time]
            
            if end_time:
                metrics = [m for m in metrics if m.timestamp <= end_time]
            
            # Sort by timestamp (newest first)
            metrics.sort(key=lambda m: m.timestamp, reverse=True)
            
            # Apply limit
            if limit is not None:
                metrics = metrics[:limit]
            
            if metrics:
                result[name] = metrics
        
        return result
    
    def get_aggregated_metrics(self, names: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Get aggregated metrics"""
        if names:
            return {name: self.aggregated_metrics.get(name, {}) for name in names}
        return self.aggregated_metrics
    
    def _aggregate_metrics_loop(self) -> None:
        """Background thread for metric aggregation"""
        while self.running:
            try:
                self._aggregate_metrics()
            except Exception as e:
                logger.exception(f"Error in metric aggregation: {str(e)}")
            
            # Sleep for a short time
            time.sleep(1)
    
    def _aggregate_metrics(self) -> None:
        """Aggregate metrics based on registered aggregations"""
        now = datetime.now()
        
        for name, aggregation in self.metric_aggregations.items():
            if aggregation.metric_name not in self.metrics:
                continue
            
            # Get metrics within the window
            window_start = now - aggregation.window
            metrics = [
                m for m in self.metrics[aggregation.metric_name]
                if m.timestamp >= window_start
            ]
            
            # Apply label filtering
            if aggregation.labels:
                metrics = [
                    m for m in metrics 
                    if all(m.labels.get(k) == v for k, v in aggregation.labels.items())
                ]
            
            # Skip if no metrics
            if not metrics:
                continue
            
            # Calculate aggregation
            values = [m.value for m in metrics]
            
            if aggregation.aggregation_type == "sum":
                value = sum(values)
            elif aggregation.aggregation_type == "avg":
                value = sum(values) / len(values) if values else 0
            elif aggregation.aggregation_type == "min":
                value = min(values) if values else 0
            elif aggregation.aggregation_type == "max":
                value = max(values) if values else 0
            elif aggregation.aggregation_type == "count":
                value = len(values)
            else:
                logger.warning(f"Unknown aggregation type: {aggregation.aggregation_type}")
                continue
            
            # Store aggregated metric
            self.aggregated_metrics[name] = {
                "name": name,
                "value": value,
                "timestamp": now.isoformat(),
                "window": aggregation.window.total_seconds(),
                "metric_count": len(metrics)
            }
    
    def shutdown(self) -> None:
        """Shutdown the monitoring system"""
        self.running = False
        if self.aggregation_thread.is_alive():
            self.aggregation_thread.join(timeout=5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert monitoring system to dictionary for serialization"""
        return {
            "events_count": len(self.events),
            "metrics_count": sum(len(m) for m in self.metrics.values()),
            "event_handlers": len(self.event_handlers),
            "metric_aggregations": len(self.metric_aggregations),
            "aggregated_metrics": len(self.aggregated_metrics)
        }

# Utility functions for common monitoring tasks
def create_performance_monitoring(monitoring_system: MonitoringSystem) -> None:
    """Setup performance monitoring aggregations"""
    # Response time aggregations
    monitoring_system.register_metric_aggregation(
        name="avg_response_time_1m",
        metric_name="response_time",
        aggregation_type="avg",
        window=timedelta(minutes=1)
    )
    
    monitoring_system.register_metric_aggregation(
        name="avg_response_time_5m",
        metric_name="response_time",
        aggregation_type="avg",
        window=timedelta(minutes=5)
    )
    
    monitoring_system.register_metric_aggregation(
        name="avg_response_time_1h",
        metric_name="response_time",
        aggregation_type="avg",
        window=timedelta(hours=1)
    )
    
    # Task count aggregations
    monitoring_system.register_metric_aggregation(
        name="tasks_completed_1m",
        metric_name="task_completed",
        aggregation_type="count",
        window=timedelta(minutes=1)
    )
    
    monitoring_system.register_metric_aggregation(
        name="tasks_failed_1m",
        metric_name="task_failed",
        aggregation_type="count",
        window=timedelta(minutes=1)
    )
    
    # Error rate aggregation
    monitoring_system.register_metric_aggregation(
        name="error_rate_5m",
        metric_name="error",
        aggregation_type="count",
        window=timedelta(minutes=5)
    )

def create_agent_monitoring(monitoring_system: MonitoringSystem, agent_id: str) -> None:
    """Setup agent-specific monitoring aggregations"""
    # Agent-specific response time
    monitoring_system.register_metric_aggregation(
        name=f"agent_{agent_id}_avg_response_time_5m",
        metric_name="response_time",
        aggregation_type="avg",
        window=timedelta(minutes=5),
        labels={"agent_id": agent_id}
    )
    
    # Agent-specific task count
    monitoring_system.register_metric_aggregation(
        name=f"agent_{agent_id}_tasks_completed_5m",
        metric_name="task_completed",
        aggregation_type="count",
        window=timedelta(minutes=5),
        labels={"agent_id": agent_id}
    )
    
    # Agent-specific error rate
    monitoring_system.register_metric_aggregation(
        name=f"agent_{agent_id}_error_rate_5m",
        metric_name="error",
        aggregation_type="count",
        window=timedelta(minutes=5),
        labels={"agent_id": agent_id}
    )

def log_agent_activity(monitoring_system: MonitoringSystem, agent_id: str, activity: str, data: Dict[str, Any] = None) -> None:
    """Log agent activity as an event"""
    data = data or {}
    
    monitoring_system.record_event(
        event_type=EventType.INFO,
        source=f"agent:{agent_id}",
        data={
            "activity": activity,
            **data
        }
    )

def record_response_time(monitoring_system: MonitoringSystem, agent_id: str, response_time: float) -> None:
    """Record agent response time"""
    monitoring_system.record_metric(
        name="response_time",
        value=response_time,
        metric_type=MetricType.HISTOGRAM,
        labels={"agent_id": agent_id}
    )

def record_task_completion(monitoring_system: MonitoringSystem, agent_id: str, task_id: str, success: bool) -> None:
    """Record task completion status"""
    if success:
        monitoring_system.record_metric(
            name="task_completed",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"agent_id": agent_id, "task_id": task_id}
        )
    else:
        monitoring_system.record_metric(
            name="task_failed",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"agent_id": agent_id, "task_id": task_id}
        )

def record_error(monitoring_system: MonitoringSystem, source: str, error_message: str, severity: EventSeverity = EventSeverity.ERROR) -> None:
    """Record an error"""
    monitoring_system.record_event(
        event_type=EventType.ERROR,
        source=source,
        data={"message": error_message},
        severity=severity
    )
    
    monitoring_system.record_metric(
        name="error",
        value=1,
        metric_type=MetricType.COUNTER,
        labels={"source": source}
    ) 