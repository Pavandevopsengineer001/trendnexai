import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Category } from '@/lib/categories';
import ArticleCard from './ArticleCard';
import SkeletonCard from './SkeletonCard';
import EmptyState from './EmptyState';

interface CategorySectionProps {
  category: Category;
  articles: any[];
  loading?: boolean;
  showFeatured?: boolean;
}

export default function CategorySection({
  category,
  articles,
  loading = false,
  showFeatured = false,
}: CategorySectionProps) {
  const displayArticles = showFeatured ? articles.slice(0, 3) : articles.slice(0, 6);
  const featuredArticle = articles[0];

  return (
    <section className="section-spacing">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex items-baseline justify-between mb-10 animate-fade-in">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">{category.icon}</span>
              <h2 className="text-3xl md:text-4xl font-bold">{category.label}</h2>
            </div>
            <p className="text-muted-foreground text-lg">{category.description}</p>
          </div>
          <Link
            href={category.href}
            className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors duration-200 font-medium text-sm group"
          >
            View All
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
          </Link>
        </div>

        {/* Featured Article (Optional) */}
        {showFeatured && !loading && featuredArticle && (
          <div className="mb-12 animate-fade-in-delay">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Featured Article - Large */}
              <div className="md:col-span-2">
                <article className="card-featured overflow-hidden h-full flex flex-col group">
                  {/* Image */}
                  {featuredArticle.image_url && (
                    <div className="relative h-80 overflow-hidden bg-muted">
                      <img
                        src={featuredArticle.image_url}
                        alt={featuredArticle.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <div className={`absolute inset-0 bg-gradient-to-t ${category.gradient} opacity-20 group-hover:opacity-30 transition-opacity duration-300`} />
                    </div>
                  )}

                  <div className="flex-1 p-6 flex flex-col">
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`badge ${category.badgeClass}`}>
                        {category.label}
                      </span>
                      <span className="text-xs text-muted-foreground">Featured</span>
                    </div>

                    <h3 className="text-2xl md:text-3xl font-bold mb-3 line-clamp-3 flex-grow">
                      {featuredArticle.title}
                    </h3>

                    <p className="text-muted-foreground mb-4 line-clamp-2 flex-grow">
                      {featuredArticle.summary}
                    </p>

                    <div className="flex items-center justify-between pt-4 border-t border-border">
                      <span className="text-sm text-muted-foreground">
                        {new Date(featuredArticle.createdAt).toLocaleDateString()}
                      </span>
                      <Link
                        href={`/article/${featuredArticle.slug}`}
                        className="text-primary hover:text-primary/80 font-semibold text-sm"
                      >
                        Read Article →
                      </Link>
                    </div>
                  </div>
                </article>
              </div>

              {/* Top Articles Sidebar */}
              <div className="flex flex-col gap-4">
                <h4 className="font-bold text-lg mb-2">Top Stories</h4>
                {articles.slice(1, 4).map((article, idx) => (
                  <Link
                    key={article._id}
                    href={`/article/${article.slug}`}
                    className="group card-hover p-3"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl font-bold text-primary/50">
                        {idx + 2}
                      </span>
                      <div className="flex-1 min-w-0">
                        <h5 className="font-semibold text-sm group-hover:text-primary transition-colors duration-200 line-clamp-2">
                          {article.title}
                        </h5>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(article.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Articles Grid */}
        <div className="articles-grid">
          {loading ? (
            <>
              {[...Array(showFeatured ? 3 : 6)].map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </>
          ) : displayArticles.length > 0 ? (
            displayArticles.map((article, idx) => (
              <div key={article._id} className={`animate-fade-up ${idx > 0 ? `style={{ '--delay': '${idx * 50}ms' }}` : ''}`}>
                <ArticleCard article={article} />
              </div>
            ))
          ) : (
            <div className="col-span-full">
              <EmptyState
                title={`No articles in ${category.label}`}
                description={`Check back soon for new {{label}} updates.`}
                icon={category.icon}
              />
            </div>
          )}
        </div>

        {/* View All Button - Mobile */}
        <div className="mt-8 sm:hidden">
          <Link
            href={category.href}
            className="btn-primary w-full text-center"
          >
            View All {category.label} Articles
          </Link>
        </div>
      </div>
    </section>
  );
}
