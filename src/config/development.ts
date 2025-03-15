export interface DevelopmentConfig {
  enableDebugLogging: boolean;
  enablePerformanceMonitoring: boolean;
  enableDetailedErrors: boolean;
  mockServices: boolean;
  devTools: {
    showGrid: boolean;
    showOutlines: boolean;
    showBreakpoints: boolean;
  };
}

class DevelopmentManager {
  private static instance: DevelopmentManager;
  private config: DevelopmentConfig;

  private constructor() {
    this.config = {
      enableDebugLogging: process.env.NODE_ENV === 'development',
      enablePerformanceMonitoring: true,
      enableDetailedErrors: process.env.NODE_ENV === 'development',
      mockServices: process.env.MOCK_SERVICES === 'true',
      devTools: {
        showGrid: false,
        showOutlines: false,
        showBreakpoints: false,
      },
    };
  }

  public static getInstance(): DevelopmentManager {
    if (!DevelopmentManager.instance) {
      DevelopmentManager.instance = new DevelopmentManager();
    }
    return DevelopmentManager.instance;
  }

  public getConfig(): DevelopmentConfig {
    return { ...this.config };
  }

  public setDevTools(options: Partial<DevelopmentConfig['devTools']>): void {
    this.config.devTools = {
      ...this.config.devTools,
      ...options,
    };
  }

  public debug(message: string, ...args: any[]): void {
    if (this.config.enableDebugLogging) {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  }

  public error(error: Error, context?: string): void {
    if (this.config.enableDetailedErrors) {
      console.error(`[ERROR] ${context || 'Uncaught error'}:`, {
        message: error.message,
        stack: error.stack,
        context,
      });
    } else {
      console.error(`[ERROR] ${error.message}`);
    }
  }

  public getMockData<T>(key: string): T | null {
    if (!this.config.mockServices) return null;
    
    try {
      const mockData = require(`../data/mocks/${key}.json`);
      return mockData as T;
    } catch (error) {
      this.debug(`Mock data not found for key: ${key}`);
      return null;
    }
  }

  public logPerformance(label: string, duration: number): void {
    if (this.config.enablePerformanceMonitoring) {
      console.log(`[PERFORMANCE] ${label}: ${duration}ms`);
    }
  }
}

export const developmentManager = DevelopmentManager.getInstance(); 