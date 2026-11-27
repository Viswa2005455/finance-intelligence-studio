"""Emails sent the moment a service order is paid: the customer gets their ready-made kit (attached)
and, for Standard and Premium, what is needed to start the custom work; the owner gets a new-order
alert with everything the customer wrote."""

from __future__ import annotations

import base64
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

import httpx

from ..config import Settings

log = logging.getLogger("fis.orders")
SITE = "https://finance-intelligence-studio.onrender.com/services"
OWNER_NAME = "Viswa Kumar"


@dataclass
class Order:
    payment_id: str
    service: str          # e.g. "Resume / CV for finance roles"
    package: str          # Basic | Standard | Premium
    amount: int           # rupees
    customer_name: str
    customer_email: str
    customer_phone: str
    requirements: str
    files_link: str
    you_send: str         # what the customer needs to send for the custom work
    delivery_days: int | None
    revisions: int | None
    custom: bool = False  # Standard/Premium: custom work follows the instant kit
    kit_name: str = ""    # file name of the attached kit, "" if none
    kit_bytes: bytes = b""


BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def brevo_configured(s: Settings) -> bool:
    return bool(s.fis_brevo_api_key and s.fis_brevo_api_key.get_secret_value().strip() and (s.fis_brevo_sender or s.fis_smtp_user or s.fis_order_email))


def sender_address(s: Settings) -> str:
    return (s.fis_brevo_sender or s.fis_smtp_user or s.fis_order_email or "").strip()


def mail_configured(s: Settings) -> bool:
    """Email is on when either the HTTPS email service (Brevo) or an SMTP account is set up."""
    return brevo_configured(s) or bool(s.fis_smtp_host and s.fis_smtp_user and s.fis_smtp_password)


def owner_address(s: Settings) -> str:
    return (s.fis_order_email or s.fis_smtp_user or "").strip()


def customer_message(o: Order, s: Settings) -> EmailMessage:
    first = o.customer_name.split()[0] if o.customer_name.strip() else "there"
    if o.kit_bytes:
        kit = ("Your ready-made kit is attached to this email. Unzip it and open the file named 00-START-HERE: it takes two "
               "minutes and shows you how to use everything. You can also download it again from the confirmation page you saw after paying.")
    else:
        kit = "Your ready-made kit is on the confirmation page you saw after paying. Reply to this email if you cannot open it."
    if o.custom:
        days = f"within {o.delivery_days} day{'s' if o.delivery_days != 1 else ''}" if o.delivery_days else "within the time on the service page"
        revs = f", with {o.revisions} revision{'s' if o.revisions != 1 else ''} included" if o.revisions else ""
        have_files = bool(o.files_link) or len(o.requirements.strip()) >= 40
        ask = ("I have your details and files link. If anything is missing I will reply to this email."
               if have_files else
               f"To start your custom work, please reply to this email with: {o.you_send}. You can attach files or share a Google Drive link.")
        custom = (f"\n\nYOUR CUSTOM WORK ({o.package} package)\n{ask}\n"
                  f"I will email your finished custom work {days} of receiving everything needed{revs}.")
    else:
        custom = "\n\nThe Basic package is the kit only, so there is nothing more to wait for. If you would like it customised for you, just reply to this email."
    m = EmailMessage()
    m["Subject"] = f"Your kit is here: {o.service}"
    m["From"] = formataddr((OWNER_NAME, sender_address(s)))
    m["To"] = o.customer_email
    m["Reply-To"] = owner_address(s)
    m.set_content(
        f"Hi {first},\n\n"
        f"Thank you for your order. Your payment of Rs {o.amount} is confirmed.\n\n"
        f"Service: {o.service}\nPackage: {o.package}\nPayment ID: {o.payment_id}\n\n"
        f"YOUR INSTANT KIT\n{kit}{custom}\n\n"
        f"Thanks,\n{OWNER_NAME}\nFinlight\n{SITE}\n"
    )
    if o.kit_bytes:
        m.add_attachment(o.kit_bytes, maintype="application", subtype="zip", filename=o.kit_name or "kit.zip")
    return m


def owner_message(o: Order, s: Settings) -> EmailMessage:
    m = EmailMessage()
    m["Subject"] = f"New paid order: {o.service} ({o.package}) - Rs {o.amount}" + (" [CUSTOM WORK DUE]" if o.custom else " [kit only]")
    m["From"] = formataddr(("Finlight", sender_address(s)))
    m["To"] = owner_address(s)
    m["Reply-To"] = o.customer_email
    owed = (f"Instant kit sent. CUSTOM WORK DUE within {o.delivery_days or '?'} day(s) after you have their details."
            if o.custom else "Instant kit sent. Nothing more owed (Basic package is the kit only).")
    m.set_content(
        "A customer has paid. Reply to this email to write to them directly.\n\n"
        f"Service: {o.service}\nPackage: {o.package}\nAmount: Rs {o.amount}\nPayment ID: {o.payment_id}\n"
        f"{owed}\n\n"
        f"Name: {o.customer_name}\nEmail: {o.customer_email}\nPhone: {o.customer_phone or '-'}\n"
        f"Files link: {o.files_link or '-'}\n\nWhat they wrote:\n{o.requirements or '-'}\n\n"
        f"They were asked to send (custom work): {o.you_send}\n"
    )
    return m


def _brevo_payload(m: EmailMessage, s: Settings) -> dict:
    """One EmailMessage as a Brevo transactional-email request. The sender must be a sender verified in Brevo."""
    name, _ = parseaddr(m["From"] or "")
    to_name, to_addr = parseaddr(m["To"] or "")
    body = m.get_body(("plain",))
    payload: dict = {"sender": {"name": name or OWNER_NAME, "email": sender_address(s)}, "to": [{"email": to_addr, **({"name": to_name} if to_name else {})}],
                     "subject": str(m["Subject"] or ""), "textContent": body.get_content() if body else ""}
    _, reply = parseaddr(m["Reply-To"] or "")
    if reply:
        payload["replyTo"] = {"email": reply}
    files = [{"name": a.get_filename() or "attachment.bin", "content": base64.b64encode(a.get_payload(decode=True) or b"").decode()} for a in m.iter_attachments()]
    if files:
        payload["attachment"] = files
    return payload


def send_brevo(messages: list[EmailMessage], s: Settings, client: httpx.Client | None = None) -> None:
    """Sends over HTTPS (port 443), which hosting plans that block SMTP ports still allow."""
    key = s.fis_brevo_api_key.get_secret_value().strip() if s.fis_brevo_api_key else ""
    own = client is None
    client = client or httpx.Client(timeout=20)
    try:
        for m in messages:
            r = client.post(BREVO_URL, json=_brevo_payload(m, s), headers={"api-key": key, "accept": "application/json", "content-type": "application/json"})
            if r.status_code >= 300:
                # Brevo explains problems in the response (for example: sender not verified); never log the key.
                raise RuntimeError(f"Brevo refused the email ({r.status_code}): {r.text[:300]}")
    finally:
        if own:
            client.close()


def send(messages: list[EmailMessage], s: Settings) -> None:
    if brevo_configured(s):
        return send_brevo(messages, s)
    password = s.fis_smtp_password.get_secret_value().replace(" ", "") if s.fis_smtp_password else ""
    host, port, user = (s.fis_smtp_host or "").strip(), s.fis_smtp_port, (s.fis_smtp_user or "").strip()
    if port == 465:
        server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=20)
    else:
        server = smtplib.SMTP(host, port, timeout=20)
        server.starttls()
    with server:
        server.login(user, password)
        for m in messages:
            server.send_message(m)
