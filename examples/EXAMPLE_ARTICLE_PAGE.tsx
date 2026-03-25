/**
 * EXAMPLE: Article Detail Page Implementation
 * File: app/article/[slug]/page.tsx
 */

'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ArticleContent from '@/components/ArticleContent';
import CategoryRelated from '@/components/CategoryRelated';
import { getCategoryById, getCategoryBadgeClass } from '@/lib/categories';
import { DOMPurify } from 'isomorphic-dompurify'; // Use for sanitizing HTML

interface ArticleType {
  _id: string;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category: string;
  author?: string;
  image_url?: string;
  source_url?: string;
  createdAt: string;
  tags: string[];
}

export default function ArticlePage() {
  const params = useParams();
  const slug = params.slug as string;

  const [article, setArticle] = useState<ArticleType | null>(null);
  const [relatedArticles, setRelatedArticles] = useState<ArticleType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadArticle();
  }, [slug]);

  const loadArticle = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch article - adjust API endpoint as needed
      const response = await fetch(`/api/article/${slug}`);
      if (!response.ok) throw new Error('Article not found');
      const data = await response.json();
      
      setArticle(data);

      // Load related articles
      if (data.category) {
        const related = await fetch(
          `/api/articles?category=${data.category}&limit=6`
        );
        const relatedData = await related.json();
        setRelatedArticles(relatedData.items || []);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to load article');
    } finally {
      setLoading(false);
    }
  };

  const category = article ? getCategoryById(article.category) : null;
  const badgeClass = article ? getCategoryBadgeClass(article.category) : '';

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-muted border-t-primary rounded-full animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading article...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <Header />
        <main className="flex-1">
          <section className="section-spacing">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h1 className="text-3xl font-bold mb-4">Article Not Found</h1>
              <p className="text-muted-foreground mb-8">
                {error || 'The article you are looking for could not be found.'}
              </p>
              <Link href="/" className="btn-primary px-6 py-3 rounded-lg inline-block">
                Back to Home
              </Link>
            </div>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Article Header */}
        <article className="section-spacing">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 animate-fade-in">
            {/* Breadcrumb & Category */}
            <div className="mb-6 flex items-center gap-3">
              {category && (
                <span className={`badge ${badgeClass} text-sm`}>
                  {category.icon} {category.label}
                </span>
              )}
              <span className="text-sm text-muted-foreground">
                {formatDate(article.createdAt)}
              </span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 leading-tight">
              {article.title}
            </h1>

            {/* Summary/Meta */}
            <div className="flex items-center justify-between gap-4 mb-8 pb-8 border-b border-border flex-wrap">
              <p className="text-lg text-muted-foreground max-w-2xl">
                {article.summary}
              </p>
              {article.source_url && (
                <a
                  href={article.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-outline px-4 py-2 text-sm rounded-lg whitespace-nowrap"
                >
                  View Source →
                </a>
              )}
            </div>

            {/* Featured Image */}
            {article.image_url && (
              <div className="mb-12 rounded-xl overflow-hidden shadow-lg">
                <img
                  src={article.image_url}
                  alt={article.title}
                  className="w-full h-96 object-cover"
                />
              </div>
            )}

            {/* Article Content */}
            <div className="prose prose-invert max-w-none mb-12">
              <ArticleContent content={article.content || article.summary} />
            </div>

            {/* Tags */}
            {article.tags && article.tags.length > 0 && (
              <div className="mb-12 pb-12 border-b border-border">
                <h3 className="text-sm font-semibold mb-3 uppercase tracking-wide text-muted-foreground">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {article.tags.map(tag => (
                    <Link
                      key={tag}
                      href={`/?search=${encodeURIComponent(tag)}`}
                      className="px-4 py-2 bg-muted hover:bg-primary hover:text-primary-foreground rounded-lg transition-colors duration-200 text-sm font-medium"
                    >
                      #{tag}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Share Options */}
            <div className="mb-12 pb-12 border-b border-border">
              <h3 className="text-sm font-semibold mb-4 uppercase tracking-wide text-muted-foreground">
                Share Article
              </h3>
              <div className="flex gap-3 flex-wrap">
                <a
                  href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(article.title)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-muted hover:bg-blue-500/20 hover:text-blue-500 rounded-lg transition-colors duration-200 text-sm font-medium"
                >
                  Share on Twitter
                </a>
                <a
                  href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-muted hover:bg-blue-600/20 hover:text-blue-600 rounded-lg transition-colors duration-200 text-sm font-medium"
                >
                  Share on LinkedIn
                </a>
                <button
                  onClick={() => navigator.clipboard.writeText(window.location.href)}
                  className="px-4 py-2 bg-muted hover:bg-primary/20 hover:text-primary rounded-lg transition-colors duration-200 text-sm font-medium"
                >
                  Copy Link
                </button>
              </div>
            </div>

            {/* Author Info (Optional) */}
            {article.author && (
              <div className="mb-12 p-6 bg-muted rounded-lg border border-border">
                <p className="text-sm text-muted-foreground mb-2">Written by</p>
                <h4 className="text-lg font-semibold">{article.author}</h4>
              </div>
            )}
          </div>
        </article>

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <CategoryRelated
            articles={relatedArticles}
            currentArticleId={article._id}
            title={`More ${category?.label || 'Articles'}`}
          />
        )}

        {/* Call to Action */}
        <section className="section-spacing bg-gradient-to-r from-primary/10 to-secondary/10 border-y border-border">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-4">Stay Updated</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Never miss important news in {category?.label.toLowerCase()}
            </p>
            <button className="btn-primary px-8 py-3 rounded-lg">
              Subscribe to Newsletter
            </button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
