import { createMocks } from 'node-mocks-http';
import privacySettingsHandler from '../../../src/pages/api/security/privacy-settings';

describe('Privacy Settings API', () => {
  it('returns a 405 for unsupported methods', async () => {
    const { req, res } = createMocks({
      method: 'DELETE',
    });

    await privacySettingsHandler(req, res);

    expect(res._getStatusCode()).toBe(405);
    expect(JSON.parse(res._getData())).toEqual({
      success: false,
      error: 'Method not allowed',
      timestamp: expect.any(String),
    });
  });

  it('returns privacy settings for GET requests', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    await privacySettingsHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    
    const data = JSON.parse(res._getData());
    expect(data.success).toBe(true);
    expect(data.data).toBeDefined();
    
    // Check structure of returned data
    const { dataCollection, communication, agents, compliance } = data.data;
    
    expect(dataCollection).toBeDefined();
    expect(dataCollection.anonymizeUserData).toBe(true);
    
    expect(communication).toBeDefined();
    expect(communication.encryptedChannelsOnly).toBe(true);
    
    expect(agents).toBeDefined();
    expect(agents.dataAccessRestrictions).toBe('strict');
    
    expect(compliance).toBeDefined();
    expect(compliance.hipaaCompliant).toBe(true);
  });

  it('updates privacy settings for PATCH requests', async () => {
    const updateData = {
      dataCollection: {
        anonymizeUserData: false,
      },
      agents: {
        auditFrequencyDays: 14,
      }
    };

    const { req, res } = createMocks({
      method: 'PATCH',
      body: updateData,
    });

    await privacySettingsHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    
    const data = JSON.parse(res._getData());
    expect(data.success).toBe(true);
    expect(data.message).toBe('Privacy settings updated successfully');
    expect(data.updates).toEqual(updateData);
  });

  it('replaces privacy settings for PUT requests', async () => {
    const newSettings = {
      dataCollection: {
        anonymizeUserData: false,
        collectUsageStatistics: true,
        retentionPeriodDays: 60,
      },
      compliance: {
        hipaaCompliant: true,
        gdprCompliant: false,
      }
    };

    const { req, res } = createMocks({
      method: 'PUT',
      body: newSettings,
    });

    await privacySettingsHandler(req, res);

    expect(res._getStatusCode()).toBe(200);
    
    const data = JSON.parse(res._getData());
    expect(data.success).toBe(true);
    expect(data.message).toBe('Privacy settings replaced successfully');
    expect(data.settings).toEqual(newSettings);
  });
}); 