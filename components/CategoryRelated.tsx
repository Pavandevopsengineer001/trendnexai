'use client';

import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { getCategoryById, getCategoryBadgeClass } from '@/lib/categories';

interface RelatedArticlesProps {
  articles: any[];
  currentArticleId?: string;
  limit?: number;
  title?: string;
}

export default function RelatedArticles({
  articles,
  currentArticleId,
  limit = 4,
  title = 'Related Articles',
}: RelatedArticlesProps) {
  const filtered = articles
    .filter(a => a._id !== currentArticleId)
    .slice(0, limit);

  if (filtered.length === 0) return null;

  return (
    <section className="section-spacing-sm">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Title */}
        <h2 className="text-2xl md:text-3xl font-bold mb-10">{title}</h2>

        {/* Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filtered.map((article) => {
            const category = getCategoryById(article.category);
            const badgeClass = getCategoryBadgeClass(article.category);

            return (
              <Link
                key={article._id}
                href={`/article/${article.slug}`}
                className="group"
              >
                <article className="card-hover overflow-hidden h-full flex flex-col">
                  {/* Image */}
                  {article.image_url && (
                    <div className="relative h-40 overflow-hidden bg-muted">
                      <img
                        src={article.image_url}
                        alt={article.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                    </div>
                  )}

                  {/* Content */}
                  <div className="flex-1 p-4 flex flex-col">
                    {/* Category Badge */}
                    {category && (
                      <span className={`badge ${badgeClass} w-max mb-3 text-xs`}>
                        {category.icon} {category.label}
                      </span>
                    )}

                    {/* Title */}
                    <h3 className="font-bold text-base group-hover:text-primary transition-colors duration-200 line-clamp-2 mb-2 flex-grow">
                      {article.title}
                    </h3>

                    {/* Summary */}
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                      {article.summary}
                    </p>

                    {/* CTA */}
                    <div className="flex items-center gap-1 text-primary text-sm font-semibold">
                      Read More
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
                    </div>
                  </div>
                </article>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
