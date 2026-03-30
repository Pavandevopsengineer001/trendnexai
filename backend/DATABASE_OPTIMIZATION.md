"""
📚 DATABASE OPTIMIZATION GUIDE for TrendNexAI

Complete reference for database performance, indexing strategy, and optimization.
"""

# ============ OVERVIEW ============

TrendNexAI uses MongoDB with a comprehensive indexing strategy designed for:
- High-performance reads (published articles, trending, search)
- Efficient approval workflow operations
- Analytics tracking and aggregation
- Automatic cleanup with TTL policies

# ============ COLLECTIONS & INDICES ============

## 1. ARTICLES COLLECTION

Total Indices: 14+
Average Document Size: ~5KB (with AI-generated content)

### PRIMARY LOOKUP INDICES

`idx_slug_unique` - (slug: 1) [UNIQUE]
  Used for: Direct article lookups by slug
  Example: db.articles.find({slug: "article-title"})
  Expected: 1 ms
  Cardinality: Very High (unique)

### FILTERING INDICES

`idx_status` - (status: 1)
  Used for: Filter by article status
  Example: db.articles.find({status: "published"})
  Expected: <10 ms
  Cardinality: Low (6 values: pending_review, draft, approved, published, archived, rejected)

`idx_category` - (category: 1)
  Used for: Browse by category
  Example: db.articles.find({category: "technology"})
  Expected: <10 ms
  Cardinality: Low-Medium (20-50 categories)

`idx_ai_generated` - (ai_generated: 1)
  Used for: Filter AI vs. manual articles
  Example: db.articles.find({ai_generated: true})
  Expected: <10 ms
  Cardinality: Very Low (2 values: true/false)

`idx_source_url` - (source_url: 1) [SPARSE]
  Used for: Deduplication checks
  Example: db.articles.find({source_url: "https://..."})
  Expected: <5 ms
  Cardinality: Very High
  Note: SPARSE - doesn't index null values (saves space)

### SORTING INDICES

`idx_createdAt_desc` - (createdAt: -1)
  Used for: Sort by creation date (newest first)
  Example: db.articles.find({}).sort({createdAt: -1})
  Expected: <20 ms
  Cardinality: Very High (each document distinct timestamp)

`idx_publishedAt_desc` - (publishedAt: -1) [SPARSE]
  Used for: Sort by publication date
  Example: db.articles.find({status: "published"}).sort({publishedAt: -1})
  Expected: <20 ms
  Note: SPARSE - unpublished articles have null publishedAt

`idx_views_desc` - (views: -1)
  Used for: Sort by popularity
  Example: db.articles.find({status: "published"}).sort({views: -1})
  Expected: <20 ms

### COMPOUND INDICES (for common query patterns)

`idx_status_publishedAt` - (status: 1, publishedAt: -1)
  Optimizes: Get published articles sorted by date
  Query: db.articles.find({status: "published"}).sort({publishedAt: -1})
  Expected: <10 ms
  Benefit: Single index covers both filter and sort

`idx_category_status_date` - (category: 1, status: 1, publishedAt: -1)
  Optimizes: Browse category + filter status + sort by date
  Query: db.articles.find({category: "tech", status: "published"}).sort({publishedAt: -1})
  Expected: <10 ms
  Index size: ~50MB per 100K articles

`idx_status_views` - (status: 1, views: -1)
  Optimizes: Get trending articles
  Query: db.articles.find({status: "published"}).sort({views: -1}).limit(20)
  Expected: <10 ms

`idx_status_createdAt` - (status: 1, createdAt: -1)
  Optimizes: Admin workflow (pending articles, newest first)
  Query: db.articles.find({status: "pending_review"}).sort({createdAt: -1})
  Expected: <5 ms

`idx_ai_status` - (ai_generated: 1, status: 1)
  Optimizes: Filter AI-generated published articles
  Query: db.articles.find({ai_generated: true, status: "published"})
  Expected: <10 ms

### TEXT SEARCH INDEX

`idx_fulltext_search` - (title: "text", summary: "text", tags: "text", content: "text")
  Optimizes: Full-text search across articles
  Query: db.articles.find({$text: {$search: "keyword"}})
  Expected: <50 ms (depending on corpus size)
  
  Weights (importance):
    title: 10x      - Title matches most important
    tags: 8x        - Tag matches very important
    summary: 5x     - Summary matches important
    content: 1x     - Content matches baseline
  
  Language: English (configurable)
  Stemming: Applies automatically (run → runs → running)

### TTL INDEX (Time-To-Live)

