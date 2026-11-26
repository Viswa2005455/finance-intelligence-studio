"""Messy and unstructured inputs: the upload engine must never crash, must say plainly what it could and
could not read, and must still find the numbers in files that are not neat tables.

Each case posts one file the way the Upload page does and checks (1) no server error, (2) a clear outcome
(read, or refused with a reason), and (3) where numbers are present, that the right ones were found.
"""

import io
import json
import zipfile

import pytest
from openpyxl import Workbook

CASES: dict[str, tuple[str, bytes]] = {}


def case(name: str, filename: str, data: bytes | str):
    CASES[name] = (filename, data.encode("utf-8") if isinstance(data, str) else data)


# --- delimited text with junk around the data ------------------------------------------------------
case("csv_junk_rows", "report.csv", 'ACME LTD\nProfit and loss statement\n(Rs in lakh)\n\n"Line item","FY2024","FY2025"\n"Revenue","11,000","12,480"\n"Cost of goods sold","(7,260)","(8,360)"\n"Net profit","1,150","1,380"\n\nTotal,,\nPrepared by finance team\n')
case("csv_semicolon_decimal_comma", "eu.csv", "Posten;2024;2025\nUmsatz;11000,50;12480,75\nGewinn;1150,25;1380,10\n")
case("tsv", "data.tsv", "Item\t2024\t2025\nRevenue\t11000\t12480\nNet income\t1150\t1380\n")
case("csv_percent_currency", "mixed.csv", "Metric,FY24,FY25\nRevenue,₹11,000,₹12,480\nMargin,10.5%,11.1%\nHeadcount,120,135\n")
case("csv_utf16_bom", "utf16.csv", "Item,2024,2025\nRevenue,11000,12480\n".encode("utf-16"))
case("csv_latin1", "latin1.csv", "Ítem,2024,2025\nRevenue,11000,12480\nGastos café,300,310\n".encode("latin-1"))
case("dat_csv_inside", "export.dat", "Item,2024,2025\nRevenue,11000,12480\nCOGS,7260,8360\n")
case("ragged_csv", "ragged.csv", "a,b,c\n1,2\n3,4,5,6\n,,\nx\n")
case("only_headers_csv", "headers.csv", "Item,2024,2025\n")
case("numbers_only_csv", "nums.csv", "1,2,3\n4,5,6\n7,8,9\n")

# --- free text and logs ----------------------------------------------------------------------------
case("notes_txt", "notes.txt", "Meeting notes 12 March\nRevenue for FY25 was Rs 12,480 lakh, up from 11,000 lakh in FY24.\nNet profit rose to 1,380 (from 1,150).\nNeed to chase Sharma about the invoice of 45,000.\n")
case("log_file", "app.log", "2025-03-01 10:00:01 INFO payment ok amount=1500.50\n2025-03-01 10:00:05 ERROR payment failed amount=200\n2025-03-02 09:12:11 INFO payment ok amount=999\n")
case("markdown_table", "summary.md", "# Results\n\n| Item | 2024 | 2025 |\n|---|---|---|\n| Revenue | 11000 | 12480 |\n| Net income | 1150 | 1380 |\n")
case("html_table", "page.html", "<html><body><h1>Results</h1><table><tr><th>Item</th><th>2024</th><th>2025</th></tr><tr><td>Revenue</td><td>11,000</td><td>12,480</td></tr></table></body></html>")
case("rtf_like_text", "memo.rtf", "{\\rtf1\\ansi Revenue was 12,480 in FY25.}")

# --- structured data -------------------------------------------------------------------------------
case("json_nested", "data.json", json.dumps({"company": "ACME", "years": [{"year": 2024, "revenue": 11000, "profit": 1150}, {"year": 2025, "revenue": 12480, "profit": 1380}], "meta": {"units": "lakh"}}))
case("json_lines", "events.jsonl", '{"d":"2025-01-01","amt":100}\n{"d":"2025-01-02","amt":250}\n')
case("json_broken", "bad.json", '{"a": 1, "b": [1,2,')
case("xml_doc", "data.xml", "<report><item name='Revenue'><y2024>11000</y2024><y2025>12480</y2025></item></report>")
case("yaml_doc", "data.yaml", "company: ACME\nrevenue:\n  2024: 11000\n  2025: 12480\n")
case("toml_doc", "data.toml", "[company]\nname = 'ACME'\nrevenue = 12480\n")

# --- code and notebooks ----------------------------------------------------------------------------
case("python_code", "calc.py", "revenue = 12480\ncogs = 8360\nprint(revenue - cogs)\n")
case("sql_code", "q.sql", "SELECT region, SUM(amount) FROM sales GROUP BY region;\n")
case("notebook", "nb.ipynb", json.dumps({"cells": [{"cell_type": "code", "source": ["x = 1\n", "print(x)"], "outputs": [], "execution_count": None, "metadata": {}}, {"cell_type": "markdown", "source": ["# Title"], "metadata": {}}], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}))


