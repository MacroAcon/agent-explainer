import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { Campaign, CampaignStatus } from '../types/campaign';
import { CampaignService } from '../services/campaignService';
import { CampaignForm } from './CampaignForm';
import { formatDate } from '../utils/campaignUtils';

const campaignService = CampaignService.getInstance();

const statusColors: Record<CampaignStatus, 'default' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning'> = {
  draft: 'default',
  in_review: 'info',
  approved: 'success',
  printing: 'primary',
  shipping: 'secondary',
  completed: 'success',
  cancelled: 'error',
};

export const CampaignDashboard: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = () => {
    const allCampaigns = campaignService.getAllCampaigns();
    setCampaigns(allCampaigns);
  };

  const handleCreateCampaign = async (campaignData: Partial<Campaign>) => {
    try {
      const newCampaign = await campaignService.createCampaign(campaignData);
      setCampaigns([...campaigns, newCampaign]);
      setIsCreateDialogOpen(false);
    } catch (error) {
      console.error('Failed to create campaign:', error);
      // TODO: Show error notification
    }
  };

  const handleEditCampaign = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
  };

  const handleDeleteCampaign = async (campaignId: string) => {
    // TODO: Implement delete functionality
    console.log('Delete campaign:', campaignId);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Campaigns</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          Create Campaign
        </Button>
      </Box>

      <Grid container spacing={3}>
        {campaigns.map((campaign) => (
          <Grid item xs={12} sm={6} md={4} key={campaign.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {campaign.name}
                  </Typography>
                  <Chip
                    label={campaign.status}
                    color={statusColors[campaign.status]}
                    size="small"
                  />
                </Box>
                <Typography color="text.secondary" gutterBottom>
                  {campaign.designType.charAt(0).toUpperCase() + campaign.designType.slice(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Target Area: {campaign.mailingList.targetZIPCodes.join(', ')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Created: {formatDate(campaign.createdAt)}
                </Typography>
                {campaign.metrics && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      Response Rate: {campaign.metrics.responseRate}%
                    </Typography>
                    <Typography variant="body2">
                      ROI: {campaign.metrics.roi}%
                    </Typography>
                  </Box>
                )}
              </CardContent>
              <CardActions>
                <Tooltip title="Edit Campaign">
                  <IconButton onClick={() => handleEditCampaign(campaign)}>
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete Campaign">
                  <IconButton onClick={() => handleDeleteCampaign(campaign.id)}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Campaign</DialogTitle>
        <DialogContent>
          <CampaignForm onSubmit={handleCreateCampaign} onCancel={() => setIsCreateDialogOpen(false)} />
        </DialogContent>
      </Dialog>

      {selectedCampaign && (
        <Dialog
          open={!!selectedCampaign}
          onClose={() => setSelectedCampaign(null)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Edit Campaign</DialogTitle>
          <DialogContent>
            <CampaignForm
              initialData={selectedCampaign}
              onSubmit={async (data) => {
                // TODO: Implement update functionality
                setSelectedCampaign(null);
              }}
              onCancel={() => setSelectedCampaign(null)}
            />
          </DialogContent>
        </Dialog>
      )}
    </Box>
  );
}; 