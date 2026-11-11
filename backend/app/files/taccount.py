"""Import a two-sided ("T-format") Trading and Profit & Loss account, as kept by many Indian firms.

The layout is a debit side on the left (lines starting "To") and a credit side on the right (lines
starting "By"), each with its own Amount column, for one year only:

    PARTICULARS            Amount     PARTICULARS            Amount
    To  Opening Stock                 By  Sales
        GOLD               5,690,908      GOLD               4,098,516
        SILVER             1,225,062      SILVER             1,366,172
    To  Purchases        ...          By  Closing Stock      ...
    To  Gross Profit         929,165
                          14,225,833                         14,225,833      <- the sheet's own total
    To  Rent                 52,800   By  Gross Profit         929,165
    ...
    To  Net profit           497,669

Lines are found by their words and position, not by fixed cells, and every value keeps its source
cell. Derived lines are always labelled, and a derived line is dropped when it does not reconcile
with the figures the file itself reports. Nothing is guessed: a line that cannot be read produces no
standard item. The result has the same shape as the Screener import, so the same screens use it.
"""

from __future__ import annotations

import datetime as dt
import io
import re
from typing import Any

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

MAX_ROWS = 400
MAX_COLS = 30
TOLERANCE = 1.0  # rupees: rounding in a hand-kept account

_AMOUNT_HEADER = re.compile(r"^\s*(amount|amt|rs\.?|₹)\s*$", re.I)
_PREFIX = re.compile(r"^\s*(to|by)\s*$", re.I)
_PREFIXED = re.compile(r"^\s*(to|by)\s+(.+)$", re.I)
_MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                         "september", "october", "november", "december"], 1)}


class NotTAccount(ValueError):
    pass


def _s(v: Any) -> str | None:
    if isinstance(v, str) and v.strip():
        return re.sub(r"\s+", " ", v).strip()
    return None


def _num(v: Any) -> float | None:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = v.replace(",", "").strip()
        try:
            return float(t) if t else None
        except ValueError:
            return None
    return None


def _norm(label: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w&' ]", " ", label.lower())).strip()


def find_layout(grid: list[list[Any]]) -> dict | None:
    """Return the column layout of a two-sided account, or None when the sheet is not one.

    A header row with two "Amount" cells marks the two sides; below it, lines starting "To" and "By"
    confirm it. Both must be present, so an ordinary table with an "Amount" column is not mistaken."""
    for r in range(min(len(grid), 40)):
        amt = [c for c, v in enumerate(grid[r]) if isinstance(v, str) and _AMOUNT_HEADER.match(v)]
        if len(amt) < 2:
            continue
        left_amt, right_amt = amt[0], amt[1]
        to_by = {"to": 0, "by": 0}
        for row in grid[r + 1:r + 120]:
            for v in row[:right_amt]:
                s = _s(v)
                if not s:
                    continue
                m = _PREFIX.match(s) or _PREFIXED.match(s)
                if m:
                    to_by[m.group(1).lower()] += 1
        if to_by["to"] >= 2 and to_by["by"] >= 2:
            return {"header_row": r, "left_amount": left_amt, "right_amount": right_amt,
                    "left_labels": list(range(0, left_amt)), "right_labels": list(range(left_amt + 1, right_amt))}
    return None


def _period_of(grid: list[list[Any]]) -> str | None:
    for row in grid[:12]:
        for v in row:
            s = _s(v)
            if not s or not re.search(r"year ended|period ended|for the year|as on|as at", s, re.I):
                continue
            m = re.search(r"(\d{1,2})\s*[/.\-]\s*(\d{1,2})\s*[/.\-]\s*((?:19|20)\d{2})", s)
            if m:
                try:
                    return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).strftime("%b %Y")
                except ValueError:
                    pass
            m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)\s+((?:19|20)\d{2})", s, re.I)
            if m and m.group(2).lower() in _MONTHS:
                return f"{m.group(2)[:3].title()} {m.group(3)}"
    return None


