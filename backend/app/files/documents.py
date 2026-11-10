"""PDF, Word, text, structured data, notebook and source-code extraction.

Uploaded content is treated as untrusted data: nothing here executes code. Python files are
parsed with `ast` (which does not run them), XML is parsed with defusedxml, YAML with
safe_load only.
"""

from __future__ import annotations

import ast
import io
import json
import re
import tomllib

import defusedxml.ElementTree as SafeET
import yaml

from .tabular import analyse_grid, decode_text, parse_number

MAX_PDF_PAGES = 60
MAX_TEXT_PREVIEW = 60_000

_CURRENCY_PAT = {
    "INR": r"₹|\bINR\b|\bRs\.?\s|\brupees?\b",
    "USD": r"\$|\bUSD\b|\bUS dollars?\b",
    "EUR": r"€|\bEUR\b|\beuros?\b",
    "GBP": r"£|\bGBP\b|\bpounds sterling\b",
    "JPY": r"¥|\bJPY\b|\byen\b",
}
_UNIT_PAT = {
    "thousands": r"\bin thousands\b|\b'000s?\b|\(000s?\)",
    "lakhs": r"\blakhs?\b|\blacs?\b",
    "crores": r"\bcrores?\b|\bcr\.?\b",
    "millions": r"\bin millions\b|\bmn\b|\(\s*m\s*\)",
    "billions": r"\bin billions\b|\bbn\b",
}
_PERIOD_PAT = r"\b(?:FY\s?\d{2,4}(?:-\d{2,4})?|Q[1-4]\s?(?:FY)?\s?\d{2,4}|(?:19|20)\d{2})\b"


def detect_financial_context(text: str) -> dict:
    """Detect currencies, units and periods mentioned in text. These are hints for the user to confirm."""
    currencies = {k: len(re.findall(p, text, re.I)) for k, p in _CURRENCY_PAT.items()}
    units = {k: len(re.findall(p, text, re.I)) for k, p in _UNIT_PAT.items()}
    periods = sorted({re.sub(r"\s+", " ", m) for m in re.findall(_PERIOD_PAT, text)})[:30]
    return {
        "currencies": {k: v for k, v in currencies.items() if v},
        "units": {k: v for k, v in units.items() if v},
        "periods": periods,
        "needs_confirmation": True,
    }


_MONTHS_ENDED = re.compile(r"\b(Three|Six|Nine|Twelve)\s+Months\s+Ended\b", re.I)
_DAY_TOKEN = re.compile(r"\b([A-Z][a-z]{2,8}\.?\s+\d{1,2}),")
_YEAR_LINE = re.compile(r"^\s*(?:(?:19|20)\d{2}\s*){1,8}$")
_DURATION_MONTHS = {"three": 3, "six": 6, "nine": 9, "twelve": 12}


def _pdf_column_periods(page_text: str) -> list[dict] | None:
    """Read the period headings printed above a statement table.

    US-style statements print the dates outside the table grid, e.g.
        Three Months Ended Twelve Months Ended
        September 26, September 27, September 26, September 27,
        2026 2025 2026 2025
    Returns one {"label", "months"} per value column, left to right, or None when the page does
    not use this layout (the caller then leaves the columns unlabelled rather than guessing).
    """
    lines = [ln.strip() for ln in page_text.splitlines()[:14]]
    for i, line in enumerate(lines):
        if not _YEAR_LINE.match(line) or i == 0:
            continue
        years = re.findall(r"(?:19|20)\d{2}", line)
        days = _DAY_TOKEN.findall(lines[i - 1])
        if len(days) != len(years):
            continue
        groups = [_DURATION_MONTHS[m.lower()] for m in _MONTHS_ENDED.findall(lines[i - 2] if i >= 2 else "")]
        if groups and len(years) % len(groups) == 0:
            per = len(years) // len(groups)
            months = [g for g in groups for _ in range(per)]
        elif not groups:
            months = [None] * len(years)
        else:
            return None
        # A full-year column and the balance sheet at the same date are the same fiscal period, so they
        # share one label and line up across statements; only shorter periods (quarters) are labelled as such.
        return [{"label": f"{m}M to {d}, {y}" if m and m < 12 else f"{d}, {y}", "months": m} for m, d, y in zip(months, days, years)]
    return None


