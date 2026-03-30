"""
TrendNexAI Backend - FastAPI Application
Production-ready backend with JWT authentication, rate limiting, and async processing.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime, timedelta

# Internal imports
from app.news_api import fetch_combined_news
from app.services import save_articles
from app.db import db
from app.security import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    UserRole,
    User
)
from app.middleware import (
    RateLimitMiddleware,
    LoggingMiddleware,
    CORSMiddleware,
    setup_logging,
    ErrorHandler,
    TrendNexAIException
)
from app.dependencies import get_current_user, require_admin, require_editor
from app.admin_routes import router as admin_router
from redis.asyncio import Redis

# ============== Configuration ==============
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_REQUESTS", 100))

# Article categories
CATEGORIES = [
    "general", "technology", "business", "sports", 
    "health", "science", "entertainment", "world", "sport"
]

redis_client = None
scheduler = None

# ============== Lifespan Management ==============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Startup: Initialize Redis and scheduler
    Shutdown: Cleanup resources
    """
    global redis_client, scheduler
    
    # Startup
    logger.info("Starting TrendNexAI backend...")
    try:
        redis_client = await Redis.from_url(REDIS_URL)
        await redis_client.ping()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    # Setup scheduler for automated news fetching
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        fetch_and_process_news,
        "interval",
        minutes=30,
        id="fetch_news_job"
    )
    scheduler.start()
    logger.info("✓ Scheduled jobs started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TrendNexAI backend...")
    if scheduler:
        scheduler.shutdown()
    if redis_client:
        await redis_client.close()

# ============== FastAPI App ==============
app = FastAPI(
    title="TrendNexAI Backend API",
    description="AI-powered news platform backend with content generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=RATE_LIMIT)
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS)

# Register admin routes
app.include_router(admin_router)
logger.info("✓ Admin routes registered")

# ============== Pydantic Models ==============
class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class ArticleQuery(BaseModel):
    """Article query filters"""
    category: str = None
    search: str = None
    sort: str = "newest"
    skip: int = 0
    limit: int = 20

