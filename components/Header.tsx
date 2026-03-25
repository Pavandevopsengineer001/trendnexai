'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import { Menu, X, Search, Bell, ChevronDown } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { CATEGORY_ARRAY, getCategoryById } from '@/lib/categories';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  const { theme } = useTheme();

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur-md border-b border-border transition-all duration-300">
      <div className="max-w-7xl mx-auto">
        {/* Main Navigation Bar */}
        <div className="flex justify-between items-center px-4 sm:px-6 lg:px-8 h-24">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center group focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary rounded-lg"
          >
            {mounted && (
              <Image
                src={theme === 'dark' ? '/trendnexai_dk.png' : '/trendnexai_wt.png'}
                alt="TrendNexAI Logo"
                width={400}
                height={150}
                className="h-24 w-auto object-contain transition-all duration-300"
                priority
              />
            )}
          </Link>

          {/* Center Navigation - Desktop */}
          <nav className="hidden md:flex items-center gap-8">
            <Link 
              href="/" 
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Home
            </Link>

            {/* Category Dropdown */}
            <div className="relative group">
              <button className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-200 flex items-center gap-1.5 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded px-2 py-1">
                Categories
                <ChevronDown className="w-4 h-4 group-hover:rotate-180 transition-transform duration-200" />
              </button>
              
              <div className="absolute left-0 mt-0 bg-card border border-border rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pt-3 min-w-48">
                <div className="grid grid-cols-1 gap-0">
                  {CATEGORY_ARRAY.map((category) => (
                    <Link
                      key={category.id}
                      href={category.href}
                      className="px-4 py-2.5 text-sm hover:bg-muted transition-colors duration-200 flex items-center gap-2 border-b border-border last:border-b-0"
                    >
                      <span className="text-lg">{category.icon}</span>
                      <span className="font-medium">{category.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            <Link 
              href="/about" 
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/about') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              About
            </Link>

            <Link 
              href="/contact" 
              className={`text-sm font-medium transition-colors duration-200 ${
                isActive('/contact') ? 'text-primary font-semibold' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Contact
            </Link>
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            {/* Search Button */}
            <button 
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200 md:hidden focus:outline-none focus:ring-2 focus:ring-primary"
              aria-label="Search"
            >
              <Search className="w-5 h-5 text-muted-foreground" />
            </button>

            {/* Desktop Search Bar */}
            <div className="hidden md:flex items-center bg-muted rounded-lg px-3 py-2 gap-2 focus-within:ring-2 focus-within:ring-primary">
              <Search className="w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-sm placeholder-muted-foreground focus:outline-none w-32"
                aria-label="Search articles"
              />
            </div>

            {/* Notifications */}
            <button 
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200 hidden sm:inline-flex focus:outline-none focus:ring-2 focus:ring-primary"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5 text-muted-foreground" />
            </button>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Mobile Menu Button */}
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 hover:bg-muted rounded-lg transition-colors duration-200 md:hidden focus:outline-none focus:ring-2 focus:ring-primary"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Search Bar */}
        {isSearchOpen && (
          <div className="border-t border-border bg-muted/50 px-4 py-3 md:hidden animate-fade-in">
            <div className="flex items-center bg-background rounded-lg px-3 py-2 gap-2 border border-border focus-within:ring-2 focus-within:ring-primary">
              <Search className="w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-sm placeholder-muted-foreground focus:outline-none w-full"
                autoFocus
                aria-label="Search articles"
              />
            </div>
          </div>
        )}

        {/* Mobile Menu */}
        {isMenuOpen && (
          <nav className="border-t border-border bg-muted/50 animate-fade-in md:hidden">
            <div className="px-4 py-3 space-y-2">
              <Link
                href="/"
                className={`block px-3 py-2.5 rounded-lg transition-colors duration-200 ${
                  isActive('/') 
                    ? 'bg-primary text-primary-foreground font-semibold' 
                    : 'text-foreground hover:bg-background'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Home
              </Link>

              {CATEGORY_ARRAY.map((category) => (
                <Link
                  key={category.id}
                  href={category.href}
                  className="block px-3 py-2.5 rounded-lg text-foreground hover:bg-background transition-colors duration-200"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span className="text-lg mr-2">{category.icon}</span>
                  {category.label}
                </Link>
              ))}

              <Link
                href="/about"
                className={`block px-3 py-2.5 rounded-lg transition-colors duration-200 ${
                  isActive('/about') 
                    ? 'bg-primary text-primary-foreground font-semibold' 
                    : 'text-foreground hover:bg-background'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                About
              </Link>

              <Link
                href="/contact"
                className={`block px-3 py-2.5 rounded-lg transition-colors duration-200 ${
                  isActive('/contact') 
                    ? 'bg-primary text-primary-foreground font-semibold' 
                    : 'text-foreground hover:bg-background'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Contact
              </Link>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}