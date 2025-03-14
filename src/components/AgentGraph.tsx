import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  EdgeChange,
  NodeChange,
  BackgroundVariant
} from 'reactflow';
import { Box, Paper, Typography } from '@mui/material';
import 'reactflow/dist/style.css';
import AgentNode from '@/components/AgentNode';

const nodeTypes = {
  agent: AgentNode
};

// Add shape variations to node types
const getNodeStyle = (type: string) => {
  const baseStyle = {
    borderRadius: '4px',
    border: '3px solid #90caf9',
    boxShadow: '0 0 10px rgba(144, 202, 249, 0.3)',
    backgroundColor: '#1e1e1e',
    color: '#fff',
    padding: '10px',
    minWidth: '180px'
  };

  switch (type) {
    case 'coordinator':
      return { 
        ...baseStyle,
        borderRadius: '4px', 
        border: '3px solid #42a5f5', 
        boxShadow: '0 0 15px rgba(66, 165, 245, 0.4)'
      };
    case 'swarm_coordinator':
      return { 
        ...baseStyle,
        border: 'none',
        background: `
          linear-gradient(#1e1e1e, #1e1e1e) padding-box,
          linear-gradient(90deg, #42a5f5 50%, transparent 50%) border-box
        `,
        backgroundSize: '200% 100%',
        animation: 'gradient 8s linear infinite',
        padding: '20px',
        minWidth: '200px',
        borderRadius: '4px',
        borderWidth: '3px',
        borderStyle: 'solid',
        borderColor: 'transparent',
        boxShadow: '0 0 20px rgba(66, 165, 245, 0.5)'
      };
    case 'swarm_agent':
      return { 
        ...baseStyle,
        border: 'none',
        background: `
          linear-gradient(#1e1e1e, #1e1e1e) padding-box,
          linear-gradient(90deg, #ce93d8 50%, transparent 50%) border-box
        `,
        backgroundSize: '200% 100%',
        animation: 'gradient 8s linear infinite',
        padding: '20px',
        minWidth: '200px',
        borderRadius: '4px',
        borderWidth: '3px',
        borderStyle: 'solid',
        borderColor: 'transparent',
        boxShadow: '0 0 20px rgba(206, 147, 216, 0.5)'
      };
    case 'operations':
      return { 
        ...baseStyle,
        borderRadius: '8px', 
        border: '3px solid #81c784', 
        boxShadow: '0 0 15px rgba(129, 199, 132, 0.4)'
      };
    case 'marketing':
      return { 
        ...baseStyle,
        borderRadius: '8px', 
        border: '3px solid #ffb74d', 
        boxShadow: '0 0 15px rgba(255, 183, 77, 0.4)'
      };
    case 'service':
      return { 
        ...baseStyle,
        borderRadius: '16px', 
        border: '3px solid #ce93d8', 
        boxShadow: '0 0 15px rgba(206, 147, 216, 0.4)'
      };
    case 'supplier':
      return { 
        ...baseStyle,
        borderRadius: '16px', 
        border: '3px solid #a1887f', 
        boxShadow: '0 0 15px rgba(161, 136, 127, 0.4)'
      };
    case 'location':
      return { 
        ...baseStyle,
        borderRadius: '8px',
        border: 'none',
        backgroundColor: 'rgba(30, 30, 30, 0.7)',
        boxShadow: '0 0 30px rgba(128, 203, 196, 0.6), inset 0 0 20px rgba(128, 203, 196, 0.3)',
        minWidth: '160px',
        minHeight: '160px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      };
    default:
      return baseStyle;
  }
};

// Legend Component
const Legend = () => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  return (
    <Paper
      sx={{
        position: 'absolute',
        top: 20,
        right: 20,
        p: 2,
        zIndex: 10,
        backgroundColor: 'rgba(30, 30, 30, 0.95)',
        color: '#fff',
        borderRadius: '8px',
        boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        maxHeight: isExpanded ? '500px' : '40px',
        overflow: 'hidden'
      }}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: isExpanded ? 2 : 0 }}>
        <Typography variant="h6" sx={{ m: 0, color: '#fff' }}>Legend</Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem' }}>
          {isExpanded ? '(click to collapse)' : '(click to expand)'}
        </Typography>
      </Box>
      
      {isExpanded && (
        <>
          <Typography variant="subtitle2" gutterBottom sx={{ color: '#fff' }}>Agent Types:</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #90caf9', borderRadius: '4px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Base Agent</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #42a5f5', borderRadius: '4px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Coordinator</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box 
                sx={{ 
                  width: 20, 
                  height: 20, 
                  backgroundColor: '#1e1e1e',
                  border: 'none',
                  background: `
                    linear-gradient(#1e1e1e, #1e1e1e) padding-box,
                    linear-gradient(90deg, #42a5f5 50%, transparent 50%) border-box
                  `,
                  backgroundSize: '200% 100%',
                  animation: 'gradient 8s linear infinite',
                  borderRadius: '4px',
                  borderWidth: '2px',
                  borderStyle: 'solid',
                  borderColor: 'transparent'
                }} 
              />
              <Typography variant="body2" sx={{ color: '#fff' }}>Swarm Coordinator (Temporary)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #81c784', borderRadius: '8px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Operations</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #ffb74d', borderRadius: '8px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Marketing</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box 
                sx={{ 
                  width: 20, 
                  height: 20, 
                  backgroundColor: '#1e1e1e',
                  border: 'none',
                  background: `
                    linear-gradient(#1e1e1e, #1e1e1e) padding-box,
                    linear-gradient(90deg, #ce93d8 50%, transparent 50%) border-box
                  `,
                  backgroundSize: '200% 100%',
                  animation: 'gradient 8s linear infinite',
                  borderRadius: '4px',
                  borderWidth: '2px',
                  borderStyle: 'solid',
                  borderColor: 'transparent'
                }} 
              />
              <Typography variant="body2" sx={{ color: '#fff' }}>Swarm Agent (Temporary)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #ce93d8', borderRadius: '16px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Service</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #a1887f', borderRadius: '16px' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Supplier</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#1e1e1e', border: '2px solid #80cbc4', borderRadius: '50%' }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Location</Typography>
            </Box>
          </Box>

          <Typography variant="subtitle2" gutterBottom sx={{ color: '#fff' }}>Connection Types:</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#42a5f5',
                boxShadow: '0 0 4px rgba(66, 165, 245, 0.5)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Base Control Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#81c784',
                boxShadow: '0 0 4px rgba(129, 199, 132, 0.5)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Operations Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#ffb74d',
                boxShadow: '0 0 4px rgba(255, 183, 77, 0.5)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Marketing Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#ce93d8',
                boxShadow: '0 0 4px rgba(206, 147, 216, 0.5)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Service Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#ce93d8',
                boxShadow: '0 0 4px rgba(206, 147, 216, 0.5)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Privacy Agent Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 30, 
                height: 2, 
                backgroundColor: '#ffb74d',
                opacity: 0.7,
                boxShadow: '0 0 4px rgba(255, 183, 77, 0.3)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Privacy Monitoring (Animated)</Typography>
            </Box>
          </Box>
        </>
      )}
    </Paper>
  );
};

