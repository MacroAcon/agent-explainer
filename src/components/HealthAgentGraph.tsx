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
    case 'service':
      return { 
        ...baseStyle,
        borderRadius: '16px', 
        border: '3px solid #ce93d8', 
        boxShadow: '0 0 15px rgba(206, 147, 216, 0.4)'
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
        <Typography variant="h6" sx={{ m: 0 }}>Legend</Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.8rem' }}>
          {isExpanded ? '(click to collapse)' : '(click to expand)'}
        </Typography>
      </Box>
      
      {isExpanded && (
        <>
          <Typography variant="subtitle2" gutterBottom>Agent Types:</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#607d8b', borderRadius: '4px' }} />
              <Typography variant="body2">Base Agent</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 20, height: 20, backgroundColor: '#2196f3', borderRadius: '4px' }} />
              <Typography variant="body2">Coordinator</Typography>
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
              <Box sx={{ width: 20, height: 20, backgroundColor: '#4caf50', borderRadius: '8px' }} />
              <Typography variant="body2">Operations</Typography>
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
              <Box sx={{ width: 20, height: 20, backgroundColor: '#9c27b0', borderRadius: '16px' }} />
              <Typography variant="body2">Service</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 20, 
                height: 20, 
                backgroundColor: 'rgba(30, 30, 30, 0.7)',
                boxShadow: '0 0 10px rgba(128, 203, 196, 0.6), inset 0 0 8px rgba(128, 203, 196, 0.3)'
              }} />
              <Typography variant="body2" sx={{ color: '#fff' }}>Location</Typography>
            </Box>
          </Box>

          <Typography variant="subtitle2" gutterBottom>Connection Types:</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 30, height: 2, backgroundColor: '#2196f3' }} />
              <Typography variant="body2">Base Control Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 30, height: 2, backgroundColor: '#4caf50' }} />
              <Typography variant="body2">Operations Flow</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 30, height: 2, backgroundColor: '#9c27b0' }} />
              <Typography variant="body2">Compliance Control</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 30, height: 2, backgroundColor: '#ff9800', opacity: 0.8 }} />
              <Typography variant="body2">Privacy Monitoring</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 30, height: 2, backgroundColor: '#80cbc4' }} />
              <Typography variant="body2">Location Connection</Typography>
            </Box>
          </Box>

          <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>Features:</Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 20, 
                height: 20, 
                backgroundColor: '#1e1e1e',
                border: '2px solid #fff',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px'
              }}>
                <span style={{ color: '#fff' }}>💬</span>
              </Box>
              <Typography variant="body2">Group Chat Enabled</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ 
                width: 20, 
                height: 20, 
                backgroundColor: '#1e1e1e',
                border: '2px dashed #fff',
                borderRadius: '4px',
                animation: 'borderDash 8s linear infinite'
              }} />
              <Typography variant="body2">Temporary Agent</Typography>
            </Box>
          </Box>
        </>
      )}
    </Paper>
  );
};

