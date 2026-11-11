"""Builds a made-up two-sided (To / By) Trading and Profit & Loss account, laid out like the ones many
Indian firms keep. Every name and figure here is invented."""

import io

from openpyxl import Workbook

# Trading account: Sales 5,000 + 1,500 = 6,500; closing stock 800 + 700 = 1,500;
# opening 600 + 400 = 1,000; purchases 3,000 + 1,000 = 4,000  ->  gross profit = 6,500 + 1,500 - 1,000 - 4,000 = 3,000.
# P&L: expenses 700 + 300 + 100 = 1,100  ->  net profit = 1,900.


def taccount_bytes(*, bad_gross_profit: bool = False, with_balance_sheet: bool = True, bad_balance: bool = False, extra_block: bool = True,
                   title: str = "TRADING AND PROFIT & LOSS A/C FOR THE YEAR ENDED 31/03/2025", bs_title: str = "BALANCE SHEET AS ON 31/03/2025") -> bytes:
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
        # Balance sheet: left 1,500 + 100 + 1,400 + 2,000 = 5,000; right 2,000 + 500 + 400 + 600 + 1,500 = 5,000.
        ws["B30"] = bs_title
        ws["C31"], ws["E31"], ws["G31"], ws["H31"] = "LIABILITIES", "AMOUNT ", "ASSETS", "AMOUNT "
        ws["G33"] = "FIXED ASSETS"
        ws["C34"], ws["E34"], ws["G34"], ws["H34"] = "Capital Account", 1500, "Building", 2000
        ws["C35"], ws["E35"], ws["G35"], ws["H35"] = "God's Account", 100, "Furniture", 500
        ws["C36"], ws["G36"] = "Current Liabilities :", "CURRENT ASSETS"
        ws["C37"], ws["E37"], ws["G37"], ws["H37"] = "Sundry Creditors", 1400, "Cash on Hand", 400
        ws["C38"], ws["G38"], ws["H38"] = "Secured Loan:", "Cash at Bank", 600
        ws["C39"], ws["E39"], ws["G39"], ws["H39"] = "Bank Loan", 2000, "Closing Stock", 1500
        ws["E40"], ws["H40"] = 5000 + (7 if bad_balance else 0), 5000
    if extra_block:  # another firm's account further down the same sheet: must not be read
        ws["B50"], ws["C50"], ws["E50"] = "To ", "Other Firm Rent", 777
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
