"""
Celery tasks for TrendNexAI.
Import from celery_app.py for actual task definitions.
This module is kept for backward compatibility.
"""

from app.celery_app import (
    fetch_and_process_news_task,
    process_single_article_task,
    clear_cache_task,
    generate_sitemap_task,
    archive_old_articles_task
)

# Alias for backward compatibility
fetch_and_process_task = fetch_and_process_news_task
process_article_task = process_single_article_task

__all__ = [
    'fetch_and_process_task',
    'process_article_task',
    'clear_cache_task',
    'generate_sitemap_task',
    'archive_old_articles_task'
]

