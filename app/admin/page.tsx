'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import AdminLayout from '@/components/AdminLayout';
import Link from 'next/link';
import { BarChart3, FileText, Eye, TrendingUp } from 'lucide-react';

interface DashboardStats {
  total_articles: number;
  published_articles: number;
  draft_articles: number;
  total_views: number;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    total_articles: 0,
    published_articles: 0,
    draft_articles: 0,
    total_views: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        router.push('/admin/login');
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }

  const statCards = [
    {
      label: 'Total Articles',
      value: stats.total_articles,
      icon: FileText,
      color: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-100',
    },
    {
      label: 'Published',
      value: stats.published_articles,
      icon: TrendingUp,
      color: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-100',
    },
    {
      label: 'Draft',
      value: stats.draft_articles,
      icon: BarChart3,
      color: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-100',
    },
    {
      label: 'Total Views',
      value: stats.total_views,
      icon: Eye,
      color: 'bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-100',
    },
  ];

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Welcome to TrendNexAI Admin</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.label}
                className="bg-card border border-border rounded-lg p-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground font-medium">
                      {card.label}
                    </p>
                    <p className="text-3xl font-bold text-foreground mt-2">
                      {loading ? '—' : stats[card.label.toLowerCase().replace(' ', '_') as any] || 0}
                    </p>
                  </div>
                  <div className={`p-4 rounded-lg ${card.color}`}>
                    <Icon size={24} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-card border border-border rounded-lg p-8 text-center">
            <FileText className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-xl font-bold text-foreground mb-2">
              Article Management
            </h3>
            <p className="text-muted-foreground mb-6">
              Create, edit, and manage articles
            </p>
            <Link
              href="/admin/articles"
              className="inline-flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              Go to Articles
            </Link>
          </div>

          <div className="bg-card border border-border rounded-lg p-8 text-center">
            <BarChart3 className="w-12 h-12 text-primary mx-auto mb-4" />
            <h3 className="text-xl font-bold text-foreground mb-2">
              Analytics
            </h3>
            <p className="text-muted-foreground mb-6">
              View detailed analytics and insights
            </p>
            <button
              disabled
              className="inline-flex items-center gap-2 px-6 py-2 bg-muted text-muted-foreground rounded-lg cursor-not-allowed font-medium"
            >
              Coming Soon
            </button>
          </div>
        </div>

        {/* Recent Articles */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-bold text-foreground mb-4">
            Quick Links
          </h2>
          <div className="space-y-2">
            <Link
              href="/admin/articles"
              className="block px-4 py-3 rounded-lg text-primary hover:bg-muted transition-colors font-medium"
            >
              → View All Articles
            </Link>
            <Link
              href="/admin/articles/new"
              className="block px-4 py-3 rounded-lg text-primary hover:bg-muted transition-colors font-medium"
            >
              → Create New Article
            </Link>
            <Link
              href="/"
              className="block px-4 py-3 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors font-medium"
            >
              → Back to Home
            </Link>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
