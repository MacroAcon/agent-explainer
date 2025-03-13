from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class MemorySettings:
    """Settings for memory management and optimization."""
    long_term_capacity: int = 10000
    working_memory_ttl: int = 3600  # 1 hour
    compression_strategy: str = "semantic"
    pruning_threshold: float = 0.8
    memory_cleanup_interval: int = 86400  # 24 hours
    max_episodic_entries: int = 1000

@dataclass
class TaskSettings:
    """Settings for task queue and prioritization."""
    max_concurrent_tasks: int = 10
    priority_levels: list = ("high", "medium", "low")
    task_timeout: int = 300  # 5 minutes
    retry_attempts: int = 3
    retry_delay: int = 5
    max_queue_size: int = 1000
    batch_size: int = 5
    dependency_check_interval: int = 60  # 1 minute

@dataclass
class PerformanceSettings:
    """Settings for performance optimization."""
    parallel_execution: bool = True
    result_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    batch_processing: bool = True
    max_batch_size: int = 10
    min_batch_interval: float = 0.1  # 100ms

@dataclass
class EnhancedSettings:
    """Combined settings for all enhanced features."""
    memory: MemorySettings = MemorySettings()
    task: TaskSettings = TaskSettings()
    performance: PerformanceSettings = PerformanceSettings()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'EnhancedSettings':
        """Create settings from a dictionary."""
        return cls(
            memory=MemorySettings(**config_dict.get('memory', {})),
            task=TaskSettings(**config_dict.get('task', {})),
            performance=PerformanceSettings(**config_dict.get('performance', {}))
        )

# Global settings instance
enhanced_settings = EnhancedSettings() 