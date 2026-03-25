# TrendNexAI - Developer Reference Guide

## 🗺️ Project Structure

```
trendnexai/
├── app/                          # Next.js app directory
│   ├── layout.tsx               # Root layout with ThemeProvider
│   ├── globals.css              # Design system (CSS variables)
│   ├── page.tsx                 # Homepage (use EXAMPLE_HOMEPAGE.tsx)
│   ├── api/                     # Route handlers
│   ├── article/[slug]/page.tsx # Article detail (use EXAMPLE_ARTICLE_PAGE.tsx)
│   ├── category/[category]/    # Category pages (use EXAMPLE_CATEGORY_PAGE.tsx)
│   ├── about/page.tsx          # About page
│   ├── contact/page.tsx        # Contact page
│   ├── privacy/page.tsx        # Privacy page
│   └── terms/page.tsx          # Terms page
│
├── components/                  # React components
│   ├── Header.tsx              # Sticky navigation ✅ UPDATED
│   ├── Footer.tsx              # Dynamic footer ✅ UPDATED
│   ├── HeroSection.tsx         # Hero banner ✅ NEW
│   ├── TrendingSection.tsx     # Trending carousel ✅ NEW
│   ├── CategorySection.tsx     # Category sections ✅ NEW
│   ├── CategoryPageHeader.tsx  # Category header ✅ NEW
│   ├── CategoryRelated.tsx     # Related articles ✅ NEW
│   ├── ArticleCard.tsx         # Article card ✅ UPDATED
│   ├── ArticleContent.tsx      # Article display
│   ├── SkeletonCard.tsx        # Loading skeleton ✅ UPDATED
│   ├── EmptyState.tsx          # Empty state ✅ UPDATED
│   ├── ErrorState.tsx          # Error state ✅ UPDATED
│   ├── ThemeToggle.tsx         # Dark/light toggle
│   ├── AdUnit.tsx              # Ad unit
│   ├── RelatedArticles.tsx     # Related articles
│   └── ui/                     # Radix UI components
│
├── lib/                        # Utilities & helpers
│   ├── categories.ts           # Category system ✅ NEW
│   ├── api.ts                  # API client
│   ├── mongodb.ts              # MongoDB connection
│   ├── news.ts                 # News utilities
│   ├── openai.ts               # OpenAI utilities
│   └── utils.ts                # Helper functions
│
├── public/                     # Static assets
│   ├── icon.svg
│   └── apple-icon.png
│
├── backend/                    # Python backend
│   ├── app/
│   │   ├── main.py
│   │   ├── security.py
│   │   ├── middleware.py
│   │   └── [other modules]
│   └── requirements.txt
│
├── scripts/                    # Utility scripts
│   ├── deploy.sh
│   ├── health-check.sh
│   └── setup.sh
│
├── package.json               # Frontend dependencies
├── tsconfig.json              # TypeScript config
├── tailwind.config.js         # Tailwind CSS config
├── next.config.js             # Next.js config
│
└── Documentation files:
    ├── UI_REDESIGN_GUIDE.md        # Design system guide
    ├── REDESIGN_SUMMARY.md         # Complete summary
    ├── EXAMPLE_HOMEPAGE.tsx        # Homepage template
    ├── EXAMPLE_CATEGORY_PAGE.tsx   # Category template
    ├── EXAMPLE_ARTICLE_PAGE.tsx    # Article template
    └── [other docs]
```

---

## 🎨 Design System (CSS Variables)

Located in: **app/globals.css**

### Light Mode Variables
```css
--background: 255 255 255           /* #ffffff */
--foreground: 15 23 42              /* #0f172a */
--card: 255 255 255                 /* #ffffff */
--border: 229 231 235               /* #e5e7eb */
--muted: 243 244 246                /* #f3f4f6 */
--muted-foreground: 107 114 128     /* #6b7280 */
--primary: 37 99 235                /* #2563eb */
--secondary: 249 115 22             /* #f97316 */
--success: 34 197 94                /* #22c55e */
--warning: 234 179 8                /* #eab308 */
--destructive: 239 68 68            /* #ef4444 */
```

### Dark Mode Variables
Automatically applied when `html.dark` or system preference is dark

