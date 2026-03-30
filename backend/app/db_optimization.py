"""
⚡ Database Optimization Utilities for TrendNexAI

Provides best-practice helpers for:
- Query optimization patterns
- Aggregation pipelines
- Connection pooling strategies
- Performance monitoring
- Index utilization analysis

Usage:
    from app.db_optimization import get_optimized_articles, get_trending_articles
    
    # Efficient query example
    articles = await get_optimized_articles(
        status="published",
        category="technology",
        limit=20,
        skip=0
    )
"""

import logging
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import pymongo

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """
    🚀 Database Query Optimization Helper
    
    Provides pre-optimized query patterns to leverage
    the index strategy from setup_db.py
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.articles = db.articles
        self.analytics = db.analytics
    
    # ========== ARTICLE QUERIES ==========
    
    async def get_published_articles(
        self,
        limit: int = 20,
        skip: int = 0,
        category: Optional[str] = None,
        sort_by: str = "publishedAt"
    ) -> List[Dict[str, Any]]:
        """
        🎯 Get published articles efficiently
        
        Uses compound index: (status, publishedAt, -1)
        or (category, status, publishedAt, -1)
        
        Args:
            limit: Max articles to return
            skip: Pagination offset
            category: Filter by category (optional)
            sort_by: Sort field (publishedAt or views)
        
        Returns:
            List of published article documents
        """
        
        query = {"status": "published"}
        
        if category:
            query["category"] = category
        
        # Use appropriate compound index
        sort_order = pymongo.DESCENDING if sort_by == "publishedAt" else pymongo.DESCENDING
        
        articles = await self.articles.find(query) \
            .sort([(sort_by, sort_order)]) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    async def get_trending_articles(
        self,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        📈 Get trending articles (most viewed in last N days)
        
        Uses compound index: (status, views, -1)
        
        Args:
            days: Look back window
            limit: Max articles to return
        
        Returns:
            List of trending articles sorted by views
        """
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = {
            "status": "published",
            "publishedAt": {"$gte": cutoff_date}
        }
        
        articles = await self.articles.find(query) \
            .sort([("views", pymongo.DESCENDING)]) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    async def get_pending_articles(
        self,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        ⏳ Get articles pending review
        
        Uses index: (status, createdAt, -1)
        
        Args:
            limit: Max articles to return
            skip: Pagination offset
        
        Returns:
            Pending articles (newest first)
        """
        
        articles = await self.articles.find({"status": "pending_review"}) \
            .sort([("createdAt", pymongo.DESCENDING)]) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    async def search_articles(
        self,
        search_text: str,
        limit: int = 20,
        status: Optional[str] = "published"
    ) -> List[Dict[str, Any]]:
        """
        🔍 Full-text search articles efficiently
        
        Uses text index on: title, summary, tags, content
        Weight distribution: title(10) > tags(8) > summary(5) > content(1)
        
        Args:
            search_text: Search query
            limit: Max results
            status: Filter by status (None = all)
        
        Returns:
            Matching articles sorted by relevance
        """
        
        query = {"$text": {"$search": search_text}}
        
        if status:
            query["status"] = status
        
        articles = await self.articles.find(query) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    async def get_articles_by_category(
        self,
        category: str,
        status: str = "published",
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        📂 Get articles in specific category
        
        Uses compound index: (category, status, publishedAt, -1)
        
        Args:
            category: Category name
            status: Filter by status
            limit: Max articles
            skip: Pagination offset
        
        Returns:
            Articles in category
        """
        
        articles = await self.articles.find({
            "category": category,
            "status": status
        }) \
            .sort([("publishedAt", pymongo.DESCENDING)]) \
            .skip(skip) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    async def get_ai_generated_articles(
        self,
        status: str = "published",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        🤖 Get AI-generated articles
        
        Uses index: (ai_generated, status)
        
        Args:
            status: Filter by status
            limit: Max articles
        
        Returns:
            AI-generated articles
        """
        
        articles = await self.articles.find({
            "ai_generated": True,
            "status": status
        }) \
            .sort([("publishedAt", pymongo.DESCENDING)]) \
            .limit(limit) \
            .to_list(length=limit)
        
        return articles
    
    # ========== ANALYTICS QUERIES ==========
    
    async def get_article_views(self, article_slug: str) -> int:
        """
        👁️ Get total views for an article
        
        Uses index: (article_slug)
        
        Args:
            article_slug: Article slug
        
        Returns:
            Total view count
        """
        
        article = await self.articles.find_one({"slug": article_slug})
        return article.get("views", 0) if article else 0
    
    async def increment_article_views(self, article_slug: str) -> None:
        """
        ➕ Increment view count for article
        
        Args:
            article_slug: Article slug
        """
        
        await self.articles.update_one(
            {"slug": article_slug},
            {"$inc": {"views": 1}},
            upsert=False
        )
    
    async def get_analytics_for_article(
        self,
        article_slug: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        📊 Get analytics events for article
        
        Uses compound index: (article_slug, timestamp, -1)
        
        Args:
            article_slug: Article slug
            days: Look back window
        
        Returns:
            Analytics events
        """
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        events = await self.analytics.find({
            "article_slug": article_slug,
            "timestamp": {"$gte": cutoff_date}
        }) \
            .sort([("timestamp", pymongo.DESCENDING)]) \
            .to_list(length=None)
        
        return events
    
    # ========== AGGREGATION PIPELINES ==========
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        📈 Get comprehensive database statistics
        
        Efficient aggregation pipeline for dashboard metrics
        
        Returns:
            Statistics dictionary
        """
        
        pipeline = [
            {
                "$facet": {
                    "total_articles": [
                        {"$count": "count"}
                    ],
                    "by_status": [
                        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ],
                    "by_category": [
                        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ],
                    "total_views": [
                        {"$group": {"_id": None, "total": {"$sum": "$views"}}}
                    ],
                    "ai_generated": [
                        {"$match": {"ai_generated": True}},
                        {"$count": "count"}
                    ],
                    "most_viewed": [
                        {"$match": {"status": "published"}},
                        {"$sort": {"views": -1}},
                        {"$limit": 5},
                        {"$project": {"title": 1, "views": 1}}
                    ]
                }
            }
        ]
        
        result = await self.articles.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {}
    
    async def get_category_statistics(self) -> List[Dict[str, Any]]:
        """
        📊 Get statistics by category
        
        Efficient aggregation for category insights
        
        Returns:
            List of category stats
        """
        
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "total_articles": {"$sum": 1},
                    "published": {
                        "$sum": {"$cond": [{"$eq": ["$status", "published"]}, 1, 0]}
                    },
                    "pending": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pending_review"]}, 1, 0]}
                    },
                    "total_views": {"$sum": "$views"},
                    "avg_views": {"$avg": "$views"}
                }
            },
            {"$sort": {"total_articles": -1}}
        ]
        
        stats = await self.articles.aggregate(pipeline).to_list(length=None)
        return stats
    
    # ========== BULK OPERATIONS ==========
    
    async def bulk_update_status(
        self,
        article_ids: List[str],
        new_status: str
    ) -> int:
        """
        🔄 Bulk update article status
        
        Efficient bulk operation for admin operations
        
        Args:
            article_ids: List of article IDs
            new_status: New status value
        
        Returns:
            Number of updated articles
        """
        
        from bson.objectid import ObjectId
        
        result = await self.articles.update_many(
            {"_id": {"$in": [ObjectId(id_) for id_ in article_ids]}},
            {
                "$set": {
                    "status": new_status,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count
    
    async def bulk_delete_articles(
        self,
        article_ids: List[str]
    ) -> int:
        """
        🗑️ Bulk delete articles
        
        Args:
            article_ids: List of article IDs
        
        Returns:
            Number of deleted articles
        """
        
        from bson.objectid import ObjectId
        
        result = await self.articles.delete_many({
            "_id": {"$in": [ObjectId(id_) for id_ in article_ids]}
        })
        
        return result.deleted_count
    
    # ========== INDEX MONITORING ==========
    
    async def get_index_statistics(self) -> Dict[str, Any]:
        """
        📊 Get index usage statistics
        
        Useful for monitoring index effectiveness
        
        Returns:
            Index statistics
        """
        
        stats = {
            "articles": {
                "size": await self._get_collection_size("articles"),
                "indexes": await self._get_indexes("articles")
            },
            "analytics": {
                "size": await self._get_collection_size("analytics"),
                "indexes": await self._get_indexes("analytics")
            }
        }
        
        return stats
    
    async def _get_collection_size(self, collection_name: str) -> int:
        """Get collection size in bytes"""
        stats = await self.db.command("collStats", collection_name)
        return stats.get("size", 0)
    
    async def _get_indexes(self, collection_name: str) -> List[Dict[str, Any]]:
        """Get all indices for collection"""
        collection = self.db[collection_name]
        indices = await collection.list_indexes()
        return [idx async for idx in indices]


# ========== CONVENIENCE FUNCTIONS ==========

async def get_optimized_articles(
    db: AsyncIOMotorDatabase,
    status: str = "published",
    category: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Convenience function for optimized article queries"""
    optimizer = DatabaseOptimizer(db)
    return await optimizer.get_published_articles(
        limit=limit,
        skip=skip,
        category=category
    )


async def get_trending_articles(
    db: AsyncIOMotorDatabase,
    days: int = 7,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Convenience function for trending articles"""
    optimizer = DatabaseOptimizer(db)
    return await optimizer.get_trending_articles(days=days, limit=limit)


async def search_articles(
    db: AsyncIOMotorDatabase,
    query: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Convenience function for article search"""
    optimizer = DatabaseOptimizer(db)
    return await optimizer.search_articles(query, limit=limit)
