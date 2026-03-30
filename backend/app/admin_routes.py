"""
🛡️ Admin API Routes for TrendNexAI
Complete CRUD operations, article approval workflow, and management.

Routes:
- GET/POST /api/admin/articles - List/create articles
- GET/PUT/DELETE /api/admin/articles/{id} - Manage specific articles
- POST /api/admin/articles/{id}/approve - Approve for publishing
- POST /api/admin/articles/{id}/reject - Reject with reason
- POST /api/admin/articles/{id}/publish - Publish approved article
- POST /api/admin/bulk-actions - Bulk status changes
- GET /api/admin/stats - Article statistics
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import  JSONResponse
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import logging

from app.db import db
from app.security import User, require_admin, require_editor
from app.schemas import (
    ArticleStatus, ArticleAdmin, ArticleUpdate, StatusChangeRequest,
    BulkStatusChangeRequest, ArticleStats, FetchNewsRequest
)
from app.services import (
    update_article, approve_article, reject_article, publish_article,
    delete_article, get_articles_awaiting_review, bulk_status_change,
    get_article_stats, search_articles, get_articles_by_category
)
from app.tasks import fetch_and_process_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============== Article Management Routes ==============

@router.get("/articles")
async def list_articles(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in title/content"),
    current_user: User = Depends(require_editor)
):
    """
    Get articles for admin (includes drafts & pending review).
    Only editors and admins can access.
    """
    try:
        query = {}
        
        # Apply filters
        if status_filter:
            query["status"] = status_filter
        if category:
            query["category"] = category
        
        # Apply search
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"summary": {"$regex": search, "$options": "i"}},
                {"tags": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await db.articles.count_documents(query)
        
        # Fetch articles
        cursor = db.articles.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        
        items = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)
        
        logger.info(f"📋 Admin: Listed {len(items)} articles for {current_user.username}")
        
        return {
            "success": True,
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "hasMore": skip + limit < total
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/pending-review")
async def list_pending_review(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_editor)
):
    """
    Get articles awaiting review (PENDING_REVIEW status).
    Shows newest first.
    """
    try:
        articles = await get_articles_awaiting_review(limit=skip + limit)
        total = await db.articles.count_documents({"status": "pending_review"})
        
        items = articles[skip:skip + limit]
        for item in items:
            item["_id"] = str(item["_id"])
        
        return {
            "success": True,
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"❌ Error listing pending articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/articles/{article_id}")
async def get_article(
    article_id: str,
    current_user: User = Depends(require_editor)
):
    """Get detailed article with AI insights for admin editing."""
    try:
        article = await db.articles.find_one({"_id": ObjectId(article_id)})
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article["_id"] = str(article["_id"])
        article["success"] = True
        
        return article
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/articles/{article_id}")
async def update_article_endpoint(
    article_id: str,
    update_data: ArticleUpdate,
    current_user: User = Depends(require_editor)
):
    """
    Update article fields.
    Only admins can change status directly.
    """
    try:
        # Convert model to dict, removing None values
        data_dict = update_data.model_dump(exclude_unset=True)
        
        # Only admins can change status
        if "status" in data_dict and current_user.role.value != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can change article status"
            )
        
        article = await update_article(article_id, data_dict)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article["_id"] = str(article["_id"])
        logger.info(f"✅ Updated article {article_id} by {current_user.username}")
        
        return {
            "success": True,
            "article": article
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/articles/{article_id}")
async def delete_article_endpoint(
    article_id: str,
    current_user: User = Depends(require_admin)
):
    """Delete an article (admin only)."""
    try:
        result = await delete_article(article_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Article not found")
        
        logger.info(f"✅ Deleted article {article_id} by {current_user.username}")
        
        return {
            "success": True,
            "message": "Article deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Approval Workflow Routes ==============

@router.post("/articles/{article_id}/approve")
async def approve_article_endpoint(
    article_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Approve a PENDING_REVIEW article for publishing.
    Changes status to APPROVED.
    Only admins can approve.
    """
    try:
        # Check if article exists and is PENDING_REVIEW
        article = await db.articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if article.get("status") != "pending_review":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot approve article with status: {article.get('status')}"
            )
        
        # Approve the article
        result = await approve_article(article_id, current_user.username)
        result["_id"] = str(result["_id"])
        
        logger.info(f"✅ Approved article {article_id} by {current_user.username}")
        
        return {
            "success": True,
            "message": "Article approved successfully",
            "article": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error approving article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/articles/{article_id}/reject")
async def reject_article_endpoint(
    article_id: str,
    request: StatusChangeRequest,
    current_user: User = Depends(require_admin)
):
    """
    Reject a PENDING_REVIEW article with reason.
    Changes status to REJECTED.
    Only admins can reject.
    """
    try:
        # Check if article exists and is PENDING_REVIEW
        article = await db.articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        if article.get("status") != "pending_review":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reject article with status: {article.get('status')}"
            )
        
        # Reject the article
        result = await reject_article(
            article_id,
            current_user.username,
            request.reason or "No reason provided"
        )
        result["_id"] = str(result["_id"])
        
        logger.info(f"✅ Rejected article {article_id}: {request.reason}")
        
        return {
            "success": True,
            "message": "Article rejected successfully",
            "article": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error rejecting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/articles/{article_id}/publish")
async def publish_article_endpoint(
    article_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Publish an APPROVED article.
    Changes status to PUBLISHED.
    Only admins can publish.
    """
    try:
        # Check if article exists
        article = await db.articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        status = article.get("status")
        if status not in ["approved", "draft"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish article with status: {status}. Must be APPROVED or DRAFT."
            )
        
        # Publish the article
        result = await publish_article(article_id)
        result["_id"] = str(result["_id"])
        
        logger.info(f"✅ Published article {article_id} by {current_user.username}")
        
        return {
            "success": True,
            "message": "Article published successfully",
            "article": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error publishing article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Bulk Operations ==============

@router.post("/bulk-status-change")
async def bulk_change_status(
    request: BulkStatusChangeRequest,
    current_user: User = Depends(require_admin)
):
    """
    Change status of multiple articles at once.
    Requires admin permissions.
    """
    try:
        if not request.article_ids:
            raise HTTPException(status_code=400, detail="No article IDs provided")
        
        result = await bulk_status_change(request.article_ids, request.status.value)
        
        logger.info(f"✅ Bulk status change: {result['modified_count']} articles by {current_user.username}")
        
        return {
            "success": True,
            "modified_count": result["modified_count"],
            "matched_count": result["matched_count"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in bulk status change: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Stats & Analytics ==============

@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_editor)
):
    """Get comprehensive article statistics."""
    try:
        stats = await get_article_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== News Fetching ==============

@router.post("/fetch-news")
async def trigger_fetch_news(
    request: FetchNewsRequest,
    current_user: User = Depends(require_admin)
):
    """
    Manually trigger news fetching and processing.
    Only admins can access.
    """
    try:
        task = fetch_and_process_task.delay(
            limit_per_category=request.limit_per_category
        )
        
        logger.info(f"🚀 News fetch triggered by {current_user.username} (Task ID: {task.id})")
        
        return {
            "success": True,
            "task_id": task.id,
            "message": "News fetch task started"
        }
    
    except Exception as e:
        logger.error(f"❌ Error triggering news fetch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-news/status/{task_id}")
async def fetch_news_status(
    task_id: str,
    current_user: User = Depends(require_editor)
):
    """Get status of a background news fetch task."""
    try:
        result = fetch_and_process_task.AsyncResult(task_id)
        
        return {
            "success": True,
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
