import redis

from app.core.config import settings

# RQ requires decode_responses=False (bytes mode) for its internal protocol.
# Do NOT set decode_responses=True on this client — it will cause
# "Worker found an unhandled exception, quitting" errors.
redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=False,
)

# A separate client for application-level string operations (e.g. caching).
redis_str_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)