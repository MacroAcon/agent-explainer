import React, { useState, useCallback, useEffect, useMemo, memo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  NodeTypes,
  EdgeTypes,
  ConnectionMode,
  Panel,
  useReactFlow,
  Position,
  BackgroundVariant,
  MiniMap,
  Handle,
  EdgeProps,
  getBezierPath,
} from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import { Box, Typography, Paper, useTheme, useMediaQuery, Chip, Divider, Tooltip as MuiTooltip } from '@mui/material';
import { NodeData } from '../types/agent';
import CustomNode from './CustomNode';

// Add some tool icons
import BuildIcon from '@mui/icons-material/Build';
import StorageIcon from '@mui/icons-material/Storage';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SearchIcon from '@mui/icons-material/Search';
import SettingsIcon from '@mui/icons-material/Settings';
import CodeIcon from '@mui/icons-material/Code';
import ApiIcon from '@mui/icons-material/Api';
import CloudIcon from '@mui/icons-material/Cloud';
import MemoryIcon from '@mui/icons-material/Memory';
import WebIcon from '@mui/icons-material/Web';
import SecurityIcon from '@mui/icons-material/Security';

// Add keyframe animation for the pulsing border
const styles = `
  @keyframes gradient {
    0% {
      background-position: 0 0;
    }
    100% {
      background-position: 200% 0;
    }
  }
  
  @keyframes dash {
    to {
      stroke-dashoffset: 10;
    }
  }

  /* Force dark backgrounds on nodes */
  .dark-node-override {
    background-color: #1e1e1e !important;
    color: white !important;
  }

  .dark-node-override.react-flow__node {
    background-color: #1e1e1e !important;
    color: white !important;
  }

  .react-flow__node {
    background-color: #1e1e1e !important;
    color: white !important;
  }

  .react-flow__node-default {
    background-color: #1e1e1e !important;
    color: white !important;
  }
  
  .react-flow__edge-path {
    stroke-width: 2;
    transition: stroke 0.3s, stroke-dasharray 0.3s, stroke-width 0.3s;
  }
  
  .edge-coordinator {
    stroke: #42a5f5;
    stroke-width: 2;
  }
  
  .edge-swarm {
    stroke: #ce93d8;
    stroke-width: 2;
    stroke-dasharray: 5,5;
  }
  
  .edge-service {
    stroke: #80cbc4;
    stroke-width: 1.5;
  }
  
  .edge-default {
    stroke: #b1b1b7;
    stroke-width: 1.5;
  }
`;

// Map tool names to icons
const getToolIcon = (toolName: string) => {
  const toolMap: { [key: string]: React.ReactNode } = {
    'database': <StorageIcon fontSize="small" />,
    'search': <SearchIcon fontSize="small" />,
    'api': <ApiIcon fontSize="small" />,
    'code': <CodeIcon fontSize="small" />,
    'cloud': <CloudIcon fontSize="small" />,
    'settings': <SettingsIcon fontSize="small" />,
    'ai': <MemoryIcon fontSize="small" />,
    'web': <WebIcon fontSize="small" />,
    'security': <SecurityIcon fontSize="small" />,
    'orchestration': <AccountTreeIcon fontSize="small" />,
  };
  
  // Check if the tool name contains any of the keys
  for (const [key, icon] of Object.entries(toolMap)) {
    if (toolName.toLowerCase().includes(key.toLowerCase())) {
      return icon;
    }
  }
  
  // Default icon
  return <BuildIcon fontSize="small" />;
};

// Custom edge component for different edge types
const CustomEdge = memo(({ id, source, target, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style, markerEnd, data }: EdgeProps) => {
  const edgeTypes: { [key: string]: string } = {
    'coordinator': 'edge-coordinator',
    'swarm': 'edge-swarm',
    'service': 'edge-service',
    'default': 'edge-default'
  };
  
  // Determine edge type based on source or target node ID
  const sourceNodeType = source?.toString().toLowerCase().includes('coordinator') ? 'coordinator' : 
                         source?.toString().toLowerCase().includes('swarm') ? 'swarm' :
                         source?.toString().toLowerCase().includes('service') ? 'service' : 'default';
  
  // Apply the appropriate edge class
  const edgeClass = edgeTypes[sourceNodeType];
  
  // Generate the path
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });
  
  return (
    <path
      id={id}
      className={`react-flow__edge-path ${edgeClass}`}
      d={edgePath}
      markerEnd={markerEnd}
      style={style}
    />
  );
});