def _company_of(grid: list[list[Any]]) -> str | None:
    for row in grid[:6]:
        for v in row[:4]:
            s = _s(v)
            if s and not re.search(r"account|a/c|profit|loss|trading", s, re.I):
                return s
    return None


_NEW_BLOCK = re.compile(r"balance sheet|trading and profit|profit (&|and) loss|a/c for the|account for the|\bas (on|at)\b|year ended", re.I)


def _end_row(grid, layout) -> int:
    """First row (0-based) after the first account: a second total line closes a trading + profit & loss
    account, and a new title (for example a balance sheet) closes a profit & loss account on its own."""
    la, ra = layout["left_amount"], layout["right_amount"]
    totals = 0
    for r in range(layout["header_row"] + 1, len(grid)):
        row = grid[r]
        labelled = any(_s(row[c]) and not _PREFIX.match(_s(row[c]) or "") for c in layout["left_labels"] + layout["right_labels"] if c < len(row))
        if not labelled and la < len(row) and ra < len(row) and _num(row[la]) is not None and _num(row[ra]) is not None:
            totals += 1
            if totals >= 2:
                return r + 1
            continue
        if totals >= 1 and any(isinstance(v, str) and _NEW_BLOCK.search(v) for v in row[:ra + 1]):
            return r
    return len(grid)


def _read_side(grid, layout, side: str, end: int | None = None) -> list[dict]:
    """Items of one side, in order, each tagged with its section (0 = trading, 1 = profit & loss)."""
    amt = layout["left_amount"] if side == "left" else layout["right_amount"]
    label_cols = layout["left_labels"] if side == "left" else layout["right_labels"]
    items: list[dict] = []
    current: dict | None = None
    section = 0
    for r in range(layout["header_row"] + 1, end if end is not None else len(grid)):
        row = grid[r]
        texts: list[str] = []
        prefix = False
        for c in label_cols:
            if c >= len(row):
                continue
            s = _s(row[c])
            if not s:
                continue
            if _PREFIX.match(s):
                prefix = True
                continue
            m = _PREFIXED.match(s)
            if m:
                prefix = True
                s = m.group(2).strip()
            texts.append(s)
        label = " ".join(texts) if texts else None
        value = _num(row[amt]) if amt < len(row) else None
        other_amt = layout["right_amount"] if side == "left" else layout["left_amount"]
        other_value = _num(row[other_amt]) if other_amt < len(row) else None
        ref = f"{get_column_letter(amt + 1)}{r + 1}"
        if label is None and value is not None:
            if other_value is not None:  # a line with a total on both sides closes a section
                section += 1
            current = None
            continue
        if label is None:
            continue
        if prefix:
            current = {"label": label, "value": value, "ref": ref if value is not None else None, "children": [], "section": section, "row": r + 1}
            items.append(current)
        elif value is not None and current is not None and current["value"] is None:
            current["children"].append({"label": label, "value": value, "ref": ref})
        elif value is not None:
            current = {"label": label, "value": value, "ref": ref, "children": [], "section": section, "row": r + 1}
            items.append(current)
    return items


def _amount(item: dict) -> tuple[float | None, str | None, bool]:
    """(amount, source cells, summed-from-children)."""
    if item["value"] is not None:
        return item["value"], item["ref"], False
    kids = item["children"]
    if kids:
        return sum(k["value"] for k in kids), " + ".join(k["ref"] for k in kids), True
    return None, None, False


def _is(label: str, *pats: str) -> bool:
    n = _norm(label)
    return any(re.match(p, n) for p in pats)


# ---- the balance sheet that often follows the account: LIABILITIES on the left, ASSETS on the right, with
# group headings (FIXED ASSETS, CURRENT ASSETS, Current Liabilities) instead of "To" / "By".