### Category Colors
```
Technology: #3b82f6 (Blue)
Business:   #8b5cf6 (Purple)
Sports:     #f43f5e (Rose)
Health:     #10b981 (Green)
```

---

## 📦 Component Library

### Header
**File**: `components/Header.tsx`
**Props**: None (reads URL pathname)
**Features**:
- Sticky positioning
- Category dropdown
- Search bar (desktop & mobile)
- Notifications button
- Theme toggle
- Mobile hamburger menu

**Usage**:
```tsx
import Header from '@/components/Header';
export default function Page() {
  return (
    <>
      <Header />
      <main>{/* content */}</main>
    </>
  );
}
```

### Footer
**File**: `components/Footer.tsx`
**Props**: None (uses CATEGORY_ARRAY)
**Features**:
- Dynamic category links
- Newsletter signup
- Social media links
- Responsive grid

**Usage**:
```tsx
import Footer from '@/components/Footer';
export default function Page() {
  return (
    <>
      <main>{/* content */}</main>
      <Footer />
    </>
  );
}
```

### HeroSection
**File**: `components/HeroSection.tsx`
**Props**:
```tsx
interface HeroSectionProps {
  featuredArticle?: any;
  loading?: boolean;
}
```

**Usage**:
```tsx
<HeroSection 
  featuredArticle={articles[0]} 
  loading={isLoading} 
/>
```

### TrendingSection
**File**: `components/TrendingSection.tsx`
**Props**:
```tsx
interface TrendingSectionProps {
  articles: any[];
  loading?: boolean;
}
```

**Usage**:
```tsx
<TrendingSection 
  articles={articles.slice(1, 6)} 
  loading={isLoading} 
/>
```

### CategorySection
**File**: `components/CategorySection.tsx`
**Props**:
```tsx
interface CategorySectionProps {
  category: Category;
  articles: any[];
  loading?: boolean;
  showFeatured?: boolean;
}
```

**Usage**:
```tsx
<CategorySection
  category={CATEGORIES.technology}
  articles={techArticles}
  loading={isLoading}
  showFeatured={true}
/>
```

### ArticleCard
**File**: `components/ArticleCard.tsx`
**Props**:
```tsx
interface ArticleCardProps {
  article: {
    _id: string;
    title: string;
    slug: string;
    summary: string;
    category: string;
    image_url?: string;
    tags: string[];
    createdAt: string;
    source_url?: string;
  };
}
```

**Features**:
- Category badge
- Image with hover effect
- Title, summary, date
- Tags display
- "Read More" link
- External link button

### SkeletonCard
**File**: `components/SkeletonCard.tsx`
**Props**: None
**Usage**: Use during loading state
```tsx
{loading ? (
  <>
    {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
  </>
) : (
  articles.map(a => <ArticleCard key={a._id} article={a} />)
)}
```

### EmptyState
**File**: `components/EmptyState.tsx`
**Props**:
```tsx
interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  icon?: string;  // emoji or path
}
```

### ErrorState
**File**: `components/ErrorState.tsx`
**Props**:
```tsx
interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  showHomeLink?: boolean;
}
```

### CategoryPageHeader
**File**: `components/CategoryPageHeader.tsx`
**Props**:
```tsx
interface CategoryPageHeaderProps {
  category: Category;
  articleCount?: number;
  currentFilter?: string;
  onFilterChange?: (filter: string) => void;
}
```

### CategoryRelated
**File**: `components/CategoryRelated.tsx`
**Props**:
```tsx
interface RelatedArticlesProps {
  articles: any[];
  currentArticleId?: string;
  limit?: number;
  title?: string;
}
```

---

## 📚 Category System

**File**: `lib/categories.ts`

### Category Interface
```typescript
interface Category {
  id: string;
  label: string;
  description: string;
  icon: string;
  color: string;        // Tailwind class
  bgColor: string;      // Tailwind class
  borderColor: string;  // Tailwind class
  badgeClass: string;   // CSS class name
  gradient: string;     // Tailwind gradient
  href: string;         // Route path
}
```

