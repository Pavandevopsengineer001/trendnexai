'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { LogOut, Menu, X, FileText, Home, Settings } from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('admin_token');
    if (!token) {
      router.push('/admin/login');
    } else {
      setIsAuthenticated(true);
      setLoading(false);
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    router.push('/admin/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const isActive = (href: string) => pathname === href || pathname.startsWith(href);

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-muted border-r border-border transition-all duration-300 flex flex-col fixed h-screen md:relative`}
      >
        {/* Logo Area */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <h1 className={`font-bold text-lg transition-opacity ${isSidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
              Admin
            </h1>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-background rounded-lg md:hidden"
            >
              {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-4 space-y-2">
          <Link
            href="/admin"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/admin') && pathname === '/admin'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-background'
            }`}
          >
            <Home size={20} />
            {isSidebarOpen && <span>Dashboard</span>}
          </Link>

          <Link
            href="/admin/articles"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/admin/articles')
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-background'
            }`}
          >
            <FileText size={20} />
            {isSidebarOpen && <span>Articles</span>}
          </Link>

          <Link
            href="/admin/settings"
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              isActive('/admin/settings')
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-background'
            }`}
          >
            <Settings size={20} />
            {isSidebarOpen && <span>Settings</span>}
          </Link>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-border">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-destructive hover:bg-destructive/10 transition-colors"
          >
            <LogOut size={20} />
            {isSidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Header */}
        <div className="sticky top-0 z-40 bg-background border-b border-border px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-muted rounded-lg hidden md:block"
          >
            <Menu size={20} />
          </button>
          <div className="flex-1" />
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>

        {/* Page Content */}
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
