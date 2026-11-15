"""Public endpoints for paying for a service from the /services pages (no account needed)."""

from __future__ import annotations

import os
import re

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field, field_validator

from ..auth.security import EMAIL_RE, limiter
from ..config import get_settings
from ..payments import TIERS, PaymentError, catalog, create_payment_link, fetch_payment_link, find_package, signature_valid
from .auth import client_ip
from .base import BaseModel

router = APIRouter(prefix="/api/payments", tags=["payments"])
_PHONE = re.compile(r"^\+?[0-9 ]{8,16}$")
_ID = re.compile(r"^[A-Za-z0-9_]{1,64}$")


def _keys() -> tuple[str, str] | None:
    s = get_settings()
    if not s.razorpay_key_id or s.razorpay_key_secret is None:
        return None
    return s.razorpay_key_id, s.razorpay_key_secret.get_secret_value()


class CheckoutIn(BaseModel):
    slug: str = Field(max_length=120)
    tier: str
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=200)
    phone: str = Field(default="", max_length=20)
    requirements: str = Field(min_length=10, max_length=2000)
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
def verify(body: VerifyIn, request: Request):
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
    days = found[1]["tiers"].get(tier, {}).get("days") if found else None
    return {
        "paid": link.get("status") == "paid",
        "description": link.get("description", ""),
        "amount": (link.get("amount_paid") or link.get("amount") or 0) / 100,
        "email": notes.get("customer_email", ""),
        "delivery_days": days,
        "payment_id": body.payment_id,
    }
