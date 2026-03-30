"""
Backend Unit Tests Configuration & Fixtures
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = AsyncMock()
    return db

@pytest.fixture
def mock_redis():
    """Mock Redis cache"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock(return_value={})
    return redis

@pytest.fixture
def sample_article():
    """Sample article data for testing"""
    return {
        "title": "Test Article",
        "slug": "test-article",
        "content": "This is test content",
        "category": "technology",
        "author": "Test Author",
        "source": "TestAPI",
        "image": "https://example.com/image.jpg",
        "description": "Test description",
        "published_at": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
    }

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "_id": "user123",
        "username": "testuser",
        "email": "test@example.com",
        "password": "hashed_password",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z",
    }

@pytest.fixture
def sample_admin():
    """Sample admin user data for testing"""
    return {
        "_id": "admin123",
        "username": "admin",
        "email": "admin@example.com",
        "password": "hashed_password",
        "role": "admin",
        "created_at": "2024-01-01T00:00:00Z",
    }
