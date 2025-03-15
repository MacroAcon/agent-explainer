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