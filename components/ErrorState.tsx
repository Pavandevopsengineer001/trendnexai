import Link from 'next/link';
import { AlertCircle, RotateCcw } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  showHomeLink?: boolean;
}

export default function ErrorState({
  message = 'Something went wrong while fetching articles. Please try again.',
  onRetry,
  showHomeLink = true,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-4 animate-fade-in">
      <div className="text-center max-w-md">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <div className="p-4 bg-destructive/10 rounded-full border border-destructive/20">
            <AlertCircle className="w-8 h-8 text-destructive" />
          </div>
        </div>

        {/* Title */}
        <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-3">
          Something went wrong
        </h3>

        {/* Message */}
        <p className="text-muted-foreground text-base mb-8 leading-relaxed max-w-sm">
          {message}
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 hover:shadow-lg transition-all duration-200"
            >
              <RotateCcw className="w-4 h-4" />
              Try again
            </button>
          )}

          {showHomeLink && (
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-muted text-foreground rounded-lg font-semibold hover:bg-muted/80 transition-all duration-200"
            >
              Go Home
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
