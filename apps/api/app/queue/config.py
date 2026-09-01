from redis import Redis
from rq import Queue

from app.core.config import settings


redis = Redis.from_url(
    settings.redis_url,
    decode_responses=False,
)

reconciliation_queue = Queue(
    "reconciliation",
    connection=redis,
    default_timeout=300,
)

investigation_queue = Queue(
    "investigation",
    connection=redis,
    default_timeout=300,
)

action_queue = Queue(
    "actions",
    connection=redis,
    default_timeout=300,
)
