'use client';

import Link from 'next/link';
import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'te', name: 'Telugu' },
  { code: 'ta', name: 'Tamil' },
  { code: 'kn', name: 'Kannada' },
  { code: 'ml', name: 'Malayalam' },
];

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const pathname = usePathname();

  const navItems = [
    { label: 'Home', href: '/' },
    { label: 'Technology', href: '/category/technology' },
    { label: 'Business', href: '/category/business' },
    { label: 'Sports', href: '/category/sports' },
    { label: 'Health', href: '/category/health' },
    { label: 'About', href: '/about' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm border-b border-slate-200 text-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 animate-fade-up">
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-gray-900">
              TrendNexAI
            </Link>
          </div>

          <nav className="hidden md:flex space-x-6">
            {navItems.map((item) => {
              const active = pathname === item.href || (item.href.startsWith('/category') && pathname?.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`font-medium transition-all duration-200 px-2 py-1 rounded-md ${active ? 'bg-white text-slate-900 shadow-md' : 'text-gray-700 dark:text-gray-200 hover:text-blue-600 dark:hover:text-sky-300 hover:bg-white/20 dark:hover:bg-slate-800/60'}`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <select className="text-sm border rounded px-2 py-1 bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-100">
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>

            {/* Theme toggler */}
            <ThemeToggle />

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4">
            <nav className="flex flex-col space-y-2">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href} className="text-gray-700 hover:text-gray-900 py-2">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>

      {/* Top Banner Ad Placeholder */}
      <div className="bg-gray-100 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="bg-blue-200 h-16 flex items-center justify-center text-sm text-gray-600">
            [Top Banner Ad - 728x90]
          </div>
        </div>
      </div>
    </header>
  );
}