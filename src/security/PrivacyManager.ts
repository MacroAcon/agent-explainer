import { z } from 'zod';

export interface PIIData {
  email?: string;
  phone?: string;
  address?: string;
  zipCode?: string;
  name?: string;
}

export interface ComplianceConfig {
  gdprEnabled: boolean;
  ccpaEnabled: boolean;
  dataRetentionDays: number;
  privacyPolicyUrl: string;
}

const piiSchema = z.object({
  email: z.string().email().optional(),
  phone: z.string().regex(/^\+?[\d\s-()]+$/).optional(),
  address: z.string().min(5).optional(),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/).optional(),
  name: z.string().min(2).optional(),
});

export class PrivacyManager {
  private static instance: PrivacyManager;
  private complianceConfig: ComplianceConfig;

  private constructor() {
    this.complianceConfig = {
      gdprEnabled: true,
      ccpaEnabled: true,
      dataRetentionDays: 90,
      privacyPolicyUrl: '/privacy-policy',
    };
  }

  public static getInstance(): PrivacyManager {
    if (!PrivacyManager.instance) {
      PrivacyManager.instance = new PrivacyManager();
    }
    return PrivacyManager.instance;
  }

  public detectPII(text: string): PIIData {
    const piiData: PIIData = {};
    
    // Email detection
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const emails = text.match(emailRegex);
    if (emails) piiData.email = emails[0];

    // Phone detection
    const phoneRegex = /(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/g;
    const phones = text.match(phoneRegex);
    if (phones) piiData.phone = phones[0];

    // ZIP code detection
    const zipRegex = /\b\d{5}(-\d{4})?\b/g;
    const zips = text.match(zipRegex);
    if (zips) piiData.zipCode = zips[0];

    return piiData;
  }

  public maskPII(text: string): string {
    const piiData = this.detectPII(text);
    let maskedText = text;

    if (piiData.email) {
      maskedText = maskedText.replace(piiData.email, '[EMAIL REDACTED]');
    }
    if (piiData.phone) {
      maskedText = maskedText.replace(piiData.phone, '[PHONE REDACTED]');
    }
    if (piiData.zipCode) {
      maskedText = maskedText.replace(piiData.zipCode, '[ZIP REDACTED]');
    }

    return maskedText;
  }

  public validatePrivacyCompliance(data: any): boolean {
    try {
      piiSchema.parse(data);
      return true;
    } catch (error) {
      console.error('Privacy compliance validation failed:', error);
      return false;
    }
  }

  public getDataRetentionPolicy(): string {
    return `Data will be retained for ${this.complianceConfig.dataRetentionDays} days.`;
  }

  public getComplianceStatus(): ComplianceConfig {
    return { ...this.complianceConfig };
  }
}

export const privacyManager = PrivacyManager.getInstance(); 