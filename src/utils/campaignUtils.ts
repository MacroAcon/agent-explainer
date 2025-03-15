import { z } from 'zod';
import { CampaignFormData, ValidationResult } from '../types/campaign';

export interface ParsedContent {
  headline: string;
  description: string;
  callToAction: string;
  imagePrompt?: string;
}

export interface CampaignFormData {
  name: string;
  designType: 'postcard' | 'letter' | 'brochure';
  targetArea: string;
  content: {
    specialOffers: string[];
  };
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Parses AI-generated content into structured format
 * @param content Raw content string from AI response
 * @returns Object containing parsed headline, description, and call to action
 */
export const parseAIContent = (content: string): ParsedContent => {
  try {
    return JSON.parse(content);
  } catch (error) {
    console.error('Failed to parse AI content:', error);
    return {
      headline: '',
      description: '',
      callToAction: '',
    };
  }
};

/**
 * Formats validation errors from Zod into a user-friendly message
 * @param error Zod validation error
 * @returns Formatted error message string
 */
export const formatValidationError = (error: z.ZodError): string => {
  return `Validation failed: ${error.errors.map(e => e.message).join(', ')}`;
};

/**
 * Validates a ZIP code string
 * @param zip ZIP code to validate
 * @returns true if valid, false otherwise
 */
export const isValidZipCode = (zipCode: string): boolean => {
  return /^\d{5}$/.test(zipCode);
};

/**
 * Formats a campaign name to be URL and file system safe
 * @param name Raw campaign name
 * @returns Formatted campaign name
 */
export const formatCampaignName = (name: string): string => {
  return name.trim().replace(/\s+/g, ' ');
};

/**
 * Removes empty special offers from the array
 * @param offers Array of special offers
 * @returns Filtered array without empty offers
 */
export const cleanSpecialOffers = (offers: string[]): string[] => {
  return offers.filter(offer => offer.trim()).map(offer => offer.trim());
};

/**
 * Creates a prompt for the AI based on campaign details
 * @param campaignName Name of the campaign
 * @param designType Type of design (postcard, letter, brochure)
 * @param targetArea Target ZIP code
 * @param specialOffers Array of special offers
 * @returns Formatted prompt string
 */
export const createAIPrompt = (
  campaignName: string,
  designType: string,
  targetArea: string,
  specialOffers: string[] = []
): string => {
  const cleanedOffers = cleanSpecialOffers(specialOffers);
  
  return `Create marketing content for a local mailer campaign with these details:
Campaign Name: ${campaignName}
Design Type: ${designType}
Target Area: ${targetArea}
Special Offers: ${cleanedOffers.length > 0 ? cleanedOffers.join(', ') : 'None specified'}

Generate a compelling headline, description, and call-to-action that will resonate with the target audience.
Format the response as follows:
Headline: [your headline]
Description: [your description]
Call to Action: [your call to action]`;
};

/**
 * Validates form data before submission
 * @param data Form data to validate
 * @returns Validation result with errors if any
 */
export const validateFormData = (data: CampaignFormData): ValidationResult => {
  const errors: string[] = [];

  if (!data.name.trim()) {
    errors.push('Campaign name is required');
  }

  if (!data.designType) {
    errors.push('Design type is required');
  }

  if (!isValidZipCode(data.targetArea)) {
    errors.push('Target area must be a valid 5-digit ZIP code');
  }

  if (!data.content.specialOffers.length || data.content.specialOffers.some(offer => !offer.trim())) {
    errors.push('At least one special offer is required');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Creates a default campaign form data object
 * @returns Default campaign form data
 */
export const createDefaultFormData = (): CampaignFormData => ({
  name: '',
  designType: 'postcard',
  targetArea: '',
  content: {
    specialOffers: [''],
  },
});

/**
 * Formats a special offer for display
 * @param offer Special offer text
 * @param index Offer index
 * @returns Formatted offer text
 */
export const formatSpecialOffer = (offer: string, index: number): string => {
  return `Special Offer ${index + 1}`;
};

/**
 * Truncates text to a specified length
 * @param text Text to truncate
 * @param maxLength Maximum length
 * @returns Truncated text
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

/**
 * Formats a date string into a human-readable format
 * @param dateString ISO date string
 * @returns Formatted date string
 */
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}; 