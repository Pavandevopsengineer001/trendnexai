import os
import re
import time
from typing import Dict
from openai import OpenAI, OpenAIError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BLOCKED_KEYWORDS = ["terror", "violence", "hate", "adult", "gambling", "drugs"]

def _contains_blocked(s: str) -> bool:
    if not s:
        return False
    lower = s.lower()
    return any(keyword in lower for keyword in BLOCKED_KEYWORDS)

def _validate_content(article: Dict):
    text = " ".join([str(article.get(k, "")) for k in ["title", "description", "content"]])
    if _contains_blocked(text):
        raise ValueError("Article contains blocked content")

async def _openai_with_retry(prompt: str, max_retries: int = 3):
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                max_tokens=1200,
                temperature=0.7,
            )
            return response
        except OpenAIError as e:
            if hasattr(e, 'status_code') and e.status_code in (429, 500, 502, 503, 504):
                if attempt == max_retries:
                    raise
                time.sleep(delay)
                delay *= 2
                continue
            raise

async def paraphrase_article(article: dict):
    _validate_content(article)

    prompt = f"""
You are an AI writer. Rewrite the article in English with same meaning but fresh phrasing. Then translate into Telugu, Tamil, Kannada, Malayalam.
Title: {article.get('title')}
Description: {article.get('description')}
Content: {article.get('content')}
Category: {article.get('category', 'General')}
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
