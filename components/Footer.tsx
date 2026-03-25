import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="trendnexai-bg text-white mt-12 border-t border-white/20 animate-fade-up">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 backdrop-blur-sm">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-2xl font-bold mb-4">TrendNexAI</h3>
            <p className="text-gray-300 mb-4">
              AI-powered news platform delivering simplified, multilingual content
              for the modern reader.
            </p>
            <div className="flex space-x-4">
              <Link href="#" className="text-gray-300 hover:text-white">
                Twitter
              </Link>
              <Link href="#" className="text-gray-300 hover:text-white">
                Facebook
              </Link>
              <Link href="#" className="text-gray-300 hover:text-white">
                LinkedIn
              </Link>
            </div>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Categories</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/category/technology" className="text-gray-300 hover:text-white">
                  Technology
                </Link>
              </li>
              <li>
                <Link href="/category/business" className="text-gray-300 hover:text-white">
                  Business
                </Link>
              </li>
              <li>
                <Link href="/category/sports" className="text-gray-300 hover:text-white">
                  Sports
                </Link>
              </li>
              <li>
                <Link href="/category/health" className="text-gray-300 hover:text-white">
                  Health
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-4">Explore</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/about" className="text-gray-300 hover:text-white">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-300 hover:text-white">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-300 hover:text-white">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-gray-300 hover:text-white">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 mt-8 pt-8 text-center">
          <p className="text-gray-300">
            © {currentYear} TrendNexAI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}