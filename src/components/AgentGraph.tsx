'use client';

import { useCallback } from 'react';
import ReactFlow, { 
  Node, 
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection
} from 'reactflow';
import AgentNode from './AgentNode';

const nodeTypes = {
  agent: AgentNode,
};

// Define our agent network
const initialNodes: Node[] = [
  // Base Agent
  {
    id: 'base',
    type: 'agent',
    position: { x: 400, y: 50 },
    data: { 
      label: 'Base Business Agent',
      description: 'Base agent class for business automation tasks',
      tools: ['process_task', 'register_tools', 'generate_response']
    }
  },
  // HIPAA Compliant Agent
  {
    id: 'hipaa',
    type: 'agent',
    position: { x: 400, y: 200 },
    data: { 
      label: 'HIPAA Compliant Agent',
      description: 'Base class for HIPAA-compliant business agents',
      tools: ['log_access', 'verify_authorization', 'process_hipaa_compliant']
    }
  },
  // Business Agents
  {
    id: 'restaurant',
    type: 'agent',
    position: { x: 100, y: 400 },
    data: { 
      label: 'Restaurant Operations',
      description: 'Manages restaurant operations in Calhoun, GA',
      tools: ['manage_menu', 'manage_kitchen', 'monitor_quality', 'manage_seating', 'manage_bar']
    }
  },
  {
    id: 'retail',
    type: 'agent',
    position: { x: 400, y: 400 },
    data: { 
      label: 'Retail Operations',
      description: 'Manages retail operations in Calhoun, GA',
      tools: ['manage_inventory', 'process_order', 'track_loyalty', 'generate_analytics']
    }
  },
  {
    id: 'marketing',
    type: 'agent',
    position: { x: 700, y: 400 },
    data: { 
      label: 'Local Marketing',
      description: 'Manages local marketing and community engagement',
      tools: ['manage_social_media', 'create_promotion', 'track_events', 'manage_reviews']
    }
  },
  {
    id: 'supplier',
    type: 'agent',
    position: { x: 250, y: 600 },
    data: { 
      label: 'Local Supplier Integration',
      description: 'Manages supplier relationships and community events',
      tools: ['manage_suppliers', 'track_ingredients', 'monitor_events', 'manage_programs']
    }
  },
  {
    id: 'customer',
    type: 'agent',
    position: { x: 550, y: 600 },
    data: { 
      label: 'Customer Service',
      description: 'Handles customer service tasks',
      tools: ['format_response', 'categorize_inquiry']
    }
  }
];

// Define connections between agents
const initialEdges: Edge[] = [
  // Inheritance edges
  { id: 'base-hipaa', source: 'base', target: 'hipaa', animated: true },
  { id: 'hipaa-restaurant', source: 'hipaa', target: 'restaurant', animated: true },
  { id: 'hipaa-retail', source: 'hipaa', target: 'retail', animated: true },
  { id: 'hipaa-marketing', source: 'hipaa', target: 'marketing', animated: true },
  
  // Communication edges
  { id: 'restaurant-supplier', source: 'restaurant', target: 'supplier' },
  { id: 'retail-supplier', source: 'retail', target: 'supplier' },
  { id: 'marketing-customer', source: 'marketing', target: 'customer' },
  { id: 'restaurant-customer', source: 'restaurant', target: 'customer' },
  { id: 'retail-customer', source: 'retail', target: 'customer' },
];

export default function AgentGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      nodeTypes={nodeTypes}
      fitView
    >
      <Background />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
} 