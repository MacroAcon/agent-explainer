import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentMetrics:
    """Class to track and store metrics for agent performance monitoring."""
    
    def __init__(self):
        self._metrics = {}
        self._lock = threading.Lock()
    
    def record_operation(self, agent_name: str, operation_name: str, duration_ms: float, 
                         success: bool, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Record metrics for an agent operation.
        
        Args:
            agent_name: Name of the agent performing the operation
            operation_name: Name of the operation being performed
            duration_ms: Duration of the operation in milliseconds
            success: Whether the operation was successful
            details: Optional additional details about the operation
        """
        with self._lock:
            # Initialize agent metrics if not exist
            if agent_name not in self._metrics:
                self._metrics[agent_name] = {
                    'operations': {},
                    'total_operations': 0,
                    'successful_operations': 0,
                    'failed_operations': 0,
                    'total_duration_ms': 0,
                    'last_operation_time': None
                }
            
            # Initialize operation metrics if not exist
            if operation_name not in self._metrics[agent_name]['operations']:
                self._metrics[agent_name]['operations'][operation_name] = {
                    'count': 0,
                    'success_count': 0,
                    'failure_count': 0,
                    'total_duration_ms': 0,
                    'min_duration_ms': float('inf'),
                    'max_duration_ms': 0,
                    'details': []
                }
            
            # Update agent metrics
            agent_metrics = self._metrics[agent_name]
            agent_metrics['total_operations'] += 1
            agent_metrics['total_duration_ms'] += duration_ms
            agent_metrics['last_operation_time'] = datetime.now()
            
            if success:
                agent_metrics['successful_operations'] += 1
            else:
                agent_metrics['failed_operations'] += 1
            
            # Update operation metrics
            op_metrics = agent_metrics['operations'][operation_name]
            op_metrics['count'] += 1
            op_metrics['total_duration_ms'] += duration_ms
            op_metrics['min_duration_ms'] = min(op_metrics['min_duration_ms'], duration_ms)
            op_metrics['max_duration_ms'] = max(op_metrics['max_duration_ms'], duration_ms)
            
            if success:
                op_metrics['success_count'] += 1
            else:
                op_metrics['failure_count'] += 1
            
            # Store operation details if provided
            if details:
                # Limit stored details to avoid memory issues
                if len(op_metrics['details']) >= 100:
                    op_metrics['details'].pop(0)
                
                op_metrics['details'].append({
                    'timestamp': datetime.now().isoformat(),
                    'duration_ms': duration_ms,
                    'success': success,
                    'details': details
                })
    
    def get_agent_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for a specific agent or all agents.
        
        Args:
            agent_name: Optional name of the agent to get metrics for.
                        If None, returns metrics for all agents.
        
        Returns:
            Dictionary containing metrics.
        """
        with self._lock:
            if agent_name:
                return self._metrics.get(agent_name, {}).copy()
            else:
                return self._metrics.copy()
    
    def get_operation_metrics(self, agent_name: str, operation_name: str) -> Dict[str, Any]:
        """
        Get metrics for a specific operation of an agent.
        
        Args:
            agent_name: Name of the agent
            operation_name: Name of the operation
        
        Returns:
            Dictionary containing operation metrics.
        """
        with self._lock:
            if agent_name in self._metrics and operation_name in self._metrics[agent_name]['operations']:
                return self._metrics[agent_name]['operations'][operation_name].copy()
            return {}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get a summary of metrics for the entire system.
        
        Returns:
            Dictionary containing system-wide metrics.
        """
        with self._lock:
            total_operations = sum(agent['total_operations'] for agent in self._metrics.values())
            total_success = sum(agent['successful_operations'] for agent in self._metrics.values())
            total_failures = sum(agent['failed_operations'] for agent in self._metrics.values())
            total_duration = sum(agent['total_duration_ms'] for agent in self._metrics.values())
            
            # Find most active agent
            most_active_agent = None
            most_operations = 0
            
            for agent_name, agent_data in self._metrics.items():
                if agent_data['total_operations'] > most_operations:
                    most_operations = agent_data['total_operations']
                    most_active_agent = agent_name
            
            return {
                'total_agents': len(self._metrics),
                'total_operations': total_operations,
                'successful_operations': total_success,
                'failed_operations': total_failures,
                'total_duration_ms': total_duration,
                'success_rate': (total_success / total_operations if total_operations else 0) * 100,
                'most_active_agent': most_active_agent,
                'agent_list': list(self._metrics.keys())
            }
    
    def reset_metrics(self, agent_name: Optional[str] = None) -> None:
        """
        Reset metrics for a specific agent or all agents.
        
        Args:
            agent_name: Optional name of the agent to reset metrics for.
                       If None, resets metrics for all agents.
        """
        with self._lock:
            if agent_name:
                if agent_name in self._metrics:
                    del self._metrics[agent_name]
            else:
                self._metrics.clear()


# Singleton instance of AgentMetrics
_metrics_instance = AgentMetrics()

def get_metrics_instance() -> AgentMetrics:
    """Get the singleton instance of AgentMetrics."""
    return _metrics_instance

def monitor_operation(operation_name: str):
    """
    Decorator for monitoring agent operations.
    
    Args:
        operation_name: Name of the operation being monitored
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            start_time = time.time()
            success = True
            details = {'args': str(args), 'kwargs': str(kwargs)}
            
            try:
                result = await func(self, *args, **kwargs)
                details['result_summary'] = str(result)[:100] + '...' if result and len(str(result)) > 100 else str(result)
                return result
            except Exception as e:
                success = False
                details['error'] = str(e)
                raise
            finally:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                # Get agent name from instance
                agent_name = getattr(self, 'name', self.__class__.__name__)
                
                # Record metrics
                _metrics_instance.record_operation(
                    agent_name=agent_name,
                    operation_name=operation_name,
                    duration_ms=duration_ms,
                    success=success,
                    details=details
                )
                
                # Log operation
                if success:
                    logger.info(f"Agent '{agent_name}' completed operation '{operation_name}' in {duration_ms:.2f}ms")
                else:
                    logger.error(f"Agent '{agent_name}' failed operation '{operation_name}' after {duration_ms:.2f}ms")
        
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            start_time = time.time()
            success = True
            details = {'args': str(args), 'kwargs': str(kwargs)}
            
            try:
                result = func(self, *args, **kwargs)
                details['result_summary'] = str(result)[:100] + '...' if result and len(str(result)) > 100 else str(result)
                return result
            except Exception as e:
                success = False
                details['error'] = str(e)
                raise
            finally:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                # Get agent name from instance
                agent_name = getattr(self, 'name', self.__class__.__name__)
                
                # Record metrics
                _metrics_instance.record_operation(
                    agent_name=agent_name,
                    operation_name=operation_name,
                    duration_ms=duration_ms,
                    success=success,
                    details=details
                )
                
                # Log operation
                if success:
                    logger.info(f"Agent '{agent_name}' completed operation '{operation_name}' in {duration_ms:.2f}ms")
                else:
                    logger.error(f"Agent '{agent_name}' failed operation '{operation_name}' after {duration_ms:.2f}ms")
        
        # Return appropriate wrapper based on whether the function is async or not
        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def asyncio_iscoroutinefunction(func):
    """Check if a function is a coroutine function."""
    import inspect
    return inspect.iscoroutinefunction(func) 