import Link from 'next/link';
import { TrendingUp, ArrowRight } from 'lucide-react';
import { getCategoryById } from '@/lib/categories';

interface TrendingSectionProps {
  articles: any[];
  loading?: boolean;
}

export default function TrendingSection({ articles, loading = false }: TrendingSectionProps) {
  const trendingArticles = articles.slice(0, 5);

  return (
    <section className="section-spacing-sm bg-muted/50 border-y border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center gap-2 mb-8 animate-fade-in">
          <TrendingUp className="w-5 h-5 text-secondary" />
          <h2 className="text-2xl md:text-3xl font-bold">Trending Now</h2>
        </div>

        {/* Horizontal Scroll Articles */}
        <div className="overflow-x-auto scrollbar-hide pb-4">
          <div className="flex gap-4 min-w-min">
            {loading ? (
              <>
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="w-72 h-48 bg-background rounded-lg animate-pulse flex-shrink-0" />
                ))}
              </>
            ) : trendingArticles.length > 0 ? (
              trendingArticles.map((article, idx) => {
                const category = getCategoryById(article.category);
                return (
                  <Link
                    key={article._id}
                    href={`/article/${article.slug}`}
                    className="flex-shrink-0 w-72 group"
                  >
                    <article className="card-hover h-full flex flex-col overflow-hidden">
                      {/* Rank Badge */}
                      <div className="absolute top-3 left-3 z-10 w-8 h-8 bg-secondary text-secondary-foreground rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
                        {idx + 1}
                      </div>

                      {/* Image */}
                      {article.image_url && (
                        <div className="relative h-40 overflow-hidden bg-muted">
                          <img
                            src={article.image_url}
                            alt={article.title}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-background/60 to-transparent" />
                        </div>
                      )}

                      {/* Content */}
                      <div className="flex-1 p-4 flex flex-col">
                        {category && (
                          <span className={`badge ${category.badgeClass} mb-2 w-max`}>
                            {category.label}
                          </span>
                        )}

                        <h3 className="font-bold text-sm line-clamp-2 mb-2 group-hover:text-primary transition-colors duration-200 flex-grow">
                          {article.title}
                        </h3>

                        <p className="text-xs text-muted-foreground line-clamp-1 mb-3">
                          {article.summary}
                        </p>

                        <div className="flex items-center justify-between pt-3 border-t border-border/50">
                          <span className="text-xs text-muted-foreground">
                            {new Date(article.createdAt).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                          <ArrowRight className="w-3 h-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                        </div>
                      </div>
                    </article>
                  </Link>
                );
              })
            ) : (
              <div className="w-full py-8 text-center text-muted-foreground">
                No trending articles available
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
