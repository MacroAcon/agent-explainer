from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import json
from dataclasses import dataclass
from collections import defaultdict
import asyncio
from ..config.enhanced_settings import enhanced_settings

@dataclass
class SystemMetrics:
    """Represents system-level metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    timestamp: str

@dataclass
class PerformanceMetrics:
    """Represents performance-related metrics."""
    response_times: List[float]
    error_rates: List[float]
    throughput: int
    active_tasks: int
    queue_size: int
    timestamp: str

@dataclass
class AgentMetrics:
    """Represents agent-specific metrics."""
    agent_id: str
    tasks_processed: int
    errors: int
    avg_response_time: float
    memory_usage: float
    timestamp: str

class MetricsCollector:
    """Collects and manages system, performance, and agent metrics."""
    
    def __init__(
        self,
        collection_interval: int = 60,
        storage_backend: str = "timeseries",
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        self.collection_interval = collection_interval
        self.storage_backend = storage_backend
        self.alert_thresholds = alert_thresholds or {
            "cpu_percent": 80.0,
            "memory_percent": 80.0,
            "disk_usage": 90.0,
            "response_time": 1000.0,  # ms
            "error_rate": 0.01
        }
        
        # Initialize metric storage
        self.system_metrics = []
        self.performance_metrics = []
        self.agent_metrics = defaultdict(list)
        self.alerts = []
        
        # Start collection task
        self.collection_task = asyncio.create_task(self._collect_metrics())
    
    async def _collect_metrics(self):
        """Continuously collect metrics at specified intervals."""
        while True:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Check for system alerts
                self._check_system_alerts(system_metrics)
                
                # Cleanup old metrics
                self._cleanup_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self._log_error("metrics_collection", str(e))
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics."""
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_io={
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            },
            process_count=len(psutil.pids()),
            timestamp=datetime.now().isoformat()
        )
    
    def record_performance_metrics(
        self,
        response_times: List[float],
        error_rates: List[float],
        throughput: int,
        active_tasks: int,
        queue_size: int
    ) -> None:
        """Record performance-related metrics."""
        metrics = PerformanceMetrics(
            response_times=response_times,
            error_rates=error_rates,
            throughput=throughput,
            active_tasks=active_tasks,
            queue_size=queue_size,
            timestamp=datetime.now().isoformat()
        )
        
        self.performance_metrics.append(metrics)
        self._check_performance_alerts(metrics)
    
    def record_agent_metrics(
        self,
        agent_id: str,
        tasks_processed: int,
        errors: int,
        avg_response_time: float,
        memory_usage: float
    ) -> None:
        """Record agent-specific metrics."""
        metrics = AgentMetrics(
            agent_id=agent_id,
            tasks_processed=tasks_processed,
            errors=errors,
            avg_response_time=avg_response_time,
            memory_usage=memory_usage,
            timestamp=datetime.now().isoformat()
        )
        
        self.agent_metrics[agent_id].append(metrics)
        self._check_agent_alerts(metrics)
    
    def _check_system_alerts(self, metrics: SystemMetrics) -> None:
        """Check system metrics against alert thresholds."""
        if metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
            self._create_alert("system", "high_cpu", metrics.cpu_percent)
        
        if metrics.memory_percent > self.alert_thresholds["memory_percent"]:
            self._create_alert("system", "high_memory", metrics.memory_percent)
        
        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            self._create_alert("system", "high_disk", metrics.disk_usage)
    
    def _check_performance_alerts(self, metrics: PerformanceMetrics) -> None:
        """Check performance metrics against alert thresholds."""
        avg_response_time = sum(metrics.response_times) / len(metrics.response_times)
        if avg_response_time > self.alert_thresholds["response_time"]:
            self._create_alert("performance", "high_response_time", avg_response_time)
        
        avg_error_rate = sum(metrics.error_rates) / len(metrics.error_rates)
        if avg_error_rate > self.alert_thresholds["error_rate"]:
            self._create_alert("performance", "high_error_rate", avg_error_rate)
    
    def _check_agent_alerts(self, metrics: AgentMetrics) -> None:
        """Check agent metrics against alert thresholds."""
        if metrics.avg_response_time > self.alert_thresholds["response_time"]:
            self._create_alert("agent", f"high_response_time_{metrics.agent_id}", metrics.avg_response_time)
        
        error_rate = metrics.errors / metrics.tasks_processed if metrics.tasks_processed > 0 else 0
        if error_rate > self.alert_thresholds["error_rate"]:
            self._create_alert("agent", f"high_error_rate_{metrics.agent_id}", error_rate)
    
    def _create_alert(self, category: str, alert_type: str, value: float) -> None:
        """Create a new alert."""
        alert = {
            "category": category,
            "type": alert_type,
            "value": value,
            "threshold": self.alert_thresholds.get(alert_type, 0),
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
    
    def _cleanup_metrics(self) -> None:
        """Clean up old metrics based on retention policy."""
        now = datetime.now()
        cutoff = now - timedelta(hours=24)  # Keep 24 hours of metrics
        
        # Cleanup system metrics
        self.system_metrics = [
            m for m in self.system_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        # Cleanup performance metrics
        self.performance_metrics = [
            m for m in self.performance_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        # Cleanup agent metrics
        for agent_id in list(self.agent_metrics.keys()):
            self.agent_metrics[agent_id] = [
                m for m in self.agent_metrics[agent_id]
                if datetime.fromisoformat(m.timestamp) > cutoff
            ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        
        # Get recent metrics
        recent_system = [
            m for m in self.system_metrics
            if datetime.fromisoformat(m.timestamp) > last_hour
        ]
        
        recent_performance = [
            m for m in self.performance_metrics
            if datetime.fromisoformat(m.timestamp) > last_hour
        ]
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_system) / len(recent_system) if recent_system else 0
        avg_memory = sum(m.memory_percent for m in recent_system) / len(recent_system) if recent_system else 0
        avg_response_time = sum(m.avg_response_time for m in recent_performance) / len(recent_performance) if recent_performance else 0
        
        return {
            "system": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "disk_usage": recent_system[-1].disk_usage if recent_system else 0,
                "process_count": recent_system[-1].process_count if recent_system else 0
            },
            "performance": {
                "avg_response_time": avg_response_time,
                "active_tasks": recent_performance[-1].active_tasks if recent_performance else 0,
                "queue_size": recent_performance[-1].queue_size if recent_performance else 0
            },
            "agents": {
                agent_id: {
                    "tasks_processed": metrics[-1].tasks_processed if metrics else 0,
                    "errors": metrics[-1].errors if metrics else 0,
                    "avg_response_time": metrics[-1].avg_response_time if metrics else 0
                }
                for agent_id, metrics in self.agent_metrics.items()
            },
            "alerts": self.alerts[-10:] if self.alerts else []  # Last 10 alerts
        }
    
    def _log_error(self, context: str, error: str) -> None:
        """Log an error with context."""
        print(f"Error in {context}: {error}")
        # In production, use proper logging 