def _xlsx(build) -> bytes:
    wb = Workbook()
    build(wb)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _messy_workbook(wb):
    ws = wb.active
    ws.title = "Summary"
    ws["A1"] = "ACME LTD - Consolidated"
    ws.merge_cells("A1:D1")
    ws["A3"], ws["B3"], ws["C3"] = "Particulars", "FY2024", "FY2025"
    ws["A4"], ws["B4"], ws["C4"] = "Revenue", "11,000", "12,480"       # numbers stored as text
    ws["A5"], ws["B5"], ws["C5"] = "Net profit", 1150, 1380
    ws["A6"], ws["B6"], ws["C6"] = "Margin", "=B5/B4", "=C5/C4"        # formulas, one over text
    ws.row_dimensions[5].hidden = True
    second = wb.create_sheet("Notes")
    second["A1"] = "Free text only, no numbers here"
    wb.create_sheet("Empty")


case("xlsx_messy", "messy.xlsx", _xlsx(_messy_workbook))
case("xlsx_garbage_bytes", "fake.xlsx", b"\x00\x01\x02 this is not a workbook \xff\xfe")
case("empty_file", "empty.csv", b"")
case("xlsx_empty_workbook", "blank.xlsx", _xlsx(lambda wb: None))


def _zip_of_csv() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("data/a.csv", "Item,2024\nRevenue,11000\n")
        z.writestr("readme.txt", "hello")
    return buf.getvalue()


case("zip_with_csv", "bundle.zip", _zip_of_csv())
case("unknown_binary", "blob.bin", bytes(range(256)) * 4)
case("no_extension", "README", "Revenue 12480 and profit 1380\n")


def _docx_with_table() -> bytes:
    from docx import Document

    d = Document()
    d.add_paragraph("Annual summary. Revenue grew in FY25.")
    t = d.add_table(rows=3, cols=3)
    for r, row in enumerate([["Item", "2024", "2025"], ["Revenue", "11,000", "12,480"], ["Net income", "1,150", "1,380"]]):
        for c, v in enumerate(row):
            t.cell(r, c).text = v
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


case("docx_table", "report.docx", _docx_with_table())


def post(client, name: str, data: bytes):
    r = client.post("/api/uploads", files=[("files", (name, data))])
    return r


@pytest.mark.parametrize("key", list(CASES))
def test_never_a_server_error_and_always_a_clear_outcome(client, key):
    name, data = CASES[key]
    r = post(client, name, data)
    assert r.status_code < 500, f"{key}: {r.status_code} {r.text[:300]}"
    body = r.json()
    results = body.get("results") or []
    assert results, f"{key}: no result entry: {body}"
    res = results[0]
    if res["ok"]:
        up = res["upload"]
        assert up["summary"], f"{key}: no summary"
        assert up["analysis"] is not None
    else:
        # A refusal must give the person a reason they can act on.
        assert res.get("error") and len(res["error"]) > 10, f"{key}: refusal without a reason: {res}"


# ---------------------------------------------------------------------------------------------------
# What was found. Hand-checked values: every expected number is written in the case above.
# ---------------------------------------------------------------------------------------------------
def upload(client, key):
    name, data = CASES[key]
    res = client.post("/api/uploads", files=[("files", (name, data))]).json()["results"][0]
    assert res["ok"], res
    return res["upload"]


def series_of(up) -> dict:
    out = {}
    for sh in (up["analysis"] or {}).get("sheets", []) or []:
        for s in sh.get("series", []) or []:
            if s["orientation"] == "row":
                out.setdefault(s["label"], s)
    return out


def warnings_of(up) -> str:
    return " ".join(w for sh in (up["analysis"] or {}).get("sheets", []) or [] for w in sh.get("warnings", []))


def test_thousands_commas_and_brackets_are_read_correctly(client):
    s = series_of(upload(client, "csv_junk_rows"))
    assert s["Revenue"]["values"] == [11000, 12480]
    assert s["Cost of goods sold"]["values"] == [-7260, -8360]  # (7,260) is a negative
    assert "decimal comma" not in warnings_of(upload(client, "csv_junk_rows"))


def test_decimal_comma_files_are_not_read_as_thousands(client):
    up = upload(client, "csv_semicolon_decimal_comma")
    s = series_of(up)
    assert s["Umsatz"]["values"] == [11000.50, 12480.75]  # was 1,100,050 and 1,248,075 before the fix
    assert s["Gewinn"]["values"] == [1150.25, 1380.10]
    assert "decimal comma" in warnings_of(up)