def _lines_above_table(page, bbox, max_gap: float = 16.0) -> list[tuple[str, list[str]]]:
    """Statement lines printed just above the detected table edge (the first row is sometimes missed).

    Returns (label, figures) for lines whose trailing tokens are all numbers; headings and
    date lines have none and are skipped."""
    out = []
    for ln in page.extract_text_lines() or []:
        if not (bbox[1] - max_gap <= ln["top"] < bbox[1]):
            continue
        toks = ln["text"].split()
        figs: list[str] = []
        while toks and (toks[-1] == "$" or (not toks[-1].endswith(",") and parse_number(toks[-1])[0] is not None)):
            if toks[-1] != "$":
                figs.insert(0, toks[-1])
            toks.pop()
        label = " ".join(toks).strip().rstrip("$").strip()
        if figs and re.search(r"[A-Za-z]{3}", label):
            out.append((label, figs))
    return out


def _pdf_table_sheets(name: str, grid: list[list], page_text: str, page: int, table: int,
                      lead: list[tuple[str, list[str]]] | None = None) -> tuple[list[dict], str | None]:
    """Analyse one PDF table. With period headings found on the page, label the value columns and
    give each reporting length (3 months, 12 months) its own sheet so they are never mixed."""
    cols = _pdf_column_periods(page_text)
    value_cols = [c for c in range(1, max((len(r) for r in grid), default=0))
                  if any(parse_number(r[c] if c < len(r) else None)[0] is not None for r in grid)]
    if cols and len(cols) == len(value_cols):
        width = max(len(r) for r in grid)
        for label, figs in reversed(lead or []):  # recovered first rows, only when their figure count matches the columns
            if len(figs) == len(value_cols):
                row: list = [None] * width
                row[0] = label
                for vc, fig in zip(value_cols, figs):
                    row[vc] = fig
                grid = [row] + grid
    if not cols or len(cols) != len(value_cols):
        s = analyse_grid(name, grid, excel=False)
        s["source"] = {"page": page, "table": table}
        note = None
        if cols is not None:
            note = (f"Page {page}: found {len(cols)} period headings but {len(value_cols)} number columns, "
                    "so the columns were left unlabelled instead of guessed.")
        return [s], note
    out = []
    durations = sorted({c["months"] for c in cols if c["months"]}, reverse=True) or [None]
    for dur in durations:
        picked = [(c, vc) for c, vc in zip(cols, value_cols) if c["months"] == dur]
        body = [[(row[0] if row else None)] + [row[vc] if vc < len(row) else None for _, vc in picked] for row in grid]
        sheet_name = name if len(durations) == 1 else f"{name} · {dur} months"
        s = analyse_grid(sheet_name, [["Line item"] + [c["label"] for c, _ in picked]] + body, excel=False)
        s["source"] = {"page": page, "table": table, **({"months": dur} if dur else {})}
        out.append(s)
    return out, None


def parse_pdf(data: bytes) -> dict:
    import pdfplumber

    pages, sheets, warnings = [], [], []
    all_text = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        total = len(pdf.pages)
        if total > MAX_PDF_PAGES:
            warnings.append(f"Only the first {MAX_PDF_PAGES} of {total} pages were processed.")
        empty_pages = []
        for i, page in enumerate(pdf.pages[:MAX_PDF_PAGES]):
            text = page.extract_text() or ""
            all_text.append(text)
            if not text.strip():
                empty_pages.append(i + 1)
            tables = []
            for t_idx, found in enumerate(page.find_tables() or []):
                table = found.extract()
                if not table or len(table) < 2:
                    continue
                grid = [[(c.strip() if isinstance(c, str) else c) or None for c in row] for row in table]
                made, note = _pdf_table_sheets(f"Page {i + 1} · Table {t_idx + 1}", grid, text, i + 1, t_idx + 1,
                                           _lines_above_table(page, found.bbox))
                sheets.extend(made)
                if note:
                    warnings.append(note)
                tables.append(t_idx + 1)
            pages.append({"page": i + 1, "chars": len(text), "text": text[:4000], "tables": tables})
        if empty_pages:
            warnings.append(f"No extractable text on page(s) {', '.join(map(str, empty_pages[:20]))}. "
                            "They may be scanned images; OCR is not configured on this server.")
    joined = "\n".join(all_text)
    if sheets:
        warnings.append("Numbers extracted from PDF tables can be misaligned. Confirm figures against the source page before relying on them.")
    return {"kind": "document", "page_count": total, "pages": pages, "sheets": sheets,
            "text": joined[:MAX_TEXT_PREVIEW], "context": detect_financial_context(joined), "warnings": warnings}


