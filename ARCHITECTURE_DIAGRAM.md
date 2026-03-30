# 🎯 TrendNexAI v2.0 - Architecture & System Design

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRENDNEXAI SYSTEM ARCHITECTURE                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      DATA SOURCES LAYER                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  RSS Feeds                    NewsAPI                            │
│  ├─ Ars Technica             ├─ Technology              
│  ├─ The Verge                ├─ Business
│  ├─ TechCrunch               ├─ Science
│  ├─ Product Hunt             ├─ General
│  ├─ Nature                   └─ ... 30+ countries
│  └─ ... 20+ feeds
│                                                                   │
└────────────┬─────────────────────────────────┬──────────────────┘
             │                                 │
          Every 30 mins                   Manual trigger
             │                                 │
┌────────────▼─────────────────────────────────▼──────────────────┐
│                   NEWS FETCHER SERVICE                           │
│  (app/news_api.py - NewsFetcher class)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Fetch articles from multiple sources concurrently           │
│     ├─ async_gather() for parallel processing                   │
│     ├─ 30 second timeout per source                             │
│     └─ Error recovery (continue if one fails)                   │
│                                                                   │
│  2. Content extraction                                           │
│     ├─ Title, summary, full content                             │
│     ├─ Author, publication date                                 │
│     ├─ Source URL, category                                     │
│     └─ Image detection & extraction                             │
│                                                                   │
│  3. Deduplication (3-level)                                      │
│     ├─ Level 1: URL fingerprint (fast)                          │
│     ├─ Level 2: Content MD5 hash                                │
│     └─ Level 3: Database lookup                                 │
│                                                                   │
│  Output: 100-200 unique articles per run                        │
│                                                                   │
└────────────┬──────────────────────────────────────────────────┬─┘
             │                                                  │
        Raw Articles                                     Error Logs
             │
┌────────────▼──────────────────────────────────────────────────┐
│              AI PROCESSING ENGINE                              │
│  (app/openai_service.py - AIContentGenerator class)           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  FOR EACH ARTICLE:                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1. KEYWORD EXTRACTION                                  │ │
│  │    ├─ Extract 5-6 main keywords                        │ │
│  │    ├─ Filter stop words                                │ │
│  │    └─ Focus on content-specific terms                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 2. SEO OPTIMIZED TITLE (OpenAI)                        │ │
│  │    ├─ 50-65 characters                                 │ │
│  │    ├─ Include primary keyword                          │ │
│  │    ├─ Add power word (How, Why, Best, etc.)           │ │
│  │    └─ Avoid clickbait                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 3. COMPELLING SUMMARY (OpenAI)                         │ │
│  │    ├─ 2-3 sentences, ~150 chars                        │ │
│  │    ├─ Include primary keyword                          │ │
│  │    ├─ Hook with curiosity                              │ │
│  │    └─ Call to action hint                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 4. FULL ARTICLE GENERATION (OpenAI)                    │ │
│  │    ├─ 800-900 words (±50)                              │ │
│  │    ├─ Authority-level content                          │
│  │    ├─ Proper H1/H2/H3 structure                       │ │
│  │    ├─ Zero plagiarism (100% rewritten)                 │ │
│  │    ├─ 5 core sections:                                 │ │
│  │    │  • Introduction (hook + relevance)                │ │
│  │    │  • Understanding topic (deep dive)                │ │
│  │    │  • Key implications (business impact)             │ │
│  │    │  • Real-world applications (examples)             │ │
│  │    │  • Future outlook (predictions)                   │ │
│  │    ├─ Keywords naturally integrated                    │ │
│  │    ├─ Active voice preferred                           │ │
│  │    └─ Statistics & data included                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 5. SEO META DESCRIPTION (OpenAI)                       │ │
│  │    ├─ 150-160 characters exactly                       │ │
│  │    ├─ Include keyword                                  │ │
│  │    ├─ Include call-to-action (Learn, Discover)        │ │
│  │    ├─ Click-worthy & compelling                        │ │
│  │    └─ For Google SERP display                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 6. SEO TAGS (OpenAI)                                   │ │
│  │    ├─ 5-8 tags optimal                                 │ │
│  │    ├─ Include category + keywords                      │ │
│  │    ├─ Single words or 2-word phrases                   │ │
│  │    ├─ Lowercase                                        │ │
│  │    └─ Popular search terms                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 7. AI INSIGHTS (OpenAI OR Claude 3.5)                  │ │
│  │    ├─ Why it matters (2-3 sentences on impact)         │ │
│  │    ├─ Key risks (3 main risks)                         │ │
│  │    ├─ Action items (3 recommendations)                 │ │
│  │    ├─ Key takeaways (3 memorable points)               │ │
│  │    ├─ Related tools (2-3 relevant products)            │ │
│  │    └─ Impact score (1-10 scale)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  CACHING: MD5(title+content) → instant on re-request          │
│  FALLBACK: If Claude fails, falls back to OpenAI              │
│  TIME: ~2-3 seconds per article total                         │
│                                                                │
└────────────┬──────────────────────────────────────────────────┘
             │
        Enhanced Articles with:
        ├─ Title + SEO title
        ├─ Summary + Meta description
        ├─ Full content (800+ words)
        ├─ Tags + Keywords
        └─ AI Insights (structured JSON)
             │
