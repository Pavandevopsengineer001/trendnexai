"""
🧠 AI Content Generation Engine for TrendNexAI
Advanced article transformation using OpenAI & Claude APIs.
Generates production-grade SEO content with structured insights.

Features:
- Dual API support (OpenAI GPT-4o-mini & Claude 3.5 Sonnet)
- Structured JSON output with insights, risks, and actions
- Cost-optimized with intelligent fallback strategy
- Deduplication via fingerprinting
- Caching layer for cost reduction
"""

import logging
import json
import re
from typing import Optional, Dict, List
import os
from openai import AsyncOpenAI
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# Initialize API clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Check if Claude is available
try:
    from anthropic import AsyncAnthropic
    claude_client = AsyncAnthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    CLAUDE_AVAILABLE = bool(os.getenv("CLAUDE_API_KEY"))
except (ImportError, Exception):
    claude_client = None
    CLAUDE_AVAILABLE = False

logger.info(f"🤖 AI Engines: OpenAI=✓ Claude={'✓' if CLAUDE_AVAILABLE else '✗'}")


class AIContentGenerator:
    """
    🚀 Production-ready AI Content Generator
    
    Features:
    - Supports OpenAI GPT-4o-mini (default) and Claude 3.5 Sonnet
    - Generates structured JSON with insights, risks, and actions
    - Cost optimization through intelligent API selection
    - Caching layer to reduce API calls
    - Comprehensive error handling with fallbacks
    
    Output Structure:
    {
        "title": "...",
        "summary": "...",
        "content": "...",
        "seo_title": "...",
        "seo_description": "...",
        "tags": [...],
        "ai_insights": {
            "why_it_matters": "...",
            "key_risks": [...],
            "action_items": [...],
            "key_takeaways": [...],
            "related_tools": [...]
        }
    }
    """
    
    def __init__(self):
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.claude_model = "claude-3-5-sonnet-20241022"
        self.max_tokens_openai = int(os.getenv("OPENAI_MAX_TOKENS", 2000))
        self.max_tokens_claude = int(os.getenv("CLAUDE_MAX_TOKENS", 2000))
        self.config = self._load_config()
        self.cache = {}  # Simple in-memory cache
        
        logger.info(f"✓ AI Generator initialized with OpenAI={self.openai_model}")
        if CLAUDE_AVAILABLE:
            logger.info(f"✓ Claude support available: {self.claude_model}")
    
    def _load_config(self) -> Dict:
        """Load AI configuration from environment or defaults"""
        return {
            "tone": os.getenv("AI_TONE", "professional"),
            "style": os.getenv("AI_STYLE", "informative"),
            "target_words": int(os.getenv("AI_TARGET_WORDS", 800)),
            "avoid_plagiarism": True,
            "include_internal_links": True,
            "use_claude_for_insights": CLAUDE_AVAILABLE,
            "cache_enabled": True
        }
    
    def _generate_cache_key(self, title: str, content: str) -> str:
        """Generate cache key from content fingerprint"""
        text = f"{title}{content}".lower().strip()
        return hashlib.md5(text.encode()).hexdigest()
    
    async def generate_article(
        self,
        original_title: str,
        original_content: str,
        category: str = "general",
        keywords: Optional[List[str]] = None,
        language: str = "en",
        use_claude: Optional[bool] = None
    ) -> Dict:
        """
        Generate a complete production-grade article with structured insights.
        
        Args:
            original_title: Raw article title
            original_content: Raw article content
            category: Article category
            keywords: Focus keywords
            language: Content language
            use_claude: Force Claude API (None = auto-select based on availability)
        
        Returns:
            Dict with complete article structure including AI insights
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key(original_title, original_content)
            if self.config.get("cache_enabled") and cache_key in self.cache:
                logger.info(f"✓ Cache hit for article: {original_title[:50]}...")
                return self.cache[cache_key]
            
            # Extract keywords
            keywords = keywords or self._extract_keywords(original_title, original_content)
            
            logger.info(f"🚀 Starting article generation for: {original_title[:60]}...")
            
            # Generate main article content (use OpenAI for main content)
            seo_title = await self._generate_seo_title(original_title, keywords)
            summary = await self._generate_summary(original_content, keywords)
            full_content = await self._generate_full_article(
                original_title, original_content, category, keywords, seo_title
            )
            seo_description = await self._generate_seo_description(full_content, keywords)
            tags = await self._generate_tags(full_content, keywords, category)
            
            # Generate AI insights (use Claude if available for better insights)
            ai_insights = await self._generate_ai_insights(
                original_title,
                original_content,
                category,
                use_claude=use_claude
            )
            
            result = {
                "title": seo_title,
                "summary": summary,
                "content": full_content,
                "seo_title": seo_title,
                "seo_description": seo_description,
                "tags": tags,
                "ai_insights": ai_insights,
                "ai_generated": True,
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": "claude" if use_claude and CLAUDE_AVAILABLE else "openai"
            }
            
            # Cache result
            if self.config.get("cache_enabled"):
                self.cache[cache_key] = result
            
            logger.info(f"✅ Article generation complete: {seo_title}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Error generating article: {e}", exc_info=True)
            raise
    
    async def _generate_ai_insights(
        self,
        title: str,
        content: str,
        category: str,
        use_claude: Optional[bool] = None
    ) -> Dict:
        """
        Generate structured insights about the article.
        Uses Claude for better analytical insights if available.
        
        Returns:
        {
            "why_it_matters": "...",
            "key_risks": ["...", "..."],
            "action_items": ["...", "..."],
            "key_takeaways": ["...", "..."],
            "related_tools": ["...", "..."],
            "impact_score": 8.5
        }
        """
        try:
            # Decide which API to use
            use_claude_for_this = use_claude if use_claude is not None else CLAUDE_AVAILABLE
            
            if use_claude_for_this and CLAUDE_AVAILABLE:
                return await self._generate_insights_claude(title, content, category)
            else:
                return await self._generate_insights_openai(title, content, category)
        
        except Exception as e:
            logger.warning(f"Failed to generate insights: {e}")
            # Return default structure
            return {
                "why_it_matters": "This development represents a significant advancement in the industry.",
                "key_risks": ["Implementation challenges", "Market adoption risks"],
                "action_items": ["Monitor developments", "Assess impact on your organization"],
                "key_takeaways": ["Innovation continues to drive the industry forward"],
                "related_tools": [],
                "impact_score": 5.0
            }
    
    async def _generate_insights_openai(
        self,
        title: str,
        content: str,
        category: str
    ) -> Dict:
        """Generate insights using OpenAI"""
        prompt = f"""
