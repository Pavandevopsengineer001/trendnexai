"""
AI Content Generation Engine for TrendNexAI.
Uses OpenAI to rewrite and enhance news articles for SEO and readability.
"""

import logging
import json
import re
from typing import Optional, Dict, List
import os
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AIContentGenerator:
    """
    Generates SEO-optimized content using OpenAI.
    Handles article rewriting, title generation, and keyword insertion.
    """
    
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 2000))
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load AI configuration from environment or defaults"""
        return {
            "tone": os.getenv("AI_TONE", "professional"),
            "style": os.getenv("AI_STYLE", "informative"),
            "include_facts": True,
            "avoid_plagiarism": True,
            "target_words": int(os.getenv("AI_TARGET_WORDS", 700)),
            "include_internal_links": True
        }
    
    async def generate_article(
        self,
        original_title: str,
        original_content: str,
        category: str = "general",
        keywords: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict[str, str]:
        """
        Generate a complete SEO-optimized article from raw news content.
        
        Returns:
            Dict with title, summary, content, seo_title, seo_description, tags
        """
        try:
            keywords = keywords or self._extract_keywords(original_title, original_content)
            
            # Step 1: Generate SEO headline
            seo_title = await self._generate_seo_title(original_title, keywords)
            
            # Step 2: Generate compelling summary
            summary = await self._generate_summary(original_content, keywords)
            
            # Step 3: Generate full article
            full_content = await self._generate_full_article(
                original_title,
                original_content,
                category,
                keywords,
                seo_title
            )
            
            # Step 4: Generate SEO meta description
            seo_description = await self._generate_seo_description(full_content, keywords)
            
            # Step 5: Extract and enhance tags
            tags = await self._generate_tags(full_content, keywords, category)
            
            return {
                "title": seo_title,
                "summary": summary,
                "content": full_content,
                "seo_title": seo_title,
                "seo_description": seo_description,
                "tags": tags,
                "ai_generated": True
            }
        
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
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

Source: {article.get('source', {}).get('name', 'TrendNexAI')}

Respond EXACTLY with a valid JSON object only like:
{{
  "title": "...",
  "slug": "...",
  "category": "...",
  "company": "...",
  "summary": "...",
  "content": {{"en":"...","te":"...","ta":"...","kn":"...","ml":"..."}},
  "tags": ["..."],
  "seo_title": "...",
  "seo_description": "..."
}}
"""

    response = await _openai_with_retry(prompt)
    text = getattr(response, 'output_text', None) or ''
    if not text:
        raise RuntimeError("OpenAI response is empty")

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        payload = match.group(0) if match else text
        parsed = __import__("json").loads(payload)
        if _contains_blocked(parsed.get('summary', '')):
            raise ValueError("Rewritten content failed moderation")
        return parsed
    except Exception as e:
        raise RuntimeError(f"Failed to parse OpenAI output: {e} | raw={text}")
