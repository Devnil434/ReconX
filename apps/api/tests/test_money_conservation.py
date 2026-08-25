def test_money_conservation():
    gross = 100_000
    fee = 2_000
    tax = 360

    expected = (
        gross - fee - tax
    )

    actual = 97_640

    assert expected == actual