Analyze this article and provide structured insights in JSON format.

ARTICLE:
Title: {title}
Category: {category}
Content: {content[:2000]}

Return VALID JSON (no markdown, no extra text):
{{
    "why_it_matters": "<2-3 sentence explanation of business/industry impact>",
    "key_risks": [
        "<Risk 1>",
        "<Risk 2>",
        "<Risk 3>"
    ],
    "action_items": [
        "<Action 1 - What professionals should do>",
        "<Action 2>",
        "<Action 3>"
    ],
    "key_takeaways": [
        "<Takeaway 1>",
        "<Takeaway 2>",
        "<Takeaway 3>"
    ],
    "related_tools": [
        {{"name": "Tool Name", "description": "brief description"}},
        {{"name": "Another Tool", "description": "brief description"}}
    ],
    "impact_score": <number 1-10 indicating impact level>
}}
"""
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(response.choices[0].message.content)
            return insights
        except json.JSONDecodeError:
            logger.warning("Failed to parse OpenAI insights JSON")
            return {}
    
    async def _generate_insights_claude(
        self,
        title: str,
        content: str,
        category: str
    ) -> Dict:
        """Generate insights using Claude (better for analysis)"""
        if not CLAUDE_AVAILABLE:
            return await self._generate_insights_openai(title, content, category)
        
        prompt = f"""
