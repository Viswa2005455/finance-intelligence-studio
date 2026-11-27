import pytest

from app.finance import FinanceInputError, cashflow
from app.finance.cashflow import CashLine

P = ["M1", "M2", "M3"]
RECEIPTS = [CashLine("Sales", [0, 100, 100])]
PAYMENTS = [CashLine("Costs", [50, 0, 0])]


def test_defaults_match_the_old_behaviour():
    r = cashflow.cash_budget(P, 0, RECEIPTS, PAYMENTS, 0)
    assert r.total_financing == 50 and r.total_interest == 0 and r.total_repayment == 0
    assert [x.closing for x in r.periods] == [0, 100, 200]


def test_interest_and_repayment_worked_by_hand():
    # M1 short by 50 -> draw 50. M2 interest = 50 x 12% / 12 = 0.5; cash 99.5, repay all 50 -> 49.5. M3 no loan -> 149.5.
    r = cashflow.cash_budget(P, 0, RECEIPTS, PAYMENTS, 0, interest_rate_pct=12, repay=True)
    assert [x.financing for x in r.periods] == [50, 0, 0]
    assert [x.interest for x in r.periods] == [0, 0.5, 0]
    assert [x.repayment for x in r.periods] == [0, 50, 0]
    assert [round(x.closing, 2) for x in r.periods] == [0, 49.5, 149.5]
    assert r.total_interest == 0.5 and r.peak_loan == 50 and r.ending_loan == 0


def test_loan_stays_when_not_repaying():
    r = cashflow.cash_budget(P, 0, RECEIPTS, PAYMENTS, 0, interest_rate_pct=12, repay=False)
    assert r.total_interest == pytest.approx(1.0)  # 0.5 in M2 and again in M3
    assert r.ending_loan == 50 and [round(x.closing, 2) for x in r.periods] == [0, 99.5, 199.0]
    assert any("still owed" in w for w in r.warnings)


def test_repayment_keeps_the_minimum_balance():
    r = cashflow.cash_budget(P, 0, RECEIPTS, PAYMENTS, 80, interest_rate_pct=0, repay=True)
    # M1: pre -50, draw 130 to reach 80. M2: pre 180, repay min(130, 100) = 100 -> closing 80, loan 30. M3: repay 30 -> 150.
    assert [x.financing for x in r.periods] == [130, 0, 0]
    assert [x.repayment for x in r.periods] == [0, 100, 30]
    assert [x.closing for x in r.periods] == [80, 80, 150] and r.ending_loan == 0


def test_rate_validation():
    with pytest.raises(FinanceInputError):
        cashflow.cash_budget(P, 0, RECEIPTS, PAYMENTS, 0, interest_rate_pct=150)
