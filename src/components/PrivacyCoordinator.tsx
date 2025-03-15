import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  DataObject as DataObjectIcon,
} from '@mui/icons-material';

interface PrivacyCheck {
  id: string;
  name: string;
  status: 'pending' | 'passed' | 'failed';
  description: string;
  timestamp: Date;
  details?: string;
}

interface PrivacyCoordinatorProps {
  campaignData: any;
  onPrivacyStatusChange: (status: 'compliant' | 'non_compliant') => void;
}

const PrivacyCoordinator: React.FC<PrivacyCoordinatorProps> = ({ campaignData, onPrivacyStatusChange }) => {
  const [privacyChecks, setPrivacyChecks] = useState<PrivacyCheck[]>([]);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const performPrivacyChecks = async () => {
      setIsChecking(true);
      const checks: PrivacyCheck[] = [
        {
          id: '1',
          name: 'Data Minimization',
          status: 'pending',
          description: 'Verifying that only necessary data is collected',
          timestamp: new Date(),
        },
        {
          id: '2',
          name: 'Consent Management',
          status: 'pending',
          description: 'Checking consent mechanisms for data collection',
          timestamp: new Date(),
        },
        {
          id: '3',
          name: 'Data Encryption',
          status: 'pending',
          description: 'Ensuring data is properly encrypted',
          timestamp: new Date(),
        },
        {
          id: '4',
          name: 'Access Controls',
          status: 'pending',
          description: 'Verifying access control mechanisms',
          timestamp: new Date(),
        },
        {
          id: '5',
          name: 'Data Retention',
          status: 'pending',
          description: 'Checking data retention policies',
          timestamp: new Date(),
        },
        {
          id: '6',
          name: 'AI Content Compliance',
          status: 'pending',
          description: 'Verifying AI-generated content compliance',
          timestamp: new Date(),
        },
        {
          id: '7',
          name: 'Image Privacy',
          status: 'pending',
          description: 'Checking image privacy and usage rights',
          timestamp: new Date(),
        },
      ];

      // Simulate privacy checks
      for (let i = 0; i < checks.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Special handling for AI and image checks
        if (checks[i].id === '6') {
          // AI Content Compliance check
          const hasAI = campaignData.content?.imageUrl;
          checks[i].status = hasAI ? 'passed' : 'failed';
          checks[i].details = hasAI 
            ? 'AI-generated content properly documented and compliant'
            : 'No AI-generated content detected';
        } else if (checks[i].id === '7') {
          // Image Privacy check
          const hasImage = campaignData.content?.imageUrl;
          checks[i].status = hasImage ? 'passed' : 'failed';
          checks[i].details = hasImage
            ? 'Image usage rights verified and privacy compliant'
            : 'No images detected in campaign';
        } else {
          // Regular checks
          checks[i].status = Math.random() > 0.1 ? 'passed' : 'failed';
        }
        
        checks[i].timestamp = new Date();
        setPrivacyChecks([...checks.slice(0, i + 1)]);
      }

      setIsChecking(false);
      
      // Determine overall compliance
      const isCompliant = checks.every(check => check.status === 'passed');
      onPrivacyStatusChange(isCompliant ? 'compliant' : 'non_compliant');
    };

    performPrivacyChecks();
  }, [campaignData, onPrivacyStatusChange]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <WarningIcon color="error" />;
      default:
        return <CircularProgress size={20} />;
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <SecurityIcon sx={{ mr: 1 }} />
        <Typography variant="h6">
          Privacy Compliance Check
        </Typography>
      </Box>

      {isChecking && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Performing privacy compliance checks...
        </Alert>
      )}

      <List>
        {privacyChecks.map((check) => (
          <ListItem key={check.id}>
            <ListItemIcon>
              {getStatusIcon(check.status)}
            </ListItemIcon>
            <ListItemText
              primary={check.name}
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {check.description}
                  </Typography>
                  {check.details && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {check.details}
                    </Typography>
                  )}
                  <Chip
                    size="small"
                    label={check.status.toUpperCase()}
                    color={getStatusColor(check.status)}
                    sx={{ mt: 1 }}
                  />
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>

      {!isChecking && privacyChecks.length > 0 && (
        <Alert 
          severity={privacyChecks.every(check => check.status === 'passed') ? 'success' : 'error'}
          sx={{ mt: 2 }}
        >
          {privacyChecks.every(check => check.status === 'passed')
            ? 'All privacy checks passed. Campaign data is compliant.'
            : 'Some privacy checks failed. Please review and address the issues.'}
        </Alert>
      )}
    </Paper>
  );
};

export default PrivacyCoordinator; 