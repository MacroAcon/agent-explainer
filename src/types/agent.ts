export interface NodeData {
  label: string;
  description: string;
  type: 'default' | 'coordinator' | 'swarm_coordinator' | 'operations' | 'location' | 'service' | 'swarm_agent' | 'marketing';
  channels: string[];
  tools: string[];
} 