export interface AgentConfig {
  id: string;
  name: string;
  type: string;
  capabilities: string[];
}

export class BaseAgent {
  protected config: AgentConfig;
  protected status: 'idle' | 'active' | 'error';
  protected lastActivity: string;

  constructor(config?: Partial<AgentConfig>) {
    this.config = {
      id: config?.id || crypto.randomUUID(),
      name: config?.name || 'Base Agent',
      type: config?.type || 'base',
      capabilities: config?.capabilities || []
    };
    this.status = 'idle';
    this.lastActivity = new Date().toISOString();
  }

  public getConfig(): AgentConfig {
    return this.config;
  }

  public getStatus(): string {
    return this.status;
  }

  public getLastActivity(): string {
    return this.lastActivity;
  }

  protected updateLastActivity(): void {
    this.lastActivity = new Date().toISOString();
  }

  public async initialize(): Promise<void> {
    this.status = 'active';
    this.updateLastActivity();
  }

  public async shutdown(): Promise<void> {
    this.status = 'idle';
    this.updateLastActivity();
  }

  public async handleError(error: Error): Promise<void> {
    this.status = 'error';
    this.updateLastActivity();
    console.error(`Agent ${this.config.name} encountered an error:`, error);
  }
} 