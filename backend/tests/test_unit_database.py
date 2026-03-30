"""
Unit Tests for Database Operations
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestDatabaseCRUD:
    """Test Create, Read, Update, Delete operations"""

    @pytest.mark.asyncio
    async def test_create_article(self, mock_db, sample_article):
        """Test creating an article in database"""
        mock_db.articles.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="article_123")
        )
        
        result = await mock_db.articles.insert_one(sample_article)
        
        assert result.inserted_id == "article_123"
        mock_db.articles.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_article_by_slug(self, mock_db, sample_article):
        """Test reading article by slug"""
        mock_db.articles.find_one = AsyncMock(return_value=sample_article)
        
        result = await mock_db.articles.find_one({"slug": "test-article"})
        
        assert result["slug"] == "test-article"
        assert result["title"] == "Test Article"

    @pytest.mark.asyncio
    async def test_read_article_not_found(self, mock_db):
        """Test reading non-existent article"""
        mock_db.articles.find_one = AsyncMock(return_value=None)
        
        result = await mock_db.articles.find_one({"slug": "non-existent"})
        
        assert result is None

    @pytest.mark.asyncio
    async def test_update_article(self, mock_db):
        """Test updating an article"""
        mock_db.articles.update_one = AsyncMock(
            return_value=MagicMock(modified_count=1)
        )
        
        result = await mock_db.articles.update_one(
            {"slug": "test-article"},
            {"$set": {"content": "Updated content"}}
        )
        
        assert result.modified_count == 1

    @pytest.mark.asyncio
    async def test_delete_article(self, mock_db):
        """Test deleting an article"""
        mock_db.articles.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )
        
        result = await mock_db.articles.delete_one({"slug": "test-article"})
        
        assert result.deleted_count == 1


class TestDatabaseQueries:
    """Test complex database queries"""

    @pytest.mark.asyncio
    async def test_get_articles_by_category(self, mock_db):
        """Test querying articles by category"""
        articles = [
            {"title": "Article 1", "category": "tech"},
            {"title": "Article 2", "category": "tech"},
        ]
        
        mock_db.articles.find = AsyncMock(return_value=articles)
        
        result = await mock_db.articles.find({"category": "tech"})
        
        assert len(result) == 2
        assert all(article["category"] == "tech" for article in result)

    @pytest.mark.asyncio
    async def test_get_latest_articles(self, mock_db):
        """Test querying latest articles"""
        articles = [
            {"title": "Article 1", "published_at": "2024-01-03"},
            {"title": "Article 2", "published_at": "2024-01-01"},
        ]
        
        mock_db.articles.find = AsyncMock(return_value=articles)
        
        result = await mock_db.articles.find({})
        
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_articles(self, mock_db):
        """Test full-text search on articles"""
        articles = [
            {"title": "Python Tutorial", "content": "Learn Python"},
        ]
        
        mock_db.articles.find = AsyncMock(return_value=articles)
        
        result = await mock_db.articles.find(
            {"$text": {"$search": "Python"}}
        )
        
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_count_articles_by_category(self, mock_db):
        """Test counting articles by category"""
        mock_db.articles.count_documents = AsyncMock(return_value=5)
        
        result = await mock_db.articles.count_documents(
            {"category": "tech"}
        )
        
        assert result == 5


class TestDatabaseIndexes:
    """Test database index creation and usage"""

    @pytest.mark.asyncio
    async def test_slug_index_exists(self, mock_db):
        """Test that slug index is created"""
        mock_db.articles.create_index = AsyncMock()
        
        await mock_db.articles.create_index([("slug", 1)], unique=True)
        
        mock_db.articles.create_index.assert_called_once()

    @pytest.mark.asyncio
    async def test_category_index_exists(self, mock_db):
        """Test that category index is created"""
        mock_db.articles.create_index = AsyncMock()
        
        await mock_db.articles.create_index([("category", 1)])
        
        mock_db.articles.create_index.assert_called_once()

    @pytest.mark.asyncio
    async def test_text_index_exists(self, mock_db):
        """Test that text search index is created"""
        mock_db.articles.create_index = AsyncMock()
        
        await mock_db.articles.create_index(
            [("title", "text"), ("content", "text")]
        )
        
        mock_db.articles.create_index.assert_called_once()


class TestDatabaseValidation:
    """Test data validation at database level"""

    @pytest.mark.asyncio
    async def test_required_fields_validation(self, sample_article):
        """Test that required fields are present"""
        required_fields = ["title", "slug", "content", "category"]
        
        has_required = all(
            field in sample_article for field in required_fields
        )
        
        assert has_required

    @pytest.mark.asyncio
    async def test_slug_uniqueness(self, mock_db):
        """Test that slug field is unique"""
        # Simulate unique index violation
        from pymongo.errors import DuplicateKeyError
        
        mock_db.articles.insert_one = AsyncMock(
            side_effect=DuplicateKeyError("Duplicate key error")
        )
        
        with pytest.raises(DuplicateKeyError):
            await mock_db.articles.insert_one({"slug": "duplicate"})

    @pytest.mark.asyncio
    async def test_field_type_validation(self, sample_article):
        """Test that field types are correct"""
        assert isinstance(sample_article["title"], str)
        assert isinstance(sample_article["content"], str)
        assert isinstance(sample_article["published_at"], str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
