"""Compliance calendar: the dates the app's own rule sets already know, put in one list in date order.

Nothing here is a new rule. Income-tax and tax-audit dates come from `incometax` and `taxaudit`; GST dates come from
`gst.select_returns`, run for a window of tax periods. Each item carries its source so the reader can check it."""

from __future__ import annotations

import datetime as dt

from . import gst, incometax, taxaudit

SOON_DAYS = 7


def _status(day: dt.date, today: dt.date) -> str:
    delta = (day - today).days
    return "overdue" if delta < 0 else "today" if delta == 0 else "soon" if delta <= SOON_DAYS else "later"


def _item(day: dt.date, today: dt.date, area: str, title: str, detail: str, source: str | None) -> dict:
    return {"id": f"{area}:{title}:{day.isoformat()}", "date": day.isoformat(), "area": area, "title": title, "detail": detail,
            "days": (day - today).days, "status": _status(day, today), "source": source}


def _income_tax(today: dt.date) -> list[dict]:
    out = []
    for key, row in incometax.DUE_DATES.items():
        out.append(_item(row["date"], today, "income_tax", "Income-tax return due", row["label"], incometax.SOURCES.get("due_dates")))
    out.append(_item(incometax.BELATED_LAST, today, "income_tax", "Last date for a belated return",
                     "A return filed after the due date but by this date is a belated return (late fee under section 234F).", incometax.SOURCES.get("due_dates")))
    out.append(_item(incometax.REVISED_LAST, today, "income_tax", "Last date to revise a return",
                     "A return already filed can be revised up to this date.", incometax.SOURCES.get("due_dates")))
    out.append(_item(taxaudit.REPORT_DUE, today, "income_tax", "Tax audit report due",
                     "Form 3CA/3CB-3CD, uploaded after the auditor signs (CBDT Circular 07/2026).", taxaudit.SOURCES.get("circular_7_2026")))
    return out


def _gst(today: dt.date, profile: dict, months: int) -> list[dict]:
    """GST dates for the tax periods from last month for `months` months ahead; the same form and date is listed once."""
    out: dict[tuple[str, str], dict] = {}
    y, m = today.year, today.month
    for _ in range(months + 1):
        for r in gst.select_returns(gst.GSTProfile(**{**profile, "year": y, "month": m})).get("returns", []):
            if not r.get("next_due") or r.get("optional"):
                continue
            key = (r["form"], r["next_due"])
            if key not in out:
                out[key] = _item(dt.date.fromisoformat(r["next_due"]), today, "gst", f"{r['form']} due", f"{r['what']} ({r['frequency']}).", r.get("source"))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return list(out.values())


def calendar(today: dt.date, gst_profile: dict | None = None, months: int = 6) -> dict:
    """Upcoming and recently missed dates, soonest first. Dates more than 30 days past are dropped."""
    items = _income_tax(today)
    if gst_profile and gst_profile.get("registration") != "not_registered":
        # start one period back so a return for last month's supplies is not missed
        y, m = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        items += _gst(dt.date(y, m, 1), gst_profile, months)
        for it in items:
            it["days"] = (dt.date.fromisoformat(it["date"]) - today).days
            it["status"] = _status(dt.date.fromisoformat(it["date"]), today)
    items = [i for i in items if i["days"] >= -30]
    items.sort(key=lambda i: (i["date"], i["area"], i["title"]))
    soon = [i for i in items if i["status"] in ("today", "soon", "overdue")]
    return {"today": today.isoformat(), "items": items, "needs_attention": len(soon),
            "gst_included": bool(gst_profile and gst_profile.get("registration") != "not_registered"),
            "note": "Dates come from the rule sets in this app (income tax and GST for the period shown). Check them on the portal before relying on them; "
                    "due dates are sometimes extended by circular."}
