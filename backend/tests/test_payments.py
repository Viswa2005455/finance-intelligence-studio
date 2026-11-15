"""Paid service orders: the server sets the price, and only correctly signed confirmations count."""

import hashlib
import hmac
import json

import httpx

from app.api import payments as api
from app.payments import build_notes, catalog, create_payment_link, find_package, signature_valid

SECRET = "test_secret_value"


def _sign(link_id, ref, status, pay_id, secret=SECRET):
    return hmac.new(secret.encode(), f"{link_id}|{ref}|{status}|{pay_id}".encode(), hashlib.sha256).hexdigest()


def test_catalog_has_fifty_services_with_three_packages():
    cat = catalog()
    assert len(cat) == 50
    assert all(set(s["tiers"]) == {"Basic", "Standard", "Premium"} for s in cat.values())


def test_find_package_rejects_unknown_tier_and_slug():
    assert find_package("custom-excel-dashboard", "Basic")[1]["price"] == 499
    assert find_package("custom-excel-dashboard", "Gold") is None
    assert find_package("no-such-service", "Basic") is None


def test_payment_link_uses_catalog_price_in_paise():
    seen = {}

    def handler(request: httpx.Request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": "plink_1", "short_url": "https://rzp.io/i/abc"})

    service, package = find_package("custom-excel-dashboard", "Standard")
    out = create_payment_link(key_id="k", key_secret="s", service=service, tier="Standard", package=package,
                              name="Asha", email="asha@example.com", phone="", requirements="x" * 600,
                              files_link="", callback_url="https://site/services/thank-you",
                              client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert out["url"] == "https://rzp.io/i/abc"
    assert seen["body"]["amount"] == 89900
    assert seen["body"]["currency"] == "INR"
    notes = seen["body"]["notes"]
    assert len(notes) <= 15 and all(len(v) <= 256 for v in notes.values())
    assert "".join(notes[k] for k in sorted(n for n in notes if n.startswith("requirements_"))) == "x" * 600


def test_notes_stay_within_razorpay_limits_for_long_input():
    service, _ = find_package("custom-excel-dashboard", "Basic")
    notes = build_notes(service=service, tier="Basic", name="N" * 300, email="a@b.co", phone="+91 9999999999",
                        requirements="r" * 2000, files_link="https://x/" + "y" * 300)
    assert len(notes) <= 15 and all(len(v) <= 256 for v in notes.values())


def test_signature_check():
    sig = _sign("plink_1", "svc_ab", "paid", "pay_1")
    assert signature_valid(key_secret=SECRET, link_id="plink_1", reference_id="svc_ab", status="paid", payment_id="pay_1", signature=sig)
    assert not signature_valid(key_secret=SECRET, link_id="plink_1", reference_id="svc_ab", status="paid", payment_id="pay_2", signature=sig)


def test_checkout_is_off_without_keys(client, monkeypatch):
    monkeypatch.setattr(api, "_keys", lambda: None)
    assert client.get("/api/payments/config").json() == {"enabled": False}
    body = {"slug": "custom-excel-dashboard", "tier": "Basic", "name": "Asha", "email": "asha@example.com",
            "requirements": "Monthly sales dashboard please"}
    assert client.post("/api/payments/checkout", json=body).status_code == 503


def test_checkout_validates_and_ignores_client_prices(client, monkeypatch):
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    captured = {}

    def fake_link(**kw):
        captured.update(kw)
        return {"url": "https://rzp.io/i/x", "id": "plink_x"}

    monkeypatch.setattr(api, "create_payment_link", fake_link)
    base = {"slug": "custom-excel-dashboard", "tier": "Premium", "name": "Asha", "email": "asha@example.com",
            "requirements": "Monthly sales dashboard please", "price": 1}
    r = client.post("/api/payments/checkout", json=base)
    assert r.status_code == 200 and r.json() == {"url": "https://rzp.io/i/x"}
    assert captured["package"]["price"] == 1199
    assert captured["callback_url"].endswith("/services/thank-you")
    assert client.post("/api/payments/checkout", json={**base, "tier": "Gold"}).status_code == 422
    assert client.post("/api/payments/checkout", json={**base, "email": "nope"}).status_code == 422
    assert client.post("/api/payments/checkout", json={**base, "slug": "missing"}).status_code == 404


def test_verify_rejects_forged_signature_and_accepts_real_one(client, monkeypatch):
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "fetch_payment_link", lambda **kw: {
        "status": "paid", "description": "Custom Excel dashboard (Basic package)", "amount": 49900, "amount_paid": 49900,
        "notes": {"service": "#1 Custom Excel dashboard", "package": "Basic", "customer_email": "asha@example.com"}})
    q = {"payment_link_id": "plink_1", "payment_link_reference_id": "svc_ab", "payment_link_status": "paid", "payment_id": "pay_1"}
    assert client.post("/api/payments/verify", json={**q, "signature": "0" * 64}).status_code == 400
    r = client.post("/api/payments/verify", json={**q, "signature": _sign("plink_1", "svc_ab", "paid", "pay_1")})
    assert r.status_code == 200
    out = r.json()
    assert out["paid"] is True and out["amount"] == 499 and out["delivery_days"] == 3


def test_keys_ignore_pasted_whitespace(monkeypatch):
    from app.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_live_abc\n")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", " secret123 \n")
    try:
        assert api._keys() == ("rzp_live_abc", "secret123")
        monkeypatch.setenv("RAZORPAY_KEY_SECRET", "  \n")
        get_settings.cache_clear()
        assert api._keys() is None
    finally:
        get_settings.cache_clear()
