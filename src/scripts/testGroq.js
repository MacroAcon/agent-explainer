const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');
const { Groq } = require('groq-sdk');

// Load environment variables from .env.local
const envLocalPath = path.resolve(process.cwd(), '.env.local');
if (fs.existsSync(envLocalPath)) {
  const envConfig = dotenv.parse(fs.readFileSync(envLocalPath));
  Object.entries(envConfig).forEach(([key, value]) => {
    process.env[key] = value;
  });
  console.log('Loaded environment variables from .env.local');
} else {
  console.log('No .env.local file found, falling back to .env');
  dotenv.config();
}

const GROQ_API_KEY = process.env.NEXT_PUBLIC_GROQ_API_KEY;

if (!GROQ_API_KEY) {
  console.error('NEXT_PUBLIC_GROQ_API_KEY environment variable is not set');
  process.exit(1);
}

console.log(`Using API key: ${GROQ_API_KEY.substring(0, 5)}...${GROQ_API_KEY.substring(GROQ_API_KEY.length - 5)}`);

const MODEL_NAME = 'llama-3.3-70b-versatile';

async function testGroq() {
  console.log('Testing Groq with Llama model...');
  
  try {
    const client = new Groq({
      apiKey: GROQ_API_KEY,
    });

    const completion = await client.chat.completions.create({
      model: MODEL_NAME,
      messages: [
        {
          role: "system",
          content: "You are an expert marketing copywriter specializing in local business campaigns."
        },
        {
          role: "user",
          content: "Create a marketing headline and brief description for a local bakery's summer special event."
        }
      ],
      temperature: 0.7,
      max_tokens: 500
    });

    console.log('Success! Model response:');
    console.log('-------------------');
    console.log(completion.choices[0]?.message?.content);
    console.log('-------------------');
    console.log('Model: ', MODEL_NAME);
    console.log('API connected successfully!');
  } catch (error) {
    console.error('Error testing Groq:');
    console.error(error);
  }
}

testGroq(); 