def parse_docx(data: bytes) -> dict:
    import docx

    d = docx.Document(io.BytesIO(data))
    paragraphs = [p.text for p in d.paragraphs if p.text.strip()]
    sheets = []
    for t_idx, table in enumerate(d.tables):
        grid = [[(cell.text.strip() or None) for cell in row.cells] for row in table.rows]
        if len(grid) >= 2:
            s = analyse_grid(f"Table {t_idx + 1}", grid, excel=False)
            s["source"] = {"table": t_idx + 1}
            sheets.append(s)
    text = "\n".join(paragraphs)
    return {"kind": "document", "paragraph_count": len(paragraphs), "sheets": sheets,
            "text": text[:MAX_TEXT_PREVIEW], "context": detect_financial_context(text), "warnings": []}


def parse_text(data: bytes, label: str) -> dict:
    text, warn = decode_text(data)
    return {"kind": "document", "text": text[:MAX_TEXT_PREVIEW], "line_count": text.count("\n") + 1,
            "context": detect_financial_context(text), "warnings": [warn] if warn else [],
            "truncated": len(text) > MAX_TEXT_PREVIEW, "format": label}


def parse_structured(data: bytes, ext: str, label: str) -> dict:
    text, warn = decode_text(data)
    out = {"kind": "data", "format": label, "text": text[:MAX_TEXT_PREVIEW], "line_count": text.count("\n") + 1,
           "warnings": [warn] if warn else [], "valid": True, "error": None, "structure": None}
    try:
        if ext == ".json":
            obj = json.loads(text)
            out["structure"] = _describe(obj)
            if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj[:50]):
                keys = list(dict.fromkeys(k for x in obj[:5000] for k in x))[:200]
                grid = [keys] + [[x.get(k) if not isinstance(x.get(k), (dict, list)) else json.dumps(x.get(k)) for k in keys]
                                 for x in obj[:5000]]
                out["sheets"] = [analyse_grid("Records", grid, excel=False)]
        elif ext == ".xml":
            root = SafeET.fromstring(text.encode())
            out["structure"] = {"root": root.tag, "children": len(list(root))}
        elif ext in (".yml", ".yaml"):
            out["structure"] = _describe(yaml.safe_load(text))
        elif ext == ".toml":
            out["structure"] = _describe(tomllib.loads(text))
    except Exception as e:  # report syntax problems as data, not as a server error
        out["valid"] = False
        out["error"] = f"{type(e).__name__}: {str(e)[:300]}"
    return out


def _describe(obj) -> dict:
    if isinstance(obj, dict):
        return {"type": "object", "keys": list(obj)[:50], "key_count": len(obj)}
    if isinstance(obj, list):
        return {"type": "array", "length": len(obj), "item_type": type(obj[0]).__name__ if obj else None}
    return {"type": type(obj).__name__}


def parse_notebook(data: bytes) -> dict:
    text, _ = decode_text(data)
    try:
        nb = json.loads(text)
    except json.JSONDecodeError as e:
        return {"kind": "code", "language": "Jupyter notebook", "valid": False, "error": str(e), "text": text[:MAX_TEXT_PREVIEW], "warnings": []}
    cells = nb.get("cells", []) if isinstance(nb, dict) else []
    lang = (nb.get("metadata", {}).get("kernelspec", {}) or {}).get("language") or \
           (nb.get("metadata", {}).get("language_info", {}) or {}).get("name") or "python"
    out_cells, syntax_errors = [], []
    for i, c in enumerate(cells[:500]):
        src = "".join(c.get("source", [])) if isinstance(c.get("source"), list) else str(c.get("source", ""))
        out_cells.append({"index": i + 1, "type": c.get("cell_type"), "source": src[:5000],
                          "has_outputs": bool(c.get("outputs"))})
        if c.get("cell_type") == "code" and lang == "python":
            # strip IPython magics/shell lines before checking syntax
            cleaned = "\n".join("" if ln.lstrip().startswith(("%", "!")) else ln for ln in src.splitlines())
            try:
                ast.parse(cleaned)
            except SyntaxError as e:
                syntax_errors.append({"cell": i + 1, "line": e.lineno, "message": e.msg})
    counts = {t: sum(1 for c in cells if c.get("cell_type") == t) for t in ("code", "markdown", "raw")}
    return {"kind": "code", "language": f"Jupyter notebook ({lang})", "valid": True, "cells": out_cells,
            "cell_counts": counts, "syntax_errors": syntax_errors, "warnings": [],
            "note": "Notebook outputs were not executed or re-run."}


