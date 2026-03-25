import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Badge } from '@/components/ui/badge';
import ArticleContent from '@/components/ArticleContent';
import RelatedArticles from '@/components/RelatedArticles';
import AdUnit from '@/components/AdUnit';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

// Revalidate every hour (ISR)
export const revalidate = 3600;

async function getArticle(slug: string) {
  try {
    const res = await fetch(`${API_BASE}/api/article/${encodeURIComponent(slug)}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.error('Failed to fetch article:', error);
    return null;
  }
}

export async function generateStaticParams() {
  try {
    const res = await fetch(`${API_BASE}/api/articles?limit=1000&status=published`, {
      revalidate: 86400,
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.items || []).map((article: any) => ({ slug: article.slug }));
  } catch (error) {
    console.error('Failed to generate static params:', error);
    return [];
  }
}

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const article = await getArticle(params.slug);

  if (!article) {
    return {
      title: 'Article Not Found | TrendNexAI',
      description: 'The article you are looking for does not exist.',
    };
  }

  const url = `${SITE_URL}/article/${article.slug}`;
  const description = article.seo_description || article.summary;

  return {
    title: article.seo_title || article.title,
    description: description,
    keywords: (article.tags || []).join(', '),
    authors: [{ name: article.author || 'TrendNexAI' }],
    creator: 'TrendNexAI',
    publisher: 'TrendNexAI',
    openGraph: {
      title: article.seo_title || article.title,
      description: description,
      type: 'article',
      publishedTime: article.published_at || article.createdAt,
      modifiedTime: article.updated_at,
      authors: [article.author || 'TrendNexAI'],
      tags: article.tags || [],
      images: article.og_image
        ? [{ url: article.og_image, width: 1200, height: 630 }]
        : [{ url: `${SITE_URL}/og-default.png`, width: 1200, height: 630 }],
      url: url,
    },
    twitter: {
      card: 'summary_large_image',
      title: article.seo_title || article.title,
      description: description,
      creator: '@TrendNexAI',
      images: article.og_image || `${SITE_URL}/og-default.png`,
    },
    alternates: {
      canonical: url,
    },
  };
}

export default async function ArticlePage({ params }: any) {
  const article = await getArticle(params.slug);

  if (!article) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <ArticleContent article={article} />
      </main>
      <Footer />
    </div>
  );
}
