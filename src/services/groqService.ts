import Groq from 'groq-sdk';
import { z } from 'zod';
import { createAIPrompt, formatValidationError } from '../utils/campaignUtils';

const GROQ_API_KEY = process.env.NEXT_PUBLIC_GROQ_API_KEY;

if (!GROQ_API_KEY) {
  throw new Error('NEXT_PUBLIC_GROQ_API_KEY environment variable is not set');
}

const MODEL_NAME = 'llama-3.3-70b-versatile';

// Initialize Groq client
let groq: any;
try {
  groq = new Groq({
    apiKey: GROQ_API_KEY,
  });
} catch (error) {
  console.warn('Failed to initialize Groq SDK, will use fetch API fallback:', error);
}

export interface GroqResponse {
  content: string;
  error?: string;
}

// Validation schemas
const CampaignContentSchema = z.object({
  specialOffers: z.array(z.string().min(1, 'Special offer cannot be empty')).optional(),
  headline: z.string().min(1, 'Headline is required').max(100, 'Headline is too long').optional(),
  description: z.string().min(1, 'Description is required').max(500, 'Description is too long').optional(),
  callToAction: z.string().min(1, 'Call to action is required').max(100, 'Call to action is too long').optional(),
  imageUrl: z.string().url('Invalid image URL').optional(),
});

const CampaignDetailsSchema = z.object({
  name: z.string()
    .min(1, 'Campaign name is required')
    .max(100, 'Campaign name is too long')
    .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Campaign name can only contain letters, numbers, spaces, hyphens, and underscores'),
  designType: z.enum(['postcard', 'letter', 'brochure'], {
    errorMap: () => ({ message: 'Design type must be postcard, letter, or brochure' })
  }),
  targetArea: z.string()
    .min(1, 'Target area is required')
    .regex(/^\d{5}(-\d{4})?$/, 'Target area must be a valid ZIP code'),
  content: CampaignContentSchema.optional(),
});

type CampaignDetails = z.infer<typeof CampaignDetailsSchema>;

export class ValidationError extends Error {
  constructor(public errors: z.ZodError) {
    super('Validation failed');
    this.name = 'ValidationError';
  }
}

// Fallback function to use fetch API if Groq SDK fails
async function fetchGroqApi(endpoint: string, body: any): Promise<any> {
  const response = await fetch(`https://api.groq.com/openai/v1/${endpoint}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export const generateImagePrompt = async (description: string): Promise<GroqResponse> => {
  try {
    // Validate description
    if (!description.trim()) {
      throw new Error('Description cannot be empty');
    }

    const prompt = `Create a detailed image generation prompt for a marketing mailer based on this description: "${description}". 
    The prompt should be optimized for creating a professional, engaging marketing image. 
    Include details about style, composition, and mood.`;

    let content: string;

    if (groq) {
      // Use Groq SDK if available
      try {
        const completion = await groq.chat.completions.create({
          messages: [
            {
              role: "system",
              content: "You are an expert at creating detailed image generation prompts for marketing materials."
            },
            {
              role: "user",
              content: prompt
            }
          ],
          model: MODEL_NAME,
          temperature: 0.7,
          max_tokens: 500,
        });
        content = completion.choices[0]?.message?.content || 'Failed to generate prompt';
      } catch (sdkError) {
        console.warn('Groq SDK error, falling back to fetch API:', sdkError);
        // Fallback to fetch API
        const data = await fetchGroqApi('chat/completions', {
          messages: [
            {
              role: "system",
              content: "You are an expert at creating detailed image generation prompts for marketing materials."
            },
            {
              role: "user",
              content: prompt
            }
          ],
          model: MODEL_NAME,
          temperature: 0.7,
          max_tokens: 500,
        });
        content = data.choices[0]?.message?.content || 'Failed to generate prompt';
      }
    } else {
      // No SDK initialized, use fetch API directly
      const data = await fetchGroqApi('chat/completions', {
        messages: [
          {
            role: "system",
            content: "You are an expert at creating detailed image generation prompts for marketing materials."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        model: MODEL_NAME,
        temperature: 0.7,
        max_tokens: 500,
      });
      content = data.choices[0]?.message?.content || 'Failed to generate prompt';
    }

    return { content };
  } catch (error) {
    console.error('Error generating image prompt:', error);
    return {
      content: '',
      error: error instanceof Error ? error.message : 'Failed to generate image prompt'
    };
  }
};

export const generateMarketingContent = async (campaignDetails: unknown): Promise<GroqResponse> => {
  try {
    // Validate campaign details
    const validatedData = CampaignDetailsSchema.parse(campaignDetails);

    const prompt = createAIPrompt(
      validatedData.name,
      validatedData.designType,
      validatedData.targetArea,
      validatedData.content?.specialOffers
    );

    let content: string;

    if (groq) {
      // Use Groq SDK if available
      try {
        const completion = await groq.chat.completions.create({
          messages: [
            {
              role: "system",
              content: "You are an expert marketing copywriter specializing in local business campaigns. Always format your response with clear sections for Headline, Description, and Call to Action."
            },
            {
              role: "user",
              content: prompt
            }
          ],
          model: MODEL_NAME,
          temperature: 0.7,
          max_tokens: 1000,
        });
        content = completion.choices[0]?.message?.content || 'Failed to generate content';
      } catch (sdkError) {
        console.warn('Groq SDK error, falling back to fetch API:', sdkError);
        // Fallback to fetch API
        const data = await fetchGroqApi('chat/completions', {
          messages: [
            {
              role: "system",
              content: "You are an expert marketing copywriter specializing in local business campaigns. Always format your response with clear sections for Headline, Description, and Call to Action."
            },
            {
              role: "user",
              content: prompt
            }
          ],
          model: MODEL_NAME,
          temperature: 0.7,
          max_tokens: 1000,
        });
        content = data.choices[0]?.message?.content || 'Failed to generate content';
      }
    } else {
      // No SDK initialized, use fetch API directly
      const data = await fetchGroqApi('chat/completions', {
        messages: [
          {
            role: "system",
            content: "You are an expert marketing copywriter specializing in local business campaigns. Always format your response with clear sections for Headline, Description, and Call to Action."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        model: MODEL_NAME,
        temperature: 0.7,
        max_tokens: 1000,
      });
      content = data.choices[0]?.message?.content || 'Failed to generate content';
    }

    return { content };
  } catch (error) {
    console.error('Error generating marketing content:', error);
    
    if (error instanceof z.ZodError) {
      return {
        content: '',
        error: formatValidationError(error)
      };
    }
    
    return {
      content: '',
      error: error instanceof Error ? error.message : 'Failed to generate marketing content'
    };
  }
}; 