def _find_bs_layout(grid, start: int) -> dict | None:
    for r in range(start, min(len(grid), start + 60)):
        row = grid[r]
        amt = [c for c, v in enumerate(row) if isinstance(v, str) and _AMOUNT_HEADER.match(v)]
        if len(amt) < 2:
            continue
        left = " ".join(filter(None, (_s(row[c]) for c in range(amt[0]) if c < len(row)))).lower()
        right = " ".join(filter(None, (_s(row[c]) for c in range(amt[0] + 1, amt[1]) if c < len(row)))).lower()
        if "liabilit" in left and "asset" in right:
            return {"header_row": r, "left_amount": amt[0], "right_amount": amt[1],
                    "left_labels": list(range(0, amt[0])), "right_labels": list(range(amt[0] + 1, amt[1]))}
    return None


def _bs_end(grid, lay) -> tuple[int, float, float, str, str] | None:
    """The line with a total on both sides: (row, left total, right total, left cell, right cell)."""
    la, ra = lay["left_amount"], lay["right_amount"]
    for r in range(lay["header_row"] + 1, len(grid)):
        row = grid[r]
        has_label = any(_s(row[c]) for c in lay["left_labels"] + lay["right_labels"] if c < len(row))
        lv, rv = (_num(row[la]) if la < len(row) else None), (_num(row[ra]) if ra < len(row) else None)
        if not has_label and lv is not None and rv is not None:
            return r, lv, rv, f"{get_column_letter(la + 1)}{r + 1}", f"{get_column_letter(ra + 1)}{r + 1}"
    return None


def _read_bs_side(grid, lay, side: str, end: int) -> list[dict]:
    amt = lay["left_amount"] if side == "left" else lay["right_amount"]
    cols = lay["left_labels"] if side == "left" else lay["right_labels"]
    items: list[dict] = []
    group: str | None = None
    headed = False
    for r in range(lay["header_row"] + 1, end):
        row = grid[r]
        texts = [t for t in (_s(row[c]) for c in cols if c < len(row)) if t]
        if not texts:
            continue
        label = " ".join(texts)
        clean = label.rstrip(":").strip()
        value = _num(row[amt]) if amt < len(row) else None
        if value is None:  # a heading such as FIXED ASSETS or "Current Liabilities :"
            group, headed = clean, True
            continue
        heading_like = label.endswith(":")  # "Unsecured Loan:" with its amount on the same line
        items.append({"label": clean, "value": value, "ref": f"{get_column_letter(amt + 1)}{r + 1}",
                      "group": None if heading_like else group, "before_heading": not headed})
        if heading_like:
            group, headed = None, True
    return items


