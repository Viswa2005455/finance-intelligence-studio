"""One Excel workbook holding everything a person has saved: an index sheet and one sheet per saved model.

Saved models are free-form JSON, so each sheet lists the model's values as path / value rows. Lists of numbers (a forecast, a
cash budget line) go across a row. Text that starts with a formula character is stored as text, never as a formula."""

from __future__ import annotations

import io
import re
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font

MAX_ROWS = 5000
MAX_COLS = 80


def _safe(v: Any) -> Any:
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + v
    return v


def _scalar(v: Any) -> bool:
    return v is None or isinstance(v, (str, int, float, bool))


def _rows(data: Any, path: str = "") -> list[list[Any]]:
    """Flatten JSON to rows: [path, value, value, ...]."""
    out: list[list[Any]] = []
    if isinstance(data, dict):
        for k, v in data.items():
            out += _rows(v, f"{path}.{k}" if path else str(k))
    elif isinstance(data, list):
        if all(_scalar(x) for x in data):
            out.append([path, *[_safe(x) for x in data[:MAX_COLS]]])
        else:
            for i, v in enumerate(data):
                out += _rows(v, f"{path}[{i + 1}]")
    else:
        out.append([path, _safe(data)])
    return out


def _title(kind: str, name: str, used: set[str]) -> str:
    base = re.sub(r"[\/*?:\[\]]", " ", f"{kind} {name}").strip()[:28] or "Saved"
    t, n = base, 2
    while t.lower() in used:
        t = f"{base[:26]} {n}"
        n += 1
    used.add(t.lower())
    return t


def build(items: list[dict]) -> bytes:
    """items: [{kind, name, version, updated_at, data}] -> .xlsx bytes."""
    wb = Workbook()
    idx = wb.active
    idx.title = "Index"
    idx.append(["Kind", "Name", "Version", "Last saved", "Sheet"])
    for c in idx[1]:
        c.font = Font(bold=True)
    used = {"index"}
    for it in items:
        title = _title(it["kind"], it["name"], used)
        idx.append([_safe(it["kind"]), _safe(it["name"]), it["version"], str(it["updated_at"])[:19], title])
        ws = wb.create_sheet(title)
        ws.append([_safe(it["name"]), f"{it['kind']}, version {it['version']}"])
        ws["A1"].font = Font(bold=True)
        ws.append([])
        for row in _rows(it["data"])[:MAX_ROWS]:
            ws.append(row)
        ws.column_dimensions["A"].width = 38
    idx.column_dimensions["A"].width = 16
    idx.column_dimensions["B"].width = 36
    idx.column_dimensions["E"].width = 30
    if not items:
        idx.append(["(nothing saved yet)"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
