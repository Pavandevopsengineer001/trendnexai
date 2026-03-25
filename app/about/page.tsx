import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'About Us | TrendNexAI',
  description: 'Learn about TrendNexAI, our mission to deliver AI-powered, multilingual news content for the modern reader.',
};

export default function AboutPage() {
  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 animate-fade-up">
          <h1 className="text-4xl font-bold mb-6">About TrendNexAI</h1>

          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
              Welcome to TrendNexAI, where artificial intelligence meets journalism to deliver
              news that&apos;s accessible, understandable, and relevant to everyone.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
            <p className="mb-6">
              In today&apos;s fast-paced world, staying informed shouldn&apos;t be a challenge.
              Our mission is to simplify complex news stories using advanced AI technology,
              making quality journalism accessible to readers worldwide in multiple languages.
            </p>

            <h2 className="text-2xl font-semibold mb-4">What We Do</h2>
            <ul className="list-disc list-inside mb-6 space-y-2">
              <li>AI-powered news summarization and simplification</li>
              <li>Multilingual content delivery (English, Telugu, Tamil, Kannada, Malayalam)</li>
              <li>Real-time news aggregation from trusted sources</li>
              <li>Category-based news organization</li>
              <li>Company-specific news tracking</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Our Technology</h2>
            <p className="mb-6">
              We leverage cutting-edge AI models to analyze, summarize, and rephrase news articles
              while maintaining factual accuracy and journalistic integrity. Our system ensures
              that complex topics are explained in clear, concise language.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Our Commitment</h2>
            <p className="mb-6">
              We are committed to providing unbiased, factual news content. Our AI systems are
              designed to detect and filter out misinformation, ensuring that our readers receive
              only verified, trustworthy information.
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}