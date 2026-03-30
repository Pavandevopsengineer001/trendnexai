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

logger.info(f"AI Engines: OpenAI=✓ Claude={'✓' if CLAUDE_AVAILABLE else '✗'}")

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
        """
        Generate an SEO-friendly title.
        - Includes primary keyword
        - 50-60 characters (optimal for Google)
        - Includes power word
        """
        primary_keyword = keywords[0] if keywords else "News"
        
        prompt = f"""
Generate a compelling, SEO-friendly article title (50-60 characters) that:
1. Includes the keyword: "{primary_keyword}"
2. Uses a power word (How, Why, Best, Top, New, etc.)
3. Is clickable and informative
4. Avoids clickbait

Original title: "{original_title}"
Keywords: {", ".join(keywords)}

Return ONLY the new title, nothing else.
"""
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_summary(self, content: str, keywords: List[str]) -> str:
        """
        Generate a compelling 2-3 sentence summary.
        Should include primary keyword naturally.
        """
        primary_keyword = keywords[0] if keywords else ""
        
        prompt = f"""
Create a concise 2-3 sentence summary (around 150 characters) that:
1. Captures the main point of the article
2. Naturally includes "{primary_keyword}"
3. Is engaging and informative
4. Ends with a call-to-action hint

Article content: {content[:1000]}

Return ONLY the summary, nothing else.
"""
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_full_article(
        self,
        title: str,
        content: str,
        category: str,
        keywords: List[str],
        seo_title: str
    ) -> str:
        """
        Generate a complete 700-900 word authority-level article with:
        - Strong introduction (hook)
        - H1, H2, H3 headings with proper structure
        - Expert insights and analysis
        - Real-world impact and implications
        - Natural keyword integration
        - Future outlook conclusion
        - 100% unique, human-like content
        """
        
        keywords_str = ", ".join(keywords)
        target_words = self.config.get("target_words", 800)
        
        prompt = f"""
Rewrite this news article into a HIGH-AUTHORITY professional blog post that will rank highly on Google.

CRITICAL REQUIREMENTS:
- WORD COUNT: {target_words} words (±50 words acceptable) - This is CRUCIAL
- Tone: {self.config.get("tone", "professional")} but engaging
- Style: {self.config.get("style", "informative")} with expert insights
- Plagiarism: ZERO - completely rewrite in your own words
- Uniqueness: Make it significantly better than the original source

ARTICLE STRUCTURE (follow exactly):

[H1]{seo_title}[/H1]

INTRODUCTION (100-150 words):
- Start with a compelling hook that grabs attention
- Clearly state the relevance to readers
- Introduce the main topic and why it matters NOW
- Include primary keyword naturally

[H2]Understanding [Main Topic][/H2] (200-250 words)
- Explain the topic in depth
- Add context and background
- Include statistics, data, or expert references
- Answer "What is this?"

[H2]Key Developments and Implications[/H2] (180-220 words)
- Highlight specific impacts
- Discuss both positive and negative implications
- Add expert insights and analysis
- Answer "Why should readers care?"

[H2]Real-World Applications and Industry Impact[/H2] (150-200 words)
- Provide concrete examples
- Show practical applications
- Discuss industry-wide implications
- Include expert perspectives

[H2]Future Outlook: What's Next?[/H2] (100-150 words)
- Discuss upcoming trends
- Predictions for the next 6-12 months
- Advice for professionals
- Call readers to action or next steps

CONCLUSION (80-120 words):
- Summarize key points
- Reinforce why this matters
- Include call-to-action
- End with forward-looking statement

KEYWORD REQUIREMENTS:
- Primary keyword: "{keywords[0] if keywords else 'topic'}" - use 2-3 times naturally
- Secondary keywords: {keywords_str[len(keywords[0]):] if len(keywords) > 1 else ''} - use 1-2 times each
- LSI keywords: Include related terms and variations naturally

WRITING STYLE:
- Use short, punchy paragraphs (2-3 sentences max)
- Use active voice whenever possible
- Include specific numbers, statistics, and data points
- Add subheadings to break up text
- Use formatting: bold for key terms, lists for multiple items
- Make it scannable and easy to read

QUALITY CHECK:
- Is it more authoritative than the original?
- Does it provide unique value?
- Would a professional recommend this article?
- Is it completely original and not plagiarized?

ORIGINAL NEWS:
Title: {title}
Content: {content}

START WRITING NOW - Return ONLY the article content with [H1], [H2] tags.
"""
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.max_tokens,
            temperature=0.8
        )
        
        article = response.choices[0].message.content.strip()
        # Replace markdown-style headings with proper HTML format
        article = article.replace("[H1]", "<h1>").replace("[/H1]", "</h1>")
        article = article.replace("[H2]", "<h2>").replace("[/H2]", "</h2>")
        article = article.replace("[H3]", "<h3>").replace("[/H3]", "</h3>")
        
        return article
    
    async def _generate_seo_description(self, content: str, keywords: List[str]) -> str:
        """
        Generate SEO meta description.
        - 150-160 characters
        - Includes primary keyword
        - Compelling call-to-action
        """
        primary_keyword = keywords[0] if keywords else ""
        
        prompt = f"""
Create an SEO meta description (150-160 characters) that:
1. Includes the keyword: "{primary_keyword}"
2. Summarizes the main value proposition
3. Includes a call-to-action (Learn, Discover, Explore, etc.)
4. Is compelling and click-worthy

Article preview: {content[:500]}

Return ONLY the meta description, nothing else.
"""
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        description = response.choices[0].message.content.strip()
        # Trim to 160 chars if needed
        return description[:160]
    
    async def _generate_tags(self, content: str, keywords: List[str], category: str) -> List[str]:
        """
        Generate relevant tags for the article.
        - 5-8 tags
        - Related to content and keywords
        - Include category
        """
        
        prompt = f"""
Generate 5-8 relevant tags for this article.

Tags should:
1. Include the category: "{category}"
2. Include these keywords where relevant: {", ".join(keywords)}
3. Be single words or 2-word phrases
4. Be popular search terms related to the content
5. Be lowercase

Article content preview: {content[:500]}

Return as JSON array: ["tag1", "tag2", "tag3"]
"""
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        try:
            tags_str = response.choices[0].message.content.strip()
            # Extract JSON array from response
            import re
            match = re.search(r'\[.*\]', tags_str, re.DOTALL)
            if match:
                tags = json.loads(match.group())
                return tags
        except Exception as e:
            logger.warning(f"Failed to parse tags: {e}")
        
        # Fallback tags
        return [category] + keywords[:4]
    
    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """
        Extract keywords from title and content.
        Returns top 5-6 keywords.
        """
        # Simple keyword extraction (in production, use NLP libraries)
        title_words = set(title.lower().split())
        content_words = content.lower().split()
        
        # Remove stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "is", "was", "are", "be", "been", "with", "as", "by", "from"
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
    language: str = "en"
) -> Dict[str, str]:
    """
    Public function to generate an article.
    """
    generator = get_ai_generator()
    return await generator.generate_article(title, content, category, keywords, language)

# Backward compatibility  
async def paraphrase_article(article: dict):
    """
    Backward compatible function for article paraphrasing.
    """
    title = article.get("title", "")
    content = article.get("content", "") or article.get("description", "")
    category = article.get("category", "general")
    
    return await generate_article(title, content, category)