┌────────────▼──────────────────────────────────────────────────┐
│                   DATABASE LAYER                              │
│          (MongoDB with 10+ optimized indices)                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Save article document:                                       │
│  {                                                            │
│    "_id": ObjectId,                                          │
│    "title": "...",          "slug": "unique-key",           │
│    "summary": "...",        "content": {...},               │
│    "seo_title": "...",      "seo_description": "...",       │
│    "tags": [...],           "category": "technology",       │
│    "ai_insights": {...},    "ai_generated": true,           │
│    "status": "pending_review",  ← KEY: Waiting for review  │
│    "source_url": "...",     "image_url": "...",            │
│    "views": 0,              "engagement_score": 0,          │
│    "createdAt": ISODate,    "publishedAt": null,           │
│    "reviewed_by": null,     "reviewed_at": null,           │
│    "rejection_reason": null                                 │
│  }                                                            │
│                                                                │
│  INDICES CREATED:                                            │
│  ├─ slug (unique)  - URL-friendly lookup                     │
│  ├─ status  - Filter by state                                │
│  ├─ category - Browse by category                            │
│  ├─ createdAt - Sort by date                                 │
│  ├─ full-text - Search title/summary/tags                    │
│  ├─ status + createdAt - Published filtered by date           │
│  ├─ views - Trending articles                                │
│  ├─ source_url - Deduplication check                         │
│  └─ TTL - Auto-delete unpublished after 30 days             │
│                                                                │
│  COLLECTIONS:                                                │
│  ├─ articles (main content store)                            │
│  ├─ analytics (view tracking, events)                        │
│  └─ cache (optional, 1-hour TTL)                             │
│                                                                │
└────────────┬──────────────────────────────────────────────────┘
             │
      Articles with status:
      "pending_review"
             │
┌────────────▼──────────────────────────────────────────────────┐
│              ADMIN DASHBOARD / REVIEW SYSTEM                  │
│  (backend/app/admin_routes.py - Complete CRUD API)           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ADMIN CAPABILITIES:                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ LIST PENDING ARTICLES                                  │ │
│  │ GET /api/admin/articles/pending-review                 │ │
│  │ Shows: Title, summary, category, AI insights           │ │
│  │ Newest first, paginated                                │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ VIEW FULL ARTICLE                                       │ │
│  │ GET /api/admin/articles/{id}                           │ │
│  │ Shows: Complete content, all metadata, insights         │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ EDIT ARTICLE (if needed)                               │ │
│  │ PUT /api/admin/articles/{id}                           │ │
│  │ Can edit: Title, summary, tags, category               │ │
│  │ Can fix: Typos, errors, improve clarity                │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────┬──────────────────────┐ │
│  │ APPROVE FOR PUBLISHING            │ REJECT ARTICLE      │ │
│  │                                   │                     │ │
│  │ POST /api/admin/articles/{}/      │ POST /api/admin/    │ │
│  │      approve                      │ articles/{}/reject  │ │
│  │                                   │                     │ │
│  │ Changes status to: APPROVED       │ Changes status to:  │ │
│  │ Now ready to publish               │ REJECTED            │ │
│  │ Records who reviewed              │ Saves rejection     │ │
│  │ Records review timestamp          │ reason              │ │
│  └──────────────────────────────────┴──────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ PUBLISH TO LIVE SITE                                    │ │
│  │ POST /api/admin/articles/{id}/publish                  │ │
│  │ Changes status to: PUBLISHED                            │ │
│  │ Sets publishedAt timestamp                              │ │
│  │ Article now appears on homepage                         │ │
│  │ SEO indexed by search engines                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ VIEW STATISTICS                                         │ │
│  │ GET /api/admin/stats                                   │ │
│  │ ├─ Total articles count                                │ │
│  │ ├─ Breakdown by status                                 │ │
│  │ ├─ Breakdown by category                               │ │
│  │ ├─ Total views across all articles                     │ │
│  │ └─ Engagement metrics                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ BULK OPERATIONS                                         │ │
│  │ POST /api/admin/bulk-status-change                     │ │
│  │ ├─ Approve 10 articles at once                         │ │
│  │ ├─ Publish multiple articles                           │ │
│  │ ├─ Archive outdated content                            │ │
│  │ └─ Change category for many articles                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ MANUAL NEWS FETCH                                       │ │
│  │ POST /api/admin/fetch-news                             │ │
│  │ Manually trigger article fetch instead of waiting       │ │
│  │ Useful for urgent news stories                          │ │
│  │ Returns task ID for status tracking                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
└─────────────────┬─────────────────────────────────────┬───────┘
                  │                                     │
            Approved/Published                    Rejected/Archived
                  │                                     │
                  │                      (Saved for re-review if needed)
                  │