// Define initial nodes with better spacing
const initialNodes: Node[] = [
  {
    id: 'base',
    type: 'agent',
    position: { x: 100, y: 400 },
    data: {
      label: 'Base Business Agent',
      description: 'Base agent class for business automation tasks',
      type: 'default',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy'],
      tools: ['process_task', 'register_tools', 'generate_response']
    }
  },
  {
    id: 'coordinator',
    type: 'agent',
    position: { x: 500, y: 400 },
    data: {
      label: 'Business Swarm Coordinator',
      description: 'Coordinates business automation agents',
      type: 'coordinator',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['delegate_task', 'monitor_performance', 'manage_channels', 'track_metrics', 'manage_group_discussions']
    }
  },
  {
    id: 'privacy_coordinator',
    type: 'agent',
    position: { x: 500, y: 700 },
    data: {
      label: 'Privacy Swarm Coordinator',
      description: 'Coordinates temporary privacy-focused agents',
      type: 'swarm_coordinator',
      channels: ['privacy', 'customer_relations', 'audit'],
      tools: ['spawn_privacy_agent', 'monitor_compliance', 'coordinate_audits']
    }
  },
  {
    id: 'restaurant',
    type: 'agent',
    position: { x: 900, y: 200 },
    data: {
      label: 'Restaurant Operations',
      description: 'Manages global restaurant operations and standards',
      type: 'operations',
      channels: ['operations', 'supply_chain', 'privacy', 'group_chat'],
      tools: ['manage_menu', 'manage_kitchen', 'monitor_quality', 'manage_inventory', 'coordinate_staff_discussions']
    }
  },
  {
    id: 'retail',
    type: 'agent',
    position: { x: 900, y: 400 },
    data: {
      label: 'Retail Operations',
      description: 'Manages global retail operations and standards',
      type: 'operations',
      channels: ['operations', 'supply_chain', 'privacy', 'group_chat'],
      tools: ['manage_inventory', 'process_orders', 'track_sales', 'manage_logistics', 'coordinate_team_discussions']
    }
  },
  {
    id: 'marketing',
    type: 'agent',
    position: { x: 900, y: 600 },
    data: {
      label: 'Marketing Operations',
      description: 'Manages global marketing strategy and standards',
      type: 'marketing',
      channels: ['marketing', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['create_promotions', 'track_events', 'manage_reviews', 'coordinate_campaign_discussions']
    }
  },
  {
    id: 'loyalty_privacy',
    type: 'agent',
    position: { x: 1300, y: 800 },
    data: {
      label: 'Loyalty Data Privacy Agent',
      description: 'Temporary agent for customer loyalty data protection',
      type: 'swarm_agent',
      channels: ['privacy', 'customer_relations'],
      tools: ['encrypt_data', 'manage_consent', 'anonymize_analytics']
    }
  },
  {
    id: 'payment_privacy',
    type: 'agent',
    position: { x: 1300, y: 900 },
    data: {
      label: 'Payment Privacy Agent',
      description: 'Temporary agent for payment data security',
      type: 'swarm_agent',
      channels: ['privacy', 'operations'],
      tools: ['secure_transactions', 'mask_card_data', 'audit_access']
    }
  },
  {
    id: 'marketing_privacy',
    type: 'agent',
    position: { x: 1300, y: 1000 },
    data: {
      label: 'Marketing Privacy Agent',
      description: 'Temporary agent for marketing data compliance',
      type: 'swarm_agent',
      channels: ['privacy', 'marketing'],
      tools: ['manage_preferences', 'verify_consent', 'clean_analytics']
    }
  },
  {
    id: 'calhoun',
    type: 'agent',
    position: { x: 1300, y: 400 },
    data: {
      label: 'Calhoun Location',
      description: 'Manages all operations for Calhoun, GA location',
      type: 'location',
      channels: ['operations', 'marketing', 'supply_chain', 'customer_relations', 'privacy', 'group_chat'],
      tools: ['manage_local_ops', 'track_performance', 'coordinate_services', 'manage_group_channels']
    }
  },
  {
    id: 'supplier',
    type: 'agent',
    position: { x: 1700, y: 300 },
    data: {
      label: 'Local Supplier Integration',
      description: 'Manages supplier relationships and contracts',
      type: 'supplier',
      channels: ['supply_chain', 'operations', 'group_chat'],
      tools: ['manage_suppliers', 'track_ingredients', 'monitor_costs', 'coordinate_supply_discussions']
    }
  },
  {
    id: 'customer',
    type: 'agent',
    position: { x: 1700, y: 500 },
    data: {
      label: 'Customer Service',
      description: 'Handles customer service tasks',
      type: 'service',
      channels: ['customer_relations', 'marketing', 'privacy', 'group_chat'],
      tools: ['handle_inquiries', 'manage_complaints', 'manage_feedback', 'coordinate_service_discussions']
    }
  }
];

const initialEdges: Edge[] = [
  { 
    id: 'base-coordinator', 
    source: 'base', 
    target: 'coordinator', 
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  {
    id: 'base-privacy-coordinator',
    source: 'base',
    target: 'privacy_coordinator',
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-restaurant', 
    source: 'coordinator', 
    target: 'restaurant', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-retail', 
    source: 'coordinator', 
    target: 'retail', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-marketing', 
    source: 'coordinator', 
    target: 'marketing', 
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-calhoun', 
    source: 'coordinator', 
    target: 'calhoun', 
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-loyalty',
    source: 'privacy_coordinator',
    target: 'loyalty_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-payment',
    source: 'privacy_coordinator',
    target: 'payment_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'privacy-coordinator-marketing',
    source: 'privacy_coordinator',
    target: 'marketing_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'loyalty-retail',
    source: 'loyalty_privacy',
    target: 'retail',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'loyalty-customer',
    source: 'loyalty_privacy',
    target: 'customer',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'payment-restaurant',
    source: 'payment_privacy',
    target: 'restaurant',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'payment-retail',
    source: 'payment_privacy',
    target: 'retail',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'marketing-privacy-marketing',
    source: 'marketing_privacy',
    target: 'marketing',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'restaurant-calhoun', 
    source: 'restaurant', 
    target: 'calhoun',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'retail-calhoun', 
    source: 'retail', 
    target: 'calhoun',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'marketing-calhoun', 
    source: 'marketing', 
    target: 'calhoun',
    style: { stroke: '#ffb74d', strokeWidth: 3 }
  },
  { 
    id: 'calhoun-supplier', 
    source: 'calhoun', 
    target: 'supplier',
    style: { stroke: '#a1887f', strokeWidth: 3 }
  },
  { 
    id: 'calhoun-customer', 
    source: 'calhoun', 
    target: 'customer',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  }
];

const CustomEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  style = {},
  data,
}: any) => {
  const edgePath = `M ${sourceX} ${sourceY} L ${targetX} ${targetY}`;
  const labelX = (sourceX + targetX) / 2;
  const labelY = (sourceY + targetY) / 2;

  return (
    <>
      <path
        id={id}
        style={style}
        className="react-flow__edge-path"
        d={edgePath}
      />
      {data?.label && (
        <foreignObject
          x={labelX - 75}
          y={labelY - 15}
          width={150}
          height={30}
          style={{ 
            background: 'rgba(255,255,255,0.9)',
            borderRadius: '4px',
            padding: '2px 4px',
            fontSize: '10px',
            textAlign: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            pointerEvents: 'none'
          }}
        >
          {data.label}
        </foreignObject>
      )}
    </>
  );
};

