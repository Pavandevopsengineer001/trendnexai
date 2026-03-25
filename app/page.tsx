"use client";

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ArticleCard from '@/components/ArticleCard';
import SkeletonCard from '@/components/SkeletonCard';
import EmptyState from '@/components/EmptyState';
import ErrorState from '@/components/ErrorState';
import { fetchArticles, fetchCategories } from '@/lib/api';
import { Search, Filter, ArrowDown } from 'lucide-react';

const FEATURED_CATEGORIES = [
  { id: 'all', label: 'All Articles', icon: '📰' },
  { id: 'technology', label: 'Technology', icon: '💻' },
  { id: 'business', label: 'Business', icon: '💼' },
  { id: 'sports', label: 'Sports', icon: '⚽' },
  { id: 'health', label: 'Health', icon: '🏥' },
];

export default function Home() {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Load categories
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await fetchCategories();
        setCategories(cats);
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    };
    loadCategories();
  }, []);

  // Load articles
  useEffect(() => {
    loadArticles(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadArticles = async (reset = false, categoryOverride?: string) => {
    try {
      setError('');
      const isResetting = reset || articles.length === 0;
      const loadingState = isResetting ? setLoading : setIsLoadingMore;
      loadingState(true);

      const pageToLoad = reset ? 0 : page;
      const cat = categoryOverride !== undefined ? categoryOverride : selectedCategory;
      const res = await fetchArticles({
        category: cat,
        search: searchQuery,
        sort: sortBy,
        page: pageToLoad,
        pageSize: 12,
      });

      const data = res.items || [];
      setArticles((prev) => (reset ? data : [...prev, ...data]));
      setHasMore(data.length === 12);
      setPage(pageToLoad + 1);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch articles');
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  };

  const handleCategoryChange = (cat: string) => {
    setSelectedCategory(cat === 'all' ? '' : cat);
    setPage(0);
    loadArticles(true, cat === 'all' ? '' : cat);
  };

  const handleSearch = () => {
    setPage(0);
    loadArticles(true);
  };

  const handleLoadMore = () => {
    loadArticles(false);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-primary/5 to-secondary/5 border-b border-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
            <div className="text-center animate-fade-up">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black mb-4 text-foreground tracking-tight">
                TrendNexAI
              </h1>
              <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-8 leading-relaxed">
                Discover the latest news powered by AI, delivered in multiple languages. Stay informed with our intelligent news curation.
              </p>

              {/* Search Bar */}
              <div className="max-w-2xl mx-auto">
                <div className="relative group">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground transition-colors duration-200 group-focus-within:text-primary" />
                  <input
                    type="text"
                    placeholder="Search articles..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full pl-12 pr-4 py-3 bg-background border-2 border-border rounded-lg font-medium placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-colors duration-200"
                  />
                  <button
                    onClick={handleSearch}
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1 bg-primary text-primary-foreground rounded font-semibold text-sm hover:bg-primary/90 transition-colors duration-200"
                  >
                    Search
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Category Filter Section */}
        <section className="border-b border-border bg-background sticky top-16 z-40 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Mobile Filter Toggle */}
            <div className="flex md:hidden items-center justify-between py-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-3 py-2 bg-muted text-foreground rounded-lg font-semibold hover:bg-primary/10 transition-colors duration-200"
              >
                <Filter className="w-4 h-4" />
                Filters
              </button>
              <span className="text-sm text-muted-foreground">Topic</span>
            </div>

            {/* Desktop Categories */}
            <div className={`${showFilters ? 'block' : 'hidden'} md:block py-4`}>
              <div className="flex flex-col md:flex-row gap-2 md:gap-3 overflow-x-auto md:overflow-x-visible pb-2 md:pb-0">
                {FEATURED_CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => handleCategoryChange(cat.id)}
                    className={`px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition-all duration-300 ${
                      (cat.id === 'all' && selectedCategory === '') ||
                      (cat.id !== 'all' && selectedCategory === cat.id)
                        ? 'bg-primary text-primary-foreground shadow-md hover:shadow-lg'
                        : 'bg-muted text-foreground hover:bg-muted/80'
                    }`}
                  >
                    <span className="mr-2">{cat.icon}</span>
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Desktop Filters Row */}
            <div className="hidden md:flex items-center justify-between py-4 gap-4">
              <div className="flex gap-3">
                <select
                  value={sortBy}
                  onChange={(e) => {
                    setSortBy(e.target.value);
                    setPage(0);
                    loadArticles(true);
                  }}
                  className="px-4 py-2 bg-muted text-foreground border border-border rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-200"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                </select>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{articles.length} articles</span>
              </div>
            </div>
          </div>
        </section>

        {/* Articles Grid */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Error State */}
          {error && (
            <div className="mb-8">
              <ErrorState message={error} onRetry={() => loadArticles(true)} />
            </div>
          )}

          {/* Articles Grid or Loading State */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 12 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : articles.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {articles.map((article) => (
                  <ArticleCard key={article._id} article={article} />
                ))}
              </div>

              {/* Load More Section */}
              {hasMore && (
                <div className="flex justify-center mt-12">
                  <button
                    onClick={handleLoadMore}
                    disabled={isLoadingMore}
                    className="flex items-center gap-2 px-6 py-3 bg-background border-2 border-primary text-primary rounded-lg font-semibold hover:bg-primary hover:text-primary-foreground transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoadingMore ? (
                      <>
                        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <ArrowDown className="w-4 h-4" />
                        Load more articles
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* End of Articles */}
              {!hasMore && articles.length > 0 && (
                <div className="text-center py-12">
                  <p className="text-muted-foreground text-sm">
                    You've reached the end of the articles
                  </p>
                </div>
              )}
            </>
          ) : (
            <EmptyState
              title="No articles found"
              description={
                searchQuery
                  ? `No articles match your search "${searchQuery}". Try different keywords.`
                  : 'No articles available in this category. Try selecting a different one.'
              }
              actionLabel="Clear filters"
              actionHref="/"
            />
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
}
