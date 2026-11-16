"""Public endpoints for paying for a service from the /services pages (no account needed)."""

from __future__ import annotations

import logging
import os
import re

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth.security import EMAIL_RE, limiter
from ..config import get_settings
from ..db.models import ServiceOrder
from ..db.session import get_db, session_factory
from ..payments import mail
from ..payments import (TIERS, PaymentError, catalog, create_payment_link, fetch_payment_link, find_package, kit_path, signature_valid,
                        slug_for_title)
from .auth import client_ip
from .base import BaseModel

router = APIRouter(prefix="/api/payments", tags=["payments"])
log = logging.getLogger("fis.orders")
_PHONE = re.compile(r"^\+?[0-9 ]{8,16}$")
_ID = re.compile(r"^[A-Za-z0-9_]{1,64}$")


def _keys() -> tuple[str, str] | None:
    # Keys pasted into a hosting dashboard often carry a stray space or line break; Razorpay rejects those.
    s = get_settings()
    key_id = (s.razorpay_key_id or "").strip()
    secret = s.razorpay_key_secret.get_secret_value().strip() if s.razorpay_key_secret else ""
    return (key_id, secret) if key_id and secret else None


class CheckoutIn(BaseModel):
    slug: str = Field(max_length=120)
    tier: str
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=200)
    phone: str = Field(default="", max_length=20)
    requirements: str = Field(default="", max_length=2000)  # Basic is the instant kit only; Standard/Premium need it (checked in checkout)
    files_link: str = Field(default="", max_length=250)

    @field_validator("tier")
    @classmethod
    def _tier(cls, v: str) -> str:
        if v not in TIERS:
            raise ValueError("must be Basic, Standard or Premium")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip()
        if not EMAIL_RE.match(v):
            raise ValueError("enter a valid email address")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        v = v.strip()
        if v and not _PHONE.match(v):
            raise ValueError("enter a valid phone number or leave it empty")
        return v

    @field_validator("files_link")
    @classmethod
    def _link(cls, v: str) -> str:
        v = v.strip()
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("must be a link starting with https://")
        return v


class VerifyIn(BaseModel):
    payment_link_id: str
    payment_link_reference_id: str
    payment_link_status: str
    payment_id: str
    signature: str = Field(max_length=128)

    @field_validator("payment_link_id", "payment_link_reference_id", "payment_link_status", "payment_id")
    @classmethod
    def _ids(cls, v: str) -> str:
        if not _ID.match(v):
            raise ValueError("invalid value")
        return v


@router.get("/config")
def config():
    return {"enabled": _keys() is not None}


@router.post("/checkout")
def checkout(body: CheckoutIn, request: Request):
    keys = _keys()
    if keys is None:
        raise HTTPException(503, "Online payment is not switched on yet. Please email me to order.")
    if not limiter.hit(f"checkout:{client_ip(request)}", 20, 3600):
        raise HTTPException(429, "Too many order attempts. Please try again later.")
    found = find_package(body.slug, body.tier)
    if found is None:
        raise HTTPException(404, "That service or package does not exist.")
    service, package = found
    if body.tier != "Basic" and len(body.requirements.strip()) < 10:
        raise HTTPException(422, "Describe what you need in at least a sentence so the custom work can start.")
    base = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/") or str(request.base_url).rstrip("/")
    try:
        link = create_payment_link(key_id=keys[0], key_secret=keys[1], service=service, tier=body.tier, package=package,
                                   name=body.name.strip(), email=body.email, phone=body.phone,
                                   requirements=body.requirements.strip(), files_link=body.files_link,
                                   callback_url=f"{base}/services/thank-you")
    except PaymentError as e:
        raise HTTPException(502, str(e)) from e
    return {"url": link["url"]}


