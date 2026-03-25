import httpx
from typing import List

GNEWS_API_KEY = None
NEWSAPI_KEY = None

async def fetch_gnews(category: str = "general", limit: int = 10):
    global GNEWS_API_KEY
    from os import environ
    GNEWS_API_KEY = GNEWS_API_KEY or environ.get("GNEWS_API_KEY")

    if not GNEWS_API_KEY:
        return []

    params = {
        "token": GNEWS_API_KEY,
        "topic": category,
        "lang": "en",
        "country": "in",
        "max": limit,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get("https://gnews.io/api/v4/top-headlines", params=params)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])

        for item in articles:
            item["category"] = category
            item["source_url"] = item.get("url")
            item["image_url"] = item.get("image")

        return articles

async def fetch_newsapi(category: str = "general", limit: int = 10):
    global NEWSAPI_KEY
    from os import environ
    NEWSAPI_KEY = NEWSAPI_KEY or environ.get("NEWSAPI_KEY")

    if not NEWSAPI_KEY:
        return []

    params = {
        "apiKey": NEWSAPI_KEY,
        "category": category,
        "country": "in",
        "pageSize": limit,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get("https://newsapi.org/v2/top-headlines", params=params)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])

        for item in articles:
            item["category"] = category
            item["source_url"] = item.get("url")
            item["image_url"] = item.get("urlToImage")

        return articles

async def fetch_combined_news(categories: List[str], limit_per_cat: int = 5):
    results = []
    for c in categories:
        sources = []
        try:
            sources.extend(await fetch_gnews(category=c, limit=limit_per_cat))
        except Exception:
            pass
        try:
            sources.extend(await fetch_newsapi(category=c, limit=limit_per_cat))
        except Exception:
            pass

        dedupe = {}
        for art in sources:
            key = art.get("url") or art.get("title")
            if not key or key in dedupe:
                continue
            dedupe[key] = True
            art["category"] = c
            results.append(art)
    return results
