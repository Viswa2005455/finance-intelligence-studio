"""Crash reports from the browser. A page that fails to draw sends a short note here so the operator can see it in the server log.

Public (a crash can happen on the sign-in page) and therefore tightly limited per address. Nothing is stored in the database and
nothing about the person is recorded: only the message, the path (no query string) and a short stack."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field

from ..auth.durable import durable_limiter
from .auth import client_ip
from .base import BaseModel

router = APIRouter(prefix="/api/client-errors", tags=["monitoring"])
log = logging.getLogger("fis.client")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]+")


def _clean(s: str, n: int) -> str:
    """One line, no control characters (so a report cannot forge log lines), cut to length."""
    return _CONTROL.sub(" ", s).strip()[:n]


class ClientErrorIn(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    page: str = Field(default="", max_length=200)
    stack: str = Field(default="", max_length=2000)
    version: str = Field(default="", max_length=40)


@router.post("", status_code=202)
def report(body: ClientErrorIn, request: Request):
    if not durable_limiter.hit(f"clienterr:{client_ip(request)}", 10, 3600):
        raise HTTPException(429, "Too many error reports from this address. Thank you; they have been received.")
    page = _clean(body.page.split("?")[0].split("#")[0], 120)
    log.error("Browser error on %s (v%s): %s | %s", page or "?", _clean(body.version, 40) or "?", _clean(body.message, 300), _clean(body.stack, 800))
    return {"received": True}
