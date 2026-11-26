"""Ratio insights: levels follow the stated thresholds, context notes appear only when two ratios agree,
and every calculated ratio gets a reading while uncalculated ones get none."""

from dataclasses import asdict

from app.finance import ratio_insights as ri
from app.finance import ratios

# The same example the Ratio Analysis page loads.
EXAMPLE = {
    "revenue": 5000, "cogs": 3100, "operating_income": 620, "depreciation_amortization": 180, "interest_expense": 95, "net_income": 390,
    "cash": 260, "marketable_securities": 40, "receivables": 720, "inventory": 610, "current_assets": 1700, "total_assets": 4200,
    "current_liabilities": 980, "accounts_payable": 430, "total_debt": 1150, "total_liabilities": 2300, "total_equity": 1900,
    "operating_cash_flow": 560, "debt_service": 310, "tax_rate": 0.25, "shares_outstanding": 100, "share_price": 58, "wacc": 0.10,
}


def _run(data):
    results = [asdict(r) for r in ratios.compute_ratios(data)]
    summary = ri.attach(results)
    return {r["key"]: r for r in results}, summary


def test_every_calculated_ratio_has_a_reading_and_missing_ones_have_none():
    by_key, _ = _run({**EXAMPLE, "inventory": None})
    for r in by_key.values():
        if r["status"] == "ok":
            ins = r["insight"]
            assert ins and ins["headline"] and ins["meaning"] and ins["next_step"] and ins["level"] in ("strong", "good", "watch", "concern", "info")
            assert r["key"] in ri.TYPICAL
        else:
            assert r["insight"] is None


def test_current_ratio_levels_follow_the_thresholds():
    assert ri.insight_for("current_ratio", 0.8, {})["level"] == "concern"
    assert ri.insight_for("current_ratio", 1.1, {})["level"] == "watch"
    assert ri.insight_for("current_ratio", 1.3, {})["level"] == "good"
    assert ri.insight_for("current_ratio", 2.0, {})["level"] == "strong"
    assert ri.insight_for("current_ratio", 4.0, {})["level"] == "watch"  # idle capital


def test_example_values_hand_checked():
    by_key, _ = _run(EXAMPLE)
    # 1700 / 980 = 1.73 -> strong; 5000-3100 / 5000 = 38% -> info only; 620/95 = 6.5x -> good
    assert by_key["current_ratio"]["insight"]["level"] == "strong"
    assert by_key["gross_margin"]["insight"]["level"] == "info"
    assert by_key["interest_coverage"]["insight"]["level"] == "good"
    assert by_key["debt_to_equity"]["insight"]["level"] == "good"  # 1150 / 1900 = 0.61


def test_roic_spread_drives_the_roic_reading_when_wacc_is_given():
    by_key, _ = _run(EXAMPLE)
    spread = by_key["roic_wacc_spread"]["value"]
    assert (by_key["roic"]["insight"]["level"] == "strong") == (spread > 3)


def test_context_note_when_high_roe_is_leveraged():
    ctx = ri._context("roe", {"roe": 22.0, "debt_to_equity": 2.4})
    assert ctx and "borrowing" in ctx[0]
    assert ri._context("roe", {"roe": 22.0, "debt_to_equity": 0.4}) == []


def test_summary_counts_and_flags():
    # Deliberately weak: negative net margin, tiny current ratio, heavy debt.
    weak = {"revenue": 1000, "net_income": -50, "operating_income": -20, "current_assets": 300, "current_liabilities": 600,
            "total_debt": 900, "total_equity": 300, "interest_expense": 80}
    by_key, summary = _run(weak)
    assert by_key["net_margin"]["insight"]["level"] == "concern"
    assert by_key["current_ratio"]["insight"]["level"] == "concern"
    assert by_key["debt_to_equity"]["insight"]["level"] == "concern"
    assert summary["overall"] in ("Under pressure", "Mixed")
    assert any(c["key"] == "net_margin" for c in summary["concerns"])
    assert "concern" in summary["headline"]


def test_summary_with_no_scored_ratios_does_not_claim_a_verdict():
    _, summary = _run({"revenue": 1000, "cogs": 600})  # gross margin only: an "info" reading
    assert summary["overall"] == "Not enough data"
    assert "Not enough" in summary["headline"]


def test_endpoint_returns_summary(client):
    r = client.post("/api/finance/ratios", json={"data": EXAMPLE})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["headline"] and body["ratios"][0]["insight"]["headline"]
