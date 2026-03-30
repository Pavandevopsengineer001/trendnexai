"""
🚀 Business Logic Services for TrendNexAI
Handles article processing, storage, AI content generation, and workflow management.

Workflow:
RSS/NewsAPI → Save (PENDING_REVIEW) → Admin Reviews → Approve → Publish → Live

Features:
- ✅ Save articles with AI-generated content
- ✅ Complete approval workflow (pending → approved → published)
- ✅ Bulk status updates for admin operations
- ✅ Optimized queries using database indices
- ✅ Analytics and statistics aggregation
- ✅ View tracking and engagement scoring
"""

from datetime import datetime
from slugify import slugify
from app.db import db
from app.openai_service import generate_article
from app.db_optimization import DatabaseOptimizer  # Performance utilities
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)


async def save_articles_async(articles: list) -> list:
    """
    Save articles to database after AI processing.
    New articles go to PENDING_REVIEW status for admin approval.
    
    Args:
        articles: List of raw articles from news API/RSS
    
    Returns:
        List of saved article documents
    """
    saved = []
    
    for raw_article in articles:
        try:
            title = raw_article.get("title", "").strip()
            if not title:
                logger.warning("Skipping article without title")
                continue
            
            # Generate slug
            slug = slugify(title, separator="-", lowercase=True)
            
            # Check for duplicate by fingerprint
            existing = await db.articles.find_one({
                "$or": [
                    {"slug": slug},
                    {"source_url": raw_article.get("url") or raw_article.get("source_url")}
                ]
            })
            
            if existing:
                logger.debug(f"⚠️ Article already exists: {slug}")
                continue
            
            # Extract content
            content = raw_article.get("content", "") or raw_article.get("description", "")
            if not content or len(content) < 50:
                logger.warning(f"Skipping article with insufficient content: {title}")
                continue
            
            category = raw_article.get("category", "general").lower()
            
            # Generate AI content with insights
            logger.info(f"🤖 Generating AI content for: {title[:60]}...")
            ai_content = await generate_article(
                title=title,
                content=content,
                category=category,
                keywords=raw_article.get("keywords", [])
            )
            
            # Prepare article document
            article_doc = {
                # Core content
                "title": ai_content.get("title", title),
                "slug": slugify(ai_content.get("title", title), separator="-", lowercase=True),
                "category": category,
                "summary": ai_content.get("summary", ""),
                
                # Multi-language content
                "content": {
                    "en": ai_content.get("content", content),
                    "te": "",
                    "ta": "",
                    "kn": "",
                    "ml": ""
                },
                
                # SEO metadata
                "seo_title": ai_content.get("seo_title", title),
                "seo_description": ai_content.get("seo_description", ""),
                "seo_keywords": ai_content.get("tags", []),
                "tags": ai_content.get("tags", []),
                
                # Media & source
                "source_url": raw_article.get("url") or raw_article.get("source_url"),
                "image_url": raw_article.get("urlToImage") or raw_article.get("image_url"),
                "author": raw_article.get("author", "TrendNexAI"),
                
                # AI-specific
                "ai_insights": ai_content.get("ai_insights", {}),
                "ai_generated": True,
                "model_used": ai_content.get("model_used", "openai"),
                "generated_at": ai_content.get("generated_at"),
                
                # Workflow & status
                "status": "pending_review",  # NEW articles start here
                "language": "en",
                
                # Engagement tracking
                "views": 0,
                "engagement_score": 0,
                
                # Timestamps
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "publishedAt": None,
                "reviewed_by": None,
                "reviewed_at": None,
            }
            
            # Save to database
            result = await db.articles.insert_one(article_doc)
            article_doc["_id"] = str(result.inserted_id)
            
            saved.append(article_doc)
            logger.info(f"✅ Article saved (PENDING_REVIEW): {article_doc['slug']}")
        
        except Exception as e:
            logger.error(f"❌ Error processing article '{raw_article.get('title', '')}': {e}", exc_info=True)
            continue
    
    logger.info(f"📊 Saved {len(saved)} articles (status: PENDING_REVIEW)")
    return saved


# Backward compatibility
async def save_articles(articles):
    """Legacy function name for backward compatibility"""
    return await save_articles_async(articles)


