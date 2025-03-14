/**
 * PII Detection and Masking Utility
 * 
 * Detects and masks personally identifiable information (PII) in text
 * to enhance privacy and security in agent interactions.
 */

type MaskingStrategy = 'redact' | 'hash' | 'tokenize' | 'partial';

interface PIIDetectorOptions {
  strategy: MaskingStrategy;
  preserveFormat: boolean;
  keepLastDigits?: number;
}

const DEFAULT_OPTIONS: PIIDetectorOptions = {
  strategy: 'redact',
  preserveFormat: true,
  keepLastDigits: 4,
};

interface DetectionPattern {
  type: string;
  regex: RegExp;
  mask: (match: string, options: PIIDetectorOptions) => string;
}

// Collection of patterns to detect common PII
const PII_PATTERNS: DetectionPattern[] = [
  {
    type: 'email',
    regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    mask: (match, options) => {
      if (options.strategy === 'redact') {
        return '[EMAIL REDACTED]';
      } else if (options.strategy === 'partial') {
        const [username, domain] = match.split('@');
        return `${username.substring(0, 2)}***@${domain}`;
      } else if (options.strategy === 'hash') {
        return `[HASHED:${hashData(match)}]`;
      }
      return '[EMAIL PROTECTED]';
    },
  },
  {
    type: 'phone',
    regex: /\b(\+\d{1,3}[\s.-]?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b/g,
    mask: (match, options) => {
      if (options.strategy === 'redact') {
        return '[PHONE REDACTED]';
      } else if (options.strategy === 'partial') {
        const digits = match.replace(/\D/g, '');
        const keep = options.keepLastDigits || 4;
        const masked = digits.slice(0, -keep).replace(/\d/g, '*') + digits.slice(-keep);
        
        if (options.preserveFormat) {
          let maskedIndex = 0;
          return match.replace(/\d/g, () => (maskedIndex < digits.length) ? masked[maskedIndex++] : '*');
        }
        return masked;
      }
      return '[PHONE PROTECTED]';
    },
  },
  {
    type: 'ssn',
    regex: /\b\d{3}[-]?\d{2}[-]?\d{4}\b/g,
    mask: (match, options) => {
      if (options.strategy === 'redact') {
        return '[SSN REDACTED]';
      } else if (options.strategy === 'partial') {
        return match.replace(/\d/g, (digit, index) => {
          const digitsOnly = match.replace(/\D/g, '');
          const totalDigits = digitsOnly.length;
          return index >= (totalDigits - (options.keepLastDigits || 4)) ? digit : '*';
        });
      }
      return '[SSN PROTECTED]';
    },
  },
  {
    type: 'creditCard',
    regex: /\b(?:\d[ -]*?){13,16}\b/g,
    mask: (match, options) => {
      if (options.strategy === 'redact') {
        return '[CREDIT CARD REDACTED]';
      } else if (options.strategy === 'partial') {
        const digits = match.replace(/\D/g, '');
        const keep = options.keepLastDigits || 4;
        return digits.slice(0, -keep).replace(/\d/g, '*') + digits.slice(-keep);
      }
      return '[PAYMENT INFO PROTECTED]';
    },
  },
  {
    type: 'address',
    // Simplified pattern - real implementation would be more robust
    regex: /\b\d+\s+[A-Za-z\s]+,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(-\d{4})?\b/g,
    mask: () => '[ADDRESS REDACTED]',
  },
  {
    type: 'name',
    // This is a simplistic approach - name detection is complex and likely needs NER
    regex: /\b(Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b/g,
    mask: () => '[NAME REDACTED]',
  }
];

/**
 * Simple hash function for demonstration
 * In production, use a proper cryptographic hashing function
 */
function hashData(data: string): string {
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(16).substring(0, 8);
}

/**
 * Detects and masks PII in the provided text
 */
export function detectAndMaskPII(
  text: string, 
  customOptions?: Partial<PIIDetectorOptions>
): string {
  if (!text) return text;
  
  const options = { ...DEFAULT_OPTIONS, ...customOptions };
  let maskedText = text;
  
  for (const pattern of PII_PATTERNS) {
    maskedText = maskedText.replace(pattern.regex, (match) => {
      return pattern.mask(match, options);
    });
  }
  
  return maskedText;
}

/**
 * Detects if a text likely contains PII without performing masking
 */
export function containsPII(text: string): boolean {
  if (!text) return false;
  
  return PII_PATTERNS.some(pattern => pattern.regex.test(text));
}

/**
 * Get detailed information about what types of PII were detected
 */
export function analyzeText(text: string): { hasPII: boolean; detectedTypes: string[] } {
  if (!text) return { hasPII: false, detectedTypes: [] };
  
  const detectedTypes: string[] = [];
  for (const pattern of PII_PATTERNS) {
    // Reset lastIndex to ensure we test from the beginning of the string
    pattern.regex.lastIndex = 0;
    if (pattern.regex.test(text)) {
      detectedTypes.push(pattern.type);
    }
  }
  
  return {
    hasPII: detectedTypes.length > 0,
    detectedTypes
  };
}

export default {
  detectAndMaskPII,
  containsPII,
  analyzeText
}; 