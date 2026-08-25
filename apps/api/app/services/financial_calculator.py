from dataclasses import dataclass


@dataclass
class ExpectedSettlement:
    gross_amount: int
    fee: int
    tax: int
    expected_net: int


def calculate_expected_settlement(
    gross_amount: int,
    fee: int,
    tax: int,
) -> ExpectedSettlement:

    expected_net = (
        gross_amount
        - fee
        - tax
    )

    return ExpectedSettlement(
        gross_amount=gross_amount,
        fee=fee,
        tax=tax,
        expected_net=expected_net,
    )