@router.post("/verify")
def verify(body: VerifyIn, request: Request, background: BackgroundTasks, db: Session = Depends(get_db)):
    keys = _keys()
    if keys is None:
        raise HTTPException(503, "Online payment is not switched on.")
    if not limiter.hit(f"verify:{client_ip(request)}", 60, 3600):
        raise HTTPException(429, "Too many requests. Please try again later.")
    ok = signature_valid(key_secret=keys[1], link_id=body.payment_link_id, reference_id=body.payment_link_reference_id,
                         status=body.payment_link_status, payment_id=body.payment_id, signature=body.signature)
    if not ok:
        raise HTTPException(400, "This payment confirmation could not be verified.")
    try:
        link = fetch_payment_link(key_id=keys[0], key_secret=keys[1], link_id=body.payment_link_id)
    except PaymentError as e:
        raise HTTPException(502, str(e)) from e
    notes = link.get("notes") or {}
    found = None
    for slug, svc in catalog().items():
        if notes.get("service", "").startswith(f"#{svc['id']} "):
            found = (slug, svc)
            break
    tier = notes.get("package", "")
    custom = tier in ("Standard", "Premium")  # Basic is the instant kit only
    days = found[1]["tiers"].get(tier, {}).get("days") if found and custom else 0
    kit = kit_path(found[0]) if found else None
    paid = link.get("status") == "paid"
    amount = (link.get("amount_paid") or link.get("amount") or 0) / 100
    if paid:
        order = mail.Order(
            payment_id=body.payment_id,
            service=found[1]["title"] if found else notes.get("service", "Service"),
            package=tier, amount=int(amount),
            customer_name=notes.get("customer_name", ""), customer_email=notes.get("customer_email", ""),
            customer_phone=notes.get("customer_phone", ""), files_link=notes.get("files_link", ""),
            requirements="".join(notes.get(f"requirements_{i}", "") for i in range(1, 9)),
            you_send=(found[1].get("you_send") if found else None) or "the details and files for your order",
            delivery_days=days, revisions=({"Standard": 2, "Premium": 3}.get(tier)), custom=custom,
            kit_name=f"{found[0]}-kit.zip" if kit else "", kit_bytes=kit.read_bytes() if kit else b"",
        )
        if _record(db, order, body.payment_link_id) and order.customer_email:
            background.add_task(_email_order, order)
    return {
        "paid": paid,
        "description": link.get("description", ""),
        "amount": amount,
        "email": notes.get("customer_email", ""),
        "delivery_days": days,
        "custom": custom,
        "kit_available": kit is not None,
        "payment_id": body.payment_id,
    }


@router.get("/kit")
def download_kit(request: Request, payment_link_id: str = Query(pattern=_ID.pattern), payment_link_reference_id: str = Query(pattern=_ID.pattern),
                 payment_link_status: str = Query(max_length=20), payment_id: str = Query(pattern=_ID.pattern),
                 razorpay_signature: str = Query(max_length=128), db: Session = Depends(get_db)):
    """The ready-made kit for a paid order. Needs the same signed values Razorpay sent to the thank-you page,
    and an order recorded for that payment, so only someone who actually paid can download it."""
    keys = _keys()
    if keys is None:
        raise HTTPException(503, "Online payment is not switched on.")
    if not limiter.hit(f"kit:{client_ip(request)}", 30, 3600):
        raise HTTPException(429, "Too many downloads. Please try again later.")
    ok = signature_valid(key_secret=keys[1], link_id=payment_link_id, reference_id=payment_link_reference_id,
                         status=payment_link_status, payment_id=payment_id, signature=razorpay_signature)
    row = db.get(ServiceOrder, payment_id) if ok and payment_link_status == "paid" else None
    if row is None or row.payment_link_id != payment_link_id:
        raise HTTPException(404, "No paid order found for this link. Use the download button on your confirmation page, or reply to your order email.")
    slug = slug_for_title(row.service)
    path = kit_path(slug) if slug else None
    if path is None:
        raise HTTPException(404, "The kit for this service is not available yet. Reply to your order email and it will be sent to you.")
    return FileResponse(path, media_type="application/zip", filename=f"{slug}-kit.zip")


def _record(db: Session, o: mail.Order, link_id: str) -> bool:
    """Saves the paid order; False when it was already recorded (thank-you page reloaded)."""
    db.add(ServiceOrder(payment_id=o.payment_id, payment_link_id=link_id, service=o.service[:160], package=o.package[:16],
                        amount=o.amount, customer_name=o.customer_name[:120], customer_email=o.customer_email[:254]))
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def _email_order(o: mail.Order) -> None:
    """Runs after the thank-you page has its answer, so a slow mail server never delays the customer."""
    s = get_settings()
    if not mail.mail_configured(s):
        log.warning("Paid order %s recorded but not emailed: order email (FIS_SMTP_*) is not set up.", o.payment_id)
        return
    try:
        mail.send([mail.customer_message(o, s), mail.owner_message(o, s)], s)
    except Exception:
        log.exception("Could not send the order emails for %s", o.payment_id)
        return
    with session_factory()() as db:
        row = db.get(ServiceOrder, o.payment_id)
        if row:
            row.customer_emailed = row.owner_emailed = True
            db.commit()
