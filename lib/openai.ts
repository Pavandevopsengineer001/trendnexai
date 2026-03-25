import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface ProcessedArticle {
  title: string;
  slug: string;
  category: string;
  company?: string;
  summary: string;
  content: {
    en: string;
    te: string;
    ta: string;
    kn: string;
    ml: string;
  };
  tags: string[];
  seo_title: string;
  seo_description: string;
}

export async function processNewsWithAI(rawNews: {
  title: string;
  description: string;
  content: string;
  category?: string;
}): Promise<ProcessedArticle> {
  const prompt = `
You are an AI news processor. Take the following raw news data and convert it into a structured JSON format suitable for a multilingual news website.

Raw News:
Title: ${rawNews.title}
Description: ${rawNews.description}
Content: ${rawNews.content}
Category: ${rawNews.category || 'General'}

Requirements:
- Create a compelling title
- Generate a unique slug (URL-friendly, lowercase, hyphens)
- Determine appropriate category
- Determine company/source name (e.g., Times of India, Economic Times, etc.)
- Write a concise summary (2-3 sentences)
- Translate the full content into English, Telugu (te), Tamil (ta), Kannada (kn), and Malayalam (ml)
- Generate relevant tags (3-5 keywords)
- Create SEO title and description

Return ONLY valid JSON with this exact structure:
{
  "title": "string",
  "slug": "string",
  "category": "string",
  "company": "string",
  "summary": "string",
  "content": {
    "en": "string",
    "te": "string",
    "ta": "string",
    "kn": "string",
    "ml": "string"
  },
  "tags": ["string"],
  "seo_title": "string",
  "seo_description": "string"
}
`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0.7,
  });

  const result = response.choices[0]?.message?.content;
  if (!result) {
    throw new Error('Failed to process news with AI');
  }

  try {
    return JSON.parse(result);
  } catch (error) {
    throw new Error('Invalid JSON response from AI');
  }
}