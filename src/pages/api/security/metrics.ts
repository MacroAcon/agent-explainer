import { NextApiRequest, NextApiResponse } from 'next';
import { HIPAACompliantAgent } from '../../../agents/hipaa_compliant_agent';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // In a production environment, you would get the agent instance from a proper service/manager
    const agent = new HIPAACompliantAgent(
      'security-monitor',
      'Security monitoring agent',
      {}
    );

    // Get security report
    const securityReport = await agent.get_security_report();

    // Get performance metrics
    const metricsSummary = agent.metrics_collector.get_metrics_summary();

    // Combine the data
    const response = {
      security_state: securityReport.security_state,
      audit_metrics: securityReport.audit_metrics,
      performance_metrics: metricsSummary
    };

    return res.status(200).json(response);
  } catch (error) {
    console.error('Error fetching security metrics:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
} 