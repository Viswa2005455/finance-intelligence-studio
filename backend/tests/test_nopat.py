"""NOPAT and the ratios built on it."""

import pytest

from app.files.routing import suggest_statement_mapping
from app.files.tabular import analyse_grid
from app.finance import FinanceInputError
from app.finance.ratios import ITEMS, compute_ratios


def by_key(data, **kw):
    return {r.key: r for r in compute_ratios(data, **kw)}


BASE = {"operating_income": 1000, "revenue": 8000, "total_debt": 600, "total_equity": 1400, "cash": 200}


def test_nopat_uses_the_tax_rate_supplied():
    r = by_key({**BASE, "tax_rate": 0.25})
    assert r["nopat"].status == "ok" and r["nopat"].value == pytest.approx(750)
    assert r["nopat_margin"].value == pytest.approx(750 / 8000 * 100)
    assert r["invested_capital"].value == pytest.approx(600 + 1400 - 200)


def test_tax_rate_is_derived_from_tax_and_profit_before_tax():
    r = by_key({**BASE, "income_tax": 30, "pretax_income": 120})  # 25%
    assert r["nopat"].value == pytest.approx(750)
    assert any("derived as income tax / profit before tax = 25.0%" in n for n in r["nopat"].notes)
    assert r["nopat"].inputs["income tax expense"] == 30 and r["nopat"].inputs["profit before tax"] == 120


def test_a_supplied_rate_overrides_the_derived_one():
    r = by_key({**BASE, "tax_rate": 0.10, "income_tax": 30, "pretax_income": 120})
    assert r["nopat"].value == pytest.approx(900)
    assert not any("derived" in n for n in r["nopat"].notes)


def test_no_rate_is_derived_from_a_loss_or_an_impossible_figure():
    for extra in ({"income_tax": 5, "pretax_income": -50}, {"income_tax": 200, "pretax_income": 100}, {"income_tax": 5}):
        r = by_key({**BASE, **extra})
        assert r["nopat"].status == "missing" and "Effective tax rate (decimal)" in r["nopat"].missing


def test_roic_is_unchanged_and_now_works_without_a_typed_tax_rate():
    typed = by_key({**BASE, "tax_rate": 0.25})["roic"].value
    assert typed == pytest.approx(750 / (600 + 1400 - 200) * 100)
    derived = by_key({**BASE, "income_tax": 30, "pretax_income": 120})["roic"]
    assert derived.status == "ok" and derived.value == pytest.approx(typed)


def test_average_invested_capital_is_used_when_opening_balances_are_given():
    r = by_key({**BASE, "tax_rate": 0.25, "total_debt_prior": 800, "total_equity_prior": 1000})
    avg = (600 + 800) / 2 + (1400 + 1000) / 2 - 200
    assert r["roic"].value == pytest.approx(750 / avg * 100)
    assert r["invested_capital_turnover"].value == pytest.approx(8000 / avg)


def test_economic_profit_and_spread_need_the_cost_of_capital():
    d = {**BASE, "tax_rate": 0.25}
    r = by_key(d)
    assert r["economic_profit"].status == "missing" and "Cost of capital (WACC, decimal)" in r["economic_profit"].missing
    assert r["roic_wacc_spread"].status == "missing"
    r = by_key({**d, "wacc": 0.10})
    assert r["economic_profit"].value == pytest.approx(750 - 0.10 * 1800)
    assert r["roic_wacc_spread"].value == pytest.approx(750 / 1800 * 100 - 10)


def test_negative_invested_capital_is_not_meaningful():
    r = by_key({**BASE, "tax_rate": 0.25, "cash": 5000})
    assert r["roic"].status == "undefined" and r["invested_capital_turnover"].status == "undefined"


def test_wacc_must_be_a_decimal():
    with pytest.raises(FinanceInputError):
        compute_ratios({**BASE, "tax_rate": 0.25, "wacc": 10})


def test_existing_ratio_keys_are_still_present():
    keys = {r.key for r in compute_ratios({})}
    assert {"current_ratio", "roe", "roic", "net_margin", "pe"} <= keys
    assert {"nopat", "nopat_margin", "invested_capital", "invested_capital_turnover", "roic_wacc_spread", "economic_profit"} <= keys
    assert {"income_tax", "pretax_income", "wacc"} <= set(ITEMS)


def test_income_tax_and_profit_before_tax_are_picked_up_from_a_statement():
    grid = [["Line", "FY2025", "FY2026"],
            ["Operating income", 133050, 158063],
            ["Income before provision for income taxes", 132729, 159237],
            ["Provision for income taxes", 20719, 27062],
            ["Net income", 112010, 132175]]
    sheet = analyse_grid("Income", grid, excel=True)
    keys = {m["item"]: m for m in suggest_statement_mapping([sheet], "f.xlsx")}
    assert keys["pretax_income"]["value"] == 159237 and keys["income_tax"]["value"] == 27062
    assert keys["income_tax"]["prior_value"] == 20719
