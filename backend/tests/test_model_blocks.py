"""Financial models that stack the statements on one sheet, each block with its own timeline row (year index, years or dates)."""

import datetime as dt
import io

from openpyxl import Workbook

from app.files.routing import suggest_statement_mapping, suggest_statements
from app.files.tabular import _timeline, parse_xlsx


def _put_block(ws, top: int, title: str, rows: list[tuple[str, list[float]]], timeline=(-1, 0, 1, 2), first_col: int = 6):
    ws.cell(top, 2, title)
    ws.cell(top + 2, 2, "All figures in USD thousands unless stated")
    for j, t in enumerate(timeline):
        ws.cell(top + 2, first_col + j, t)
    for i, (label, vals) in enumerate(rows):
        ws.cell(top + 4 + i, 2, label)
        for j, v in enumerate(vals):
            ws.cell(top + 4 + i, first_col + j, v)


def model_bytes(*, negative_costs: bool = True, with_dashboard: bool = True) -> bytes:
    sg = -1 if negative_costs else 1
    wb = Workbook()
    out = wb.active
    out.title = "Outputs"
    if with_dashboard:  # a dashboard sheet that repeats part of the model's income statement
        _put_block(out, 3, "Dashboard", [("Revenue", [1000, 1100, 1200, 1300]), ("Net Income", [100, 110, 120, 130]),
                                         ("Gross Profit", [400, 440, 480, 520]), ("EBITDA Margin", [0.3, 0.3, 0.3, 0.3])])
    m = wb.create_sheet("Model")
    _put_block(m, 3, "Income Statement", [
        ("Revenue", [1000, 1100, 1200, 1300]), ("COGS", [sg * 600, sg * 660, sg * 720, sg * 780]), ("Gross Profit", [400, 440, 480, 520]),
        ("Depreciation", [sg * 50, sg * 55, sg * 60, sg * 65]), ("EBIT", [350, 385, 420, 455]), ("Interest Expense", [sg * 20, sg * 15, sg * 10, sg * 5]),
        ("Net Income", [100, 110, 120, 130]), ("Total Tax", [sg * 30, sg * 33, sg * 36, sg * 39])])
    _put_block(m, 20, "Balance Sheet", [
        ("Cash", [100, 120, 140, 160]), ("Accounts Receivable", [150, 160, 170, 180]), ("Total Current Assets", [250, 280, 310, 340]),
        ("Total Assets", [1000, 1100, 1200, 1300]), ("Accounts Payable", [90, 95, 100, 105]), ("Revolving Credit Line", [40, 20, 0, 0]),
        ("Long-Term Debt", [300, 250, 200, 150]), ("Total Liabilities", [500, 520, 540, 560]), ("Total Shareholders' Equity", [500, 580, 660, 740])])
    _put_block(m, 40, "Cash Flow Statement", [
        ("CASH FROM OPERATING", []), ("Net Income", [100, 110, 120, 130]), ("Subtotal", [200, 210, 220, 230]),
        ("CASH FROM INVESTING", []), ("Capital Expenditure", [-80, -85, -90, -95]), ("Subtotal", [-80, -85, -90, -95]),
        ("CASH FROM FINANCING", []), ("Dividends", [-50, -60, -70, -80]), ("Subtotal", [-50, -60, -70, -80]),
        ("CASH BALANCE", []), ("Beginning of the Year", [10, 80, 145, 205]), ("Increase / (Decrease)", [70, 65, 60, 55]),
        ("End of the Year", [80, 145, 205, 260])])
    _put_block(m, 62, "Depreciation Schedule", [  # a schedule, not a statement: its lines must not leak into the statements
        ("Cash", [9, 9, 9, 9]), ("Opening balance", [1, 2, 3, 4]), ("Additions", [5, 5, 5, 5]), ("Revolving Credit Line", [77, 77, 77, 77])])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def sheets_of(data: bytes):
    return {s["name"]: s for s in parse_xlsx(data)["sheets"]}


def test_stacked_blocks_become_named_statement_sheets():
    sheets = sheets_of(model_bytes())
    assert "Model" not in sheets  # the combined sheet is replaced by its blocks
    for name, kind in (("Model · Income Statement", "income"), ("Model · Balance Sheet", "balance"), ("Model · Cash Flow Statement", "cashflow")):
        assert sheets[name]["section"]["type"] == kind
    assert sheets["Model · Depreciation Schedule"]["section"]["type"] is None
    inc = sheets["Model · Income Statement"]
    assert [c["name"] for c in inc["columns"] if c["dtype"] == "number"] == ["Year -1", "Year 0", "Year 1", "Year 2"]
    assert inc["preview"]["first_row_number"] == 3 and inc["header_row"] == 5
    assert any("model year numbers" in w for w in inc["warnings"])


def test_each_block_keeps_its_own_cell_references():
    sheets = sheets_of(model_bytes())
    rev = next(s for s in sheets["Model · Income Statement"]["series"] if s["label"] == "Revenue")
    assert rev["refs"][0] == "F7" and rev["refs"][-1] == "I7"
    cash = next(s for s in sheets["Model · Balance Sheet"]["series"] if s["label"] == "Cash")
    assert cash["refs"][0] == "F24"


def test_statements_use_the_year_periods_and_skip_schedules():
    sts = suggest_statements(list(sheets_of(model_bytes()).values()), "m.xlsx")
    assert {s["sheet"] for s in sts} == {"Model · Income Statement", "Model · Balance Sheet", "Model · Cash Flow Statement"}
    assert all(s["periods"] == ["Year -1", "Year 0", "Year 1", "Year 2"] for s in sts)


