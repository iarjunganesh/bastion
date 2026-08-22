"""The private human-review inbox accepts only Bastion's minimized schema."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import fastapi
import pytest

from infrastructure.findings_api import (
    Escalation,
    ExceptionApproval,
    _validate,
    _validate_approval,
    approve_exception,
    caller_identity,
)


def payload(**overrides: object) -> Escalation:
    values: dict[str, object] = {
        "source": "bastion",
        "investigation_id": "investigation-1",
        "department": "security-engineering",
        "finding_count": 1,
        "finding_ids": ["a1b2c3d4e5f60718293a4b5c"],
        "risk_categories": ["overly_broad_role"],
        "summary": "Access-review findings require attention: overly_broad_role",
    }
    values.update(overrides)
    return Escalation.model_validate(values)


def test_accepts_the_count_only_allowlisted_escalation_shape():
    _validate(payload())


@pytest.mark.parametrize(
    "change",
    [
        {"source": "untrusted"},
        {"department": "everyone"},
        {"risk_categories": ["free text"]},
        {"summary": "a model-supplied narrative"},
        {"finding_ids": ["not-an-opaque-id"]},
        {"finding_ids": []},
        {"finding_ids": ["a1b2c3d4e5f60718293a4b5c", "b1b2c3d4e5f60718293a4b5c"]},
    ],
)
def test_rejects_untrusted_routing_and_model_text(change: dict[str, object]):
    with pytest.raises(ValueError):
        _validate(payload(**change))


def approval(**overrides: object) -> ExceptionApproval:
    values: dict[str, object] = {
        "finding_id": "a1b2c3d4e5f60718293a4b5c",
        "approved_until": datetime.now(UTC) + timedelta(days=7),
        "policy_version": "policy-1",
    }
    values.update(overrides)
    return ExceptionApproval.model_validate(values)


def test_a_bounded_future_approval_is_accepted():
    assert _validate_approval(approval()).tzinfo is not None


@pytest.mark.parametrize(
    ("change", "because"),
    [
        ({"finding_id": "not-opaque"}, "a non-opaque id could name something other than a finding"),
        ({"approved_until": datetime.now(UTC) - timedelta(days=1)}, "already expired"),
        ({"approved_until": datetime.now(UTC) + timedelta(days=400)}, "beyond the 90-day cap"),
        ({"approved_until": datetime(2099, 1, 1)}, "naive datetimes are ambiguous"),  # noqa: DTZ001
    ],
)
def test_rejects_unbounded_or_unshaped_approvals(change: dict[str, object], because: str):
    with pytest.raises(ValueError):
        _validate_approval(approval(**change))


@pytest.mark.parametrize("header", [None, "", "Basic abc", "Bearer"])
def test_an_unauthenticated_caller_cannot_approve(header):
    """Approval is an accountable act; there is no anonymous path to it."""
    with pytest.raises(fastapi.HTTPException) as raised:
        caller_identity(header)
    assert raised.value.status_code == 401


def test_an_unverifiable_token_is_refused(monkeypatch):
    def reject(*_args, **_kwargs):
        raise ValueError("bad token")

    monkeypatch.setattr("infrastructure.findings_api.id_token.verify_oauth2_token", reject)
    with pytest.raises(fastapi.HTTPException) as raised:
        caller_identity("Bearer forged")
    assert raised.value.status_code == 401


def test_a_verified_token_without_a_principal_is_refused(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.findings_api.id_token.verify_oauth2_token",
        lambda *_a, **_k: {"sub": "123"},
    )
    with pytest.raises(fastapi.HTTPException) as raised:
        caller_identity("Bearer valid")
    assert raised.value.status_code == 403


def test_the_reviewer_is_the_verified_caller_not_a_request_field(monkeypatch):
    """The whole point of the endpoint: identity is observed, never asserted."""
    monkeypatch.setattr(
        "infrastructure.findings_api.id_token.verify_oauth2_token",
        lambda *_a, **_k: {"email": "reviewer@example.com"},
    )
    written: dict[str, object] = {}
    monkeypatch.setattr(
        "infrastructure.findings_api.record_approval",
        lambda finding_id, approved_until, reviewer, policy_version: written.update(
            finding_id=finding_id, reviewer=reviewer, policy_version=policy_version
        ),
    )
    result = approve_exception(approval(), authorization="Bearer valid")
    assert written["reviewer"] == "reviewer@example.com"
    assert result["finding_id"] == "a1b2c3d4e5f60718293a4b5c"


def test_an_invalid_approval_becomes_a_400_not_a_crash(monkeypatch):
    monkeypatch.setattr(
        "infrastructure.findings_api.id_token.verify_oauth2_token",
        lambda *_a, **_k: {"email": "reviewer@example.com"},
    )
    with pytest.raises(fastapi.HTTPException) as raised:
        approve_exception(approval(finding_id="not-opaque"), authorization="Bearer valid")
    assert raised.value.status_code == 400
