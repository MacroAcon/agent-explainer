import React, { useState } from 'react';
import { Box, Button, Card, CardContent, Grid, Typography, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Tabs, Tab } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import LocalMailerWorkflow from './LocalMailerWorkflow';

interface Campaign {
  id: string;
  name: string;
  type: 'social' | 'promotion' | 'comprehensive' | 'event';
  details: any;
  status: 'active' | 'completed' | 'scheduled';
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`marketing-tabpanel-${index}`}
      aria-labelledby={`marketing-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `marketing-tab-${index}`,
    'aria-controls': `marketing-tabpanel-${index}`,
  };
}

const MarketingDemo: React.FC = () => {
  const [value, setValue] = useState(0);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedType, setSelectedType] = useState<'social' | 'promotion' | 'comprehensive' | 'event'>('social');
  const [formData, setFormData] = useState({
    name: '',
    startDate: new Date(),
    endDate: new Date(),
    budget: '',
    description: '',
    platforms: [] as string[],
  });

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  const handleCreateCampaign = () => {
    const newCampaign: Campaign = {
      id: `${selectedType.toUpperCase()}${Date.now()}`,
      name: formData.name,
      type: selectedType,
      details: {
        ...formData,
        startDate: formData.startDate.toISOString(),
        endDate: formData.endDate.toISOString(),
      },
      status: 'scheduled',
    };

    setCampaigns([...campaigns, newCampaign]);
    setOpenDialog(false);
    setFormData({
      name: '',
      startDate: new Date(),
      endDate: new Date(),
      budget: '',
      description: '',
      platforms: [],
    });
  };

  const renderCampaignCard = (campaign: Campaign) => (
    <Card key={campaign.id} sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {campaign.name}
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          ID: {campaign.id}
        </Typography>
        <Typography variant="body2">
          Type: {campaign.type.charAt(0).toUpperCase() + campaign.type.slice(1)}
        </Typography>
        <Typography variant="body2">
          Status: {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
        </Typography>
        <Typography variant="body2">
          Duration: {new Date(campaign.details.startDate).toLocaleDateString()} - 
                  {new Date(campaign.details.endDate).toLocaleDateString()}
        </Typography>
        {campaign.details.budget && (
          <Typography variant="body2">
            Budget: ${campaign.details.budget}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="marketing tabs">
          <Tab label="Campaign Dashboard" {...a11yProps(0)} />
          <Tab label="Local Mailer" {...a11yProps(1)} />
        </Tabs>
      </Box>

      <TabPanel value={value} index={0}>
        <Typography variant="h4" gutterBottom>
          Marketing Campaign Dashboard
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Create New Campaign
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => {
                    setSelectedType('social');
                    setOpenDialog(true);
                  }}
                  sx={{ mb: 1 }}
                  fullWidth
                >
                  Social Media Campaign
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => {
                    setSelectedType('promotion');
                    setOpenDialog(true);
                  }}
                  sx={{ mb: 1 }}
                  fullWidth
                >
                  Local Promotion
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => {
                    setSelectedType('comprehensive');
                    setOpenDialog(true);
                  }}
                  sx={{ mb: 1 }}
                  fullWidth
                >
                  Marketing Campaign
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => {
                    setSelectedType('event');
                    setOpenDialog(true);
                  }}
                  fullWidth
                >
                  Community Event
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Active Campaigns
            </Typography>
            {campaigns.map(renderCampaignCard)}
          </Grid>
        </Grid>

        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            Create New {selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Campaign
          </DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Campaign Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={formData.startDate}
                onChange={(newValue) => setFormData({ ...formData, startDate: newValue || new Date() })}
                sx={{ mt: 2, width: '100%' }}
              />
              <DatePicker
                label="End Date"
                value={formData.endDate}
                onChange={(newValue) => setFormData({ ...formData, endDate: newValue || new Date() })}
                sx={{ mt: 2, width: '100%' }}
              />
            </LocalizationProvider>
            <TextField
              margin="dense"
              label="Budget"
              type="number"
              fullWidth
              value={formData.budget}
              onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateCampaign} variant="contained" color="primary">
              Create Campaign
            </Button>
          </DialogActions>
        </Dialog>
      </TabPanel>

      <TabPanel value={value} index={1}>
        <LocalMailerWorkflow />
      </TabPanel>
    </Box>
  );
};

export default MarketingDemo; 