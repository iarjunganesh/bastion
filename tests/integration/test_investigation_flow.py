"""Cross-module durable investigation contract, without GCP credentials."""

from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from agents.escalation_agent import agent as escalation
from agents.orchestrator import agent as orchestrator
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
        finding_ids=["a1b2c3d4e5f60718293a4b5c"],
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
            "finding_ids": ["a1b2c3d4e5f60718293a4b5c"],
            "risk_categories": ["overly_broad_role"],
            "summary": "Access-review findings require attention: overly_broad_role",
        }
    ]


def test_restart_reclaims_work_and_preserves_cross_week_exception(tmp_path):
    """A killed worker is recoverable without forgetting a prior approved exception."""
    database = tmp_path / "investigations.db"
    event = InvestigationEvent(str(uuid4()), "week-2-context")

    first_process = DurableStore(database)
    first_process.approve(
        "opaque-finding-1",
        "2099-01-01T00:00:00+00:00",
        "reviewer-ticket-42",
        "iam-policy-v3",
    )
    assert first_process.receive(event)
    assert first_process.claim(event.event_id, lease_seconds=1)
    assert first_process.enqueue(
        "notice-security-engineering",
        event.event_id,
        {"department": "security-engineering"},
    )
    # Simulate abrupt process loss: no finish and no delivered transition.
    first_process.connection.execute(
        "UPDATE investigations SET lease_until=? WHERE event_id=?",
        ("2000-01-01T00:00:00+00:00", event.event_id),
    )
    first_process.connection.commit()
    first_process.close()

    restarted = DurableStore(database)
    assert restarted.claim(event.event_id)
    assert restarted.approved_exception("opaque-finding-1", at="2098-01-01T00:00:00+00:00") == {
        "approved_until": "2099-01-01T00:00:00+00:00",
        "reviewer": "reviewer-ticket-42",
        "policy_version": "iam-policy-v3",
    }
    suppressed = orchestrator.apply_policy_rules_with_memory(
        [
            {
                "finding_id": "opaque-finding-1",
                "department": "security-engineering",
                "reason": "overly_broad_role",
                "risk_score": 0.9,
            }
        ],
        restarted,
    )
    assert suppressed["suppress_count"] == 1
    assert suppressed["escalate_count"] == 0
    assert [item["delivery_key"] for item in restarted.pending()] == ["notice-security-engineering"]
    assert not restarted.enqueue("notice-security-engineering", event.event_id, {})
    restarted.delivered("notice-security-engineering")
    restarted.finish(event.event_id)
    restarted.close()

    final_process = DurableStore(database)
    assert not final_process.receive(event)
    assert not final_process.claim(event.event_id)
    assert final_process.status(event.event_id) == "completed"
    assert final_process.pending() == []
    final_process.close()
