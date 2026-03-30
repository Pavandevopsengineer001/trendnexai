# 🧪 TrendNexAI - Comprehensive Testing Plan

**Created:** March 30, 2026  
**Project Goals:** Full test coverage for production-ready deployment

---

## 📋 Project Overview

**TrendNexAI** is a full-stack AI-powered news aggregation platform with:
- **Frontend**: Next.js + React + TypeScript
- **Backend**: FastAPI + Python + MongoDB + Redis + Celery
- **DevOps**: Docker, Docker Compose, GitHub Actions

---

## 🎯 Testing Objectives

| Goal | Why | Success Metric |
|------|-----|-----------------|
| **Functional Correctness** | Ensure all features work as designed | All tests pass |
| **Performance** | System handles production load | <500ms response times |
| **Security** | Protect user data and prevent attacks | No vulnerabilities found |
| **Reliability** | Zero downtime deployments | 99.9% uptime |
| **Data Integrity** | Prevent data loss or corruption | All CRUD operations verified |

---

## 📊 Testing Matrix

```
Testing Level        Coverage    Priority    Status
─────────────────────────────────────────────────
Unit Tests           70%         HIGH        ⏳ To Do
Integration Tests    80%         HIGH        ⏳ To Do  
API Tests            95%         CRITICAL    ⏳ To Do
E2E Tests            60%         MEDIUM      ⏳ To Do
Performance Tests    80%         HIGH        ⏳ To Do
Security Tests       85%         CRITICAL    ⏳ To Do
```

---

## 🏗️ Part 1: Backend Testing (FastAPI + Python)

### 1.1 Unit Tests

**What to test:**
- Individual functions in isolation
- Business logic (news fetching, article generation, caching)
- Utility functions

**Files to test:**
```
backend/app/
├── news_api.py          → fetch_combined_news()
├── services.py          → save_articles(), get_articles()
├── openai_service.py    → generate_article()
├── cache.py             → Redis operations
├── security.py          → hash_password(), verify_token()
└── schemas.py           → Pydantic model validation
```

**Tools:** pytest, unittest.mock, pytest-cov

**Commands:**
```bash
# Run all backend tests
cd backend && pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_news_api.py -v

# Run only fast tests
pytest -m "not slow"
```

### 1.2 Integration Tests

**What to test:**
- Components working together
- Database operations (CRUD)
- Cache interactions
- Celery tasks

**Test scenarios:**
```
✓ Create article → Save to DB → Query from DB
✓ Fetch news → Process → Generate AI content
✓ Cache write → Cache read → Cache invalidation
✓ Schedule job → Execute → Update DB
```

**Test coverage needed:**
- POST /articles (create)
- GET /articles (list with filtering)
- GET /articles/{slug} (retrieve)
- PUT /articles/{slug} (update)
- DELETE /articles/{slug}
- POST /admin/fetch-news (trigger fetch)
- POST /admin/generate-article (trigger generation)

### 1.3 API Tests

**Critical endpoints to test:**
```
AUTH ENDPOINTS
──────────────
POST /auth/login             → Return JWT token
POST /auth/refresh           → Return new token
POST /auth/logout            → Invalidate token

PUBLIC ENDPOINTS
────────────────
GET /articles                → List all articles
GET /articles/{slug}         → Get single article
GET /articles?category=tech  → Filter by category
GET /categories              → List categories
GET /health                  → System status

ADMIN ENDPOINTS (Protected)
───────────────────────────
POST /admin/fetch-news       → Trigger news fetch
POST /admin/generate-article → Generate AI content
POST /admin/articles         → Create article
PUT /admin/articles/{slug}   → Update article
DELETE /admin/articles/{slug}→ Delete article

ANALYTICS ENDPOINTS
───────────────────
POST /analytics/view         → Track page view
GET /analytics/stats         → Get engagement stats
```

**Tools:** pytest-httpx, httpx, requests

### 1.4 Database Tests

**MongoDB operations:**
```sql
✓ Insert article with all fields
✓ Query by slug (unique)
✓ Query by category
✓ Update article content
✓ Delete article with cascade
✓ Aggregate: articles per category
✓ Index verification
✓ Connection pooling
```

**Test with:**
- Real MongoDB in docker
- Fixtures for sample data
- Teardown/cleanup after tests

---

## 🎨 Part 2: Frontend Testing (Next.js + React)

### 2.1 Component Unit Tests

