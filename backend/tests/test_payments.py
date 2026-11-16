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
    assert out["paid"] is True and out["amount"] == 499 and out["delivery_days"] == 0 and out["custom"] is False and out["kit_available"] is True


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


def _paid_link(**kw):
    return {"status": "paid", "description": "Resume / CV for finance roles (Basic package)", "amount": 9900, "amount_paid": 9900,
            "notes": {"service": "#49 Resume / CV for finance roles", "package": "Basic", "customer_name": "Asha Rao",
                      "customer_email": "asha@example.com", "customer_phone": "+91 9999999999", "requirements_1": "Fresher, B.Com"}}


def _verify_body(pay_id="pay_9"):
    q = {"payment_link_id": "plink_9", "payment_link_reference_id": "svc_cd", "payment_link_status": "paid", "payment_id": pay_id}
    return {**q, "signature": _sign("plink_9", "svc_cd", "paid", pay_id)}


def _mail_on(monkeypatch):
    from app.config import get_settings
    for k, v in {"FIS_SMTP_HOST": "smtp.example.com", "FIS_SMTP_USER": "me@example.com", "FIS_SMTP_PASSWORD": "abcd efgh",
                 "FIS_ORDER_EMAIL": "owner@example.com"}.items():
        monkeypatch.setenv(k, v)
    get_settings.cache_clear()


def test_paid_order_is_recorded_and_emailed_once(client, monkeypatch):
    from app.db.models import ServiceOrder
    from app.db.session import session_factory
    from app.payments import mail
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "fetch_payment_link", _paid_link)
    _mail_on(monkeypatch)
    sent = []
    monkeypatch.setattr(mail, "send", lambda messages, s: sent.append(messages))

    assert client.post("/api/payments/verify", json=_verify_body()).json()["paid"] is True
    assert client.post("/api/payments/verify", json=_verify_body()).status_code == 200  # page reloaded
    assert len(sent) == 1
    to_customer, to_owner = sent[0]
    assert to_customer["To"] == "asha@example.com" and to_customer["Reply-To"] == "owner@example.com"
    body = to_customer.get_body(("plain",)).get_content()
    assert "Rs 99" in body and "Basic package is the kit only" in body and "YOUR CUSTOM WORK" not in body
    assert to_customer["Subject"].startswith("Your kit is here")
    kit = [part for part in to_customer.iter_attachments()]
    assert len(kit) == 1 and kit[0].get_filename() == "resume-cv-for-finance-roles-kit.zip" and len(kit[0].get_content()) > 1000
    assert "[kit only]" in to_owner["Subject"]
    assert to_owner["To"] == "owner@example.com" and to_owner["Reply-To"] == "asha@example.com"
    assert "Fresher, B.Com" in to_owner.get_content() and "+91 9999999999" in to_owner.get_content()
    with session_factory()() as db:
        row = db.get(ServiceOrder, "pay_9")
        assert row.amount == 99 and row.customer_emailed and row.owner_emailed


def test_paid_order_without_mail_setup_is_still_recorded(client, monkeypatch):
    from app.db.models import ServiceOrder
    from app.db.session import session_factory
    from app.payments import mail
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "fetch_payment_link", _paid_link)
    monkeypatch.setattr(mail, "send", lambda *a: (_ for _ in ()).throw(AssertionError("must not send")))
    assert client.post("/api/payments/verify", json=_verify_body("pay_10")).json()["paid"] is True
    with session_factory()() as db:
        row = db.get(ServiceOrder, "pay_10")
        assert row is not None and not row.customer_emailed


def test_customer_email_skips_asking_for_files_already_given():
    from app.config import Settings
    from app.payments import mail
    s = Settings(fis_smtp_host="h", fis_smtp_user="me@example.com", fis_smtp_password="p")
    o = mail.Order(payment_id="pay_1", service="Custom Excel dashboard", package="Standard", amount=899, customer_name="Ravi",
                   customer_email="r@example.com", customer_phone="", requirements="Monthly sales dashboard", files_link="https://drive.example/x",
                   you_send="Your Excel data", delivery_days=4, revisions=2, custom=True)
    body = mail.customer_message(o, s).get_content()
    assert "I have your details and files link" in body and "within 4 days" in body and "2 revisions" in body
    assert "YOUR CUSTOM WORK (Standard package)" in body


def _paid_standard_link(**kw):
    link = _paid_link()
    link["notes"] = {**link["notes"], "package": "Standard", "requirements_1": "Fresher B.Com looking for an accounts executive role in Madurai"}
    link["amount"] = link["amount_paid"] = 24900
    return link


def test_standard_order_email_asks_for_custom_work_details(client, monkeypatch):
    from app.payments import mail
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "fetch_payment_link", _paid_standard_link)
    _mail_on(monkeypatch)
    sent = []
    monkeypatch.setattr(mail, "send", lambda messages, s: sent.append(messages))
    out = client.post("/api/payments/verify", json=_verify_body("pay_11")).json()
    assert out["custom"] is True and out["delivery_days"] == 2 and out["kit_available"] is True
    to_customer, to_owner = sent[0]
    assert "YOUR CUSTOM WORK (Standard package)" in to_customer.get_body(("plain",)).get_content() and len(list(to_customer.iter_attachments())) == 1
    assert "[CUSTOM WORK DUE]" in to_owner["Subject"]


def test_basic_checkout_needs_no_requirements_but_standard_does(client, monkeypatch):
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "create_payment_link", lambda **kw: {"url": "https://rzp.io/i/x", "id": "plink_x"})
    base = {"slug": "custom-excel-dashboard", "name": "Asha", "email": "asha@example.com"}
    assert client.post("/api/payments/checkout", json={**base, "tier": "Basic"}).status_code == 200
    assert client.post("/api/payments/checkout", json={**base, "tier": "Standard"}).status_code == 422


def _kit_query(pay_id="pay_12", link="plink_9", ref="svc_cd", status="paid", sig=None):
    sig = sig or _sign(link, ref, status, pay_id)
    return (f"/api/payments/kit?payment_link_id={link}&payment_link_reference_id={ref}&payment_link_status={status}"
            f"&payment_id={pay_id}&razorpay_signature={sig}")


def test_kit_download_needs_a_verified_paid_order(client, monkeypatch):
    monkeypatch.setattr(api, "_keys", lambda: ("key", SECRET))
    monkeypatch.setattr(api, "fetch_payment_link", _paid_link)
    # no order recorded yet: not downloadable even with a valid signature
    assert client.get(_kit_query()).status_code == 404
    assert client.post("/api/payments/verify", json=_verify_body("pay_12")).json()["paid"] is True
    r = client.get(_kit_query())
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip" and r.content[:2] == b"PK"
    assert "resume-cv-for-finance-roles-kit.zip" in r.headers["content-disposition"]
    assert client.get(_kit_query(sig="0" * 64)).status_code == 404                        # forged signature
    assert client.get(_kit_query(status="created", sig=_sign("plink_9", "svc_cd", "created", "pay_12"))).status_code == 404  # not paid
    assert client.get(_kit_query(link="plink_other", sig=_sign("plink_other", "svc_cd", "paid", "pay_12"))).status_code == 404  # other link


def test_every_service_has_a_kit_with_a_how_to_guide():
    import zipfile
    from app.payments import catalog, kit_path
    for slug in catalog():
        path = kit_path(slug)
        assert path is not None, f"missing kit for {slug}"
        names = zipfile.ZipFile(path).namelist()
        assert any(n.endswith("00-START-HERE-How-to-use.docx") for n in names) and len(names) >= 2, slug
    assert kit_path("../../etc/passwd") is None
