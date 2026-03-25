/**
 * EXAMPLE: Updated Homepage Implementation
 * This shows how to integrate all the new components
 * 
 * File: app/page.tsx
 */

'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import HeroSection from '@/components/HeroSection';
import TrendingSection from '@/components/TrendingSection';
import CategorySection from '@/components/CategorySection';
import { CATEGORY_ARRAY } from '@/lib/categories';
import { fetchArticles } from '@/lib/api';

export default function Home() {
  const [allArticles, setAllArticles] = useState<any[]>([]);
  const [categoryArticles, setCategoryArticles] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      setLoading(true);
      setError('');

      // Load all articles
      const response = await fetchArticles({
        pageSize: 50,
      });
      
      const articles = response.items || [];
      setAllArticles(articles);

      // Group articles by category
      const grouped: Record<string, any[]> = {};
      CATEGORY_ARRAY.forEach(cat => {
        grouped[cat.id] = articles.filter(a => a.category === cat.id);
      });
      setCategoryArticles(grouped);
    } catch (err: any) {
      setError(err?.message || 'Failed to load articles');
      console.error('Error loading articles:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    loadArticles();
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <HeroSection 
          featuredArticle={allArticles[0]} 
          loading={loading}
        />

        {/* Trending Section */}
        {!error && (
          <TrendingSection 
            articles={allArticles.slice(1, 6)}
            loading={loading}
          />
        )}

        {/* Category Sections */}
        {error ? (
          <section className="section-spacing">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <ErrorState 
                message={error}
                onRetry={handleRetry}
              />
            </div>
          </section>
        ) : (
          CATEGORY_ARRAY.map(category => (
            <CategorySection
              key={category.id}
              category={category}
              articles={categoryArticles[category.id] || []}
              loading={loading}
              showFeatured={true}
            />
          ))
        )}

        {/* Call to Action Section */}
        <section className="section-spacing bg-gradient-to-r from-primary/10 to-secondary/10 border-y border-border">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Never Miss Important Updates
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Get AI-curated insights delivered to your inbox. Industry news, 
              market trends, and expert analysis - all summarized for you.
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <button className="btn-primary px-8 py-3 text-lg rounded-xl">
                Subscribe Now
              </button>
              <button className="btn-outline px-8 py-3 text-lg rounded-xl">
                Learn More
              </button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
