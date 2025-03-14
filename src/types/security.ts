export interface SecurityState {
  last_audit: string;
  failed_attempts: number;
  locked_until: string | null;
  active_sessions: string[];
}

export interface AuditMetrics {
  total_events: number;
  events_last_24h: number;
  events_by_type: Record<string, number>;
  events_by_severity: Record<string, number>;
  events_by_agent: Record<string, number>;
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_usage: number;
  process_count: number;
}

export interface PerformanceMetrics {
  system: SystemMetrics;
  performance: {
    avg_response_time: number;
    active_tasks: number;
    queue_size: number;
  };
  agents: Record<string, {
    tasks_processed: number;
    errors: number;
    avg_response_time: number;
  }>;
  alerts: Array<{
    category: string;
    type: string;
    value: number;
    threshold: number;
    timestamp: string;
  }>;
}

export interface SecurityMetrics {
  security_state: SecurityState;
  audit_metrics: AuditMetrics;
  performance_metrics: PerformanceMetrics;
} 