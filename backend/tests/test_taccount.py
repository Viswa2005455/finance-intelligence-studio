"""Two-sided (To / By) Trading and Profit & Loss account import."""

import pytest

from app.files.tabular import parse_xlsx
from app.files.taccount import NotTAccount, find_layout, parse_taccount

from .taccount_fixture import plain_table_bytes, taccount_bytes


def by_key(r):
    return {l["key"]: l for l in r["lines"] if l["key"]}


def test_reads_both_sides_with_sources():
    r = parse_taccount(taccount_bytes())
    assert r["company"] == "SAMPLE TRADERS"
    assert r["periods"] == ["Mar 2025"]
    k = by_key(r)
    # groups are summed from their lines, and say so; each keeps its source cells
    assert k["revenue"]["values"] == [6500] and k["revenue"]["source"] == "Sheet3!H11 + H12"
    assert k["gross_profit"]["values"] == [3000] and k["gross_profit"]["source"] == "Sheet3!E16"
    assert k["net_income"]["values"] == [1900] and k["net_income"]["source"] == "Sheet3!E21"
    labels = {l["label"]: l for l in r["lines"]}
    assert labels["Opening Stock (sum of its lines)"]["values"] == [1000]
    assert labels["Purchases (sum of its lines)"]["values"] == [4000]
    assert labels["Closing Stock (sum of its lines)"]["values"] == [1500]  # the stray figure in column J is ignored


def test_derived_lines_are_labelled_and_reconcile():
    r = parse_taccount(taccount_bytes())
    k = by_key(r)
    assert k["cogs"]["values"] == [1000 + 4000 - 1500] and k["cogs"]["source"] == "derived" and "derived" in k["cogs"]["label"]
    assert k["operating_income"]["values"] == [3000 - 1100] and "derived" in k["operating_income"]["label"]
    assert r["units"] == ""  # the file states no currency or unit, so none is claimed


def test_cogs_is_dropped_when_it_does_not_reconcile():
    r = parse_taccount(taccount_bytes(bad_gross_profit=True))
    assert "cogs" not in by_key(r)
    assert any("does not equal the gross profit" in n for n in r["notes"])


def test_stops_after_the_first_account():
    r = parse_taccount(taccount_bytes())
    names = [l["label"] for l in r["lines"]]
    assert "Capital Account" not in names and "Sundry Creditors" not in names and "Building" not in names
    assert any("continues below" in n for n in r["notes"])
    r2 = parse_taccount(taccount_bytes(with_balance_sheet=False))
    assert not any("continues below" in n for n in r2["notes"])


def test_period_comes_from_the_title_or_is_labelled_unknown():
    assert parse_taccount(taccount_bytes(title="PROFIT & LOSS ACCOUNT FOR THE YEAR ENDED 31st March 2024"))["periods"] == ["Mar 2024"]
    r = parse_taccount(taccount_bytes(title="TRADING AND PROFIT & LOSS A/C"))
    assert r["periods"] == ["Current year"] and any("year-end" in n for n in r["notes"])


def test_ordinary_tables_are_not_mistaken_for_an_account():
    from openpyxl import Workbook
    import io

    assert find_layout([["Item", "Amount"], ["Rent", 100]]) is None
    with pytest.raises(NotTAccount):
        parse_taccount(plain_table_bytes())
    buf = io.BytesIO()
    Workbook().save(buf)
    with pytest.raises(NotTAccount):
        parse_taccount(buf.getvalue())


def test_sheet_is_flagged_by_the_general_parser():
    sheets = {s["name"]: s for s in parse_xlsx(taccount_bytes())["sheets"]}
    assert sheets["Sheet3"].get("layout") == "t_account" and "layout" not in sheets["Notes"]


def test_account_endpoint(client):
    up = client.post("/api/uploads", files=[("files", ("firm.xlsx", taccount_bytes()))]).json()["results"][0]
    assert up["ok"], up
    r = client.post(f"/api/analysis/taccount/{up['upload']['id']}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["sheet"] == "Sheet3" and body["periods"] == ["Mar 2025"]
    assert {l["key"] for l in body["lines"] if l["key"]} >= {"revenue", "gross_profit", "cogs", "net_income", "operating_income"}
    # the upload itself is flagged, so the page knows which endpoint to call
    full = client.get(f"/api/uploads/{up['upload']['id']}").json()
    assert any(s.get("layout") == "t_account" for s in full["analysis"]["sheets"])
    csv = client.post("/api/uploads", files=[("files", ("a.csv", b"x,y\n1,2\n"))]).json()["results"][0]["upload"]
    assert client.post(f"/api/analysis/taccount/{csv['id']}").status_code == 422
