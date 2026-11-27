import io

from openpyxl import load_workbook

from app.reports import workbook


def test_workbook_flattens_models_and_defuses_formulas():
    data = workbook.build([{"kind": "dcf", "name": "Base case", "version": 3, "updated_at": "2026-11-01T10:00:00",
                            "data": {"wacc": 0.11, "revenue_growth": [0.1, 0.09], "note": "=HYPERLINK(\"http://x\")", "debt": {"bank": 300}}}])
    wb = load_workbook(io.BytesIO(data))
    assert wb.sheetnames == ["Index", "dcf Base case"]
    ws = wb["dcf Base case"]
    rows = {r[0].value: [c.value for c in r[1:] if c.value is not None] for r in ws.iter_rows(min_row=3)}
    assert rows["wacc"] == [0.11] and rows["revenue_growth"] == [0.1, 0.09] and rows["debt.bank"] == [300]
    assert rows["note"][0].startswith("'=")  # stored as text, not a formula
    assert wb["Index"]["C2"].value == 3


def test_sheet_names_are_unique_and_legal():
    items = [{"kind": "dcf", "name": "A/B:*?", "version": 1, "updated_at": "x", "data": {}}] * 3
    wb = load_workbook(io.BytesIO(workbook.build(items)))
    assert len(set(n.lower() for n in wb.sheetnames)) == 4 and all(len(n) <= 31 for n in wb.sheetnames)


def test_empty_account_still_gives_a_workbook():
    wb = load_workbook(io.BytesIO(workbook.build([])))
    assert wb.sheetnames == ["Index"]


def test_endpoints(client):
    made = client.post("/api/saved", json={"kind": "dcf", "name": "My DCF", "data": {"wacc": 0.1, "revenue_growth": [0.1, 0.08]}})
    assert made.status_code == 201, made.text
    x = client.get("/api/account/export.xlsx")
    assert x.status_code == 200 and "spreadsheetml" in x.headers["content-type"]
    wb = load_workbook(io.BytesIO(x.content))
    assert any(row[1].value == "My DCF" for row in wb["Index"].iter_rows(min_row=2))
    events = client.get("/api/account/activity?limit=20").json()["events"]
    actions = [e["action"] for e in events]
    assert "model.saved" in actions and "account.exported_xlsx" in actions
    assert actions.index("account.exported_xlsx") < actions.index("model.saved")  # newest first


def test_handover_zip_holds_workbook_json_files_and_readme(client):
    import zipfile
    client.post("/api/saved", json={"kind": "dcf", "name": "For my accountant", "data": {"wacc": 0.1}})
    z = client.get("/api/account/handover.zip")
    assert z.status_code == 200 and z.headers["content-type"] == "application/zip"
    names = zipfile.ZipFile(io.BytesIO(z.content)).namelist()
    assert {"saved-models.xlsx", "everything.json", "README.txt"} <= set(names)
    readme = zipfile.ZipFile(io.BytesIO(z.content)).read("README.txt").decode()
    assert "Saved models: 1" in readme and "not audited" in readme
    assert any(e["action"] == "account.handover" for e in client.get("/api/account/activity").json()["events"])
