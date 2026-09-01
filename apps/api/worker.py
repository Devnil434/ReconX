import logging
import time
from rq import Worker

from app.queue.redis import (
    redis_client,
)
from app.queue.tasks import (
    reconciliation_queue,
    investigation_queue,
    action_queue,
)

logger = logging.getLogger("worker")


if __name__ == "__main__":
    while True:
        try:
            redis_client.ping()
            logger.info("Connected to Redis successfully. Starting RQ worker...")
            worker = Worker(
                [
                    reconciliation_queue,
                    investigation_queue,
                    action_queue,
                ],
                connection=redis_client,
            )
            worker.work()
        except Exception as e:
            logger.warning(f"Worker Redis connection failed: {e}. Retrying in 10 seconds...")
            time.sleep(10)
