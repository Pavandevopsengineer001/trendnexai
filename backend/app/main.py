from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.news_api import fetch_combined_news
from app.services import save_articles
from app.db import db
from datetime import datetime
from redis.asyncio import Redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL)

app = FastAPI(
    title="TrendNexAI Python Backend",
    description="Fetch news, process with AI, store in MongoDB",
)

categories = ["general", "technology", "business", "sports", "health", "science", "entertainment"]

@app.on_event("startup")
async def startup_event():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_process, "cron", minute=0)
    scheduler.start()

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.get("/api/fetch-news")
async def fetch_news(limit_per_cat: int = 5, async_task: bool = False):
    if async_task:
        from app.tasks import fetch_and_process_task
        task = fetch_and_process_task.delay(limit_per_cat)
        return JSONResponse({"success": True, "task_id": task.id})

    saved = await fetch_and_process(limit_per_cat)
    return JSONResponse({"success": True, "published": len(saved), "articles": saved})

async def fetch_and_process(limit_per_cat: int = 5):
    articles = await fetch_combined_news(categories, limit_per_cat)
    saved = await save_articles(articles)
    return saved

@app.get("/api/articles")
async def list_articles(category: str = None, company: str = None, search: str = None, sort: str = "newest", skip: int = 0, limit: int = 20):
    key = f"articles:{category or 'all'}:{company or 'all'}:{search or 'none'}:{sort}:{skip}:{limit}"
    cached = await redis_client.get(key)
    if cached:
        return JSONResponse(content=__import__("json").loads(cached))

    query = {}
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
    if company:
        query["company"] = {"$regex": f"^{company}$", "$options": "i"}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"summary": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
        ]

    direction = -1 if sort == "newest" else 1
    cursor = db.articles.find(query).sort("createdAt", direction).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)

    body = {"items": items, "count": len(items)}
    await redis_client.set(key, __import__("json").dumps(body), ex=60)
    return body

@app.get("/api/article/{slug}")
async def get_article(slug: str):
    key = f"article:{slug}"
    cached = await redis_client.get(key)
    if cached:
        return JSONResponse(content=__import__("json").loads(cached))

    article = await db.articles.find_one({"slug": slug})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    article["_id"] = str(article["_id"])

    await redis_client.set(key, __import__("json").dumps(article), ex=300)
    return article

@app.get("/api/categories")
async def categories_list():
    categories = await db.articles.distinct("category")
    return {"categories": categories}

@app.get("/api/companies")
async def companies_list():
    companies = await db.articles.distinct("company")
    return {"companies": companies}
