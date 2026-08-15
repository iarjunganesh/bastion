"""Schema validation and exactly-once admission for Pub/Sub investigations."""

from __future__ import annotations

import base64
import json
from typing import Any, Protocol
from uuid import uuid4

from runtime.durable import InvestigationEvent


class Inbox(Protocol):  # pragma: no cover - type-only adapter contract
    def receive(self, event: InvestigationEvent) -> bool: ...


def decode_pubsub_event(envelope: dict[str, Any]) -> InvestigationEvent:
    """Validate the CloudEvents-shaped Pub/Sub envelope before it reaches an agent."""
    event_id = str(envelope.get("id") or "")
    encoded = envelope.get("data", {}).get("message", {}).get("data")
    if not event_id:
        raise ValueError("missing Pub/Sub event id or message data")
    if not isinstance(encoded, str):
        raise ValueError("missing Pub/Sub event id or message data")
    try:
        payload = json.loads(base64.b64decode(encoded, validate=True))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid Pub/Sub payload") from exc
    if not isinstance(payload, dict):
        raise ValueError("Pub/Sub payload must be an object")
    context_id = payload.get("context_id")
    if not isinstance(context_id, str) or not context_id:
        raise ValueError("context_id is required")
    return InvestigationEvent(event_id=event_id, context_id=context_id)


def new_investigation_payload(*, mock_data: bool) -> dict[str, object]:
    """Create an explicit event identity; Pub/Sub publish acknowledgement is awaited by caller."""
    return {
        "event_id": str(uuid4()),
        "context_id": str(uuid4()),
        "schema_version": 1,
        "classification": "internal",
        "mock_data": mock_data,
    }
