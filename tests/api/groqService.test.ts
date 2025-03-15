import { generateMarketingContent, generateImagePrompt } from '../../src/services/groqService';
import { mockDeep } from 'jest-mock-extended';

// Mock the Groq client
jest.mock('groq', () => {
  return jest.fn().mockImplementation(() => {
    return {
      chat: {
        completions: {
          create: jest.fn()
        }
      }
    };
  });
});

describe('Groq Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generateMarketingContent', () => {
    const validCampaignDetails = {
      name: 'Summer Sale 2024',
      designType: 'postcard',
      targetArea: '12345',
      content: {
        specialOffers: ['20% off all products', 'Free shipping on orders over $50']
      }
    };

    it('should generate marketing content successfully', async () => {
      // Arrange
      const mockCompletion = {
        choices: [
          {
            message: {
              content: '{"headline":"Amazing Summer Deals!","description":"Shop our summer collection with incredible discounts.","callToAction":"Visit us today!"}'
            }
          }
        ]
      };
      
      require('groq')().chat.completions.create.mockResolvedValueOnce(mockCompletion);

      // Act
      const result = await generateMarketingContent(validCampaignDetails);

      // Assert
      expect(result.content).toBe(mockCompletion.choices[0].message.content);
      expect(result.error).toBeUndefined();
      expect(require('groq')().chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'llama-3.3-70b-versatile',
          messages: expect.arrayContaining([
            expect.objectContaining({ role: 'system' }),
            expect.objectContaining({ role: 'user' })
          ])
        })
      );
    });

    it('should handle validation errors', async () => {
      // Arrange
      const invalidCampaignDetails = {
        name: '',
        designType: 'invalid-type',
        targetArea: 'not-a-zip',
      };

      // Act
      const result = await generateMarketingContent(invalidCampaignDetails);

      // Assert
      expect(result.content).toBe('');
      expect(result.error).toBeDefined();
      expect(require('groq')().chat.completions.create).not.toHaveBeenCalled();
    });

    it('should handle API errors', async () => {
      // Arrange
      require('groq')().chat.completions.create.mockRejectedValueOnce(
        new Error('API Error')
      );

      // Act
      const result = await generateMarketingContent(validCampaignDetails);

      // Assert
      expect(result.content).toBe('');
      expect(result.error).toBe('API Error');
    });
  });

  describe('generateImagePrompt', () => {
    it('should generate image prompt successfully', async () => {
      // Arrange
      const mockCompletion = {
        choices: [
          {
            message: {
              content: 'Professional image of a retail store with summer sale signs'
            }
          }
        ]
      };
      
      require('groq')().chat.completions.create.mockResolvedValueOnce(mockCompletion);

      // Act
      const result = await generateImagePrompt('A store with summer sale');

      // Assert
      expect(result.content).toBe(mockCompletion.choices[0].message.content);
      expect(result.error).toBeUndefined();
      expect(require('groq')().chat.completions.create).toHaveBeenCalledWith(
        expect.objectContaining({
          model: 'llama-3.3-70b-versatile',
          messages: expect.arrayContaining([
            expect.objectContaining({ role: 'system' }),
            expect.objectContaining({ role: 'user' })
          ])
        })
      );
    });

    it('should handle empty description', async () => {
      // Act
      const result = await generateImagePrompt('');

      // Assert
      expect(result.content).toBe('');
      expect(result.error).toBeDefined();
      expect(require('groq')().chat.completions.create).not.toHaveBeenCalled();
    });

    it('should handle API errors', async () => {
      // Arrange
      require('groq')().chat.completions.create.mockRejectedValueOnce(
        new Error('API Error')
      );

      // Act
      const result = await generateImagePrompt('A store with summer sale');

      // Assert
      expect(result.content).toBe('');
      expect(result.error).toBe('API Error');
    });
  });
}); 