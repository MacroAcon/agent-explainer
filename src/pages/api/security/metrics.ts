import { NextApiRequest, NextApiResponse } from 'next';
import { SecurityMetrics } from '@/types/security';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Mock security metrics data
    const mockMetrics: SecurityMetrics = {
      security_state: {
        last_audit: new Date().toISOString(),
        failed_attempts: 0,
        locked_until: null,
        active_sessions: ['session1', 'session2']
      },
      audit_metrics: {
        total_events: 1250,
        events_last_24h: 150,
        events_by_type: {
          'access': 500,
          'update': 300,
          'delete': 50,
          'create': 400
        },
        events_by_severity: {
          'info': 800,
          'warning': 350,
          'error': 100
        },
        events_by_agent: {
          'user1': 400,
          'user2': 350,
          'system': 500
        }
      },
      performance_metrics: {
        system: {
          cpu_percent: 45.5,
          memory_percent: 60.2,
          disk_usage: 72.8,
          process_count: 128
        },
        performance: {
          avg_response_time: 250,
          active_tasks: 15,
          queue_size: 5
        },
        agents: {
          'agent1': {
            tasks_processed: 500,
            errors: 5,
            avg_response_time: 200
          },
          'agent2': {
            tasks_processed: 450,
            errors: 3,
            avg_response_time: 180
          }
        },
        alerts: [
          {
            category: 'System',
            type: 'Memory Usage',
            value: 85.5,
            threshold: 80,
            timestamp: new Date().toISOString()
          },
          {
            category: 'Performance',
            type: 'Response Time',
            value: 450,
            threshold: 400,
            timestamp: new Date().toISOString()
          }
        ]
      }
    };

    res.status(200).json({
      success: true,
      data: mockMetrics,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error generating security metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to generate security metrics',
      timestamp: new Date().toISOString()
    });
  }
} 