export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  networkRequests: number;
}

export interface PerformanceConfig {
  enableMetrics: boolean;
  sampleRate: number;
  reportingEndpoint?: string;
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetrics;
  private config: PerformanceConfig;

  private constructor() {
    this.metrics = {
      loadTime: 0,
      renderTime: 0,
      memoryUsage: 0,
      networkRequests: 0,
    };
    this.config = {
      enableMetrics: true,
      sampleRate: 0.1, // 10% sampling rate
    };
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  public startMeasurement(key: string): void {
    if (!this.config.enableMetrics) return;
    performance.mark(`${key}-start`);
  }

  public endMeasurement(key: string): number {
    if (!this.config.enableMetrics) return 0;
    performance.mark(`${key}-end`);
    const measure = performance.measure(
      key,
      `${key}-start`,
      `${key}-end`
    );
    return measure.duration;
  }

  public trackNetworkRequest(): void {
    this.metrics.networkRequests++;
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public shouldSample(): boolean {
    return Math.random() < this.config.sampleRate;
  }

  public async reportMetrics(): Promise<void> {
    if (!this.config.reportingEndpoint) return;

    try {
      await fetch(this.config.reportingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.metrics),
      });
    } catch (error) {
      console.error('Failed to report metrics:', error);
    }
  }

  public clearMetrics(): void {
    this.metrics = {
      loadTime: 0,
      renderTime: 0,
      memoryUsage: 0,
      networkRequests: 0,
    };
    performance.clearMarks();
    performance.clearMeasures();
  }
}

export const performanceMonitor = PerformanceMonitor.getInstance(); 