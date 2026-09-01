class PostActionReconciliation:
    """
    Re-runs reconciliation after an action completes.

    The reconciliation cycle is:
        ACTION -> VERIFY -> RECONCILE AGAIN

    This lets the system confirm whether the action (e.g. refund)
    actually resolved the exception, e.g.:
        Before: exception = 564
        Action: refund 564
        After:  expected = 0, actual = 0  ->  RESOLVED
    """

    def __init__(self, reconciliation_service):
        self.reconciliation = reconciliation_service

    async def verify(
        self,
        case_id: str,
    ) -> dict:
        """
        Re-reconcile the case identified by case_id.

        Returns the reconciliation result from the service.
        """
        result = await self.reconciliation.reconcile_case(case_id)
        return result
