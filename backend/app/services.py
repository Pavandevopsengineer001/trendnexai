"""
Business logic services for TrendNexAI.
Handles article processing, storage, and AI content generation.
"""

from datetime import datetime
from python_slugify import slugify
from app.db import db
from app.openai_service import generate_article
import logging

logger = logging.getLogger(__name__)

async def save_articles_async(articles: list) -> list:
    """
    Save articles to database after AI processing.
    Skips duplicates and drafts new articles.
    
    Args:
        articles: List of raw articles from news API
    
    Returns:
        List of saved article IDs
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
            
            # Check for duplicate
            existing = await db.articles.find_one({"slug": slug})
            if existing:
                logger.debug(f"Article already exists: {slug}")
                continue
            
            # Extract content
            content = raw_article.get("content", "") or raw_article.get("description", "")
            if not content:
                logger.warning(f"Skipping article without content: {title}")
                continue
            
            category = raw_article.get("category", "general").lower()
            
            # Generate AI content
            logger.info(f"Generating AI content for: {title}")
            ai_content = await generate_article(
                title=title,
                content=content,
                category=category,
                keywords=raw_article.get("keywords", [])
            )
            
            # Prepare article document
            article_doc = {
                "title": ai_content.get("title", title),
                "slug": slugify(ai_content.get("title", title), separator="-", lowercase=True),
                "category": category,
                "tags": ai_content.get("tags", []),
                "summary": ai_content.get("summary", ""),
                "content": {
                    "en": ai_content.get("content", content),
                    "te": "",
                    "ta": "",
                    "kn": "",
                    "ml": ""
                },
                "seo_title": ai_content.get("seo_title", title),
                "seo_description": ai_content.get("seo_description", ""),
                "seo_keywords": ai_content.get("tags", []),
                "source_url": raw_article.get("url") or raw_article.get("source_url"),
                "image_url": raw_article.get("urlToImage") or raw_article.get("image_url"),
                "author": raw_article.get("author", "TrendNexAI"),
                "status": "draft",
                "language": "en",
                "ai_generated": True,
                "views": 0,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }
            
            # Save to database
            result = await db.articles.insert_one(article_doc)
            article_doc["_id"] = str(result.inserted_id)
            
            saved.append(article_doc)
            logger.info(f"Article saved: {article_doc['slug']}")
        
        except Exception as e:
            logger.error(f"Error processing article {raw_article.get('title')}: {e}", exc_info=True)
            continue
    
    logger.info(f"Successfully saved {len(saved)} articles")
    return saved

# Backward compatibility
async def save_articles(articles):
    """Legacy function name for backward compatibility"""
    return await save_articles_async(articles)

async def update_article(article_id: str, update_data: dict) -> dict:
    """
    Update an article with new data.
    """
    from bson import ObjectId
    from datetime import datetime
    
    update_data["updatedAt"] = datetime.utcnow()
    
    result = await db.articles.find_one_and_update(
        {"_id": ObjectId(article_id)},
        {"$set": update_data},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Article updated: {article_id}")
    
    return result

async def delete_article(article_id: str) -> bool:
    """
    Delete an article from database.
    """
    from bson import ObjectId
    
    result = await db.articles.delete_one({"_id": ObjectId(article_id)})
    
    if result.deleted_count > 0:
        logger.info(f"Article deleted: {article_id}")
        return True
    
    return False

async def publish_article(article_id: str) -> dict:
    """
    Publish a draft article.
    """
    return await update_article(
        article_id,
        {
            "status": "published",
            "publishedAt": datetime.utcnow()
        }
    )

async def archive_article(article_id: str) -> dict:
    """
    Archive an article.
    """
    return await update_article(
        article_id,
        {"status": "archived"}
    )

async def search_articles(query: str, limit: int = 20) -> list:
    """
    Search articles by title, summary, or tags.
    """
    search_query = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"summary": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}},
            {"seo_keywords": {"$regex": query, "$options": "i"}}
        ]
    }
    
    cursor = await db.articles.find(search_query).limit(limit)
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    return articles

async def get_trending_articles(limit: int = 10) -> list:
    """
    Get trending articles by views.
    """
    cursor = await db.articles.find(
        {"status": "published"}
    ).sort("views", -1).limit(limit)
    
    articles = []
    async for article in cursor:
        article["_id"] = str(article["_id"])
        articles.append(article)
    
    return articles

async def get_articles_by_category(category: str, limit: int = 20) -> list:
    """
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

