import Link from 'next/link';
import { Calendar, MessageSquare, ExternalLink, ArrowRight } from 'lucide-react';
import { getCategoryById, getCategoryBadgeClass } from '@/lib/categories';

interface ArticleCardProps {
  article: {
    _id: string;
    title: string;
    slug: string;
    summary: string;
    category: string;
    company?: string;
    source_url?: string;
    image_url?: string;
    tags: string[];
    createdAt: string;
  };
}

export default function ArticleCard({ article }: ArticleCardProps) {
  const category = getCategoryById(article.category);
  const badgeClass = getCategoryBadgeClass(article.category);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <article className="card-premium group h-full flex flex-col overflow-hidden transition-all duration-300">
      {/* Image Container with Overlay */}
      <div className="relative h-56 overflow-hidden bg-muted flex-shrink-0">
        {article.image_url ? (
          <>
            <img
              src={article.image_url}
              alt={article.title}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              loading="lazy"
            />
            {/* Overlay Gradient */}
            <div className="absolute inset-0 bg-gradient-to-t from-foreground/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </>
        ) : (
          <div className={`w-full h-full ${category?.bgColor} flex items-center justify-center`}>
            <div className="text-center">
              <MessageSquare className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm text-muted-foreground">No image</p>
            </div>
          </div>
        )}

        {/* Category Badge - Positioned on image */}
        {category && (
          <div className="absolute top-3 left-3">
            <span className={`badge ${badgeClass} text-xs font-semibold`}>
              {category.icon} {category.label}
            </span>
          </div>
        )}
      </div>

      {/* Content Container */}
      <div className="flex-1 p-5 flex flex-col">
        {/* Date */}
        <div className="flex items-center gap-2 mb-3">
          <Calendar className="w-4 h-4 text-muted-foreground flex-shrink-0" />
          <span className="text-xs text-muted-foreground font-medium">
            {formatDate(article.createdAt)}
          </span>
        </div>

        {/* Title */}
        <Link href={`/article/${article.slug}`}>
          <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors duration-200 line-clamp-3 mb-3 leading-snug">
            {article.title}
          </h3>
        </Link>

        {/* Summary */}
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-grow leading-relaxed">
          {article.summary}
        </p>

        {/* Tags - Optional */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4 pb-4 border-b border-border/50">
            {article.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded-md">
                #{tag}
              </span>
            ))}
            {article.tags.length > 2 && (
              <span className="text-xs px-2 py-1 bg-muted text-muted-foreground rounded-md">
                +{article.tags.length - 2}
              </span>
            )}
          </div>
        )}

        {/* Footer with CTA */}
        <div className="flex items-center justify-between gap-2 mt-auto">
          <Link
            href={`/article/${article.slug}`}
            className="inline-flex items-center gap-1 text-primary hover:text-primary/80 font-semibold text-sm group/link transition-colors duration-200"
          >
            Read More
            <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform duration-200" />
          </Link>

          {article.source_url && (
            <a
              href={article.source_url}
              target="_blank"
              rel="noreferrer noopener"
              className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-lg transition-all duration-200 flex-shrink-0"
              title="Open original source"
              aria-label="View original source"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </article>
  );
}