import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Terms of Service | TrendNexAI',
  description: 'Read the terms and conditions for using TrendNexAI services.',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 animate-fade-up">
          <h1 className="text-4xl font-bold mb-6">Terms of Service</h1>

          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Last updated: {new Date().toLocaleDateString()}
            </p>

            <p className="mb-6">
              Welcome to TrendNexAI. These Terms of Service (&quot;Terms&quot;) govern your use of our
              website and services. By accessing or using TrendNexAI, you agree to be bound by these Terms.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Acceptance of Terms</h2>
            <p className="mb-6">
              By accessing and using TrendNexAI, you accept and agree to be bound by the terms and
              provision of this agreement. If you do not agree to abide by the above, please do not
              use this service.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Use License</h2>
            <p className="mb-4">Permission is granted to temporarily use TrendNexAI for personal,
            non-commercial transitory viewing only. This is the grant of a license, not a transfer
            of title, and under this license you may not:</p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>Modify or copy the materials</li>
              <li>Use the materials for any commercial purpose or for any public display</li>
              <li>Attempt to decompile or reverse engineer any software contained on our website</li>
              <li>Remove any copyright or other proprietary notations from the materials</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Service Description</h2>
            <p className="mb-6">
              TrendNexAI provides AI-powered news aggregation, summarization, and multilingual
              content delivery services. We strive to provide accurate and timely information,
              but we cannot guarantee the completeness or accuracy of all content.
            </p>

            <h2 className="text-2xl font-semibold mb-4">User Responsibilities</h2>
            <p className="mb-4">As a user of our service, you agree to:</p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>Provide accurate and complete information when creating an account</li>
              <li>Use the service only for lawful purposes</li>
              <li>Not engage in any activity that interferes with or disrupts our services</li>
              <li>Not attempt to gain unauthorized access to our systems</li>
              <li>Respect the intellectual property rights of others</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Content and Accuracy</h2>
            <p className="mb-6">
              While we strive to provide accurate and reliable news content, we cannot guarantee
              the accuracy, completeness, or timeliness of information. Users should verify
              information from multiple sources when making important decisions.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Intellectual Property</h2>
            <p className="mb-6">
              The service and its original content, features, and functionality are and will remain
              the exclusive property of TrendNexAI and its licensors. The service is protected by
              copyright, trademark, and other laws.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Privacy</h2>
            <p className="mb-6">
              Your privacy is important to us. Please review our Privacy Policy, which also governs
              your use of TrendNexAI, to understand our practices.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Termination</h2>
            <p className="mb-6">
              We may terminate or suspend your account and bar access to the service immediately,
              without prior notice or liability, under our sole discretion, for any reason whatsoever
              and without limitation, including but not limited to a breach of the Terms.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Disclaimer</h2>
            <p className="mb-6">
              The information on this website is provided on an &apos;as is&apos; basis. To the fullest
              extent permitted by law, TrendNexAI excludes all representations, warranties, conditions
              and terms whether express or implied, statutory or otherwise.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Limitation of Liability</h2>
            <p className="mb-6">
              In no event shall TrendNexAI, nor its directors, employees, partners, agents, suppliers,
              or affiliates, be liable for any indirect, incidental, special, consequential, or punitive
              damages, including without limitation, loss of profits, data, use, goodwill, or other
              intangible losses.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Governing Law</h2>
            <p className="mb-6">
              These Terms shall be interpreted and governed by the laws of [Jurisdiction], without
              regard to conflict of law provisions. Our failure to enforce any right or provision
              of these Terms will not be considered a waiver of those rights.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Changes to Terms</h2>
            <p className="mb-6">
              We reserve the right, at our sole discretion, to modify or replace these Terms at any
              time. If a revision is material, we will provide at least 30 days notice prior to any
              new terms taking effect.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Contact Information</h2>
            <p className="mb-6">
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <p className="mb-2">
              <strong>Email:</strong> legal@trendnexai.com
            </p>
            <p className="mb-2">
              <strong>Address:</strong> TrendNexAI Legal Team, [Company Address]
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}