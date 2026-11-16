"""Excel kit builders: a spec-driven tracker/dashboard engine plus the finance models."""

from __future__ import annotations

import datetime as dt
import re

from openpyxl.chart import Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from lib import (add_dashboard, BORDER, FIRST, GREEN, LAST, MONEY, MONEY2, PCT, SOFT, TEAL, bar, calc, col, dropdown, head, inp, new_wb,
                 start_sheet, title, widths)

EQUITY = "Shareholders' equity"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
D = dt.date


def money_cols(ws, cells: str, fmt: str = MONEY) -> None:
    for row in ws[cells]:
        for c in row:
            c.number_format = fmt


# ======================================================================== tracker / dashboard engine
def tracker(heading, hint, cols, value, category=None, date=None, kpis=(), steps=None, note="", sheet="Data", first_month=D(2026, 1, 1), share=True):
    """cols: dicts with n(name), k(kind: date|text|num|money|list|formula), w(width), o(options), f(formula, {r}=row), s(samples), fmt.
    Builds a Start sheet, a Data sheet (1000 formatted rows, dropdowns, formulas) and a Summary sheet with charts."""
    wb = new_wb()
    ws = wb.create_sheet(sheet)
    title(ws, heading, hint)
    ids = {c["n"]: i + 1 for i, c in enumerate(cols)}

    def R(name):
        L = col(ids[name])
        return f"{sheet}!${L}${FIRST}:${L}${LAST}"

    head(ws, 4, [c["n"] for c in cols])
    widths(ws, [c.get("w", 16) for c in cols])
    ws.freeze_panes = "A5"
    nsamples = max((len(c.get("s", [])) for c in cols), default=0)
    for r in range(FIRST, LAST + 1):
        for i, c in enumerate(cols, start=1):
            cell = ws.cell(row=r, column=i)
            if c["k"] == "formula":
                cell.value = c["f"].format(r=r)
                calc(cell, c.get("fmt"))
            else:
                i0 = r - FIRST
                if i0 < nsamples and c.get("s"):
                    cell.value = c["s"][i0 % len(c["s"])]
                inp(cell)
                if c["k"] == "date":
                    cell.number_format = "dd-mmm-yyyy"
                elif c["k"] == "money":
                    cell.number_format = MONEY
                elif c.get("fmt"):
                    cell.number_format = c["fmt"]
    for i, c in enumerate(cols, start=1):
        if c["k"] == "list":
            dropdown(ws, f"{col(i)}{FIRST}:{col(i)}{LAST}", c["o"])
    for c in cols:
        if c.get("cf_text"):  # {"Overdue": "FFC7CE"} style highlights
            L = col(ids[c["n"]])
            for text, colour in c["cf_text"].items():
                ws.conditional_formatting.add(f"{L}{FIRST}:{L}{LAST}", FormulaRule(
                    formula=[f'{L}{FIRST}="{text}"'], fill=PatternFill("solid", bgColor=colour, fgColor=colour)))

    sm = wb.create_sheet("Summary")
    sm.sheet_view.showGridLines = False
    title(sm, f"{heading}: summary", "Updates automatically from the Data sheet. Nothing to type here except the peach start month.")
    base = [("Total " + value.lower(), f"=SUM({R(value)})", MONEY), ("Number of entries", f"=COUNT({R(value)})", "0"),
            ("Average per entry", f"=IFERROR(AVERAGE({R(value)}),0)", MONEY), ("Largest entry", f"=MAX({R(value)})", MONEY)]
    rows = list(base)
    for label, f, fmt in kpis:
        rows.append((label, re.sub(r"\[([^\]]+)\]", lambda m: R(m.group(1)), f), fmt))
    widths(sm, [30, 18, 11, 4, 14, 16, 4, 16, 16, 16])
    tiles = [(1, 1), (2, 3), (5, 6), (8, 9)]  # column spans of the four KPI tiles in a row
    for i, (label, f, fmt) in enumerate(rows[:8]):
        rr = 4 + (i // 4) * 3
        c1, c2 = tiles[i % 4]
        for rowx in (rr, rr + 1):
            for cc in range(c1, c2 + 1):
                cell = sm.cell(row=rowx, column=cc)
                cell.fill = PatternFill("solid", fgColor=SOFT)
                if rowx == rr:
                    cell.border = Border(top=Side(style="thick", color=TEAL))
            if c2 > c1:
                sm.merge_cells(start_row=rowx, start_column=c1, end_row=rowx, end_column=c2)
        lab = sm.cell(row=rr, column=c1, value=label)
        lab.font = Font(size=10, bold=True, color="5B6770")
        lab.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        val = sm.cell(row=rr + 1, column=c1, value=f)
        val.number_format = fmt
        val.font = Font(size=20, bold=True, color=GREEN)
        val.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        sm.row_dimensions[rr].height = 20
        sm.row_dimensions[rr + 1].height = 36
    top = 4 + ((min(len(rows), 8) - 1) // 4 + 1) * 3 + 2
    if category:
        head(sm, top, [category, "Total"] + (["Share"] if share else []))
        opts = next(c["o"] for c in cols if c["n"] == category)
        for i, o in enumerate(opts):
            r = top + 1 + i
            sm.cell(row=r, column=1, value=o).border = BORDER
            b = sm.cell(row=r, column=2, value=f"=SUMIFS({R(value)},{R(category)},A{r})")
            calc(b, MONEY)
            if share:
                c3 = sm.cell(row=r, column=3, value=f"=IFERROR(B{r}/$B${top + 1 + len(opts)},0)")
                calc(c3, PCT)
        tr = top + 1 + len(opts)
        sm.cell(row=tr, column=1, value="Total").font = Font(bold=True)
        calc(sm.cell(row=tr, column=2, value=f"=SUM(B{top + 1}:B{tr - 1})"), MONEY, True)
        bar(sm, f"H{top}", f"{value} by {category}", Reference(sm, min_col=1, min_row=top + 1, max_row=tr - 1),
            Reference(sm, min_col=2, min_row=top, max_row=tr - 1))
    if date:
        mcol = 5 if category else 1
        sm.cell(row=top - 1, column=mcol, value="Start month").font = Font(bold=True)
        s = sm.cell(row=top - 1, column=mcol + 1, value=first_month)
        inp(s, "mmm-yyyy")
        head(sm, top, ["Month", value], start=mcol)
        for i in range(12):
            r = top + 1 + i
            a = sm.cell(row=r, column=mcol, value=f"=EDATE(${col(mcol + 1)}${top - 1},{i})")
            a.number_format = "mmm-yyyy"
            a.border = BORDER
            b = sm.cell(row=r, column=mcol + 1,
                        value=f'=SUMIFS({R(value)},{R(date)},">="&{col(mcol)}{r},{R(date)},"<"&EDATE({col(mcol)}{r},1))')
            calc(b, MONEY)
        bar(sm, f"H{top + 17}" if category else f"H{top}", f"{value} by month", Reference(sm, min_col=mcol, min_row=top + 1, max_row=top + 12),
            Reference(sm, min_col=mcol + 1, min_row=top, max_row=top + 12), line=True)
    start_sheet(wb, "Start here", heading, steps or [
        f"Open the {sheet} sheet and type over the sample rows (they are examples). One row per entry.",
        "Pick values from the dropdown lists where you see them.",
        "Open the Summary sheet to see totals, shares and the monthly chart update by themselves.",
        "The sheet is formatted for 1,000 rows. Copy the last row down if you need more.",
    ], note)
    return wb


# ======================================================================== finance models
def budget_tracker():
    wb = new_wb()
    cats = ["Rent", "Groceries", "Transport", "Bills", "Education", "Eating out", "Shopping", "Health", "EMI", "Other"]
    b = wb.create_sheet("Budget")
    title(b, "Monthly budget by category", "Type your planned monthly amount for each category.")
    head(b, 4, ["Category", "Monthly budget"])
    widths(b, [24, 18])
    plan = [9000, 6000, 2000, 2500, 3000, 1500, 2000, 1000, 4000, 1500]
    for i, (c, p) in enumerate(zip(cats, plan)):
        b.cell(row=5 + i, column=1, value=c).border = BORDER
        inp(b.cell(row=5 + i, column=2, value=p), MONEY)
    b.cell(row=15, column=1, value="Total budget").font = Font(bold=True)
    calc(b.cell(row=15, column=2, value="=SUM(B5:B14)"), MONEY, True)
    inc = wb.create_sheet("Transactions")
    title(inc, "Transactions", "One row per income or expense. Pick Income or Expense and a category.")
    head(inc, 4, ["Date", "Type", "Category", "Note", "Amount"])
    widths(inc, [14, 12, 16, 30, 14])
    samples = [(D(2026, 1, 1), "Income", "Salary", "January salary", 30000), (D(2026, 1, 2), "Expense", "Rent", "House rent", 9000),
               (D(2026, 1, 4), "Expense", "Groceries", "Weekly groceries", 1800), (D(2026, 1, 8), "Expense", "Transport", "Metro card", 600),
               (D(2026, 1, 12), "Expense", "Bills", "Electricity", 1100), (D(2026, 1, 15), "Income", "Other", "Freelance work", 4000),
               (D(2026, 1, 20), "Expense", "Eating out", "Dinner", 900), (D(2026, 1, 25), "Expense", "EMI", "Phone EMI", 2000)]
    for r in range(5, 1005):
        for c in range(1, 6):
            cell = inc.cell(row=r, column=c)
            if r - 5 < len(samples):
                cell.value = samples[r - 5][c - 1]
            inp(cell)
        inc.cell(row=r, column=1).number_format = "dd-mmm-yyyy"
        inc.cell(row=r, column=5).number_format = MONEY
    dropdown(inc, "B5:B1004", ["Income", "Expense"])
    dropdown(inc, "C5:C1004", cats + ["Salary"])
    inc.freeze_panes = "A5"

    s = wb.create_sheet("Month view")
    s.sheet_view.showGridLines = False
    title(s, "Month view: budget vs actual", "Change the peach month to see any month. Red means over budget.")
    s["A3"], s["B3"] = "Month (1st of month)", D(2026, 1, 1)
    inp(s["B3"], "mmm-yyyy")
    s["A4"], s["B4"] = "Total income", '=SUMIFS(Transactions!$E$5:$E$1004,Transactions!$B$5:$B$1004,"Income",Transactions!$A$5:$A$1004,">="&B3,Transactions!$A$5:$A$1004,"<"&EDATE(B3,1))'
    s["A5"], s["B5"] = "Total expenses", '=SUMIFS(Transactions!$E$5:$E$1004,Transactions!$B$5:$B$1004,"Expense",Transactions!$A$5:$A$1004,">="&B3,Transactions!$A$5:$A$1004,"<"&EDATE(B3,1))'
    s["A6"], s["B6"] = "Savings", "=B4-B5"
    s["A7"], s["B7"] = "Savings rate", "=IFERROR(B6/B4,0)"
    for r in (4, 5, 6):
        calc(s[f"B{r}"], MONEY, True)
    calc(s["B7"], PCT, True)
    head(s, 9, ["Category", "Budget", "Actual", "Left", "Status"])
    widths(s, [24, 16, 16, 16, 14])
    for i, c in enumerate(cats):
        r = 10 + i
        s.cell(row=r, column=1, value=c).border = BORDER
        calc(s.cell(row=r, column=2, value=f"=Budget!B{5 + i}"), MONEY)
        calc(s.cell(row=r, column=3, value=f'=SUMIFS(Transactions!$E$5:$E$1004,Transactions!$B$5:$B$1004,"Expense",Transactions!$C$5:$C$1004,A{r},Transactions!$A$5:$A$1004,">="&$B$3,Transactions!$A$5:$A$1004,"<"&EDATE($B$3,1))'), MONEY)
        calc(s.cell(row=r, column=4, value=f"=B{r}-C{r}"), MONEY)
        calc(s.cell(row=r, column=5, value=f'=IF(C{r}>B{r},"Over budget","OK")'))
    s.conditional_formatting.add("E10:E19", FormulaRule(formula=['E10="Over budget"'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    bar(s, "G3", "Budget vs actual", Reference(s, min_col=1, min_row=10, max_row=19), Reference(s, min_col=2, max_col=3, min_row=9, max_row=19))

    g = wb.create_sheet("Savings goals")
    title(g, "Savings goals", "Add what you are saving for, the target, and how much you have saved so far.")
    head(g, 4, ["Goal", "Target", "Saved so far", "Remaining", "Progress", "Monthly saving", "Months left"])
    widths(g, [26, 14, 14, 14, 12, 16, 12])
    for i, (n, t, sv, m) in enumerate([("Emergency fund", 60000, 15000, 3000), ("New laptop", 50000, 12000, 2500), ("Trip", 20000, 5000, 1500)] + [("", None, None, None)] * 7):
        r = 5 + i
        for c, v in enumerate([n, t, sv], start=1):
            inp(g.cell(row=r, column=c, value=v), MONEY if c > 1 else None)
        calc(g.cell(row=r, column=4, value=f'=IF(B{r}="","",B{r}-C{r})'), MONEY)
        calc(g.cell(row=r, column=5, value=f'=IF(B{r}="","",C{r}/B{r})'), "0%")
        inp(g.cell(row=r, column=6, value=m), MONEY)
        calc(g.cell(row=r, column=7, value=f'=IF(OR(B{r}="",F{r}="",F{r}=0),"",ROUNDUP(D{r}/F{r},0))'), "0")

    e = wb.create_sheet("EMI tracker")
    title(e, "Loan / EMI tracker", "Enter each loan. The EMI is calculated for you.")
    head(e, 4, ["Loan", "Amount", "Interest % per year", "Years", "Monthly EMI", "Total paid", "Total interest"])
    widths(e, [24, 14, 18, 8, 14, 14, 14])
    for i, (n, a, ir, y) in enumerate([("Phone EMI", 40000, 14, 2), ("Education loan", 300000, 9.5, 5)] + [("", None, None, None)] * 6):
        r = 5 + i
        for c, v in enumerate([n, a, ir, y], start=1):
            inp(e.cell(row=r, column=c, value=v), MONEY if c == 2 else None)
        calc(e.cell(row=r, column=5, value=f'=IF(B{r}="","",-PMT(C{r}/1200,D{r}*12,B{r}))'), MONEY)
        calc(e.cell(row=r, column=6, value=f'=IF(B{r}="","",E{r}*D{r}*12)'), MONEY)
        calc(e.cell(row=r, column=7, value=f'=IF(B{r}="","",F{r}-B{r})'), MONEY)
    add_dashboard(wb, "Personal budget: dashboard", [
        ("Income this month", "='Month view'!B4", MONEY), ("Expenses this month", "='Month view'!B5", MONEY),
        ("Savings this month", "='Month view'!B6", MONEY), ("Savings rate", "='Month view'!B7", PCT),
        ("Total monthly budget", "=Budget!B15", MONEY), ("Saved towards goals", "=SUM('Savings goals'!C5:C14)", MONEY),
        ("Months to reach goals", "=IFERROR(MAX('Savings goals'!G5:G14),0)", "0"), ("EMIs per month", "=SUM('EMI tracker'!E5:E12)", MONEY)],
        [dict(kind="bar", title="Budget vs actual (month chosen on Month view)", cats=cats,
              series=[("Budget", [f"='Month view'!B{10 + i}" for i in range(10)]), ("Actual", [f"='Month view'!C{10 + i}" for i in range(10)])])])
    start_sheet(wb, "Start here", "Personal budget tracker", [
        "Budget sheet: type your planned monthly amount for each category.",
        "Transactions sheet: add every income and expense (one row each). Sample rows are examples; type over them.",
        "Month view: change the month to see budget vs actual and your savings rate. Red = over budget.",
        "Savings goals and EMI tracker: optional extras for goals and loans.",
    ])
    wb.move_sheet("Month view", offset=-3)
    return wb


def pnl_dashboard(heading="Monthly profit and loss dashboard", rev=("Product sales", "Services", "Other income"), cogs=("Materials / stock", "Direct labour"),
                  opex=("Rent", "Salaries", "Electricity and water", "Marketing", "Transport", "Other expenses")):
    wb = new_wb()
    ws = wb.create_sheet("Monthly P&L")
    ws.sheet_view.showGridLines = False
    title(ws, heading, "Type your monthly figures in the peach cells. Totals, profit and margins calculate by themselves.")
    head(ws, 4, ["Line"] + MONTHS + ["Year total"])
    widths(ws, [28] + [11] * 12 + [14])
    ws.freeze_panes = "B5"
    r = 5
    sample = {"Product sales": 60000, "Services": 18000, "Other income": 2000, "Materials / stock": 29000, "Direct labour": 8000,
              "Rent": 12000, "Salaries": 15000, "Electricity and water": 2500, "Marketing": 3000, "Transport": 1800, "Other expenses": 2200}

    def block(label, names, first_row):
        ws.cell(row=first_row, column=1, value=label).font = Font(bold=True, color=GREEN)
        rr = first_row + 1
        for n in names:
            ws.cell(row=rr, column=1, value=n).border = BORDER
            for m in range(12):
                inp(ws.cell(row=rr, column=2 + m, value=sample.get(n, 0) if m < 6 else None), MONEY)
            calc(ws.cell(row=rr, column=14, value=f"=SUM(B{rr}:M{rr})"), MONEY)
            rr += 1
        ws.cell(row=rr, column=1, value=f"Total {label.lower()}").font = Font(bold=True)
        for m in range(13):
            c = col(2 + m)
            calc(ws.cell(row=rr, column=2 + m, value=f"=SUM({c}{first_row + 1}:{c}{rr - 1})"), MONEY, True)
        return rr

    t_rev = block("Revenue", rev, 5)
    t_cogs = block("Cost of goods sold", cogs, t_rev + 2)
    gp = t_cogs + 1
    ws.cell(row=gp, column=1, value="Gross profit").font = Font(bold=True)
    for m in range(13):
        c = col(2 + m)
        calc(ws.cell(row=gp, column=2 + m, value=f"={c}{t_rev}-{c}{t_cogs}"), MONEY, True)
    t_opex = block("Operating expenses", opex, gp + 2)
    npf = t_opex + 1
    ws.cell(row=npf, column=1, value="Net profit").font = Font(bold=True)
    gm = npf + 1
    nm = npf + 2
    ws.cell(row=gm, column=1, value="Gross margin %").font = Font(bold=True)
    ws.cell(row=nm, column=1, value="Net margin %").font = Font(bold=True)
    for m in range(13):
        c = col(2 + m)
        calc(ws.cell(row=npf, column=2 + m, value=f"={c}{gp}-{c}{t_opex}"), MONEY, True)
        calc(ws.cell(row=gm, column=2 + m, value=f"=IFERROR({c}{gp}/{c}{t_rev},0)"), PCT)
        calc(ws.cell(row=nm, column=2 + m, value=f"=IFERROR({c}{npf}/{c}{t_rev},0)"), PCT)
    ws.conditional_formatting.add(f"B{npf}:N{npf}", CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    bar(ws, f"B{nm + 3}", "Revenue and net profit by month", Reference(ws, min_col=2, max_col=13, min_row=4),
        Reference(ws, min_col=1, max_col=13, min_row=t_rev), w=24)
    ch = ws._charts[-1]
    ch.series = []
    from openpyxl.chart import Series
    for rowno, name in ((t_rev, "Revenue"), (npf, "Net profit")):
        s = Series(Reference(ws, min_col=2, max_col=13, min_row=rowno), title=name)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=2, max_col=13, min_row=4))
    mcols = [col(2 + m) for m in range(12)]
    add_dashboard(wb, f"{heading}: dashboard", [
        ("Revenue (year)", f"='Monthly P&L'!N{t_rev}", MONEY), ("Gross profit", f"='Monthly P&L'!N{gp}", MONEY),
        ("Net profit", f"='Monthly P&L'!N{npf}", MONEY), ("Net margin", f"='Monthly P&L'!N{nm}", PCT),
        ("Gross margin", f"='Monthly P&L'!N{gm}", PCT), ("Total expenses", f"='Monthly P&L'!N{t_opex}", MONEY),
        ("Best month profit", f"=MAX('Monthly P&L'!B{npf}:M{npf})", MONEY), ("Loss-making months", f"=COUNTIF('Monthly P&L'!B{npf}:M{npf},{chr(34)}<0{chr(34)})", "0")],
        [dict(kind="bar", zero=False, title="Revenue and net profit by month", cats=MONTHS,
              series=[("Revenue", [f"='Monthly P&L'!{c}{t_rev}" for c in mcols]), ("Net profit", [f"='Monthly P&L'!{c}{npf}" for c in mcols])])])
    start_sheet(wb, "Start here", heading, [
        "Open Monthly P&L. Type each month's revenue, cost of goods and expenses in the peach cells (the first six months are examples).",
        "Edit the line names in column A to match your business.",
        "Read gross profit, net profit and margins at the bottom. A red net profit means a loss that month.",
        "Use the chart to see revenue and profit trends across the year.",
    ])
    return wb


def variance_report():
    wb = new_wb()
    ws = wb.create_sheet("Variance")
    ws.sheet_view.showGridLines = False
    title(ws, "Budget vs actual variance report", "Enter budget and actual for each line. Favourable = better than budget. Flag shows lines more than the tolerance off budget.")
    ws["A3"], ws["B3"] = "Review flag above (±%)", 0.10
    inp(ws["B3"], "0%")
    head(ws, 5, ["Line item", "Type", "Budget", "Actual", "Variance", "Variance %", "Result", "Flag"])
    widths(ws, [28, 12, 14, 14, 14, 12, 14, 12])
    lines = [("Sales revenue", "Revenue", 500000, 524000), ("Service income", "Revenue", 120000, 98000), ("Raw materials", "Cost", 240000, 262000),
             ("Salaries", "Cost", 110000, 110000), ("Rent", "Cost", 36000, 36000), ("Marketing", "Cost", 25000, 41000),
             ("Electricity", "Cost", 9000, 9800), ("Transport", "Cost", 12000, 10500)] + [("", "Cost", None, None)] * 12
    for i, (n, t, b, a) in enumerate(lines):
        r = 6 + i
        inp(ws.cell(row=r, column=1, value=n))
        inp(ws.cell(row=r, column=2, value=t))
        inp(ws.cell(row=r, column=3, value=b), MONEY)
        inp(ws.cell(row=r, column=4, value=a), MONEY)
        calc(ws.cell(row=r, column=5, value=f'=IF(C{r}="","",D{r}-C{r})'), MONEY)
        calc(ws.cell(row=r, column=6, value=f'=IF(OR(C{r}="",C{r}=0),"",E{r}/C{r})'), PCT)
        calc(ws.cell(row=r, column=7, value=f'=IF(C{r}="","",IF(E{r}=0,"On budget",IF(OR(AND(B{r}="Revenue",E{r}>0),AND(B{r}="Cost",E{r}<0)),"Favourable","Unfavourable")))'))
        calc(ws.cell(row=r, column=8, value=f'=IF(F{r}="","",IF(ABS(F{r})>$B$3,"Review","OK"))'))
    dropdown(ws, "B6:B25", ["Revenue", "Cost"])
    ws.cell(row=27, column=1, value="Total revenue").font = Font(bold=True)
    ws.cell(row=28, column=1, value="Total cost").font = Font(bold=True)
    ws.cell(row=29, column=1, value="Profit").font = Font(bold=True)
    for r, f in ((27, 'SUMIFS({c}6:{c}25,$B$6:$B$25,"Revenue")'), (28, 'SUMIFS({c}6:{c}25,$B$6:$B$25,"Cost")')):
        for c in "CD":
            calc(ws[f"{c}{r}"], MONEY, True)
            ws[f"{c}{r}"] = "=" + f.format(c=c)
    for c in "CD":
        calc(ws[f"{c}29"], MONEY, True)
        ws[f"{c}29"] = f"={c}27-{c}28"
    calc(ws["E29"], MONEY, True)
    ws["E29"] = "=D29-C29"
    ws.conditional_formatting.add("H6:H25", FormulaRule(formula=['H6="Review"'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    ws.conditional_formatting.add("G6:G25", FormulaRule(formula=['G6="Unfavourable"'], fill=PatternFill("solid", bgColor="FFE5B4", fgColor="FFE5B4")))
    bar(ws, "J5", "Budget vs actual", Reference(ws, min_col=1, min_row=6, max_row=13), Reference(ws, min_col=3, max_col=4, min_row=5, max_row=13))
    c = wb.create_sheet("Commentary")
    title(c, "Variance commentary", "For every line flagged Review, write why it happened and what you will do.")
    head(c, 4, ["Line item", "Why did it differ?", "Action", "Owner", "Due date"])
    widths(c, [26, 50, 40, 16, 14])
    for r in range(5, 25):
        for cc in range(1, 6):
            inp(c.cell(row=r, column=cc))
    add_dashboard(wb, "Budget vs actual: dashboard", [
        ("Revenue (actual)", "=Variance!D27", MONEY), ("Revenue (budget)", "=Variance!C27", MONEY),
        ("Profit (actual)", "=Variance!D29", MONEY), ("Profit vs budget", "=Variance!E29", MONEY),
        ("Total cost (actual)", "=Variance!D28", MONEY), ("Lines to review", '=COUNTIF(Variance!H6:H25,"Review")', "0"),
        ("Unfavourable lines", '=COUNTIF(Variance!G6:G25,"Unfavourable")', "0"), ("Review threshold", "=Variance!B3", "0%")],
        [dict(kind="bar", title="Budget vs actual by line", cats=[f"=Variance!A{6 + i}" for i in range(8)],
              series=[("Budget", [f"=Variance!C{6 + i}" for i in range(8)]), ("Actual", [f"=Variance!D{6 + i}" for i in range(8)])])])
    start_sheet(wb, "Start here", "Budget vs actual variance report", [
        "Variance sheet: type each line's budget and actual. Mark it Revenue or Cost (this decides whether higher is good or bad).",
        "Change the review threshold in cell B3 (10% by default). Lines further off than this show Review in red.",
        "Commentary sheet: write the reason and action for every Review line. This is the part managers read.",
        "For monthly use, save a copy of the workbook each month.",
    ])
    return wb


def cashflow_forecast():
    wb = new_wb()
    ws = wb.create_sheet("12-month forecast")
    ws.sheet_view.showGridLines = False
    title(ws, "12-month cash flow forecast", "Type opening cash and your expected receipts and payments. Closing cash and warnings calculate by themselves.")
    ws["A3"], ws["B3"] = "Opening cash", 50000
    inp(ws["B3"], MONEY)
    ws["D3"], ws["E3"] = "Min. cash", 20000
    inp(ws["E3"], MONEY)
    head(ws, 5, ["Line"] + MONTHS + ["Total"])
    widths(ws, [28] + [11] * 12 + [14])
    ws.freeze_panes = "B6"
    receipts = [("Customer receipts", 100000), ("Other receipts", 3000), ("Loan / funding received", 0)]
    pays = [("Purchases / materials", 40000), ("Salaries", 25000), ("Rent", 12000), ("Utilities", 4000), ("Marketing", 5000), ("Loan repayment (EMI)", 6000), ("Tax and GST paid", 4000), ("Other payments", 3000)]
    ws.cell(row=6, column=1, value="Cash in").font = Font(bold=True, color=GREEN)
    r = 7
    for n, v in receipts:
        ws.cell(row=r, column=1, value=n).border = BORDER
        for m in range(12):
            inp(ws.cell(row=r, column=2 + m, value=v if m < 12 else None), MONEY)
        calc(ws.cell(row=r, column=14, value=f"=SUM(B{r}:M{r})"), MONEY)
        r += 1
    t_in = r
    ws.cell(row=t_in, column=1, value="Total cash in").font = Font(bold=True)
    for m in range(13):
        c = col(2 + m)
        calc(ws.cell(row=t_in, column=2 + m, value=f"=SUM({c}7:{c}{t_in - 1})"), MONEY, True)
    ws.cell(row=t_in + 2, column=1, value="Cash out").font = Font(bold=True, color=GREEN)
    r = t_in + 3
    first_out = r
    for n, v in pays:
        ws.cell(row=r, column=1, value=n).border = BORDER
        for m in range(12):
            inp(ws.cell(row=r, column=2 + m, value=v), MONEY)
        calc(ws.cell(row=r, column=14, value=f"=SUM(B{r}:M{r})"), MONEY)
        r += 1
    t_out = r
    ws.cell(row=t_out, column=1, value="Total cash out").font = Font(bold=True)
    for m in range(13):
        c = col(2 + m)
        calc(ws.cell(row=t_out, column=2 + m, value=f"=SUM({c}{first_out}:{c}{t_out - 1})"), MONEY, True)
    net, op, cl, warn = t_out + 2, t_out + 3, t_out + 4, t_out + 5
    for rr, lab in ((net, "Net cash flow"), (op, "Opening cash"), (cl, "Closing cash"), (warn, "Warning")):
        ws.cell(row=rr, column=1, value=lab).font = Font(bold=True)
    for m in range(12):
        c = col(2 + m)
        calc(ws.cell(row=net, column=2 + m, value=f"={c}{t_in}-{c}{t_out}"), MONEY, True)
        calc(ws.cell(row=op, column=2 + m, value="=$B$3" if m == 0 else f"={col(1 + m)}{cl}"), MONEY)
        calc(ws.cell(row=cl, column=2 + m, value=f"={c}{op}+{c}{net}"), MONEY, True)
        calc(ws.cell(row=warn, column=2 + m, value=f'=IF({c}{cl}<0,"CASH SHORT",IF({c}{cl}<$E$3,"Low","OK"))'))
    ws.conditional_formatting.add(f"B{warn}:M{warn}", FormulaRule(formula=[f'B{warn}="CASH SHORT"'], fill=PatternFill("solid", bgColor="FF9999", fgColor="FF9999")))
    ws.conditional_formatting.add(f"B{warn}:M{warn}", FormulaRule(formula=[f'B{warn}="Low"'], fill=PatternFill("solid", bgColor="FFE5B4", fgColor="FFE5B4")))
    bar(ws, f"B{warn + 3}", "Closing cash by month", Reference(ws, min_col=2, max_col=13, min_row=5), Reference(ws, min_col=1, max_col=13, min_row=cl), w=24, line=True)
    from openpyxl.chart import Series
    ch = ws._charts[-1]
    ch.series = []
    ch.series.append(Series(Reference(ws, min_col=2, max_col=13, min_row=cl), title="Closing cash"))
    ch.set_categories(Reference(ws, min_col=2, max_col=13, min_row=5))
    mc = [col(2 + m) for m in range(12)]
    add_dashboard(wb, "Cash flow: dashboard", [
        ("Opening cash", "='12-month forecast'!B3", MONEY), ("Total cash in", f"='12-month forecast'!N{t_in}", MONEY),
        ("Total cash out", f"='12-month forecast'!N{t_out}", MONEY), ("Closing cash (December)", f"='12-month forecast'!M{cl}", MONEY),
        ("Lowest closing cash", f"=MIN('12-month forecast'!B{cl}:M{cl})", MONEY), ("Months short of cash", f'=COUNTIF({chr(39)}12-month forecast{chr(39)}!B{warn}:M{warn},"CASH SHORT")', "0"),
        ("Average monthly net", f"=AVERAGE('12-month forecast'!B{net}:M{net})", MONEY), ("Months below safe level", f'=COUNTIF({chr(39)}12-month forecast{chr(39)}!B{warn}:M{warn},"Low")', "0")],
        [dict(kind="line", title="Closing cash by month", cats=MONTHS, series=[("Closing cash", [f"='12-month forecast'!{c}{cl}" for c in mc])]),
         dict(kind="bar", title="Cash in vs cash out", cats=MONTHS, series=[("Cash in", [f"='12-month forecast'!{c}{t_in}" for c in mc]), ("Cash out", [f"='12-month forecast'!{c}{t_out}" for c in mc])])])
    start_sheet(wb, "Start here", "12-month cash flow forecast", [
        "Type your opening cash (cell B3) and the minimum cash you want to keep safe (cell E3).",
        "Fill in expected cash in and cash out for each month. The examples are placeholders: type over them.",
        "Read the Warning row: CASH SHORT means you would run out of cash that month; Low means below your safe level.",
        "Change numbers to test 'what if' ideas (a late customer, a new loan) and watch closing cash.",
    ])
    return wb


def breakeven():
    wb = new_wb()
    ws = wb.create_sheet("Break-even")
    ws.sheet_view.showGridLines = False
    title(ws, "Break-even and pricing analysis", "Type the peach cells. See how many units you must sell to cover costs, and test different prices.")
    labels = [("Selling price per unit", 250, MONEY), ("Variable cost per unit", 140, MONEY), ("Fixed costs per month", 55000, MONEY), ("Target profit per month", 20000, MONEY)]
    for i, (l, v, f) in enumerate(labels):
        ws.cell(row=3 + i, column=1, value=l).font = Font(bold=True)
        inp(ws.cell(row=3 + i, column=2, value=v), f)
    out = [("Contribution per unit", "=B3-B4", MONEY), ("Contribution margin %", "=IFERROR(B8/B3,0)", PCT),
           ("Break-even units per month", "=IFERROR(ROUNDUP(B5/B8,0),0)", "#,##0"), ("Break-even sales per month", "=B10*B3", MONEY),
           ("Units needed for target profit", "=IFERROR(ROUNDUP((B5+B6)/B8,0),0)", "#,##0"), ("Sales needed for target profit", "=B12*B3", MONEY)]
    for i, (l, f, fmt) in enumerate(out):
        ws.cell(row=8 + i, column=1, value=l).font = Font(bold=True)
        calc(ws.cell(row=8 + i, column=2, value=f), fmt, True)
    ws["A15"], ws["B15"] = "Expected units sold per month", 650
    ws["A15"].font = Font(bold=True)
    inp(ws["B15"], "#,##0")
    ws["A16"], ws["B16"] = "Profit at expected units", "=B15*B8-B5"
    ws["A17"], ws["B17"] = "Margin of safety", '=IFERROR((B15-B10)/B15,0)'
    ws["A16"].font = ws["A17"].font = Font(bold=True)
    calc(ws["B16"], MONEY, True)
    calc(ws["B17"], PCT, True)
    widths(ws, [34, 18, 4, 14, 14, 14, 14])
    head(ws, 3, ["Units", "Sales", "Total cost", "Profit"], start=4)
    for i in range(13):
        r = 4 + i
        calc(ws.cell(row=r, column=4, value=f"={i}*MAX(1,ROUNDUP($B$10/6,0))"), "#,##0")
        calc(ws.cell(row=r, column=5, value=f"=D{r}*$B$3"), MONEY)
        calc(ws.cell(row=r, column=6, value=f"=$B$5+D{r}*$B$4"), MONEY)
        calc(ws.cell(row=r, column=7, value=f"=E{r}-F{r}"), MONEY)
    bar(ws, "I3", "Sales vs total cost (they cross at break-even)", Reference(ws, min_col=4, min_row=4, max_row=16), Reference(ws, min_col=5, max_col=6, min_row=3, max_row=16), line=True)
    pr = wb.create_sheet("Price test")
    title(pr, "Price test: what if I change my price?", "Type different prices in column A and see profit at your expected volume.")
    head(pr, 4, ["Price per unit", "Contribution / unit", "Break-even units", "Profit at expected units", "Margin %"])
    widths(pr, [16, 18, 18, 24, 12])
    for i, p in enumerate([200, 220, 250, 280, 300, 330, 360, 400]):
        r = 5 + i
        inp(pr.cell(row=r, column=1, value=p), MONEY)
        calc(pr.cell(row=r, column=2, value=f"=A{r}-'Break-even'!$B$4"), MONEY)
        calc(pr.cell(row=r, column=3, value=f"=IFERROR(ROUNDUP('Break-even'!$B$5/B{r},0),\"n/a\")"), "#,##0")
        calc(pr.cell(row=r, column=4, value=f"='Break-even'!$B$15*B{r}-'Break-even'!$B$5"), MONEY)
        calc(pr.cell(row=r, column=5, value=f"=IFERROR(B{r}/A{r},0)"), PCT)
    add_dashboard(wb, "Break-even: dashboard", [
        ("Break-even units / month", "='Break-even'!B10", "#,##0"), ("Break-even sales / month", "='Break-even'!B11", MONEY),
        ("Contribution per unit", "='Break-even'!B8", MONEY), ("Contribution margin", "='Break-even'!B9", PCT),
        ("Units for target profit", "='Break-even'!B12", "#,##0"), ("Sales for target profit", "='Break-even'!B13", MONEY),
        ("Profit at expected units", "='Break-even'!B16", MONEY), ("Margin of safety", "='Break-even'!B17", PCT)],
        [dict(kind="line", title="Sales vs total cost (they cross at break-even)", cats=[f"='Break-even'!D{4 + i}" for i in range(13)],
              series=[("Sales", [f"='Break-even'!E{4 + i}" for i in range(13)]), ("Total cost", [f"='Break-even'!F{4 + i}" for i in range(13)])]),
         dict(kind="bar", zero=False, title="Profit at each volume", cats=[f"='Break-even'!D{4 + i}" for i in range(13)],
              series=[("Profit", [f"='Break-even'!G{4 + i}" for i in range(13)])])])
    start_sheet(wb, "Start here", "Break-even and pricing analysis", [
        "Break-even sheet: type your price, cost per unit, fixed costs per month and the profit you want.",
        "Read the green cells: how many units and how much sales you need to break even and to reach your target.",
        "Type your expected monthly units to see profit and margin of safety (how far sales can fall before a loss).",
        "Price test sheet: try different prices side by side before you change them.",
    ])
    return wb


def ratio_workbook(heading="Financial ratio analysis workbook"):
    wb = new_wb()
    ws = wb.create_sheet("Inputs")
    title(ws, "Financial statement inputs", "Type two years of figures from the company's profit and loss account and balance sheet. All amounts in the same unit (e.g. ₹ lakh).")
    head(ws, 4, ["Item", "Year 1 (latest)", "Year 2 (previous)"])
    widths(ws, [34, 18, 18])
    items = [("Revenue (net sales)", 1250, 1100), ("Cost of goods sold", 780, 700), ("Operating expenses", 260, 240), ("Interest expense", 35, 38),
             ("Tax", 38, 30), ("Net profit", 137, 92), ("Inventory", 210, 190), ("Trade receivables", 180, 160), ("Cash and bank", 95, 70),
             ("Other current assets", 40, 35), ("Fixed assets (net)", 520, 480), ("Total assets", 1045, 935), ("Trade payables", 150, 140),
             ("Short-term borrowings", 90, 100), ("Other current liabilities", 60, 55), ("Long-term borrowings", 200, 220), (EQUITY, 545, 420)]
    for i, (n, a, b) in enumerate(items):
        r = 5 + i
        ws.cell(row=r, column=1, value=n).border = BORDER
        inp(ws.cell(row=r, column=2, value=a), "#,##0.0")
        inp(ws.cell(row=r, column=3, value=b), "#,##0.0")
    ref = {n: 5 + i for i, (n, _, _) in enumerate(items)}

    def v(n, c="B"):
        return f"Inputs!{c}{ref[n]}"

    rt = wb.create_sheet("Ratios")
    rt.sheet_view.showGridLines = False
    title(rt, "Ratios and what they mean", "Everything calculates from the Inputs sheet.")
    head(rt, 4, ["Ratio", "Year 1", "Year 2", "Good range", "Reading (Year 1)"])
    widths(rt, [30, 12, 12, 22, 60])
    cur_a = lambda c: f"({v('Inventory', c)}+{v('Trade receivables', c)}+{v('Cash and bank', c)}+{v('Other current assets', c)})"
    cur_l = lambda c: f"({v('Trade payables', c)}+{v('Short-term borrowings', c)}+{v('Other current liabilities', c)})"
    ratios = [
        ("LIQUIDITY", None, None, "", ""),
        ("Current ratio", lambda c: f"=IFERROR({cur_a(c)}/{cur_l(c)},0)", "0.00", "1.5 to 2", 'IF(B{r}>=2,"Strong short-term cover.",IF(B{r}>=1.2,"Adequate; watch cash.","Tight: may struggle to pay short-term dues."))'),
        ("Quick ratio", lambda c: f"=IFERROR(({cur_a(c)}-{v('Inventory', c)})/{cur_l(c)},0)", "0.00", "1 or more", 'IF(B{r}>=1,"Can pay dues without selling stock.","Depends on selling stock to pay dues.")'),
        ("PROFITABILITY", None, None, "", ""),
        ("Gross margin %", lambda c: f"=IFERROR(({v('Revenue (net sales)', c)}-{v('Cost of goods sold', c)})/{v('Revenue (net sales)', c)},0)", PCT, "Industry specific", 'IF(B{r}>C{r},"Improving vs last year.","Falling vs last year: check input costs or pricing.")'),
        ("Net profit margin %", lambda c: f"=IFERROR({v('Net profit', c)}/{v('Revenue (net sales)', c)},0)", PCT, "10%+ is healthy", 'IF(B{r}>=0.1,"Healthy margin.",IF(B{r}>0,"Thin margin.","Loss-making."))'),
        ("Return on equity %", lambda c: f"=IFERROR({v('Net profit', c)}/{v(EQUITY, c)},0)", PCT, "15%+ is good", 'IF(B{r}>=0.15,"Good return for owners.","Modest return for owners.")'),
        ("Return on assets %", lambda c: f"=IFERROR({v('Net profit', c)}/{v('Total assets', c)},0)", PCT, "5%+ is good", 'IF(B{r}>=0.05,"Assets used well.","Assets earn little.")'),
        ("LEVERAGE", None, None, "", ""),
        ("Debt to equity", lambda c: f"=IFERROR(({v('Short-term borrowings', c)}+{v('Long-term borrowings', c)})/{v(EQUITY, c)},0)", "0.00", "Below 1.5", 'IF(B{r}<=1,"Low borrowing.",IF(B{r}<=2,"Moderate borrowing.","High borrowing: risky."))'),
        ("Interest cover (times)", lambda c: f"=IFERROR(({v('Net profit', c)}+{v('Tax', c)}+{v('Interest expense', c)})/{v('Interest expense', c)},0)", "0.0", "3 or more", 'IF(B{r}>=3,"Comfortably pays interest.","Interest is a burden.")'),
        ("EFFICIENCY", None, None, "", ""),
        ("Asset turnover (times)", lambda c: f"=IFERROR({v('Revenue (net sales)', c)}/{v('Total assets', c)},0)", "0.00", "Higher is better", 'IF(B{r}>C{r},"Using assets more efficiently.","Less efficient than last year.")'),
        ("Inventory days", lambda c: f"=IFERROR({v('Inventory', c)}/{v('Cost of goods sold', c)}*365,0)", "0", "Lower is better", 'IF(B{r}<C{r},"Stock moving faster.","Stock moving slower: cash tied up.")'),
        ("Debtor days", lambda c: f"=IFERROR({v('Trade receivables', c)}/{v('Revenue (net sales)', c)}*365,0)", "0", "Lower is better", 'IF(B{r}<C{r},"Collecting faster.","Collecting slower: chase customers.")'),
        ("Creditor days", lambda c: f"=IFERROR({v('Trade payables', c)}/{v('Cost of goods sold', c)}*365,0)", "0", "Balanced", 'IF(B{r}>C{r},"Taking longer to pay suppliers.","Paying suppliers faster.")'),
    ]
    for i, (n, f, fmt, rng_, read) in enumerate(ratios):
        r = 5 + i
        c1 = rt.cell(row=r, column=1, value=n)
        if f is None:
            c1.font = Font(bold=True, color=GREEN)
            continue
        c1.border = BORDER
        calc(rt.cell(row=r, column=2, value=f("B")), fmt)
        calc(rt.cell(row=r, column=3, value=f("C")), fmt)
        rt.cell(row=r, column=4, value=rng_).border = BORDER
        calc(rt.cell(row=r, column=5, value="=" + read.format(r=r)))
    add_dashboard(wb, f"{heading}: dashboard", [
        ("Current ratio", "=Ratios!B6", "0.00"), ("Quick ratio", "=Ratios!B7", "0.00"), ("Net profit margin", "=Ratios!B10", PCT), ("Return on equity", "=Ratios!B11", PCT),
        ("Debt to equity", "=Ratios!B14", "0.00"), ("Interest cover (times)", "=Ratios!B15", "0.0"), ("Debtor days", "=Ratios!B19", "0"), ("Inventory days", "=Ratios!B18", "0")],
        [dict(kind="bar", title="Profitability: this year vs last year", fmt=PCT, cats=["Gross margin", "Net margin", "Return on equity", "Return on assets"],
              series=[("This year", ["=Ratios!B9", "=Ratios!B10", "=Ratios!B11", "=Ratios!B12"]), ("Last year", ["=Ratios!C9", "=Ratios!C10", "=Ratios!C11", "=Ratios!C12"])]),
         dict(kind="bar", title="Working capital days", fmt="0", cats=["Inventory days", "Debtor days", "Creditor days"],
              series=[("This year", ["=Ratios!B18", "=Ratios!B19", "=Ratios!B20"]), ("Last year", ["=Ratios!C18", "=Ratios!C19", "=Ratios!C20"])])])
    start_sheet(wb, "Start here", heading, [
        "Inputs sheet: type two years of figures from the profit and loss account and balance sheet (examples are placeholders).",
        "Ratios sheet: ratios for both years calculate by themselves, with a plain-English reading for the latest year.",
        "Compare Year 1 with Year 2 to see the direction. A single year says little; trends matter.",
        "Ratios depend on the figures you type, and good ranges differ by industry. Treat them as signals to investigate, not final verdicts.",
    ])
    return wb


def projections(heading="3-year financial projections", years=3):
    wb = new_wb()
    a = wb.create_sheet("Assumptions")
    title(a, "Assumptions", "Peach cells are your assumptions. Change them and the projections update.")
    items = [("Year 1 revenue", 1200000, MONEY), ("Revenue growth per year", 0.35, "0%"), ("Cost of goods as % of revenue", 0.45, "0%"),
             ("Salaries (Year 1)", 360000, MONEY), ("Rent and utilities (Year 1)", 120000, MONEY), ("Marketing as % of revenue", 0.08, "0%"),
             ("Other expenses as % of revenue", 0.04, "0%"), ("Annual increase in salaries and rent", 0.08, "0%"), ("Income tax rate", 0.25, "0%"),
             ("Opening cash / funding", 500000, MONEY), ("Equipment spend in Year 1", 200000, MONEY), ("Depreciation per year", 0.15, "0%")]
    widths(a, [38, 18])
    for i, (n, v, f) in enumerate(items):
        a.cell(row=3 + i, column=1, value=n).font = Font(bold=True)
        inp(a.cell(row=3 + i, column=2, value=v), f)
    p = wb.create_sheet("Projections")
    p.sheet_view.showGridLines = False
    title(p, heading, "Calculated from the Assumptions sheet. Ask a CA or mentor to review before showing investors or banks.")
    head(p, 4, ["Line"] + [f"Year {i}" for i in range(1, years + 1)])
    widths(p, [30] + [16] * years)
    labels = ["Revenue", "Cost of goods sold", "Gross profit", "Salaries", "Rent and utilities", "Marketing", "Other expenses", "Depreciation",
              "Total operating costs", "Profit before tax", "Tax", "Net profit", "Net margin %", "Cash at end of year (simple)"]
    for i, l in enumerate(labels):
        p.cell(row=5 + i, column=1, value=l).font = Font(bold=l in ("Gross profit", "Net profit", "Revenue"))
    for y in range(years):
        c = col(2 + y)
        pc = col(1 + y)
        f = {
            5: "=Assumptions!$B$3" if y == 0 else f"={pc}5*(1+Assumptions!$B$4)",
            6: f"={c}5*Assumptions!$B$5", 7: f"={c}5-{c}6",
            8: "=Assumptions!$B$6" if y == 0 else f"={pc}8*(1+Assumptions!$B$10)",
            9: "=Assumptions!$B$7" if y == 0 else f"={pc}9*(1+Assumptions!$B$10)",
            10: f"={c}5*Assumptions!$B$8", 11: f"={c}5*Assumptions!$B$9", 12: "=Assumptions!$B$13*Assumptions!$B$14",
            13: f"=SUM({c}8:{c}12)", 14: f"={c}7-{c}13", 15: f"=MAX(0,{c}14)*Assumptions!$B$11", 16: f"={c}14-{c}15",
            17: f"=IFERROR({c}16/{c}5,0)",
            18: ("=Assumptions!$B$12-Assumptions!$B$13+" + f"{c}16+{c}12") if y == 0 else f"={pc}18+{c}16+{c}12",
        }
        for r, formula in f.items():
            cell = p.cell(row=r, column=2 + y, value=formula)
            calc(cell, PCT if r == 17 else MONEY, r in (7, 16))
    bar(p, "F4", "Revenue and net profit", Reference(p, min_col=2, max_col=1 + years, min_row=4), Reference(p, min_col=1, max_col=1 + years, min_row=5))
    from openpyxl.chart import Series
    ch = p._charts[-1]
    ch.series = []
    for rowno, name in ((5, "Revenue"), (16, "Net profit")):
        ch.series.append(Series(Reference(p, min_col=2, max_col=1 + years, min_row=rowno), title=name))
    ch.set_categories(Reference(p, min_col=2, max_col=1 + years, min_row=4))
    lastc = col(1 + years)
    add_dashboard(wb, f"{heading}: dashboard", [
        ("Year 1 revenue", "=Projections!B5", MONEY), (f"Year {years} revenue", f"=Projections!{lastc}5", MONEY),
        ("Year 1 net profit", "=Projections!B16", MONEY), (f"Year {years} net profit", f"=Projections!{lastc}16", MONEY),
        (f"Year {years} net margin", f"=Projections!{lastc}17", PCT), (f"Cash at end of year {years}", f"=Projections!{lastc}18", MONEY),
        ("Opening cash / funding", "=Assumptions!B12", MONEY), ("Revenue growth per year", "=Assumptions!B4", "0%")],
        [dict(kind="bar", zero=False, title="Revenue and net profit by year", cats=[f"Year {i}" for i in range(1, years + 1)],
              series=[("Revenue", [f"=Projections!{col(1 + i)}5" for i in range(1, years + 1)]), ("Net profit", [f"=Projections!{col(1 + i)}16" for i in range(1, years + 1)])]),
         dict(kind="line", title="Cash at end of year", cats=[f"Year {i}" for i in range(1, years + 1)],
              series=[("Cash", [f"=Projections!{col(1 + i)}18" for i in range(1, years + 1)])])])
    start_sheet(wb, "Start here", heading, [
        "Assumptions sheet: type your Year 1 revenue, growth, cost percentages, salaries, tax rate and funding. The values are examples.",
        "Projections sheet: revenue, costs, profit and cash for each year calculate automatically.",
        "Test a cautious, a likely and an ambitious case by changing growth and cost percentages.",
        "This is a planning model with simple assumptions. It does not replace professional advice, and the future will differ.",
    ])
    return wb


def startup_budget():
    wb = new_wb()
    ws = wb.create_sheet("Startup budget")
    ws.sheet_view.showGridLines = False
    title(ws, "Startup budget planning model", "Plan 12 months: revenue growth, costs, funding and cash runway.")
    a = [("Starting monthly revenue", 60000, MONEY), ("Monthly revenue growth", 0.12, "0%"), ("Cost of goods %", 0.40, "0%"),
         ("Opening cash (funding)", 700000, MONEY), ("One-time setup costs (month 1)", 150000, MONEY)]
    for i, (n, v, f) in enumerate(a):
        ws.cell(row=3 + i, column=1, value=n).font = Font(bold=True)
        inp(ws.cell(row=3 + i, column=2, value=v), f)
    head(ws, 9, ["Line"] + MONTHS + ["Total"])
    widths(ws, [30] + [11] * 12 + [14])
    ws.freeze_panes = "B10"
    fixed = [("Salaries and founders", 60000), ("Rent", 18000), ("Software and tools", 6000), ("Marketing", 15000), ("Other fixed costs", 8000)]
    ws["A10"] = "Revenue"
    ws["A11"] = "Cost of goods"
    ws["A12"] = "Gross profit"
    for m in range(12):
        c = col(2 + m)
        ws[f"{c}10"] = "=$B$3" if m == 0 else f"={col(1 + m)}10*(1+$B$4)"
        ws[f"{c}11"] = f"={c}10*$B$5"
        ws[f"{c}12"] = f"={c}10-{c}11"
        for r in (10, 11, 12):
            calc(ws[f"{c}{r}"], MONEY)
    for i, (n, v) in enumerate(fixed):
        r = 13 + i
        ws.cell(row=r, column=1, value=n).border = BORDER
        for m in range(12):
            inp(ws.cell(row=r, column=2 + m, value=v), MONEY)
    ws["A18"], ws["A19"], ws["A20"], ws["A21"], ws["A22"] = "Setup costs", "Total fixed costs", "Net cash flow", "Cash at end of month", "Runway status"
    for m in range(12):
        c = col(2 + m)
        ws[f"{c}18"] = "=$B$7" if m == 0 else 0
        ws[f"{c}19"] = f"=SUM({c}13:{c}17)+{c}18"
        ws[f"{c}20"] = f"={c}12-{c}19"
        ws[f"{c}21"] = f"=$B$6+{c}20" if m == 0 else f"={col(1 + m)}21+{c}20"
        ws[f"{c}22"] = f'=IF({c}21<0,"Out of cash",IF({c}20<0,"Burning","Profit"))'
        for r in (18, 19, 20, 21):
            calc(ws[f"{c}{r}"], MONEY, r == 21)
        calc(ws[f"{c}22"])
    for r in range(10, 13):
        calc(ws.cell(row=r, column=14, value=f"=SUM(B{r}:M{r})"), MONEY, True)
    ws.conditional_formatting.add("B22:M22", FormulaRule(formula=['B22="Out of cash"'], fill=PatternFill("solid", bgColor="FF9999", fgColor="FF9999")))
    ws["A24"] = "Months of cash left at current burn"
    ws["A24"].font = Font(bold=True)
    ws["B24"] = '=IFERROR(IF(AVERAGE(B20:M20)>=0,"Not burning",ROUNDDOWN($B$6/-AVERAGE(B20:M20),0)),"")'
    calc(ws["B24"], "0", True)
    bar(ws, "B27", "Cash at end of month", Reference(ws, min_col=2, max_col=13, min_row=9), Reference(ws, min_col=1, max_col=13, min_row=21), w=24, line=True)
    from openpyxl.chart import Series
    ch = ws._charts[-1]
    ch.series = []
    ch.series.append(Series(Reference(ws, min_col=2, max_col=13, min_row=21), title="Cash"))
    ch.set_categories(Reference(ws, min_col=2, max_col=13, min_row=9))
    sc = [col(2 + m) for m in range(12)]
    add_dashboard(wb, "Startup budget: dashboard", [
        ("Revenue (12 months)", "='Startup budget'!N10", MONEY), ("Gross profit (12 months)", "='Startup budget'!N12", MONEY),
        ("Cash at month 12", "='Startup budget'!M21", MONEY), ("Lowest cash balance", "=MIN('Startup budget'!B21:M21)", MONEY),
        ("Months of cash left", "='Startup budget'!B24", "0"), ("Months out of cash", '=COUNTIF(' + chr(39) + 'Startup budget' + chr(39) + '!B22:M22,"Out of cash")', "0"),
        ("Starting cash (funding)", "='Startup budget'!B6", MONEY), ("One-time setup costs", "='Startup budget'!B7", MONEY)],
        [dict(kind="line", title="Cash at the end of each month", cats=MONTHS, series=[("Cash", [f"='Startup budget'!{c}21" for c in sc])]),
         dict(kind="bar", title="Revenue vs fixed costs", cats=MONTHS, series=[("Revenue", [f"='Startup budget'!{c}10" for c in sc]), ("Fixed costs", [f"='Startup budget'!{c}19" for c in sc])])])
    start_sheet(wb, "Start here", "Startup budget planning model", [
        "Type starting revenue, monthly growth, cost of goods %, funding and one-time setup costs at the top.",
        "Edit the fixed-cost lines (salaries, rent, tools, marketing) by month.",
        "Read cash at the end of each month and the status row. Out of cash tells you the month you need more funding.",
        "Try a slower growth rate to see a cautious case. Investors and banks always ask for one.",
    ])
    return wb


def mis_report():
    wb = new_wb()
    ws = wb.create_sheet("MIS report")
    ws.sheet_view.showGridLines = False
    title(ws, "Monthly management report (MIS)", "One-page monthly report for owners and managers. Fill the peach cells each month.")
    ws["A3"], ws["B3"] = "Month", "January 2026"
    inp(ws["B3"])
    head(ws, 5, ["Key figure", "Actual", "Budget / target", "Last month", "vs Budget", "vs Last month"])
    widths(ws, [30, 16, 16, 16, 14, 14])
    rows = [("Revenue", 650000, 600000, 610000), ("Gross profit", 260000, 240000, 245000), ("Operating expenses", 180000, 175000, 172000),
            ("Net profit", 80000, 65000, 73000), ("Cash in bank", 420000, 400000, 380000), ("Receivables (money owed to you)", 310000, 250000, 290000),
            ("Payables (money you owe)", 190000, 200000, 185000), ("Closing stock", 280000, 260000, 270000)]
    for i, (n, a, b, c) in enumerate(rows):
        r = 6 + i
        ws.cell(row=r, column=1, value=n).border = BORDER
        for cc, v in ((2, a), (3, b), (4, c)):
            inp(ws.cell(row=r, column=cc, value=v), MONEY)
        calc(ws.cell(row=r, column=5, value=f"=IFERROR((B{r}-C{r})/C{r},0)"), PCT)
        calc(ws.cell(row=r, column=6, value=f"=IFERROR((B{r}-D{r})/D{r},0)"), PCT)
    ws["A15"], ws["B15"] = "Gross margin %", "=IFERROR(B7/B6,0)"
    ws["A16"], ws["B16"] = "Net margin %", "=IFERROR(B9/B6,0)"
    ws["A17"], ws["B17"] = "Debtor days", "=IFERROR(B11/B6*30,0)"
    for r, f in ((15, PCT), (16, PCT), (17, "0")):
        ws[f"A{r}"].font = Font(bold=True)
        calc(ws[f"B{r}"], f, True)
    ws["A19"] = "Highlights this month"
    ws["A19"].font = Font(bold=True, color=GREEN)
    ws["A25"] = "Problems and risks"
    ws["A25"].font = Font(bold=True, color=GREEN)
    ws["A31"] = "Actions for next month (what, who, by when)"
    ws["A31"].font = Font(bold=True, color=GREEN)
    for base in (20, 26, 32):
        for r in range(base, base + 4):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
            inp(ws.cell(row=r, column=1))
    bar(ws, "H5", "Actual vs budget", Reference(ws, min_col=1, min_row=6, max_row=9), Reference(ws, min_col=2, max_col=3, min_row=5, max_row=9))
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    add_dashboard(wb, "Monthly MIS: dashboard", [
        ("Revenue", "='MIS report'!B6", MONEY), ("Gross profit", "='MIS report'!B7", MONEY), ("Net profit", "='MIS report'!B9", MONEY), ("Cash in bank", "='MIS report'!B10", MONEY),
        ("Gross margin", "='MIS report'!B15", PCT), ("Net margin", "='MIS report'!B16", PCT), ("Receivables", "='MIS report'!B11", MONEY), ("Debtor days", "='MIS report'!B17", "0")],
        [dict(kind="bar", title="Actual vs budget", cats=[f"='MIS report'!A{6 + i}" for i in range(4)],
              series=[("Actual", [f"='MIS report'!B{6 + i}" for i in range(4)]), ("Budget", [f"='MIS report'!C{6 + i}" for i in range(4)])]),
         dict(kind="bar", title="This month vs last month", cats=[f"='MIS report'!A{6 + i}" for i in range(4)],
              series=[("This month", [f"='MIS report'!B{6 + i}" for i in range(4)]), ("Last month", [f"='MIS report'!D{6 + i}" for i in range(4)])])])
    start_sheet(wb, "Start here", "Monthly management report (MIS)", [
        "MIS report sheet: change the month and type actual, budget and last month's figures.",
        "Read the percentage columns to see where you are ahead or behind.",
        "Write highlights, problems and next actions in the notes boxes. This is what the owner reads first.",
        "Print or save as PDF (the sheet fits one page). Save a copy for each month.",
    ])
    return wb
