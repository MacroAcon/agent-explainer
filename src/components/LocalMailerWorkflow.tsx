import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Card,
  CardContent,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  FormControlLabel,
  Switch,
  Chip,
  Paper,
  Alert,
  CardMedia,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import PrivacyCoordinator from './PrivacyCoordinator';
import DalleImageGenerator from './DalleImageGenerator';
import { generateMarketingContent } from '../services/groqService';
import ImageIcon from '@mui/icons-material/Image';

interface MailerCampaign {
  id: string;
  name: string;
  targetArea: string;
  mailingSize: number;
  designType: 'postcard' | 'letter' | 'brochure';
  content: {
    headline?: string;
    description?: string;
    callToAction?: string;
    specialOffers: string[];
    imageUrl?: string;
  };
  timing: {
    designStart: Date;
    printingStart: Date;
    mailingDate: Date;
  };
  budget: number;
  trackingEnabled: boolean;
  status: 'draft' | 'design' | 'printing' | 'mailing' | 'completed';
}

const steps = [
  'Campaign Details',
  'Content Design',
  'Targeting & Budget',
  'Review & Launch'
];

const LocalMailerWorkflow: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [campaign, setCampaign] = useState<Partial<MailerCampaign>>({
    status: 'draft',
    content: {
      headline: '',
      description: '',
      callToAction: '',
      specialOffers: [],
      imageUrl: ''
    }
  });
  const [privacyStatus, setPrivacyStatus] = useState<'compliant' | 'non_compliant' | null>(null);

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      // Launch campaign
      if (privacyStatus === 'compliant') {
        // TODO: Implement actual campaign launch
        console.log('Launching campaign:', campaign);
      }
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleAddSpecialOffer = () => {
    const newOffer = prompt('Enter special offer:');
    if (newOffer) {
      setCampaign(prev => ({
        ...prev,
        content: {
          ...prev.content!,
          specialOffers: [...(prev.content?.specialOffers || []), newOffer]
        }
      }));
    }
  };

  const handleRemoveSpecialOffer = (index: number) => {
    setCampaign(prev => ({
      ...prev,
      content: {
        ...prev.content!,
        specialOffers: prev.content?.specialOffers.filter((_, i) => i !== index) || []
      }
    }));
  };

  const handleImageGenerated = (imageUrl: string) => {
    setCampaign(prev => ({
      ...prev,
      content: {
        ...prev.content!,
        imageUrl
      }
    }));
  };

  const handleGenerateContent = async () => {
    try {
      const response = await generateMarketingContent(campaign);
      
      if (response.error) {
        throw new Error(response.error);
      }

      // Parse the generated content
      const content = response.content;
      const lines = content.split('\n');
      let headline = '';
      let description = '';
      let callToAction = '';

      // Simple parsing logic - can be improved based on actual response format
      for (const line of lines) {
        if (line.toLowerCase().includes('headline:')) {
          headline = line.split(':')[1].trim();
        } else if (line.toLowerCase().includes('description:')) {
          description = line.split(':')[1].trim();
        } else if (line.toLowerCase().includes('call to action:')) {
          callToAction = line.split(':')[1].trim();
        }
      }

      setCampaign(prev => ({
        ...prev,
        content: {
          ...prev.content!,
          headline,
          description,
          callToAction
        }
      }));
    } catch (error) {
      console.error('Error generating content:', error);
      // You might want to show an error message to the user here
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Campaign Name"
                value={campaign.name || ''}
                onChange={(e) => setCampaign(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Design Type</InputLabel>
                <Select
                  value={campaign.designType || ''}
                  onChange={(e) => setCampaign(prev => ({ ...prev, designType: e.target.value as any }))}
                >
                  <MenuItem value="postcard">Postcard</MenuItem>
                  <MenuItem value="letter">Letter</MenuItem>
                  <MenuItem value="brochure">Brochure</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Area (ZIP codes or neighborhoods)"
                value={campaign.targetArea || ''}
                onChange={(e) => setCampaign(prev => ({ ...prev, targetArea: e.target.value }))}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <DalleImageGenerator
                onImageGenerated={handleImageGenerated}
                currentImage={campaign.content?.imageUrl}
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Campaign Content</Typography>
                <Button
                  variant="outlined"
                  onClick={handleGenerateContent}
                  startIcon={<ImageIcon />}
                >
                  Generate Content
                </Button>
              </Box>
              <TextField
                fullWidth
                label="Headline"
                value={campaign.content?.headline || ''}
                onChange={(e) => setCampaign(prev => ({
                  ...prev,
                  content: {
                    ...prev.content!,
                    headline: e.target.value
                  }
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={campaign.content?.description || ''}
                onChange={(e) => setCampaign(prev => ({
                  ...prev,
                  content: {
                    ...prev.content!,
                    description: e.target.value
                  }
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Call to Action"
                value={campaign.content?.callToAction || ''}
                onChange={(e) => setCampaign(prev => ({
                  ...prev,
                  content: {
                    ...prev.content!,
                    callToAction: e.target.value
                  }
                }))}
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Special Offers
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                  {campaign.content?.specialOffers?.map((offer, index) => (
                    <Chip
                      key={index}
                      label={offer}
                      onDelete={() => handleRemoveSpecialOffer(index)}
                    />
                  ))}
                </Box>
                <Button
                  variant="outlined"
                  onClick={handleAddSpecialOffer}
                >
                  Add Special Offer
                </Button>
              </Box>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography gutterBottom>Mailing Size</Typography>
              <Slider
                value={campaign.mailingSize || 1000}
                onChange={(_, value) => setCampaign(prev => ({ ...prev, mailingSize: value as number }))}
                min={100}
                max={10000}
                step={100}
                marks
              />
              <Typography variant="caption" display="block" align="center">
                {campaign.mailingSize || 1000} pieces
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Budget"
                value={campaign.budget || ''}
                onChange={(e) => setCampaign(prev => ({ ...prev, budget: Number(e.target.value) }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={campaign.trackingEnabled || false}
                    onChange={(e) => setCampaign(prev => ({ ...prev, trackingEnabled: e.target.checked }))}
                  />
                }
                label="Enable Campaign Tracking"
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Campaign Summary
                  </Typography>
                  {campaign.content?.imageUrl && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Campaign Image
                      </Typography>
                      <CardMedia
                        component="img"
                        height="200"
                        image={campaign.content.imageUrl}
                        alt="Campaign image"
                      />
                    </Box>
                  )}
                  <Typography variant="body1">
                    <strong>Name:</strong> {campaign.name}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Design Type:</strong> {campaign.designType}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Target Area:</strong> {campaign.targetArea}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Mailing Size:</strong> {campaign.mailingSize} pieces
                  </Typography>
                  <Typography variant="body1">
                    <strong>Budget:</strong> ${campaign.budget}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Headline:</strong> {campaign.content?.headline}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Special Offers:</strong>
                  </Typography>
                  <ul>
                    {campaign.content?.specialOffers?.map((offer, index) => (
                      <li key={index}>{offer}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <PrivacyCoordinator
                campaignData={campaign}
                onPrivacyStatusChange={setPrivacyStatus}
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Local Mailer Campaign Creator
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper sx={{ p: 3, mb: 3 }}>
        {renderStepContent(activeStep)}
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
        >
          Back
        </Button>
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={
            activeStep === steps.length - 1 && 
            privacyStatus !== 'compliant'
          }
        >
          {activeStep === steps.length - 1 ? 'Launch Campaign' : 'Next'}
        </Button>
      </Box>
    </Box>
  );
};

export default LocalMailerWorkflow; 