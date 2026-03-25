"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { fetchCategories } from '@/lib/api';

export default function CategoriesPage() {
  const [categories, setCategories] = useState<string[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setError('');
        const data = await fetchCategories();
        setCategories(data);
      } catch (err: any) {
        setError('Failed to load categories');
      }
    })();
  }, []);

  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 mb-8">
          <h1 className="text-4xl font-bold mb-4">News Categories</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Explore curated category feeds. Tap a category to view its latest stories.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.length === 0 ? (
              <div className="col-span-full text-center py-10 text-gray-500">No categories found yet.</div>
            ) : (
              categories.map((category) => (
                <Link
                  key={category}
                  href={`/category/${encodeURIComponent(category.toLowerCase())}`}
                  className="p-5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white/70 dark:bg-slate-800/70 hover:shadow-lg transition duration-300"
                >
                  <h2 className="text-xl font-semibold">{category}</h2>
                  <p className="text-sm text-gray-500">View articles in {category}</p>
                </Link>
              ))
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
