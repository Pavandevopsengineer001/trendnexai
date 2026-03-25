import { Category } from '@/lib/categories';
import { Filter, ArrowRight } from 'lucide-react';

interface CategoryPageHeaderProps {
  category: Category;
  articleCount?: number;
  currentFilter?: string;
  onFilterChange?: (filter: string) => void;
}

export default function CategoryPageHeader({
  category,
  articleCount = 0,
  currentFilter = 'latest',
  onFilterChange,
}: CategoryPageHeaderProps) {
  const filters = [
    { id: 'latest', label: 'Latest' },
    { id: 'trending', label: 'Trending' },
    { id: 'oldest', label: 'Oldest' },
  ];

  return (
    <section className="bg-gradient-to-r from-primary/5 to-secondary/5 border-b border-border py-12 md:py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-10 animate-fade-in">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-5xl md:text-6xl">{category.icon}</span>
            <div>
              <h1 className="text-4xl md:text-5xl font-bold">{category.label}</h1>
              <p className="text-lg text-muted-foreground mt-2">
                {category.description}
              </p>
            </div>
          </div>

          {/* Stats */}
          {articleCount > 0 && (
            <p className="text-sm text-muted-foreground">
              <span className="font-semibold text-foreground">{articleCount}</span> articles available
            </p>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Filter Buttons */}
          <div className="flex items-center gap-3">
            <Filter className="w-4 h-4 text-muted-foreground flex-shrink-0" />
            <div className="flex flex-wrap gap-2">
              {filters.map((filter) => (
                <button
                  key={filter.id}
                  onClick={() => onFilterChange?.(filter.id)}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
                    currentFilter === filter.id
                      ? `bg-primary text-primary-foreground shadow-md`
                      : `bg-background border border-border text-foreground hover:border-primary/50`
                  }`}
                  aria-pressed={currentFilter === filter.id}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>

          {/* Sort/View Options */}
          <div className="hidden sm:flex items-center gap-2">
            <button
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200 text-muted-foreground"
              aria-label="List view"
              title="List view"
            >
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" />
              </svg>
            </button>
            <button
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200 text-muted-foreground"
              aria-label="Grid view"
              title="Grid view"
            >
              <svg
                className="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M3 4a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1v-3zm6-6a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-3zm6-6a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-3z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
