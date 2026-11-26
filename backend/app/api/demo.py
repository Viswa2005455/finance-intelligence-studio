"""A public, rate-limited taste of the app for visitors without an account.

Only one small calculator is exposed (investment appraisal), and it runs the very same function as the signed-in
page, so the numbers are identical. Nothing is stored and no data about the visitor is kept.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field

from ..auth.security import limiter
from . import finance
from .auth import client_ip
from .base import BaseModel

router = APIRouter(prefix="/api/demo", tags=["demo"])


class DemoAppraisal(BaseModel):
    initial: float = Field(gt=0, le=1e12, description="Initial investment (a positive amount)")
    flows: list[float] = Field(min_length=1, max_length=10, description="Cash flows for years 1..n")
    rate: float = Field(ge=0, le=1, description="Discount rate as a decimal, 0.10 for 10%")


@router.post("/appraisal")
def demo_appraisal(req: DemoAppraisal, request: Request):
    if not limiter.hit(f"demo:{client_ip(request)}", 120, 600):
        raise HTTPException(429, "That is a lot of demo calculations in a short time. Wait a few minutes, or create a free account for unlimited use.")
    if any(abs(f) > 1e12 for f in req.flows):
        raise HTTPException(422, "Cash flows must be smaller than 1,000,000,000,000.")
    return finance.appraisal(finance.AppraisalRequest(cash_flows=[-req.initial, *req.flows], discount_rate=req.rate))
