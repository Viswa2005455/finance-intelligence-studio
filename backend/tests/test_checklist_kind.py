"""The month-end close checklist is saved like any other model, with versions."""


def test_a_close_checklist_can_be_saved_listed_and_versioned(client):
    data = {"month": "2026-11", "items": [{"id": "bank", "group": "Cash and bank", "label": "Reconcile", "done": True, "owner": "Asha", "note": ""}]}
    made = client.post("/api/saved", json={"kind": "checklist", "name": "Nov 2026 close", "project_id": None, "data": data}).json()
    assert made["kind"] == "checklist" and made["latest_version"] == 1
    listed = client.get("/api/saved?kind=checklist").json()["items"]
    assert [i["name"] for i in listed] == ["Nov 2026 close"]
    data["items"][0]["note"] = "Axis matched"
    v2 = client.put(f"/api/saved/{made['id']}", json={"data": data, "note": "after review"}).json()
    assert v2["latest_version"] == 2
    assert client.get(f"/api/saved/{made['id']}/versions/1").json()["data"]["items"][0]["note"] == ""


def test_unknown_kinds_are_still_refused(client):
    assert client.post("/api/saved", json={"kind": "not-a-kind", "name": "x", "project_id": None, "data": {}}).status_code == 422