def _add_balance_sheet(grid, title: str, start: int, pl_period: str | None, add, keyed, notes: list[str]) -> int | None:
    """Add the balance sheet lines; returns the row (0-based) of its totals line, or None when none was imported."""
    lay = _find_bs_layout(grid, start)
    if lay is None:
        return None
    tot = _bs_end(grid, lay)
    if tot is None:
        return None
    end, lt, rt, lref, rref = tot
    left, right = _read_bs_side(grid, lay, "left", end), _read_bs_side(grid, lay, "right", end)
    bs_period = _period_of(grid[max(0, lay["header_row"] - 8):lay["header_row"] + 1])
    if abs(sum(i["value"] for i in left) - lt) > TOLERANCE or abs(sum(i["value"] for i in right) - rt) > TOLERANCE or abs(lt - rt) > TOLERANCE:
        notes.append("A balance sheet was found, but its lines do not add up to the totals shown in the file, so it was not imported. "
                     "Please check the balance sheet in the file.")
        return None
    if bs_period and pl_period and bs_period != pl_period:
        notes.append(f"The balance sheet is dated {bs_period} but the account is for {pl_period}, so the balance sheet was not imported.")
        return None

    def names(items: list[dict]) -> str:
        return " + ".join(re.sub(r"[()]", "", i["label"]) for i in items)

    def total(items: list[dict]) -> float:
        return sum(i["value"] for i in items)

    def put(label: str, key: str | None, value: float, source: str, kind: str = "reported"):
        add(label, key, value, source, kind, "balance")

    cash = [i for i in right if _is(i["label"], r"^cash\b", r"^bank\b", r"^balances? with banks?", r"^cash (on|in) hand", r"^cash at bank")]
    stock = [i for i in right if _is(i["label"], r"^(closing )?stock\b", r"^inventor(y|ies)\b")]
    debtors = [i for i in right if _is(i["label"], r"^(sundry |trade )?debtors\b", r"^(trade )?receivables?\b") and not _is(i["label"], r".*\b(gst|tds|tax)\b")]
    creditors = [i for i in left if _is(i["label"], r"^(sundry |trade )?creditors\b", r"^(trade )?payables?\b", r"^accounts payable")]
    debt = [i for i in left if re.search(r"loan|borrowing|overdraft|cash credit|debenture", i["label"], re.I)]
    fixed = [i for i in right if i["group"] and re.search(r"fixed assets", i["group"], re.I)]
    current_a = [i for i in right if i["group"] and re.search(r"current assets", i["group"], re.I)]
    current_l = [i for i in left if i["group"] and re.search(r"current liabilit", i["group"], re.I)]
    headed_left = any(not i["before_heading"] for i in left)
    equity = [i for i in left if i["before_heading"]] if headed_left else [i for i in left if re.search(r"capital|reserve|surplus|proprietor|partner", i["label"], re.I)]

    single = {id(i): k for lst, k in ((stock, "inventory"), (debtors, "receivables"), (creditors, "accounts_payable"), (cash, "cash")) for i in lst if len(lst) == 1}
    for item in right + left:
        put(item["label"], keyed(single.get(id(item))), item["value"], f"{title}!{item['ref']}")
    if len(cash) > 1:
        put(f"Cash and bank (derived: {names(cash)})", keyed("cash"), total(cash), "derived", "derived")
    if len(stock) > 1:
        put(f"Inventory (derived: {names(stock)})", keyed("inventory"), total(stock), "derived", "derived")
    if len(debtors) > 1:
        put(f"Receivables (derived: {names(debtors)})", keyed("receivables"), total(debtors), "derived", "derived")
    if fixed:
        put(f"Fixed assets (derived: the lines under {re.sub(r'[()]', '', fixed[0]['group'])})", keyed("ppe"), total(fixed), "derived", "derived")
    if current_a:
        put(f"Current assets (derived: the lines under {re.sub(r'[()]', '', current_a[0]['group'])})", keyed("current_assets"), total(current_a), "derived", "derived")
    put("Total assets", keyed("total_assets"), rt, f"{title}!{rref}")
    if equity:
        put(f"Total equity (derived: {names(equity)})", keyed("total_equity"), total(equity), "derived", "derived")
        put("Total liabilities (derived: total of the liabilities side less the owner's funds above)", keyed("total_liabilities"), lt - total(equity), "derived", "derived")
    if current_l:
        put(f"Current liabilities (derived: the lines under {re.sub(r'[()]', '', current_l[0]['group'])})", keyed("current_liabilities"), total(current_l), "derived", "derived")
    if debt:
        put(f"Total debt (derived: {names(debt)})", keyed("total_debt"), total(debt), "derived", "derived")
    notes.append("The balance sheet was read as written: assets and liabilities are grouped exactly as the file groups them (FIXED ASSETS, "
                 "CURRENT ASSETS, Current Liabilities). Owner's funds are the lines above the first heading on the liabilities side. "
                 "Loans are not counted as current liabilities unless the file lists them under that heading.")
    return end


