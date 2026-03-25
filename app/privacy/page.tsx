import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Privacy Policy | TrendNexAI',
  description: 'Learn how TrendNexAI collects, uses, and protects your personal information.',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen trendnexai-bg dark:bg-slate-950 text-gray-900 dark:text-gray-100">
      <Header />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <section className="glass-glow p-8 animate-fade-up">
          <h1 className="text-4xl font-bold mb-6">Privacy Policy</h1>

          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
              Last updated: {new Date().toLocaleDateString()}
            </p>

            <p className="mb-6">
              At TrendNexAI, we are committed to protecting your privacy and ensuring the security
              of your personal information. This Privacy Policy explains how we collect, use,
              disclose, and safeguard your information when you use our website and services.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Information We Collect</h2>

            <h3 className="text-xl font-medium mb-3">Personal Information</h3>
            <p className="mb-4">
              We may collect personal information that you provide directly to us, such as:
            </p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>Name and contact information (email, phone number)</li>
              <li>Account credentials and preferences</li>
              <li>Communication preferences</li>
              <li>Feedback and support requests</li>
            </ul>

            <h3 className="text-xl font-medium mb-3">Usage Information</h3>
            <p className="mb-4">
              We automatically collect certain information about your use of our services:
            </p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>IP address and location information</li>
              <li>Browser type and version</li>
              <li>Pages visited and time spent on our site</li>
              <li>Device information and screen resolution</li>
              <li>Referral sources</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">How We Use Your Information</h2>
            <p className="mb-4">We use the information we collect to:</p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>Provide, maintain, and improve our services</li>
              <li>Process transactions and send related information</li>
              <li>Send technical notices and support messages</li>
              <li>Respond to your comments and questions</li>
              <li>Analyze usage patterns and improve user experience</li>
              <li>Prevent fraud and ensure security</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Information Sharing</h2>
            <p className="mb-6">
              We do not sell, trade, or otherwise transfer your personal information to third parties
              without your consent, except as described in this policy. We may share your information
              in the following circumstances:
            </p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>With service providers who assist us in operating our website</li>
              <li>To comply with legal obligations</li>
              <li>To protect our rights and prevent fraud</li>
              <li>In connection with a business transfer or acquisition</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
            <p className="mb-6">
              We implement appropriate technical and organizational measures to protect your personal
              information against unauthorized access, alteration, disclosure, or destruction. However,
              no method of transmission over the internet is 100% secure.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
            <p className="mb-4">You have the right to:</p>
            <ul className="list-disc list-inside mb-6 space-y-1">
              <li>Access and update your personal information</li>
              <li>Request deletion of your data</li>
              <li>Opt out of marketing communications</li>
              <li>Request data portability</li>
              <li>Lodge a complaint with supervisory authorities</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Cookies</h2>
            <p className="mb-6">
              We use cookies and similar technologies to enhance your experience on our website.
              You can control cookie settings through your browser preferences.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Changes to This Policy</h2>
            <p className="mb-6">
              We may update this Privacy Policy from time to time. We will notify you of any changes
              by posting the new policy on this page and updating the &quot;Last updated&quot; date.
            </p>

            <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
            <p className="mb-6">
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <p className="mb-2">
              <strong>Email:</strong> privacy@trendnexai.com
            </p>
            <p className="mb-2">
              <strong>Address:</strong> TrendNexAI Privacy Team, [Company Address]
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}