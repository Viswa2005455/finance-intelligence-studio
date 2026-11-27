"""Accounts: register, sign in/out, sessions, password change, data export and deletion."""

from __future__ import annotations

import datetime as dt

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from pydantic import Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..auth.deps import SESSION_COOKIE, current_session, current_user, log_activity
from ..auth.durable import durable_limiter
from ..auth.reset import create_reset, find_valid, reset_link, reset_message
from ..auth.security import DUMMY_HASH, EMAIL_RE, hash_password, limiter, new_session_token, normalise_email, password_problems, token_hash, verify_password
from ..config import Settings, get_settings
from ..db.models import Activity, AuthSession, Feedback, PasswordReset, Project, SavedItem, Upload, User, utcnow
from ..payments.mail import mail_configured, send as send_mail
from ..db.session import get_db
from .base import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = logging.getLogger("fis.auth")
account = APIRouter(prefix="/api/account", tags=["account"])


def client_ip(request: Request) -> str:
    # Behind a reverse proxy, configure uvicorn --proxy-headers so this is the real client address.
    return request.client.host if request.client else "unknown"


def start_session(db: Session, user: User, request: Request, response: Response, settings: Settings) -> None:
    token = new_session_token()
    expires = utcnow() + dt.timedelta(days=settings.fis_session_days)
    db.add(AuthSession(user_id=user.id, token_hash=token_hash(token), expires_at=expires,
                       user_agent=(request.headers.get("user-agent") or "")[:300]))
    user.last_login_at = utcnow()
    response.set_cookie(SESSION_COOKIE, token, max_age=settings.fis_session_days * 86400, httponly=True,
                        secure=settings.cookie_secure, samesite="lax", path="/")


def user_out(u: User, settings: Settings) -> dict:
    return {"id": str(u.id), "email": u.email, "display_name": u.display_name, "created_at": u.created_at,
            "retention_days": settings.fis_upload_retention_days, "session_days": settings.fis_session_days}


class RegisterIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=200)
    display_name: str = Field(min_length=1, max_length=80)


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=200)


@router.get("/config")
def auth_config(settings: Settings = Depends(get_settings)):
    return {"registration_open": settings.fis_allow_registration, "min_password_length": 10}


@router.post("/register", status_code=201)
def register(body: RegisterIn, request: Request, response: Response, db: Session = Depends(get_db),
             settings: Settings = Depends(get_settings)):
    if not settings.fis_allow_registration:
        raise HTTPException(403, "Registration is closed on this server.")
    if not durable_limiter.hit(f"register:{client_ip(request)}", 10, 3600):
        raise HTTPException(429, "Too many sign-up attempts. Try again later.")
    email = normalise_email(body.email)
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Enter a valid email address.")
    problems = password_problems(body.password, email)
    if problems:
        raise HTTPException(422, " ".join(problems))
    if db.scalar(select(User.id).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists. Sign in instead.")
    user = User(email=email, display_name=body.display_name.strip(), password_hash=hash_password(body.password))
    db.add(user)
    db.flush()
    start_session(db, user, request, response, settings)
    log_activity(db, user.id, "account.created")
    db.commit()
    return user_out(user, settings)


@router.post("/login")
def login(body: LoginIn, request: Request, response: Response, db: Session = Depends(get_db),
          settings: Settings = Depends(get_settings)):
    email = normalise_email(body.email)
    if not (durable_limiter.hit(f"login-ip:{client_ip(request)}", 30, 900) and durable_limiter.hit(f"login-email:{email}", 10, 900)):
        raise HTTPException(429, "Too many sign-in attempts. Wait 15 minutes and try again.")
    user = db.scalar(select(User).where(User.email == email))
    ok = verify_password(body.password, user.password_hash if user else DUMMY_HASH)
    if not (user and ok):
        raise HTTPException(401, "Email or password is incorrect.")
    start_session(db, user, request, response, settings)
    log_activity(db, user.id, "account.signed_in")
    db.commit()
    return user_out(user, settings)


@router.post("/logout")
def logout(response: Response, s: AuthSession = Depends(current_session), db: Session = Depends(get_db)):
    db.delete(db.get(AuthSession, s.id))
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"signed_out": True}


@router.get("/me")
def me(user: User = Depends(current_user), settings: Settings = Depends(get_settings)):
    return user_out(user, settings)


class PasswordChange(BaseModel):
    current_password: str = Field(max_length=200)
    new_password: str = Field(max_length=200)


@router.post("/change-password")
def change_password(body: PasswordChange, request: Request, s: AuthSession = Depends(current_session), db: Session = Depends(get_db)):
    user = db.get(User, s.user_id)
    if not limiter.hit(f"pwchange:{user.id}", 10, 900):
        raise HTTPException(429, "Too many attempts. Try again later.")
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(403, "Current password is incorrect.")
    problems = password_problems(body.new_password, user.email)
    if problems:
        raise HTTPException(422, " ".join(problems))
    user.password_hash = hash_password(body.new_password)
    # Sign out every other device.
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.id, AuthSession.id != s.id))
    log_activity(db, user.id, "account.password_changed")
    db.commit()
    return {"changed": True}


