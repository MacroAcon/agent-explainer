import { z } from 'zod';

const envSchema = z.object({
  // API Keys
  NEXT_PUBLIC_GROQ_API_KEY: z.string().min(1, 'GROQ API Key is required'),

  // Security Settings
  ENABLE_CSP: z.string().transform(val => val === 'true'),
  ENABLE_XSS_PROTECTION: z.string().transform(val => val === 'true'),
  ENABLE_HSTS: z.string().transform(val => val === 'true'),
  RATE_LIMIT_REQUESTS: z.string().transform(val => parseInt(val, 10)),
  RATE_LIMIT_WINDOW: z.string().transform(val => parseInt(val, 10)),

  // Privacy Settings
  GDPR_ENABLED: z.string().transform(val => val === 'true'),
  CCPA_ENABLED: z.string().transform(val => val === 'true'),
  DATA_RETENTION_DAYS: z.string().transform(val => parseInt(val, 10)),
  PRIVACY_POLICY_URL: z.string(),

  // Performance Monitoring
  ENABLE_PERFORMANCE_MONITORING: z.string().transform(val => val === 'true'),
  PERFORMANCE_SAMPLE_RATE: z.string().transform(val => parseFloat(val)),
  PERFORMANCE_REPORTING_ENDPOINT: z.string().url().optional(),

  // Development
  NODE_ENV: z.enum(['development', 'production', 'test']),
  MOCK_SERVICES: z.string().transform(val => val === 'true'),
  ENABLE_DEBUG_LOGGING: z.string().transform(val => val === 'true'),
  ENABLE_DETAILED_ERRORS: z.string().transform(val => val === 'true'),
});

export type EnvConfig = z.infer<typeof envSchema>;

class EnvironmentManager {
  private static instance: EnvironmentManager;
  private config: EnvConfig;

  private constructor() {
    try {
      this.config = this.validateEnv();
    } catch (error) {
      console.error('Environment validation failed:', error);
      throw error;
    }
  }

  public static getInstance(): EnvironmentManager {
    if (!EnvironmentManager.instance) {
      EnvironmentManager.instance = new EnvironmentManager();
    }
    return EnvironmentManager.instance;
  }

  private validateEnv(): EnvConfig {
    try {
      return envSchema.parse(process.env);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const missingVars = error.errors
          .filter(e => e.code === 'invalid_type' && e.received === 'undefined')
          .map(e => e.path.join('.'));

        if (missingVars.length > 0) {
          throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
        }
      }
      throw error;
    }
  }

  public getConfig(): EnvConfig {
    return { ...this.config };
  }

  public isDevelopment(): boolean {
    return this.config.NODE_ENV === 'development';
  }

  public isProduction(): boolean {
    return this.config.NODE_ENV === 'production';
  }

  public isTest(): boolean {
    return this.config.NODE_ENV === 'test';
  }
}

export const environmentManager = EnvironmentManager.getInstance(); 