"""
MongoDB database setup and initialization for TrendNexAI.
Creates indexes and collections for optimal performance.
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncMongoClient, AsyncIOMotorDatabase
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database initialization, migrations, and optimization"""
    
    def __init__(self):
        self.mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
        )
        self.db_name = "trendnexai"
        self.client = None
        self.db = None
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Connect to MongoDB"""
        try:
            self.client = AsyncMongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            
            # Test connection
            await self.db.command("ping")
            logger.info("✓ MongoDB connected successfully")
            
            return self.db
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    async def create_indexes(self):
        """Create all necessary indexes for optimal performance"""
        logger.info("Creating database indexes...")
        
        articles = self.db.articles
        
        # Index 1: Slug (unique for fast lookups)
        await articles.create_index("slug", unique=True, background=True)
        logger.info("✓ Index: slug (unique)")
        
        # Index 2: Status & CreatedAt (for filtered lists)
        await articles.create_index([("status", 1), ("createdAt", -1)], background=True)
        logger.info("✓ Index: status + createdAt")
        
        # Index 3: Category & CreatedAt (for category pages)
        await articles.create_index([("category", 1), ("createdAt", -1)], background=True)
        logger.info("✓ Index: category + createdAt")
        
        # Index 4: Created date (for sorting)
        await articles.create_index("createdAt", background=True)
        logger.info("✓ Index: createdAt")
        
        # Index 5: Tags (for tag-based searches)
        await articles.create_index("tags", background=True)
        logger.info("✓ Index: tags")
        
        # Index 6: Views (for trending articles)
        await articles.create_index("views", background=True)
        logger.info("✓ Index: views")
        
        # Index 7: Text search indexes for full-text search
        await articles.create_index([
            ("title", "text"),
            ("summary", "text"),
            ("content.en", "text"),
            ("tags", "text")
        ], background=True)
        logger.info("✓ Index: full-text search (title, summary, content, tags)")
        
        # Index 8: Author (for filtering by author)
        await articles.create_index("author", background=True)
        logger.info("✓ Index: author")
        
        # Index 9: Language (for multi-language filtering)
        await articles.create_index("language", background=True)
        logger.info("✓ Index: language")
        
        # Index 10: Composite index for admin dashboard
        await articles.create_index([
            ("status", 1),
            ("createdAt", -1),
            ("category", 1)
        ], background=True)
        logger.info("✓ Index: status + createdAt + category (admin)")
        
        # Index 11: Fingerprint for deduplication
        await articles.create_index("fingerprint", sparse=True, background=True)
        logger.info("✓ Index: fingerprint (sparse)")
        
        # Index 12: Published articles with pagination
        await articles.create_index([
            ("status", 1),
            ("publishedAt", -1)
        ], background=True)
        logger.info("✓ Index: status + publishedAt")
        
        logger.info("✓ All indexes created successfully")
    
    async def create_collections(self):
        """Create collections with schema validation"""
        logger.info("Creating collections...")
        
        # Articles collection
        try:
            await self.db.create_collection("articles")
            logger.info("✓ Created collection: articles")
        except Exception as e:
            logger.warning(f"Articles collection may already exist: {e}")
        
        # Create collection validators for data integrity
        await self._set_collection_validation()
    
    async def _set_collection_validation(self):
        """Set MongoDB collection validators for schema validation"""
        articles_validator = {
            "bsonType": "object",
            "required": ["title", "slug", "category", "status"],
            "properties": {
                "title": {"bsonType": "string", "minLength": 5, "maxLength": 200},
                "slug": {"bsonType": "string"},
                "category": {"bsonType": "string"},
                "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
                "status": {"enum": ["draft", "published", "archived"]},
                "language": {"enum": ["en", "te", "ta", "kn", "ml"]},
                "seo_title": {"bsonType": "string"},
                "seo_description": {"bsonType": "string"},
                "seo_keywords": {"bsonType": "array"},
                "content": {
                    "bsonType": "object",
                    "properties": {
                        "en": {"bsonType": "string"},
                        "te": {"bsonType": "string"},
                        "ta": {"bsonType": "string"},
                        "kn": {"bsonType": "string"},
                        "ml": {"bsonType": "string"}
                    }
                },
                "views": {"bsonType": "int", "minimum": 0},
                "ai_generated": {"bsonType": "bool"},
                "createdAt": {"bsonType": "date"},
                "updatedAt": {"bsonType": "date"},
                "publishedAt": {"bsonType": "date"}
            }
        }
        
        try:
            await self.db.command(
                "collMod",
                "articles",
                validator={"$jsonSchema": articles_validator}
            )
            logger.info("✓ Collection validators set")
        except Exception as e:
            logger.warning(f"Could not set validators (may not exist yet): {e}")
    
    async def init_database(self):
        """Initialize database (connect, create collections, add indexes)"""
        logger.info("Initializing TrendNexAI database...")
        await self.connect()
        await self.create_collections()
        await self.create_indexes()
        logger.info("✓ Database initialization complete")
    
    async def drop_database(self):
        """Drop entire database (USE WITH CAUTION!)"""
        if self.db:
            await self.client.drop_database(self.db_name)
            logger.warning(f"✗ Database '{self.db_name}' dropped")
    
    async def get_database_stats(self):
        """Get database statistics"""
        stats = await self.db.command("dbStats")
        return stats
    
    async def create_backup_collection(self):
        """Create a backup of articles collection"""
        try:
            articles = self.db.articles
            backup = self.db.articles_backup
            
            # Copy all documents
            async for doc in articles.find():
                await backup.insert_one(doc)
            
            logger.info("✓ Backup created")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

# Global instance
db_manager = None

async def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

async def initialize_database():
    """Initialize database on application startup"""
    manager = await get_db_manager()
    await manager.init_database()

async def close_database():
    """Close database on application shutdown"""
    manager = await get_db_manager()
    await manager.disconnect()

# Migration functions for schema updates
async def add_ai_generated_flag():
    """Migration: Add ai_generated flag to existing articles"""
    articles = db.articles
    result = await articles.update_many(
        {"ai_generated": {"$exists": False}},
        {"$set": {"ai_generated": False}}
    )
    logger.info(f"Migration: Updated {result.modified_count} articles with ai_generated flag")

async def add_fingerprint_field():
    """Migration: Add fingerprint for deduplication"""
    from hashlib import md5
    articles = db.articles
    
    count = 0
    async for article in articles.find({"fingerprint": {"$exists": False}}):
        fingerprint = md5(
            f"{article['title']}{article.get('summary', '')}".encode()
        ).hexdigest()
        
        await articles.update_one(
            {"_id": article["_id"]},
            {"$set": {"fingerprint": fingerprint}}
        )
        count += 1
    
    logger.info(f"Migration: Added fingerprint to {count} articles")

# Example usage for running migrations
async def run_migrations():
    """Run all pending migrations"""
    logger.info("Running database migrations...")
    await add_ai_generated_flag()
    await add_fingerprint_field()
    logger.info("✓ All migrations completed")

if __name__ == "__main__":
    # For standalone script execution
    async def main():
        manager = DatabaseManager()
        await manager.init_database()
    
    asyncio.run(main())
