# 🎯 Database Index Strategy & Query Patterns

## Visual Overview of Index Strategy

```
ARTICLES COLLECTION
│
├─ UNIQUE INDICES (Lookups)
│  └─ slug [UNIQUE]
│     └─ .find({slug: "article-title"})  →  <5ms
│
├─ FILTER INDICES (Categorical Data)
│  ├─ status [Very Low Cardinality]
│  │  └─ published, pending_review, draft, approved, archived, rejected (6 values)
│  │
│  ├─ category [Low Cardinality]
│  │  └─ technology, business, science, startup... (20-50 values)
│  │
│  ├─ ai_generated [Very Low Cardinality]
│  │  └─ true, false (2 values)
│  │
│  └─ source_url [Very High Cardinality - SPARSE]
│     └─ Only indexes non-null URLs (saves space)
│
├─ SORT INDICES (Time-series Data)
│  ├─ createdAt DESC
│  │  └─ .find({}).sort({createdAt: -1})  →  <20ms
│  │
│  ├─ publishedAt DESC [SPARSE - unpublished have null]
│  │  └─ .find({status: "published"}).sort({publishedAt: -1})  →  <20ms
│  │
│  └─ views DESC
│     └─ .find({status: "published"}).sort({views: -1})  →  <10ms
│
├─ COMPOUND INDICES (Multi-condition Queries)
│  ├─ status + publishedAt
│  │  └─ .find({status: "published"}).sort({publishedAt: -1})  →  <10ms
│  │
│  ├─ category + status + publishedAt ← MOST USED
│  │  └─ .find({category: "tech", status: "published"}).sort({publishedAt: -1}).limit(50)
│  │     └─ <10ms (covers filter + sort in single index)
│  │
│  ├─ status + views
│  │  └─ .find({status: "published"}).sort({views: -1}).limit(20)  →  <10ms
│  │
│  ├─ status + createdAt
│  │  └─ .find({status: "pending_review"}).sort({createdAt: -1})  →  <5ms
│  │
│  └─ ai_generated + status
│     └─ .find({ai_generated: true, status: "published"})  →  <10ms
│
├─ TEXT SEARCH INDEX (Full-text Search)
│  ├─ Fields: title, summary, tags, content
│  ├─ Weights: title(10x) > tags(8x) > summary(5x) > content(1x)
│  ├─ Features: Stemming, Stop words, Scoring
│  └─ .find({$text: {$search: "machine learning"}})  →  <50ms
│
└─ TTL INDEX (Auto-cleanup)
   ├─ createdAt + Partial Filter (status: "draft" or "rejected")
   ├─ Auto-deletes after 30 days
   ├─ Runs every 60 seconds (background)
   └─ Saves storage by not keeping drafts
```

## Query Pattern → Index Mapping

### MOST COMMON QUERIES

```
1️⃣  "Get published articles in a category, sorted by date"
    Query:  db.articles.find({category: "tech", status: "published"})
            .sort({publishedAt: -1}).limit(50)
    Index:  idx_category_status_date (category, status, publishedAt DESC)
    Time:   <10ms ⚡
    ESR:    ✓ Equality (category, status) + Sort (publishedAt) + Range (limit)

2️⃣  "Get trending articles (most viewed)"
    Query:  db.articles.find({status: "published"})
            .sort({views: -1}).limit(20)
    Index:  idx_status_views
    Time:   <10ms ⚡
    Uses:   Homepage/Trending Section

3️⃣  "Get articles by slug (direct lookup)"
    Query:  db.articles.findOne({slug: "article-title"})
    Index:  idx_slug_unique [UNIQUE]
    Time:   <5ms ⚡
    Uses:   Article detail page

4️⃣  "Get pending articles (admin workflow)"
    Query:  db.articles.find({status: "pending_review"})
            .sort({createdAt: -1})
    Index:  idx_status_createdAt
    Time:   <5ms ⚡
    Uses:   Admin dashboard review queue

5️⃣  "Full-text search"
    Query:  db.articles.find({$text: {$search: "keyword"}})
            .limit(20)
    Index:  idx_fulltext_search (text index)
    Time:   <50ms ⚡
    Uses:   Search functionality
    Features: Stemming, scoring, stop words
```

### COMPOUND INDEX STRATEGY (ESR Rule)

MongoDB's ESR (Equality, Sort, Range) rule for optimal indices:

```
INDEX KEY ORDER MATTERS!

Example: Query {category: "tech", status: "published"}.sort({publishedAt: -1})

✅ OPTIMAL: idx_category_status_date (category, status, publishedAt DESC)
   └─ Equality on category (filter out categories)
   └─ Equality on status (filter by status)
   └─ Sort on publishedAt (pre-sorted by index)
   └─ Result: ~10ms ⚡

❌ NOT OPTIMAL: idx_status_publishedAt (status, publishedAt DESC)
   └─ Doesn't start with category
   └─ Must scan more documents
   └─ Result: ~100ms (10x slower)

❌ WRONG ORDER: idx_publishedAt_category_status
   └─ Starts with sort field (wrong)
   └─ Must scan all documents, then sort
   └─ Result: ~1000ms (100x slower)
```

## Index Size & Storage Impact

```
Storage for 100,000 articles:

Without indices:
  Articles: ~500 MB (compressed)
  Total: ~500 MB

With 14 indices:
  Articles: ~500 MB
  Indices: ~150 MB (30% of data size)
  Total: ~650 MB

Cost of indices: +30% storage for <10x query speedup (WORTH IT!)
```

## Cardinality Analysis

Optimal index cardinality (for efficiency):