def _python_outline(src: str) -> dict:
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"syntax_ok": False, "syntax_errors": [{"line": e.lineno, "column": e.offset, "message": e.msg}]}
    imports, functions, classes = set(), [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "line": node.lineno})
    risky = sorted(imports & {"os", "subprocess", "socket", "shutil", "requests", "urllib", "ctypes", "pickle"})
    return {"syntax_ok": True, "syntax_errors": [], "imports": sorted(imports), "functions": functions[:200],
            "classes": classes[:100], "risky_imports": risky}


def _sql_outline(src: str) -> dict:
    no_comments = re.sub(r"--[^\n]*|/\*.*?\*/", "", src, flags=re.S)
    statements = [s for s in (x.strip() for x in no_comments.split(";")) if s]
    up = no_comments.upper()
    features = [name for name, pat in {
        "SELECT": r"\bSELECT\b", "JOIN": r"\bJOIN\b", "GROUP BY": r"\bGROUP\s+BY\b", "CTE (WITH)": r"^\s*WITH\b|\bWITH\s+\w+\s+AS\s*\(",
        "Subquery": r"\(\s*SELECT\b", "Window function": r"\bOVER\s*\(", "INSERT/UPDATE/DELETE": r"\b(INSERT|UPDATE|DELETE)\b",
        "DDL (CREATE/ALTER/DROP)": r"\b(CREATE|ALTER|DROP)\b"}.items() if re.search(pat, up, re.M)]
    tables = sorted(set(re.findall(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+([A-Za-z_][\w.]*)", no_comments, re.I)))[:100]
    issues = []
    if no_comments.count("(") != no_comments.count(")"):
        issues.append("Unbalanced parentheses.")
    if no_comments.count("'") % 2:
        issues.append("Unclosed string literal (odd number of single quotes).")
    if re.search(r"\bSELECT\s+\*", up):
        issues.append("SELECT * used; list columns explicitly for stable results.")
    if re.search(r"\b(UPDATE|DELETE)\b(?![^;]*\bWHERE\b)", up):
        issues.append("UPDATE/DELETE without WHERE affects every row.")
    return {"statement_count": len(statements), "features": features, "tables": tables, "issues": issues}


def _java_outline(src: str) -> dict:
    classes = re.findall(r"\b(?:class|interface|enum|record)\s+([A-Z]\w*)", src)
    methods = re.findall(r"(?:public|private|protected|static|\s)+[\w<>\[\],\s]+\s+(\w+)\s*\([^)]*\)\s*(?:throws [\w.,\s]+)?\{", src)
    issues = []
    if src.count("{") != src.count("}"):
        issues.append("Unbalanced braces.")
    return {"classes": classes[:100], "methods": [m for m in methods if m not in ("if", "for", "while", "switch", "catch")][:200],
            "has_main": bool(re.search(r"static\s+void\s+main\s*\(", src)), "issues": issues}


def parse_code(data: bytes, ext: str, label: str) -> dict:
    text, warn = decode_text(data)
    out = {"kind": "code", "language": label, "extension": ext, "text": text[:MAX_TEXT_PREVIEW],
           "line_count": text.count("\n") + 1, "warnings": [warn] if warn else [],
           "note": "Code is never executed on upload. Execution requires explicit approval in the Data & Code Lab."}
    if ext == ".py":
        out["outline"] = _python_outline(text)
    elif ext == ".sql":
        out["outline"] = _sql_outline(text)
    elif ext == ".java":
        out["outline"] = _java_outline(text)
    return out
