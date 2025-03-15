import { Campaign, CampaignDraft, CampaignReview, CampaignContent, DesignSpecs, MailingList, PostageDetails } from '../types/campaign';
import { generateMarketingContent, generateImagePrompt } from './groqService';
import { validateFormData, cleanSpecialOffers } from '../utils/campaignUtils';

export class CampaignService {
  private static instance: CampaignService;
  private campaigns: Map<string, Campaign> = new Map();
  private drafts: Map<string, CampaignDraft> = new Map();
  private reviews: Map<string, CampaignReview> = new Map();

  private constructor() {}

  static getInstance(): CampaignService {
    if (!CampaignService.instance) {
      CampaignService.instance = new CampaignService();
    }
    return CampaignService.instance;
  }

  async createCampaign(campaignData: Partial<Campaign>): Promise<Campaign> {
    // Generate content using AI
    const contentResponse = await generateMarketingContent({
      name: campaignData.name || '',
      designType: campaignData.designType || 'postcard',
      targetArea: campaignData.mailingList?.targetZIPCodes[0] || '',
      content: {
        specialOffers: campaignData.content?.specialOffers || [],
      },
    });

    if (contentResponse.error) {
      throw new Error(`Failed to generate content: ${contentResponse.error}`);
    }

    // Generate image prompt
    const imagePromptResponse = await generateImagePrompt(contentResponse.content);
    if (imagePromptResponse.error) {
      throw new Error(`Failed to generate image prompt: ${imagePromptResponse.error}`);
    }

    // Create campaign object
    const campaign: Campaign = {
      id: crypto.randomUUID(),
      name: campaignData.name || '',
      businessId: campaignData.businessId || '',
      status: 'draft',
      designType: campaignData.designType || 'postcard',
      goals: campaignData.goals || {
        primaryGoal: '',
        targetResponseRate: 0,
        expectedROI: 0,
        timeline: {
          startDate: new Date().toISOString(),
          endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days from now
        },
      },
      targetAudience: campaignData.targetAudience || {
        demographics: {},
        psychographics: [],
        behavior: [],
      },
      content: {
        ...campaignData.content,
        headline: contentResponse.content,
        imagePrompt: imagePromptResponse.content,
      } as CampaignContent,
      designSpecs: campaignData.designSpecs || this.getDefaultDesignSpecs(campaignData.designType || 'postcard'),
      mailingList: campaignData.mailingList || {
        targetZIPCodes: [],
        estimatedRecipients: 0,
        listSource: '',
        lastUpdated: new Date().toISOString(),
      },
      postageDetails: campaignData.postageDetails || {
        postageClass: 'Standard',
        rate: 0,
        totalCost: 0,
        estimatedDeliveryTime: '3-5 business days',
      },
      budget: campaignData.budget || {
        designCost: 0,
        printingCost: 0,
        postageCost: 0,
        listCost: 0,
        totalBudget: 0,
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      notes: [],
    };

    this.campaigns.set(campaign.id, campaign);
    return campaign;
  }

  async createDraft(campaignId: string, content: CampaignContent, designSpecs: DesignSpecs): Promise<CampaignDraft> {
    const campaign = this.campaigns.get(campaignId);
    if (!campaign) {
      throw new Error('Campaign not found');
    }

    const draft: CampaignDraft = {
      id: crypto.randomUUID(),
      campaignId,
      version: this.getNextDraftVersion(campaignId),
      content,
      designSpecs,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.drafts.set(draft.id, draft);
    return draft;
  }

  async submitForReview(campaignId: string, draftId: string): Promise<CampaignReview> {
    const campaign = this.campaigns.get(campaignId);
    const draft = this.drafts.get(draftId);

    if (!campaign || !draft) {
      throw new Error('Campaign or draft not found');
    }

    const review: CampaignReview = {
      id: crypto.randomUUID(),
      campaignId,
      reviewerId: 'system', // Replace with actual reviewer ID
      status: 'pending',
      feedback: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.reviews.set(review.id, review);
    campaign.status = 'in_review';
    this.campaigns.set(campaignId, campaign);

    return review;
  }

  async approveCampaign(campaignId: string, reviewId: string): Promise<Campaign> {
    const campaign = this.campaigns.get(campaignId);
    const review = this.reviews.get(reviewId);

    if (!campaign || !review) {
      throw new Error('Campaign or review not found');
    }

    campaign.status = 'approved';
    campaign.approvedAt = new Date().toISOString();
    campaign.updatedAt = new Date().toISOString();

    review.status = 'approved';
    review.completedAt = new Date().toISOString();
    review.updatedAt = new Date().toISOString();

    this.campaigns.set(campaignId, campaign);
    this.reviews.set(reviewId, review);

    return campaign;
  }

  async rejectCampaign(campaignId: string, reviewId: string, feedback: string[]): Promise<Campaign> {
    const campaign = this.campaigns.get(campaignId);
    const review = this.reviews.get(reviewId);

    if (!campaign || !review) {
      throw new Error('Campaign or review not found');
    }

    campaign.status = 'draft';
    campaign.updatedAt = new Date().toISOString();
    campaign.notes = [...(campaign.notes || []), ...feedback];

    review.status = 'rejected';
    review.feedback = feedback;
    review.completedAt = new Date().toISOString();
    review.updatedAt = new Date().toISOString();

    this.campaigns.set(campaignId, campaign);
    this.reviews.set(reviewId, review);

    return campaign;
  }

  private getDefaultDesignSpecs(designType: string): DesignSpecs {
    const specs: Record<string, DesignSpecs> = {
      postcard: {
        dimensions: { width: 6, height: 4.25 },
        paperStock: '14pt Card Stock',
        finish: 'Glossy',
        colorMode: 'CMYK',
        bleed: 0.125,
      },
      letter: {
        dimensions: { width: 8.5, height: 11 },
        paperStock: '24lb Bond',
        finish: 'Matte',
        colorMode: 'CMYK',
        bleed: 0,
      },
      brochure: {
        dimensions: { width: 8.5, height: 11 },
        paperStock: '100lb Gloss',
        finish: 'Glossy',
        colorMode: 'CMYK',
        bleed: 0.125,
      },
    };

    return specs[designType] || specs.postcard;
  }

  private getNextDraftVersion(campaignId: string): number {
    const drafts = Array.from(this.drafts.values())
      .filter(d => d.campaignId === campaignId);
    return drafts.length + 1;
  }

  // Getters
  getCampaign(id: string): Campaign | undefined {
    return this.campaigns.get(id);
  }

  getDraft(id: string): CampaignDraft | undefined {
    return this.drafts.get(id);
  }

  getReview(id: string): CampaignReview | undefined {
    return this.reviews.get(id);
  }

  getAllCampaigns(): Campaign[] {
    return Array.from(this.campaigns.values());
  }

  getCampaignDrafts(campaignId: string): CampaignDraft[] {
    return Array.from(this.drafts.values())
      .filter(d => d.campaignId === campaignId);
  }

  getCampaignReviews(campaignId: string): CampaignReview[] {
    return Array.from(this.reviews.values())
      .filter(r => r.campaignId === campaignId);
  }
} 