**Tools:** Jest, React Testing Library, @testing-library/react

**Components to test:**
```
components/
├── Header.tsx            → Navigation, theme toggle
├── Footer.tsx            → Links, contact
├── ArticleCard.tsx       → Card rendering, links
├── ArticleContent.tsx    → Content display
├── RelatedArticles.tsx   → Related content loading
├── CategorySection.tsx   → Category display
├── TrendingSection.tsx   → Trending articles
├── ThemeToggle.tsx       → Dark/light mode
└── AdUnit.tsx            → Ad rendering
```

**Test scenarios:**
- Render correctly with props
- Handle missing data gracefully
- Click handlers work
- Links point to correct routes
- Dark mode toggle switches theme
- Responsive design

### 2.2 Page Tests

**Pages to test:**
```
app/
├── page.tsx              → Home page: articles load
├── article/[slug]/page.tsx     → Article display, SEO meta tags
├── category/[category]/page.tsx → Category filtering
├── company/[company]/page.tsx  → Company page
└── contact/page.tsx      → Form submission
```

**Test scenarios:**
- Page loads and renders
- Dynamic routes work
- SEO meta tags present
- Forms submit correctly
- Error states handled

### 2.3 Integration Tests

**Tools:** Cypress, Playwright, or Playwright Test

**User flows:**
```
✓ Home → Click article → Read content → See related articles
✓ Home → Select category → View filtered articles
✓ Search/filter articles
✓ Click trending article
✓ Theme toggle persists
✓ Navigation works across pages
```

### 2.4 API Integration

**Test scenarios:**
```
✓ Fetch articles from /api/articles
✓ Load article by slug from /api/article/[slug]
✓ Filter by category
✓ Handle API errors gracefully
✓ Loading states display correctly
```

---

## 🔗 Part 3: End-to-End Testing (Full Stack)

### 3.1 Happy Path Scenarios

**Scenario 1: User reads an article**
```
1. Start server
2. Open http://localhost:3000
3. Home page loads with articles
4. Click on article
5. Article page displays with full content
6. Meta tags in page <head> are correct
7. Related articles shown
8. Click related article
9. New article loads
✓ PASS
```

**Scenario 2: Admin fetches and generates content**
```
1. Login as admin
2. Navigate to admin dashboard
3. Click "Fetch Latest News"
4. See loading state
5. News fetched successfully
6. Click "Generate AI Content"
7. Article generated with 700+ words
8. Article appears on home page
✓ PASS
```

**Scenario 3: Caching works**
```
1. Request article #1 (cache miss) - 500ms
2. Request article #1 again (cache hit) - 50ms
3. Update article #1
4. Request article #1 (cache invalidated) - 500ms
✓ PASS
```

### 3.2 Error Handling

**Test scenarios:**
```
✓ API server down → Show error page
✓ Invalid article slug → 404 page
✓ Authentication failure → Redirect to login
✓ Rate limit exceeded → 429 error
✓ Database connection lost → Graceful error message
```

---

## ⚙️ Part 4: Performance Testing

### 4.1 Load Testing

**Tools:** Apache JMeter, Locust, k6

**Test scenarios:**
```
Test #1: Concurrent Readers
- 100 users
- Reading articles simultaneously
- Measure: response time, throughput, errors
- Expected: <500ms, 0% errors

Test #2: API Stress
- 1000 requests/sec
- Mix of GET and POST
- Duration: 5 minutes
- Expected: <1000ms p95, <5% errors

Test #3: Cache Effectiveness
- 80% cache hits
- Verify Redis is being used
- Expected: >80% hit ratio
```

### 4.2 Frontend Performance

**Tools:** Lighthouse, WebPageTest, Puppeteer

**Metrics:**
```
Metric              Target    Current
─────────────────────────────────────
First Contentful Paint   <1.8s   TBD
Largest Contentful Paint <2.5s   TBD
Cumulative Layout Shift  <0.1    TBD
Time to Interactive      <3.5s   TBD
```

### 4.3 Database Performance

**Test scenarios:**
```
✓ Query 1000 articles → <100ms
✓ Full-text search → <200ms
✓ Aggregate by category → <300ms
✓ Concurrent writes (10) → No locks
```

---

## 🔒 Part 5: Security Testing

### 5.1 Authentication & Authorization