`idx_ttl_unpublished` - (createdAt: 1) [TTL: 30 days]
  Auto-deletes: Draft and rejected articles after 30 days
  Query: Not applicable (automatic background deletion)
  Benefit: Automatic cleanup of unpublished content
  
  Partial Filter: status IN ("draft", "rejected")
  - This index only applies to draft/rejected articles
  - Published articles are NOT auto-deleted
  - Saves index space by not indexing published articles

# ============ STORAGE & COMPRESSION ============

Collection Compression: Snappy (built-in to MongoDB)
  - Reduces disk usage by 40-60%
  - Slightly slower than uncompressed (negligible)
  - Best for large text content (articles)

Estimated Storage (100,000 articles):
  - Uncompressed: ~500 MB
  - Compressed: ~250 MB (50% reduction)
  - Indices: ~150 MB

# ============ ANALYTICS COLLECTION ============

Total Indices: 5+
Average Document Size: ~200 bytes
Purpose: Track article views, engagement, and events

### INDICES

`idx_article_slug` - (article_slug: 1)
  Used for: Find all analytics for an article
  Example: db.analytics.find({article_slug: "article-slug"})
  Expected: <10 ms

`idx_event_type` - (event_type: 1)
  Used for: Filter by event type (view, click, share, etc.)
  Example: db.analytics.find({event_type: "view"})
  Expected: <10 ms

`idx_timestamp_desc` - (timestamp: -1)
  Used for: Get recent events
  Example: db.analytics.find({}).sort({timestamp: -1})
  Expected: <20 ms

`idx_article_timestamp` - (article_slug: 1, timestamp: -1) [COMPOUND]
  Optimizes: Get analytics for specific article, newest first
  Query: db.analytics.find({article_slug: "slug"}).sort({timestamp: -1})
  Expected: <10 ms

`idx_ttl_analytics` - (timestamp: 1) [TTL: 90 days]
  Auto-deletes: Analytics events after 90 days
  Benefit: Automatic cleanup, keeps database size manageable
  Note: Always-on, transparent to queries

# ============ CACHE COLLECTION ============

Total Indices: 2+
Average Document Size: ~1 KB
Purpose: Fast query result caching

### INDICES

`idx_cache_key` - (key: 1) [UNIQUE]
  Used for: Look up cached values
  Example: db.cache.find_one({key: "article_slug_insights"})
  Expected: <5 ms

`idx_ttl_cache` - (createdAt: 1) [TTL: 1 hour]
  Auto-deletes: Cache entries after 1 hour
  Benefit: Automatic cache invalidation

# ============ DATABASE VIEWS ============

Materialized Views for Common Queries:

### articles_by_category
Purpose: Pre-computed article counts per category
Query: db.articles_by_category.find()
Returns: {_id: "category", count: 42, published: 38, total_views: 1250}
Use for: Category picker, dashboard stats

### trending_articles
Purpose: Top articles from last 7 days
Query: db.trending_articles.find().limit(20)
Returns: Top 20 articles by views (updated hourly)
Use for: Trending section on homepage

### pending_review_queue
Purpose: Articles awaiting admin approval
Query: db.pending_review_queue.find()
Returns: Pending articles with essential fields only
Use for: Admin dashboard

# ============ PERFORMANCE TARGETS ============

Expected Query Performance (with warm cache):

| Query Type | Expected Time | Worst Case | Index Used |
|------------|---------------|-----------|-----------|
| Single article by slug | <5 ms | <20 ms | idx_slug_unique |
| List published articles | <10 ms | <50 ms | idx_status_publishedAt |
| Browse category | <15 ms | <100 ms | idx_category_status_date |
| Get trending (top 20) | <10 ms | <50 ms | idx_status_views |
| Full-text search | <50 ms | <500 ms | idx_fulltext_search |
| Pending review list | <5 ms | <20 ms | idx_status_createdAt |
| Analytics for article | <20 ms | <100 ms | idx_article_timestamp |
| Complex aggregation | <100 ms | <1000 ms | Multiple indices |

Notes:
- Times assume 100K-1M documents
- Cold cache (no relevant data in memory) adds 10-50ms per index read
- Bulk operations (1000+ docs) may take longer but complete efficiently
- Full-text search performance depends on corpus size

# ============ CONNECTION POOLING ============

Configuration (in setup_db.py):
  maxPoolSize: 50    - Maximum concurrent connections
  minPoolSize: 10    - Minimum maintained connections
  
Usage Guidelines:
  - 10-50 users: Current configuration optimal
  - 50-200 users: Good performance expected
  - 200+ users: Consider increasing maxPoolSize to 100+

# ============ QUERY OPTIMIZATION RULES ============

