/**
 * Category configuration system
 * Defines all categories with their colors, icons, and metadata
 */

export interface Category {
  id: string;
  label: string;
  description: string;
  icon: string;
  color: string;
  bgColor: string;
  borderColor: string;
  badgeClass: string;
  gradient: string;
  href: string;
}

export const CATEGORIES: Record<string, Category> = {
  technology: {
    id: 'technology',
    label: 'Technology',
    description: 'Latest in tech, AI, and innovation',
    icon: '💻',
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    badgeClass: 'badge-technology',
    gradient: 'from-blue-500 to-blue-600',
    href: '/category/technology',
  },
  business: {
    id: 'business',
    label: 'Business',
    description: 'Markets, startups & enterprise',
    icon: '💼',
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
    borderColor: 'border-purple-200 dark:border-purple-800',
    badgeClass: 'badge-business',
    gradient: 'from-purple-500 to-purple-600',
    href: '/category/business',
  },
  sports: {
    id: 'sports',
    label: 'Sports',
    description: 'Games, athletes & competition',
    icon: '⚽',
    color: 'text-rose-600 dark:text-rose-400',
    bgColor: 'bg-rose-50 dark:bg-rose-900/20',
    borderColor: 'border-rose-200 dark:border-rose-800',
    badgeClass: 'badge-sports',
    gradient: 'from-rose-500 to-rose-600',
    href: '/category/sports',
  },
  health: {
    id: 'health',
    label: 'Health',
    description: 'Wellness, medicine & fitness',
    icon: '🏥',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
    badgeClass: 'badge-health',
    gradient: 'from-green-500 to-green-600',
    href: '/category/health',
  },
};

export const CATEGORY_ARRAY = Object.values(CATEGORIES);

export function getCategoryById(id: string): Category | undefined {
  return CATEGORIES[id.toLowerCase()];
}

export function getCategoryColor(categoryId: string): string {
  const category = getCategoryById(categoryId);
  return category?.color || 'text-gray-600';
}

export function getCategoryBadgeClass(categoryId: string): string {
  const category = getCategoryById(categoryId);
  return category?.badgeClass || 'badge-muted';
}

export function getCategoryGradient(categoryId: string): string {
  const category = getCategoryById(categoryId);
  return category?.gradient || 'from-gray-500 to-gray-600';
}
