import axios from 'axios';

const GNEWS_API_KEY = process.env.GNEWS_API_KEY;
const GNEWS_BASE_URL = 'https://gnews.io/api/v4/top-headlines';

export interface RawNewsArticle {
  title: string;
  description: string;
  content: string;
  url: string;
  image: string;
  publishedAt: string;
  source: {
    name: string;
    url: string;
  };
}

export interface GNewsResponse {
  totalArticles: number;
  articles: RawNewsArticle[];
}

export async function fetchLatestNews(limit: number = 10): Promise<RawNewsArticle[]> {
  if (!GNEWS_API_KEY) {
    throw new Error('GNEWS_API_KEY is not defined');
  }

  try {
    const response = await axios.get<GNewsResponse>(GNEWS_BASE_URL, {
      params: {
        token: GNEWS_API_KEY,
        lang: 'en',
        max: limit,
        country: 'in', // Focus on India
      },
    });

    return response.data.articles;
  } catch (error) {
    console.error('Error fetching news:', error);
    throw new Error('Failed to fetch news from GNews API');
  }
}