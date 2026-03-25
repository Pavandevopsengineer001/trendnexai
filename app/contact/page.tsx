import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Contact Us | TrendNexAI',
  description: 'Get in touch with the TrendNexAI team. We&apos;d love to hear from you.',
};

export default function ContactPage() {
  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 animate-fade-up">
          <h1 className="text-4xl font-bold mb-6">Contact Us</h1>

          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
              Have questions, feedback, or suggestions? We&apos;d love to hear from you.
              Reach out to us through any of the channels below.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h2 className="text-2xl font-semibold mb-4">General Inquiries</h2>
                <p className="mb-4">
                  For general questions about TrendNexAI, our services, or partnerships:
                </p>
                <p className="mb-2">
                  <strong>Email:</strong> info@trendnexai.com
                </p>
                <p className="mb-2">
                  <strong>Phone:</strong> +1 (555) 123-4567
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Technical Support</h2>
                <p className="mb-4">
                  For technical issues, bugs, or feature requests:
                </p>
                <p className="mb-2">
                  <strong>Email:</strong> support@trendnexai.com
                </p>
                <p className="mb-2">
                  <strong>Response Time:</strong> Within 24 hours
                </p>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-slate-800 p-6 rounded-lg mb-8">
              <h2 className="text-2xl font-semibold mb-4">Send us a Message</h2>
              <form className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium mb-2">
                      Name
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="subject" className="block text-sm font-medium mb-2">
                    Subject
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100"
                    placeholder="What's this about?"
                  />
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-medium mb-2">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    rows={5}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100"
                    placeholder="Tell us what's on your mind..."
                  />
                </div>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md font-medium transition-colors duration-200"
                >
                  Send Message
                </button>
              </form>
            </div>

            <div className="text-center">
              <h2 className="text-2xl font-semibold mb-4">Follow Us</h2>
              <p className="mb-4">
                Stay connected and get the latest updates from TrendNexAI.
              </p>
              <div className="flex justify-center space-x-4">
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  Twitter
                </a>
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  Facebook
                </a>
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}