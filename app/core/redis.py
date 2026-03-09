from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from redis.asyncio import Redis
from app.core.config import settings
from loguru import logger
from typing import Optional

class RedisManager:
    def __init__(self):
        self.connection: Optional[Redis] = None
        self.checkpointer: Optional[AsyncRedisSaver] = None

    async def connect(self):
        """Initialize Redis connection and checkpointer."""
        logger.info(f"Connecting to Redis at {settings.REDIS_URL}...")
        try:
            # Create a raw Redis connection first
            self.connection = Redis.from_url(settings.REDIS_URL)
            
            # We use an async context manager hook provided by LangGraph for Redis
            self._context_manager = AsyncRedisSaver.from_conn_string(settings.REDIS_URL)
            self.checkpointer = await self._context_manager.__aenter__()
            logger.info("Successfully connected to Redis and initialized checkpointer.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if hasattr(self, '_context_manager') and self._context_manager:
            logger.info("Closing Redis checkpointer connection...")
            await self._context_manager.__aexit__(None, None, None)
            logger.info("Redis checkpointer closed.")

# Global instance
redis_manager = RedisManager()
