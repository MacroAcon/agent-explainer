// This file is no longer needed as we're using the types from groq-sdk
// The file is kept for backward compatibility but its content is not used
declare module 'groq' {
  interface GroqConfig {
    apiKey: string;
  }

  interface GroqClient {
    chat: {
      completions: {
        create: (params: {
          messages: Array<{
            role: string;
            content: string;
          }>;
          model: string;
          temperature?: number;
          max_tokens?: number;
        }) => Promise<{
          choices: Array<{
            message: {
              content: string;
            };
          }>;
        }>;
      };
    };
  }

  export default class Groq {
    constructor(config: GroqConfig);
    chat: GroqClient['chat'];
  }
} 