/// <reference types="vite/client" />

interface ImportMetaEnv {
  // API Keys
  readonly VITE_GROQ_API_KEY: string;
  readonly VITE_OPENAI_API_KEY: string;
  
  // Environment
  readonly VITE_ENV: 'development' | 'production' | 'test';
  readonly VITE_DEBUG: string;
  
  // Business Settings
  readonly VITE_BUSINESS_NAME: string;
  readonly VITE_BUSINESS_TYPE: string;
  readonly VITE_BUSINESS_DESCRIPTION: string;
  readonly VITE_LOCATION: string;
  
  // Security
  readonly VITE_SECRET_KEY: string;
  readonly VITE_ACCESS_TOKEN_EXPIRE_MINUTES: string;
  
  // Logging
  readonly VITE_LOG_LEVEL: string;
  readonly VITE_LOG_FILE: string;
  
  // Feature Flags
  readonly VITE_ENABLE_HIPAA: string;
  readonly VITE_ENABLE_AUDIT_LOGGING: string;
  readonly VITE_ENABLE_CACHING: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
} 