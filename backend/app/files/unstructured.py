"""Find tables and numbers in files that are not neat spreadsheets: running text, logs, Markdown, HTML, RTF,
and JSON / YAML / TOML / XML data.

Every extractor returns the same sheet shape as the spreadsheet parser (via analyse_grid), so the rest of the
app (statement matching, ratios, forecasting, the "Data found in this file" panel) works on them unchanged.
Nothing is guessed silently: numbers found in sentences are listed with the line they came from, and anything
that looks like a date, time or year is left out rather than read as an amount.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from typing import Any

from .routing import _PERIODISH, _period_year, match_item
from .tabular import MAX_COLS, MAX_ROWS, analyse_grid, parse_number

# ----------------------------------------------------------------------------------------------- text numbers
_CONNECT = {
    "was", "is", "were", "are", "be", "of", "to", "at", "for", "in", "on", "by", "from", "rose", "fell", "grew", "stood", "reached", "up", "down",
    "about", "around", "approximately", "approx", "increased", "decreased", "totalled", "totaled", "amounted", "and", "the", "a", "an", "with",
    "rs", "inr", "usd", "eur", "gbp", "lakh", "lakhs", "lac", "lacs", "crore", "crores", "cr", "million", "millions", "mn", "billion", "bn",
    "thousand", "k", "fy", "q", "h", "year", "quarter", "it", "its", "this", "that", "which", "has", "had", "have", "reported", "recorded",
    "came", "closed", "ended", "totalling", "totaling",
}
_DATES = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?)?|\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}[/.]\d{1,2}[/.]\d{2,4}|\bFY\s?\d{2,4}(?:-\d{2,4})?\b|\bQ[1-4]\b")
_MENTION = re.compile(r"(?<![\w.,])(?:[₹$€£]\s?|Rs\.?\s?|INR\s?|USD\s?)?\(?-?\d[\d,]*(?:\.\d+)?\)?%?(?![\w])")
_KEY_EQ = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*$")  # amount=1500.50: the single word before "="
_KEY_COLON = re.compile(r"((?:[A-Za-z_][\w\-]*\s){0,2}[A-Za-z_][\w\-]*)\s*:\s*$")  # Total sales: 1,200: up to three words before ":"


_DATES_ONLY = re.compile(r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?)?|\d{1,2}:\d{2}(?::\d{2})?|\d{1,2}[/.]\d{1,2}[/.]\d{2,4}")


def _mask(line: str) -> str:
    """Blank out dates, times and period names so their digits are never read as amounts (positions are kept)."""
    return _DATES.sub(lambda m: " " * len(m.group(0)), line)


def _clean_token(tok: str) -> str:
    t = tok.strip()
    if t.startswith("(") != t.rstrip("%").endswith(")"):  # a stray bracket from "(from 1,150)"
        t = t.replace("(", "").replace(")", "")
    return t


def _period_for(raw: str, start: int, end: int) -> str | None:
    """The reporting period named in the same clause as a number: the nearest FY25 / Q1 FY25 / 2025 / Mar 2025
    between the commas or semicolons around it. None when the clause names no period (it is never guessed)."""
    left = max((i for i in (raw.rfind(",", 0, start), raw.rfind(";", 0, start)) if i >= 0), default=-1) + 1
    cands = [i for i in (raw.find(",", end), raw.find(";", end)) if i >= 0]
    right = min(cands) if cands else len(raw)
    best, gap = None, 10**9
    for pm in _PERIODISH.finditer(raw, left, right):
        d = 0 if pm.start() <= start < pm.end() else min(abs(pm.start() - end), abs(start - pm.end()))
        if d < gap:
            best, gap = pm, d
    return re.sub(r"\s+", " ", best.group(0)).strip() if best else None


def number_mentions(text: str) -> list[dict]:
    """Numbers named in running text ("Revenue was Rs 12,480 lakh") and in key=value pairs (amount=1500.50).

    A number is kept only when something names it: a known statement item (revenue, net profit, ...) just before
    it, or "name=" / "name:" in front of it. Each value keeps the line it came from. Values whose own clause
    names a period (FY25, Q1 FY25, 2025) go into a period-by-period sheet that the statement and ratio engines can
    use; the rest are listed in order of appearance."""
    rows: dict[str, dict] = {}
    for ln, raw in enumerate(text.splitlines()[:MAX_ROWS], 1):
        if len(raw) > 2000 or raw.count("|") >= 2:
            continue
        line = _mask(raw)
        for m in _MENTION.finditer(line):
            tok = _clean_token(m.group(0))
            value, _ = parse_number(tok)
            if value is None:
                continue
            plain = tok.replace(",", "").strip("()%")
            has_currency = bool(re.match(r"[₹$€£]|Rs|INR|USD", tok))
            if re.fullmatch(r"(?:19|20)\d{2}", plain) and "," not in tok and not has_currency:
                continue  # a bare year
            words = re.findall(r"[A-Za-z&']+", line[:m.start()])
            while words and words[-1].lower() in _CONNECT:
                words.pop()
            label = next((" ".join(words[-n:]) for n in range(min(6, len(words)), 0, -1) if match_item(" ".join(words[-n:]))), None)
            if label is None:
                kv = _KEY_EQ.search(line[:m.start()]) or _KEY_COLON.search(line[:m.start()])
                label = kv.group(1).strip().replace("_", " ") if kv else None
            if not label:
                continue
            row = rows.setdefault(label.lower(), {"label": label[:1].upper() + label[1:], "values": []})
            if len(row["values"]) < MAX_COLS - 1:
                row["values"].append((value, ln, _period_for(_DATES_ONLY.sub(lambda d: " " * len(d.group(0)), raw), m.start(), m.end())))
    if not rows:
        return []

    sheets: list[dict] = []
    placed: dict[str, dict[str, tuple[float, int]]] = {}
    loose: dict[str, dict] = {}
    for key, row in rows.items():
        for value, ln, period in row["values"]:
            if period and period not in placed.setdefault(key, {}):
                placed[key][period] = (value, ln)
            else:
                loose.setdefault(key, {"label": row["label"], "values": []})["values"].append((value, ln))
    placed = {k: v for k, v in placed.items() if v}

    if placed:
        periods = sorted({p for v in placed.values() for p in v}, key=lambda p: (_period_year(p) or 0, p))
        grid: list[list[Any]] = [["Item"] + periods]
        where: dict[tuple[int, int], int] = {}
        for r_i, (key, by_p) in enumerate(placed.items(), start=1):
            grid.append([rows[key]["label"]] + [by_p[p][0] if p in by_p else None for p in periods])
            for c_i, p in enumerate(periods, start=1):
                if p in by_p:
                    where[(r_i, c_i)] = by_p[p][1]
        sheet = analyse_grid("Numbers found in text (by period)", grid, excel=False)
        for s in sheet["series"]:
            s["refs"] = [_line_ref(ref, where) for ref in s["refs"]]
        sheet["source"] = {"kind": "text numbers"}
        sheet["warnings"].append("These numbers were picked out of sentences. Each was assigned to the period named in the same part of the sentence "
                                 "(between commas), and shows the line it came from. Check each one against the text.")
        sheets.append(sheet)

    if loose:
        width = max(len(r["values"]) for r in loose.values())
        grid = [["Item"] + [f"Mention {i}" for i in range(1, width + 1)]]
        where = {}
        for r_i, row in enumerate(loose.values(), start=1):
            grid.append([row["label"]] + [v for v, _ in row["values"]])
            for c_i, (_, ln) in enumerate(row["values"], start=1):
                where[(r_i, c_i)] = ln
        sheet = analyse_grid("Numbers found in text", grid, excel=False)
        for s in sheet["series"]:
            s["refs"] = [_line_ref(ref, where) for ref in s["refs"]]
        sheet["source"] = {"kind": "text numbers"}
        sheet["warnings"].append("These numbers were picked out of sentences and lines of text, and no period was named next to them. Each shows the line it "
                                 "came from; when one name appears twice in a sentence (for example a current and a previous figure) the order is the order "
                                 "written, not necessarily oldest first. Check them against the text.")
        sheets.append(sheet)
    return sheets


def _line_ref(ref: str, where: dict[tuple[int, int], int]) -> str:
    m = re.match(r"row (\d+), col (\d+)", ref)
    if not m:
        return ref
    ln = where.get((int(m.group(1)) - 1, int(m.group(2)) - 1))
    return f"line {ln}" if ln else ref


# ----------------------------------------------------------------------------------------------- Markdown and HTML tables
_MD_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?\s*$")


def _md_cells(line: str) -> list[Any]:
    return [c.strip() or None for c in line.strip().strip("|").split("|")]


def markdown_tables(text: str) -> list[list[list[Any]]]:
    lines = text.splitlines()
    grids, i = [], 0
    while i < len(lines):
        if lines[i].count("|") >= 1 and i + 1 < len(lines) and _MD_SEP.match(lines[i + 1]) and "-" in lines[i + 1]:
            grid, j = [_md_cells(lines[i])], i + 2
            while j < len(lines) and lines[j].strip() and "|" in lines[j] and len(grid) < MAX_ROWS:
                grid.append(_md_cells(lines[j]))
                j += 1
            grids.append(grid)
            i = j
        else:
            i += 1
    return grids


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[Any]]] = []
        self.text: list[str] = []
        self._depth = 0
        self._row: list[Any] | None = None
        self._cell: list[str] | None = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag == "table":
            self._depth += 1
            if self._depth == 1:
                self.tables.append([])
        elif self._depth == 1 and tag == "tr":
            self._row = []
        elif self._depth == 1 and tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag in ("br", "p", "div", "li", "h1", "h2", "h3", "h4"):
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        elif tag == "table":
            self._depth = max(0, self._depth - 1)
        elif self._depth == 1 and tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()) or None)
            self._cell = None
        elif self._depth == 1 and tag == "tr" and self._row is not None:
            if any(c is not None for c in self._row):
                self.tables[-1].append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._cell is not None:
            self._cell.append(data)
        self.text.append(data)


def html_tables(html: str) -> tuple[list[list[list[Any]]], str]:
    p = _TableParser()
    p.feed(html[:2_000_000])
    p.close()
    text = re.sub(r"\n\s*\n+", "\n", "".join(p.text)).strip()
    return [t for t in p.tables if len(t) >= 2], text


def sheets_from_grids(grids: list[list[list[Any]]], label: str) -> list[dict]:
    out = []
    for i, g in enumerate(grids[:20], 1):
        s = analyse_grid(f"{label} {i}", [r[:MAX_COLS] for r in g[:MAX_ROWS]], excel=False)
        s["source"] = {"table": i}
        out.append(s)
    return out


def strip_rtf(raw: str) -> str:
    s = re.sub(r"\\par[d]?\b", "\n", raw)
    s = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: bytes.fromhex(m.group(1)).decode("cp1252", "replace"), s)
    s = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", s)
    s = s.replace("\\{", "\x01").replace("\\}", "\x02").replace("\\\\", "\\")
    s = re.sub(r"[{}]", "", s)
    return s.replace("\x01", "{").replace("\x02", "}")


# ----------------------------------------------------------------------------------------------- JSON / YAML / TOML / XML
_PERIOD_KEYS = {"year", "yr", "period", "fy", "fiscal_year", "fiscal year", "date", "month", "quarter", "time"}


def _is_num(v: Any) -> bool:
    return not isinstance(v, bool) and parse_number(v)[0] is not None


def _scalar(v: Any) -> Any:
    return json.dumps(v, default=str)[:200] if isinstance(v, (dict, list)) else v


def _flatten(d: dict, prefix: str = "", depth: int = 0) -> dict:
    out: dict = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and depth < 2:
            out.update(_flatten(v, key + ".", depth + 1))
        else:
            out[key] = _scalar(v)
    return out


def _periodic(keys: list[str], rows: list[dict]) -> list[list[Any]] | None:
    """Records that are one-per-period ({"year": 2024, "revenue": ...}) read better as items down, periods across."""
    if not 2 <= len(rows) <= 60:
        return None
    pk = next((k for k in keys if k.lower() in _PERIOD_KEYS), None)
    if pk is None:
        pk = next((k for k in keys if all(_is_num(r.get(k)) and 1990 <= (parse_number(r.get(k))[0] or 0) <= 2100 for r in rows)), None)
    if pk is None:
        return None
    numeric = [k for k in keys if k != pk and sum(_is_num(r.get(k)) for r in rows) >= max(2, len(rows) // 2)]
    if not numeric:
        return None
    return [["Item"] + [str(r.get(pk)) for r in rows]] + [[k] + [r.get(k) for r in rows] for k in numeric]


def _records_grid(rows: list[dict]) -> list[list[Any]]:
    flat = [_flatten(r) for r in rows[:MAX_ROWS]]
    keys = list(dict.fromkeys(k for r in flat for k in r))[:MAX_COLS]
    return _periodic(keys, flat) or [keys] + [[r.get(k) for k in keys] for r in flat]


def _walk(obj: Any, path: str, depth: int, found: list[tuple[str, str, Any]]) -> None:
    if depth > 4 or len(found) >= 12:
        return
    if isinstance(obj, list):
        if len(obj) >= 2 and all(isinstance(x, dict) for x in obj[:50]):
            found.append(("records", path or "Records", obj))
        elif len(obj) >= 2 and all(_is_num(x) for x in obj[:200]):
            found.append(("series", path or "Values", obj))
        else:
            for i, x in enumerate(obj[:5]):
                _walk(x, f"{path}[{i}]", depth + 1, found)
    elif isinstance(obj, dict):
        wide = {k: v for k, v in obj.items() if isinstance(v, dict) and v and all(_is_num(x) for x in v.values())}
        if wide and (len(wide) >= 2 or max(len(v) for v in wide.values()) >= 2):
            found.append(("wide", path or "Items by period", wide))
        series = {k: v for k, v in obj.items() if isinstance(v, list) and len(v) >= 2 and all(_is_num(x) for x in v)}
        if series:
            found.append(("lists", path or "Series", series))
        scalars = {k: v for k, v in obj.items() if _is_num(v)}
        if len(scalars) >= 2 and not wide and not series:
            label = next((v for v in obj.values() if isinstance(v, str) and not _is_num(v)), None)
            found.append(("record", path or "Values", (label, scalars)))
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                _walk(v, f"{path}.{k}" if path else str(k), depth + 1, found)


def structured_sheets(obj: Any) -> list[dict]:
    """Sheets for every table-like part of parsed JSON/YAML/TOML/XML data: lists of records, label -> {period: value}
    maps, label -> [values] maps, and objects holding several numbers. At most six are kept."""
    found: list[tuple[str, str, Any]] = []
    _walk(obj, "", 0, found)
    sheets, seen = [], set()
    for kind, name, val in found:
        if kind == "records":
            grid = _records_grid(val)
        elif kind == "wide":
            periods = list(dict.fromkeys(str(p) for v in val.values() for p in v))
            grid = [["Item"] + periods] + [[k] + [next((x for p, x in v.items() if str(p) == per), None) for per in periods] for k, v in val.items()]
        elif kind == "lists":
            n = max(len(v) for v in val.values())
            grid = [["Item"] + [f"Value {i}" for i in range(1, n + 1)]] + [[k] + list(v) for k, v in val.items()]
        elif kind == "series":
            grid = [["Index", "Value"]] + [[i + 1, x] for i, x in enumerate(val[:MAX_ROWS])]
        else:  # record: one object with several numbers
            label, nums = val
            grid = [["Item", "Value"]] + [[k, v] for k, v in nums.items()] if label is None else \
                [["Name"] + list(nums)] + [[label] + list(nums.values())]
        key = json.dumps(grid, default=str)[:400]
        if len(grid) < 2 or key in seen:
            continue
        seen.add(key)
        s = analyse_grid(name.split(".")[-1] or name, grid, excel=False)
        s["source"] = {"path": name}
        sheets.append(s)
        if len(sheets) >= 6:
            break
    return sheets


def xml_to_obj(el: Any) -> Any:
    d: dict[str, Any] = {f"@{k}": v for k, v in el.attrib.items()}
    kids = list(el)
    text = (el.text or "").strip()
    if not kids and not d:
        return text
    for ch in kids:
        v = xml_to_obj(ch)
        if ch.tag in d:
            if not isinstance(d[ch.tag], list):  # a second element with the same tag makes a list (xml_to_obj never returns a list itself)
                d[ch.tag] = [d[ch.tag]]
            d[ch.tag].append(v)
        else:
            d[ch.tag] = v
    if text and not kids:
        d["#text"] = text
    return d
