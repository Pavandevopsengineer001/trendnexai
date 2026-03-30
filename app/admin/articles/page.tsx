'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import AdminLayout from '@/components/AdminLayout';
import { Plus, Search, Loader, Trash2, Archive, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface Article {
  _id: string;
  title: string;
  category: string;
  status: 'draft' | 'published' | 'archived';
  views: number;
  created_at: string;
  slug: string;
}

export default function AdminArticlesPage() {
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [filter, setFilter] = useState<'all' | 'draft' | 'published' | 'archived'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState('');
  const [publishingId, setPublishingId] = useState('');

  useEffect(() => {
    fetchArticles();
  }, [filter]);

  async function fetchArticles() {
    try {
      setLoading(true);
      setError('');

      const token = localStorage.getItem('admin_token');
      if (!token) {
        router.push('/admin/login');
        return;
      }

      const query = filter === 'all' ? '' : `?status=${filter}`;
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/articles${query}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/admin/login');
          return;
        }
        throw new Error('Failed to fetch articles');
      }

      const data = await response.json();
      setArticles(data.items || []);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to load articles. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function deleteArticle(id: string) {
    if (!window.confirm('Are you sure you want to delete this article?')) return;

    try {
      setDeletingId(id);
      const token = localStorage.getItem('admin_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/articles/${id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Delete failed');

      setArticles(articles.filter((a) => a._id !== id));
    } catch (err) {
      console.error('Delete error:', err);
      alert('Failed to delete article');
    } finally {
      setDeletingId('');
    }
  }

  async function publishArticle(id: string) {
    try {
      setPublishingId(id);
      const token = localStorage.getItem('admin_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/articles/${id}/status`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status_value: 'published' }),
        }
      );

      if (!response.ok) throw new Error('Publish failed');

      fetchArticles();
    } catch (err) {
      console.error('Publish error:', err);
      alert('Failed to publish article');
    } finally {
      setPublishingId('');
    }
  }

  async function archiveArticle(id: string) {
    try {
      setPublishingId(id);
      const token = localStorage.getItem('admin_token');

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/articles/${id}/status`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status_value: 'archived' }),
        }
      );

      if (!response.ok) throw new Error('Archive failed');

      fetchArticles();
    } catch (err) {
      console.error('Archive error:', err);
      alert('Failed to archive article');
    } finally {
      setPublishingId('');
    }
  }

  const filteredArticles = articles.filter((article) =>
    article.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const statusCounts = {
    all: articles.length,
    draft: articles.filter((a) => a.status === 'draft').length,
    published: articles.filter((a) => a.status === 'published').length,
    archived: articles.filter((a) => a.status === 'archived').length,
  };

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-foreground">Articles</h1>
            <p className="text-muted-foreground mt-1">Manage and publish articles</p>
          </div>
          <Link
            href="/admin/articles/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            <Plus size={20} />
            New Article
          </Link>
        </div>

        {/* Search */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 border-b border-border overflow-x-auto pb-4">
          {(['all', 'draft', 'published', 'archived'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                filter === status
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
              <span className="ml-2 text-sm">({statusCounts[status]})</span>
            </button>
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Articles List */}
        {loading && articles.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-muted-foreground animate-spin" />
          </div>
        ) : filteredArticles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No articles found</p>
          </div>
        ) : (
          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted border-b border-border">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Title</th>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Category</th>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Status</th>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Views</th>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Created</th>
                  <th className="px-6 py-3 text-left font-semibold text-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredArticles.map((article) => (
                  <tr key={article._id} className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-foreground max-w-xs truncate">
                      <Link
                        href={`/admin/articles/${article._id}`}
                        className="text-primary hover:underline"
                      >
                        {article.title}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{article.category}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {article.status === 'published' && (
                          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-100 rounded-full text-xs font-semibold">
                            <CheckCircle size={14} />
                            Published
                          </div>
                        )}
                        {article.status === 'draft' && (
                          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-100 rounded-full text-xs font-semibold">
                            <Clock size={14} />
                            Draft
                          </div>
                        )}
                        {article.status === 'archived' && (
                          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-100 rounded-full text-xs font-semibold">
                            <Archive size={14} />
                            Archived
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{article.views || 0}</td>
                    <td className="px-6 py-4 text-muted-foreground text-xs">
                      {new Date(article.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2 flex-wrap">
                        <Link
                          href={`/admin/articles/${article._id}`}
                          className="text-primary hover:underline text-xs font-medium"
                        >
                          Edit
                        </Link>
                        {article.status === 'draft' && (
                          <button
                            onClick={() => publishArticle(article._id)}
                            disabled={publishingId === article._id}
                            className="text-green-600 hover:text-green-700 text-xs font-medium disabled:opacity-50"
                          >
                            {publishingId === article._id ? 'Publishing...' : 'Publish'}
                          </button>
                        )}
                        {article.status !== 'archived' && (
                          <button
                            onClick={() => archiveArticle(article._id)}
                            disabled={publishingId === article._id}
                            className="text-orange-600 hover:text-orange-700 text-xs font-medium disabled:opacity-50"
                          >
                            Archive
                          </button>
                        )}
                        <button
                          onClick={() => deleteArticle(article._id)}
                          disabled={deletingId === article._id}
                          className="text-destructive hover:text-destructive/80 text-xs font-medium disabled:opacity-50"
                        >
                          {deletingId === article._id ? 'Deleting...' : 'Delete'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
