/**
 * EXAMPLE: Category Page Implementation
 * File: app/category/[category]/page.tsx
 */

'use client';

import { useParams, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import CategoryPageHeader from '@/components/CategoryPageHeader';
import ArticleCard from '@/components/ArticleCard';
import SkeletonCard from '@/components/SkeletonCard';
import EmptyState from '@/components/EmptyState';
import ErrorState from '@/components/ErrorState';
import { getCategoryById, CATEGORY_ARRAY } from '@/lib/categories';
import { fetchArticles } from '@/lib/api';

export default function CategoryPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const categoryId = params.category as string;
  
  const category = getCategoryById(categoryId);
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState(searchParams.get('filter') || 'latest');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    if (!category) return;
    setPage(0);
    setArticles([]);
    loadArticles(0, filter);
  }, [category, filter]);

  const loadArticles = async (pageNum: number, currentFilter: string) => {
    if (!category) return;

    try {
      setLoading(pageNum === 0);
      setError('');

      const response = await fetchArticles({
        category: category.id,
        sort: currentFilter === 'trending' ? 'trending' : 'newest',
        page: pageNum,
        pageSize: 12,
      });

      const newArticles = response.items || [];
      setArticles(prev => pageNum === 0 ? newArticles : [...prev, ...newArticles]);
      setHasMore(newArticles.length === 12);
      setPage(pageNum + 1);
    } catch (err: any) {
      setError(err?.message || 'Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    loadArticles(page, filter);
  };

  if (!category) {
    return (
      <div className="min-h-screen bg-background text-foreground flex flex-col">
        <Header />
        <main className="flex-1">
          <EmptyState
            title="Category not found"
            description="The category you're looking for doesn't exist."
            actionLabel="Back to Home"
            actionHref="/"
          />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Category Header */}
        <CategoryPageHeader
          category={category}
          articleCount={articles.length}
          currentFilter={filter}
          onFilterChange={setFilter}
        />

        {/* Articles Section */}
        <section className="section-spacing">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {error ? (
              <ErrorState
                message={error}
                onRetry={() => loadArticles(0, filter)}
              />
            ) : articles.length > 0 || !loading ? (
              <>
                {/* Articles Grid */}
                <div className="articles-grid">
                  {loading && articles.length === 0 ? (
                    <>
                      {[...Array(12)].map((_, i) => (
                        <SkeletonCard key={i} />
                      ))}
                    </>
                  ) : articles.length > 0 ? (
                    articles.map((article) => (
                      <ArticleCard key={article._id} article={article} />
                    ))
                  ) : (
                    <div className="col-span-full">
                      <EmptyState
                        title={`No ${category.label} articles`}
                        description="Check back soon for new articles in this category."
                        actionLabel="View All Articles"
                        actionHref="/"
                        icon={category.icon}
                      />
                    </div>
                  )}
                </div>

                {/* Load More Button */}
                {hasMore && articles.length > 0 && !loading && (
                  <div className="flex justify-center mt-12">
                    <button
                      onClick={loadMore}
                      className="btn-primary px-8 py-3 rounded-lg"
                    >
                      Load More Articles
                    </button>
                  </div>
                )}
              </>
            ) : null}
          </div>
        </section>

        {/* Related Categories Section */}
        {articles.length > 0 && (
          <section className="section-spacing bg-muted/30 border-y border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <h2 className="text-2xl md:text-3xl font-bold mb-8">Other Categories</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {CATEGORY_ARRAY.filter(cat => cat.id !== category.id).map(cat => (
                  <a
                    key={cat.id}
                    href={cat.href}
                    className={`card-hover p-6 rounded-lg text-center group border-2 ${cat.borderColor}`}
                  >
                    <div className="text-4xl mb-3">{cat.icon}</div>
                    <h3 className="font-bold group-hover:text-primary transition-colors duration-200">
                      {cat.label}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-2">
                      {cat.description}
                    </p>
                  </a>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}
