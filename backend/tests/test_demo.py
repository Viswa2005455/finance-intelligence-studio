"""The public demo calculator: works without an account, matches the signed-in engine, and is rate limited."""

import pytest


def test_demo_needs_no_account_and_matches_the_engine(anon_client):
    body = {"initial": 100000, "flows": [30000, 35000, 40000, 30000, 20000], "rate": 0.10}
    r = anon_client.post("/api/demo/appraisal", json=body)
    assert r.status_code == 200, r.text
    d = r.json()
    # Hand calculation: -100000 + 30000/1.1 + 35000/1.21 + 40000/1.331 + 30000/1.4641 + 20000/1.61051 = 19,159.9...
    assert d["npv"] == pytest.approx(19159.9, abs=0.5)
    assert d["irr"]["status"] == "unique" and 0.17 < d["irr"]["values"][0] < 0.18
    assert len(d["timeline"]) == 6


def test_demo_rejects_bad_input(anon_client):
    assert anon_client.post("/api/demo/appraisal", json={"initial": -5, "flows": [1], "rate": 0.1}).status_code == 422
    assert anon_client.post("/api/demo/appraisal", json={"initial": 5, "flows": [], "rate": 0.1}).status_code == 422
    assert anon_client.post("/api/demo/appraisal", json={"initial": 5, "flows": [1] * 11, "rate": 0.1}).status_code == 422
    assert anon_client.post("/api/demo/appraisal", json={"initial": 5, "flows": [1], "rate": 3}).status_code == 422


def test_demo_is_rate_limited(anon_client):
    body = {"initial": 100, "flows": [60, 60], "rate": 0.1}
    codes = [anon_client.post("/api/demo/appraisal", json=body).status_code for _ in range(125)]
    assert codes.count(200) == 120 and codes[-1] == 429


def test_other_calculators_still_need_an_account(anon_client):
    assert anon_client.post("/api/finance/appraisal", json={"cash_flows": [-100, 60, 60], "discount_rate": 0.1}).status_code == 401
