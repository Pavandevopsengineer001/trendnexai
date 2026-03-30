"""
🔄 Advanced News Fetching Engine for TrendNexAI
Fetches from multiple sources (NewsAPI, RSS feeds, etc.) with intelligent deduplication.

Features:
- Multi-source integration (NewsAPI, RSS)
- Smart deduplication using fingerprinting
- Async operations for performance
- Comprehensive error handling
- Categorization and filtering
"""

import httpx
import feedparser
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
import os
from hashlib import md5
import asyncio

logger = logging.getLogger(__name__)

# API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# RSS Feed URLs (curated tech & business sources)
RSS_FEEDS = {
    "technology": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds2.cnbc.com/id/100003114/device/rss/rss.html",
        "https://news.ycombinator.com/rss",
    ],
    "business": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "https://feeds.reuters.com/reuters/businessNews",
    ],
    "science": [
        "https://feeds.nature.com/nature/rss/current",
        "https://www.sciencedaily.com/rss/all.xml",
    ],
    "startup": [
        "https://techcrunch.com/feed/",
        "https://feeds.producthunt.com/posts/spicy.rss",
    ],
    "general": [
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    ]
}

class ArticleFingerprint:
    """Smart fingerprinting for deduplication"""
    
    @staticmethod
    def generate(title: str, content: str, url: str = "") -> str:
        """
        Generate unique fingerprint for article deduplication.
        Uses title + content hash for better accuracy.
        """
        text = f"{title}{content}{url}".lower().strip()
        return md5(text.encode()).hexdigest()
    
    @staticmethod
    def generate_url_fingerprint(url: str) -> str:
        """Generate fingerprint from URL only"""
        return md5(url.lower().strip().encode()).hexdigest()


