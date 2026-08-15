"""Durable, idempotent investigation state backed by SQLite locally.

The schema is intentionally portable: the production adapter maps these records to Firestore
and Pub/Sub without changing event IDs, state transitions, or outbox semantics.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID


def now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True, slots=True)
class InvestigationEvent:
    event_id: str
    context_id: str
    schema_version: int = 1
    classification: str = "internal"

    def __post_init__(self) -> None:
        UUID(self.event_id)
        if not self.context_id or self.schema_version != 1 or self.classification != "internal":
            raise ValueError("invalid investigation event")


class DurableStore:
    """Inbox, state machine, approved-exception memory, and idempotent delivery outbox."""

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS investigations (
              event_id TEXT PRIMARY KEY, context_id TEXT NOT NULL, payload TEXT NOT NULL,
              status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS outbox (
              delivery_key TEXT PRIMARY KEY, event_id TEXT NOT NULL, payload TEXT NOT NULL,
              status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT);
            CREATE TABLE IF NOT EXISTS exceptions (
              finding_id TEXT PRIMARY KEY, approved_until TEXT NOT NULL, reviewer TEXT NOT NULL,
              policy_version TEXT NOT NULL);
            """
        )

    def receive(self, event: InvestigationEvent) -> bool:
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO investigations VALUES (?, ?, ?, 'received', 0, ?)",
            (event.event_id, event.context_id, json.dumps(asdict(event)), now()),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def claim(self, event_id: str) -> bool:
        cursor = self.connection.execute(
            "UPDATE investigations SET status='running', attempts=attempts+1, updated_at=? "
            "WHERE event_id=? AND status IN ('received', 'failed')",
            (now(), event_id),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def finish(self, event_id: str, *, failed: bool = False) -> None:
        status = "failed" if failed else "completed"
        cursor = self.connection.execute(
            "UPDATE investigations SET status=?, updated_at=? "
            "WHERE event_id=? AND status='running'",
            (status, now(), event_id),
        )
        self.connection.commit()
        if cursor.rowcount != 1:
            raise ValueError("invalid investigation transition")

    def enqueue(self, delivery_key: str, event_id: str, payload: dict[str, object]) -> bool:
        cursor = self.connection.execute(
            "INSERT OR IGNORE INTO outbox VALUES (?, ?, ?, 'pending', 0, NULL)",
            (delivery_key, event_id, json.dumps(payload, sort_keys=True)),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def pending(self) -> list[dict[str, object]]:
        rows = self.connection.execute("SELECT * FROM outbox WHERE status='pending'").fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]

    def delivered(self, delivery_key: str) -> None:
        self._outbox_transition(delivery_key, "delivered", None)

    def retry(self, delivery_key: str, error: Exception, *, max_attempts: int = 3) -> None:
        row = self.connection.execute(
            "SELECT attempts FROM outbox WHERE delivery_key=?", (delivery_key,)
        ).fetchone()
        if row is None:
            raise ValueError("unknown delivery")
        status = "dead_letter" if row["attempts"] + 1 >= max_attempts else "pending"
        self.connection.execute(
            "UPDATE outbox SET status=?, attempts=attempts+1, last_error=? WHERE delivery_key=?",
            (status, type(error).__name__, delivery_key),
        )
        self.connection.commit()

    def approve(
        self, finding_id: str, approved_until: str, reviewer: str, policy_version: str
    ) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO exceptions VALUES (?, ?, ?, ?)",
            (finding_id, approved_until, reviewer, policy_version),
        )
        self.connection.commit()

    def is_approved(self, finding_id: str, at: str | None = None) -> bool:
        row = self.connection.execute(
            "SELECT approved_until FROM exceptions WHERE finding_id=?", (finding_id,)
        ).fetchone()
        return row is not None and row["approved_until"] > (at or now())

    def _outbox_transition(self, delivery_key: str, status: str, error: str | None) -> None:
        cursor = self.connection.execute(
            "UPDATE outbox SET status=?, last_error=? WHERE delivery_key=? AND status='pending'",
            (status, error, delivery_key),
        )
        self.connection.commit()
        if cursor.rowcount != 1:
            raise ValueError("invalid delivery transition")

    def close(self) -> None:
        self.connection.close()
