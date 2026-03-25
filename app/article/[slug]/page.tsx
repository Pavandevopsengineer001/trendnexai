import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Badge } from '@/components/ui/badge';
import ArticleContent from '@/components/ArticleContent';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';

async function getArticle(slug: string) {
  const res = await fetch(`${API_BASE}/api/article/${encodeURIComponent(slug)}`, {
    cache: 'no-store',
  });
  if (!res.ok) return null;
  const article = await res.json();
  return article;
}

export async function generateMetadata({ params }: any): Promise<Metadata> {
  const article = await getArticle(params.slug);

  if (!article) {
    return {
      title: 'Article Not Found',
    };
  }

  return {
    title: article.seo_title,
    description: article.seo_description,
    keywords: article.tags.join(', '),
    openGraph: {
      title: article.seo_title,
      description: article.seo_description,
      type: 'article',
    },
  };
}

export default async function ArticlePage({ params }: any) {
  const article = await getArticle(params.slug);

  if (!article) {
    notFound();
  }

  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <header className="mb-8 glass-glow p-6 animate-fade-up">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <Badge variant="secondary">{article.category}</Badge>
            {article.company && (
              <span className="text-sm text-blue-600 dark:text-blue-300 font-medium">
                {article.company}
              </span>
            )}
            <span className="text-sm text-gray-500 dark:text-gray-300">
              {new Date(article.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {article.title}
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
            {article.summary}
          </p>

          <div className="flex flex-wrap gap-2 mb-6">
            {article.tags.map((tag: string) => (
              <Badge key={tag} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
        </header>

        <div className="mb-8 bg-white/40 dark:bg-slate-800/50 border border-white/30 dark:border-slate-700/40 rounded-xl h-32 flex items-center justify-center text-gray-700 dark:text-gray-200 animate-pop-in">
          [In-Article Ad - 300x250]
        </div>

        <ArticleContent article={article} />

        <div className="mb-8 bg-white/40 dark:bg-slate-800/50 border border-white/30 dark:border-slate-700/40 rounded-xl h-32 flex items-center justify-center text-gray-700 dark:text-gray-200 animate-pop-in">
          [Bottom Article Ad - 728x90]
        </div>

        <section className="border-t border-gray-200 dark:border-slate-700 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Related Articles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-100 dark:bg-slate-800 p-4 rounded-lg">
              <p className="text-gray-600 dark:text-gray-300">Related articles will be displayed here</p>
            </div>
            <div className="bg-gray-100 dark:bg-slate-800 p-4 rounded-lg">
              <p className="text-gray-600 dark:text-gray-300">Related articles will be displayed here</p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
