"""Password reset and the database-backed rate limiter."""

import datetime as dt
import re

import pytest
from sqlalchemy import func, select

from app.auth.durable import DurableLimiter
from app.auth.security import RateLimiter, token_hash
from app.db.models import PasswordReset, RateHit, utcnow
from app.db.session import session_factory
from tests.conftest import PASSWORD, register

NEW = "a-brand-new-passphrase-42"


@pytest.fixture()
def mailbox(monkeypatch):
    """Pretend email is configured and capture what would be sent."""
    sent = []
    monkeypatch.setattr("app.api.auth.mail_configured", lambda s: True)
    monkeypatch.setattr("app.api.auth.send_mail", lambda messages, s: sent.extend(messages))
    return sent


def token_from(message) -> str:
    return re.search(r"\?reset=([\w-]+)", message.get_content()).group(1)


def count(model) -> int:
    with session_factory()() as db:
        return db.scalar(select(func.count()).select_from(model))


def test_unknown_and_known_emails_get_the_same_answer(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/logout")
    a = anon_client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
    b = anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    assert a.status_code == b.status_code == 200 and a.json() == b.json()  # no account enumeration
    assert len(mailbox) == 1 and mailbox[0]["To"] == "ann@example.com"
    assert count(PasswordReset) == 1


def test_token_is_stored_hashed_and_the_link_uses_the_configured_site(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/forgot-password", json={"email": "Ann@Example.com "})
    token = token_from(mailbox[0])
    assert mailbox[0].get_content().count("http://localhost:5173/?reset=") == 1
    with session_factory()() as db:
        row = db.scalar(select(PasswordReset))
        assert row.token_hash == token_hash(token) and token not in row.token_hash


def test_full_reset_changes_the_password_signs_out_devices_and_is_single_use(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    token = token_from(mailbox[0])
    assert anon_client.get("/api/auth/me").status_code == 200  # still signed in on this device
    r = anon_client.post("/api/auth/reset-password", json={"token": token, "new_password": NEW})
    assert r.status_code == 200 and r.json() == {"reset": True}
    assert anon_client.get("/api/auth/me").status_code == 401  # every session was ended
    assert anon_client.post("/api/auth/login", json={"email": "ann@example.com", "password": PASSWORD}).status_code == 401
    assert anon_client.post("/api/auth/login", json={"email": "ann@example.com", "password": NEW}).status_code == 200
    again = anon_client.post("/api/auth/reset-password", json={"token": token, "new_password": "yet-another-passphrase-7"})
    assert again.status_code == 400 and "invalid or has expired" in again.json()["detail"]


def test_weak_password_keeps_the_link_usable_and_bad_tokens_are_refused(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    token = token_from(mailbox[0])
    assert anon_client.post("/api/auth/reset-password", json={"token": token, "new_password": "short"}).status_code == 422
    assert anon_client.post("/api/auth/reset-password", json={"token": "not-a-real-token", "new_password": NEW}).status_code == 400
    assert anon_client.post("/api/auth/reset-password", json={"token": token, "new_password": NEW}).status_code == 200


def test_expired_links_are_refused(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    token = token_from(mailbox[0])
    with session_factory()() as db:
        row = db.scalar(select(PasswordReset))
        row.expires_at = utcnow() - dt.timedelta(minutes=1)
        db.commit()
    r = anon_client.post("/api/auth/reset-password", json={"token": token, "new_password": NEW})
    assert r.status_code == 400


def test_a_new_request_cancels_the_old_link(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    first, second = token_from(mailbox[0]), token_from(mailbox[1])
    assert anon_client.post("/api/auth/reset-password", json={"token": first, "new_password": NEW}).status_code == 400
    assert anon_client.post("/api/auth/reset-password", json={"token": second, "new_password": NEW}).status_code == 200


def test_requests_are_limited_per_address_without_changing_the_answer(anon_client, mailbox):
    register(anon_client, email="ann@example.com")
    answers = [anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"}) for _ in range(6)]
    assert all(a.status_code == 200 and a.json()["sent"] for a in answers)  # same answer, so the limit leaks nothing
    assert len(mailbox) == 3  # but only three emails were sent in the hour


def test_without_email_set_up_the_link_goes_to_the_server_log_only(anon_client, caplog):
    register(anon_client, email="ann@example.com")
    with caplog.at_level("WARNING", logger="fis.auth"):
        r = anon_client.post("/api/auth/forgot-password", json={"email": "ann@example.com"})
    assert "?reset=" not in r.text  # never returned to the caller
    assert any("?reset=" in rec.getMessage() for rec in caplog.records)


def test_durable_limiter_counts_survive_a_new_instance_and_expire(anon_client):
    a = DurableLimiter(RateLimiter())
    assert [a.hit("k", 3, 60) for _ in range(4)] == [True, True, True, False]
    b = DurableLimiter(RateLimiter())  # a "restarted" process
    assert b.hit("k", 3, 60) is False
    assert b.hit("other", 3, 60) is True
    with session_factory()() as db:  # age the hits beyond the window
        for h in db.scalars(select(RateHit).where(RateHit.key == "k")):
            h.hit_at = utcnow() - dt.timedelta(seconds=120)
        db.commit()
    assert b.hit("k", 3, 60) is True


def test_sign_in_limit_now_persists_in_the_database(anon_client):
    register(anon_client, email="ann@example.com")
    anon_client.post("/api/auth/logout")
    for _ in range(10):
        anon_client.post("/api/auth/login", json={"email": "ann@example.com", "password": "wrong-password-1"})
    assert anon_client.post("/api/auth/login", json={"email": "ann@example.com", "password": PASSWORD}).status_code == 429
    assert count(RateHit) >= 10
