# 💻 Development Guide for TrendNexAI

## Local Development Setup

### System Requirements

- **OS**: Linux, macOS, or Windows (WSL2)
- **Node.js**: v18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **Docker**: Latest version (recommended)
- **Docker Compose**: v2.0+

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd trendnexai

# 2. Create environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp .env.frontend.example .env.local

# 3. Update .env with your API keys
nano .env

# 4. Start all services
docker-compose up -d

# 5. Verify services are running
docker-compose ps
```

**Services will be available at:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB: localhost:27017
- Redis: localhost:6379

### Option 2: Local Development (Without Docker)

#### Backend Setup

```bash
# 1. Install MongoDB (or use Docker)
# macOS: brew install mongodb-community
# Linux: sudo apt-get install mongodb
# Or run: docker run -d -p 27017:27017 mongo:7.0

# 2. Install Redis
# macOS: brew install redis
# Linux: sudo apt-get install redis-server
# Or run: docker run -d -p 6379:6379 redis:7-alpine

# 3. Create Python virtual environment
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start FastAPI server
uvicorn app.main:app --reload

# 6. In another terminal, start Celery worker
celery -A app.celery_app worker -l info

# 7. In another terminal, start Celery Beat
celery -A app.celery_app beat -l info
```

#### Frontend Setup

```bash
# 1. Install dependencies
npm install

# 2. Create .env.local
cp .env.frontend.example .env.local

# 3. Start development server
npm run dev

# 4. Open browser
# http://localhost:3000
```

---

## Development Workflows

### Adding a New API Endpoint

```python
# backend/app/main.py

@app.get("/api/my-endpoint")
async def my_endpoint(
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 20
):
    """
    Description of your endpoint
    """
    # Implementation
    return {"data": []}
```

### Creating a New Database Migration

```python
# backend/app/db_manager.py

async def migrate_add_new_field():
    """Add new field to articles collection"""
    result = await db.articles.update_many(
        {"new_field": {"$exists": False}},
        {"$set": {"new_field": "default_value"}}
    )
    logger.info(f"Migration: Updated {result.modified_count} documents")

# Run migrations
await run_migrations()
```

### Background Task Processing

```python
# backend/app/celery_app.py

@app.task(bind=True, max_retries=3)
def my_background_task(self, param1: str):
    """Your background task"""
    try:
        # Do work
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# Trigger from main.py
from app.celery_app import my_background_task
my_background_task.delay("param_value")
```

### Frontend Page with Admin Protection

```typescript
// app/admin/articles/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function AdminArticles() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [articles, setArticles] = useState([]);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/admin');
    }
  }, [user, loading]);

  useEffect(() => {
    if (user?.role !== 'admin') return;
    
    // Fetch articles
    fetch('/api/admin/articles', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(setArticles);
  }, [user]);

  if (loading) return <div>Loading...</div>;
  if (!user) return null;

  return (
    <div>
      {/* Your admin dashboard */}
    </div>
  );
}
```

---

## Testing

### Backend Testing

```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest tests/test_news_api.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_news_api.py::test_fetch_articles
```

### Frontend Testing

```bash
# Run Jest tests
npm run test

# Run with coverage
npm run test -- --coverage

# Run specific test file
npm run test -- articles.test.ts

# Watch mode
npm run test -- --watch
```

### Integration Testing

```bash
# Start services
docker-compose up -d

# Run integration tests
cd backend
pytest tests/integration/

# Health check
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## Code Style & Conventions

### Backend (Python)

```python
# Follow PEP 8
# Use type hints
async def fetch_articles(category: str, limit: int = 20) -> List[Dict]:
    pass

# Use descriptive names
user_articles = await get_user_articles()

# Use docstrings
def process_article(article: dict) -> dict:
    """
    Process article for publication.
    
    Args:
        article: Raw article data
    
    Returns:
        Processed article with AI-generated content
    """
    pass

# Use logging
logger.info(f"Processing article: {article_id}")
```

### Frontend (TypeScript)

```typescript
// Use strong typing
interface Article {
  _id: string;
  title: string;
  slug: string;
  content: string;
}

// Use functional components
export function ArticleCard({ article }: { article: Article }) {
  return <div>{article.title}</div>;
}

// Use meaningful variable names
const publishedArticles = articles.filter(a => a.status === 'published');

// Use comments for complex logic
// Filter articles that were published in last 7 days
const recentArticles = articles.filter(
  a => new Date(a.publishedAt).getTime() > Date.now() - 7 * 24 * 60 * 60 * 1000
);
```

---

## Debugging

### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use debugpy for VSCode
python -m debugpy --listen 5678 -m uvicorn app.main:app --reload
```

### Frontend Debugging

```typescript
// Browser DevTools
console.log('Debug info:', data);
debugger; // Pause execution

// Or use VSCode debugger
// .vscode/launch.json configured in repo
```

### Database Debugging

```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh admin -u admin -p password

# Query articles
use trendnexai
db.articles.find().pretty()
db.articles.countDocuments()

# View indexes
db.articles.getIndexes()

# Check Redis
docker-compose exec redis redis-cli
> PING
> KEYS *
> GET "articles:all:none:newest:0:20"
```

---

## Common Issues & Solutions

### Issue: "Port 3000 already in use"
```bash
# Find and kill process
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### Issue: MongoDB connection failed
```bash
# Check if MongoDB is running
docker-compose ps mongodb

# Restart MongoDB
docker-compose restart mongodb

# Check connection string in .env
MONGODB_URI=mongodb://admin:password@localhost:27017/trendnexai
```

### Issue: Redis connection failed
```bash
# Check if Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Test Redis connection
redis-cli ping
```

### Issue: Celery tasks not running
```bash
# Check if worker is running
ps aux | grep celery

# Check Celery logs
celery -A app.celery_app inspect active

# Restart worker
docker-compose restart celery-worker
```

---

## Performance Tips

### Frontend
- Use React.memo for expensive components
- Use useMemo/useCallback sparingly
- Lazy load images
- Use Next.js Image component
- Enable static generation (SSG) where possible

### Backend
- Use database indexes
- Enable query result caching
- Use connection pooling
- Monitor slow queries
- Use async/await properly

### Database
- Regular ANALYZE commands
- Remove unused indexes
- Archive old data
- Use appropriate field types

---

## Database Backups

### Local Development
```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --archive=/backup/dump.archive

# Restore MongoDB
docker-compose exec mongodb mongorestore --archive=/backup/dump.archive

# Backup Redis
docker-compose exec redis redis-cli BGSAVE
```

### Production
```bash
# Monthly snapshots
aws ec2 create-snapshot --volume-id vol-xxxxx

# Or use managed services
# MongoDB Atlas: Automatic backups
# AWS RDS: Automated backups
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
git add .
git commit -m "feat: Add new feature"

# Push and create PR
git push origin feature/your-feature

# After review, merge to main
git checkout main
git merge feature/your-feature
git push origin main
```

### Commit Message Format
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code style changes
refactor: Code refactoring
test: Add tests
chore: Maintenance
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [Redis Documentation](https://redis.io/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

---

## Getting Help

1. **Check Documentation**: See README.md, ARCHITECTURE.md, DEPLOYMENT.md
2. **Search GitHub Issues**: Look for similar problems
3. **Ask on Community**: Discord, StackOverflow
4. **Create an Issue**: Provide details and minimal reproduction
