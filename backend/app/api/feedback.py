"""The in-app feedback button: signed-in users send a note (and, if they choose, technical details). Notes are stored in the
database and written to the server log; `python -m app.tools.show_feedback` lists the latest ones."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import Field
from sqlalchemy.orm import Session

from ..auth.deps import current_user
from ..auth.durable import durable_limiter
from ..db.models import Feedback, User
from ..db.session import get_db
from .base import BaseModel

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
log = logging.getLogger("fis.feedback")


class FeedbackIn(BaseModel):
    kind: Literal["idea", "problem", "question"] = "idea"
    message: str = Field(min_length=3, max_length=2000)
    page: str = Field(default="", max_length=200)
    details: str = Field(default="", max_length=3000)


@router.post("", status_code=201)
def send_feedback(body: FeedbackIn, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not durable_limiter.hit(f"feedback:{user.id}", 10, 3600):
        raise HTTPException(429, "That is a lot of feedback in an hour. Thank you: please try again later.")
    note = Feedback(user_id=user.id, kind=body.kind, message=body.message.strip(), page=body.page.strip(),
                    details=body.details.strip(), user_agent=(request.headers.get("user-agent") or "")[:300])
    db.add(note)
    db.commit()
    log.info("Feedback (%s) from %s on %s: %s", body.kind, user.email, body.page or "?", body.message.strip()[:200])
    return {"sent": True}
