"""Pages that need no account: the methodology catalogue. Everything here is read-only and the same for every visitor."""

from __future__ import annotations

from fastapi import APIRouter

from ..finance import methodology

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/methodology")
def methodology_catalogue():
    return methodology.catalogue()
