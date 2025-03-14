import React from 'react';
import { Handle, Position } from 'reactflow';
import { Paper, Box, Typography, Divider, Chip } from '@mui/material';
import { NodeData } from '../types/agent';

/**
 * Styling configuration for different node types
 * Each node type has a specific visual style to represent its role in the agent system
 */
const nodeStyles = {
  default: {
    backgroundColor: '#1e1e1e',
    borderColor: '#90caf9',
    boxShadow: '0 0 6px rgba(144, 202, 249, 0.3)'
  },
  coordinator: {
    backgroundColor: 'rgba(66, 165, 245, 0.1)',
    borderColor: '#42a5f5',
    boxShadow: '0 0 6px rgba(66, 165, 245, 0.3)'
  },
  swarm_coordinator: {
    backgroundColor: 'rgba(66, 165, 245, 0.1)',
    borderColor: '#42a5f5',
    boxShadow: '0 0 6px rgba(66, 165, 245, 0.3)'
  },
  operations: {
    backgroundColor: 'rgba(129, 199, 132, 0.1)',
    borderColor: '#81c784',
    boxShadow: '0 0 6px rgba(129, 199, 132, 0.3)'
  },
  location: {
    backgroundColor: 'rgba(128, 203, 196, 0.1)',
    borderColor: '#80cbc4',
    boxShadow: '0 0 6px rgba(128, 203, 196, 0.3)'
  },
  service: {
    backgroundColor: 'rgba(206, 147, 216, 0.1)',
    borderColor: '#ce93d8',
    boxShadow: '0 0 6px rgba(206, 147, 216, 0.3)'
  },
  swarm_agent: {
    backgroundColor: 'rgba(206, 147, 216, 0.05)',
    borderColor: '#ce93d8',
    boxShadow: '0 0 18px rgba(206, 147, 216, 0.6), 0 0 30px rgba(206, 147, 216, 0.3)'
  },
  marketing: {
    backgroundColor: 'rgba(255, 183, 77, 0.1)',
    borderColor: '#ffb74d',
    boxShadow: '0 0 6px rgba(255, 183, 77, 0.3)'
  },
};

/**
 * CustomNode Component
 * 
 * A specialized ReactFlow node component that visualizes different types of agents
 * in the agent graph. Each node type has a unique visual representation and displays
 * information about the agent's capabilities, channels, and tools.
 * 
 * The component handles:
 * - Different visual styling based on agent type
 * - Connection handles for linking nodes together
 * - Displaying agent metadata (channels, tools)
 * 
 * @param {Object} props - Component props
 * @param {NodeData} props.data - The data object containing agent information
 * @returns {React.ReactElement} A styled ReactFlow node
 */
const CustomNode: React.FC<{ data: NodeData }> = ({ data }) => {
  const style = nodeStyles[data.type] || nodeStyles.default;
  
  // Force dark background by adding !important
  const paperStyle = {
    backgroundColor: style.backgroundColor,
    background: style.backgroundColor,
    borderColor: style.borderColor,
    borderWidth: 2,
    borderStyle: 'solid',
    boxShadow: style.boxShadow || `0 0 10px ${style.borderColor}40`,
    color: '#ffffff',
  };

  return (
    <Paper
      className="node-content dark-node"
      style={paperStyle}
      sx={{
        backgroundColor: '#1e1e1e !important',
        background: '#1e1e1e !important'
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: style.borderColor }} />
      <Box sx={{ backgroundColor: 'transparent !important' }}>
        <Typography className="node-label" sx={{ color: '#ffffff !important' }}>
          {data.label}
        </Typography>
        <Typography className="node-description" sx={{ color: 'rgba(255,255,255,0.7) !important' }}>
          {data.description}
        </Typography>
        
        {/* Divider between name/description and tools/channels */}
        {(data.tools?.length > 0 || data.channels?.length > 0) && (
          <Divider 
            sx={{ 
              my: 1, 
              borderColor: `${style.borderColor}60`,
              opacity: 0.6 
            }} 
          />
        )}
        
        {data.tools?.length > 0 && (
          <Box sx={{ mb: 1 }}>
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'rgba(255,255,255,0.6) !important',
                fontWeight: 'bold',
                display: 'block',
                mb: 0.5,
                fontSize: '0.7rem'
              }}
            >
              Tools:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {data.tools.map((tool, index) => (
                <Chip
                  key={index}
                  label={tool}
                  size="small"
                  data-type="tool"
                  sx={{
                    height: '20px',
                    backgroundColor: 'rgba(255,255,255,0.15)',
                    color: '#fff',
                    fontSize: '0.65rem',
                    '& .MuiChip-label': {
                      padding: '0 6px',
                    },
                    border: '1px solid rgba(255,255,255,0.2)',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.2)',
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
        
        {data.channels?.length > 0 && (
          <Box>
            <Typography 
              variant="caption" 
              sx={{ 
                color: 'rgba(255,255,255,0.6) !important',
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
                <Chip
                  key={index}
                  label={channel}
                  size="small"
                  data-type="channel"
                  sx={{
                    height: '20px',
                    backgroundColor: 'rgba(255,255,255,0.12)',
                    color: '#fff',
                    fontSize: '0.65rem',
                    '& .MuiChip-label': {
                      padding: '0 6px',
                    },
                    border: '1px solid rgba(255,255,255,0.15)',
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.18)',
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
      </Box>
      <Handle type="source" position={Position.Bottom} style={{ background: style.borderColor }} />
    </Paper>
  );
};

export default CustomNode; 