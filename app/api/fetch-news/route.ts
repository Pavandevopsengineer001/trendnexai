import { NextRequest, NextResponse } from 'next/server';
import { fetchLatestNews } from '@/lib/news';
import dbConnect from '@/lib/mongodb';
import Article from '@/models/Article';
import { processNewsWithAI } from '@/lib/openai';

export async function GET(request: NextRequest) {
  try {
    await dbConnect();

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '5');

    const rawNews = await fetchLatestNews(limit);

    const processedArticles = [];

    for (const news of rawNews) {
      try {
        // Check if article already exists
        const existingArticle = await Article.findOne({ title: news.title });
        if (existingArticle) {
          processedArticles.push(existingArticle);
          continue;
        }

        // Process with AI
        const processedArticle = await processNewsWithAI({
          title: news.title,
          description: news.description,
          content: news.content,
          category: 'General', // You can enhance this with category detection
        });

        const companyName = news.source?.name || processedArticle.company || 'TrendNexAI';

        // Save to database
        const article = new Article({
          ...processedArticle,
          company: companyName,
          createdAt: new Date(news.publishedAt),
        });

        await article.save();
        processedArticles.push(article);
      } catch (error) {
        console.error('Error processing article:', error);
        // Continue with next article
      }
    }

    return NextResponse.json({
      success: true,
      articles: processedArticles,
      count: processedArticles.length,
    });
  } catch (error) {
    console.error('Error in fetch-news:', error);
    return NextResponse.json(
      { error: 'Failed to fetch and process news' },
      { status: 500 }
    );
  }
}