"use client";

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ArticleCard from '@/components/ArticleCard';
import { fetchArticles, fetchCategories } from '@/lib/api';

const TOP_CATEGORIES = ['technology', 'business', 'sports', 'health'];

export default function Home() {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('newest');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  async function loadMeta() {
    try {
      const cats = await fetchCategories();
      setCategories(cats);
    } catch {
      // ignore
    }
  }

  async function loadArticles(reset = false, categoryOverride?: string) {
    try {
      setError('');
      setLoading(true);
      const pageToLoad = reset ? 0 : page;
      const selectedCategory = categoryOverride !== undefined ? categoryOverride : category;
      const res = await fetchArticles({ category: selectedCategory, search, sort, page: pageToLoad, pageSize: 12 });
      const data = res.items || [];
      setArticles((prev) => (reset ? data : [...prev, ...data]));
      setHasMore(data.length === 12);
      setPage(pageToLoad + 1);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch articles');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMeta();
    loadArticles(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function onApplyFilters() {
    setPage(0);
    loadArticles(true);
  }

  return (
    <div className="min-h-screen trendnexai-bg text-slate-900 dark:text-slate-100">
      <Header />
      <main className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <section className="glass-glow p-6 mb-8 animate-fade-up">
          <h1 className="text-4xl md:text-6xl font-black text-white drop-shadow-lg mb-4">TrendNexAI</h1>
          <p className="text-xl text-white/80 mb-6">
            AI-powered multilingual news, now with filters, search, sort & infinite loading.
          </p>

          <div className="flex flex-wrap gap-2 mb-4 animate-pop-in">
            {TOP_CATEGORIES.map((cat) => {
              const active = category.toLowerCase() === cat;
              return (
                <button
                  key={cat}
                  onClick={() => {
                    const normalized = cat;
                    setCategory(normalized);
                    setPage(0);
                    loadArticles(true, normalized);
                  }}
                  className={`px-3 py-1.5 rounded-full text-sm font-semibold transition-all duration-300 ${active ? 'bg-white text-slate-900 shadow-lg' : 'bg-white/20 text-white hover:bg-white/40'}`}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              );
            })}
            <button
              onClick={() => {
                setCategory('');
                setPage(0);
                loadArticles(true, '');
              }}
              className="px-3 py-1.5 rounded-full text-sm font-semibold text-white bg-primary/80 hover:bg-primary transition-all duration-300"
            >
              All
            </button>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 mb-4">
            <select className="p-2 rounded border" value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <input className="p-2 rounded border" placeholder="Search" value={search} onChange={(e) => setSearch(e.target.value)} />
            <select className="p-2 rounded border" value={sort} onChange={(e) => setSort(e.target.value)}>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </div>
          <button className="btn-gradient" onClick={onApplyFilters}>Apply</button>
        </section>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <ArticleCard key={article._id} article={article} />
          ))}
        </section>

        <div className="text-center mt-8">
          {loading ? (
            <span>Loading...</span>
          ) : hasMore ? (
            <button className="btn-outline px-6 py-2 rounded-lg" onClick={() => loadArticles(false)}>Load More</button>
          ) : (
            <span>No more articles</span>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
