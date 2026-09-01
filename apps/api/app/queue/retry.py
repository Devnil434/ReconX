from rq import Retry


DEFAULT_RETRY = Retry(
    max=3,
    interval=[
        10,
        30,
        120,
    ],
)
