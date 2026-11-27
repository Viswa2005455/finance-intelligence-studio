"""Password reset: one-time links that expire, stored only as hashes, and never revealing whether an email has an account."""

from __future__ import annotations

import datetime as dt
import secrets
from email.message import EmailMessage
from email.utils import formataddr

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..config import Settings
from ..db.models import PasswordReset, User, utcnow
from ..payments.mail import sender_address
from .security import token_hash

RESET_MINUTES = 30


def create_reset(db: Session, user: User) -> str:
    """A fresh reset token for the user. Earlier unused links stop working, so only the newest email is valid."""
    db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None)))
    token = secrets.token_urlsafe(32)
    db.add(PasswordReset(user_id=user.id, token_hash=token_hash(token), expires_at=utcnow() + dt.timedelta(minutes=RESET_MINUTES)))
    return token


def find_valid(db: Session, token: str) -> PasswordReset | None:
    """The reset row for this token if it exists, is unused and has not expired."""
    if not token or len(token) > 200:
        return None
    row = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == token_hash(token)))
    if row is None or row.used_at is not None:
        return None
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=dt.timezone.utc)
    return row if expires > utcnow() else None


def reset_link(settings: Settings, token: str) -> str:
    return f"{settings.public_url}/?reset={token}"


def reset_message(user: User, link: str, settings: Settings) -> EmailMessage:
    first = user.display_name.split()[0] if user.display_name.strip() else "there"
    m = EmailMessage()
    m["Subject"] = "Reset your Finlight password"
    m["From"] = formataddr(("Finlight", sender_address(settings)))
    m["To"] = user.email
    m.set_content(
        f"Hi {first},\n\n"
        "Someone asked to reset the password for this account. If that was you, open this link and choose a new password:\n\n"
        f"{link}\n\n"
        f"The link works once and expires in {RESET_MINUTES} minutes. If you did not ask for it, ignore this email: your password has not changed.\n\n"
        "Finlight\n"
    )
    return m
