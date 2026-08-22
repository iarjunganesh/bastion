"""The private human-review inbox accepts only Bastion's minimized schema."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import fastapi
import pytest

from infrastructure.findings_api import (
    APPROVER_IDENTITY_VAR,
    APPROVER_PRINCIPAL_VAR,
    Escalation,
    ExceptionApproval,
    _validate,
    _validate_approval,
    approve_exception,
    authorize_approver,
    caller_identity,
)

APPROVER = "approver-sa@bastion-fleet-2026.iam.gserviceaccount.com"
HUMAN = "user:reviewer@example.com"


@pytest.fixture
def configured_approver(monkeypatch):
    """Deployment has named an approver identity and the human permitted to wield it."""
    monkeypatch.setenv(APPROVER_IDENTITY_VAR, APPROVER)
    monkeypatch.setenv(APPROVER_PRINCIPAL_VAR, HUMAN)


def as_caller(monkeypatch, principal: str) -> None:
    monkeypatch.setattr(
        "infrastructure.findings_api.id_token.verify_oauth2_token",
        lambda *_a, **_k: {"email": principal},
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


def test_the_reviewer_is_the_verified_caller_not_a_request_field(monkeypatch, configured_approver):
    """The whole point of the endpoint: identity is observed, never asserted."""
    as_caller(monkeypatch, APPROVER)
    written: dict[str, object] = {}
    monkeypatch.setattr(
        "infrastructure.findings_api.record_approval",
        lambda finding_id, approved_until, reviewer, policy_version, on_behalf_of: written.update(
            finding_id=finding_id,
            reviewer=reviewer,
            policy_version=policy_version,
            on_behalf_of=on_behalf_of,
        ),
    )
    result = approve_exception(approval(), authorization="Bearer valid")
    assert written["reviewer"] == APPROVER
    # The credential that authenticated is the approver identity; the ledger still names the
    # person it was wielded on behalf of, taken from deployment config rather than the caller.
    assert written["on_behalf_of"] == HUMAN
    assert result["finding_id"] == "a1b2c3d4e5f60718293a4b5c"


def test_a_reachable_non_approver_cannot_approve(monkeypatch, configured_approver):
    """Regression: every worker identity holds run.invoker on this service.

    The Escalation Agent must reach the API to post a review record. If reachability were the
    authorization, the agent that raises a finding could approve its own suppression.
    """
    as_caller(monkeypatch, "escalation-agent-sa@bastion-fleet-2026.iam.gserviceaccount.com")
    with pytest.raises(fastapi.HTTPException) as raised:
        approve_exception(approval(), authorization="Bearer valid")
    assert raised.value.status_code == 403


def test_an_unconfigured_approver_refuses_rather_than_admits(monkeypatch):
    """No configured approver is a closed door, not an open one."""
    monkeypatch.delenv(APPROVER_IDENTITY_VAR, raising=False)
    monkeypatch.delenv(APPROVER_PRINCIPAL_VAR, raising=False)
    as_caller(monkeypatch, APPROVER)
    with pytest.raises(fastapi.HTTPException) as raised:
        authorize_approver("Bearer valid")
    assert raised.value.status_code == 503


def test_a_half_configured_approver_also_refuses(monkeypatch):
    """An identity with nobody accountable behind it is not an approval path."""
    monkeypatch.setenv(APPROVER_IDENTITY_VAR, APPROVER)
    monkeypatch.delenv(APPROVER_PRINCIPAL_VAR, raising=False)
    as_caller(monkeypatch, APPROVER)
    with pytest.raises(fastapi.HTTPException) as raised:
        authorize_approver("Bearer valid")
    assert raised.value.status_code == 503


def test_an_invalid_approval_becomes_a_400_not_a_crash(monkeypatch, configured_approver):
    as_caller(monkeypatch, APPROVER)
    with pytest.raises(fastapi.HTTPException) as raised:
        approve_exception(approval(finding_id="not-opaque"), authorization="Bearer valid")
    assert raised.value.status_code == 400
