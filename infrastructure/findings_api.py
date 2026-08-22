"""Private human-review inbox and exception-approval surface for Bastion escalations.

This is deliberately a tiny Cloud Run service rather than a webhook dependency.  The
Escalation Agent can write one redacted, idempotent review record; humans with project access
can inspect the Firestore-backed inbox, while the service has no IAM-policy read capability.

It also owns the **only** path that creates an approved exception.  That matters twice over.
`SECURITY.md` states the model cannot create an exception, so approval must never be an agent
tool; and the suppression logic in the Orchestrator reads an exception ledger that, before this
endpoint existed, nothing in production ever wrote - the cross-week story worked in tests and
was unreachable in the deployed fleet.

The reviewer is taken from the **verified caller identity**, never from the request body.  A
self-asserted reviewer field is an attestation that whoever can reach the endpoint can forge,
which is not an audit trail.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any

import uvicorn
from fastapi import FastAPI, Header, HTTPException, status
from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.cloud import firestore
from google.oauth2 import id_token
from pydantic import BaseModel, Field

from model_armor.redaction import (
    OPAQUE_FINDING_ID,
    notification_summary,
    validate_finding_ids,
    validate_risk_categories,
)
from registry.departments import load_catalog

APP = FastAPI(title="Bastion findings inbox", docs_url=None, redoc_url=None)
COLLECTION = "bastion_human_review"
EXCEPTIONS = "bastion_exceptions"

# An exception is a silent suppression: for as long as it is valid, a real finding stops being
# raised. An unbounded one is a permanent hole in the audit that nobody is reminded of, so the
# horizon is capped here rather than trusted to the caller.
MAX_APPROVAL_DAYS = 90


class Escalation(BaseModel):
    source: str
    investigation_id: str
    department: str
    finding_count: int = Field(gt=0)
    finding_ids: list[str]
    risk_categories: list[str]
    summary: str


class ExceptionApproval(BaseModel):
    """A human decision to suppress one opaque finding until a bounded expiry."""

    finding_id: str
    approved_until: datetime
    policy_version: str = Field(min_length=1, max_length=64)


@lru_cache(maxsize=1)
def _client() -> Any:  # pragma: no cover - Cloud Run wires ADC and Firestore
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return firestore.Client(project=project)


def _collection() -> Any:  # pragma: no cover - Cloud Run wires ADC and Firestore
    return _client().collection(COLLECTION)


def _exceptions() -> Any:  # pragma: no cover - Cloud Run wires ADC and Firestore
    return _client().collection(EXCEPTIONS)


def caller_identity(authorization: str | None) -> str:
    """Return the verified caller principal, never a value the caller asserted about itself.

    Cloud Run IAM has already rejected unauthenticated traffic before this runs. Verifying the
    token again is defence in depth, and it is what turns "someone reached the endpoint" into
    "this principal approved this suppression".
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="an authenticated caller is required"
        )
    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = id_token.verify_oauth2_token(token, Request())  # type: ignore[no-untyped-call]
    except (ValueError, GoogleAuthError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="caller identity could not be verified",
        ) from exc
    principal = claims.get("email")
    if not principal:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="caller carries no principal claim"
        )
    return str(principal)


def _validate(payload: Escalation) -> None:
    if payload.source != "bastion":
        raise ValueError("untrusted escalation source")
    if payload.department not in {entry["id"] for entry in load_catalog()}:
        raise ValueError("unknown department")
    categories = validate_risk_categories(payload.risk_categories)
    if payload.summary != notification_summary(categories):
        raise ValueError("summary does not match the allowlisted risk categories")
    identifiers = validate_finding_ids(payload.finding_ids)
    if len(identifiers) != payload.finding_count:
        raise ValueError("finding_count does not match the number of distinct finding ids")


def _validate_approval(payload: ExceptionApproval) -> datetime:
    """Bound the approval in shape and in time before it can suppress anything."""
    if not OPAQUE_FINDING_ID.match(payload.finding_id):
        raise ValueError("finding id is not an opaque Auditor identifier")
    approved_until = payload.approved_until
    if approved_until.tzinfo is None:
        raise ValueError("approved_until must carry an explicit timezone")
    now = datetime.now(UTC)
    if approved_until <= now:
        raise ValueError("approved_until is already in the past")
    if approved_until > now + timedelta(days=MAX_APPROVAL_DAYS):
        raise ValueError(f"approved_until exceeds the {MAX_APPROVAL_DAYS}-day maximum")
    return approved_until


def record_escalation(idempotency_key: str, payload: Escalation) -> bool:
    """Create one immutable review record; repeated deliveries return success unchanged."""
    reference = _collection().document(idempotency_key)
    transaction = _client().transaction()

    @firestore.transactional
    def create(txn: Any) -> bool:
        if reference.get(transaction=txn).exists:
            return False
        txn.create(
            reference,
            {
                "investigation_id": payload.investigation_id,
                "department": payload.department,
                "finding_count": payload.finding_count,
                "finding_ids": validate_finding_ids(payload.finding_ids),
                "risk_categories": validate_risk_categories(payload.risk_categories),
                "summary": payload.summary,
                "received_at": datetime.now(UTC),
                "status": "needs_review",
            },
        )
        return True

    return bool(create(transaction))


@APP.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@APP.post("/v1/escalations", status_code=status.HTTP_202_ACCEPTED)
def accept_escalation(
    payload: Escalation, idempotency_key: str = Header(alias="Idempotency-Key")
) -> dict[str, object]:
    if not idempotency_key or len(idempotency_key) != 64:
        raise HTTPException(status_code=400, detail="a SHA-256 idempotency key is required")
    try:
        _validate(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "accepted": record_escalation(idempotency_key, payload),
        "department": payload.department,
    }


def record_approval(
    finding_id: str, approved_until: datetime, reviewer: str, policy_version: str
) -> None:
    """Write the exception the Orchestrator's suppression path reads.

    Deliberately a plain set rather than a transaction: re-approving the same finding with a new
    expiry is a legitimate renewal, and the document is keyed by finding id so a renewal replaces
    rather than accumulates.
    """
    _exceptions().document(finding_id).set(
        {
            "approved_until": approved_until.isoformat(),
            "reviewer": reviewer,
            "policy_version": policy_version,
        }
    )


@APP.post("/v1/exceptions", status_code=status.HTTP_201_CREATED)
def approve_exception(
    payload: ExceptionApproval, authorization: str | None = Header(default=None)
) -> dict[str, object]:
    """Approve one opaque finding for a bounded period, as a named human.

    This is the write side of the cross-week story. The Orchestrator already reads this ledger on
    every finding; until this endpoint existed, nothing in production wrote to it.
    """
    reviewer = caller_identity(authorization)
    try:
        approved_until = _validate_approval(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_approval(payload.finding_id, approved_until, reviewer, payload.policy_version)
    return {
        "finding_id": payload.finding_id,
        "approved_until": approved_until.isoformat(),
        "policy_version": payload.policy_version,
    }


def main() -> None:
    uvicorn.run(APP, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))  # noqa: S104


if __name__ == "__main__":
    main()
