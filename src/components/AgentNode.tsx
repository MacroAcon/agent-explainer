import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Card, Typography, Box, Chip, Tooltip } from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import RouterIcon from '@mui/icons-material/Router';
import BuildIcon from '@mui/icons-material/Build';

interface AgentNodeData {
  label: string;
  description: string;
  channels?: string[];
  tools?: string[];
  type?: string;
}

const AgentNode = ({ data }: { data: AgentNodeData }) => {
  // Determine node color based on type
  const getNodeColor = (type: string = 'default') => {
    const colors = {
      coordinator: '#2196f3',
      operations: '#4caf50',
      marketing: '#ff9800',
      service: '#9c27b0',
      supplier: '#795548',
      location: '#009688',
      default: '#607d8b'
    };
    return colors[type as keyof typeof colors] || colors.default;
  };

  const nodeColor = getNodeColor(data.type);

  const hasGroupChat = data.channels?.includes('group_chat');

  return (
    <Card 
      sx={{
        minWidth: 250,
        maxWidth: 300,
        border: 2,
        borderColor: nodeColor,
        borderRadius: 2,
        bgcolor: 'background.paper',
        boxShadow: 3,
        '&:hover': {
          boxShadow: 6,
          transform: 'scale(1.02)',
          transition: 'all 0.2s ease-in-out'
        }
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: nodeColor }} />
      
      {/* Header */}
      <Box sx={{ p: 2, bgcolor: nodeColor, color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessIcon />
          <Typography variant="h6" component="div">
            {data.label}
          </Typography>
          {hasGroupChat && (
            <Box sx={{ 
              width: 24,
              height: 24,
              backgroundColor: 'rgba(30, 30, 30, 0.7)',
              border: '2px solid #fff',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px'
            }}>
              <span role="img" aria-label="group chat">💬</span>
            </Box>
          )}
        </Box>
        <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
          {data.description}
        </Typography>
      </Box>

      {/* Content */}
      <Box sx={{ p: 2 }}>
        {/* Channels */}
        {data.channels && data.channels.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <RouterIcon fontSize="small" />
              <Typography variant="subtitle2" color="text.secondary">
                Channels
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {data.channels.map((channel, index) => (
                <Tooltip key={index} title={channel}>
                  <Chip
                    label={channel.split('_')[0]}
                    size="small"
                    variant="outlined"
                    sx={{ borderColor: nodeColor }}
                  />
                </Tooltip>
              ))}
            </Box>
          </Box>
        )}

        {/* Tools */}
        {data.tools && data.tools.length > 0 && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <BuildIcon fontSize="small" />
              <Typography variant="subtitle2" color="text.secondary">
                Tools
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {data.tools.map((tool, index) => (
                <Tooltip key={index} title={tool}>
                  <Chip
                    label={tool.split('_')[0]}
                    size="small"
                    variant="outlined"
                    sx={{ borderColor: nodeColor }}
                  />
                </Tooltip>
              ))}
            </Box>
          </Box>
        )}
      </Box>

      <Handle type="source" position={Position.Bottom} style={{ background: nodeColor }} />
    </Card>
  );
};

export default memo(AgentNode); 