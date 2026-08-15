"""Cross-module durable investigation contract, without GCP credentials."""

from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from agents.escalation_agent import agent as escalation
from runtime.durable import DurableStore, InvestigationEvent


def test_duplicate_delivery_produces_one_durable_notification(tmp_path, monkeypatch):
    """A replay after process loss cannot create another human escalation."""
    store = DurableStore(tmp_path / "investigations.db")
    event = InvestigationEvent(str(uuid4()), "cross-week-context")
    assert store.receive(event)
    assert not store.receive(event)
    assert store.claim(event.event_id)
    assert store.enqueue(
        "notice-security-engineering", event.event_id, {"department": "security-engineering"}
    )
    assert not store.enqueue(
        "notice-security-engineering", event.event_id, {"department": "security-engineering"}
    )

    posted: list[dict[str, object]] = []

    class Response:
        def raise_for_status(self) -> None:
            return None

    class Client:
        def __init__(self, **_: object) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def post(self, _: str, *, headers: dict[str, str], json: dict[str, object]) -> Response:
            posted.append({"idempotency_key": headers["Idempotency-Key"], **json})
            return Response()

    monkeypatch.setenv(escalation.NOTIFY_ENDPOINT_VAR, "https://findings.example.test")
    monkeypatch.setattr(escalation.httpx, "Client", Client)
    result = escalation.notify_human(
        investigation_id=event.event_id,
        finding_count=1,
        risk_categories=["overly_broad_role"],
        department="security-engineering",
    )
    store.delivered("notice-security-engineering")
    store.finish(event.event_id)
    store.close()

    assert result["delivered"] is True
    assert posted == [
        {
            "idempotency_key": sha256(
                f"{event.event_id}:security-engineering".encode()
            ).hexdigest(),
            "source": "bastion",
            "investigation_id": event.event_id,
            "department": "security-engineering",
            "finding_count": 1,
            "risk_categories": ["overly_broad_role"],
            "summary": "Access-review findings require attention: overly_broad_role",
        }
    ]
