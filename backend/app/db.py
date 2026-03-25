from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str = "trendnexai"

    class Config:
        env_file = "../.env.local"

settings = Settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
