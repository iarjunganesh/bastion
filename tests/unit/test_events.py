"""Pub/Sub events receive stable identities and reject malformed payloads."""

from __future__ import annotations

import base64
import json

import pytest

from runtime.events import decode_pubsub_event, new_investigation_payload
from runtime.firestore import _now


def _envelope(
    payload: object,
    cloud_event_id: str = "pubsub-message-123",
) -> dict:
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return {"id": cloud_event_id, "data": {"message": {"data": encoded}}}


def test_decoded_pubsub_event_preserves_context_and_delivery_identity():
    event = decode_pubsub_event(
        _envelope({"event_id": "00000000-0000-0000-0000-000000000001", "context_id": "week-42"})
    )
    assert event.event_id == "00000000-0000-0000-0000-000000000001"
    assert event.context_id == "week-42"


@pytest.mark.parametrize(
    "envelope",
    [
        {},
        {"id": "x"},
        {"data": {"message": {"data": "e30="}}},
        _envelope([]),
        _envelope({"context_id": "x"}, cloud_event_id="not-a-uuid"),
    ],
)
def test_invalid_pubsub_envelopes_are_rejected(envelope):
    with pytest.raises(ValueError):
        decode_pubsub_event(envelope)


def test_invalid_pubsub_encoding_and_context_are_rejected():
    with pytest.raises(ValueError):
        decode_pubsub_event({"id": "x", "data": {"message": {"data": "not*base64"}}})
    with pytest.raises(ValueError):
        decode_pubsub_event(_envelope({}))


def test_new_payload_has_separate_context_and_event_identities():
    payload = new_investigation_payload(mock_data=True)
    assert payload["event_id"] != payload["context_id"]
    assert payload["classification"] == "internal"
    assert payload["mock_data"] is True


def test_firestore_clock_is_timezone_aware():
    assert _now().tzinfo is not None
