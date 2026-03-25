from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ArticleStatus(str, Enum):
    """Article publication status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Language(str, Enum):
    """Supported languages"""
    EN = "en"
    TE = "te"
    TA = "ta"
    KN = "kn"
    ML = "ml"

class ArticleContent(BaseModel):
    """Multi-language article content"""
    en: str = Field(..., min_length=100, description="English content")
    te: Optional[str] = ""
    ta: Optional[str] = ""
    kn: Optional[str] = ""
    ml: Optional[str] = ""

class ArticleBase(BaseModel):
    """Base article schema"""
    title: str = Field(..., min_length=5, max_length=200, description="Article title")
    slug: str = Field(..., description="URL-friendly slug")
    category: str = Field(..., min_length=3, description="Article category")
    tags: List[str] = Field(default=[], description="Article tags for SEO")
    summary: str = Field(..., min_length=20, max_length=500, description="Article summary")
    content: ArticleContent
    
    # SEO fields
    seo_title: str = Field(..., min_length=20, max_length=60, description="SEO title (meta)")
    seo_description: str = Field(..., min_length=50, max_length=160, description="SEO description (meta)")
    seo_keywords: List[str] = Field(default=[], description="SEO keywords")
    
    # Media
    image_url: Optional[str] = None
    author: Optional[str] = Field(default="TrendNexAI", description="Article author")
    
    # Metadata
    source_url: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT
    language: Language = Language.EN
    
    @validator('slug')
    def validate_slug(cls, v):
        """Ensure slug is hyphenated lowercase"""
        if not v.islower() or ' ' in v:
            raise ValueError('Slug must be lowercase with hyphens, no spaces')
        return v

class ArticleCreate(ArticleBase):
    """Create article request"""
    pass

class ArticleUpdate(BaseModel):
    """Update article request (partial fields)"""
    title: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[ArticleContent] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[ArticleStatus] = None
    image_url: Optional[str] = None

class ArticleOut(ArticleBase):
    """Article response schema"""
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    publishedAt: Optional[datetime] = None
    views: int = 0
    ai_generated: bool = False

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ArticleListItem(BaseModel):
    """Article list item (minimal fields)"""
    id: str = Field(..., alias="_id")
    title: str
    slug: str
    category: str
    summary: str
    seo_title: str
    image_url: Optional[str] = None
    createdAt: datetime
    views: int = 0
    status: ArticleStatus

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FetchNewsRequest(BaseModel):
    """Request to fetch news"""
    limit_per_category: int = Field(default=10, ge=1, le=50)
    categories: Optional[List[str]] = None

class BatchDeleteRequest(BaseModel):
    """Request to delete multiple articles"""
    article_ids: List[str] = Field(..., min_items=1)

