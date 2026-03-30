"""
🚀 DATABASE SETUP & USAGE QUICK START

Complete guide to setting up and using TrendNexAI's optimized MongoDB setup.
"""

# ============== QUICK START ==============

## 1. SETUP DATABASE (One-time)

```bash
# Navigate to backend
cd backend

# Setup collections and indices only
python setup_db.py

# Setup + insert sample data
python setup_db.py --with-data

# Setup + sample data + analysis
python setup_db.py --full
```

Output:
```
============================================================
🔧 TRENDNEXAI DATABASE SETUP & OPTIMIZATION
============================================================

📰 ARTICLES COLLECTION
--
  Creating 14 indices...
    ✓ idx_slug_unique
    ✓ idx_status
    ✓ idx_category
    ... (14 indices total)
  Summary: 14/14 indices created

📊 ANALYTICS COLLECTION
--
  Creating 5 indices...
    ✓ idx_article_slug
    ... (5 indices total)
  Summary: 5/5 indices created

⚡ CACHE COLLECTION
--
  Creating 2 indices...
    ✓ idx_cache_key
    ✓ idx_ttl_cache
  Summary: 2/2 indices created

===
✅ DATABASE SETUP COMPLETE!

💡 OPTIMIZATION RECOMMENDATIONS:
  1. QUERY PATTERNS TO LEVERAGE:
     • db.articles.find({status: 'published'}).sort({publishedAt: -1})
     • db.articles.find({category: 'tech', status: 'published'})
     • db.articles.find({$text: {$search: 'keyword'}})
  ...
```

## 2. VERIFY SETUP

```bash
# Connect to MongoDB
mongo mongodb://admin:password@localhost:27017/trendnexai?authSource=admin

# Check collections
> show collections
articles
analytics
cache
articles_by_category
trending_articles
pending_review_queue

# Check indices
> db.articles.getIndexes()
[
  { v: 2, key: { _id: 1 }, name: '_id_' },
  { v: 2, key: { slug: 1 }, name: 'idx_slug_unique', unique: true },
  { v: 2, key: { status: 1 }, name: 'idx_status' },
  ... 14 total indices
]

# Count documents
> db.articles.countDocuments()
3    # If using --with-data
```

## 3. ANALYZE DATABASE

```bash
python setup_db.py --analyze

Output:
====================
🔍 DATABASE PERFORMANCE ANALYSIS
====================

🖥️  SERVER STATUS:
  Uptime: 2.5 hours
  Connections: 12 current

📊 INDEX STATISTICS:
  Collection: articles
    Total indices: 14
    Document count: 3
    • idx_slug_unique [UNIQUE]
    • idx_status
    • idx_category
    ... (11 more)
```

# ============== USING OPTIMIZED QUERIES ==============

## From Python Code

### Option 1: Using get_optimized_articles() Helper

```python
from app.services import get_optimized_articles

# Get published articles in a category
articles = await get_optimized_articles(
    status="published",
    category="technology",
    limit=20,
    skip=0
)
print(f"Found {len(articles)} articles")
```

### Option 2: Using DatabaseOptimizer Class

```python
from app.db_optimization import DatabaseOptimizer
from app.db import db

optimizer = DatabaseOptimizer(db)

# Get trending articles
trending = await optimizer.get_trending_articles(days=7, limit=10)

# Get pending articles for admin
pending = await optimizer.get_pending_articles(limit=50)

# Get statistics
stats = await optimizer.get_statistics()
print(f"Total articles: {stats['total_articles']}")
print(f"By status: {stats['by_status']}")

# Search articles
results = await optimizer.search_articles("machine learning", limit=20)

# Get analytics
analytics = await optimizer.get_analytics_for_article("article-slug", days=7)
```

### Option 3: Direct MongoDB Queries (With Indices)

```python
from app.db import db

# These queries automatically use the created indices

# Get published articles sorted by date (uses: idx_status_publishedAt)
articles = await db.articles.find(
    {"status": "published"}
).sort([("publishedAt", -1)]).limit(20).to_list(length=20)

# Browse category (uses: idx_category_status_date)
articles = await db.articles.find(
    {"category": "tech", "status": "published"}
).sort([("publishedAt", -1)]).limit(50).to_list(length=50)

# Get trending (uses: idx_status_views)
trending = await db.articles.find(
    {"status": "published"}
).sort([("views", -1)]).limit(20).to_list(length=20)

# Full-text search (uses: idx_fulltext_search)
results = await db.articles.find(
    {"$text": {"$search": "keyword"}}
).limit(20).to_list(length=20)

# Admin: Get pending review (uses: idx_status_createdAt)
pending = await db.articles.find(
    {"status": "pending_review"}
).sort([("createdAt", -1)]).to_list(length=None)
```

## From API Routes

