"""Property-based tests: rules that must hold for any sensible input, checked on many generated cases (Hypothesis).

Where a hand-worked example shows one case is right, these show the engines obey the identities finance is built on:
NPV is zero at the IRR, higher rates lower the value of positive cash flows, DuPont multiplies back to ROE, and so on."""

import math

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from app.files.tabular import normalise_decimal_commas, parse_number
from app.finance import ratio_insights, ratios, tvm
from app.finance.dcf import DCFInputs, run_dcf

FAST = settings(max_examples=120, deadline=None, suppress_health_check=[HealthCheck.too_slow])

money = st.floats(min_value=1, max_value=1e7, allow_nan=False, allow_infinity=False)


@st.composite
def conventional_flows(draw):
    """One outflow now, then positive inflows: the usual project, which has exactly one IRR."""
    out = draw(money)
    inflows = draw(st.lists(money, min_size=1, max_size=8))
    # The project must pay back (so an IRR above zero exists) but not return more than 8x in total: the solver searches rates up to
    # 1000% and says so in its message, so a 12x one-year return is outside the documented range rather than a failure.
    assume(out * 1.01 < sum(inflows) < out * 8)
    return [-out, *inflows]


@FAST
@given(conventional_flows())
def test_npv_is_zero_at_the_irr(flows):
    res = tvm.irr(flows)
    assert res.status == "unique"
    scale = sum(abs(f) for f in flows)
    assert abs(tvm.npv(res.irrs[0], flows)) <= 1e-6 * scale


@FAST
@given(conventional_flows(), st.floats(min_value=0, max_value=0.5), st.floats(min_value=0.001, max_value=0.4))
def test_a_higher_discount_rate_never_raises_the_npv_of_a_conventional_project(flows, rate, bump):
    assert tvm.npv(rate + bump, flows) <= tvm.npv(rate, flows) + 1e-6


@FAST
@given(conventional_flows(), st.floats(min_value=0, max_value=0.4))
def test_discounted_payback_is_never_earlier_than_payback(flows, rate):
    plain = tvm.payback_period(flows)
    disc = tvm.discounted_payback_period(rate, flows)
    if disc.period is not None:
        assert plain.period is not None and disc.period >= plain.period - 1e-9


@FAST
@given(conventional_flows(), st.floats(min_value=0, max_value=0.3))
def test_a_positive_npv_means_the_profitability_index_is_above_one(flows, rate):
    npv = tvm.npv(rate, flows)
    assume(abs(npv) > 1e-6 * sum(abs(f) for f in flows))
    assert (tvm.profitability_index(rate, flows) > 1) == (npv > 0)


positive_base = st.floats(min_value=1_000, max_value=1e9, allow_nan=False, allow_infinity=False)


@FAST
@given(
    revenue=positive_base, cogs_share=st.floats(0.2, 0.9), net_share=st.floats(-0.3, 0.4), assets_x=st.floats(0.3, 5), equity_share=st.floats(0.05, 0.95),
)
def test_dupont_always_multiplies_back_to_roe(revenue, cogs_share, net_share, assets_x, equity_share):
    ta = revenue * assets_x
    data = {"revenue": revenue, "cogs": revenue * cogs_share, "net_income": revenue * net_share, "total_assets": ta, "total_equity": ta * equity_share}
    results = [r for r in ratios.compute_ratios(data) if r.status == "ok"]
    values = {r.key: r.value for r in results}
    dp = ratio_insights.dupont(values)
    assert dp is not None
    assert dp["product"] == pytest.approx(values["roe"], rel=1e-9, abs=1e-9)
    assert dp["consistent"] is True


@FAST
@given(revenue=positive_base, cogs_share=st.floats(0, 1))
def test_gross_margin_is_a_percentage_between_zero_and_a_hundred(revenue, cogs_share):
    out = {r.key: r for r in ratios.compute_ratios({"revenue": revenue, "cogs": revenue * cogs_share})}
    assert 0 <= out["gross_margin"].value <= 100 + 1e-9


@FAST
@given(st.floats(min_value=0.07, max_value=0.14), st.floats(min_value=0.001, max_value=0.05))
def test_a_higher_wacc_never_raises_the_enterprise_value(wacc, bump):
    def ev(w):
        return run_dcf(DCFInputs(base_revenue=1000, revenue_growth=[0.1, 0.09, 0.08, 0.07, 0.06], ebit_margin=[0.2], tax_rate=0.25, da_pct_revenue=0.04,
                                 capex_pct_revenue=0.05, nwc_pct_revenue=0.1, wacc=w, terminal_growth=0.03, terminal_method="gordon", exit_multiple=None,
                                 debt=0, cash=0, shares_outstanding=None, mid_year=False)).enterprise_value
    assert ev(wacc + bump) <= ev(wacc) + 1e-6


@FAST
@given(st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False))
def test_numbers_formatted_with_thousands_commas_parse_back(x):
    x = round(x, 2)
    txt = f"{abs(x):,.2f}"
    v, _ = parse_number(f"({txt})" if x < 0 else txt)
    assert v == pytest.approx(x, abs=0.005)


@FAST
@given(st.integers(min_value=0, max_value=10**9), st.integers(min_value=1, max_value=99))
def test_european_decimal_commas_parse_back(whole, cents):
    eu = f"{whole:,}".replace(",", ".") + f",{cents:02d}"
    grid, converted = normalise_decimal_commas([["Item", "FY1"], ["Amount", eu]])
    assert converted == 1
    v, _ = parse_number(grid[1][1])
    assert v == pytest.approx(whole + cents / 100, abs=0.005)


@FAST
@given(st.lists(st.integers(min_value=1, max_value=10**9), min_size=2, max_size=6))
def test_thousands_style_files_are_never_changed_by_the_decimal_comma_rule(values):
    grid = [["Item", *[f"FY{i}" for i in range(len(values))]], ["Amount", *[f"{v:,}" for v in values]]]
    assume(any("," in c for c in grid[1][1:]))
    out, converted = normalise_decimal_commas(grid)
    assert converted == 0 and out == grid
    assert all(math.isclose(parse_number(c)[0], v) for c, v in zip(out[1][1:], values))
