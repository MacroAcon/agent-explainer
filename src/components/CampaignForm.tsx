import React, { useState, useCallback, useEffect } from 'react';
import { privacyManager } from '../security/PrivacyManager';
import { performanceMonitor } from '../monitoring/PerformanceMonitor';
import { generateMarketingContent, generateImagePrompt } from '../services/groqService';
import { 
  Button, 
  TextField, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Box, 
  Typography, 
  Alert, 
  SelectChangeEvent, 
  IconButton, 
  Tooltip, 
  Stepper, 
  Step, 
  StepLabel,
  Slider,
  Chip,
  Stack,
  Autocomplete,
  Paper,
  useTheme,
  alpha
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { 
  parseAIContent, 
  cleanSpecialOffers, 
  isValidZipCode, 
  formatCampaignName,
  validateFormData,
  createDefaultFormData,
  formatSpecialOffer,
} from '../utils/campaignUtils';
import { Campaign, TargetAudience, CampaignFormData, ValidationResult } from '../types/campaign';

interface CampaignFormProps {
  onSubmit: (content: any) => void;
  onCancel?: () => void;
  initialData?: Campaign;
}

const steps = ['Basic Info', 'Target Audience', 'Content', 'Review'];

const psychographicOptions = [
  'Value-conscious',
  'Quality-focused',
  'Trend-following',
  'Traditional',
  'Adventurous',
  'Family-oriented',
  'Career-focused',
  'Health-conscious',
  'Environmentally conscious',
  'Tech-savvy'
];

const behaviorOptions = [
  'Regular shoppers',
  'Online shoppers',
  'Bargain hunters',
  'Brand loyal',
  'Impulse buyers',
  'Research-oriented',
  'Early adopters',
  'Late adopters',
  'Seasonal shoppers',
  'Weekend shoppers'
];

export const CampaignForm: React.FC<CampaignFormProps> = ({ onSubmit, onCancel, initialData }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<CampaignFormData>(
    initialData ? {
      name: initialData.name,
      designType: initialData.designType,
      targetArea: initialData.mailingList.targetZIPCodes[0] || '',
      content: {
        specialOffers: initialData.content.specialOffers.map(offer => offer.title),
      },
    } : createDefaultFormData()
  );
  const [targetAudience, setTargetAudience] = useState<TargetAudience>(
    initialData?.targetAudience || {
      demographics: {
        ageRange: [25, 65] as [number, number],
        incomeRange: [30000, 120000] as [number, number],
        householdSize: 2,
      },
      psychographics: [],
      behavior: [],
    }
  );
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validation, setValidation] = useState<ValidationResult>({ isValid: true, errors: [] });

  useEffect(() => {
    performanceMonitor.startMeasurement('campaign-form-render');
    return () => {
      performanceMonitor.endMeasurement('campaign-form-render');
    };
  }, []);

  const validateField = useCallback((field: keyof CampaignFormData, value: any) => {
    const result = validateFormData({ ...formData, [field]: value });
    setValidation(result);
    return result.isValid;
  }, [formData]);

  const handleTextInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    let processedValue = value;

    // Apply special formatting for certain fields
    if (name === 'name') {
      processedValue = formatCampaignName(value);
    }

    setFormData((prev) => ({
      ...prev,
      [name]: processedValue,
    }));
    setError(null);
    validateField(name as keyof CampaignFormData, processedValue);
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError(null);
    validateField(name as keyof CampaignFormData, value);
  };

  const handleSpecialOfferChange = (index: number, value: string) => {
    setFormData((prev) => ({
      ...prev,
      content: {
        ...prev.content,
        specialOffers: prev.content.specialOffers.map((offer: string, i: number) => (i === index ? value : offer)),
      },
    }));
    setError(null);
    validateField('content', {
      ...formData.content,
      specialOffers: formData.content.specialOffers.map((offer: string, i: number) => (i === index ? value : offer)),
    });
  };

  const addSpecialOffer = () => {
    setFormData((prev) => ({
      ...prev,
      content: {
        ...prev.content,
        specialOffers: [...prev.content.specialOffers, ''],
      },
    }));
  };

  const removeSpecialOffer = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      content: {
        ...prev.content,
        specialOffers: prev.content.specialOffers.filter((_, i) => i !== index),
      },
    }));
  };

  const handleNext = () => {
    const validationResult = validateFormData(formData);
    if (!validationResult.isValid) {
      setError(validationResult.errors.join(', '));
      return;
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    performanceMonitor.startMeasurement('campaign-submit');

    try {
      // Clean up special offers before submission
      const cleanedFormData = {
        ...formData,
        content: {
          ...formData.content,
          specialOffers: cleanSpecialOffers(formData.content.specialOffers),
        },
        targetAudience, // Include target audience data
      };

      // Check for PII in form data
      const piiCheck = privacyManager.detectPII(JSON.stringify(cleanedFormData));
      if (Object.keys(piiCheck).length > 0) {
        setError('Please remove personal information from the campaign details.');
        return;
      }

      // Validate privacy compliance
      if (!privacyManager.validatePrivacyCompliance(cleanedFormData)) {
        setError('Form data does not meet privacy requirements.');
        return;
      }

      // Track network request
      performanceMonitor.trackNetworkRequest();
      
      // Generate marketing content
      const response = await generateMarketingContent(cleanedFormData);
      
      if (response.error) {
        setError(response.error);
        return;
      }

      if (!response.content) {
        setError('Failed to generate content. Please try again.');
        return;
      }

      // Parse the response content
      const parsedContent = parseAIContent(response.content);
      
      // Generate image prompt based on the description
      if (parsedContent.description) {
        const imagePromptResponse = await generateImagePrompt(parsedContent.description);
        if (imagePromptResponse.content) {
          parsedContent.imagePrompt = imagePromptResponse.content;
        }
      }

      // Submit the final data
      await onSubmit({
        ...cleanedFormData,
        content: {
          ...cleanedFormData.content,
          ...parsedContent,
        },
      });
      
      // Report performance metrics if sampling
      if (performanceMonitor.shouldSample()) {
        await performanceMonitor.reportMetrics();
      }
    } catch (error) {
      console.error('Campaign submission failed:', error);
      setError('Failed to submit campaign. Please try again.');
    } finally {
      performanceMonitor.endMeasurement('campaign-submit');
      setIsLoading(false);
    }
  }, [formData, targetAudience, onSubmit]);

  const handleAgeRangeChange = (_event: Event, newValue: number | number[]) => {
    if (Array.isArray(newValue)) {
      setTargetAudience(prev => ({
        ...prev,
        demographics: {
          ...prev.demographics,
          ageRange: newValue as [number, number],
        },
      }));
    }
  };

  const handleIncomeRangeChange = (_event: Event, newValue: number | number[]) => {
    if (Array.isArray(newValue)) {
      setTargetAudience(prev => ({
        ...prev,
        demographics: {
          ...prev.demographics,
          incomeRange: newValue as [number, number],
        },
      }));
    }
  };

  const handleHouseholdSizeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value);
    if (!isNaN(value)) {
      setTargetAudience(prev => ({
        ...prev,
        demographics: {
          ...prev.demographics,
          householdSize: value,
        },
      }));
    }
  };

  const handlePsychographicChange = (_event: React.SyntheticEvent, newValue: string[]) => {
    setTargetAudience(prev => ({
      ...prev,
      psychographics: newValue,
    }));
  };

  const handleBehaviorChange = (_event: React.SyntheticEvent, newValue: string[]) => {
    setTargetAudience(prev => ({
      ...prev,
      behavior: newValue,
    }));
  };

  const renderTargetAudienceStep = () => {
    const { demographics, psychographics = [], behavior = [] } = targetAudience;
    const { ageRange = [25, 65], incomeRange = [30000, 120000], householdSize = 2 } = demographics;
    const theme = useTheme();

    return (
      <Box sx={{ mt: 2 }}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 4, 
            background: alpha(theme.palette.primary.main, 0.05),
            borderLeft: `4px solid ${theme.palette.primary.main}`,
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ color: theme.palette.primary.main }}>
            Demographics
          </Typography>
          
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Age Range</Typography>
              <Tooltip title="Select the age range of your target audience. This helps tailor the messaging and design to resonate with specific age groups.">
                <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
              </Tooltip>
            </Box>
            <Slider
              value={ageRange}
              onChange={handleAgeRangeChange}
              valueLabelDisplay="auto"
              min={18}
              max={100}
              marks={[
                { value: 18, label: '18' },
                { value: 65, label: '65' },
                { value: 100, label: '100' },
              ]}
              sx={{ 
                mt: 2,
                '& .MuiSlider-thumb': {
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'scale(1.2)',
                  },
                },
              }}
            />
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              mt: 1,
              px: 1,
              '& .MuiTypography-root': {
                fontWeight: 500,
                color: theme.palette.text.secondary,
              }
            }}>
              <Typography variant="body2">{ageRange[0]} years</Typography>
              <Typography variant="body2">{ageRange[1]} years</Typography>
            </Box>
          </Box>

          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Income Range</Typography>
              <Tooltip title="Specify the annual household income range of your target audience. This helps determine appropriate pricing and value propositions.">
                <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
              </Tooltip>
            </Box>
            <Slider
              value={incomeRange}
              onChange={handleIncomeRangeChange}
              valueLabelDisplay="auto"
              min={0}
              max={200000}
              step={10000}
              marks={[
                { value: 0, label: '$0' },
                { value: 100000, label: '$100k' },
                { value: 200000, label: '$200k' },
              ]}
              sx={{ 
                mt: 2,
                '& .MuiSlider-thumb': {
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'scale(1.2)',
                  },
                },
              }}
            />
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              mt: 1,
              px: 1,
              '& .MuiTypography-root': {
                fontWeight: 500,
                color: theme.palette.text.secondary,
              }
            }}>
              <Typography variant="body2">${incomeRange[0].toLocaleString()}</Typography>
              <Typography variant="body2">${incomeRange[1].toLocaleString()}</Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Average Household Size</Typography>
            <Tooltip title="Enter the typical number of people living in the households of your target audience. This helps customize offers for family sizes.">
              <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
            </Tooltip>
          </Box>
          <TextField
            fullWidth
            label="Average Household Size"
            type="number"
            value={householdSize}
            onChange={handleHouseholdSizeChange}
            margin="normal"
            inputProps={{ min: 1, max: 10 }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&:hover fieldset': {
                  borderColor: theme.palette.primary.main,
                },
              },
            }}
          />
        </Paper>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 4, 
            background: alpha(theme.palette.secondary.main, 0.05),
            borderLeft: `4px solid ${theme.palette.secondary.main}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6" sx={{ color: theme.palette.secondary.main }}>Psychographics</Typography>
            <Tooltip title="Select the psychological characteristics and lifestyle traits of your target audience. This helps create more resonant messaging.">
              <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
            </Tooltip>
          </Box>
          <Autocomplete
            multiple
            options={psychographicOptions}
            value={psychographics}
            onChange={handlePsychographicChange}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Psychographic Traits"
                placeholder="Choose traits that describe your target audience"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                  sx={{
                    backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                    color: theme.palette.secondary.main,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.secondary.main, 0.2),
                    },
                  }}
                />
              ))
            }
            sx={{ mb: 4 }}
          />
        </Paper>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 4, 
            background: alpha(theme.palette.info.main, 0.05),
            borderLeft: `4px solid ${theme.palette.info.main}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6" sx={{ color: theme.palette.info.main }}>Behavior Patterns</Typography>
            <Tooltip title="Select the shopping and consumption behaviors of your target audience. This helps optimize the timing and presentation of offers.">
              <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
            </Tooltip>
          </Box>
          <Autocomplete
            multiple
            options={behaviorOptions}
            value={behavior}
            onChange={handleBehaviorChange}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Behavior Patterns"
                placeholder="Choose behaviors that describe your target audience"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                  sx={{
                    backgroundColor: alpha(theme.palette.info.main, 0.1),
                    color: theme.palette.info.main,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.info.main, 0.2),
                    },
                  }}
                />
              ))
            }
            sx={{ mb: 4 }}
          />
        </Paper>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            background: alpha(theme.palette.success.main, 0.05),
            borderLeft: `4px solid ${theme.palette.success.main}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6" sx={{ color: theme.palette.success.main }}>Target Audience Summary</Typography>
            <Tooltip title="Review your target audience configuration before proceeding to the next step.">
              <InfoIcon fontSize="small" sx={{ color: 'action.active', cursor: 'help' }} />
            </Tooltip>
          </Box>
          <Stack spacing={2}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircleIcon sx={{ color: theme.palette.success.main }} />
              <Typography variant="body2">
                Age: {ageRange[0]} - {ageRange[1]} years
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircleIcon sx={{ color: theme.palette.success.main }} />
              <Typography variant="body2">
                Income: ${incomeRange[0].toLocaleString()} - ${incomeRange[1].toLocaleString()}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircleIcon sx={{ color: theme.palette.success.main }} />
              <Typography variant="body2">
                Household Size: {householdSize}
              </Typography>
            </Box>
            {psychographics.length > 0 && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircleIcon sx={{ color: theme.palette.success.main }} />
                <Typography variant="body2">
                  Psychographics: {psychographics.join(', ')}
                </Typography>
              </Box>
            )}
            {behavior.length > 0 && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckCircleIcon sx={{ color: theme.palette.success.main }} />
                <Typography variant="body2">
                  Behaviors: {behavior.join(', ')}
                </Typography>
              </Box>
            )}
          </Stack>
        </Paper>
      </Box>
    );
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <>
            <TextField
              fullWidth
              label="Campaign Name"
              name="name"
              value={formData.name}
              onChange={handleTextInputChange}
              margin="normal"
              required
              error={!!validation.errors.find(e => e.includes('Campaign name'))}
              helperText={validation.errors.find(e => e.includes('Campaign name'))}
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Design Type</InputLabel>
              <Select<string>
                name="designType"
                value={formData.designType}
                onChange={handleSelectChange}
                required
                error={!!validation.errors.find(e => e.includes('Design type'))}
              >
                <MenuItem value="postcard">Postcard</MenuItem>
                <MenuItem value="letter">Letter</MenuItem>
                <MenuItem value="brochure">Brochure</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Target Area (ZIP Code)"
              name="targetArea"
              value={formData.targetArea}
              onChange={handleTextInputChange}
              margin="normal"
              required
              error={!!validation.errors.find(e => e.includes('Target area'))}
              helperText={validation.errors.find(e => e.includes('Target area')) || 'Enter a valid 5-digit ZIP code'}
            />
          </>
        );
      case 1:
        return renderTargetAudienceStep();
      case 2:
        return (
          <Box sx={{ mt: 2, mb: 1 }}>
            <Typography variant="subtitle1">Special Offers</Typography>
            {formData.content.specialOffers.map((offer, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  fullWidth
                  label={`Special Offer ${index + 1}`}
                  value={offer}
                  onChange={(e) => handleSpecialOfferChange(index, e.target.value)}
                  error={!!validation.errors.find(e => e.includes(`Special offer ${index + 1}`))}
                  helperText={validation.errors.find(e => e.includes(`Special offer ${index + 1}`))}
                />
                {formData.content.specialOffers.length > 1 && (
                  <Tooltip title="Remove Offer">
                    <IconButton
                      color="error"
                      onClick={() => removeSpecialOffer(index)}
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            ))}
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={addSpecialOffer}
              sx={{ mt: 1 }}
            >
              Add Special Offer
            </Button>
          </Box>
        );
      case 3:
        const { demographics, psychographics = [], behavior = [] } = targetAudience;
        const { ageRange = [25, 65], incomeRange = [30000, 120000], householdSize = 2 } = demographics;
        
        return (
          <Box>
            <Typography variant="h6">Review Your Campaign</Typography>
            <Typography>Name: {formData.name}</Typography>
            <Typography>Design Type: {formData.designType}</Typography>
            <Typography>Target Area: {formData.targetArea}</Typography>
            <Typography>Special Offers: {formData.content.specialOffers.length}</Typography>
            <Typography variant="subtitle1" sx={{ mt: 2 }}>Target Audience</Typography>
            <Typography>Age: {ageRange[0]} - {ageRange[1]} years</Typography>
            <Typography>Income: ${incomeRange[0].toLocaleString()} - ${incomeRange[1].toLocaleString()}</Typography>
            <Typography>Household Size: {householdSize}</Typography>
            {psychographics.length > 0 && (
              <Typography>Psychographics: {psychographics.join(', ')}</Typography>
            )}
            {behavior.length > 0 && (
              <Typography>Behaviors: {behavior.join(', ')}</Typography>
            )}
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, mx: 'auto', p: 2 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {renderStepContent(activeStep)}

      <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
        {activeStep > 0 && (
          <Button
            variant="outlined"
            onClick={handleBack}
            disabled={isLoading}
          >
            Back
          </Button>
        )}
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={isLoading}
          >
            Next
          </Button>
        ) : (
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Campaign'}
          </Button>
        )}
        {onCancel && (
          <Button
            variant="outlined"
            color="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        )}
      </Box>

      {/* Add Privacy Notice */}
      <Alert severity="info" sx={{ mb: 2 }}>
        {privacyManager.getDataRetentionPolicy()}
      </Alert>
    </Box>
  );
}; 