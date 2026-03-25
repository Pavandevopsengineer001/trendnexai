import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ArticleCard from '@/components/ArticleCard';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';

export async function generateMetadata({ params }: any): Promise<Metadata> {
  return {
    title: `TrendNexAI | ${params.company} News`,
    description: `Latest news stories from company ${params.company}.`,
  };
}

async function getCompanyArticles(company: string) {
  try {
    const res = await fetch(`${API_BASE}/api/articles?company=${encodeURIComponent(company)}&limit=50`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) {
      console.warn(`API request failed with status ${res.status}`);
      return [];
    }
    const payload = await res.json();
    return payload.items || [];
  } catch (error) {
    console.warn('Failed to fetch company articles:', error);
    return [];
  }
}

export default async function CompanyPage({ params }: any) {
  const articles = await getCompanyArticles(params.company);

  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 mb-8 animate-fade-up">
          <h1 className="text-4xl font-bold mb-4">Company: {params.company}</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-8">
            Showing latest articles from {params.company}.
          </p>

          {articles.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No articles found for this company yet.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article: any) => (
                <ArticleCard key={article._id} article={article} />
              ))}
            </div>
          )}
        </section>
      </main>
      <Footer />
    </div>
  );
}
