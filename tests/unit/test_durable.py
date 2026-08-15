"""Durable investigation state rejects duplicates and preserves failed delivery."""

from __future__ import annotations

from uuid import uuid4

import pytest

from runtime.durable import DurableStore, InvestigationEvent


@pytest.fixture
def store(tmp_path):
    value = DurableStore(tmp_path / "state.db")
    yield value
    value.close()


def event() -> InvestigationEvent:
    return InvestigationEvent(str(uuid4()), "context-1")


def test_event_requires_a_uuid_and_supported_contract():
    with pytest.raises(ValueError):
        InvestigationEvent("not-a-uuid", "context")
    with pytest.raises(ValueError):
        InvestigationEvent(str(uuid4()), "", classification="public")


def test_inbox_claim_and_completion_are_exactly_once(store):
    item = event()
    assert store.receive(item)
    assert not store.receive(item)
    assert store.claim(item.event_id)
    assert not store.claim(item.event_id)
    store.finish(item.event_id)
    with pytest.raises(ValueError):
        store.finish(item.event_id)


def test_failed_investigation_is_recorded(store):
    item = event()
    store.receive(item)
    store.claim(item.event_id)
    store.finish(item.event_id, failed=True)
    # Eventarc retries the same CloudEvent after a 5xx. A recorded failure must be
    # claimable again, while completed/running work remains exactly-once.
    assert store.claim(item.event_id)
    store.finish(item.event_id)


def test_outbox_is_idempotent_and_dead_letters_after_bounded_retries(store):
    item = event()
    store.receive(item)
    assert store.enqueue("delivery-1", item.event_id, {"department": "security-engineering"})
    assert not store.enqueue("delivery-1", item.event_id, {})
    assert store.pending()[0]["payload"] == {"department": "security-engineering"}
    store.retry("delivery-1", RuntimeError())
    store.retry("delivery-1", RuntimeError())
    store.retry("delivery-1", RuntimeError())
    assert store.pending() == []
    with pytest.raises(ValueError):
        store.delivered("delivery-1")


def test_outbox_can_be_marked_delivered(store):
    item = event()
    store.receive(item)
    store.enqueue("delivery-1", item.event_id, {})
    store.delivered("delivery-1")
    assert store.pending() == []


def test_unknown_delivery_cannot_be_retried(store):
    with pytest.raises(ValueError):
        store.retry("missing", RuntimeError())


def test_approved_exception_expires(store):
    store.approve("finding-1", "2099-01-01T00:00:00+00:00", "reviewer-1", "policy-1")
    assert store.is_approved("finding-1")
    assert not store.is_approved("finding-1", at="2100-01-01T00:00:00+00:00")