def test_year_header_rows_become_periods(client):
    for key in ("tsv", "csv_utf16_bom", "dat_csv_inside", "docx_table"):
        up = upload(client, key)
        s = series_of(up)
        assert s["Revenue"]["values"] == [11000, 12480], key
        assert s["Revenue"]["period_labels"] == ["2024", "2025"], key


def test_windows_encoded_text_keeps_its_accents_and_warns(client):
    up = upload(client, "csv_latin1")
    assert "Gastos café" in series_of(up)
    assert "Windows-1252" in warnings_of(up)


def test_unquoted_thousands_commas_are_flagged_not_trusted_silently(client):
    assert "more columns" in warnings_of(upload(client, "csv_percent_currency"))
    assert "more columns" in warnings_of(upload(client, "ragged_csv"))


def test_numbers_in_sentences_keep_their_line(client):
    s = series_of(upload(client, "notes_txt"))
    # The clause "Revenue for FY25 was Rs 12,480 lakh" and "up from 11,000 lakh in FY24" each name their period,
    # so the values are placed by period and come out oldest first, with the line they came from.
    assert s["Revenue"]["values"] == [11000, 12480] and s["Revenue"]["period_labels"] == ["FY24", "FY25"]
    assert set(s["Revenue"]["refs"]) == {"line 2"}
    assert s["Net profit"]["values"] == [1380, 1150]  # no period named: listed in the order written, and said so
    assert not any("nvoice" in k or "Need" in k for k in s), "an unnamed 45,000 must not be invented into a line item"


def test_log_values_group_by_name_and_dates_are_not_amounts(client):
    s = series_of(upload(client, "log_file"))
    assert s["Amount"]["values"] == [1500.50, 200, 999] and s["Amount"]["refs"] == ["line 1", "line 2", "line 3"]
    assert all("2025" not in k for k in s)


@pytest.mark.parametrize("key", ["markdown_table", "html_table", "json_nested", "xml_doc", "yaml_doc"])
def test_tables_inside_other_formats_are_found(client, key):
    s = series_of(upload(client, key))
    label = next(k for k in s if k.lower() == "revenue")
    assert s[label]["values"] == [11000, 12480]


def test_json_lines_with_enough_rows_give_a_series(client):
    rows = "\n".join(json.dumps({"d": f"2025-01-{i:02d}", "amt": 100 + i}) for i in range(1, 8))
    res = client.post("/api/uploads", files=[("files", ("events.jsonl", rows.encode()))]).json()["results"][0]
    assert res["ok"]
    cols = {s["label"]: s["values"] for sh in res["upload"]["analysis"]["sheets"] for s in sh["series"]}
    assert cols["amt"] == [101 + i for i in range(7)]


def test_unknown_extensions_are_read_by_content_but_programs_are_refused(client):
    assert series_of(upload(client, "dat_csv_inside"))["COGS"]["values"] == [7260, 8360]
    assert upload(client, "no_extension")["analysis"]["kind"] == "document"
    r = client.post("/api/uploads", files=[("files", ("blob.bin", bytes(range(256)) * 4))]).json()["results"][0]
    assert not r["ok"] and "never accepted" in r["error"]
    r = client.post("/api/uploads", files=[("files", ("run.exe", b"Revenue,2024\nx,1\n"))]).json()["results"][0]
    assert not r["ok"] and "never accepted" in r["error"]  # text-looking content does not make a program acceptable
    r = client.post("/api/uploads", files=[("files", ("photo.png", b"\x89PNG\r\n\x1a\n" + bytes(300)))]).json()["results"][0]
    assert not r["ok"] and r["error"]


def test_hidden_rows_text_numbers_and_formulas_in_workbooks(client):
    s = series_of(upload(client, "xlsx_messy"))
    assert s["Revenue"]["values"] == [11000, 12480]       # numbers stored as text
    assert s["Margin"]["values"] == pytest.approx([1150 / 11000, 1380 / 12480])  # formulas without saved results are calculated


def test_sentences_that_name_their_periods_feed_the_statement_engines(client):
    text = "Revenue in FY24 was 11,000 and in FY25 it was 12,480.\nNet profit in FY24 was 1,150 and in FY25 it was 1,380.\n"
    res = client.post("/api/uploads", files=[("files", ("summary.txt", text.encode()))]).json()["results"][0]
    st = res["upload"]["statements"][0]
    assert st["periods"] == ["FY24", "FY25"]
    by_key = {l["key"]: l["values"] for l in st["lines"]}
    assert by_key["revenue"] == [11000, 12480] and by_key["net_income"] == [1150, 1380]