def test_the_dashboard_that_repeats_the_income_statement_is_dropped():
    sts = suggest_statements(list(sheets_of(model_bytes()).values()), "m.xlsx")
    assert [s["sheet"] for s in sts if s["statement"] == "income"] == ["Model · Income Statement"]
    kept = suggest_statements(list(sheets_of(model_bytes(with_dashboard=False)).values()), "m.xlsx")
    assert [s["sheet"] for s in kept if s["statement"] == "income"] == ["Model · Income Statement"]


def test_costs_shown_as_negatives_are_read_as_positive_costs_and_say_so():
    sts = suggest_statements(list(sheets_of(model_bytes()).values()), "m.xlsx")
    inc = next(s for s in sts if s["statement"] == "income")
    by = {l["key"]: l for l in inc["lines"] if l["key"]}
    assert by["cogs"]["values"] == [600, 660, 720, 780] and "sign reversed" in by["cogs"]["source"]
    assert by["interest_expense"]["values"] == [20, 15, 10, 5] and by["depreciation_amortization"]["values"][0] == 50
    assert by["revenue"]["values"] == [1000, 1100, 1200, 1300] and "sign reversed" not in by["revenue"]["source"]
    m = {x["item"]: x for x in suggest_statement_mapping(list(sheets_of(model_bytes()).values()), "m.xlsx")}
    assert m["cogs"]["value"] == 780 and "sign reversed" in m["cogs"]["source_label"]


def test_costs_already_positive_are_left_alone():
    sts = suggest_statements(list(sheets_of(model_bytes(negative_costs=False)).values()), "m.xlsx")
    inc = next(s for s in sts if s["statement"] == "income")
    cogs = next(l for l in inc["lines"] if l["key"] == "cogs")
    assert cogs["values"] == [600, 660, 720, 780] and "sign reversed" not in (cogs["source"] or "")


def test_mapping_comes_from_the_statements_not_from_a_schedule():
    m = {x["item"]: x for x in suggest_statement_mapping(list(sheets_of(model_bytes()).values()), "m.xlsx")}
    assert m["cash"]["value"] == 160 and m["cash"]["period"] == "Year 2"  # the balance sheet, not the schedule's 9
    assert m["revenue"]["value"] == 1300


def test_a_revolving_credit_line_counts_as_debt():
    m = {x["item"]: x for x in suggest_statement_mapping(list(sheets_of(model_bytes()).values()), "m.xlsx")}
    assert m["total_debt"]["value"] == 150 and m["total_debt"]["prior_value"] == 200  # 0 + 150, 0 + 200
    bs = next(s for s in suggest_statements(list(sheets_of(model_bytes()).values()), "m.xlsx") if s["statement"] == "balance")
    debt = next(l for l in bs["lines"] if l["key"] == "total_debt")
    assert debt["values"] == [340, 270, 200, 150] and "Revolving Credit Line" in debt["label"]


def test_a_sheet_with_one_timeline_is_not_split_but_gets_its_period_headers():
    wb = Workbook()
    ws = wb.active
    ws.title = "Fin"
    _put_block(ws, 3, "Summary", [("Revenue", [10, 12, 14, 16]), ("Net Income", [1, 2, 3, 4]), ("Total Assets", [50, 55, 60, 65])])
    sheet = parse_xlsx(_save(wb))["sheets"][0]
    assert sheet["name"] == "Fin" and "section" not in sheet
    assert [c["name"] for c in sheet["columns"] if c["dtype"] == "number"] == ["Year -1", "Year 0", "Year 1", "Year 2"]


def _save(wb) -> bytes:
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_timeline_rows_are_recognised_only_when_every_number_belongs_to_the_sequence():
    assert _timeline([None, "x", -2, -1, 0, 1, 2])[0] == "index"
    assert _timeline(["", 2023, 2024, 2025, 2026])[1] == {1: "2023", 2: "2024", 3: "2025", 4: "2026"}
    assert _timeline([dt.datetime(2024, 3, 31), dt.datetime(2025, 3, 31), dt.datetime(2026, 3, 31)])[1][1] == "Mar 2025"
    assert _timeline(["Revenue", 10, 12, 15, 19]) is None  # ordinary figures
    assert _timeline([1, 2, 3]) is None  # too short
    assert _timeline(["Revenue", 1, 2, 3, 4, 900]) is None  # one stray number breaks it


def test_generic_cash_flow_labels_take_their_meaning_from_the_heading_above():
    sts = suggest_statements(list(sheets_of(model_bytes()).values()), "m.xlsx")
    cf = next(s for s in sts if s["statement"] == "cashflow")
    by = {l["key"]: l for l in cf["lines"] if l["key"]}
    assert by["operating_cash_flow"]["values"] == [200, 210, 220, 230] and by["operating_cash_flow"]["label"] == "Subtotal (cash from operating)"
    assert by["investing_cash_flow"]["values"] == [-80, -85, -90, -95]
    assert by["financing_cash_flow"]["values"] == [-50, -60, -70, -80]
    assert by["beginning_cash"]["values"][0] == 10 and by["net_change_in_cash"]["values"][0] == 70 and by["ending_cash"]["values"][-1] == 260
    assert by["capex"]["values"][0] == -80  # an outflow stays negative in a cash flow statement


def test_headings_are_recorded_for_each_block():
    cf = sheets_of(model_bytes())["Model · Cash Flow Statement"]
    assert [h["text"] for h in cf["headings"]] == ["CASH FROM OPERATING", "CASH FROM INVESTING", "CASH FROM FINANCING", "CASH BALANCE"]
