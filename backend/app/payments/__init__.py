"""Paid service orders through Razorpay Payment Links.

The browser never sets the price: the server looks up the service and package in
service_catalog.json (exported from frontend/src/lib/services.ts, the source of truth; a frontend
test fails if the two drift apart), creates a Razorpay payment link for that amount, and sends the
customer to Razorpay's hosted page. When Razorpay redirects back, the signature is verified with
the key secret before the order is shown as paid.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from functools import lru_cache
from pathlib import Path

import httpx

RAZORPAY_API = "https://api.razorpay.com/v1"
TIERS = ("Basic", "Standard", "Premium")
NOTE_CHUNK = 250  # Razorpay notes: at most 15 keys, values up to 256 characters


class PaymentError(Exception):
    """A problem talking to Razorpay, safe to show to the customer."""


@lru_cache
def catalog() -> dict[str, dict]:
    return json.loads((Path(__file__).with_name("service_catalog.json")).read_text(encoding="utf-8"))


def find_package(slug: str, tier: str) -> tuple[dict, dict] | None:
    service = catalog().get(slug)
    if service is None or tier not in service["tiers"]:
        return None
    return service, service["tiers"][tier]


def build_notes(*, service: dict, tier: str, name: str, email: str, phone: str, requirements: str, files_link: str) -> dict[str, str]:
    notes = {
        "service": f"#{service['id']} {service['title']}"[:NOTE_CHUNK],
        "package": tier,
        "customer_name": name[:NOTE_CHUNK],
        "customer_email": email[:NOTE_CHUNK],
    }
    if phone:
        notes["customer_phone"] = phone[:NOTE_CHUNK]
    if files_link:
        notes["files_link"] = files_link[:NOTE_CHUNK]
    for i in range(0, min(len(requirements), NOTE_CHUNK * 8), NOTE_CHUNK):
        notes[f"requirements_{i // NOTE_CHUNK + 1}"] = requirements[i:i + NOTE_CHUNK]
    return notes


def create_payment_link(*, key_id: str, key_secret: str, service: dict, tier: str, package: dict, name: str, email: str,
                        phone: str, requirements: str, files_link: str, callback_url: str,
                        client: httpx.Client | None = None) -> dict:
    body = {
        "amount": int(package["price"]) * 100,  # paise
        "currency": "INR",
        "accept_partial": False,
        "reference_id": "svc_" + secrets.token_hex(8),
        "description": f"{service['title']} ({tier} package)"[:2048],
        "customer": {"name": name, "email": email, **({"contact": phone} if phone else {})},
        "notify": {"email": True, "sms": False},
        "reminder_enable": False,
        "notes": build_notes(service=service, tier=tier, name=name, email=email, phone=phone,
                             requirements=requirements, files_link=files_link),
        "callback_url": callback_url,
        "callback_method": "get",
    }
    http = client or httpx.Client(timeout=20.0)
    try:
        r = http.post(f"{RAZORPAY_API}/payment_links", json=body, auth=(key_id, key_secret))
    except httpx.HTTPError as e:
        raise PaymentError("Could not reach the payment provider. Please try again in a minute.") from e
    if r.status_code >= 400:
        raise PaymentError("The payment provider rejected the request. Please try again later or email me.")
    data = r.json()
    return {"url": data["short_url"], "id": data["id"]}


def signature_valid(*, key_secret: str, link_id: str, reference_id: str, status: str, payment_id: str, signature: str) -> bool:
    message = f"{link_id}|{reference_id}|{status}|{payment_id}"
    expected = hmac.new(key_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def fetch_payment_link(*, key_id: str, key_secret: str, link_id: str, client: httpx.Client | None = None) -> dict:
    http = client or httpx.Client(timeout=20.0)
    try:
        r = http.get(f"{RAZORPAY_API}/payment_links/{link_id}", auth=(key_id, key_secret))
    except httpx.HTTPError as e:
        raise PaymentError("Could not reach the payment provider to confirm the order.") from e
    if r.status_code >= 400:
        raise PaymentError("The payment provider could not find this order.")
    return r.json()