async def update_article(article_id: str, update_data: dict) -> dict:
    """
    Update an article with new data.
    Automatically updates the updatedAt timestamp.
    """
    update_data["updatedAt"] = datetime.utcnow()
    
    result = await db.articles.find_one_and_update(
        {"_id": ObjectId(article_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"✅ Article updated: {article_id}")
    
    return result


async def delete_article(article_id: str) -> bool:
    """Delete an article from database."""
    result = await db.articles.delete_one({"_id": ObjectId(article_id)})
    
    if result.deleted_count > 0:
        logger.info(f"✅ Article deleted: {article_id}")
        return True
    
    return False


async def approve_article(article_id: str, reviewer_username: str) -> dict:
    """
    Approve a PENDING_REVIEW article for publishing.
    Changes status to APPROVED.
    """
    return await update_article(
        article_id,
        {
            "status": "approved",
            "reviewed_by": reviewer_username,
            "reviewed_at": datetime.utcnow()
        }
    )


async def reject_article(article_id: str, reviewer_username: str, reason: str) -> dict:
    """
    Reject a PENDING_REVIEW article.
    Changes status to REJECTED with reason.
    """
    return await update_article(
        article_id,
        {
            "status": "rejected",
            "reviewed_by": reviewer_username,
            "reviewed_at": datetime.utcnow(),
            "rejection_reason": reason
        }
    )


async def publish_article(article_id: str) -> dict:
    """
    Publish an APPROVED or DRAFT article.
    Changes status to PUBLISHED and sets publishedAt.
    """
    return await update_article(
        article_id,
        {
            "status": "published",
            "publishedAt": datetime.utcnow()
        }
    )


async def archive_article(article_id: str) -> dict:
    """Archive a published article."""
    return await update_article(
        article_id,
        {"status": "archived"}
    )


async def search_articles(query: str, status: str = None, limit: int = 20) -> list:
    """
    Search articles by title, summary, or tags.
    Optionally filter by status.
    """
    search_query = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"summary": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}},
            {"seo_keywords": {"$regex": query, "$options": "i"}}
        ]
    }
    
    if status:
        search_query["status"] = status
    
    cursor = db.articles.find(search_query).limit(limit)
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    logger.info(f"🔍 Found {len(articles)} articles matching query: '{query}'")
    return articles


async def get_trending_articles(limit: int = 10) -> list:
    """Get trending articles by views (published only)."""
    cursor = db.articles.find(
        {"status": "published"}
    ).sort("views", -1).limit(limit)
    
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    return articles


async def get_articles_by_category(category: str, status: str = "published", limit: int = 20) -> list:
    """Get articles in a specific category."""
    cursor = db.articles.find(
        {"category": category, "status": status}
    ).sort("createdAt", -1).limit(limit)
    
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    return articles


async def get_articles_awaiting_review(limit: int = 50) -> list:
    """Get all articles awaiting admin review (PENDING_REVIEW status)."""
    cursor = db.articles.find(
        {"status": "pending_review"}
    ).sort("createdAt", -1).limit(limit)
    
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    logger.info(f"📋 Found {len(articles)} articles awaiting review")
    return articles


async def bulk_status_change(article_ids: list, new_status: str) -> dict:
    """Change status of multiple articles at once."""
    result = await db.articles.update_many(
        {"_id": {"$in": [ObjectId(id) for id in article_ids]}},
        {
            "$set": {
                "status": new_status,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"✅ Bulk status change: {result.modified_count} articles → {new_status}")
    return {
        "modified_count": result.modified_count,
        "matched_count": result.matched_count
    }


async def get_article_stats() -> dict:
    """Get comprehensive article statistics."""
    pipeline = [
        {
            "$facet": {
                "by_status": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "by_category": [
                    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "total": [
                    {"$count": "count"}
                ],
                "total_views": [
                    {"$group": {"_id": None, "views": {"$sum": "$views"}}}
                ]
            }
        }
    ]
    
    result = await db.articles.aggregate(pipeline).to_list(length=1)
    if result:
        stats = result[0]
        return {
            "total_articles": stats["total"][0]["count"] if stats["total"] else 0,
            "by_status": {item["_id"]: item["count"] for item in stats["by_status"]},
            "by_category": {item["_id"]: item["count"] for item in stats["by_category"]},
            "total_views": stats["total_views"][0]["views"] if stats["total_views"] else 0
        }
    
    return {
        "total_articles": 0,
        "by_status": {},
        "by_category": {},
        "total_views": 0
    }

    Get articles by category.
    """
    cursor = await db.articles.find(
        {"category": category, "status": "published"}
    ).sort("createdAt", -1).limit(limit)
    
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    return articles


# ============= DATABASE OPTIMIZATION HELPERS =============

def get_db_optimizer() -> DatabaseOptimizer:
    """
    Get database optimizer for high-performance queries.
    
    Usage:
        optimizer = get_db_optimizer()
        trending = await optimizer.get_trending_articles(days=7, limit=20)
        stats = await optimizer.get_statistics()
    
    Returns:
        DatabaseOptimizer instance with pre-optimized query methods
    """
    return DatabaseOptimizer(db)


async def get_optimized_articles(
    status: str = "published",
    category: str = None,
    limit: int = 20,
    skip: int = 0
) -> list:
    """
    Get articles using optimized queries that leverage database indices.
    
    This function is recommended for all public-facing queries
    as it automatically uses the most efficient index strategy.
    
    Args:
        status: Article status to filter (default: "published")
        category: Category to filter (optional)
        limit: Max articles to return (default: 20)
        skip: Pagination offset (default: 0)
    
    Returns:
        List of articles with optimization applied
    
    Example:
        articles = await get_optimized_articles(
            status="published",
            category="technology",
            limit=10,
            skip=0
        )
    """
    optimizer = get_db_optimizer()
    articles = await optimizer.get_published_articles(
        limit=limit,
        skip=skip,
        category=category,
        sort_by="publishedAt"
    )
    
    # Convert ObjectId to string for JSON serialization
    for article in articles:
        if "_id" in article:
            article["_id"] = str(article["_id"])
    
    return articles