Analyze this article and provide structured insights as valid JSON.

ARTICLE:
Title: {title}
Category: {category}
Content: {content[:2000]}

Return ONLY valid JSON, no markdown code blocks or explanations:
{{
    "why_it_matters": "<2-3 sentence explanation of business/industry impact>",
    "key_risks": ["<Risk 1>", "<Risk 2>", "<Risk 3>"],
    "action_items": ["<Action 1>", "<Action 2>", "<Action 3>"],
    "key_takeaways": ["<Takeaway 1>", "<Takeaway 2>", "<Takeaway 3>"],
    "related_tools": [{{"name": "Tool", "description": "desc"}}],
    "impact_score": 7
}}
"""
        try:
            response = await claude_client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            insights = json.loads(response.content[0].text)
            return insights
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Claude insights error: {e}, falling back to OpenAI")
            return await self._generate_insights_openai(title, content, category)
    
    async def _generate_seo_title(self, original_title: str, keywords: List[str]) -> str:
        """Generate an SEO-friendly title (50-65 chars with keyword and power word)"""
        primary_keyword = keywords[0] if keywords else "News"
        
        prompt = f"""Generate a compelling SEO title (50-65 chars) with:
1. Primary keyword: "{primary_keyword}"
2. Power word (How, Why, Best, Top, New, Complete, etc.)
3. Clickable & informative
4. No clickbait

Original: "{original_title}"
Keywords: {", ".join(keywords)}

Return ONLY the title."""
        
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Failed to generate SEO title: {e}")
            return f"{primary_keyword}: {original_title[:50]}"
    
    async def _generate_summary(self, content: str, keywords: List[str]) -> str:
        """Generate a 2-3 sentence summary (~150 chars) with primary keyword"""
        primary_keyword = keywords[0] if keywords else ""
        
        prompt = f"""Create a 2-3 sentence summary (max 150 chars):
1. Capture main point
2. Include "{primary_keyword}" naturally
3. Engaging & informative
4. End with curiosity hook

Content: {content[:800]}

Return ONLY the summary."""
        
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Failed to generate summary: {e}")
            return content[:150] + "..."
    
    async def _generate_full_article(
        self,
        title: str,
        content: str,
        category: str,
        keywords: List[str],
        seo_title: str
    ) -> str:
        """
        Generate complete 800-900 word authority-level article.
        
        Structure:
        - Strong hook/intro
        - H2: Core explanation
        - H2: Key developments & implications
        - H2: Real-world applications
        - H2: Future outlook
        - Conclusion
        """
        
        keywords_str = ", ".join(keywords)
        target_words = self.config.get("target_words", 800)
        
        prompt = f"""Rewrite as a HIGH-AUTHORITY blog post ({target_words} words ±50).

CONSTRAINTS:
- 0% plagiarism - completely rewrite
- Tone: {self.config.get('tone')}
- Style: {self.config.get('style')} with expert insights  
- Make it rank-worthy for Google

STRUCTURE:

<h1>{seo_title}</h1>

INTRO (100-150 words):
- Hook that grabs attention
- Why it matters NOW
- Main topic clarity
- Include "{keywords[0]}" naturally

<h2>Understanding [Topic]</h2> (200-250 words)
- Deep explanation
- Context & background
- Add data/stats
- Answer "What is this?"

<h2>Key Implications</h2> (180-220 words)
- Specific impacts
- Positive & negative sides
- Expert insights
- Answer "Why should I care?"

<h2>Real-World Applications</h2> (150-200 words)
- Concrete examples
- Practical uses
- Industry impact
- Expert perspectives

<h2>What's Next?</h2> (100-150 words)
- Upcoming trends
- 6-12 month predictions
- Professional advice
- Next steps

