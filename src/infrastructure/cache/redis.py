import logging

from redis.asyncio import Redis

from src.core.config import settings

redis_client: Redis | None = None
logger = logging.getLogger(__name__)


def init_redis() -> None:
    global redis_client
    redis_client = Redis.from_url(str(settings.redis.url))
    logger.info("Redis client initialized")


async def get_redis() -> Redis:
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
        logger.info("Redis client closed")
