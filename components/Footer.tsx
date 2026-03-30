'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Facebook, Twitter, Linkedin, Github, Mail, Heart } from 'lucide-react';
import { CATEGORY_ARRAY } from '@/lib/categories';

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const [mounted, setMounted] = useState(false);
  const { theme } = useTheme();

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const footerSections = [
    {
      title: 'Categories',
      links: CATEGORY_ARRAY.map(cat => ({
        label: cat.label,
        href: cat.href,
      })),
    },
    {
      title: 'Company',
      links: [
        { label: 'About Us', href: '/about' },
        { label: 'Contact', href: '/contact' },
        { label: 'Blog', href: '/' },
      ],
    },
    {
      title: 'Legal',
      links: [
        { label: 'Privacy Policy', href: '/privacy' },
        { label: 'Terms of Service', href: '/terms' },
      ],
    },
  ];

  const socialLinks = [
    { icon: Twitter, href: '#twitter', label: 'Twitter', shorthand: 'X' },
    { icon: Facebook, href: '#facebook', label: 'Facebook' },
    { icon: Linkedin, href: '#linkedin', label: 'LinkedIn' },
    { icon: Github, href: '#github', label: 'GitHub' },
    { icon: Mail, href: 'mailto:contact@trendnexai.com', label: 'Email' },
  ];

  return (
    <footer className="bg-muted/30 border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12 py-16">
          {/* Brand Section */}
          <div className="lg:col-span-1 md:col-span-2">
            <Link 
              href="/" 
              className="inline-flex items-center mb-4 group focus:outline-none focus:ring-2 focus:ring-primary rounded-lg p-1"
            >
              {mounted && (
                <Image
                  src={theme === 'dark' ? '/trendnexai_dk.png' : '/trendnexai_wt.png'}
                  alt="TrendNexAI Logo"
                  width={280}
                  height={100}
                  className="h-32 w-auto object-contain transition-all duration-300"
                />
              )}
            </Link>

            <p className="text-sm text-muted-foreground mb-6 leading-relaxed max-w-xs">
              Stay informed with AI-powered insights across Technology, Business, Sports, and Health. Get smarter news in seconds.
            </p>

            {/* Social Links */}
            <div className="flex gap-3">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.href}
                    aria-label={social.label}
                    title={social.label}
                    className="p-2.5 rounded-lg bg-background border border-border text-muted-foreground hover:text-primary hover:border-primary hover:bg-primary/10 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <Icon className="w-4 h-4" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Links Sections */}
          {footerSections.map((section) => (
            <div key={section.title} className="lg:col-span-1">
              <h4 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide opacity-80">
                {section.title}
              </h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary rounded px-2 py-1"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Newsletter Signup */}
          <div className="lg:col-span-1">
            <h4 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide opacity-80">
              Newsletter
            </h4>
            <p className="text-sm text-muted-foreground mb-4">
              Get the latest insights delivered to your inbox.
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="Your email"
                className="flex-1 px-3 py-2 text-sm bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                aria-label="Email for newsletter"
              />
              <button
                className="px-3 py-2 bg-primary text-primary-foreground text-sm font-semibold rounded-lg hover:bg-primary/90 transition-colors duration-200"
                aria-label="Subscribe to newsletter"
              >
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border" />

        {/* Bottom Footer */}
        <div className="py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <p className="flex items-center gap-2">
            © {currentYear} TrendNexAI. Made with <Heart className="w-4 h-4 text-destructive" /> by the TrendNexAI team.
          </p>
          <div className="flex gap-6">
            <Link
              href="/privacy"
              className="hover:text-primary transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary rounded px-2 py-1"
            >
              Privacy
            </Link>
            <Link
              href="/terms"
              className="hover:text-primary transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary rounded px-2 py-1"
            >
              Terms
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}