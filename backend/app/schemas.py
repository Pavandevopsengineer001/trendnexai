from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ArticleContent(BaseModel):
    en: str
    te: Optional[str] = ""
    ta: Optional[str] = ""
    kn: Optional[str] = ""
    ml: Optional[str] = ""

class ArticleBase(BaseModel):
    title: str
    slug: str
    category: str
    company: Optional[str] = "TrendNexAI"
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    summary: str
    content: ArticleContent
    tags: List[str]
    seo_title: str
    seo_description: str

class ArticleIn(ArticleBase):
    pass

class ArticleOut(ArticleBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
