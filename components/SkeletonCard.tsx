export default function SkeletonCard() {
  return (
    <div className="card-premium h-full flex flex-col overflow-hidden">
      {/* Image Skeleton */}
      <div className="h-56 bg-gradient-to-r from-muted via-muted/50 to-muted rounded-t-lg animate-pulse-soft" />

      {/* Content Skeleton */}
      <div className="flex-1 p-5 flex flex-col gap-4">
        {/* Category Badge */}
        <div className="h-6 w-24 bg-muted rounded-full animate-pulse" />

        {/* Title Lines */}
        <div className="space-y-3">
          <div className="h-5 bg-muted rounded animate-pulse" />
          <div className="h-5 w-5/6 bg-muted rounded animate-pulse" />
        </div>

        {/* Summary Lines */}
        <div className="space-y-2 flex-grow">
          <div className="h-4 bg-muted rounded animate-pulse" />
          <div className="h-4 bg-muted rounded animate-pulse" />
        </div>

        {/* Tags */}
        <div className="flex gap-2 pt-2">
          <div className="h-5 w-12 bg-muted rounded animate-pulse" />
          <div className="h-5 w-12 bg-muted rounded animate-pulse" />
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center pt-3 border-t border-border/50">
          <div className="h-4 w-20 bg-muted rounded animate-pulse" />
          <div className="h-4 w-4 bg-muted rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
