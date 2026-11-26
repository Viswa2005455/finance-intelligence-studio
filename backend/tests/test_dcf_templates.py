"""DCF templates: every template must run through the engine and produce a sensible answer."""

import pytest

from app.finance.dcf import DCFInputs, run_dcf
from app.finance.dcf_templates import TEMPLATES


@pytest.mark.parametrize("t", TEMPLATES, ids=lambda t: t["id"])
def test_every_template_runs_and_gives_a_positive_value_without_errors(t):
    r = run_dcf(DCFInputs(**t["model"]))
    assert r.enterprise_value > 0
    assert len(r.years) == len(t["model"]["revenue_growth"])
    # Terminal growth must stay below the discount rate or the perpetuity formula breaks.
    assert t["model"]["terminal_growth"] < t["model"]["wacc"]


def test_the_startup_template_really_starts_with_losses():
    startup = next(t for t in TEMPLATES if t["id"] == "startup")
    r = run_dcf(DCFInputs(**startup["model"]))
    assert r.years[0].ebit < 0 < r.years[-1].ebit


def test_templates_endpoint_lists_them_for_signed_in_users(client):
    body = client.get("/api/finance/dcf/templates").json()
    assert [t["id"] for t in body["templates"]] == [t["id"] for t in TEMPLATES]
    assert all(t["model"]["wacc"] > 0 for t in body["templates"])


def test_templates_need_an_account(anon_client):
    assert anon_client.get("/api/finance/dcf/templates").status_code == 401
