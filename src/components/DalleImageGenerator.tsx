import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  CircularProgress,
  Paper,
  Typography,
  Alert,
  Grid,
  Card,
  CardMedia,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Image as ImageIcon } from '@mui/icons-material';
import { generateImagePrompt } from '../services/groqService';

interface DalleImageGeneratorProps {
  onImageGenerated: (imageUrl: string) => void;
  currentImage?: string;
}

const DalleImageGenerator: React.FC<DalleImageGeneratorProps> = ({ onImageGenerated, currentImage }) => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedPrompt, setGeneratedPrompt] = useState<string | null>(null);
  const [showPromptDialog, setShowPromptDialog] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt for the image generation');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Generate an optimized prompt using Groq
      const promptResponse = await generateImagePrompt(prompt);
      
      if (promptResponse.error) {
        throw new Error(promptResponse.error);
      }

      setGeneratedPrompt(promptResponse.content);
      setShowPromptDialog(true);

      // For now, we'll use a placeholder image service
      // In a real implementation, you would use a free image generation service
      // like Stable Diffusion or a similar open-source model
      const mockImageUrl = `https://picsum.photos/seed/${Date.now()}/800/600`;
      onImageGenerated(mockImageUrl);
    } catch (err) {
      setError('Failed to generate image. Please try again.');
      console.error('Image generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUsePrompt = () => {
    setShowPromptDialog(false);
    // Here you would typically use the generated prompt with your chosen image generation service
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Campaign Image Generator
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Image Description"
            placeholder="Describe the image you want to generate..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isGenerating}
          />
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            startIcon={isGenerating ? <CircularProgress size={20} /> : <ImageIcon />}
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
          >
            {isGenerating ? 'Generating...' : 'Generate Image'}
          </Button>
        </Grid>

        {error && (
          <Grid item xs={12}>
            <Alert severity="error">{error}</Alert>
          </Grid>
        )}

        {(currentImage || isGenerating) && (
          <Grid item xs={12}>
            <Card>
              <CardMedia
                component="img"
                height="300"
                image={currentImage || 'https://via.placeholder.com/800x600?text=Generating...'}
                alt="Generated campaign image"
              />
              <CardActions>
                <Button size="small" color="primary">
                  Use This Image
                </Button>
                <Button size="small" color="error">
                  Generate New
                </Button>
              </CardActions>
            </Card>
          </Grid>
        )}
      </Grid>

      <Dialog open={showPromptDialog} onClose={() => setShowPromptDialog(false)}>
        <DialogTitle>Generated Image Prompt</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mt: 2 }}>
            {generatedPrompt}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPromptDialog(false)}>Cancel</Button>
          <Button onClick={handleUsePrompt} variant="contained">
            Use This Prompt
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default DalleImageGenerator; 