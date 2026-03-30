"""
News fetching module for TrendNexAI.
Handles fetching from multiple sources (News API, RSS, etc.) with deduplication.
"""

import httpx
import feedparser
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
from hashlib import md5

logger = logging.getLogger(__name__)

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

class NewsFetcher:
    """Fetches news from multiple sources"""
    
    def __init__(self):
        self.timeout = 30
        self.session = None
    
    async def get_session(self) -> httpx.AsyncClient:
        """Get or create async HTTP session"""
        if not self.session:
            self.session = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": "TrendNexAI/1.0"}
            )
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    def _generate_fingerprint(self, title: str, content: str) -> str:
        """Generate unique fingerprint for article deduplication"""
        text = f"{title}{content}".lower().strip()
        return md5(text.encode()).hexdigest()
    
    async def fetch_newsapi(
        self,
        category: str = "general",
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch from NewsAPI (https://newsapi.org/)
        Supports multiple categories and countries.
        """
        if not NEWS_API_KEY:
            logger.warning("NEWS_API_KEY not set, skipping NewsAPI")
            return []
        
        try:
            client = await self.get_session()
            
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "country": "us",
                "language": "en",
                "pageSize": limit,
                "sortBy": "publishedAt"
            }
            
            logger.info(f"Fetching NewsAPI for category: {category}")
            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get("articles", []):
                article = {
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                    "urlToImage": item.get("urlToImage", ""),
                    "author": item.get("author", ""),
                    "publishedAt": item.get("publishedAt", ""),
                    "source": item.get("source", {}).get("name", "NewsAPI"),
                    "category": category,
                    "source_url": item.get("url"),
                    "image_url": item.get("urlToImage"),
                }
                article["fingerprint"] = self._generate_fingerprint(
                    article["title"],
                    article["content"]
                )
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from NewsAPI ({category})")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching NewsAPI: {e}")
            return []

async def fetch_combined_news(categories: List[str], limit_per_cat: int = 5):
    """
    Fetch news from multiple sources and deduplicate.
    Backward compatible with existing code.
    """
    fetcher = NewsFetcher()
    all_articles = []
    
    try:
        for category in categories:
            logger.info(f"Fetching news for category: {category}")
            
            # Fetch from NewsAPI
            try:
                articles = await fetcher.fetch_newsapi(category, limit_per_cat)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching news for {category}: {e}")
        
        # Simple deduplication by URL
        seen_urls = set()
        unique_articles = []
        
        for article in all_articles:
            url = article.get("url") or article.get("source_url")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        logger.info(f"Total articles fetched: {len(all_articles)}, Unique: {len(unique_articles)}")
        return unique_articles
    
    finally:
        await fetcher.close()

# Backward compatibility functions
async def fetch_gnews(category: str = "general", limit: int = 10):
    """Backward compatible - uses NewsAPI instead"""
    fetcher = NewsFetcher()
    try:
        return await fetcher.fetch_newsapi(category, limit)
    finally:
        await fetcher.close()

async def fetch_newsapi(category: str = "general", limit: int = 10):
    """Backward compatible function"""
    fetcher = NewsFetcher()
    try:
        return await fetcher.fetch_newsapi(category, limit)
    finally:
        await fetcher.close()