def parse_taccount(data: bytes, sheet: str | None = None) -> dict:
    wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        found: list[tuple[str, list[list[Any]], dict]] = []
        for ws in wb.worksheets:
            if ws.sheet_state != "visible":
                continue
            grid = [list(r) for r in ws.iter_rows(max_row=MAX_ROWS, max_col=MAX_COLS, values_only=True)]
            lay = find_layout(grid)
            if lay:
                found.append((ws.title, grid, lay))
    finally:
        wb.close()
    if not found:
        raise NotTAccount("No two-sided Trading and Profit & Loss account ('To' / 'By' lines with two Amount columns) was found.")
    if sheet:
        pick = next((f for f in found if f[0] == sheet), None)
        if pick is None:
            raise NotTAccount(f"Sheet '{sheet}' does not hold a two-sided account.")
    else:
        pick = found[0]
    title, grid, lay = pick
    end = _end_row(grid, lay)
    left, right = _read_side(grid, lay, "left", end), _read_side(grid, lay, "right", end)
    below = any(_num(v) is not None for row in grid[end:] for v in row)

    def src(ref: str | None) -> str | None:
        return f"{title}!{ref}" if ref else None

    lines: list[dict] = []
    notes: list[str] = []

    def add(label: str, key: str | None, value: float, source: str | None, kind: str = "reported", statement: str = "income"):
        lines.append({"label": label, "statement": statement, "key": key, "values": [value],
                      "source": "derived" if kind == "derived" else (source if statement == "balance" else src(source))})

    used: set[str] = set()

    def keyed(key: str | None) -> str | None:
        if key and key not in used:
            used.add(key)
            return key
        return None

    # ---- trading section
    t_left = [i for i in left if i["section"] == 0]
    t_right = [i for i in right if i["section"] == 0]
    sales = next((i for i in t_right if _is(i["label"], r"^(net )?sales\b", r"^turnover$", r"^revenue\b")), None)
    opening = next((i for i in t_left if _is(i["label"], r"^opening stock\b", r"^stock at (the )?beginning")), None)
    purchases = next((i for i in t_left if _is(i["label"], r"^purchases?\b")), None)
    closing = next((i for i in t_right if _is(i["label"], r"^closing stock\b", r"^stock at (the )?end")), None)
    gp_item = next((i for i in t_left if _is(i["label"], r"^gross profit\b")), None)
    gl_item = next((i for i in t_right if _is(i["label"], r"^gross loss\b")), None)

    sales_amt = None
    for item, key in ((sales, "revenue"), (opening, None), (purchases, None)):
        if item is None:
            continue
        v, ref, summed = _amount(item)
        if v is None:
            continue
        label = item["label"] + (" (sum of its lines)" if summed else "")
        add(label, keyed(key), v, ref)
        if item is sales:
            sales_amt = v
    direct = [i for i in t_left if i not in (opening, purchases, gp_item)]
    direct_vals = []
    for item in direct:
        v, ref, summed = _amount(item)
        if v is None:
            continue
        add(item["label"] + (" (sum of its lines)" if summed else ""), None, v, ref)
        direct_vals.append(v)
    if closing is not None:
        v, ref, summed = _amount(closing)
        if v is not None:
            add(closing["label"] + (" (sum of its lines)" if summed else ""), None, v, ref)
    other_right = [i for i in t_right if i not in (sales, closing, gl_item)]
    for item in other_right:
        v, ref, summed = _amount(item)
        if v is not None:
            add(item["label"] + (" (sum of its lines)" if summed else ""), None, v, ref)

    gross = None
    if gp_item is not None:
        v, ref, _ = _amount(gp_item)
        if v is not None:
            gross = v
            add("Gross profit", keyed("gross_profit"), v, ref)
    elif gl_item is not None:
        v, ref, _ = _amount(gl_item)
        if v is not None:
            gross = -v
            add("Gross loss (shown as a negative gross profit)", keyed("gross_profit"), -v, ref)

    # cost of goods sold, only when it reconciles with the gross profit the file reports
    if sales_amt is not None and opening and purchases and closing and gross is not None and not other_right:
        o, p, c = _amount(opening)[0], _amount(purchases)[0], _amount(closing)[0]
        if None not in (o, p, c):
            cogs = o + p + sum(direct_vals) - c
            if abs((sales_amt - cogs) - gross) <= TOLERANCE:
                extra = " + direct expenses" if direct_vals else ""
                add(f"Cost of goods sold (derived: opening stock + purchases{extra} − closing stock)", keyed("cogs"), cogs, None, "derived")
            else:
                notes.append("Sales less (opening stock + purchases − closing stock) does not equal the gross profit shown in the file, "
                             "so cost of goods sold was not derived. Please check the trading account.")

    # ---- profit & loss section
    p_left = [i for i in left if i["section"] >= 1]
    p_right = [i for i in right if i["section"] >= 1]
    net_item = next((i for i in p_left if _is(i["label"], r"^net profit\b")), None)
    loss_item = next((i for i in p_right if _is(i["label"], r"^net loss\b")), None)
    expenses = [i for i in p_left if i is not net_item and not _is(i["label"], r"^net loss\b", r"^gross profit\b")]
    incomes = [i for i in p_right if i is not loss_item and not _is(i["label"], r"^gross profit\b", r"^gross loss\b")]
    exp_total, exp_n, has_interest = 0.0, 0, False
    for item in expenses:
        v, ref, summed = _amount(item)
        if v is None:
            continue
        key = None
        if _is(item["label"], r"^interest( paid| on .*|)$", r"^interest( and bank)? charges$", r"^finance costs?$"):
            key, has_interest = "interest_expense", True
        elif _is(item["label"], r"^depreciation\b"):
            key = "depreciation_amortization"
        add(item["label"] + (" (sum of its lines)" if summed else ""), keyed(key), v, ref)
        exp_total += v
        exp_n += 1
    income_total = 0.0
    for item in incomes:
        v, ref, summed = _amount(item)
        if v is None:
            continue
        add(item["label"] + (" (sum of its lines)" if summed else ""), None, v, ref)
        income_total += v
    net = None
    if net_item is not None:
        v, ref, _ = _amount(net_item)
        if v is not None:
            net = v
            add("Net profit", keyed("net_income"), v, ref)
    elif loss_item is not None:
        v, ref, _ = _amount(loss_item)
        if v is not None:
            net = -v
            add("Net loss (shown as a negative net profit)", keyed("net_income"), -v, ref)

    if gross is not None and net is not None and exp_n and not has_interest and not incomes:
        ebit = gross - exp_total
        if abs(ebit - net) <= TOLERANCE:
            add(f"Operating profit (derived: gross profit − the {exp_n} expense lines)", keyed("operating_income"), ebit, None, "derived")
        else:
            notes.append("Gross profit less the expense lines does not equal the net profit shown in the file, so operating profit was not derived.")

    if not any(l["key"] for l in lines):
        raise NotTAccount("A two-sided account was found, but none of its lines (Sales, Gross profit, Net profit) could be read.")

    period = _period_of(grid)
    bs_end = _add_balance_sheet(grid, title, end, period, add, keyed, notes)
    last_row = end
    if bs_end is not None:
        last_row = bs_end + 1
        below = any(_num(v) is not None for row in grid[last_row:] for v in row)
    if period is None:
        period = "Current year"
        notes.append("The account does not state its year-end in a form that could be read, so the period is labelled 'Current year'.")
    other = [t for t, _, _ in found if t != title]
    if other:
        notes.append(f"This workbook has {len(other)} other two-sided account sheet(s) ({', '.join(other)}). "
                     f"Only '{title}' was imported; ask for another by sheet name.")
    notes.insert(0, "Lines starting 'To' are the debit side (stock, purchases, expenses, profit); lines starting 'By' are the credit side "
                    "(sales, closing stock). Amounts are shown as written in the file; no currency or unit is stated in it.")
    notes.append("The account covers one year, so growth and change calculations are not possible. Net profit is as shown in the account; "
                 "this layout does not deduct income tax.")
    if below:
        what = "first account and its balance sheet" if bs_end is not None else "first account"
        notes.append(f"Only the {what} (down to row {last_row}) was imported. The sheet continues below it (for example other "
                     "accounts or a balance sheet); that part was not read.")
    notes.append("Cash flow figures are not part of this import" + ("" if bs_end is not None else ", nor is a balance sheet")
                 + ", so ratios that need them show 'Needs data'.")
    return {
        "company": _company_of(grid),
        "periods": [period],
        "units": "",
        "lines": lines,
        "market": {},
        "approximations": {},
        "notes": notes,
        "sheet": title,
        "available_sheets": [t for t, _, _ in found],
    }
