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
      tools: ['process_task', 'register_tools', 'generate_response'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations']
    }
  },
  // Business Swarm Coordinator
  {
    id: 'coordinator',
    type: 'agent',
    position: { x: 400, y: 200 },
    data: { 
      label: 'Business Swarm Coordinator',
      description: 'Coordinates business automation agents with AG2 CaptainAgent',
      tools: ['delegate_task', 'monitor_performance', 'manage_channels', 'track_metrics'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations']
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
      tools: ['manage_menu', 'manage_kitchen', 'monitor_quality', 'manage_seating', 'manage_bar'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['operations', 'supply_chain']
    }
  },
  {
    id: 'retail',
    type: 'agent',
    position: { x: 400, y: 400 },
    data: { 
      label: 'Retail Operations',
      description: 'Manages retail operations in Calhoun, GA',
      tools: ['manage_inventory', 'process_order', 'track_loyalty', 'generate_analytics'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['operations', 'supply_chain']
    }
  },
  {
    id: 'marketing',
    type: 'agent',
    position: { x: 700, y: 400 },
    data: { 
      label: 'Local Marketing',
      description: 'Manages local marketing and community engagement',
      tools: ['manage_social_media', 'create_promotion', 'track_events', 'manage_reviews'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['marketing', 'customer_relations']
    }
  },
  {
    id: 'supplier',
    type: 'agent',
    position: { x: 250, y: 600 },
    data: { 
      label: 'Local Supplier Integration',
      description: 'Manages supplier relationships and community events',
      tools: ['manage_suppliers', 'track_ingredients', 'monitor_events', 'manage_programs'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['supply_chain', 'operations']
    }
  },
  {
    id: 'customer',
    type: 'agent',
    position: { x: 550, y: 600 },
    data: { 
      label: 'Customer Service',
      description: 'Handles customer service tasks',
      tools: ['format_response', 'categorize_inquiry', 'manage_feedback'],
      memorySystems: ['long_term', 'working', 'episodic'],
      channels: ['customer_relations', 'marketing']
    }
  }
];

// Define connections between agents
const initialEdges: Edge[] = [
  // Inheritance edges
  { id: 'base-coordinator', source: 'base', target: 'coordinator', animated: true, style: { stroke: '#60a5fa' } },
  { id: 'coordinator-restaurant', source: 'coordinator', target: 'restaurant', animated: true, style: { stroke: '#60a5fa' } },
  { id: 'coordinator-retail', source: 'coordinator', target: 'retail', animated: true, style: { stroke: '#60a5fa' } },
  { id: 'coordinator-marketing', source: 'coordinator', target: 'marketing', animated: true, style: { stroke: '#60a5fa' } },
  
  // Communication channel edges
  { id: 'restaurant-supplier', source: 'restaurant', target: 'supplier', label: 'supply_chain', style: { stroke: '#34d399' } },
  { id: 'retail-supplier', source: 'retail', target: 'supplier', label: 'supply_chain', style: { stroke: '#34d399' } },
  { id: 'marketing-customer', source: 'marketing', target: 'customer', label: 'customer_relations', style: { stroke: '#f472b6' } },
  { id: 'restaurant-customer', source: 'restaurant', target: 'customer', label: 'customer_relations', style: { stroke: '#f472b6' } },
  { id: 'retail-customer', source: 'retail', target: 'customer', label: 'customer_relations', style: { stroke: '#f472b6' } },
  { id: 'marketing-retail', source: 'marketing', target: 'retail', label: 'marketing', style: { stroke: '#fbbf24' } },
  { id: 'marketing-restaurant', source: 'marketing', target: 'restaurant', label: 'marketing', style: { stroke: '#fbbf24' } },
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
      className="bg-gray-900"
    >
      <Background color="#374151" gap={16} />
      <Controls className="!bg-gray-800 !text-gray-200" />
      <MiniMap className="!bg-gray-800" nodeColor="#1f2937" />
    </ReactFlow>
  );
} 