import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { detectAndMaskPII, containsPII, analyzeText } from './pii_detector';

// Privacy level determines how aggressively we mask PII
export type PrivacyLevel = 'low' | 'medium' | 'high' | 'maximum';

interface PrivacyContextType {
  // Current privacy settings
  privacyLevel: PrivacyLevel;
  setPrivacyLevel: (level: PrivacyLevel) => void;
  
  // PII handling functions
  maskPII: (text: string) => string;
  checkForPII: (text: string) => boolean;
  analyzePII: (text: string) => { hasPII: boolean; detectedTypes: string[] };
  
  // User consent tracking
  hasConsent: boolean;
  setConsent: (consent: boolean) => void;
  
  // Settings for what kinds of data to protect
  protectedDataTypes: Record<string, boolean>;
  toggleDataTypeProtection: (dataType: string) => void;
}

// Define the data types we want to protect
export type ProtectedDataType = 'email' | 'phone' | 'ssn' | 'creditCard' | 'address' | 'name';

// Default privacy context
const defaultPrivacyContext: PrivacyContextType = {
  privacyLevel: 'medium',
  setPrivacyLevel: () => {},
  maskPII: (text) => text,
  checkForPII: () => false,
  analyzePII: () => ({ hasPII: false, detectedTypes: [] }),
  hasConsent: false,
  setConsent: () => {},
  protectedDataTypes: {
    email: true,
    phone: true,
    ssn: true,
    creditCard: true,
    address: true,
    name: true,
  },
  toggleDataTypeProtection: () => {},
};

// Create the context
const PrivacyContext = createContext<PrivacyContextType>(defaultPrivacyContext);

// Type for strategy options
type StrategyOptions = {
  strategy: 'redact' | 'hash' | 'tokenize' | 'partial';
  preserveFormat: boolean;
  keepLastDigits?: number;
};

// Privacy strategy mapping based on privacy level
const privacyStrategyMap: Record<PrivacyLevel, StrategyOptions> = {
  low: { strategy: 'partial', preserveFormat: true, keepLastDigits: 4 },
  medium: { strategy: 'partial', preserveFormat: true, keepLastDigits: 2 },
  high: { strategy: 'redact', preserveFormat: false },
  maximum: { strategy: 'hash', preserveFormat: false },
};

// Provider component
export const PrivacyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [privacyLevel, setPrivacyLevel] = useState<PrivacyLevel>('medium');
  const [hasConsent, setHasConsent] = useState<boolean>(false);
  const [protectedDataTypes, setProtectedDataTypes] = useState<Record<ProtectedDataType, boolean>>({
    email: true,
    phone: true,
    ssn: true,
    creditCard: true,
    address: true,
    name: true,
  });
  
  // Load privacy settings from local storage on component mount
  useEffect(() => {
    try {
      const storedLevel = localStorage.getItem('privacyLevel');
      if (storedLevel && isValidPrivacyLevel(storedLevel)) {
        setPrivacyLevel(storedLevel as PrivacyLevel);
      }
      
      const storedConsent = localStorage.getItem('privacyConsent');
      if (storedConsent) {
        setHasConsent(JSON.parse(storedConsent));
      }
      
      const storedDataTypes = localStorage.getItem('protectedDataTypes');
      if (storedDataTypes) {
        setProtectedDataTypes(JSON.parse(storedDataTypes));
      }
    } catch (error) {
      console.error('Error loading privacy settings:', error);
    }
  }, []);
  
  // Helper function to validate privacy level
  function isValidPrivacyLevel(level: string): level is PrivacyLevel {
    return ['low', 'medium', 'high', 'maximum'].includes(level);
  }
  
  // Save privacy settings to local storage when they change
  useEffect(() => {
    try {
      localStorage.setItem('privacyLevel', privacyLevel);
      localStorage.setItem('privacyConsent', JSON.stringify(hasConsent));
      localStorage.setItem('protectedDataTypes', JSON.stringify(protectedDataTypes));
    } catch (error) {
      console.error('Error saving privacy settings:', error);
    }
  }, [privacyLevel, hasConsent, protectedDataTypes]);
  
  // Function to mask PII based on current privacy level
  const maskPII = (text: string): string => {
    const strategyOptions = privacyStrategyMap[privacyLevel];
    return detectAndMaskPII(text, strategyOptions);
  };
  
  // Function to check if text contains PII
  const checkForPII = (text: string): boolean => {
    return containsPII(text);
  };
  
  // Function to analyze what types of PII are in text
  const analyzePII = (text: string) => {
    return analyzeText(text);
  };
  
  // Function to toggle protection for a specific data type
  const toggleDataTypeProtection = (dataType: string) => {
    if (isValidDataType(dataType)) {
      setProtectedDataTypes(prevTypes => ({
        ...prevTypes,
        [dataType]: !prevTypes[dataType],
      }));
    }
  };
  
  // Helper function to validate data type
  function isValidDataType(type: string): type is ProtectedDataType {
    return ['email', 'phone', 'ssn', 'creditCard', 'address', 'name'].includes(type);
  }
  
  const contextValue: PrivacyContextType = {
    privacyLevel,
    setPrivacyLevel,
    maskPII,
    checkForPII,
    analyzePII,
    hasConsent,
    setConsent: setHasConsent,
    protectedDataTypes,
    toggleDataTypeProtection,
  };
  
  return (
    <PrivacyContext.Provider value={contextValue}>
      {children}
    </PrivacyContext.Provider>
  );
};

// Custom hook to use the privacy context
export const usePrivacy = () => useContext(PrivacyContext);

export default PrivacyContext; 