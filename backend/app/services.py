from datetime import datetime
from slugify import slugify
from app.db import db
from app.openai_service import paraphrase_article
from app.schemas import ArticleIn

async def save_articles(articles):
    saved = []
    for raw in articles:
        title = raw.get("title")
        if not title:
            continue

        slug = slugify(raw.get("title", ""), separator="-").lower()
        found = await db.articles.find_one({"slug": slug})
        if found:
            continue

        clean = {
            "title": raw.get("title", "Untitled"),
            "slug": slug,
            "category": raw.get("category", "General"),
            "company": raw.get("source", {}).get("name") or raw.get("company") or "TrendNexAI",
            "source_url": raw.get("url") or raw.get("source_url"),
            "image_url": raw.get("image") or raw.get("image_url"),
            "summary": raw.get("description", ""),
            "content": {"en": raw.get("content", ""), "te": "", "ta": "", "kn": "", "ml": ""},
            "tags": raw.get("tags") or [],
            "seo_title": raw.get("title", ""),
            "seo_description": raw.get("description", ""),
            "createdAt": datetime.utcnow(),
        }

        processed = await paraphrase_article({
            "title": clean["title"],
            "description": clean["summary"],
            "content": clean["content"]["en"],
            "category": clean["category"],
            "source": {"name": clean["company"]},
        })

        item_data = {
            **clean,
            **{
                "title": processed.get("title", clean["title"]),
                "slug": processed.get("slug", clean["slug"]),
                "category": processed.get("category", clean["category"]),
                "company": processed.get("company", clean["company"]),
                "summary": processed.get("summary", clean["summary"]),
                "content": processed.get("content", clean["content"]),
                "tags": processed.get("tags", clean["tags"]),
                "seo_title": processed.get("seo_title", clean["seo_title"]),
                "seo_description": processed.get("seo_description", clean["seo_description"]),
            }
        }

        item = ArticleIn(**item_data).dict()
        item["createdAt"] = datetime.utcnow()
        result = await db.articles.insert_one(item)
        item["_id"] = str(result.inserted_id)
        saved.append(item)

    return saved
