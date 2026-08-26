import os


def should_fail(failure: str) -> bool:
    """
    Check whether a named failure scenario is currently enabled.

    Enabled failures are listed as a comma-separated value in the
    FAILURE_INJECTION environment variable.

    Example:
        FAILURE_INJECTION=webhook_timeout,db_unavailable

    Usage in code:
        from app.testing.failures import should_fail

        if should_fail("webhook_timeout"):
            raise RuntimeError("Injected webhook failure")
    """
    enabled = os.getenv("FAILURE_INJECTION", "")
    return failure in enabled.split(",")
