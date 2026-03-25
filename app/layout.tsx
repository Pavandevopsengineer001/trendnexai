import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ThemeProvider } from 'next-themes'
import './globals.css'

const geist = Geist({ subsets: ["latin"], variable: '--font-sans' });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: '--font-mono' });

export const metadata: Metadata = {
  title: {
    default: 'TrendNexAI - AI-Powered Multilingual News',
    template: '%s | TrendNexAI'
  },
  description: 'Stay informed with AI-simplified news in multiple Indian languages. Latest updates in English, Telugu, Tamil, Kannada, and Malayalam.',
  keywords: ['news', 'AI', 'multilingual', 'India', 'Telugu', 'Tamil', 'Kannada', 'Malayalam', 'artificial intelligence'],
  authors: [{ name: 'TrendNexAI' }],
  creator: 'TrendNexAI',
  publisher: 'TrendNexAI',
  generator: 'Next.js',
  referrer: 'origin-when-cross-origin',
  metadataBase: new URL('https://trendnexai.com'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://trendnexai.com',
    title: 'TrendNexAI - AI-Powered Multilingual News',
    description: 'Stay informed with AI-simplified news in multiple Indian languages.',
    siteName: 'TrendNexAI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TrendNexAI - AI-Powered Multilingual News',
    description: 'Stay informed with AI-simplified news in multiple Indian languages.',
  },
  icons: {
    icon: '/icon.svg',
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#ffffff',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className={`${geist.variable} ${geistMono.variable} font-sans antialiased trendnexai-bg`}> 
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
          <Analytics />
        </ThemeProvider>
      </body>
    </html>
  )
}