"""Firestore implementation of the Bastion durable-state contract.

The local SQLite store is used for fast tests.  This adapter is deliberately a separate
implementation because a Cloud Run instance's disk is ephemeral: a successful retry or
idempotency decision must survive restarts and weeks between human approvals.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any

from google.cloud import firestore

from runtime.durable import InvestigationEvent


def _now() -> datetime:  # pragma: no cover - exercised against the Firestore emulator
    return datetime.now(UTC)


class FirestoreDurableStore:  # pragma: no cover - requires the Firestore emulator in integration CI
    """Atomic inbox/outbox/exception state machine in one EU Firestore database."""

    def __init__(self, project_id: str, database: str = "(default)") -> None:
        self.client = firestore.Client(project=project_id, database=database)
        self.investigations = self.client.collection("bastion_investigations")
        self.outbox = self.client.collection("bastion_outbox")
        self.exceptions = self.client.collection("bastion_exceptions")

    def receive(self, event: InvestigationEvent) -> bool:
        reference = self.investigations.document(event.event_id)
        transaction = self.client.transaction()

        @firestore.transactional
        def insert(transaction: Any) -> bool:
            if reference.get(transaction=transaction).exists:
                return False
            transaction.create(
                reference,
                {"event": asdict(event), "status": "received", "attempts": 0, "updated_at": _now()},
            )
            return True

        return bool(insert(transaction))

    def claim(self, event_id: str) -> bool:
        reference = self.investigations.document(event_id)
        transaction = self.client.transaction()

        @firestore.transactional
        def transition(transaction: Any) -> bool:
            snapshot = reference.get(transaction=transaction)
            if not snapshot.exists or snapshot.get("status") != "received":
                return False
            transaction.update(
                reference,
                {"status": "running", "attempts": firestore.Increment(1), "updated_at": _now()},
            )
            return True

        return bool(transition(transaction))

    def finish(self, event_id: str, *, failed: bool = False) -> None:
        reference = self.investigations.document(event_id)
        transaction = self.client.transaction()

        @firestore.transactional
        def transition(transaction: Any) -> None:
            snapshot = reference.get(transaction=transaction)
            if not snapshot.exists or snapshot.get("status") != "running":
                raise ValueError("invalid investigation transition")
            transaction.update(
                reference,
                {"status": "failed" if failed else "completed", "updated_at": _now()},
            )

        transition(transaction)

    def enqueue(self, delivery_key: str, event_id: str, payload: dict[str, object]) -> bool:
        reference = self.outbox.document(delivery_key)
        transaction = self.client.transaction()

        @firestore.transactional
        def insert(transaction: Any) -> bool:
            if reference.get(transaction=transaction).exists:
                return False
            transaction.create(
                reference,
                {"event_id": event_id, "payload": payload, "status": "pending", "attempts": 0},
            )
            return True

        return bool(insert(transaction))

    def delivered(self, delivery_key: str) -> None:
        self._outbox_transition(delivery_key, "delivered", None)

    def retry(self, delivery_key: str, error: Exception, *, max_attempts: int = 3) -> None:
        reference = self.outbox.document(delivery_key)
        transaction = self.client.transaction()

        @firestore.transactional
        def transition(transaction: Any) -> None:
            snapshot = reference.get(transaction=transaction)
            if not snapshot.exists:
                raise ValueError("unknown delivery")
            attempts = int(snapshot.get("attempts") or 0) + 1
            transaction.update(
                reference,
                {
                    "status": "dead_letter" if attempts >= max_attempts else "pending",
                    "attempts": attempts,
                    "last_error": type(error).__name__,
                },
            )

        transition(transaction)

    def approve(
        self, finding_id: str, approved_until: str, reviewer: str, policy_version: str
    ) -> None:
        self.exceptions.document(finding_id).set(
            {
                "approved_until": approved_until,
                "reviewer": reviewer,
                "policy_version": policy_version,
            }
        )

    def is_approved(self, finding_id: str, at: str | None = None) -> bool:
        snapshot = self.exceptions.document(finding_id).get()
        return bool(snapshot.exists and snapshot.get("approved_until") > (at or _now().isoformat()))

    def _outbox_transition(self, delivery_key: str, status: str, error: str | None) -> None:
        reference = self.outbox.document(delivery_key)
        transaction = self.client.transaction()

        @firestore.transactional
        def transition(transaction: Any) -> None:
            snapshot = reference.get(transaction=transaction)
            if not snapshot.exists or snapshot.get("status") != "pending":
                raise ValueError("invalid delivery transition")
            transaction.update(reference, {"status": status, "last_error": error})

        transition(transaction)