CustomEdge.displayName = 'CustomEdge';

// Unified node styling that combines both examples
const getNodeStyle = (type: string): React.CSSProperties => {
  const baseStyle: React.CSSProperties = {
    padding: '10px',
    color: '#fff',
    minWidth: '180px',
    backgroundColor: '#1e1e1e',
    cursor: 'grab',
    userSelect: 'none',
    transition: 'transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out',
    touchAction: 'none',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative'
  };

  switch (type) {
    case 'coordinator':
    case 'swarm_coordinator':
      return {
        ...baseStyle,
        border: '2px solid #42a5f5',
        borderRadius: '4px',
        backgroundColor: 'rgba(66, 165, 245, 0.1)',
        boxShadow: '0 0 6px rgba(66, 165, 245, 0.3)'
      };
    case 'operations':
      return {
        ...baseStyle,
        borderRadius: '6px',
        border: '2px solid #81c784',
        backgroundColor: 'rgba(129, 199, 132, 0.1)',
        boxShadow: '0 0 6px rgba(129, 199, 132, 0.3)'
      };
    case 'service':
      return {
        ...baseStyle,
        borderRadius: '8px',
        border: '2px solid #ce93d8',
        backgroundColor: 'rgba(206, 147, 216, 0.1)',
        boxShadow: '0 0 6px rgba(206, 147, 216, 0.3)'
      };
    case 'location':
      return {
        ...baseStyle,
        borderRadius: '6px',
        border: '2px solid #80cbc4',
        backgroundColor: 'rgba(128, 203, 196, 0.1)',
        boxShadow: '0 0 6px rgba(128, 203, 196, 0.3)',
        minWidth: '160px',
        minHeight: '100px'
      };
    case 'swarm_agent':
      return {
        ...baseStyle,
        borderRadius: '4px',
        border: '2px solid #ce93d8',
        backgroundColor: 'rgba(206, 147, 216, 0.05)',
        boxShadow: '0 0 18px rgba(206, 147, 216, 0.6), 0 0 30px rgba(206, 147, 216, 0.3)',
        outline: '1px dashed rgba(206, 147, 216, 0.4)',
        outlineOffset: '2px'
      };
    case 'marketing':
      return {
        ...baseStyle,
        borderRadius: '4px',
        border: '2px solid #ffb74d',
        backgroundColor: 'rgba(255, 183, 77, 0.1)',
        boxShadow: '0 0 6px rgba(255, 183, 77, 0.3)'
      };
    default:
      return {
        ...baseStyle,
        borderRadius: '4px',
        border: '2px solid #90caf9',
        backgroundColor: 'rgba(144, 202, 249, 0.1)',
        boxShadow: '0 0 6px rgba(144, 202, 249, 0.3)'
      };
  }
};

// Add this helper function at the top level
const getCommonTools = (nodes: Node<NodeData>[]): Set<string> => {
  const toolCounts = new Map<string, number>();
  const commonTools = new Set<string>();

  // Count tool occurrences
  nodes.forEach(node => {
    node.data.tools?.forEach(tool => {
      toolCounts.set(tool, (toolCounts.get(tool) || 0) + 1);
    });
  });

  // Find tools used by more than 3 nodes
  toolCounts.forEach((count, tool) => {
    if (count > 3) {
      commonTools.add(tool);
    }
  });

  return commonTools;
};

