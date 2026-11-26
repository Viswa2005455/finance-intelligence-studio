"""A rate limiter whose counts live in the database, for the attempts that matter most (sign-in, sign-up,
password reset). Unlike the in-process limiter, its counts survive a restart and are shared by every worker
or server, so an attacker cannot reset the limit by waiting for a restart or by landing on another process.

If the database cannot be reached the limiter falls back to the in-memory one rather than locking everyone out."""

from __future__ import annotations

import datetime as dt
import logging
import random

from sqlalchemy import delete, func, select

from ..db.models import RateHit, utcnow
from ..db.session import session_factory
from .security import RateLimiter

log = logging.getLogger("fis.ratelimit")


class DurableLimiter:
    def __init__(self, fallback: RateLimiter | None = None):
        self.fallback = fallback or RateLimiter()

    def hit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Record an attempt; return False when `limit` attempts were already made in the last `window_seconds`."""
        try:
            now = utcnow()
            cutoff = now - dt.timedelta(seconds=window_seconds)
            with session_factory()() as db:
                used = db.scalar(select(func.count()).select_from(RateHit).where(RateHit.key == key, RateHit.hit_at > cutoff)) or 0
                if used >= limit:
                    return False
                db.add(RateHit(key=key, hit_at=now))
                if random.random() < 0.02:  # tidy up now and then: nothing older than a day is ever needed
                    db.execute(delete(RateHit).where(RateHit.hit_at < now - dt.timedelta(days=1)))
                db.commit()
                return True
        except Exception:  # noqa: BLE001 - a broken limiter store must not block sign-in
            log.exception("Durable rate limiter unavailable; using the in-memory limiter for this check")
            return self.fallback.hit(key, limit, window_seconds)

    def reset(self, key: str | None = None) -> None:
        self.fallback.reset(key)
        with session_factory()() as db:
            db.execute(delete(RateHit) if key is None else delete(RateHit).where(RateHit.key == key))
            db.commit()


durable_limiter = DurableLimiter()
