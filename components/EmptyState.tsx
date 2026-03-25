import Link from 'next/link';
import { Search } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  icon?: string;
}

export default function EmptyState({
  title = 'No articles found',
  description = 'Try adjusting your filters or search query to find what you are looking for.',
  actionLabel = 'Reset filters',
  actionHref = '/',
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-4 animate-fade-in">
      <div className="text-center max-w-md">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          {icon && typeof icon === 'string' ? (
            <div className="text-6xl mb-4">{icon}</div>
          ) : (
            <div className="p-4 bg-primary/10 rounded-full border border-primary/20">
              <Search className="w-8 h-8 text-primary" />
            </div>
          )}
        </div>

        {/* Title */}
        <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-3">{title}</h3>

        {/* Description */}
        <p className="text-muted-foreground text-base mb-8 leading-relaxed max-w-sm">
          {description}
        </p>

        {/* Action Button */}
        {actionHref && (
          <Link
            href={actionHref}
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 hover:shadow-lg transition-all duration-200"
          >
            {actionLabel}
          </Link>
        )}
      </div>
    </div>
  );
}
