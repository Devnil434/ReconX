from rq import Queue

from app.queue.redis import (
    redis_client,
)


reconciliation_queue = Queue(
    "reconciliation",
    connection=redis_client,
)

investigation_queue = Queue(
    "investigation",
    connection=redis_client,
)

action_queue = Queue(
    "actions",
    connection=redis_client,
)