CONCLUSION (80-120 words):
- Summarize key points
- Reinforce importance
- Call-to-action
- Forward-looking

KEYWORDS:
- "{keywords[0]}": use 2-3 times
- {", ".join(keywords[1:])}: use 1-2 times each
- Include LSI keywords naturally

STYLE:
- Short paragraphs (2-3 sentences)
- Active voice
- Specific numbers/stats
- Scannable with headings
- Bold key terms
- Lists for multiple items

ORIGINAL NEWS:
Title: {title}
Content: {content}

Return ONLY article with <h1>, <h2>, <h3> tags."""
        
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens_openai,
                temperature=0.8
            )
            
            article = response.choices[0].message.content.strip()
            return article
        except Exception as e:
            logger.error(f"Failed to generate full article: {e}")
            # Return basic formatted version
            return f"<h1>{seo_title}</h1><p>{content}</p>"
    
    async def _generate_seo_description(self, content: str, keywords: List[str]) -> str:
        """Generate SEO meta description (150-160 chars with keyword + CTA)"""
        primary_keyword = keywords[0] if keywords else ""
        
        prompt = f"""Create SEO meta description (150-160 chars):
1. Include "{primary_keyword}"
2. Summarize value
3. Include CTA (Learn, Discover, etc.)
4. Click-worthy

Content: {content[:500]}

Return ONLY description."""
        
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            desc = response.choices[0].message.content.strip()
            return desc[:160]
        except Exception as e:
            logger.warning(f"Failed to generate SEO description: {e}")
            return content[:160]
    
    async def _generate_tags(self, content: str, keywords: List[str], category: str) -> List[str]:
        """Generate 5-8 relevant tags including category and keywords"""
        
        prompt = f"""Generate 5-8 tags for this article.

Requirements:
- Include category: "{category}"
- Include keywords: {", ".join(keywords)}
- Single word or 2-word phrases
- Popular search terms
- Lowercase only

Content: {content[:500]}

Return as JSON: ["tag1", "tag2"]"""
        
        try:
            response = await openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            tags_str = response.choices[0].message.content.strip()
            match = re.search(r'\[.*\]', tags_str, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.warning(f"Failed to parse tags: {e}")
        
        # Fallback
        return [category] + keywords[:4]
    
    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """Extract 5-6 keywords from title and content"""
        title_words = set(title.lower().split())
        content_words = content.lower().split()
        
        # Stop words to exclude
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "is", "was", "are", "be", "been", "with", "as", "by", "from",
            "it", "that", "this", "these", "those", "which", "who", "what", "where",
            "when", "why", "how", "all", "each", "every", "both", "her", "his"
        }
        
        keywords = []
        for word in set(content_words):
            if len(word) > 4 and word not in stop_words and word[0].isalpha():
                keywords.append(word)
                if len(keywords) >= 6:
                    break
        
        return keywords[:6] if keywords else ["news", "update"]


# Singleton instance
_generator = None

def get_ai_generator():
    """Get or create AI generator instance"""
    global _generator
    if _generator is None:
        _generator = AIContentGenerator()
    return _generator

async def generate_article(
    title: str,
    content: str,
    category: str = "general",
    keywords: Optional[List[str]] = None,
    language: str = "en",
    use_claude: Optional[bool] = None
) -> Dict:
    """
    Public function to generate a production-grade article.
    
    Args:
        title: Article title
        content: Article content
        category: Article category
        keywords: Focus keywords (auto-extracted if not provided)
        language: Content language
        use_claude: Force Claude API
    
    Returns:
        Complete article dict with insights
    """
    generator = get_ai_generator()
    return await generator.generate_article(
        title, content, category, keywords, language, use_claude
    )

# Backward compatibility  
async def paraphrase_article(article: dict):
    """Backward compatible function for article paraphrasing."""
    title = article.get("title", "")
    content = article.get("content", "") or article.get("description", "")
    category = article.get("category", "general")
    
    return await generate_article(title, content, category)
