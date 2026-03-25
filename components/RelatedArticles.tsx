'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getCategoryById, getCategoryBadgeClass } from '@/lib/categories';
import { CalendarIcon } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';

interface RelatedArticlesProps {
  tags: string[];
  currentSlug: string;
}

export default function RelatedArticles({ tags, currentSlug }: RelatedArticlesProps) {
  const [related, setRelated] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRelated = async () => {
      try {
        // Search for articles with matching tags
        const query = tags.slice(0, 3).map(tag => `search=${encodeURIComponent(tag)}`).join('&');
        const res = await fetch(`${API_BASE}/api/articles?${query}&limit=6`);
        
        if (res.ok) {
          const data = await res.json();
          // Filter out current article and limit to 3
          const filtered = (data.items || [])
            .filter((article: any) => article.slug !== currentSlug)
            .slice(0, 3);
          setRelated(filtered);
        }
      } catch (error) {
        console.error('Failed to fetch related articles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRelated();
  }, [tags, currentSlug]);

  if (loading) {
    return (
      <div className="animate-pulse">
        <h2 className="text-2xl font-bold mb-6 text-foreground">Related Articles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-muted dark:bg-card h-64 rounded-lg border border-border" />
          ))}
        </div>
      </div>
    );
  }

  if (related.length === 0) {
    return null;
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-foreground mb-6">Related Articles</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {related.map(article => {
          const category = getCategoryById(article.category);
          const badgeClass = getCategoryBadgeClass(article.category);
          
          return (
            <Link
              key={article.slug}
              href={`/article/${article.slug}`}
              className="group card-premium h-full flex flex-col overflow-hidden transition-all duration-300"
            >
              {/* Image */}
              <div className="relative h-40 overflow-hidden bg-muted flex-shrink-0">
                {article.image_url ? (
                  <img
                    src={article.image_url}
                    alt={article.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center" />
                )}
              </div>

              {/* Content */}
              <div className="p-4 flex-1 flex flex-col">
                {/* Category Badge */}
                {category && (
                  <span className={`badge ${badgeClass} text-xs font-semibold mb-2 w-fit`}>
                    {category.icon} {category.label}
                  </span>
                )}

                {/* Title */}
                <h3 className="font-bold text-foreground line-clamp-2 group-hover:text-primary transition-colors duration-200 mb-2 flex-grow">
                  {article.title}
                </h3>

                {/* Summary */}
                <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                  {article.summary}
                </p>

                {/* Tags */}
                {article.tags && article.tags.length > 0 && (
                  <div className="flex gap-1 mb-3 flex-wrap">
                    {article.tags.slice(0, 2).map((tag: string) => (
                      <span key={tag} className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded-md">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Date */}
                <div className="flex items-center gap-1 text-xs text-muted-foreground mt-auto pt-3 border-t border-border">
                  <CalendarIcon className="w-3 h-3" />
                  {new Date(article.createdAt).toLocaleDateString()}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
