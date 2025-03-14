import { createMocks } from 'node-mocks-http';
import metricsHandler from '../../../src/pages/api/security/metrics';

describe('Security Metrics API', () => {
  it('returns a 405 for non-GET requests', async () => {
    const { req, res } = createMocks({
      method: 'POST',
    });

    await metricsHandler(req, res);

    expect(res._getStatusCode()).toBe(405);
    expect(JSON.parse(res._getData())).toEqual({
      message: 'Method not allowed',
    });
  });

  it('returns security metrics data for GET requests', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    await metricsHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    
    const data = JSON.parse(res._getData());
    expect(data.success).toBe(true);
    expect(data.data).toBeDefined();
    
    // Check structure of returned data
    const { security_state, audit_metrics, performance_metrics } = data.data;
    
    expect(security_state).toBeDefined();
    expect(security_state.active_sessions).toEqual(['session1', 'session2']);
    
    expect(audit_metrics).toBeDefined();
    expect(audit_metrics.total_events).toBe(1250);
    
    expect(performance_metrics).toBeDefined();
    expect(performance_metrics.system).toBeDefined();
    expect(performance_metrics.performance).toBeDefined();
    expect(performance_metrics.agents).toBeDefined();
    expect(performance_metrics.alerts).toHaveLength(2);
  });
}); 