### Available Categories
- `technology` - 💻 Tech blue
- `business` - 💼 Business purple  
- `sports` - ⚽ Sports rose
- `health` - 🏥 Health green

### Helper Functions
```typescript
getCategoryById(id: string): Category
getCategoryColor(categoryId: string): string
getCategoryBadgeClass(categoryId: string): string
getCategoryGradient(categoryId: string): string
```

### Usage
```tsx
import { getCategoryById, CATEGORY_ARRAY } from '@/lib/categories';

// Get single category
const category = getCategoryById('technology');

// Loop all categories
CATEGORY_ARRAY.forEach(cat => {
  console.log(cat.label);
});
```

---

## 🎯 CSS Classes Reference

### Components
```css
.card                  /* Base card style */
.card-hover           /* Card with hover effects */
.card-interactive     /* Clickable card */
.card-premium         /* Premium featured card */
.card-featured        /* Featured with ring border */

.btn-primary          /* Filled primary button */
.btn-secondary        /* Filled secondary button */
.btn-outline          /* Outlined button */
.btn-ghost            /* Ghost/transparent button */
.btn-sm               /* Small button */
.btn-lg               /* Large button */

.badge                /* Base badge */
.badge-primary        /* Primary badge */
.badge-secondary      /* Secondary badge */
.badge-success        /* Success state badge */
.badge-warning        /* Warning state badge */
.badge-destructive    /* Error state badge */
.badge-muted          /* Muted badge */
.badge-outline        /* Outline badge */
.badge-technology     /* Tech category */
.badge-business       /* Business category */
.badge-sports         /* Sports category */
.badge-health         /* Health category */
```

### Layout
```css
.section-spacing      /* py-12 md:py-16 lg:py-20 */
.section-spacing-sm   /* py-8 md:py-12 */
.container-spacing    /* px-4 sm:px-6 lg:px-8 */
.container-max        /* max-w-7xl mx-auto */
.container-max-lg     /* max-w-4xl mx-auto */

.grid-auto-fit        /* Responsive auto-fit grid */
.grid-auto-fit-sm     /* Responsive with smaller min */
.articles-grid        /* 3-column article grid */

.flex-center          /* flex + center alignment */
.flex-between         /* flex + space-between */
```

### Typography
```css
.line-clamp-1         /* Single line truncate */
.line-clamp-2         /* 2-line truncate */
.line-clamp-3         /* 3-line truncate */
.line-clamp-4         /* 4-line truncate */

.text-muted           /* Muted foreground color */
.text-subtle          /* Muted + small size */
.text-xs-subtle       /* Muted + extra small */
```

### Animations
```css
.animate-fade-up      /* Fade + slide up */
.animate-fade-in      /* Simple fade in */
.animate-fade-in-delay /* Delayed fade */
.animate-scale-in     /* Scale from small */
.animate-slide-in-left /* Slide from left */
.animate-slide-in-right /* Slide from right */
.animate-bounce-subtle /* Subtle bounce */
.animate-pulse-soft   /* Soft pulsing */
```

---

## 🔧 Common Implementation Patterns

### Loading with Skeleton
```tsx
{loading ? (
  <div className="articles-grid">
    {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
  </div>
) : articles.length > 0 ? (
  <div className="articles-grid">
    {articles.map(a => <ArticleCard key={a._id} article={a} />)}
  </div>
) : (
  <EmptyState title="No articles found" />
)}
```

### Error Handling
```tsx
if (error) {
  return (
    <ErrorState 
      message={error}
      onRetry={() => refetch()}
      showHomeLink={true}
    />
  );
}
```

### Pagination
```tsx
{hasMore && (
  <div className="flex justify-center mt-12">
    <button 
      onClick={loadMore}
      disabled={isLoadingMore}
      className="btn-primary px-8 py-3 rounded-lg"
    >
      Load More
    </button>
  </div>
)}
```

### Responsive Grid
```tsx
<div className="articles-grid">
  {/* Auto-responsive: 1 col mobile → 2 tablet → 3 desktop */}
  {articles.map(a => <ArticleCard key={a._id} article={a} />)}
</div>

// Or custom grid:
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* Content */}
</div>
```

---

## 🚀 Page Templates