1. ALWAYS USE INDICES FOR FILTERING
   ❌ BAD:   db.articles.find({}).filter(doc => doc.status === "published")
   ✅ GOOD:  db.articles.find({status: "published"})

2. LEVERAGE COMPOUND INDICES
   ❌ BAD:   db.articles.find({category: "tech"}).sort({publishedAt: -1})
   ✅ GOOD:  Use idx_category_status_date with category first in query

3. USE PROJECTION TO LIMIT RETURNED FIELDS
   ❌ BAD:   db.articles.find({status: "published"})  // 5KB per doc
   ✅ GOOD:  db.articles.find({status: "published"}, {title: 1, slug: 1})  // 200 bytes

4. LIMIT RESULT SET
   ❌ BAD:   db.articles.find({status: "published"})  // 10K docs
   ✅ GOOD:  db.articles.find({status: "published"}).limit(20)

5. USE PAGINATION
   ❌ BAD:   db.articles.find({status: "published"}).sort({createdAt: -1})
   ✅ GOOD:  db.articles.find({status: "published"}).sort({createdAt: -1}).skip(20).limit(20)

6. BATCH INSERT FOR BETTER PERFORMANCE
   ❌ BAD:   for(article in articles) db.articles.insert(article)
   ✅ GOOD:  db.articles.insertMany(articles, {ordered: false})

# ============ MONITORING & MAINTENANCE ============

## Regular Tasks

Weekly:
  - Check index sizes: db.articles.aggregate({$indexStats: {}})
  - Monitor slow queries: db.setProfilingLevel(1, {slogms: 100})

Monthly:
  - Rebuild indices (if fragmented): db.articles.reIndex()
  - Analyze index effectiveness: db.articles.aggregate({$indexStats: {}})
  - Check disk space usage: db.stats()

## Optimization Script

Run the optimization utility:
  python setup_db.py --analyze     # View index statistics
  python setup_db.py --cleanup     # Remove old data
  python setup_db.py --optimize    # Analyze & report

## Common Issues & Solutions

### ISSUE: Q ue ries Getting Slower Over Time
CAUSE: Unbounded analytics/cache collection growth
SOLUTION: 
  1. Verify TTL indices are active: db.articles.list_indexes()
  2. Run cleanup: python setup_db.py --cleanup
  3. Force index rebuild: db.articles.reIndex()

### ISSUE: High RAM Usage
CAUSE: Large working set, many indices competing for space
SOLUTION:
  1. Archive old analytics (>90 days)
  2. Review index effectiveness
  3. Increase RAM or optimize index design

### ISSUE: Text Search Returns No Results
CAUSE: Index not created or wrong weights
SOLUTION:
  1. Verify text index exists: db.articles.listIndexes()
  2. Check if documents have text fields
  3. Recreate index with proper weights

### ISSUE: Slow Aggregations
CAUSE: Non-indexed stage or large dataset
SOLUTION:
  1. Add $match early in pipeline (for filtering)
  2. Use $limit to reduce docs
  3. Use view instead of running aggregation repeatedly

# ============ SCALING STRATEGY ============

## When Database Grows Beyond 10M Documents

Consider:
1. SHARDING by {category: 1, createdAt: -1}
   - Distributes load across multiple servers
   - Must be planned carefully
   - Irreversible decision

2. ARCHIVING old articles
   - Move articles >1 year old to archive collection
   - Use separate archive database

3. READ REPLICAS
   - Offload slow aggregations to secondary nodes
   - Read from replicas, write to primary

4. CACHING LAYER (Redis)
   - Cache frequently accessed articles (homepage, trending)
   - Invalidate on publish/update

# ============ BEST PRACTICES SUMMARY ============

✅ DO:
  - Use indices for all filtering operations
  - Leverage compound indices for multiple predicates
  - Use projection to limit returned data
  - Batch inserts for multiple documents
  - Configure TTL for automatic cleanup
  - Monitor slow query logs regularly
  - Test queries with explain() before production

❌ DON'T:
  - Create indices on low-cardinality fields alone
  - Use aggregation for simple queries
  - Store large unrelated data in same document
  - Ignore index bloat over time
  - Query without limits (pagination)
  - Create more than one text index per collection

# ============ REFERENCES ============

MongoDB Documentation:
  - Index Design: https://docs.mongodb.com/manual/core/index-design/
  - Explain Plan: https://docs.mongodb.com/manual/reference/method/db.collection.explain/
  - Query Optimization: https://docs.mongodb.com/manual/core/query-optimization/
  - TTL Indices: https://docs.mongodb.com/manual/core/index-ttl/
  - Compound Indices: https://docs.mongodb.com/manual/core/index-compound/
"""