# ============== Health & Status ==============
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if redis_client:
            await redis_client.ping()
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status")
async def status_check():
    """Application status endpoint"""
    return {
        "status": "running",
        "environment": os.getenv("ENV", "development"),
        "scheduler_running": scheduler and scheduler.running,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============== Authentication Routes ==============
@app.post("/api/admin/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint for admin users.
    Returns JWT tokens for authentication.
    """
    user = authenticate_user(request.username, request.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(
        username=user.username,
        role=user.role,
        expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(username=user.username)
    
    logger.info(f"User logged in: {user.username} ({user.role.value})")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 30 * 60
    }

@app.get("/api/admin/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "username": current_user.username,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }

# ============== Article Routes - Public ==============
@app.get("/api/articles")
async def list_articles(
    category: str = None,
    search: str = None,
    sort: str = "newest",
    skip: int = 0,
    limit: int = 20
):
    """
    Get list of published articles with filters.
    Cached for 60 seconds.
    """
    # Cache key
    cache_key = f"articles:{category or 'all'}:{search or 'none'}:{sort}:{skip}:{limit}"
    
    # Check cache
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {cache_key}")
                import json
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    # Build query
    query = {"status": "published"}
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"summary": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.articles.count_documents(query)
    
    # Fetch articles
    direction = -1 if sort == "newest" else 1
    cursor = db.articles.find(query).sort("createdAt", direction).skip(skip).limit(limit)
    
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    
    response = {
        "success": True,
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "hasMore": skip + limit < total
    }
    
    # Cache result
    if redis_client:
        try:
            import json
            await redis_client.set(cache_key, json.dumps(response), ex=60)
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
    
    return response

@app.get("/api/articles/{slug}")
async def get_article_by_slug(slug: str):
    """
    Get article by slug.
    Cached for 5 minutes.
    """
    cache_key = f"article:{slug}"
    
    # Check cache
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                import json
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
    
    # Fetch article
    article = await db.articles.find_one({"slug": slug, "status": "published"})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article["_id"] = str(article["_id"])
    article["success"] = True
    
    # Increment views
    try:
        await db.articles.update_one(
            {"_id": article["_id"]},
            {"$inc": {"views": 1}}
        )
    except Exception as e:
        logger.warning(f"Failed to increment views: {e}")
    
    # Cache result
    if redis_client:
        try:
            import json
            await redis_client.set(cache_key, json.dumps(article), ex=300)
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
    
    return article

@app.get("/api/categories")
async def get_categories():
    """Get all article categories"""
    cache_key = "categories"
    
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                import json
                return json.loads(cached)
        except Exception:
            pass
    
    categories = await db.articles.distinct("category", {"status": "published"})
    response = {"success": True, "categories": sorted(categories or [])}
    
    if redis_client:
        try:
            import json
            await redis_client.set(cache_key, json.dumps(response), ex=3600)
        except Exception:
            pass
    
    return response

@app.get("/api/articles/related")
async def get_related_articles(tags: str = "", exclude_slug: str = None, limit: int = 3):
    """
    Get articles related by tags.
    Filters by matching tags and excludes current article.
    """
    if not tags:
        raise HTTPException(status_code=400, detail="tags parameter is required")
    
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    if not tag_list:
        raise HTTPException(status_code=400, detail="At least one tag is required")
    
    # Build query: articles with matching tags, published, excluding current
    query = {
        "status": "published",
        "tags": {"$in": tag_list}
    }
    
    if exclude_slug:
        query["slug"] = {"$ne": exclude_slug}
    
    # Fetch related articles
    cursor = db.articles.find(query).sort("createdAt", -1).limit(limit)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    
    return {
        "success": True,
        "items": items,
        "count": len(items)
    }

@app.post("/api/analytics/view")
async def track_article_view(slug: str = None):
    """
    Track article view for analytics.
    Increments view counter and logs engagement.
    """
    if not slug:
        raise HTTPException(status_code=400, detail="slug parameter is required")
    
    try:
        # Update article view count
        result = await db.articles.update_one(
            {"slug": slug, "status": "published"},
            {
                "$inc": {"views": 1, "engagement_score": 5},
                "$set": {"lastViewedAt": datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Also track in analytics collection
        await db.analytics.insert_one({
            "article_slug": slug,
            "event": "view",
            "timestamp": datetime.utcnow(),
            "user_agent": "browser"
        })
        
        logger.debug(f"View tracked for article: {slug}")
        
        return {
            "success": True,
            "message": "View tracked successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track view: {e}")
        # Don't fail the request, just log the error
        return {
            "success": False,
            "message": "Failed to track view",
            "error": str(e)
        }

# ============== Admin Routes - Protected ==============
@app.get("/api/admin/articles")
async def admin_list_articles(
    status_filter: str = None,
    category: str = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_editor)
):
    """
    Get articles for admin (includes draft/archived).
    Only editors and admins can access.
    """
    query = {}
    if status_filter:
        query["status"] = status_filter
    if category:
        query["category"] = category
    
    total = await db.articles.count_documents(query)
    cursor = db.articles.find(query).sort("createdAt", -1).skip(skip).limit(limit)
    
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)
    
    return {
        "success": True,
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/admin/articles/{article_id}/status")
async def update_article_status(
    article_id: str,
    status_value: str,
    current_user: User = Depends(require_admin)
):
    """
    Update article status (draft/published/archived).
    Only admins can access.
    """
    from bson import ObjectId
    
    valid_statuses = ["draft", "published", "archived"]
    if status_value not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    result = await db.articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {"status": status_value, "updatedAt": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Invalidate cache
    if redis_client:
        try:
            await redis_client.delete(f"article:*")
        except Exception:
            pass
    
    logger.info(f"Article {article_id} status changed to {status_value} by {current_user.username}")
    
    return {"success": True, "message": f"Article status updated to {status_value}"}

@app.post("/api/admin/fetch-news")
async def trigger_fetch_news(
    limit_per_category: int = 10,
    current_user: User = Depends(require_admin)
):
    """
    Manually trigger news fetching and processing.
    Only admins can access.
    """
    from app.tasks import fetch_and_process_task
    
    try:
        task = fetch_and_process_task.delay(limit_per_category)
        logger.info(f"News fetch triggered by {current_user.username} (Task ID: {task.id})")
        return {
            "success": True,
            "task_id": task.id,
            "message": "News fetching started"
        }
    except Exception as e:
        logger.error(f"Failed to trigger news fetch: {e}")
        raise HTTPException(status_code=500, detail="Failed to start news fetch task")

# ============== Scheduled Tasks ==============
async def fetch_and_process_news(limit_per_category: int = 10):
    """
    Scheduled task: Fetch news and process with AI.
    Runs every 30 minutes.
    """
    try:
        logger.info("Started scheduled news fetching...")
        articles = await fetch_combined_news(CATEGORIES, limit_per_category)
        saved = await save_articles(articles)
        logger.info(f"Fetched and saved {len(saved)} articles")
    except Exception as e:
        logger.error(f"Error in news fetching task: {e}")

# ============== Error Handling ==============
@app.exception_handler(TrendNexAIException)
async def custom_exception_handler(request, exc: TrendNexAIException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}")
    return ErrorHandler.handle_error(exc.status_code, exc.message, exc.detail)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return ErrorHandler.handle_error(exc.status_code, exc.detail)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return ErrorHandler.handle_error(500, "Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development"
    )

