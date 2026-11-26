"""Upload oddity checks: real problems are flagged, a normal file produces nothing."""

import io

from openpyxl import Workbook


def workbook(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def upload(client, rows, name="t.xlsx"):
    res = client.post("/api/uploads", files=[("files", (name, workbook(rows)))]).json()["results"][0]
    assert res["ok"], res
    return res["upload"]["analysis"].get("oddities", [])


def titles(found):
    return [f["title"] for f in found]


def test_a_clean_statement_has_no_findings(client):
    found = upload(client, [["Item", "FY2023", "FY2024", "FY2025"], ["Revenue", 1000, 1100, 1210], ["Cost of goods sold", 600, 650, 700],
                            ["Gross profit", 400, 450, 510], ["Net income", 90, 100, 120]])
    assert found == []


def test_units_mixed_in_one_period_are_flagged_with_the_cell(client):
    found = upload(client, [["Item", "FY2023", "FY2024", "FY2025"], ["Revenue", 1000, 1100, 1210000], ["Net income", 90, 100, 120]])
    f = next(x for x in found if "factor of 500" in x["title"])
    assert "FY2025" in f["title"] and f["severity"] == "high" and "D2" in f["where"]


def test_gross_profit_that_does_not_equal_revenue_minus_cost_is_flagged(client):
    found = upload(client, [["Item", "FY2024", "FY2025"], ["Revenue", 1000, 1200], ["Cost of goods sold", 600, 700], ["Gross profit", 400, 560]])
    assert any("Gross profit" in t and "FY2025" in t for t in titles(found))


def test_balance_sheet_that_does_not_balance_is_flagged(client):
    found = upload(client, [["Item", "FY2024", "FY2025"], ["Total assets", 5000, 5600], ["Total liabilities", 3000, 3300], ["Total equity", 2000, 2000]])
    assert any("balance sheet" in t.lower() and "FY2025" in t for t in titles(found))


def test_duplicate_period_headings_are_flagged(client):
    found = upload(client, [["Item", "FY2024", "FY2024", "FY2025"], ["Revenue", 1000, 1100, 1210], ["Net income", 90, 100, 120]])
    assert any("appears more than once" in t for t in titles(found))


def test_one_sign_flip_and_a_percentage_above_100(client):
    found = upload(client, [["Item", "FY2022", "FY2023", "FY2024", "FY2025"], ["Interest paid", -50, -55, 60, -58], ["Net margin", 12, 13, 150, 14]])
    t = titles(found)
    assert any("opposite sign in FY2024" in x for x in t)
    assert any("percentage above 100" in x for x in t)


def test_a_row_copied_across_every_period_is_noted(client):
    found = upload(client, [["Item", "FY2022", "FY2023", "FY2024", "FY2025"], ["Revenue", 500, 500, 500, 500], ["Net income", 10, 12, 15, 18]])
    assert any("same figure in every period" in x["title"] and x["severity"] == "info" for x in found)
