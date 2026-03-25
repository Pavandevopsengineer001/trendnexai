# TrendNexAI: Production-Ready AI News Platform

A scalable, production-grade AI news platform that automatically fetches, processes, and publishes SEO-optimized articles using AI-powered content generation.

## 🎯 Features

- **Automated News Fetching**: Scheduled RSS/API-based news collection
- **AI Content Generation**: OpenAI-powered article rewriting and enhancement
- **SEO Optimization**: Meta tags, structured URLs, sitemaps, and internal linking
- **Admin Dashboard**: Review, edit, and publish articles with approval workflows
- **Multi-language Support**: English, Telugu, Tamil, Kannada, Malayalam
- **Production-Ready**: Docker, CI/CD, security, authentication, and scaling considerations
- **Real-time Updates**: Redis caching, async processing, and background jobs
- **Admin Authentication**: JWT-based role-based access control

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│          - Public Articles & Category Pages              │
│          - Admin Dashboard (Protected)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Backend (FastAPI)                      │
│          - REST API for Content Management              │
│          - Authentication & Authorization               │
│          - News Fetching & Processing                   │
└────────────────────┬────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼──────┐  ┌─────▼──────┐  ┌────▼──────────┐
│  MongoDB  │  │   Redis    │  │ Celery Worker │
│ Database  │  │   Cache    │  │  (Background) │
└───────────┘  └────────────┘  └───────────────┘
```

## 📋 Prerequisites

- **Node.js** 18+ (Frontend)
- **Python** 3.10+ (Backend)
- **MongoDB** 6+ (Database)
- **Redis** 7+ (Cache & Message Queue)
- **Docker & Docker Compose** (Recommended)
- **OpenAI API Key** (For AI content generation)
- **News API Key** (For news fetching)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd trendnexai

# Copy environment files
cp .env.example .env
cp .env.frontend.example frontend/.env.local
cp backend/.env.example backend/.env
```

### 2. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Run migrations (if needed)
docker-compose exec backend python -m alembic upgrade head

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin Dashboard: http://localhost:3000/admin
```

### 3. Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
celery -A app.celery_app worker -l info

# Start Celery beat scheduler (in another terminal)
celery -A app.celery_app beat -l info
```

#### Frontend Setup

```bash
cd <root-directory>

# Install dependencies
npm install

# Create .env.local
cp .env.frontend.example .env.local

# Start development server
npm run dev

# Open browser
# http://localhost:3000
```

### 4. Environment Configuration

Update `.env` file with your credentials:

```bash
# Critical: Change these in production!
MONGODB_URI=mongodb://admin:password@localhost:27017/trendnexai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<generate-random-32-char-key>
OPENAI_API_KEY=<your-openai-key>
NEWS_API_KEY=<your-newsapi-key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-password>
```

## 📚 Documentation

### Backend API

**Health Check**
```bash
curl http://localhost:8000/health
```

**Admin Login** (Get JWT Token)
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**Fetch News** (Trigger manually)
```bash
curl -X POST http://localhost:8000/api/admin/fetch-news \
  -H "Authorization: Bearer <token>"
```

**List Articles with Filters**
```bash
curl "http://localhost:8000/api/articles?category=technology&skip=0&limit=20"
```

### Frontend Routes

| Route | Purpose |
|-------|---------|
| `/` | Homepage with latest articles |
| `/article/[slug]` | Article detail page with SEO meta tags |
| `/category/[category]` | Category-specific article list |
| `/admin` | Admin dashboard (protected) |
| `/admin/articles` | Article management |
| `/admin/articles/[id]/edit` | Edit article |
| `/about` | About page |
| `/contact` | Contact page |

### Database Schema

**Articles Collection**
```javascript
{
  _id: ObjectId,
  title: string,
  slug: string,
  status: enum["draft", "published", "archived"],
  category: string,
  tags: [string],
  language: enum["en", "te", "ta", "kn", "ml"],
  content: {
    en: string,
    te: string,
    ta: string,
    kn: string,
    ml: string
  },
  seo_title: string,
  seo_description: string,
  seo_keywords: [string],
  source_url: string,
  image_url: string,
  author: string,
  createdAt: Date,
  updatedAt: Date,
  publishedAt: Date,
  views: number,
  _ai_generated: boolean
}
```

## 🔐 Security

- **Authentication**: JWT tokens with expiration
- **Authorization**: Role-based access control (Admin, Editor, Viewer)
- **Input Validation**: Pydantic schemas for all inputs
- **Rate Limiting**: API rate limiting middleware
- **CORS**: Configurable cross-origin access
- **HTTPS**: Required in production
- **Environment Variables**: All secrets in `.env` (never committed)
- **Password Hashing**: bcrypt for password storage

## 📈 Performance Optimization

- **Redis Caching**: Article lists and detail pages cached for 5 minutes
- **Async Processing**: Celery for background news fetching
- **Scheduled Tasks**: Celery Beat for automated news collection every 30 minutes
- **Database Indexes**: Optimized queries on title, slug, createdAt, category
- **Image Optimization**: Next.js Image component for lazy loading
- **API Response Pagination**: Default 20 items per page

## 🐳 Docker Deployment

### Build Docker Images

```bash
# Backend
docker build -t trendnexai-backend:latest backend/
docker run -p 8000:8000 --env-file .env trendnexai-backend:latest

# Frontend
docker build -t trendnexai-frontend:latest .
docker run -p 3000:3000 --env-file .env.local trendnexai-frontend:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 🚢 Production Deployment

### Azure App Service
```bash
# Deploy backend
az webapp up --name trendnexai-backend --runtime PYTHON:3.10

# Deploy frontend
az webapp up --name trendnexai-frontend --runtime NODE:18
```

### AWS EC2
```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Clone repo & setup
git clone <repo-url>
./scripts/deploy.sh production
```

### GitHub Actions CI/CD
Automated testing, building, and deployment on push to main branch.
See `.github/workflows/deploy.yml`

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_news_api.py -v
```

### Frontend Testing

```bash
# Run Jest tests
npm run test

# Generate coverage
npm run test -- --coverage
```

## 📊 Monitoring & Logging

- **Application Logs**: Structured JSON logging
- **Error Tracking**: Sentry integration (optional)
- **Performance Monitoring**: APM tools ready
- **Database Monitoring**: MongoDB Atlas monitoring

## 🔄 Scheduled Tasks

- **Every 30 minutes**: Fetch news from sources
- **Daily**: Clear old cached items
- **Weekly**: Generate sitemap
- **Monthly**: Archive old articles

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### MongoDB Connection Error
```
SOLUTION: Ensure MongoDB is running and credentials in .env are correct
docker-compose ps  # Check MongoDB container status
```

### Redis Connection Error
```
SOLUTION: Check Redis service is running
redis-cli ping  # Should return PONG
```

### OpenAI API Errors
```
SOLUTION: Verify API key and quota in https://platform.openai.com
```

### Celery Tasks Not Running
```
SOLUTION: Check celery worker is running and Redis connection is valid
celery -A app.celery_app inspect active  # List active tasks
```

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Email**: support@trendnexai.com

---

**Made with ❤️ for production-grade AI news generation**
