"""Builds a made-up two-sided (To / By) Trading and Profit & Loss account, laid out like the ones many
Indian firms keep. Every name and figure here is invented."""

import io

from openpyxl import Workbook

# Trading account: Sales 5,000 + 1,500 = 6,500; closing stock 800 + 700 = 1,500;
# opening 600 + 400 = 1,000; purchases 3,000 + 1,000 = 4,000  ->  gross profit = 6,500 + 1,500 - 1,000 - 4,000 = 3,000.
# P&L: expenses 700 + 300 + 100 = 1,100  ->  net profit = 1,900.


def taccount_bytes(*, bad_gross_profit: bool = False, with_balance_sheet: bool = True, title: str = "TRADING AND PROFIT & LOSS A/C FOR THE YEAR ENDED 31/03/2025") -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet3"
    ws["B2"] = "SAMPLE TRADERS"
    ws["B3"] = "1, EXAMPLE ROAD"
    ws["B7"] = title
    ws["C8"], ws["E8"], ws["G8"], ws["H8"] = "PARTICULARS", "Amount", "PARTICULARS", "Amount"
    rows = [
        # row, left (prefix col B, label col C, child label col D, amount col E), right (prefix F, label G, amount H)
        (10, {"B": "To ", "C": "Opening Stock"}, {"F": "By ", "G": "Sales"}),
        (11, {"D": "GOLD", "E": 600}, {"G": "GOLD", "H": 5000}),
        (12, {"D": "SILVER", "E": 400}, {"G": "SILVER", "H": 1500}),
        (13, {"B": "To ", "C": "Purchases"}, {"F": "By ", "G": "Closing Stock"}),
        (14, {"D": "GOLD", "E": 3000}, {"G": "GOLD", "H": 800, "J": 999999}),  # a stray figure outside the Amount column
        (15, {"D": "SILVER", "E": 1000}, {"G": "SILVER", "H": 700}),
        (16, {"B": "To ", "C": "Gross Profit", "E": 3500 if bad_gross_profit else 3000}, {}),
        (17, {"E": 8500 if bad_gross_profit else 8000}, {"H": 8000, "I": 0}),
        (18, {"B": "To ", "C": "Rent", "E": 700}, {"F": "By ", "G": "Gross Profit", "H": 3000}),
        (19, {"B": "To ", "C": "Salary", "E": 300}, {}),
        (20, {"B": "To ", "C": "Sundry Exp", "E": 100}, {}),
        (21, {"B": "To ", "C": "Net profit", "E": 1900}, {}),
        (23, {"E": 3000}, {"H": 3000, "I": 0}),
    ]
    for r, left, right in rows:
        for col, v in {**left, **right}.items():
            ws[f"{col}{r}"] = v
    if with_balance_sheet:
        ws["B30"] = "BALANCE SHEET AS ON 31/03/2025"
        ws["C31"], ws["E31"], ws["G31"], ws["H31"] = "LIABILITIES", "Amount", "ASSETS", "Amount"
        ws["B32"], ws["C32"], ws["E32"] = "To ", "Capital Account", 12345
        ws["F32"], ws["G32"], ws["H32"] = "By ", "Building", 12345
        ws["E33"], ws["H33"] = 12345, 12345
        ws["B34"], ws["C34"], ws["E34"] = "To ", "Sundry Creditors", 555  # must not be read as an expense
    ws2 = wb.create_sheet("Notes")
    ws2["A1"] = "Just a note"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def plain_table_bytes() -> bytes:
    """An ordinary table with an Amount column and 'To' words: must not be mistaken for a two-sided account."""
    wb = Workbook()
    ws = wb.active
    ws.append(["Item", "Amount"])
    ws.append(["Rent", 100])
    ws.append(["Salary", 200])
    ws.append(["Moving to the new shop", 300])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
