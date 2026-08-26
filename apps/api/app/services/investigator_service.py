class InvestigatorService:
    """
    AI-powered investigation layer.

    Receives deterministic reconciliation results
    and produces evidence-backed explanations.

    Failure policy:
        If the AI provider is unavailable or raises an exception,
        the system must NOT attempt autonomous action.  Instead it
        sets the case to human_review and records an AI_FAILURE audit
        event so an operator can intervene.
    """

    async def investigate(self, exception_id: int):
        raise NotImplementedError