from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://admin:password@localhost:27017/trendnexai?authSource=admin"
    DATABASE_NAME: str = "trendnexai"

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