┌─────────────────▼─────────────────────────────────────┐
│         PUBLISHED ARTICLES LAYER                      │
│     (Status: "published" OR "approved")               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SEO-Optimized for Discovery:                        │
│  ├─ Proper H1/H2 structure                           │
│  ├─ Meta description in HTML head                    │
│  ├─ Keywords naturally distributed                  │
│  ├─ Internal links to related articles               │
│  ├─ Image alt text for accessibility                │
│  └─ Schema.org structured data for rich snippets     │
│                                                        │
│  Caching Strategy:                                    │
│  ├─ Redis cache (60 seconds)                         │
│  ├─ Browser cache (300 seconds)                      │
│  └─ CDN caching (1 hour)                             │
│                                                        │
│  Analytics Tracking:                                  │
│  ├─ View counter incremented                        │
│  ├─ Engagement score calculated                      │
│  ├─ Events logged to analytics collection            │
│  └─ Trends identified (trending articles)            │
│                                                        │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│         FRONTEND / PUBLIC DISPLAY                    │
│      (Next.js - React Components)                   │
├────────────────────────────────────────────────────┤
│                                                     │
│  Homepage                                          │
│  ├─ Featured articles (trending)                   │
│  ├─ Latest by category                             │
│  ├─ AI insights preview                            │
│  └─ "Read more" links to full articles             │
│                                                     │
│  Article Detail Page                               │
│  ├─ Full H1/H2 structured content                  │
│  ├─ AI insights sidebar                            │
│  ├─ Related articles suggestions                   │
│  ├─ Author & source attribution                    │
│  └─ View counter & engagement                      │
│                                                     │
│  Category Browse                                    │
│  ├─ All articles in category                       │
│  ├─ Filtered & sorted by date                      │
│  ├─ Pagination support                             │
│  └─ View analytics                                 │
│                                                     │
│  Search                                             │
│  ├─ Full-text search across all articles           │
│  ├─ Instant results (powered by MongoDB)           │
│  └─ Faceted filtering (category, date, author)     │
│                                                     │
└──────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────┐
│  EXTERNAL DATA SOURCES                          │
│  (RSS + NewsAPI)                                │
└────────────────┬────────────────────────────────┘
                 │
                 │ Fetch every 30 mins
                 │ (Celery Beat Scheduler)
                 │
                 ▼
        ┌────────────────────────┐
        │  News Fetcher Service  │
        │  • Get raw articles    │
        │  • Extract metadata    │
        │  • Detect duplicates   │
        └────────────┬───────────┘
                     │
                     │ 100-200 unique raw articles
                     │
                     ▼
        ┌────────────────────────┐
        │  AI Processing Engine  │
        │  • Content rewrite     │
        │  • Title optimization  │
        │  • Insights generation │
        │  • SEO meta creation   │
        └────────────┬───────────┘
                     │
                     │ Enhanced article with insights
                     │
                     ▼
        ┌────────────────────────┐
        │  MongoDB Storage       │
        │  Status: pending_review│
        │  • Indexed for speed   │
        │  • Analytics tracked   │
        │  • Cache invalidated   │
        └────────────┬───────────┘
                     │
                     │ Admin notification (optional)
                     │
              ┌──────┴──────┐
              │             │
              ▼             ▼
        ┌───────────┐  ┌──────────┐
        │  APPROVE  │  │  REJECT  │
        │    ✓      │  │    ✗     │
        └─────┬─────┘  └──────────┘
              │
              │ Status: approved
              │
              ▼
        ┌────────────────────────┐
        │    PUBLISH ARTICLE     │
        │  • Set publishedAt    │
        │  • Status: published  │
        │  • Cache entry updated│
        └────────────┬───────────┘
                     │
                     │ SEO-optimized, live content
                     │
                     ▼
        ┌────────────────────────┐
        │  FRONTEND DISPLAY      │
        │  • Homepage            │
        │  • Article page        │
        │  • Category browse     │
        │  • Search results      │
        └────────────┬───────────┘
                     │
                     │ User views article
                     │
                     ▼
        ┌────────────────────────┐
        │  ANALYTICS TRACKING    │
        │  • View counter        │
        │  • Engagement score    │
        │  • Trending detection  │
        │  • Performance metrics │
        └────────────────────────┘