```
HIGH CARDINALITY (Good for indices)
  ├─ slug: 100,000 unique values (every document unique)  ✅ INDEX IT
  ├─ createdAt: 100,000 unique values (different times)   ✅ INDEX IT
  ├─ source_url: 90,000 unique values (different sources) ✅ INDEX IT (SPARSE)
  └─ views: 50,000 unique values (different counts)        ✅ INDEX IT

MEDIUM CARDINALITY
  ├─ category: 30 unique values (30 categories)
  └─ ai_generated: 2 unique values (true/false)

LOW CARDINALITY (Use as equality in compound indices)
  ├─ status: 6 unique values (draft, published, etc.)
  ├─ category: 30 unique values
  └─ language: 5 unique values (en, te, ta, kn, ml)

RULE: Lead compound indices with high or medium cardinality,
end with sort fields. Avoid starting with low cardinality.
```

## Query Execution Plans

### Fast Query (using index)

```
Query: db.articles.find({status: "published"}).sort({publishedAt: -1}).limit(20)

Execution Plan:
  ├─ INDEX SCAN: idx_status_publishedAt
  │  ├─ Start at: {status: "published"}
  │  └─ Direction: publishedAt DESC (already sorted!)
  │
  ├─ FETCH: documents (only first 20 needed)
  │  └─ Total fetched: 20 documents
  │
  └─ RETURN: 20 articles

Time: <10ms
Memory: ~100 KB (only 20 docs in memory)
I/O: 1 index traversal + 1 document fetch
```

### Slow Query (no index)

```
Query: db.articles.find({category: "tech"}).sort({views: -1}).limit(20)
WITHOUT proper index

Execution Plan:
  ├─ COLLECTION SCAN: Read ALL documents (100,000!)
  │  └─ Filter: category == "tech" (1,000 docs match)
  │
  ├─ SORT IN MEMORY: Sort by views desc
  │  └─ Load 100,000 documents into memory
  │  └─ Compare and sort (O(n log n) = 1.7 million comparisons)
  │
  ├─ LIMIT: Take first 20 from sorted set
  │  └─ Fetch 20 documents
  │
  └─ RETURN: 20 articles

Time: 100-500ms (10-50x slower!)
Memory: ~500 MB (all docs in RAM)
I/O: Full collection scan
⚠️ Problem: Can't use limit before sort!
```

## Index Usage Recommendations

```
ARTICLES QUERIES (Audience: Public/Admin)

Homepage - Featured Articles:
  Query: {status: "published", category: ...}.sort({publishedAt: -1}).limit(20)
  Index: idx_category_status_date ✅
  Speed: <10ms ⚡

Trending Section:
  Query: {status: "published"}.sort({views: -1}).limit(10)
  Index: idx_status_views ✅
  Speed: <10ms ⚡

Category Browse:
  Query: {category: "tech", status: "published"}.sort({publishedAt: -1})
  Index: idx_category_status_date ✅
  Speed: <15ms ⚡

Article Detail:
  Query: {slug: "article-title"}
  Index: idx_slug_unique ✅
  Speed: <5ms ⚡

Search:
  Query: {$text: {$search: "keyword"}}
  Index: idx_fulltext_search ✅
  Speed: <50ms ⚡

ADMIN QUERIES

Pending Review:
  Query: {status: "pending_review"}.sort({createdAt: -1})
  Index: idx_status_createdAt ✅
  Speed: <5ms ⚡

Bulk Operations:
  Query: {_id: {$in: [...]}, status: "..."}
  Index: idx_status ✅ (or just _id index)
  Speed: <20ms ⚡

ANALYTICS QUERIES

Views for Article:
  Query: {article_slug: "slug"}
  Index: idx_article_slug ✅
  Speed: <10ms ⚡

Analytics Timeline:
  Query: {article_slug: "slug"}.sort({timestamp: -1})
  Index: idx_article_timestamp ✅
  Speed: <20ms ⚡
```

## Visual Query Performance Chart

```
Query Performance Over Time (10K → 10M documents)

     10,000 docs       100K docs       1M docs        10M docs
     ────────────────  ────────────    ────────────   ────────────
     │                 │                │              │
 5ms │●                │●               │●             │●   ← WITH INDEX
     │ \               │ \              │ \            │ \
10ms │  \              │  \             │  \           │  \
     │   ●             │   ●            │   ●          │   ●
50ms │                 │                │              │
     │                 │    ●           │    ●         │    ●
100ms│                 │     \          │     \        │     \
     │                 │      ●         │      ●       │      ●
500ms│                 │              ╱        ╱       │        ╱
     │                 │    ╱────────╱        ╱        │      ╱────
  1s │                 │  ╱                  ╱         │    ╱
     │                 │╱                   ╱          │  ╱
  5s │                 ●────────────────────────────────●─────── ← NO INDEX
     └─────────────────────────────────────────────────────────
     
Legend:
  ● = Query execution time
  ← WITH INDEX: Remains <10ms even at 10M docs ✅
  ← NO INDEX: Grows from 100ms to 5s+ (unusable) ❌
```

## Maintenance Recommendations

```
DAILY:
  ✓ Monitor query performance
  ✓ Check for slow queries (>100ms)

WEEKLY:
  ✓ Analyze index effectiveness: python setup_db.py --analyze
  ✓ Check index sizes: db.articles.aggregate({$indexStats: {}})

MONTHLY:
  ✓ Rebuild fragmented indices: db.articles.reIndex()
  ✓ Clean old data: python setup_db.py --cleanup
  ✓ Review query logs for new optimization opportunities

QUARTERLY:
  ✓ Full database optimization review
  ✓ Plan for sharding if >50M documents
  ✓ Archive old analytics if >100M events
```

---

**For detailed implementation details, see:**
- `DATABASE_OPTIMIZATION.md` - Complete index specifications
- `DATABASE_SETUP_GUIDE.md` - Setup and usage instructions
- `db_optimization.py` - Pre-optimized query helpers
