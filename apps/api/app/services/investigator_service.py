class InvestigatorService:
    """
    AI-powered investigation layer.

    Receives deterministic reconciliation results
    and produces evidence-backed explanations.
    """

    async def investigate(self, exception_id: int):
        raise NotImplementedError