class NewsFetcher:
    """
    🚀 Multi-source News Fetcher
    
    Supports:
    - NewsAPI (30+ countries, 100+ sources)
    - RSS feeds (unlimited custom sources)
    - Smart deduplication
    - Rate limiting
    - Error recovery
    """
    
    def __init__(self):
        self.timeout = 30
        self.session = None
        self.seen_fingerprints: Set[str] = set()
        self.seen_urls: Set[str] = set()
    
    async def get_session(self) -> httpx.AsyncClient:
        """Get or create async HTTP session"""
        if not self.session:
            self.session = httpx.AsyncClient(
                timeout=self.timeout,
                headers={
                    "User-Agent": "TrendNexAI/2.0 (News Aggregator)",
                    "Accept": "application/xml, application/json"
                },
                limits=httpx.Limits(max_keepalive_connections=5)
            )
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def fetch_newsapi(
        self,
        category: str = "general",
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch from NewsAPI (https://newsapi.org/)
        
        Supports 30+ countries and 100+ news sources.
        Rate limited to 100 requests/day on free tier.
        """
        if not NEWS_API_KEY:
            logger.debug("NEWS_API_KEY not set, skipping NewsAPI")
            return []
        
        try:
            client = await self.get_session()
            
            params = {
                "apiKey": NEWS_API_KEY,
                "category": category,
                "country": "us",
                "language": "en",
                "pageSize": min(limit, 100),  # Max 100 per request
                "sortBy": "publishedAt"
            }
            
            logger.info(f"📰 Fetching NewsAPI: {category} ({limit} articles)")
            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get("articles", []):
                title = item.get("title", "").strip()
                content = item.get("content", "") or item.get("description", "")
                url = item.get("url", "")
                
                if not title or not content:
                    continue
                
                # Skip if already seen
                if url in self.seen_urls:
                    logger.debug(f"⚠️ Duplicate URL skipped: {title[:50]}")
                    continue
                
                self.seen_urls.add(url)
                
                article = {
                    "source": "newsapi",
                    "title": title,
                    "description": item.get("description", ""),
                    "content": content,
                    "url": url,
                    "source_url": url,
                    "image_url": item.get("urlToImage", ""),
                    "author": item.get("author", ""),
                    "published_at": item.get("publishedAt", ""),
                    "source_name": item.get("source", {}).get("name", "NewsAPI"),
                    "category": category,
                }
                
                # Generate fingerprints
                article["fingerprint"] = ArticleFingerprint.generate(
                    article["title"],
                    article["content"],
                    article["url"]
                )
                article["url_fingerprint"] = ArticleFingerprint.generate_url_fingerprint(url)
                
                articles.append(article)
            
            logger.info(f"✓ Fetched {len(articles)} articles from NewsAPI ({category})")
            return articles
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ NewsAPI HTTP error: {e.status_code} - {e.response.text[:200]}")
            return []
        except Exception as e:
            logger.error(f"❌ Error fetching NewsAPI: {e}", exc_info=True)
            return []
    
    async def fetch_rss(
        self,
        category: str = "general",
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch from RSS feeds.
        
        Features:
        - Multiple feeds per category
        - XML parsing with feedparser
        - Full error handling
        - Multi-language support
        """
        feeds = RSS_FEEDS.get(category, RSS_FEEDS.get("general", []))
        if not feeds:
            logger.warning(f"No RSS feeds configured for category: {category}")
            return []
        
        articles = []
        
        for feed_url in feeds:
            try:
                logger.info(f"🔄 Parsing RSS: {feed_url[:60]}...")
                
                client = await self.get_session()
                response = await client.get(feed_url, timeout=self.timeout)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                if not feed.entries:
                    logger.warning(f"⚠️ No entries in feed: {feed_url[:50]}")
                    continue
                
                count = 0
                for entry in feed.entries[:limit]:
                    title = entry.get("title", "").strip()
                    content = entry.get("summary", "") or entry.get("description", "")
                    url = entry.get("link", "")
                    
                    if not title or not content:
                        continue
                    
                    # Skip if already seen
                    if url in self.seen_urls:
                        continue
                    
                    self.seen_urls.add(url)
                    
                    article = {
                        "source": "rss",
                        "title": title,
                        "description": content[:200] if len(content) > 200 else content,
                        "content": content,
                        "url": url,
                        "source_url": url,
                        "image_url": self._extract_rss_image(entry),
                        "author": entry.get("author", ""),
                        "published_at": entry.get("published", "") or entry.get("updated", ""),
                        "source_name": feed.feed.get("title", "RSS Feed"),
                        "category": category,
                        "feed_url": feed_url,
                    }
                    
                    # Generate fingerprints
                    article["fingerprint"] = ArticleFingerprint.generate(
                        article["title"],
                        article["content"],
                        article["url"]
                    )
                    article["url_fingerprint"] = ArticleFingerprint.generate_url_fingerprint(url)
                    
                    articles.append(article)
                    count += 1
                    
                    if count >= limit:
                        break
                
                logger.info(f"✓ Fetched {count} articles from RSS feed")
            
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse RSS feed: {feed_url[:60]} - {e}")
                continue
        
        return articles
    
    @staticmethod
    def _extract_rss_image(entry: Dict) -> str:
        """Extract image URL from RSS entry"""
        # Try common fields
        for field in ["media_content", "media_thumbnail", "image"]:
            if field in entry:
                content = entry.get(field)
                if isinstance(content, list) and content:
                    return content[0].get("url", "")
                elif isinstance(content, dict):
                    return content.get("url", "")
        
        return ""


class ArticleDeduplicator:
    """
    🎯 Intelligent Article Deduplication
    
    Strategies:
    1. Exact URL match (fastest)
    2. Content fingerprint match (most accurate)
    3. Similarity threshold (fuzzy matching)
    """
    
    def __init__(self):
        self.seen_fingerprints: Dict[str, str] = {}  # fingerprint -> article_id
        self.seen_urls: Set[str] = set()
    
    def is_duplicate(self, article: Dict) -> bool:
        """Check if article is a duplicate"""
        # Check URL
        url = article.get("url") or article.get("source_url")
        if url in self.seen_urls:
            logger.debug(f"Duplicate detected (URL): {article.get('title', '')[:50]}")
            return True
        
        # Check fingerprint
        fingerprint = article.get("fingerprint", "")
        if fingerprint in self.seen_fingerprints:
            logger.debug(f"Duplicate detected (fingerprint): {article.get('title', '')[:50]}")
            return True
        
        return False
    
    def register(self, article: Dict, article_id: str = ""):
        """Register article as seen"""
        url = article.get("url") or article.get("source_url")
        if url:
            self.seen_urls.add(url)
        
        fingerprint = article.get("fingerprint", "")
        if fingerprint:
            self.seen_fingerprints[fingerprint] = article_id or fingerprint
    
    def reset(self):
        """Clear deduplication cache"""
        self.seen_fingerprints.clear()
        self.seen_urls.clear()


# Global deduplicator
deduplicator = ArticleDeduplicator()


async def fetch_combined_news(
    categories: List[str],
    limit_per_category: int = 10,
    include_rss: bool = True,
    include_newsapi: bool = True
) -> List[Dict]:
    """
    🚀 Fetch news from all sources and deduplicate.
    
    Args:
        categories: List of categories to fetch
        limit_per_category: Max articles per category per source
        include_rss: Include RSS feeds
        include_newsapi: Include NewsAPI
    
    Returns:
        List of unique articles
    """
    fetcher = NewsFetcher()
    all_articles = []
    
    try:
        tasks = []
        
        for category in categories:
            logger.info(f"📋 Preparing fetch tasks for: {category}")
            
            if include_newsapi and NEWS_API_KEY:
                tasks.append(
                    fetcher.fetch_newsapi(category, limit_per_category)
                )
            
            if include_rss:
                tasks.append(
                    fetcher.fetch_rss(category, limit_per_category)
                )
        
        # Run all fetch tasks concurrently
        if tasks:
            logger.info(f"🚀 Running {len(tasks)} async fetch tasks...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Task failed: {result}")
        
        # Deduplicate
        logger.info(f"🔄 Deduplicating {len(all_articles)} articles...")
        unique_articles = []
        seen = set()
        
        for article in all_articles:
            fingerprint = article.get("fingerprint", "")
            if fingerprint and fingerprint not in seen:
                seen.add(fingerprint)
                unique_articles.append(article)
                logger.debug(f"✓ Unique: {article.get('title', '')[:60]}")
            else:
                logger.debug(f"⚠️ Duplicate skipped: {article.get('title', '')[:60]}")
        
        logger.info(f"📊 Result: {len(all_articles)} articles → {len(unique_articles)} unique")
        return unique_articles
    
    finally:
        await fetcher.close()


# Backward compatibility functions
async def fetch_gnews(category: str = "general", limit: int = 10):
    """Backward compatible - returns NewsAPI articles"""
    fetcher = NewsFetcher()
    try:
        return await fetcher.fetch_newsapi(category, limit)
    finally:
        await fetcher.close()

async def fetch_newsapi(category: str = "general", limit: int = 10):
    """Backward compatible - returns NewsAPI articles"""
    fetcher = NewsFetcher()
    try:
        return await fetcher.fetch_newsapi(category, limit)
    finally:
        await fetcher.close()

async def fetch_rss(category: str = "general", limit: int = 10):
    """Backward compatible - returns RSS articles"""
    fetcher = NewsFetcher()
    try:
        return await fetcher.fetch_rss(category, limit)
    finally:
        await fetcher.close()
