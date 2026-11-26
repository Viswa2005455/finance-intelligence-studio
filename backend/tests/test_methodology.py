"""The public methodology catalogue is generated from the real engine, so it can never drift from the formulas in use."""

from app.finance import ratios


def test_catalogue_is_public_and_lists_every_engine_ratio_with_its_formula(anon_client):
    r = anon_client.get("/api/public/methodology")
    assert r.status_code == 200
    body = r.json()
    engine = {x.key: x for x in ratios.compute_ratios({})}
    assert {x["key"] for x in body["ratios"]} == set(engine)
    for x in body["ratios"]:
        assert x["formula"] == engine[x["key"]].formula and x["name"] and x["category"]


def test_every_ratio_has_a_typical_range_and_the_method_list_is_present(anon_client):
    body = anon_client.get("/api/public/methodology").json()
    assert all(x["typical"] for x in body["ratios"]), [x["key"] for x in body["ratios"] if not x["typical"]]
    names = [m["name"] for m in body["methods"]]
    assert "Net present value (NPV)" in names and "Beneish M-score" in names
    assert all(m["formula"] and m["what"] and m["caution"] for m in body["methods"])


def test_documented_screen_formulas_match_the_code(anon_client):
    """The Beneish and Altman text on the page must show the coefficients the engine really uses."""
    from app.finance import forensic
    src = open(forensic.__file__, encoding="utf-8").read()
    body = anon_client.get("/api/public/methodology").json()
    texts = {m["name"]: m["formula"] for m in body["methods"]}
    for coef in ("4.84", "0.920", "0.528", "0.404", "0.892", "0.115", "0.172", "4.679", "0.327"):
        assert coef in texts["Beneish M-score"] and coef in src
    for coef in ("1.2", "1.4", "3.3", "0.6", "1.0"):
        assert coef in texts["Altman Z-score (original, listed manufacturers)"]
    for coef in ("6.56", "3.26", "6.72", "1.05"):
        assert coef in texts["Altman Z''-score (non-manufacturers, book equity)"] and coef in src