const edgeTypes = {
  custom: CustomEdge
};

const AgentGraph = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes.map(node => ({
    ...node,
    style: getNodeStyle(node.data.type)
  })));
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: Connection) => {
    setEdges((eds: Edge[]) => addEdge({
      ...params,
      style: { stroke: '#666', strokeWidth: 2 }
    }, eds));
  }, [setEdges]);

  return (
    <div style={{ width: '100%', height: '90vh', background: '#121212', position: 'relative' }}>
      <style>
        {`
          @keyframes gradient {
            0% {
              background-position: 0 0;
            }
            100% {
              background-position: 200% 0;
            }
          }
        `}
      </style>
      <Legend />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        minZoom={0.5}
        maxZoom={1.5}
        fitViewOptions={{ padding: 0.3 }}
        attributionPosition="bottom-right"
        snapToGrid={true}
        snapGrid={[25, 25]}
      >
        <Background 
          gap={25} 
          color="#2a2a2a" 
          variant={BackgroundVariant.Dots}
        />
        <Controls 
          showInteractive={false}
          style={{
            backgroundColor: '#1e1e1e',
            borderColor: '#333',
            color: '#fff'
          }}
        />
        <MiniMap 
          nodeColor={(node: Node) => {
            switch (node.data?.type) {
              case 'coordinator':
              case 'swarm_coordinator':
                return '#42a5f5';
              case 'operations':
                return '#81c784';
              case 'marketing':
                return '#ffb74d';
              case 'service':
              case 'swarm_agent':
                return '#ce93d8';
              case 'supplier':
                return '#a1887f';
              case 'location':
                return '#80cbc4';
              default:
                return '#90caf9';
            }
          }}
          style={{
            backgroundColor: '#1e1e1e',
            border: '1px solid #333',
            borderRadius: '4px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
          }}
          maskColor="#12121280"
        />
      </ReactFlow>
    </div>
  );
};

export default AgentGraph; 