```python
# app/admin_routes.py or app/routes.py

from app.services import get_optimized_articles, get_db_optimizer

@app.get("/api/articles/published")
async def get_published_articles(
    category: str = None,
    page: int = 0,
    limit: int = 20
):
    """Get published articles using optimized queries"""
    skip = page * limit
    
    articles = await get_optimized_articles(
        status="published",
        category=category,
        limit=limit,
        skip=skip
    )
    
    return {
        "success": True,
        "data": articles,
        "total": len(articles)
    }

@app.get("/api/articles/trending")
async def get_trending():
    """Get trending articles"""
    optimizer = get_db_optimizer()
    articles = await optimizer.get_trending_articles(days=7, limit=20)
    
    return {
        "success": True,
        "data": articles
    }

@app.get("/api/admin/stats")
async def get_stats():
    """Get database statistics"""
    optimizer = get_db_optimizer()
    stats = await optimizer.get_statistics()
    
    return {
        "success": True,
        "data": stats
    }
```

# ============== MAINTENANCE ==============

## Weekly Tasks

```bash
# Analyze and report on database
python setup_db.py --analyze

# Review output for:
# - Index sizes
# - Document counts
# - Slow queries if enabled
```

## Monthly Tasks

```bash
# Clean up old data
python setup_db.py --cleanup

# Output:
# ✓ Deleted 45 old unpublished articles (older than 30 days)
# ✓ Deleted 1200 old analytics records (older than 90 days)
# ✓ Cleared 32 expired cache entries
```

## Monitoring Common Issues

### Issue: Queries Getting Slower

```bash
# 1. Check index stats
python setup_db.py --analyze

# 2. Clean up old data
python setup_db.py --cleanup

# 3. Verify indices exist
mongo
> use trendnexai
> db.articles.listIndexes()

# 4. If needed, rebuild indices
> db.articles.reIndex()
```

### Issue: High Disk Usage

```bash
# Check database size
mongo
> db.stats()

# Check collection sizes
> db.articles.stats()

# Solution: Clean old data
python setup_db.py --cleanup
```

### Issue: Text Search Returns No Results

```bash
# Verify text index exists
mongo
> db.articles.listIndexes()
# Should see: { key: { title: "text", summary: "text", ... } }

# If missing, recreate indices
python setup_db.py

# Test search
> db.articles.find({$text: {$search: "keyword"}})
```

# ============== PERFORMANCE EXPECTATIONS ==============

Query Performance (with ~100K articles):

| Operation | Expected Time | Index Used |
|-----------|---------------|-----------|
| Single article by slug | <5 ms | idx_slug_unique |
| List published (20 items) | <10 ms | idx_status_publishedAt |
| Browse category | <15 ms | idx_category_status_date |
| Get trending (top 20) | <10 ms | idx_status_views |
| Full-text search (20 results) | <50 ms | idx_fulltext_search |
| Get pending (admin) | <5 ms | idx_status_createdAt |

Cold cache (first query after server restart) adds ~20-50ms per index read.

# ============== DATABASE INDICES SUMMARY ==============

ARTICLES Collection:
- 1 UNIQUE index (slug)
- 4 FILTER indices (status, category, ai_generated, source_url)
- 3 SORT indices (createdAt, publishedAt, views)
- 5 COMPOUND indices (for common query patterns)
- 1 TEXT search index
- 1 TTL index (auto-delete unpublished after 30 days)

ANALYTICS Collection:
- 1 LOOKUP index (article_slug)
- 1 FILTER index (event_type)
- 1 SORT index (timestamp)
- 1 COMPOUND index (article_slug, timestamp)
- 1 TTL index (auto-delete after 90 days)

CACHE Collection:
- 1 UNIQUE index (key)
- 1 TTL index (auto-delete after 1 hour)

DATABASE VIEWS (materialized):
- articles_by_category (stats by category)
- trending_articles (top articles last 7 days)
- pending_review_queue (pending articles for admin)

# ============== CONFIGURATION ==============

Connection Settings (in setup_db.py):

```python
client = AsyncIOMotorClient(
    mongodb_uri,
    maxPoolSize=50,      # Max concurrent connections
    minPoolSize=10       # Min maintained connections
)
```

Current Configuration:
- Supports 10-50 concurrent users
- Good for small-to-medium deployments
- Increase maxPoolSize to 100+ for 200+ users

# ============== NEXT STEPS ==============

1. ✅ Run setup script: python setup_db.py
2. ✅ Verify indices: python setup_db.py --analyze
3. ✅ Insert sample data: python setup_db.py --with-data
4. ✅ Start using optimized queries in code
5. ✅ Monitor with: python setup_db.py --cleanup (monthly)

For detailed index design info, see: DATABASE_OPTIMIZATION.md
"""
