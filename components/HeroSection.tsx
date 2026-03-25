import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';
import { CATEGORY_ARRAY } from '@/lib/categories';

interface HeroSectionProps {
  featuredArticle?: any;
  loading?: boolean;
}

export default function HeroSection({ featuredArticle, loading = false }: HeroSectionProps) {
  return (
    <section className="relative bg-gradient-to-br from-primary/10 via-background to-secondary/10 py-16 md:py-24 lg:py-32 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary/20 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center mb-12 animate-fade-in">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold text-primary">AI-Powered Insights</span>
          </div>

          {/* Main Title */}
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent mb-6 leading-tight">
            Stay Informed With AI
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 leading-relaxed">
            Get expert insights across Technology, Business, Sports, and Health. 
            Simplified news powered by artificial intelligence.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="#latest"
              className="btn-primary px-8 py-3 text-lg rounded-xl flex items-center gap-2 group"
            >
              Explore Latest
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-200" />
            </Link>
            <Link
              href="/about"
              className="btn-outline px-8 py-3 text-lg rounded-xl"
            >
              Learn More
            </Link>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap justify-center gap-3 mb-16 animate-fade-in-delay">
          {CATEGORY_ARRAY.map((category) => (
            <Link
              key={category.id}
              href={category.href}
              className={`group px-5 py-2.5 rounded-full border ${category.borderColor} ${category.bgColor} font-medium text-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md`}
            >
              <span className="text-lg mr-2">{category.icon}</span>
              {category.label}
            </Link>
          ))}
        </div>

        {/* Featured Article Preview */}
        {!loading && featuredArticle && (
          <div className="max-w-4xl mx-auto animate-fade-up" style={{ animationDelay: '0.2s' }}>
            <div className="card-premium overflow-hidden border-2 border-primary/30">
              <div className="grid grid-cols-1 md:grid-cols-5 gap-0">
                {/* Image */}
                {featuredArticle.image_url && (
                  <div className="md:col-span-2 h-64 md:h-auto overflow-hidden bg-muted">
                    <img
                      src={featuredArticle.image_url}
                      alt={featuredArticle.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                )}

                {/* Content */}
                <div className={`p-6 md:p-8 flex flex-col justify-between ${!featuredArticle.image_url ? 'md:col-span-5' : 'md:col-span-3'}`}>
                  <div>
                    <span className="inline-block badge badge-primary mb-3">
                      Featured
                    </span>
                    <h3 className="text-2xl md:text-3xl font-bold mb-3 line-clamp-2">
                      {featuredArticle.title}
                    </h3>
                    <p className="text-muted-foreground text-lg mb-4 line-clamp-2">
                      {featuredArticle.summary}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-border">
                    <span className="text-sm text-muted-foreground">
                      {new Date(featuredArticle.createdAt).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                    <Link
                      href={`/article/${featuredArticle.slug}`}
                      className="text-primary hover:text-primary/80 font-semibold inline-flex items-center gap-2 group/link"
                    >
                      Read Article
                      <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform duration-200" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