// Define initial nodes with health service focus
const initialNodes: Node[] = [
  {
    id: 'base',
    type: 'agent',
    position: { x: 100, y: 400 },
    data: {
      label: 'Base Health Agent',
      description: 'Base agent class for healthcare automation tasks',
      type: 'default',
      channels: ['patient_care', 'medical_records', 'pharmacy', 'compliance'],
      tools: ['process_request', 'verify_auth', 'generate_response']
    }
  },
  {
    id: 'coordinator',
    type: 'agent',
    position: { x: 500, y: 400 },
    data: {
      label: 'Healthcare Coordinator',
      description: 'Coordinates healthcare automation agents',
      type: 'coordinator',
      channels: ['patient_care', 'medical_records', 'pharmacy', 'compliance', 'group_chat'],
      tools: ['delegate_task', 'monitor_compliance', 'manage_workflow', 'track_metrics', 'manage_group_discussions']
    }
  },
  {
    id: 'compliance_coordinator',
    type: 'agent',
    position: { x: 500, y: 700 },
    data: {
      label: 'Compliance Swarm Coordinator',
      description: 'Coordinates temporary compliance-focused agents',
      type: 'swarm_coordinator',
      channels: ['compliance', 'medical_records', 'audit'],
      tools: ['spawn_compliance_agent', 'monitor_violations', 'coordinate_audits']
    }
  },
  {
    id: 'patient',
    type: 'agent',
    position: { x: 900, y: 200 },
    data: {
      label: 'Patient Care Operations',
      description: 'Manages patient care and appointment scheduling',
      type: 'operations',
      channels: ['patient_care', 'medical_records', 'compliance', 'group_chat'],
      tools: ['schedule_appointment', 'manage_records', 'track_vitals', 'coordinate_care', 'manage_care_discussions']
    }
  },
  {
    id: 'pharmacy',
    type: 'agent',
    position: { x: 900, y: 400 },
    data: {
      label: 'Pharmacy Operations',
      description: 'Manages medication and prescription services',
      type: 'operations',
      channels: ['pharmacy', 'patient_care', 'compliance', 'group_chat'],
      tools: ['process_prescription', 'check_interactions', 'manage_inventory', 'verify_insurance', 'coordinate_med_discussions']
    }
  },
  {
    id: 'lab',
    type: 'agent',
    position: { x: 900, y: 600 },
    data: {
      label: 'Laboratory Services',
      description: 'Manages lab tests and results',
      type: 'operations',
      channels: ['medical_records', 'patient_care', 'compliance', 'group_chat'],
      tools: ['process_samples', 'analyze_results', 'manage_tests', 'report_findings', 'discuss_results']
    }
  },
  {
    id: 'clinic',
    type: 'agent',
    position: { x: 1300, y: 400 },
    data: {
      label: 'Calhoun Clinic',
      description: 'Manages operations for Calhoun, GA clinic location',
      type: 'location',
      channels: ['patient_care', 'medical_records', 'pharmacy', 'compliance', 'group_chat'],
      tools: ['manage_facility', 'coordinate_staff', 'monitor_resources', 'manage_group_channels']
    }
  },
  {
    id: 'data_privacy',
    type: 'agent',
    position: { x: 1300, y: 800 },
    data: {
      label: 'Data Privacy Agent',
      description: 'Temporary agent for data privacy and access control',
      type: 'swarm_agent',
      channels: ['compliance', 'medical_records'],
      tools: ['encrypt_data', 'manage_access', 'track_consent']
    }
  },
  {
    id: 'audit',
    type: 'agent',
    position: { x: 1300, y: 900 },
    data: {
      label: 'Audit Agent',
      description: 'Temporary agent for compliance audits',
      type: 'swarm_agent',
      channels: ['compliance', 'audit'],
      tools: ['perform_audit', 'generate_reports', 'track_violations']
    }
  },
  {
    id: 'breach',
    type: 'agent',
    position: { x: 1300, y: 1000 },
    data: {
      label: 'Breach Detection Agent',
      description: 'Temporary agent for breach monitoring and response',
      type: 'swarm_agent',
      channels: ['compliance', 'audit'],
      tools: ['monitor_access', 'detect_anomalies', 'respond_incidents']
    }
  },
  {
    id: 'insurance',
    type: 'agent',
    position: { x: 1700, y: 400 },
    data: {
      label: 'Insurance Processing',
      description: 'Handles insurance claims and verification',
      type: 'service',
      channels: ['compliance', 'patient_care', 'group_chat'],
      tools: ['verify_coverage', 'process_claims', 'manage_authorizations', 'coordinate_claim_discussions']
    }
  },
  {
    id: 'telemedicine',
    type: 'agent',
    position: { x: 900, y: 0 },
    data: {
      label: 'Telemedicine Operations',
      description: 'Manages virtual healthcare services',
      type: 'operations',
      channels: ['patient_care', 'medical_records', 'compliance', 'group_chat'],
      tools: ['manage_virtual_visits', 'coordinate_remote_care', 'monitor_vitals', 'facilitate_consultations']
    }
  },
  {
    id: 'emergency',
    type: 'agent',
    position: { x: 500, y: 100 },
    data: {
      label: 'Emergency Response Coordinator',
      description: 'Coordinates emergency medical responses',
      type: 'coordinator',
      channels: ['patient_care', 'medical_records', 'emergency', 'group_chat'],
      tools: ['coordinate_emergency', 'track_resources', 'manage_priorities', 'alert_staff']
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
    id: 'base-compliance-coordinator',
    source: 'base',
    target: 'compliance_coordinator',
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-patient', 
    source: 'coordinator', 
    target: 'patient', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-pharmacy', 
    source: 'coordinator', 
    target: 'pharmacy', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-lab', 
    source: 'coordinator', 
    target: 'lab', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-clinic', 
    source: 'coordinator', 
    target: 'clinic', 
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  {
    id: 'compliance-coordinator-data-privacy',
    source: 'compliance_coordinator',
    target: 'data_privacy',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'compliance-coordinator-audit',
    source: 'compliance_coordinator',
    target: 'audit',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'compliance-coordinator-breach',
    source: 'compliance_coordinator',
    target: 'breach',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  {
    id: 'data-privacy-patient',
    source: 'data_privacy',
    target: 'patient',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'data-privacy-pharmacy',
    source: 'data_privacy',
    target: 'pharmacy',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  {
    id: 'data-privacy-lab',
    source: 'data_privacy',
    target: 'lab',
    animated: true,
    style: { stroke: '#ffb74d', strokeWidth: 2, strokeDasharray: '5,5' }
  },
  { 
    id: 'patient-clinic', 
    source: 'patient', 
    target: 'clinic',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'pharmacy-clinic', 
    source: 'pharmacy', 
    target: 'clinic',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'lab-clinic', 
    source: 'lab', 
    target: 'clinic',
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'clinic-insurance', 
    source: 'clinic', 
    target: 'insurance',
    style: { stroke: '#ce93d8', strokeWidth: 3 }
  },
  { 
    id: 'coordinator-telemedicine', 
    source: 'coordinator', 
    target: 'telemedicine', 
    style: { stroke: '#81c784', strokeWidth: 3 }
  },
  { 
    id: 'base-emergency', 
    source: 'base', 
    target: 'emergency', 
    animated: true,
    style: { stroke: '#42a5f5', strokeWidth: 3 }
  },
  { 
    id: 'emergency-clinic', 
    source: 'emergency', 
    target: 'clinic', 
    style: { stroke: '#80cbc4', strokeWidth: 3 }
  },
  { 
    id: 'telemedicine-clinic', 
    source: 'telemedicine', 
    target: 'clinic',
    style: { stroke: '#81c784', strokeWidth: 3 }
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

const HealthAgentGraph = () => {
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
              case 'service':
              case 'swarm_agent':
                return '#ce93d8';
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

export default HealthAgentGraph; 