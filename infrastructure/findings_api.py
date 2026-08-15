"""Private, count-only human-review inbox for Bastion escalations.

This is deliberately a tiny Cloud Run service rather than a webhook dependency.  The
Escalation Agent can write one redacted, idempotent review record; humans with project access
can inspect the Firestore-backed inbox, while the service has no IAM-policy read capability.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

import uvicorn
from fastapi import FastAPI, Header, HTTPException, status
from google.cloud import firestore
from pydantic import BaseModel, Field

from model_armor.redaction import notification_summary, validate_risk_categories
from registry.departments import load_catalog

APP = FastAPI(title="Bastion findings inbox", docs_url=None, redoc_url=None)
COLLECTION = "bastion_human_review"


class Escalation(BaseModel):
    source: str
    investigation_id: str
    department: str
    finding_count: int = Field(gt=0)
    risk_categories: list[str]
    summary: str


@lru_cache(maxsize=1)
def _client() -> Any:  # pragma: no cover - Cloud Run wires ADC and Firestore
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    return firestore.Client(project=project)


def _collection() -> Any:  # pragma: no cover - Cloud Run wires ADC and Firestore
    return _client().collection(COLLECTION)


def _validate(payload: Escalation) -> None:
    if payload.source != "bastion":
        raise ValueError("untrusted escalation source")
    if payload.department not in {entry["id"] for entry in load_catalog()}:
        raise ValueError("unknown department")
    categories = validate_risk_categories(payload.risk_categories)
    if payload.summary != notification_summary(categories):
        raise ValueError("summary does not match the allowlisted risk categories")


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


def main() -> None:
    uvicorn.run(APP, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))  # noqa: S104


if __name__ == "__main__":
    main()
