"""
Celery task queue configuration for TrendNexAI.
Handles background jobs like news fetching and article processing.
"""

from celery import Celery, Task
from celery.schedules import crontab
import os
from app.db import db
import logging

logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery(
    'trendnexai',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule for Celery Beat
app.conf.beat_schedule = {
    'fetch-news-every-30-minutes': {
        'task': 'app.celery_tasks.fetch_and_process_news_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'time_limit': 25 * 60,  # 25 minutes
        }
    },
    'clear-cache-daily': {
        'task': 'app.celery_tasks.clear_cache_task',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'generate-sitemap-weekly': {
        'task': 'app.celery_tasks.generate_sitemap_task',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Weekly (Sunday 2 AM)
    },
}

class CallbackTask(Task):
    """Task with callbacks for error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}", exc_info=einfo)
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(f"Task {task_id} retrying: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, result, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully")
        super().on_success(result, task_id, args, kwargs)

app.Task = CallbackTask

# ============== Tasks ==============

@app.task(bind=True, max_retries=3)
def fetch_and_process_news_task(self, limit_per_category: int = 10):
    """
    Background task to fetch and process news.
    Retries up to 3 times on failure.
    """
    try:
        from app.news_api import fetch_combined_news
        from app.services import save_articles_async
        import asyncio
        
        categories = [
            "general", "technology", "business", "sports",
            "health", "science", "entertainment", "world"
        ]
        
        logger.info(f"Starting news fetch task (limit={limit_per_category} per category)")
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            articles = loop.run_until_complete(
                fetch_combined_news(categories, limit_per_category)
            )
            saved = loop.run_until_complete(save_articles_async(articles))
            logger.info(f"Fetched and processed {len(saved)} articles")
            return {
                "success": True,
                "articles_processed": len(saved),
                "task_id": self.request.id
            }
        finally:
            loop.close()
        
    except Exception as exc:
        logger.error(f"Error in fetch_and_process_news_task: {exc}", exc_info=True)
        # Retry after exponential backoff (30 sec, 2 min, 5 min)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)

@app.task(bind=True, max_retries=2)
def process_single_article_task(self, article_data: dict):
    """
    Background task to process a single article.
    Generates AI content and stores in database.
    """
    try:
        from app.openai_service import generate_article as ai_generate
        from app.db import db
        from python_slugify import slugify
        import asyncio
        
        logger.info(f"Processing article: {article_data.get('title')}")
        
        # Generate AI content
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ai_content = loop.run_until_complete(ai_generate(
                title=article_data.get('title', ''),
                content=article_data.get('content', ''),
                category=article_data.get('category', 'general'),
                keywords=article_data.get('keywords', [])
            ))
        finally:
            loop.close()
        
        # Prepare article document
        article_doc = {
            'title': ai_content.get('title'),
            'slug': slugify(ai_content.get('title')),
            'category': article_data.get('category', 'general'),
            'summary': ai_content.get('summary'),
            'content': ai_content.get('content'),
            'seo_title': ai_content.get('seo_title'),
            'seo_description': ai_content.get('seo_description'),
            'seo_keywords': ai_content.get('tags', []),
            'tags': ai_content.get('tags', []),
            'source_url': article_data.get('source_url'),
            'image_url': article_data.get('image_url'),
            'status': 'draft',
            'ai_generated': True,
            'views': 0,
            'createdAt': db.connection.current_time(),
        }
        
        # Store in database
        db.articles.insert_one(article_doc)
        logger.info(f"Article processed and stored: {article_doc['slug']}")
        
        return {
            "success": True,
            "article_slug": article_doc['slug'],
            "task_id": self.request.id
        }
    
    except Exception as exc:
        logger.error(f"Error processing article: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@app.task(bind=True)
def clear_cache_task(self):
    """
    Scheduled task to clear old cached items.
    Runs daily at midnight.
    """
    try:
        from redis.asyncio import Redis
        import asyncio
        
        logger.info("Clearing cache...")
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        async def clear():
            redis = await Redis.from_url(redis_url)
            await redis.flushdb()
            await redis.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(clear())
        finally:
            loop.close()
        
        logger.info("Cache cleared successfully")
        return {"success": True, "task_id": self.request.id}
    
    except Exception as exc:
        logger.error(f"Error clearing cache: {exc}", exc_info=True)
        return {"success": False, "error": str(exc)}

@app.task(bind=True)
def generate_sitemap_task(self):
    """
    Scheduled task to generate sitemap for SEO.
    Runs weekly on Sunday at 2 AM.
    """
    try:
        from datetime import datetime
        from app.db import db
        import asyncio
        
        logger.info("Generating sitemap...")
        
        async def generate():
            # Get all published articles
            articles = await db.articles.find({"status": "published"}).to_list(None)
            
            # Generate sitemap XML
            sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
            sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            # Add homepage
            sitemap += f'  <url>\n'
            sitemap += f'    <loc>https://yourdomain.com</loc>\n'
            sitemap += f'    <lastmod>{datetime.utcnow().isoformat()}</lastmod>\n'
            sitemap += f'    <priority>1.0</priority>\n'
            sitemap += f'  </url>\n'
            
            # Add article pages
            for article in articles:
                sitemap += f'  <url>\n'
                sitemap += f'    <loc>https://yourdomain.com/article/{article["slug"]}</loc>\n'
                sitemap += f'    <lastmod>{article["updatedAt"].isoformat() if article.get("updatedAt") else article["createdAt"].isoformat()}</lastmod>\n'
                sitemap += f'    <priority>0.8</priority>\n'
                sitemap += f'  </url>\n'
            
            sitemap += '</urlset>'
            
            # Save sitemap
            # In production, save to storage or CDN
            logger.info(f"Sitemap generated with {len(articles)} articles")
            return sitemap
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(generate())
        finally:
            loop.close()
        
        return {"success": True, "articles_in_sitemap": len(result), "task_id": self.request.id}
    
    except Exception as exc:
        logger.error(f"Error generating sitemap: {exc}", exc_info=True)
        return {"success": False, "error": str(exc)}

@app.task(bind=True, max_retries=3)
def archive_old_articles_task(self, days: int = 90):
    """
    Background task to archive articles older than specified days.
    """
    try:
        from datetime import datetime, timedelta
        from app.db import db
        import asyncio
        
        logger.info(f"Archiving articles older than {days} days...")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async def archive():
            result = await db.articles.update_many(
                {
                    "createdAt": {"$lt": cutoff_date},
                    "status": {"$ne": "archived"}
                },
                {"$set": {"status": "archived"}}
            )
            return result.modified_count
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            count = loop.run_until_complete(archive())
        finally:
            loop.close()
        
        logger.info(f"Archived {count} articles")
        return {"success": True, "archived_count": count, "task_id": self.request.id}
    
    except Exception as exc:
        logger.error(f"Error archiving articles: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60 * 60)

# For backward compatibility
fetch_and_process_task = fetch_and_process_news_task
process_article_task = process_single_article_task
