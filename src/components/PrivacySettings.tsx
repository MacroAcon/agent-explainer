import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Slider, 
  FormControlLabel, 
  Switch, 
  Card, 
  CardContent, 
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Tooltip,
  IconButton,
  Alert,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SecurityIcon from '@mui/icons-material/Security';
import { usePrivacy, PrivacyLevel, ProtectedDataType } from '../security/privacy/PrivacyContext';

// Example text with PII to demonstrate masking
const EXAMPLE_TEXT = `
Name: Dr. Jane Smith
Email: jane.smith@example.com
Phone: (555) 123-4567
SSN: 123-45-6789
Credit Card: 4111 1111 1111 1111
Address: 123 Main St, Springfield, IL 62701
`;

const PrivacySettings: React.FC = () => {
  const { 
    privacyLevel, 
    setPrivacyLevel, 
    maskPII, 
    protectedDataTypes,
    toggleDataTypeProtection,
    hasConsent,
    setConsent,
  } = usePrivacy();
  
  const [open, setOpen] = useState(false);
  const [demoText, setDemoText] = useState(EXAMPLE_TEXT);
  const [showPrivacyDemo, setShowPrivacyDemo] = useState(false);
  
  // Convert privacy level to slider value and back
  const privacyLevels: PrivacyLevel[] = ['low', 'medium', 'high', 'maximum'];
  const privacyLevelIndex = privacyLevels.indexOf(privacyLevel);
  
  const handlePrivacyLevelChange = (event: Event, newValue: number | number[]) => {
    const index = newValue as number;
    setPrivacyLevel(privacyLevels[index]);
  };
  
  const handleToggleDataType = (dataType: ProtectedDataType) => {
    toggleDataTypeProtection(dataType);
  };
  
  const handleOpen = () => {
    setOpen(true);
  };
  
  const handleClose = () => {
    setOpen(false);
  };
  
  // Get masked example text based on current privacy settings
  const maskedText = maskPII(demoText);
  
  return (
    <>
      <Tooltip title="Privacy Settings">
        <IconButton 
          onClick={handleOpen} 
          color="primary" 
          aria-label="privacy settings"
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            backgroundColor: 'rgba(30, 30, 30, 0.7)',
            '&:hover': {
              backgroundColor: 'rgba(40, 40, 40, 0.9)',
            },
          }}
        >
          <SecurityIcon />
        </IconButton>
      </Tooltip>
      
      <Dialog 
        open={open} 
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <SecurityIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Privacy Settings</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {!hasConsent && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              You have not given consent for data collection. Some features may be limited.
            </Alert>
          )}
          
          <Typography variant="subtitle1" gutterBottom>
            Privacy Protection Level
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <Slider
              value={privacyLevelIndex}
              onChange={handlePrivacyLevelChange}
              step={1}
              marks
              min={0}
              max={3}
              valueLabelDisplay="off"
            />
            <Box display="flex" justifyContent="space-between">
              <Typography variant="caption">Low</Typography>
              <Typography variant="caption">Medium</Typography>
              <Typography variant="caption">High</Typography>
              <Typography variant="caption">Maximum</Typography>
            </Box>
          </Box>
          
          <Typography variant="subtitle1" gutterBottom>
            Data Types to Protect
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <Box display="flex" flexWrap="wrap">
              {(Object.keys(protectedDataTypes) as ProtectedDataType[]).map((type) => (
                <FormControlLabel
                  key={type}
                  control={
                    <Switch
                      checked={protectedDataTypes[type]}
                      onChange={() => handleToggleDataType(type)}
                      name={type}
                    />
                  }
                  label={type.charAt(0).toUpperCase() + type.slice(1)}
                  sx={{ width: '50%', mb: 1 }}
                />
              ))}
            </Box>
          </Box>
          
          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Data Collection Consent
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={hasConsent}
                  onChange={(e) => setConsent(e.target.checked)}
                />
              }
              label="I consent to the collection and processing of my data"
            />
          </Box>
          
          <Divider sx={{ my: 2 }} />
          
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="subtitle1">
                Privacy Protection Demo
              </Typography>
              <Button 
                size="small" 
                onClick={() => setShowPrivacyDemo(!showPrivacyDemo)}
              >
                {showPrivacyDemo ? 'Hide Demo' : 'Show Demo'}
              </Button>
            </Box>
            
            {showPrivacyDemo && (
              <Card variant="outlined" sx={{ mt: 2, backgroundColor: 'rgba(0,0,0,0.1)' }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    Original Text:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    component="pre"
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      mb: 2,
                      p: 1,
                      backgroundColor: 'rgba(0,0,0,0.1)',
                      borderRadius: 1
                    }}
                  >
                    {demoText}
                  </Typography>
                  
                  <Typography variant="subtitle2" gutterBottom>
                    Protected Text (Privacy Level: {privacyLevel}):
                  </Typography>
                  <Typography 
                    variant="body2" 
                    component="pre"
                    sx={{ 
                      whiteSpace: 'pre-wrap',
                      p: 1,
                      backgroundColor: 'rgba(0,0,0,0.1)',
                      borderRadius: 1
                    }}
                  >
                    {maskedText}
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default PrivacySettings; 