### Homepage (`app/page.tsx`)
Use **EXAMPLE_HOMEPAGE.tsx** as template. Includes:
- Header
- HeroSection (with featured article)
- TrendingSection
- Multiple CategorySections
- CTA section
- Footer

### Category Page (`app/category/[category]/page.tsx`)
Use **EXAMPLE_CATEGORY_PAGE.tsx** as template. Includes:
- Header
- CategoryPageHeader (with filters)
- Articles grid
- Pagination
- Related categories
- Footer

### Article Page (`app/article/[slug]/page.tsx`)
Use **EXAMPLE_ARTICLE_PAGE.tsx** as template. Includes:
- Header
- Article content
- Category badge
- Share buttons
- Related articles
- Newsletter CTA
- Footer

---

## 📱 Responsive Breakpoints

```
Mobile: 360px (default)
sm:     640px (tablets)
md:     768px (small desktops)
lg:     1024px (desktops)
xl:     1280px (large screens)
2xl:    1536px (very large screens)
```

**Usage**:
```tsx
<div className="block md:hidden">Mobile only</div>
<div className="hidden md:block">Desktop only</div>
<div className="grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  Responsive grid
</div>
```

---

## 🎓 Best Practices

### 1. Component Composition
Keep components small and focused. Combine them for complex UIs.

### 2. Type Safety
Use TypeScript interfaces for all props.

### 3. Error Handling
Always show EmptyState or ErrorState to users.

### 4. Loading States
Use SkeletonCard during data fetching.

### 5. Accessibility
- Use semantic HTML
- Add ARIA labels
- Test keyboard navigation
- Ensure color contrast

### 6. Performance
- Lazy load images
- Code split pages
- Memoize expensive components
- Use React DevTools Profiler

### 7. Dark Mode
Test all components in both light and dark modes.

### 8. Mobile Testing
Test on actual mobile devices, not just DevTools.

---

## 🧪 Testing Components

### Manual Testing Checklist
- [ ] Light mode appearance
- [ ] Dark mode appearance
- [ ] Mobile responsive (all breakpoints)
- [ ] Tablet responsive (md breakpoint)
- [ ] Desktop responsive (lg/xl breakpoints)
- [ ] Hover effects working
- [ ] Focus states visible
- [ ] Animations smooth
- [ ] Links functional
- [ ] Forms working
- [ ] Loading states showing
- [ ] Error states showing
- [ ] Images loading
- [ ] Accessibility with keyboard

---

## 📊 Performance Tips

1. **Images**
   - Use Next.js Image component
   - Set width/height
   - Use lazy loading
   - Optimize image sizes

2. **JavaScript**
   - Code split pages
   - Dynamic imports for large components
   - Memoize expensive renders
   - Minimize bundle size

3. **CSS**
   - Use CSS variables for theming
   - Minimize media queries
   - Use Tailwind purging
   - Avoid inline styles

4. **Animations**
   - Use CSS animations (not JS)
   - Respect prefers-reduced-motion
   - Use will-change sparingly
   - Test FPS in DevTools

---

## 🆘 Common Issues & Solutions

### Issue: Components not styled
**Solution**: Ensure Tailwind CSS is properly configured and watching CSS files.

### Issue: Dark mode not working
**Solution**: Check ThemeProvider in layout.tsx and CSS variables in globals.css.

### Issue: Layout broken on mobile
**Solution**: Review responsive classes - use `hidden md:flex` pattern correctly.

### Issue: Images stretched
**Solution**: Add `object-cover` and set explicit width/height.

### Issue: Slow animations
**Solution**: Check DevTools performance, reduce animation complexity.

---

## 📞 Quick Links

- **Design System**: UI_REDESIGN_GUIDE.md
- **Implementation**: REDESIGN_SUMMARY.md
- **Homepage Example**: EXAMPLE_HOMEPAGE.tsx
- **Category Example**: EXAMPLE_CATEGORY_PAGE.tsx
- **Article Example**: EXAMPLE_ARTICLE_PAGE.tsx
- **Categories Config**: lib/categories.ts
- **CSS Variables**: app/globals.css

---

Last Updated: March 2026
Version: 1.0
