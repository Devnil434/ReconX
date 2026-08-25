from datetime import timedelta


class TimingDetector:

    def is_late(
        self,
        payment,
        settlement,
        allowed_days: int = 3,
    ) -> bool:

        if not payment.captured_at:
            return False

        expected_date = (
            payment.captured_at
            + timedelta(days=allowed_days)
        )

        return (
            settlement.settlement_date
            > expected_date
        )