```

---

## 📊 Status Workflow Diagram

```
Raw Article
   │
   ├──> [save to DB] ──> Status: pending_review
   │                           │
   │                     ┌─────┴─────┐
   │                     │           │
   │           (Admin Reviews)       │
   │                     │           │
   │         ┌───────────┴────┬──────┴───────┐
   │         │                │              │
   │         ▼                ▼              ▼
   │     APPROVED        REJECTED         EDITED
   │         │                │              │
   │         │           (save reason)       │
   │         │                │              │
   │         │           Status:          (save changes)
   │         │           rejected           │
   │         │                │              │
   │         │         (for re-review)      │
   │         │                              │
   │         └──────────────┬───────────────┘
   │                        │
   │                  Status: approved
   │                        │
   │              (Admin clicks PUBLISH)
   │                        │
   │            ┌───────────▼──────────┐
   │            │                      │
   │            ▼                      ▼
   │       PUBLISHED          NEEDS UPDATES
   │            │              (edit again)
   │            │                      │
   │      Status: published            │
   │      publishedAt: now      (repeat workflow)
   │            │
   │      ┌─────┴─────┐
   │      │           │
   │      ▼           ▼
   │   LIVE on    Appears in
   │   Homepage   Archives
   │      │           │
   │      └─────┬─────┘
   │            │
   │   View tracking
   │   Analytics
   │   Trending detection
   │
   └─────> [After 30 days]
          Auto-archive/delete (optional TTL)
```

---

## 📦 Component Architecture

```
FastAPI Application
├── MIDDLEWARE
│   ├── RateLimitMiddleware (100 req/min)
│   ├── LoggingMiddleware (all requests)
│   ├── CORSMiddleware (cross-origin)
│   └── ErrorHandler (exception management)
│
├── ROUTES
│   ├── Public API (/api)
│   │   ├── GET /articles - List published
│   │   ├── GET /articles/{slug} - Details
│   │   ├── GET /articles/related - Related
│   │   ├── GET /categories - All cats
│   │   └── POST /analytics/view - Tracking
│   │
│   └── Admin API (/api/admin) [protected]
│       ├── GET /articles - List all
│       ├── GET /articles/pending-review - Pending
│       ├── POST /articles/{id}/approve - Approve
│       ├── POST /articles/{id}/reject - Reject
│       ├── POST /articles/{id}/publish - Publish
│       ├── PUT /articles/{id} - Edit
│       ├── DELETE /articles/{id} - Delete
│       ├── POST /bulk-status-change - Bulk ops
│       ├── GET /stats - Statistics
│       ├── POST /fetch-news - Manual fetch
│       └── GET /fetch-news/status/{id} - Task status
│
├── SERVICES
│   ├── NewsApi (news_api.py)
│   │   ├── NewsFetcher - Async fetching
│   │   ├── ArticleFingerprint - Deduplication
│   │   └── ArticleDeduplicator - History tracking
│   │
│   ├── AIContent (openai_service.py)
│   │   ├── AIContentGenerator
│   │   │   ├─ generate_article(title, content, category)
│   │   │   └─ _generate_ai_insights(... + use_claude)
│   │   ├── OpenAI integration
│   │   └─ Claude integration (fallback)
│   │
│   └── ArticleServices (services.py)
│       ├── save_articles_async() - Batch save
│       ├── approve_article() - Mark approved
│       ├── reject_article() - Mark rejected
│       ├── publish_article() - Go live
│       ├── get_articles_awaiting_review() - Pending list
│       ├── bulk_status_change() - Bulk update
│       └─ get_article_stats() - Analytics
│
├── SECURITY
│   ├── JWT Authentication (PyJWT)
│   ├── Role-based Authorization (admin, editor)
│   ├── Password hashing (bcrypt)
│   └─ HTTPS/SSL support
│
└── INFRASTRUCTURE
    ├── MongoDB (data persistence)
    ├── Redis (caching + task queue)
    ├── Celery (background jobs)
    ├── APScheduler (cron tasks)
    └─ Docker (containerization)
```

---

## 🎯 What Makes This Production-Ready

### 1. **Scalability**
- Async/await for concurrency
- Database sharding support
- Horizontal scaling with Celery
- Load balancing ready

### 2. **Reliability**
- Error handling & recovery
- Graceful degradation
- Fallback strategies
- Logging & monitoring

### 3. **Performance**
- Caching layer (Redis)
- Database indices
- Query optimization
- Connection pooling

### 4. **Security**
- JWT authentication
- Role-based access control
- Input validation
- Rate limiting

### 5. **Maintainability**
- Clean code structure
- Comprehensive documentation
- Clear separation of concerns
- Consistent patterns

### 6. **Observability**
- Structured logging
- Request tracing
- Error tracking
- Performance metrics

---

**This is a complete, production-grade system ready for deployment! 🚀**
