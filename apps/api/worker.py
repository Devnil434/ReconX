from rq import Worker

from app.queue.redis import (
    redis_client,
)
from app.queue.tasks import (
    reconciliation_queue,
    investigation_queue,
    action_queue,
)


if __name__ == "__main__":

    worker = Worker(
        [
            reconciliation_queue,
            investigation_queue,
            action_queue,
        ],
        connection=redis_client,
    )

    worker.work()
