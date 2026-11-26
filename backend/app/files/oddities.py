"""Things in an uploaded file that look wrong or unusual, found before any analysis is run.

These are prompts to look, never corrections: nothing in the data is changed. Each finding says what was seen, where, and
why it matters. Checks stay deliberately conservative so a normal file produces no findings.
"""

from __future__ import annotations

import statistics
from collections import Counter

Finding = dict


def _f(severity: str, title: str, detail: str, where: str | None = None) -> Finding:
    return {"severity": severity, "title": title, "detail": detail, "where": where}


def _row_series(sheets: list[dict]) -> list[tuple[str, dict]]:
    return [(sh.get("name", "Sheet"), s) for sh in sheets for s in sh.get("series", []) if s.get("orientation") == "row"]


def _duplicate_periods(sheets: list[dict]) -> list[Finding]:
    out = []
    for sh in sheets:
        names = [c["name"] for c in sh.get("columns", []) if c.get("dtype") == "number" and not str(c["name"]).startswith("Column ")]
        dup = [n for n, k in Counter(names).items() if k > 1]
        if dup:
            out.append(_f("high", f"Period '{dup[0]}' appears more than once",
                          f"The column heading {dup[0]!r} is used for {Counter(names)[dup[0]]} columns. Figures for different periods may be mixed together.", sh.get("name")))
    return out


def _unit_mix(rows: list[tuple[str, dict]]) -> list[Finding]:
    out = []
    for sheet, s in rows:
        vals = [v for v in s["values"] if isinstance(v, (int, float)) and v != 0]
        if len(vals) < 3:
            continue
        med = statistics.median(abs(v) for v in vals)  # the typical size of this line across all its periods
        for i, v in enumerate(s["values"]):
            if not isinstance(v, (int, float)) or v == 0:
                continue
            if med > 0 and (abs(v) / med >= 500 or abs(v) / med <= 1 / 500):
                label = s["period_labels"][i] if i < len(s["period_labels"]) else f"value {i + 1}"
                ref = s["refs"][i] if i < len(s["refs"]) else None
                out.append(_f("high", f"'{s['label']}' changes by a factor of 500 or more in {label}",
                              f"{v:,.2f} against a typical {med:,.2f} for the same line. This often means one period is in different units (for example thousands against units) or a decimal point slipped.",
                              f"{sheet} › {ref}" if ref else sheet))
                break
    return out


def _sign_flip(rows: list[tuple[str, dict]]) -> list[Finding]:
    out = []
    for sheet, s in rows:
        vals = [v for v in s["values"] if isinstance(v, (int, float)) and v != 0]
        if len(vals) < 4:
            continue
        neg = sum(1 for v in vals if v < 0)
        if neg == 1 or neg == len(vals) - 1:
            odd = next(i for i, v in enumerate([x for x in s["values"]]) if isinstance(v, (int, float)) and v != 0 and ((v < 0) == (neg == 1)))
            label = s["period_labels"][odd] if odd < len(s["period_labels"]) else f"value {odd + 1}"
            out.append(_f("medium", f"'{s['label']}' has one value with the opposite sign in {label}",
                          "Every other period has the same sign. If this is a loss or a reversal, that is fine; if not, a sign may have been typed wrongly.", sheet))
    return out


def _constant(rows: list[tuple[str, dict]]) -> list[Finding]:
    out = []
    for sheet, s in rows:
        vals = [v for v in s["values"] if isinstance(v, (int, float))]
        if len(vals) >= 4 and len(set(vals)) == 1 and vals[0] != 0 and s["label"].strip().lower() not in {"year", "period", "index"}:
            out.append(_f("info", f"'{s['label']}' has the same figure in every period",
                          f"All {len(vals)} values are {vals[0]:,.2f}. That is right for a fixed charge but suspicious for revenue or profit (a copied row?).", sheet))
    return out


def _percent_over_100(rows: list[tuple[str, dict]]) -> list[Finding]:
    out = []
    for sheet, s in rows:
        label = s["label"].lower()
        if ("margin" in label or "%" in label or "percent" in label) and any(isinstance(v, (int, float)) and abs(v) > 100 for v in s["values"]):
            out.append(_f("medium", f"'{s['label']}' has a percentage above 100",
                          "A margin or percentage over 100 is unusual. Check whether it holds an amount, or a ratio shown as a whole number (for example 1.2 typed as 120).", sheet))
    return out


def _identities(statements: list[dict]) -> list[Finding]:
    """Subtotals that should add up. Only checked when every part is present for the period."""
    out = []
    for st in statements:
        by_key = {ln["key"]: ln["values"] for ln in st.get("lines", []) if ln.get("key")}
        periods = st.get("periods", [])

        def gap(parts: dict[str, int], total: str, label: str, tol: float = 0.01):
            if total not in by_key or any(k not in by_key for k in parts):
                return
            for i, p in enumerate(periods):
                vs = [by_key[k][i] for k in parts]
                t = by_key[total][i]
                if t is None or any(v is None for v in vs):
                    continue
                calc = sum(sign * v for sign, v in zip(parts.values(), vs))
                if abs(calc - t) > max(1.0, abs(t) * tol):
                    out.append(_f("high", f"{label} does not add up in {p}",
                                  f"The parts give {calc:,.2f} but the file shows {t:,.2f} (a difference of {abs(calc - t):,.2f}).", st.get("sheet")))
                    return

        # revenue - cost of goods sold = gross profit
        gap({"revenue": 1, "cogs": -1}, "gross_profit", "Gross profit (revenue minus cost of goods sold)")
        # operating + investing + financing = net change in cash
        gap({"operating_cash_flow": 1, "investing_cash_flow": 1, "financing_cash_flow": 1}, "net_change_in_cash", "Net change in cash")
        # total assets = total liabilities + total equity
        gap({"total_liabilities": 1, "total_equity": 1}, "total_assets", "The balance sheet (assets against liabilities plus equity)", tol=0.005)
    return out


ORDER = {"high": 0, "medium": 1, "info": 2}


def find_oddities(sheets: list[dict], statements: list[dict] | None = None) -> list[Finding]:
    rows = _row_series(sheets)
    found = (_duplicate_periods(sheets) + _identities(statements or []) + _unit_mix(rows) + _sign_flip(rows) + _percent_over_100(rows) + _constant(rows))
    seen, out = set(), []
    for f in sorted(found, key=lambda x: ORDER[x["severity"]]):
        if f["title"] in seen:
            continue
        seen.add(f["title"])
        out.append(f)
    return out[:20]
