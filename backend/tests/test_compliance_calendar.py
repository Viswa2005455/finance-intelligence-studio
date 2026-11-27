import datetime as dt

from app.finance import compliance_calendar as cal

GST = {"registration": "regular", "state_code": "27", "aggregate_turnover_prev_fy": 5_000_000, "qrmp": False}


def test_income_tax_dates_come_from_the_engine():
    out = cal.calendar(dt.date(2026, 11, 10))
    dates = {(i["title"], i["date"]) for i in out["items"]}
    assert ("Tax audit report due", "2026-10-21") in dates  # 20 days ago: still listed
    assert any(i["date"] == "2026-11-21" for i in out["items"])
    assert any(i["date"] == "2026-12-31" and "belated" in i["title"] for i in out["items"])
    assert not out["gst_included"]


def test_status_and_ordering():
    out = cal.calendar(dt.date(2026, 11, 18))
    items = out["items"]
    assert [i["date"] for i in items] == sorted(i["date"] for i in items)
    by_date = {i["date"]: i for i in items if i["area"] == "income_tax"}
    assert by_date["2026-11-21"]["status"] == "soon" and by_date["2026-11-21"]["days"] == 3
    assert by_date["2026-10-21"]["status"] == "overdue"
    assert by_date["2027-03-31"]["status"] == "later"
    assert out["needs_attention"] >= 2


def test_old_dates_are_dropped():
    out = cal.calendar(dt.date(2026, 11, 27))
    assert all(i["days"] >= -30 for i in out["items"])
    assert not any(i["date"] == "2026-07-31" for i in out["items"])


def test_gst_dates_monthly_filer():
    out = cal.calendar(dt.date(2026, 11, 5), GST, months=2)
    gst = [i for i in out["items"] if i["area"] == "gst"]
    assert out["gst_included"]
    got = {(i["title"], i["date"]) for i in gst}
    # October supplies are due in November: GSTR-1 on the 11th, GSTR-3B on the 20th
    assert ("GSTR-1 due", "2026-11-11") in got and ("GSTR-3B due", "2026-11-20") in got
    assert ("GSTR-3B due", "2026-12-20") in got
    assert len({i["id"] for i in gst}) == len(gst)  # nothing listed twice


def test_not_registered_has_no_gst():
    out = cal.calendar(dt.date(2026, 11, 5), {**GST, "registration": "not_registered"})
    assert not out["gst_included"] and not any(i["area"] == "gst" for i in out["items"])


def test_endpoint(client):
    r = client.post("/api/tax/calendar", json={"today": "2026-11-18", "gst": {**GST}})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["gst_included"] and d["items"]
    assert client.post("/api/tax/calendar", json={"months": 99}).status_code == 422
