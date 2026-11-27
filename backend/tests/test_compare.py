"""Comparing two uploads: matched lines ranked by movement, lines in only one file listed, other users' files refused."""

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


def up(client, name, rows):
    res = client.post("/api/uploads", files=[("files", (name, workbook(rows)))]).json()["results"][0]
    assert res["ok"], res
    return res["upload"]["id"]


def test_lines_are_matched_ranked_and_the_unmatched_are_listed(client):
    older = up(client, "q1.xlsx", [["Item", "Q1", "Q2"], ["Revenue", 1000, 1100], ["Net income", 100, 110], ["Marketing", 50, 50], ["Old line", 5, 5]])
    newer = up(client, "q2.xlsx", [["Item", "Q3", "Q4"], ["Revenue", 1200, 1210], ["Net income", 120, 180], ["Marketing", 60, 50], ["New line", 9, 9]])
    r = client.post("/api/analysis/compare", json={"older_id": older, "newer_id": newer}).json()
    assert r["matched"] == 3
    by = {x["label"]: x for x in r["rows"]}
    # Hand check: net income 110 -> 180 is +63.6%; revenue 1100 -> 1210 is +10%; marketing 50 -> 50 is 0%.
    assert round(by["Net income"]["change_pct"], 1) == 63.6 and by["Net income"]["moved"] is True
    assert round(by["Revenue"]["change_pct"], 1) == 10.0 and by["Revenue"]["moved"] is True
    assert by["Marketing"]["change"] == 0 and by["Marketing"]["moved"] is False
    assert [x["label"] for x in r["rows"]][0] == "Net income"  # biggest mover first
    assert r["only_in_older"] == ["Old line"] and r["only_in_newer"] == ["New line"]
    assert "2 moved" in r["headline"] and by["Net income"]["newer_ref"] == "C3"


def test_a_zero_starting_value_has_no_percentage(client):
    a = up(client, "a.xlsx", [["Item", "Y1", "Y2"], ["Grants", 0, 0], ["Revenue", 10, 20]])
    b = up(client, "b.xlsx", [["Item", "Y3", "Y4"], ["Grants", 5, 5], ["Revenue", 20, 20]])
    rows = {x["label"]: x for x in client.post("/api/analysis/compare", json={"older_id": a, "newer_id": b}).json()["rows"]}
    assert rows["Grants"]["change_pct"] is None and rows["Grants"]["change"] == 5


def test_same_file_twice_and_missing_files_are_refused(client):
    a = up(client, "a.xlsx", [["Item", "Y1", "Y2"], ["Revenue", 10, 20]])
    assert client.post("/api/analysis/compare", json={"older_id": a, "newer_id": a}).status_code == 422
    assert client.post("/api/analysis/compare", json={"older_id": a, "newer_id": "0" * 32}).status_code == 404


def test_one_user_cannot_compare_another_users_files(client, anon_client):
    from tests.conftest import register
    mine = up(client, "mine.xlsx", [["Item", "Y1", "Y2"], ["Revenue", 10, 20]])
    anon_client.post("/api/auth/logout")
    register(anon_client, email="other@example.com", name="Other")
    theirs = up(anon_client, "theirs.xlsx", [["Item", "Y1", "Y2"], ["Revenue", 10, 20]])
    r = anon_client.post("/api/analysis/compare", json={"older_id": theirs, "newer_id": mine})
    assert r.status_code == 404
