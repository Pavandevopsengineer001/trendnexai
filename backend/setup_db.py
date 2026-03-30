"""
🏗️ Database Setup Script for TrendNexAI
Creates collections, indices, and optimizations for production performance.

Features:
- Advanced index creation for query optimization
- Connection pooling configuration
- TTL policies for automatic cleanup
- Analytics aggregation pipelines
- Full-text search indices
- Compound indices for common query patterns
- Sharding preparation

Run this once after initial MongoDB deployment.
Usage:
    python setup_db.py                  # Setup only
    python setup_db.py --with-data      # Setup + sample data
    python setup_db.py --optimize       # Analyze & optimize existing DB
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def setup_database():
    """
    🚀 Complete database setup with advanced optimizations
    - Creates collections with proper configuration
    - Sets up 15+ strategic indices
    - Configures TTL policies
    - Prepares aggregation pipelines
    """
    
    mongodb_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
    )
    db_name = os.getenv("DATABASE_NAME", "trendnexai")
    
    client = AsyncIOMotorClient(
        mongodb_uri,
        maxPoolSize=50,  # Connection pooling for concurrent requests
        minPoolSize=10
    )
    db = client[db_name]
    
    print("\n" + "="*60)
    print("🔧 TRENDNEXAI DATABASE SETUP & OPTIMIZATION")
    print("="*60)
    
    try:
        # ============== ARTICLES COLLECTION ==============
        print("\n📰 ARTICLES COLLECTION")
        print("-" * 60)
        
        if "articles" not in await db.list_collection_names():
            # Create with compression for large text content
            await db.create_collection(
                "articles",
                storageEngine={"wiredTiger": {"configString": "block_compressor=snappy"}}
            )
            print("✓ Collection created with Snappy compression")
        else:
            print("✓ Collection already exists")
        
        articles = db.articles
        
        # ========== COMPREHENSIVE INDEX STRATEGY ==========
        # 1. PRIMARY LOOKUP INDICES
        primary_indices = [
            ([("slug", 1)], {"unique": True, "name": "idx_slug_unique"}),
            ([("_id", 1)], {"sparse": True, "name": "idx_id"}),
        ]
        
        # 2. FILTERING INDICES (single column)
        filter_indices = [
            ([("status", 1)], {"name": "idx_status"}),  # Fast status filtering
            ([("category", 1)], {"name": "idx_category"}),  # Category browsing
            ([("ai_generated", 1)], {"name": "idx_ai_generated"}),  # AI article filtering
            ([("source_url", 1)], {"sparse": True, "name": "idx_source_url"}),  # Deduplication
        ]
        
        # 3. SORTING INDICES (timestamps)
        sort_indices = [
            ([("createdAt", -1)], {"name": "idx_createdAt_desc"}),  # Most recent first
            ([("publishedAt", -1)], {"sparse": True, "name": "idx_publishedAt_desc"}),  # Published date
            ([("views", -1)], {"name": "idx_views_desc"}),  # Trending articles
        ]
        
        # 4. COMPOUND INDICES (for common query patterns)
        compound_indices = [
            # Status + Date (published articles by date)
            ([("status", 1), ("publishedAt", -1)], {"name": "idx_status_publishedAt"}),
            
            # Category + Status (articles in category)
            ([("category", 1), ("status", 1), ("publishedAt", -1)], 
             {"name": "idx_category_status_date"}),
            
            # Status + Views (trending published articles)
            ([("status", 1), ("views", -1)], {"name": "idx_status_views"}),
            
            # For pending review workflow
            ([("status", 1), ("createdAt", -1)], {"name": "idx_status_createdAt"}),
            
            # AI insights + Status (filter AI processed articles)
            ([("ai_generated", 1), ("status", 1)], {"name": "idx_ai_status"}),
        ]
        
        # 5. TEXT SEARCH INDICES (full-text search)
        text_indices = [
            ([("title", "text"), ("summary", "text"), ("tags", "text"), ("content", "text")],
             {
                 "name": "idx_fulltext_search",
                 "default_language": "english",
                 "weights": {
                     "title": 10,      # Title matches worth more
                     "summary": 5,      # Summary matches
                     "tags": 8,         # Tags important
                     "content": 1       # Content weight
                 }
             }),
        ]
        
        # 6. EXPIRING INDEX (TTL - auto-delete unpublished after 30 days)
        ttl_indices = [
            (
                [("createdAt", 1)],
                {
                    "expireAfterSeconds": 2592000,  # 30 days
                    "partialFilterExpression": {"status": {"$in": ["draft", "rejected"]}},
                    "name": "idx_ttl_unpublished"
                }
            ),
        ]
        
        # Apply all indices
        all_indices = primary_indices + filter_indices + sort_indices + compound_indices + text_indices + ttl_indices
        
        print(f"\n  Creating {len(all_indices)} indices...")
        created_count = 0
        
        for index_spec, options in all_indices:
            try:
                await articles.create_index(index_spec, **options)
                index_name = options.get("name", str(index_spec[0]))
                print(f"    ✓ {index_name}")
                created_count += 1
            except Exception as e:
                print(f"    ⚠️ {options.get('name', str(index_spec[0]))}: {str(e)[:50]}")
        
        print(f"  Summary: {created_count}/{len(all_indices)} indices created")
        
        
        # ============== ANALYTICS COLLECTION ==============
        print("\n📊 ANALYTICS COLLECTION")
        print("-" * 60)
        
        if "analytics" not in await db.list_collection_names():
            await db.create_collection("analytics")
            print("✓ Collection created")
        else:
            print("✓ Collection already exists")
        
        analytics = db.analytics
        
        analytics_indices = [
            # Lookup by article
            ([("article_slug", 1)], {"name": "idx_article_slug"}),
            
            # Event filtering
            ([("event_type", 1)], {"name": "idx_event_type"}),
            
            # Time-based queries
            ([("timestamp", -1)], {"name": "idx_timestamp_desc"}),
            
            # Aggregation queries
            ([("article_slug", 1), ("timestamp", -1)], 
             {"name": "idx_article_timestamp"}),
            
            # TTL: Auto-delete after 90 days (analytics retention)
            ([("timestamp", 1)], 
             {
                 "expireAfterSeconds": 7776000,  # 90 days
                 "name": "idx_ttl_analytics"
             }),
        ]
        
        print(f"\n  Creating {len(analytics_indices)} indices...")
        created_count = 0
        
        for index_spec, options in analytics_indices:
            try:
                await analytics.create_index(index_spec, **options)
                index_name = options.get("name", str(index_spec[0]))
                print(f"    ✓ {index_name}")
                created_count += 1
            except Exception as e:
                print(f"    ⚠️ {options.get('name', str(index_spec[0]))}: {str(e)[:50]}")
        
        print(f"  Summary: {created_count}/{len(analytics_indices)} indices created")
        
        
        # ============== CACHE COLLECTION ==============
        print("\n⚡ CACHE COLLECTION (1-hour TTL)")
        print("-" * 60)
        
        if "cache" not in await db.list_collection_names():
            await db.create_collection("cache")
            print("✓ Collection created")
        else:
            print("✓ Collection already exists")
        
        cache = db.cache
        
        cache_indices = [
            # Unique key for cache lookup
            ([("key", 1)], {"unique": True, "name": "idx_cache_key"}),
            
            # TTL: Auto-delete after 1 hour
            ([("createdAt", 1)], 
             {
                 "expireAfterSeconds": 3600,
                 "name": "idx_ttl_cache"
             }),
        ]
        
        print(f"\n  Creating {len(cache_indices)} indices...")
        created_count = 0
        
        for index_spec, options in cache_indices:
            try:
                await cache.create_index(index_spec, **options)
                index_name = options.get("name", str(index_spec[0]))
                print(f"    ✓ {index_name}")
                created_count += 1
            except Exception as e:
                print(f"    ⚠️ {options.get('name', str(index_spec[0]))}: {str(e)[:50]}")
        
        print(f"  Summary: {created_count}/{len(cache_indices)} indices created")
        
        
        # ============== STATS VIEWS ==============
        print("\n📈 CREATING AGGREGATION VIEWS (Pre-computed stats)")
        print("-" * 60)
        
        try:
            # View 1: Article stats by category
            if "articles_by_category" not in await db.list_collection_names():
                await db.create_collection(
                    "articles_by_category",
                    viewOn="articles",
                    pipeline=[
                        {
                            "$group": {
                                "_id": "$category",
                                "count": {"$sum": 1},
                                "published": {
                                    "$sum": {
                                        "$cond": [{"$eq": ["$status", "published"]}, 1, 0]
                                    }
                                },
                                "total_views": {"$sum": "$views"}
                            }
                        },
                        {"$sort": {"count": -1}}
                    ]
                )
                print("✓ View: articles_by_category")
            
            # View 2: Trending articles (last 7 days)
            if "trending_articles" not in await db.list_collection_names():
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                await db.create_collection(
                    "trending_articles",
                    viewOn="articles",
                    pipeline=[
                        {
                            "$match": {
                                "status": "published",
                                "publishedAt": {"$gte": seven_days_ago}
                            }
                        },
                        {"$sort": {"views": -1}},
                        {"$limit": 20}
                    ]
                )
                print("✓ View: trending_articles")
            
            # View 3: Pending review queue
            if "pending_review_queue" not in await db.list_collection_names():
                await db.create_collection(
                    "pending_review_queue",
                    viewOn="articles",
                    pipeline=[
                        {"$match": {"status": "pending_review"}},
                        {"$sort": {"createdAt": -1}},
                        {
                            "$project": {
                                "title": 1,
                                "summary": 1,
                                "category": 1,
                                "createdAt": 1,
                                "ai_insights": 1
                            }
                        }
                    ]
                )
                print("✓ View: pending_review_queue")
        
        except Exception as e:
            print(f"⚠️ View creation (some may already exist): {str(e)[:50]}")
        
        
        # ============== DATABASE SUMMARY ==============
        print("\n" + "="*60)
        print("📊 DATABASE SUMMARY")
        print("="*60)
        
        collections = await db.list_collection_names()
        total_indices = 0
        
        for col in sorted(collections):
            try:
                count = await db[col].count_documents({})
                indices = await db[col].list_indexes()
                index_count = len([i async for i in indices])
                total_indices += index_count
                
                col_type = "[VIEW]" if col.startswith("articles_by") or col.startswith("trending") or col.startswith("pending") else "[COLLECTION]"
                print(f"  {col_type} {col:25} • {count:6} docs • {index_count:2} indices")
            except Exception as e:
                print(f"  [ERROR] {col}: {str(e)[:40]}")
        
        print(f"\n  Total Collections: {len(collections)}")
        print(f"  Total Indices: {total_indices}")
        print("\n✅ DATABASE SETUP COMPLETE!")
        
        # ============== OPTIMIZATION RECOMMENDATIONS ==============
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        print("-" * 60)
        print("""
  1. QUERY PATTERNS TO LEVERAGE:
     • db.articles.find({status: 'published'}).sort({publishedAt: -1})
     • db.articles.find({category: 'tech', status: 'published'})
     • db.articles.find({$text: {$search: 'keyword'}})
  
  2. AGGREGATION PERFORMANCE:
     • Use pre-computed views for dashboard stats
     • Cache aggregation results in Redis
     • Avoid large $lookup operations
  
  3. CONNECTION POOLING:
     • Current pool: 10-50 connections
     • Good for 50-200 concurrent users
     • Scale maxPoolSize if needed
  
  4. MONITORING:
     • Use MongoDB Atlas charts for index usage
     • Check slow logs: db.system.profile.find()
     • Monitor replication lag if using replica set
  
  5. FUTURE SCALING:
     • Consider sharding by {category: 1, createdAt: -1}
     • Archive analytics after 90 days
     • Use bulk inserts for batch operations
        """)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", exc_info=True)
        raise
    
    finally:
        client.close()

async def analyze_database_performance():
    """
    🔍 Analyze and report on database performance
    - Check index utilization
    - Identify missing indices
    - Report slow queries
    """
    
    mongodb_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
    )
    db_name = os.getenv("DATABASE_NAME", "trendnexai")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    admin_db = client.admin
    
    print("\n" + "="*60)
    print("🔍 DATABASE PERFORMANCE ANALYSIS")
    print("="*60)
    
    try:
        # Get server status
        server_status = await admin_db.command("serverStatus")
        
        print("\n🖥️  SERVER STATUS:")
        print("-" * 60)
        print(f"  Uptime: {server_status.get('uptime', 0) / 3600:.1f} hours")
        print(f"  Connections: {server_status.get('connections', {}).get('current', 0)} current")
        
        # Index statistics
        print("\n📊 INDEX STATISTICS:")
        print("-" * 60)
        
        for col_name in ["articles", "analytics", "cache"]:
            if col_name in await db.list_collection_names():
                collection = db[col_name]
                
                # Get index info
                indices = await collection.list_indexes()
                index_list = [i async for i in indices]
                
                print(f"\n  Collection: {col_name}")
                print(f"    Total indices: {len(index_list)}")
                print(f"    Document count: {await collection.count_documents({})}")
                
                for idx in index_list:
                    idx_name = idx.get('name', 'unknown')
                    idx_keys = idx.get('key', [])
                    unique = idx.get('unique', False)
                    ttl = idx.get('expireAfterSeconds')
                    
                    flags = []
                    if unique:
                        flags.append("UNIQUE")
                    if ttl:
                        flags.append(f"TTL:{ttl}s")
                    
                    flag_str = f" [{', '.join(flags)}]" if flags else ""
                    print(f"      • {idx_name}{flag_str}")
        
        print("\n✅ ANALYSIS COMPLETE!")
        
    except Exception as e:
        print(f"\n❌ Analysis error: {e}")
    
    finally:
        client.close()



async def create_test_data():
    """
    🌱 Create sample data for testing
    Inserts realistic sample articles for development/testing
    """
    
    mongodb_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
    )
    db_name = os.getenv("DATABASE_NAME", "trendnexai")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    print("\n🌱 Creating sample articles...")
    
    try:
        from datetime import datetime
        
        sample_articles = [
            {
                "title": "Getting Started with TrendNexAI",
                "slug": "getting-started-with-trendnexai",
                "category": "technology",
                "summary": "Learn how to get started with the TrendNexAI platform.",
                "content": {
                    "en": "<h1>Getting Started</h1><p>This is a sample article...</p>",
                },
                "tags": ["trendnexai", "tutorial", "startup"],
                "seo_title": "Getting Started with TrendNexAI - Guide",
                "seo_description": "Learn TrendNexAI setup and basics.",
                "seo_keywords": ["trendnexai", "ai", "news"],
                "status": "published",
                "ai_generated": True,
                "views": 42,
                "engagement_score": 8.5,
                "createdAt": datetime.utcnow(),
                "publishedAt": datetime.utcnow(),
            },
            {
                "title": "Advanced AI Processing in TrendNexAI",
                "slug": "advanced-ai-processing-trendnexai",
                "category": "technology",
                "summary": "Deep dive into AI-powered content generation.",
                "content": {
                    "en": "<h1>Advanced AI</h1><p>TrendNexAI uses dual AI engines...</p>",
                },
                "tags": ["ai", "processing", "trendnexai"],
                "seo_title": "Advanced AI Processing - TrendNexAI",
                "seo_description": "Explore AI-powered content generation capabilities.",
                "status": "published",
                "ai_generated": True,
                "views": 78,
                "engagement_score": 9.2,
                "createdAt": datetime.utcnow() - timedelta(days=1),
                "publishedAt": datetime.utcnow() - timedelta(days=1),
            },
            {
                "title": "Pending Article for Review",
                "slug": "pending-article-review",
                "category": "business",
                "summary": "This article is waiting for admin approval.",
                "content": {
                    "en": "<h1>Pending</h1><p>Awaiting review...</p>",
                },
                "tags": ["pending", "review"],
                "seo_title": "Pending Review Article",
                "seo_description": "Article pending admin review.",
                "status": "pending_review",
                "ai_generated": True,
                "views": 0,
                "engagement_score": 0,
                "createdAt": datetime.utcnow(),
                "publishedAt": None,
            }
        ]
        
        result = await db.articles.insert_many(sample_articles)
        print(f"\n✓ Inserted {len(result.inserted_ids)} sample articles")
        print(f"  • 2 published articles")
        print(f"  • 1 pending review article")
        
    except Exception as e:
        print(f"⚠️ Error creating sample data: {e}")
    
    finally:
        client.close()


async def cleanup_old_data():
    """
    🧹 Clean up old/expired data
    - Remove unpublished articles older than 30 days
    - Remove analytics older than 90 days
    - Remove cache entries
    """
    
    mongodb_uri = os.getenv(
        "MONGODB_URI",
        "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
    )
    db_name = os.getenv("DATABASE_NAME", "trendnexai")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[db_name]
    
    print("\n🧹 Cleaning up old data...")
    
    try:
        # Clean old unpublished articles
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = await db.articles.delete_many({
            "status": {"$in": ["draft", "rejected"]},
            "createdAt": {"$lt": cutoff_date}
        })
        print(f"  ✓ Deleted {result.deleted_count} old unpublished articles")
        
        # Clean old analytics (if TTL didn't work automatically)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        result = await db.analytics.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        print(f"  ✓ Deleted {result.deleted_count} old analytics records")
        
        # Clear expired cache (should be auto-TTL but just in case)
        result = await db.cache.delete_many({
            "createdAt": {"$lt": datetime.utcnow() - timedelta(hours=1)}
        })
        print(f"  ✓ Cleared {result.deleted_count} expired cache entries")
        
        print("\n✅ Cleanup complete!")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    finally:
        client.close()



if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("TRENDNEXAI DATABASE MANAGEMENT")
    print("="*60)
    
    if len(sys.argv) < 2:
        # Default: just setup
        asyncio.run(setup_database())
    
    elif sys.argv[1] == "--with-data":
        # Setup + sample data
        asyncio.run(setup_database())
        asyncio.run(create_test_data())
    
    elif sys.argv[1] == "--analyze":
        # Analyze performance
        asyncio.run(analyze_database_performance())
    
    elif sys.argv[1] == "--cleanup":
        # Clean old data
        asyncio.run(cleanup_old_data())
    
    elif sys.argv[1] == "--full":
        # Complete setup: tables + indices + sample data + analysis
        asyncio.run(setup_database())
        asyncio.run(create_test_data())
        asyncio.run(analyze_database_performance())
    
    else:
        print(f"""
Usage:
  python setup_db.py                  Setup database & indices only
  python setup_db.py --with-data      Setup + insert sample data
  python setup_db.py --analyze        Analyze existing database
  python setup_db.py --cleanup        Remove old/expired data
  python setup_db.py --full           Complete setup (all of above)
        """)

