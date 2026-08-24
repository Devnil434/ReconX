class ReconciliationService:
    """
    Deterministic financial reconciliation engine.

    This service must NOT use an LLM.
    """

    def reconcile(self, payment, settlement, bank_transaction):
        raise NotImplementedError