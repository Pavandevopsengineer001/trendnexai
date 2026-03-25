'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';

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
        <h2 className="text-2xl font-bold mb-6">Related Articles</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-gray-100 dark:bg-slate-800 h-64 rounded-lg" />
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
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Related Articles</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {related.map(article => (
          <Link
            key={article.slug}
            href={`/article/${article.slug}`}\n            className="group bg-white dark:bg-slate-800 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow\"\n          >\n            <div className=\"bg-gradient-to-br from-blue-500 to-purple-600 h-40 group-hover:scale-105 transition-transform\" />\n            <div className=\"p-4\">\n              <Badge variant=\"secondary\" className=\"mb-2\">\n                {article.category}\n              </Badge>\n              <h3 className=\"font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition\">\n                {article.title}\n              </h3>\n              <p className=\"text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mt-2\">\n                {article.summary}\n              </p>\n              <div className=\"flex gap-1 mt-3 flex-wrap\">\n                {article.tags?.slice(0, 2).map((tag: string) => (\n                  <Badge key={tag} variant=\"outline\" className=\"text-xs\">\n                    {tag}\n                  </Badge>\n                ))}\n              </div>\n              <div className=\"text-xs text-gray-500 dark:text-gray-400 mt-3\">\n                {new Date(article.createdAt).toLocaleDateString()}\n              </div>\n            </div>\n          </Link>\n        ))}\n      </div>\n    </div>\n  );\n}
