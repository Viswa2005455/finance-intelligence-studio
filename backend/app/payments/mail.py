"""Emails sent the moment a service order is paid: a confirmation to the customer (what to send
next, when it will be delivered) and a new-order alert to the owner with everything they wrote."""

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr

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
    you_send: str         # what the customer needs to send for this service
    delivery_days: int | None
    revisions: int | None


def mail_configured(s: Settings) -> bool:
    return bool(s.fis_smtp_host and s.fis_smtp_user and s.fis_smtp_password)


def owner_address(s: Settings) -> str:
    return (s.fis_order_email or s.fis_smtp_user or "").strip()


def customer_message(o: Order, s: Settings) -> EmailMessage:
    first = o.customer_name.split()[0] if o.customer_name.strip() else "there"
    days = f"within {o.delivery_days} day{'s' if o.delivery_days != 1 else ''}" if o.delivery_days else "as listed on the service page"
    revs = f", with {o.revisions} revision{'s' if o.revisions != 1 else ''} included" if o.revisions else ""
    have_files = bool(o.files_link) or len(o.requirements.strip()) >= 40
    ask = ("I have your details and files link. If anything is missing I'll reply to this email."
           if have_files else
           f"To start, please reply to this email with: {o.you_send}. "
           "You can attach files to your reply or share a Google Drive link.")
    m = EmailMessage()
    m["Subject"] = f"Order confirmed: {o.service} ({o.package})"
    m["From"] = formataddr((OWNER_NAME, s.fis_smtp_user or ""))
    m["To"] = o.customer_email
    m["Reply-To"] = owner_address(s)
    m.set_content(
        f"Hi {first},\n\n"
        f"Thank you for your order. Your payment of Rs {o.amount} is confirmed.\n\n"
        f"Service: {o.service}\nPackage: {o.package}\nPayment ID: {o.payment_id}\n\n"
        f"{ask}\n\n"
        f"Your finished work will be emailed to you {days} of receiving everything needed{revs}.\n\n"
        f"Thanks,\n{OWNER_NAME}\nFinance Intelligence Studio\n{SITE}\n"
    )
    return m


def owner_message(o: Order, s: Settings) -> EmailMessage:
    m = EmailMessage()
    m["Subject"] = f"New paid order: {o.service} ({o.package}) - Rs {o.amount}"
    m["From"] = formataddr(("Finance Intelligence Studio", s.fis_smtp_user or ""))
    m["To"] = owner_address(s)
    m["Reply-To"] = o.customer_email
    m.set_content(
        "A customer has paid. Reply to this email to write to them directly.\n\n"
        f"Service: {o.service}\nPackage: {o.package}\nAmount: Rs {o.amount}\nPayment ID: {o.payment_id}\n"
        f"Delivery promised: {o.delivery_days or '?'} day(s) after receiving their details\n\n"
        f"Name: {o.customer_name}\nEmail: {o.customer_email}\nPhone: {o.customer_phone or '-'}\n"
        f"Files link: {o.files_link or '-'}\n\nWhat they need:\n{o.requirements or '-'}\n\n"
        f"They were asked to send: {o.you_send}\n"
    )
    return m


def send(messages: list[EmailMessage], s: Settings) -> None:
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