// Template node component - memoized for performance
const TemplateNode: React.FC<{ data: NodeData; commonTools: Set<string> }> = memo(({ data, commonTools }) => {
  // Initialize expanded state based on node type
  const [isGrabbing, setIsGrabbing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(
    data.type === 'coordinator' || 
    data.type === 'swarm_coordinator' || 
    data.type === 'operations'
  );
  const [hoveredTool, setHoveredTool] = useState<string | null>(null);
  const [hoveredChannel, setHoveredChannel] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const nodeStyle = getNodeStyle(data.type);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Create a style object with the most critical properties
  const style = {
    ...nodeStyle,
    cursor: isGrabbing ? 'grabbing' : 'grab',
    transform: isGrabbing ? 'scale(1.02)' : 'none',
    background: nodeStyle.backgroundColor,
    color: '#fff',
    border: nodeStyle.border,
    boxShadow: nodeStyle.boxShadow,
    transition: 'all 0.3s ease',
    zIndex: isExpanded ? 1000 : 1,
    maxHeight: isExpanded ? 'none' : '120px',
    overflow: 'hidden',
  };

  // Tooltip component
  const Tooltip = ({ content }: { content: string }) => (
    <Paper
      sx={{
        position: 'fixed',
        left: tooltipPosition.x,
        top: tooltipPosition.y,
        backgroundColor: 'rgba(0, 0, 0, 0.95)',
        color: '#fff',
        padding: '8px 12px',
        borderRadius: '4px',
        fontSize: '0.75rem',
        zIndex: 9999,
        boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
        backdropFilter: 'blur(4px)',
        border: '1px solid rgba(255,255,255,0.1)',
        transform: 'translate(-50%, -100%)',
        marginTop: '-8px',
        whiteSpace: 'nowrap',
        pointerEvents: 'none',
        opacity: 1,
        transition: 'opacity 0.2s ease'
      }}
    >
      {content}
    </Paper>
  );
  
  const handleInteraction = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isGrabbing) {
      setIsExpanded(!isExpanded);
    }
  };

  // Categorize tools as common or specific
  const commonToolsList = data.tools ? data.tools.filter(tool => commonTools.has(tool)) : [];
  const specificToolsList = data.tools ? data.tools.filter(tool => !commonTools.has(tool)) : [];
  
  return (
    <div 
      style={style}
      className="dark-node-override"
      data-type={data.type}
      onMouseDown={() => setIsGrabbing(true)}
      onMouseUp={() => setIsGrabbing(false)}
      onMouseLeave={() => setIsGrabbing(false)}
      onClick={handleInteraction}
      onTouchEnd={handleInteraction}
    >
      <Handle 
        type="target" 
        position={Position.Left} 
        style={{ 
          background: 'rgba(255, 255, 255, 0.3)',
          width: '8px',
          height: '8px',
          border: 'none',
          left: '-4px'
        }} 
      />
      <Box sx={{ 
        p: 1, 
        display: 'flex', 
        flexDirection: 'column',
        gap: 1,
        width: '100%',
        backgroundColor: 'transparent'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography 
            variant="h6" 
            sx={{ 
              color: '#fff', 
              fontSize: '0.9rem', 
              fontWeight: 600,
              lineHeight: 1.2
            }}
          >
            {data.label}
          </Typography>
          <Typography sx={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.8rem' }}>
            {isExpanded ? '▼' : '▶'}
          </Typography>
        </Box>
        <Typography 
          variant="body2" 
          sx={{ 
            color: 'rgba(255,255,255,0.7)', 
            fontSize: '0.75rem',
            lineHeight: 1.3
          }}
        >
          {data.description}
        </Typography>
        
        {/* Common tools shown as icons, always visible */}
        {commonToolsList.length > 0 && (
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: 0.5, 
            mt: 0.5, 
            justifyContent: 'flex-start'
          }}>
            {commonToolsList.map((tool, index) => (
              <MuiTooltip 
                key={index} 
                title={`Common Tool: ${tool}`}
                placement="top"
                arrow
              >
                <Box
                  sx={{
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    borderRadius: '50%',
                    width: 24,
                    height: 24,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.2)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  {getToolIcon(tool)}
                </Box>
              </MuiTooltip>
            ))}
          </Box>
        )}
        
        {/* Divider between name/description and tools/channels */}
        {(specificToolsList.length > 0 || data.channels?.length > 0) && isExpanded && (
          <Box 
            sx={{ 
              height: '1px', 
              backgroundColor: `${nodeStyle.borderColor}60`,
              opacity: 0.6,
              my: 0.5
            }} 
          />
        )}

        {isExpanded && (
          <>
            {specificToolsList.length > 0 && (
              <Box sx={{ mb: 1 }}>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'rgba(255,255,255,0.6)',
                    fontWeight: 'bold',
                    display: 'block',
                    mb: 0.5,
                    fontSize: '0.7rem'
                  }}
                >
                  Specific Tools:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {specificToolsList.map((tool, index) => (
                    <Box key={index} sx={{ position: 'relative' }}>
                      <Chip
                        label={tool}
                        size="small"
                        icon={<Box sx={{ fontSize: '0.8rem', opacity: 0.7 }}>{getToolIcon(tool)}</Box>}
                        data-type="tool"
                        onMouseEnter={(e) => {
                          const rect = e.currentTarget.getBoundingClientRect();
                          setTooltipPosition({
                            x: rect.left + rect.width / 2,
                            y: rect.top
                          });
                          setHoveredTool(tool);
                        }}
                        onMouseLeave={() => setHoveredTool(null)}
                        sx={{
                          height: '20px',
                          backgroundColor: hoveredTool === tool ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.08)',
                          color: '#fff',
                          fontSize: '0.65rem',
                          '& .MuiChip-label': {
                            padding: '0 6px',
                          },
                          border: '1px solid rgba(255,255,255,0.1)',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            transform: 'translateY(-1px)',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
            
            {data.channels?.length > 0 && (
              <Box>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'rgba(255,255,255,0.6)',
                    fontWeight: 'bold',
                    display: 'block',
                    mb: 0.5,
                    fontSize: '0.7rem'
                  }}
                >
                  Channels:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {data.channels.map((channel, index) => (
                    <Box key={index} sx={{ position: 'relative' }}>
                      <Chip
                        label={channel}
                        size="small"
                        data-type="channel"
                        onMouseEnter={(e) => {
                          const rect = e.currentTarget.getBoundingClientRect();
                          setTooltipPosition({
                            x: rect.left + rect.width / 2,
                            y: rect.top
                          });
                          setHoveredChannel(channel);
                        }}
                        onMouseLeave={() => setHoveredChannel(null)}
                        sx={{
                          height: '20px',
                          backgroundColor: hoveredChannel === channel ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.05)',
                          color: '#fff',
                          fontSize: '0.65rem',
                          '& .MuiChip-label': {
                            padding: '0 6px',
                          },
                          border: '1px solid rgba(255,255,255,0.08)',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            transform: 'translateY(-1px)',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </>
        )}
      </Box>
      <Handle 
        type="source" 
        position={Position.Right} 
        style={{ 
          background: 'rgba(255, 255, 255, 0.3)',
          width: '8px',
          height: '8px',
          border: 'none',
          right: '-4px'
        }} 
      />
      {(hoveredTool || hoveredChannel) && (
        <Tooltip content={hoveredTool ? `Tool: ${hoveredTool}` : `Channel: ${hoveredChannel}`} />
      )}
    </div>
  );
});

TemplateNode.displayName = 'TemplateNode';

// Legend component
const Legend: React.FC<{ isExpanded: boolean; onToggle: () => void }> = ({ isExpanded, onToggle }) => {
  const agentTypes = [
    { type: 'default', color: '#90caf9', label: 'Base Agent' },
    { type: 'coordinator', color: '#42a5f5', label: 'Coordinator' },
    { type: 'swarm_coordinator', color: '#42a5f5', label: 'Swarm Coordinator' },
    { type: 'operations', color: '#81c784', label: 'Operations' },
    { type: 'location', color: '#80cbc4', label: 'Location' },
    { type: 'service', color: '#ce93d8', label: 'Service' },
    { type: 'swarm_agent', color: '#ce93d8', label: 'Swarm Agent' },
  ];

  return (
    <Paper
      sx={{
        backgroundColor: 'rgba(30, 30, 30, 0.9)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '4px',
        padding: '8px',
        color: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
        maxWidth: '200px',
        backdropFilter: 'blur(4px)'
      }}
    >
      <Box
        onClick={onToggle}
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          padding: '2px 4px'
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Agent Types</Typography>
        <Typography variant="caption" sx={{ color: '#888', fontSize: '0.7rem' }}>
          {isExpanded ? '▼' : '▶'}
        </Typography>
      </Box>
      {isExpanded && (
        <Box sx={{ mt: 0.5 }}>
          {agentTypes.map(({ type, color, label }) => (
            <Box
              key={type}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                my: 0.25,
                px: 0.5
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  backgroundColor: color,
                  borderRadius: '2px'
                }}
              />
              <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>{label}</Typography>
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  );
};

interface AgentGraphTemplateProps {
  nodes: Node<NodeData>[];
  edges: Edge[];
}

const AgentGraphTemplate: React.FC<AgentGraphTemplateProps> = ({ nodes, edges }) => {
  const [nodesState, setNodes, onNodesChange] = useNodesState(nodes);
  const [edgesState, setEdges, onEdgesChange] = useEdgesState(edges);
  const [isLegendExpanded, setIsLegendExpanded] = useState(true);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Get common tools - memoized for performance
  const commonTools = useMemo(() => getCommonTools(nodes), [nodes]);

  // Define the custom node and edge types
  const nodeTypes = useMemo(() => ({
    custom: (props: any) => <TemplateNode {...props} commonTools={commonTools} />,
  }), [commonTools]);

  const edgeTypes = useMemo(() => ({
    custom: CustomEdge,
  }), []);

  // Function to get node dimensions
  const getNodeDimensions = useCallback((node: Node) => {
    return {
      width: 339,
      height: 150,
    };
  }, []);

  // Function to apply dagre layout - optimized with callbacks
  const applyDagreLayout = useCallback(() => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    
    // Configure for horizontal layout
    dagreGraph.setGraph({
      rankdir: 'LR',  // Left to Right layout
      nodesep: 150,   // Increased horizontal spacing
      ranksep: 100,   // Reduced vertical spacing
      acyclicer: 'greedy',
      align: 'UL',
      marginx: 50,
      marginy: 50,
    });

    // Add nodes to dagre graph
    nodesState.forEach((node) => {
      const { width, height } = getNodeDimensions(node);
      dagreGraph.setNode(node.id, { width, height });
    });

    // Add edges to dagre graph
    edgesState.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    // Compute the layout
    dagre.layout(dagreGraph);

    // Apply the computed positions to the nodes
    const newNodes = nodesState.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - getNodeDimensions(node).width / 2,
          y: nodeWithPosition.y - getNodeDimensions(node).height / 2,
        },
        // Set type to custom for all nodes
        type: 'custom',
      };
    });

    // Update edge types
    const newEdges = edgesState.map(edge => ({
      ...edge,
      type: 'custom'
    }));

    setNodes(newNodes);
    setEdges(newEdges);
  }, [nodesState, edgesState, setNodes, setEdges, getNodeDimensions]);

  // Apply layout only once on mount
  useEffect(() => {
    applyDagreLayout();
  }, []); // Empty dependency array means this only runs once on mount

  return (
    <Box sx={{ width: '100%', height: '80vh', position: 'relative' }}>
      <style>{styles}</style>
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="bottom-left"
        minZoom={0.2}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        nodesDraggable={true}
        nodesConnectable={true}
        elementsSelectable={true}
        connectionMode={ConnectionMode.Loose}
        snapToGrid={true}
        snapGrid={[15, 15]}
        defaultEdgeOptions={{
          type: 'custom',
          animated: false,
        }}
        fitViewOptions={{
          padding: 0.3,
          minZoom: 0.5,
          maxZoom: 1.5,
        }}
        style={{ background: 'linear-gradient(to bottom right, #1a1a1a, #2a2a2a)' }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={12}
          size={1}
          color="#666"
          style={{ opacity: 0.2 }}
        />
        <Controls />
        <MiniMap
          style={{
            backgroundColor: 'rgba(30, 30, 30, 0.9)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
          }}
        />
        <Panel position="top-right">
          <Legend isExpanded={isLegendExpanded} onToggle={() => setIsLegendExpanded(!isLegendExpanded)} />
        </Panel>
      </ReactFlow>
    </Box>
  );
};

export default AgentGraphTemplate; 