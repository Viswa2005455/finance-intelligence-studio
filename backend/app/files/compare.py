"""Compare two uploads of the same kind of data (this quarter against last, this version against the draft).

Lines are matched by name. For each line found in both, the latest figure in the older file is set against the latest figure in the
newer file, and the lines are ranked by how much they moved. Lines that appear in only one file are listed, never guessed at."""

from __future__ import annotations

import re

MOVE = 10.0  # percent: a line that moves by more than this is called out


def _norm(label: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w% ]", " ", label.lower())).strip()


def _lines(analysis: dict) -> dict[str, dict]:
    """Row series by normalised label: the last value, its period and its source cell. The first sheet to name a line wins."""
    out: dict[str, dict] = {}
    for sh in analysis.get("sheets") or []:
        for s in sh.get("series") or []:
            if s.get("orientation") != "row" or not s.get("values"):
                continue
            key = _norm(s["label"])
            if key and key not in out:
                labels = s.get("period_labels") or []
                refs = s.get("refs") or []
                out[key] = {"label": s["label"].strip(), "value": s["values"][-1], "period": labels[-1] if labels else None, "ref": refs[-1] if refs else None, "sheet": sh.get("name")}
    return out


def compare(older: dict, newer: dict) -> dict:
    a, b = _lines(older), _lines(newer)
    rows = []
    for key in a.keys() & b.keys():
        old, new = a[key], b[key]
        change = new["value"] - old["value"]
        pct = None if old["value"] == 0 else change / abs(old["value"]) * 100
        rows.append({"label": new["label"], "older": old["value"], "older_period": old["period"], "older_ref": old["ref"],
                     "newer": new["value"], "newer_period": new["period"], "newer_ref": new["ref"], "change": change, "change_pct": pct, "moved": pct is not None and abs(pct) >= MOVE})
    rows.sort(key=lambda r: (r["change_pct"] is None, -abs(r["change_pct"] or 0), -abs(r["change"])))
    moved = [r for r in rows if r["moved"]]
    headline = (f"{len(rows)} lines appear in both files; {len(moved)} moved by {MOVE:.0f}% or more." if rows
                else "No line has the same name in both files, so there is nothing to compare line by line.")
    return {"rows": rows[:200], "only_in_older": sorted(a[k]["label"] for k in a.keys() - b.keys())[:20],
            "only_in_newer": sorted(b[k]["label"] for k in b.keys() - a.keys())[:20], "matched": len(rows), "moved": len(moved), "headline": headline,
            "note": "Each figure is the last value on its line in that file. Check that both files use the same currency, units and period length."}
