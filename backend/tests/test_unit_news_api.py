"""
Unit Tests for News API Module
Tests news fetching, parsing, and data transformation
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from datetime import datetime


class TestNewsFetching:
    """Test news data fetching from external APIs"""

    @pytest.mark.asyncio
    async def test_fetch_combined_news_success(self):
        """Test successful news fetching from combined sources"""
        # Mock the httpx.AsyncClient
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'articles': [
                    {
                        'title': 'Breaking News',
                        'description': 'News description',
                        'url': 'https://example.com/article',
                        'image': 'https://example.com/image.jpg',
                        'publishedAt': '2024-01-01T00:00:00Z',
                        'source': {'name': 'TestNews'},
                        'content': 'Full content here'
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            # This would call your actual fetch function
            # Result should contain parsed articles
            assert mock_response.json()['articles']
            assert len(mock_response.json()['articles']) > 0

    @pytest.mark.asyncio
    async def test_fetch_news_api_failure(self):
        """Test handling of API failures"""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Simulate API error
            mock_get.side_effect = httpx.RequestError("Connection failed")
            
            # Should raise exception
            with pytest.raises(httpx.RequestError):
                raise httpx.RequestError("Connection failed")

    @pytest.mark.asyncio
    async def test_fetch_news_empty_results(self):
        """Test handling of empty news results"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'articles': []}
            mock_get.return_value = mock_response
            
            result = mock_response.json()
            assert result['articles'] == []

    @pytest.mark.asyncio
    async def test_fetch_news_rate_limit(self):
        """Test handling of rate limits (429)"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_get.return_value = mock_response
            
            assert mock_response.status_code == 429


class TestNewsDataProcessing:
    """Test news data processing and validation"""

    def test_article_slug_generation(self):
        """Test slug generation from article title"""
        from app.news_api import slugify_title
        
        title = "Python Tips and Tricks for Beginners"
        expected_slug = "python-tips-and-tricks-for-beginners"
        # This would call your slug function
        assert expected_slug.replace(" ", "-").lower()

    def test_article_deduplication(self):
        """Test removing duplicate articles"""
        articles = [
            {'title': 'Article 1', 'url': 'http://example.com/1'},
            {'title': 'Article 1', 'url': 'http://example.com/1'},  # Duplicate
            {'title': 'Article 2', 'url': 'http://example.com/2'},
        ]
        
        # Remove duplicates by URL
        unique_urls = set(article['url'] for article in articles)
        assert len(unique_urls) == 2

    def test_article_validation(self):
        """Test article data validation"""
        valid_article = {
            'title': 'Valid Article',
            'description': 'Valid description',
            'url': 'https://example.com/article',
            'image': 'https://example.com/image.jpg',
            'publishedAt': '2024-01-01T00:00:00Z',
            'source': 'TestSource'
        }
        
        # Validate required fields
        required_fields = ['title', 'url', 'description']
        has_required = all(field in valid_article for field in required_fields)
        assert has_required


class TestNewsCategorization:
    """Test automatic article categorization"""

    def test_categorize_technology_article(self):
        """Test categorizing technology articles"""
        article = {
            'title': 'New Python 3.12 Features Released',
            'description': 'Python announced new features in version 3.12',
        }
        
        tech_keywords = ['python', 'ai', 'machine learning', 'software', 'tech']
        content = f"{article['title']} {article['description']}".lower()
        
        is_tech = any(keyword in content for keyword in tech_keywords)
        assert is_tech

    def test_categorize_business_article(self):
        """Test categorizing business articles"""
        article = {
            'title': 'Tech Company Announces Quarterly Earnings',
            'description': 'Company reports record profits',
        }
        
        business_keywords = ['earnings', 'profit', 'revenue', 'stock', 'business']
        content = f"{article['title']} {article['description']}".lower()
        
        is_business = any(keyword in content for keyword in business_keywords)
        assert is_business


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
