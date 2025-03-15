import { z } from 'zod';
import { CampaignFormData as FormData, ValidationResult as ValidationResultType } from '../types/campaign';

export interface ParsedContent {
  headline: string;
  description: string;
  callToAction: string;
  imagePrompt?: string;
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
 * Cleans special offers array by removing empty strings and trimming whitespace
 * @param offers Array of special offers
 * @returns Cleaned array of special offers
 */
export const cleanSpecialOffers = (offers: string[]): string[] => {
  if (!offers) return [];
  return offers.map(offer => offer.trim()).filter(offer => offer.length > 0);
};

/**
 * Validates a US ZIP code
 * @param zipCode ZIP code to validate
 * @returns True if valid, false otherwise
 */
export const isValidZipCode = (zipCode: string): boolean => {
  return /^\d{5}(-\d{4})?$/.test(zipCode);
};

/**
 * Formats a campaign name by capitalizing words and replacing underscores with spaces
 * @param name Campaign name to format
 * @returns Formatted campaign name
 */
export const formatCampaignName = (name: string): string => {
  if (!name) return '';
  return name
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Formats a special offer for display
 * @param offer Special offer to format
 * @returns Formatted special offer
 */
export const formatSpecialOffer = (offer: string): string => {
  if (!offer) return '';
  return offer.trim().charAt(0).toUpperCase() + offer.trim().slice(1);
};

/**
 * Creates an AI prompt for generating marketing content
 * @param campaignName Name of the campaign
 * @param designType Type of design (postcard, letter, brochure)
 * @param targetArea Target ZIP code
 * @param specialOffers Array of special offers
 * @returns Formatted prompt for AI
 */
export const createAIPrompt = (
  campaignName: string,
  designType: string,
  targetArea: string,
  specialOffers?: string[]
): string => {
  let prompt = `Create marketing content for a ${designType} campaign named "${campaignName}" targeting ZIP code ${targetArea}.`;
  
  if (specialOffers && specialOffers.length > 0) {
    prompt += ` Include these special offers: ${specialOffers.join(', ')}.`;
  }
  
  prompt += ` Return a JSON object with these fields: "headline" (catchy headline), "description" (compelling description), and "callToAction" (strong call to action).`;
  
  return prompt;
};

/**
 * Validates form data
 * @param data Form data to validate
 * @returns Validation result
 */
export const validateFormData = (data: FormData): ValidationResultType => {
  const errors: string[] = [];
  
  if (!data.name || data.name.trim().length === 0) {
    errors.push('Campaign name is required');
  }
  
  if (!data.designType) {
    errors.push('Design type is required');
  }
  
  if (!data.targetArea || !isValidZipCode(data.targetArea)) {
    errors.push('Valid ZIP code is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Creates default form data
 * @returns Default form data
 */
export const createDefaultFormData = (): FormData => {
  return {
    name: '',
    designType: 'postcard',
    targetArea: '',
    content: {
      specialOffers: [''],
    },
  };
};

/**
 * Formats a date for display
 * @param date Date to format
 * @returns Formatted date string
 */
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}; 