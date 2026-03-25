import { NextRequest, NextResponse } from 'next/server';
import dbConnect from '@/lib/mongodb';
import Article from '@/models/Article';

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const pathParts = url.pathname.split('/');
  const slug = pathParts[pathParts.length - 1];

  try {
    await dbConnect();

    const article = (await Article.findOne({ slug }).lean()) as any;

    if (!article) {
      return NextResponse.json(
        { error: 'Article not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      ...article,
      _id: String(article._id),
      createdAt: article.createdAt ? new Date(article.createdAt).toISOString() : new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error fetching article:', error);
    return NextResponse.json(
      { error: 'Failed to fetch article' },
      { status: 500 }
    );
  }
}