@router.get("/sessions")
def sessions(s: AuthSession = Depends(current_session), db: Session = Depends(get_db)):
    rows = db.scalars(select(AuthSession).where(AuthSession.user_id == s.user_id).order_by(AuthSession.last_seen_at.desc())).all()
    return {"sessions": [{"id": str(x.id), "created_at": x.created_at, "last_seen_at": x.last_seen_at, "expires_at": x.expires_at,
                          "user_agent": x.user_agent, "current": x.id == s.id} for x in rows]}


@router.post("/sessions/revoke-others")
def revoke_others(s: AuthSession = Depends(current_session), db: Session = Depends(get_db)):
    n = db.execute(delete(AuthSession).where(AuthSession.user_id == s.user_id, AuthSession.id != s.id)).rowcount
    log_activity(db, s.user_id, "account.sessions_revoked", count=n)
    db.commit()
    return {"revoked": n}


# ---------------------------------------------------------------- account data


@account.get("/export")
def export_all(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Everything stored about the user, as JSON (uploaded file bytes are not included)."""
    from .projects import export_payload
    payload = export_payload(db, user.id, project_id=None)
    payload["account"] = {"email": user.email, "display_name": user.display_name, "created_at": user.created_at}
    payload["feedback"] = [{"created_at": f.created_at, "kind": f.kind, "page": f.page, "message": f.message, "details": f.details}
                           for f in db.scalars(select(Feedback).where(Feedback.user_id == user.id).order_by(Feedback.created_at))]
    log_activity(db, user.id, "account.exported")
    db.commit()
    return payload


@account.get("/export.xlsx")
def export_xlsx(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """The latest version of every saved model as one Excel workbook (an index sheet and a sheet per model)."""
    from ..db.models import SavedVersion
    from ..reports import workbook
    rows = db.scalars(select(SavedItem).where(SavedItem.user_id == user.id).order_by(SavedItem.kind, SavedItem.name).limit(200)).all()
    items = []
    for it in rows:
        v = db.scalar(select(SavedVersion).where(SavedVersion.item_id == it.id, SavedVersion.version == it.latest_version))
        if v is not None:
            items.append({"kind": it.kind, "name": it.name, "version": it.latest_version, "updated_at": it.updated_at, "data": v.data})
    log_activity(db, user.id, "account.exported_xlsx", count=len(items))
    db.commit()
    return Response(workbook.build(items), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": 'attachment; filename="finance-intelligence-studio-saved-models.xlsx"'})


HANDOVER_MAX_BYTES = 60 * 1024 * 1024


@account.get("/handover.zip")
def handover_pack(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Everything an accountant needs in one zip: an Excel workbook of saved models, the full JSON export and the original uploaded files
    (up to a size cap; files over it are named in the README, not silently dropped)."""
    import io
    import json
    import re
    import zipfile
    from ..db.models import SavedVersion, UploadBlob
    from ..reports import workbook
    from .projects import export_payload

    items = []
    for it in db.scalars(select(SavedItem).where(SavedItem.user_id == user.id).order_by(SavedItem.kind, SavedItem.name).limit(200)).all():
        v = db.scalar(select(SavedVersion).where(SavedVersion.item_id == it.id, SavedVersion.version == it.latest_version))
        if v is not None:
            items.append({"kind": it.kind, "name": it.name, "version": it.latest_version, "updated_at": it.updated_at, "data": v.data})
    buf = io.BytesIO()
    included, left_out, used = [], [], 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("saved-models.xlsx", workbook.build(items))
        z.writestr("everything.json", json.dumps(export_payload(db, user.id, None), indent=2, default=str))
        for u in db.scalars(select(Upload).where(Upload.user_id == user.id).order_by(Upload.uploaded_at)).all():
            blob = db.get(UploadBlob, u.id)
            safe = re.sub(r"[^A-Za-z0-9._ -]", "_", u.name)[:80] or "file"
            if blob is None or used + len(blob.data) > HANDOVER_MAX_BYTES:
                left_out.append(u.name)
                continue
            used += len(blob.data)
            z.writestr(f"source-files/{u.id.hex[:8]}-{safe}", blob.data)
            included.append(u.name)
        lines = ["Finance Intelligence Studio: handover pack", "", f"Prepared for: {user.display_name}", f"Saved models: {len(items)} (see saved-models.xlsx)",
                 "everything.json holds projects, every saved version and the activity history.", "", f"Source files included: {len(included)}"]
        lines += [f"  - {n}" for n in included]
        if left_out:
            lines += ["", "Not included (over the size cap, or the original is no longer stored):"] + [f"  - {n}" for n in left_out]
        lines += ["", "These figures are calculations from the files and assumptions listed. They are not audited and not advice."]
        z.writestr("README.txt", chr(10).join(lines))
    log_activity(db, user.id, "account.handover", files=len(included), models=len(items))
    db.commit()
    return Response(buf.getvalue(), media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="finance-studio-handover.zip"'})


@account.get("/activity")
def recent_activity(limit: int = 50, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Your own history: sign-ins, saves, uploads, exports. Never holds file contents or passwords."""
    n = max(1, min(limit, 200))
    rows = db.scalars(select(Activity).where(Activity.user_id == user.id).order_by(Activity.created_at.desc(), Activity.id.desc()).limit(n)).all()
    return {"events": [{"when": a.created_at, "action": a.action, "entity_type": a.entity_type, "detail": a.detail or {}} for a in rows]}


class ConfirmIn(BaseModel):
    password: str = Field(max_length=200)


@account.post("/delete-data")
def delete_data(body: ConfirmIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Delete all uploads, projects, saved models and history, but keep the account."""
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(403, "Password is incorrect.")
    ids = db.scalars(select(Upload.id).where(Upload.user_id == user.id)).all()
    db.execute(delete(Upload).where(Upload.user_id == user.id))
    db.execute(delete(SavedItem).where(SavedItem.user_id == user.id))
    db.execute(delete(Project).where(Project.user_id == user.id))
    db.execute(delete(Activity).where(Activity.user_id == user.id))
    log_activity(db, user.id, "account.data_deleted", uploads=len(ids))
    db.commit()
    return {"deleted_uploads": len(ids)}


@account.post("/delete")
def delete_account(body: ConfirmIn, response: Response, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Permanently delete the account and everything in it."""
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(403, "Password is incorrect.")
    # ORM-level deletes so cascades also work on SQLite (test fallback); PostgreSQL cascades via FKs.
    for model in (Upload, SavedItem, Activity, Project, AuthSession, PasswordReset, Feedback):  # feedback may hold personal details: it goes too
        db.execute(delete(model).where(model.user_id == user.id))
    db.delete(db.get(User, user.id))
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"deleted": True}


# ---------------------------------------------------------------- Password reset
class ForgotIn(BaseModel):
    email: str = Field(max_length=254)


class ResetIn(BaseModel):
    token: str = Field(max_length=200)
    new_password: str = Field(max_length=200)


NEUTRAL = {"sent": True, "message": "If an account exists for that email, a reset link is on its way. It works once and expires in 30 minutes."}


def _deliver(user_email: str, user_name: str, token: str, settings: Settings) -> None:
    """Send (or, on a computer with no email set up, log) the reset link. Runs after the response so timing never reveals whether the account exists."""
    from types import SimpleNamespace
    link = reset_link(settings, token)
    if mail_configured(settings):
        try:
            send_mail([reset_message(SimpleNamespace(email=user_email, display_name=user_name), link, settings)], settings)  # type: ignore[arg-type]
        except Exception:  # noqa: BLE001
            log.exception("Could not send the password reset email")
    elif not settings.is_production:
        log.warning("Email is not set up, so the password reset link for %s is shown here instead: %s", user_email, link)
    else:
        log.error("A password reset was requested but email is not configured on this server")


@router.post("/forgot-password")
def forgot_password(body: ForgotIn, request: Request, tasks: BackgroundTasks, db: Session = Depends(get_db),
                    settings: Settings = Depends(get_settings)):
    """Always answers the same way, whether or not the email has an account (no account enumeration). Limited per address and per client."""
    email = normalise_email(body.email)
    allowed = durable_limiter.hit(f"forgot-ip:{client_ip(request)}", 10, 3600) and durable_limiter.hit(f"forgot-email:{email}", 3, 3600)
    user = db.scalar(select(User).where(User.email == email)) if allowed and EMAIL_RE.match(email) else None
    if user:
        token = create_reset(db, user)
        log_activity(db, user.id, "account.password_reset_requested")
        db.commit()
        tasks.add_task(_deliver, user.email, user.display_name, token, settings)
    return NEUTRAL


@router.post("/reset-password")
def reset_password(body: ResetIn, request: Request, db: Session = Depends(get_db)):
    if not durable_limiter.hit(f"reset-ip:{client_ip(request)}", 20, 3600):
        raise HTTPException(429, "Too many attempts. Try again later.")
    row = find_valid(db, body.token)
    if row is None:
        raise HTTPException(400, "This reset link is invalid or has expired. Ask for a new one.")
    user = db.get(User, row.user_id)
    problems = password_problems(body.new_password, user.email)
    if problems:
        raise HTTPException(422, " ".join(problems))  # the link stays usable so the person can try another password
    user.password_hash = hash_password(body.new_password)
    row.used_at = utcnow()
    db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.id != row.id))
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))  # signs out every device, including any thief's
    log_activity(db, user.id, "account.password_reset")
    db.commit()
    return {"reset": True}