**Test scenarios:**
```
✓ Login with valid credentials → Get JWT
✓ Login with invalid password → 401 Unauthorized
✓ Access admin endpoint without token → 403 Forbidden
✓ Use expired token → 401 Unauthorized
✓ Token refresh works
✓ Password is hashed (not plaintext)
```

### 5.2 Input Validation

**Test scenarios:**
```
✓ XSS attack in article content → Sanitized
✓ SQL injection in search → No DB access
✓ Invalid JSON in request → 400 Bad Request
✓ Missing required fields → 422 Unprocessable Entity
✓ File upload validation
```

### 5.3 API Security

**Test scenarios:**
```
✓ Rate limiting works (100/min)
✓ CORS headers correct
✓ No sensitive data in logs
✓ HTTPS enforced in production
✓ No hardcoded secrets
```

---

## 📈 Part 6: Deployment Testing

### 6.1 Docker Build

```bash
# Build images
docker build -t trendnexai-frontend:latest .
docker build -t trendnexai-backend:latest backend/

# Test images
docker run trendnexai-frontend:latest npm test
docker run trendnexai-backend:latest pytest
```

### 6.2 Docker Compose

```bash
# Full stack test
docker-compose up -d
sleep 20

# Health checks
curl http://localhost:3000/
curl http://localhost:8001/health
curl http://localhost:8001/docs

# Stop
docker-compose down
```

### 6.3 CI/CD Pipeline

**GitHub Actions tests:**
```
✓ Code lint passes
✓ Unit tests pass
✓ Build succeeds
✓ Docker image builds
✓ Security scan passes
✓ Integration tests pass
```

---

## 🚀 Execution Plan

### Week 1: Foundation
- [ ] Setup pytest for backend
- [ ] Setup Jest for frontend
- [ ] Create test fixtures/mocks
- [ ] Write 20 unit tests (backend)
- [ ] Write 20 unit tests (frontend)

### Week 2: Integration & API
- [ ] Write 15 integration tests
- [ ] Write 20 API endpoint tests
- [ ] Test database operations
- [ ] Test authentication flow

### Week 3: E2E & Performance
- [ ] Setup Cypress for E2E
- [ ] Write 5 critical user flows
- [ ] Load testing (100 concurrent users)
- [ ] Performance profiling

### Week 4: Security & DevOps
- [ ] Security testing (OWASP top 10)
- [ ] Dependency vulnerability scan
- [ ] Docker compose testing
- [ ] Deployment testing

---

## 📊 Test Coverage Goals

```
Component           Target    Current Status
──────────────────────────────────────────
Backend API         95%       ⏳ Pending
Database Layer      90%       ⏳ Pending
Frontend Pages      80%       ⏳ Pending
Frontend Components 85%       ⏳ Pending
Security Layer      100%      ⏳ Pending
Overall Project     85%       ⏳ Pending
```

---

## ✅ Success Criteria

Project is ready for production when:

1. ✅ **70%+ test coverage** across entire codebase
2. ✅ **All critical tests pass** (auth, CRUD, API)
3. ✅ **0 security vulnerabilities** found
4. ✅ **<500ms p95 response time** for API
5. ✅ **Zero console errors** in production build
6. ✅ **All E2E flows execute** successfully
7. ✅ **Docker compose** runs all services without errors
8. ✅ **CI/CD pipeline** passes all checks

---

## 🔗 Test Command Reference

```bash
# BACKEND TESTS
cd backend
pytest                           # All tests
pytest -v                        # Verbose
pytest --cov=app               # With coverage
pytest tests/test_news_api.py  # Specific file
pytest -k "test_login"          # Specific test

# FRONTEND TESTS
npm test                         # All Jest tests
npm test -- --coverage          # With coverage
npm run test:e2e                # Cypress E2E

# FULL STACK
docker-compose up -d
npm run test:integration        # Integration tests
docker-compose down

# CI/CD
git push origin main            # Triggers GitHub Actions
```

---

## 📝 Notes

- **Mock external APIs** (OpenAI, NewsAPI) in tests
- **Use fixtures** for sample data
- **Isolate database** tests (use test DB)
- **Run tests in CI/CD** automatically
- **Keep tests fast** (<5s total for unit tests)
- **Document failing tests** with clear error messages

---

**Next Steps:**
1. Review and approve this plan
2. Setup test infrastructure (pytest, Jest)
3. Begin with Part 1: Backend unit tests
4. Progressively move through parts 2-6
