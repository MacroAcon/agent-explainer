export type DesignType = 'postcard' | 'letter' | 'brochure';

export type CampaignStatus = 'draft' | 'in_review' | 'approved' | 'printing' | 'shipping' | 'completed' | 'cancelled';

export interface CampaignGoals {
  primaryGoal: string;
  targetResponseRate: number;
  expectedROI: number;
  timeline: {
    startDate: string;
    endDate: string;
  };
}

export interface TargetAudience {
  demographics: {
    ageRange?: [number, number];
    incomeRange?: [number, number];
    householdSize?: number;
  };
  psychographics?: string[];
  behavior?: string[];
}

export interface SpecialOffer {
  title: string;
  description: string;
  validUntil?: string;
  terms?: string;
  redemptionCode?: string;
}

export interface DesignSpecs {
  dimensions: {
    width: number;
    height: number;
  };
  paperStock: string;
  finish: string;
  colorMode: 'CMYK' | 'RGB';
  bleed: number;
}

export interface MailingList {
  targetZIPCodes: string[];
  estimatedRecipients: number;
  listSource: string;
  lastUpdated: string;
}

export interface PostageDetails {
  postageClass: string;
  rate: number;
  totalCost: number;
  estimatedDeliveryTime: string;
}

export interface CampaignContent {
  headline: string;
  description: string;
  callToAction: string;
  specialOffers: SpecialOffer[];
  imagePrompt?: string;
  legalDisclaimers?: string[];
  trackingCode?: string;
}

export interface CampaignBudget {
  designCost: number;
  printingCost: number;
  postageCost: number;
  listCost: number;
  totalBudget: number;
}

export interface CampaignMetrics {
  sentCount: number;
  deliveredCount: number;
  responseCount: number;
  responseRate: number;
  revenueGenerated: number;
  roi: number;
}

export interface Campaign {
  id: string;
  name: string;
  businessId: string;
  status: 'draft' | 'in_review' | 'approved' | 'printing' | 'shipping' | 'completed' | 'cancelled';
  designType: DesignType;
  goals: CampaignGoals;
  targetAudience: TargetAudience;
  content: CampaignContent;
  designSpecs: DesignSpecs;
  mailingList: MailingList;
  postageDetails: PostageDetails;
  budget: CampaignBudget;
  metrics?: CampaignMetrics;
  createdAt: string;
  updatedAt: string;
  approvedAt?: string;
  shippedAt?: string;
  completedAt?: string;
  cancelledAt?: string;
  notes?: string[];
}

export interface CampaignDraft {
  id: string;
  campaignId: string;
  version: number;
  content: CampaignContent;
  designSpecs: DesignSpecs;
  status: 'pending' | 'approved' | 'rejected';
  feedback?: string[];
  createdAt: string;
  updatedAt: string;
  approvedAt?: string;
  rejectedAt?: string;
}

export interface CampaignReview {
  id: string;
  campaignId: string;
  reviewerId: string;
  status: 'pending' | 'approved' | 'rejected';
  feedback: string[];
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
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