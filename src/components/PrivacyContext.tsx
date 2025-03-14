import React, { createContext, useContext, useState, ReactNode } from 'react';

interface PrivacySettings {
  maskPII: boolean;
  anonymizeData: boolean;
  strictMode: boolean;
}

interface PrivacyContextType {
  settings: PrivacySettings;
  updateSettings: (newSettings: Partial<PrivacySettings>) => void;
}

const defaultSettings: PrivacySettings = {
  maskPII: true,
  anonymizeData: true,
  strictMode: false,
};

const PrivacyContext = createContext<PrivacyContextType | undefined>(undefined);

export function PrivacyProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<PrivacySettings>(defaultSettings);

  const updateSettings = (newSettings: Partial<PrivacySettings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  };

  return (
    <PrivacyContext.Provider value={{ settings, updateSettings }}>
      {children}
    </PrivacyContext.Provider>
  );
}

export function usePrivacy() {
  const context = useContext(PrivacyContext);
  if (context === undefined) {
    throw new Error('usePrivacy must be used within a PrivacyProvider');
  }
  return context;
} 