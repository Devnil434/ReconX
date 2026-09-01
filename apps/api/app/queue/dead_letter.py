from rq import Queue

from app.queue.config import redis


dead_letter_queue = Queue(
    "dead-letter",
    connection=redis,
)
