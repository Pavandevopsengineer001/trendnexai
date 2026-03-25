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

export default async function ArticlePage({ params }: any) {\n  const article = await getArticle(params.slug);\n\n  if (!article) {\n    notFound();\n  }\n\n  const url = `${SITE_URL}/article/${article.slug}`;\n\n  return (\n    <>\n      {/* JSON-LD Structured Data */}\n      <script\n        type=\"application/ld+json\"\n        dangerouslySetInnerHTML={{\n          __html: JSON.stringify({\n            '@context': 'https://schema.org',\n            '@type': 'NewsArticle',\n            headline: article.seo_title || article.title,\n            description: article.seo_description || article.summary,\n            image: article.og_image || `${SITE_URL}/og-default.png`,\n            datePublished: article.published_at || article.createdAt,\n            dateModified: article.updated_at || article.createdAt,\n            author: {\n              '@type': 'Person',\n              name: article.author || 'TrendNexAI',\n            },\n            publisher: {\n              '@type': 'Organization',\n              name: 'TrendNexAI',\n              logo: {\n                '@type': 'ImageObject',\n                url: `${SITE_URL}/logo.png`,\n              },\n            },\n            mainEntityOfPage: {\n              '@type': 'WebPage',\n              '@id': url,\n            },\n          }),\n        }}\n      />\n\n      <div className=\"min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100\">\n        <Header />\n\n        <main className=\"max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">\n          {/* Breadcrumb Navigation */}\n          <nav className=\"flex gap-2 text-sm text-gray-600 dark:text-gray-400 mb-6\">\n            <Link href=\"\" className=\"hover:text-gray-900\">Home</Link>\n            <span>/</span>\n            <Link href={`/category/${article.category}`} className=\"hover:text-gray-900 capitalize\">\n              {article.category}\n            </Link>\n            <span>/</span>\n            <span className=\"text-gray-900 dark:text-white truncate\">{article.title}</span>\n          </nav>\n\n          <header className=\"mb-8 glass-glow p-6 animate-fade-up\">\n            <div className=\"flex flex-wrap items-center gap-2 mb-4\">\n              <Badge variant=\"secondary\">{article.category}</Badge>\n              {article.company && (\n                <span className=\"text-sm text-blue-600 dark:text-blue-300 font-medium\">\n                  {article.company}\n                </span>\n              )}\n              <span className=\"text-sm text-gray-500 dark:text-gray-300\">\n                {new Date(article.createdAt || article.published_at).toLocaleDateString('en-US', {\n                  year: 'numeric',\n                  month: 'long',\n                  day: 'numeric',\n                })}\n              </span>\n              {article.views && (\n                <>\n                  <span>•</span>\n                  <span className=\"text-sm text-gray-500 dark:text-gray-300\">\n                    {article.views} views\n                  </span>\n                </>\n              )}\n            </div>\n\n            <h1 className=\"text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4\">\n              {article.title}\n            </h1>\n\n            <p className=\"text-xl text-gray-600 dark:text-gray-300 mb-6\">\n              {article.summary}\n            </p>\n\n            <div className=\"flex flex-wrap gap-2 mb-6\">\n              {article.tags?.map((tag: string) => (\n                <Badge key={tag} variant=\"outline\">\n                  #{tag}\n                </Badge>\n              ))}\n            </div>\n          </header>\n\n          {/* Top Ad Unit */}\n          <div className=\"mb-8\">\n            <AdUnit slot=\"article-top\" />\n          </div>\n\n          <ArticleContent article={article} />\n\n          {/* Mid Article Ad Unit */}\n          <div className=\"my-8\">\n            <AdUnit slot=\"article-mid\" />\n          </div>\n\n          {/* Social Sharing */}\n          <div className=\"my-8 py-6 border-t border-b border-gray-200 dark:border-slate-700\">\n            <div className=\"flex items-center gap-4\">\n              <span className=\"text-gray-600 dark:text-gray-400 font-medium\">Share:</span>\n              <a\n                href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title)}&url=${encodeURIComponent(url)}`}\n                className=\"text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300\"\n                target=\"_blank\"\n                rel=\"noopener noreferrer\"\n              >\n                Twitter\n              </a>\n              <a\n                href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`}\n                className=\"text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300\"\n                target=\"_blank\"\n                rel=\"noopener noreferrer\"\n              >\n                Facebook\n              </a>\n              <a\n                href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}\n                className=\"text-blue-700 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300\"\n                target=\"_blank\"\n                rel=\"noopener noreferrer\"\n              >\n                LinkedIn\n              </a>\n            </div>\n          </div>\n\n          {/* Related Articles Section */}\n          {article.tags && article.tags.length > 0 && (\n            <section className=\"border-t border-gray-200 dark:border-slate-700 pt-8 mt-8\">\n              <RelatedArticles tags={article.tags} currentSlug={article.slug} />\n            </section>\n          )}\n\n          {/* Bottom Ad Unit */}\n          <div className=\"mt-8 mb-8\">\n            <AdUnit slot=\"article-bottom\" />\n          </div>\n        </main>\n\n        <Footer />\n      </div>\n    </>\n  );\n}
