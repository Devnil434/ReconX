from app.integrations.razorpay.client import RazorpayClient


class ActionVerifier:
    """
    Verifies the real state of an action on the Razorpay side.

    Used after execute() to avoid the UNKNOWN state: instead of
    assuming success or failure after a timeout, we explicitly
    fetch the canonical state from Razorpay.
    """

    def __init__(self, razorpay_client: RazorpayClient | None = None):
        self.client = razorpay_client or RazorpayClient()

    def verify_refund(
        self,
        refund_id: str,
    ) -> dict:
        """
        Fetches the refund from Razorpay and returns a verified flag.

        Returns:
            {"verified": True,  "status": "processed"}
            {"verified": False, "status": "pending"}
        """
        refund = self.client.fetch_refund(refund_id)
        status = refund.get("status")

        verified = status in {"processed", "successful"}

        return {
            "verified": verified,
            "status": status,
            "refund_id": refund_id,
        }
