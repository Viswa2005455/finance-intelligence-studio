"""The in-app feedback button."""

from sqlalchemy import func, select

from app.db.models import Feedback
from app.db.session import session_factory


def stored():
    with session_factory()() as db:
        return db.scalars(select(Feedback)).all()


def test_signed_in_users_can_send_a_note_with_details(client):
    r = client.post("/api/feedback", json={"kind": "problem", "message": "The DCF chart did not load", "page": "/dcf", "details": "Status: 500\nRequest: POST /api/finance/dcf"})
    assert r.status_code == 201 and r.json() == {"sent": True}
    [n] = stored()
    assert n.kind == "problem" and n.page == "/dcf" and "Status: 500" in n.details and n.user_id is not None


def test_visitors_cannot_send_feedback(anon_client):
    assert anon_client.post("/api/feedback", json={"message": "hello there"}).status_code == 401


def test_bad_notes_are_refused(client):
    assert client.post("/api/feedback", json={"message": "x"}).status_code == 422
    assert client.post("/api/feedback", json={"message": "a" * 2001}).status_code == 422
    assert client.post("/api/feedback", json={"message": "fine message", "kind": "rant"}).status_code == 422
    assert stored() == []


def test_feedback_is_rate_limited(client):
    codes = [client.post("/api/feedback", json={"message": f"note number {i}"}).status_code for i in range(12)]
    assert codes.count(201) == 10 and codes[-1] == 429


def test_notes_are_exported_and_deleted_with_the_account(client):
    from tests.conftest import PASSWORD
    client.post("/api/feedback", json={"message": "this mentions my company Acme"})
    exported = client.get("/api/account/export").json()
    assert [f["message"] for f in exported["feedback"]] == ["this mentions my company Acme"]
    assert client.post("/api/account/delete", json={"password": PASSWORD}).status_code == 200
    assert stored() == []  # a note can hold personal details, so it is deleted with the account
