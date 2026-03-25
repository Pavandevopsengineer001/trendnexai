import { NextRequest, NextResponse } from 'next/server';
import { processNewsWithAI } from '@/lib/openai';
import dbConnect from '@/lib/mongodb';
import Article from '@/models/Article';

export async function POST(request: NextRequest) {
  try {
    await dbConnect();

    const body = await request.json();
    const { title, description, content, category, company } = body;

    if (!title || !description || !content) {
      return NextResponse.json(
        { error: 'Missing required fields: title, description, content' },
        { status: 400 }
      );
    }

    // Process with AI
    const processedArticle = await processNewsWithAI({
      title,
      description,
      content,
      category: category || 'General',
    });

    processedArticle.company = company || processedArticle.company || 'TrendNexAI';

    // Check if article already exists
    const existingArticle = await Article.findOne({ slug: processedArticle.slug });
    if (existingArticle) {
      return NextResponse.json(
        { error: 'Article with this slug already exists' },
        { status: 409 }
      );
    }

    // Save to database
    const article = new Article(processedArticle);
    await article.save();

    return NextResponse.json({
      success: true,
      article,
    });
  } catch (error) {
    console.error('Error in generate-article:', error);
    return NextResponse.json(
      { error: 'Failed to generate article' },
      { status: 500 }
    );
  }
}