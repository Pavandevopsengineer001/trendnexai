# 🏗️ TrendNexAI Project Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Next.js Frontend (React + TypeScript)            │  │
│  │  - Public Article Pages & Category Browsing              │  │
│  │  - Admin Dashboard (Protected Routes)                    │  │
│  │  - Real-time SEO Meta Tags                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────▼──────────────────────────────────────────┐
│                  API Gateway Layer (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  JWT Authentication │ Rate Limiting │ Error Handling     │  │
│  │  CORS Middleware    │ Input Validation │ Logging        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
         ┌─────────────┼─────────────┬──────────────┐
         │             │             │              │
    ┌────▼──┐   ┌─────▼──┐  ┌──────▼────┐  ┌─────▼──┐
    │  News │   │   AI   │  │ Admin API │  │ Public │
    │ Fetch │   │Content │  │  Routes   │  │ Routes │
    └────┬──┘   └────┬───┘  └───┬───────┘  └─────┬──┘
         │            │          │               │
    ┌────┴────────────┴──────────┴───────────────┴────┐
    │     Background Tasks & Scheduled Jobs (Celery)  │
    │  - News Fetching (Every 30 minutes)             │
    │  - AI Content Generation                         │
    │  - Cache Management                             │
    │  - Sitemap Generation                           │
    └────┬──────────────────────────────────────────┬──┘
         │                                          │
    ┌────▼────────┬───────────┬──────────────┬──────▼────┐
    │             │           │              │           │
┌───▼───┐  ┌─────▼──┐  ┌─────▼────┐  ┌──────▼──┐  ┌─────▼────┐
│MongoDB│  │ Redis  │  │  OpenAI  │  │ News    │  │External  │
│       │  │ Cache  │  │   API    │  │  APIs   │  │Services  │
└───────┘  └────────┘  └──────────┘  └─────────┘  └──────────┘
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI Components
- **State**: React Hooks
- **HTTP Client**: Axios
- **Routing**: Next.js App Router (Dynamic Routes)

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Server**: Uvicorn (ASGI)
- **Database**: MongoDB (Motor async driver)
- **Cache**: Redis
- **Background Jobs**: Celery + Celery Beat
- **Task Queue**: Redis
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic
- **API Documentation**: OpenAPI/Swagger

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Azure App Service / AWS ECS
- **Monitoring**: CloudWatch / Azure Monitor

---

## File Structure

```
trendnexai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── security.py          # JWT & password hashing
│   │   ├── middleware.py        # Rate limiting, CORS, logging
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   ├── schemas.py           # Pydantic models
│   │   ├── db.py                # MongoDB connection
│   │   ├── db_manager.py        # Database initialization & indexes
│   │   ├── news_api.py          # News fetching from multiple sources
│   │   ├── services.py          # Business logic
│   │   ├── openai_service.py    # AI content generation
│   │   ├── celery_app.py        # Celery configuration & tasks
│   │   ├── tasks.py             # Backward compatibility
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── app/                         # Next.js App Directory
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Homepage
│   ├── api/                    # API routes (if needed)
│   ├── admin/                  # Admin dashboard (protected)
│   ├── article/[slug]/         # Dynamic article pages
│   ├── category/[category]/    # Category pages
│   ├── about/
│   ├── contact/
│   └── globals.css
│
├── components/
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── ArticleCard.tsx
│   ├── ArticleContent.tsx
│   ├── ThemeToggle.tsx
│   └── ui/                     # Radix UI component library
│
├── lib/
│   ├── api.ts                  # API client
│   ├── mongodb.ts              # MongoDB connection
│   ├── news.ts                 # News fetching utilities
│   ├── openai.ts               # OpenAI utilities
│   └── utils.ts                # Utility functions
│
├── models/
│   └── Article.ts              # Mongoose schemas (reference)
│
├── scripts/
│   ├── deploy.sh              # Deployment script
│   ├── setup.sh               # Setup script
│   └── health-check.sh        # Health check script
│
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
│
├── docker-compose.yml          # Multi-container setup
├── Dockerfile                  # Frontend Docker image
├── Dockerfile.backend          # Backend Docker image  (in backend/)
├── .gitignore
├── .env.example               # Environment variables template
├── .env.frontend.example      # Frontend env template
├── README.md                  # Project documentation
├── DEPLOYMENT.md              # Deployment guide
├── ARCHITECTURE.md            # This file
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
├── package.json
└── postcss.config.js
```

---

## Data Models

### Article Schema (MongoDB)

```typescript
{
  _id: ObjectId,
  
  // Core Fields
  title: string,              // SEO-friendly title
  slug: string,              // URL slug (unique)
  category: string,          // Article category
  summary: string,           // 150-200 character summary
  
  // Content (Multi-language)
  content: {
    en: string,             // English content (HTML)
    te: string,             // Telugu
    ta: string,             // Tamil
    kn: string,             // Kannada
    ml: string              // Malayalam
  },
  
  // SEO Fields
  seo_title: string,         // Meta title (50-60 chars)
  seo_description: string,   // Meta description (150-160 chars)
  seo_keywords: [string],    // Keywords array
  
  // Media
  image_url: string,         // Featured image
  author: string,            // Article author
  
  // Metadata
  tags: [string],            // Article tags
  language: enum,            // Primary language
  status: enum,              // draft | published | archived
  
  // Stats
  views: number,             // View count
  ai_generated: boolean,     // AI-powered content flag
  fingerprint: string,       // For deduplication
  
  // Dates
  createdAt: Date,
  updatedAt: Date,
  publishedAt: Date,
  
  // Source
  source_url: string,        // Original news URL
}
```

---

## API Endpoints

### Public Routes (No Authentication)

```
GET  /health                    # Health check
GET  /status                    # Service status
GET  /api/articles              # List published articles (paginated)
GET  /api/articles/{slug}       # Get single article
GET  /api/categories            # List all categories
```

### Admin Routes (JWT Required)

```
POST /api/admin/login           # User authentication
GET  /api/admin/profile         # Current user profile
GET  /api/admin/articles        # List all articles (draft, published, archived)
POST /api/admin/articles/{id}/status   # Update article status
POST /api/admin/fetch-news      # Manually trigger news fetch
```

---

## Environment Configuration

```bash
# Backend Configuration
ENV=production
DEBUG=false
LOG_LEVEL=INFO
PORT=8000

# Database
MONGODB_URI=mongodb://...
REDIS_URL=redis://...

# Authentication
SECRET_KEY=<32-char-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo

# News Fetching
NEWS_API_KEY=...
NEWS_FETCH_INTERVAL_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://...
CELERY_RESULT_BACKEND=redis://...

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
```

---

## Deployment Strategy

### Development
- Docker Compose (local)
- Hot reload enabled
- Debug logging

### Staging
- Docker Compose + load balancer
- Integration testing
- Pre-production validation

### Production
- Kubernetes or managed container service
- Auto-scaling configured
- SSL/TLS enabled
- Database backups scheduled
- CDN deployed
- Monitoring & alerts active

---

## Security Architecture

```
┌─ Client ─────────────────────────────────────┐
│                                               │
├─ HTTPS/TLS Encryption ─────────────────────┤
│                                               │
─── CORS Middleware ────────────────────────────
│
├─ InputValidation (Pydantic) ───────────────┤
│
├─ JWT Authentication ──────────────────────┤
│
├─ Rate Limiting ────────────────────────────┤
│
├─ Authorization (Role-Based) ──────────────┤
│
├─ Database Queries (Parametrized) ─────────┤
│
└─ Secrets (Environment Variables) ─────────┘
```

---

## Performance Optimization

### Frontend
- Next.js Image Optimization
- Code Splitting
- Static Generation (SSG)
- API Route Caching

### Backend
- Redis Caching (60s for lists, 300s for articles)
- Database Indexes (12 indexes)
- Async Processing (Celery)
- Connection Pooling

### Infrastructure
- CDN for static assets
- Database read replicas
- Load balancing
- Auto-scaling

---

## Monitoring & Logging

### Application Logs
- Structured JSON logging
- Log aggregation (ELK/CloudWatch)
- Error tracking (Sentry)

### Performance Metrics
- API response times
- Database query performance
- Worker job completion rates
- Cache hit rates

### Alerts
- High error rate (>5%)
- Slow responses (>5s)
- Failed background jobs
- Low disk space
- Database connection issues

---

## Backup & Disaster Recovery

### Database Backups
- Daily automated backups
- 30-day retention
- Point-in-time recovery enabled

### Disaster Recovery Plan
- RTO: 4 hours
- RPO: 1 hour
- Multi-region failover capability
- Regular DR drills (monthly)

---

## Cost Breakdown (Monthly Estimate)

| Service | Est. Cost | Notes |
|---------|-----------|-------|
| MongoDB Atlas | $50-100 | M10+ cluster |
| Redis | $15-50 | Premium tier |
| Compute (Backend) | $100-300 | Auto-scaled |
| Compute (Frontend) | $20-50 | CDN + hosting |
| OpenAI API | 100-500 | Based on usage |
| News APIs | 10-50 | NewsAPI + others |
| **Total** | **$295-1050** | ~500K articles/month |

---

## Future Enhancements

- [ ] Multi-language support expansion
- [ ] Advanced analytics dashboard
- [ ] Email newsletter system
- [ ] Social media integration
- [ ] Recommendation engine
- [ ] Mobile app (React Native)
- [ ] GraphQL API
- [ ] Real-time WebSocket updates
- [ ] Blockchain verification for content
- [ ] Advanced search with ES
