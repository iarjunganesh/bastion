"""The Escalation Agent notifies without ever holding what it escalates."""

from __future__ import annotations

import inspect
from hashlib import sha256
from unittest.mock import patch

import httpx
import pytest

from agents.escalation_agent import agent as escalation


@pytest.fixture
def _endpoint():
    with patch.dict(
        "os.environ",
        {escalation.NOTIFY_ENDPOINT_VAR: "https://findings.example.com/v1/escalations"},
    ):
        yield


def test_posts_when_something_needs_review(_endpoint):
    with patch.object(escalation.httpx, "Client") as client:
        result = escalation.notify_human(
            "investigation-1", 3, ["overly_broad_role"], "data-platform"
        )

    assert result == {"delivered": True, "department": "data-platform", "count": 3}
    posted = client.return_value.__enter__.return_value.post
    body = posted.call_args.kwargs["json"]
    # A typed body, not a sentence: a free-text field is where principal identifiers end up.
    assert body == {
        "source": "bastion",
        "investigation_id": "investigation-1",
        "department": "data-platform",
        "finding_count": 3,
        "risk_categories": ["overly_broad_role"],
        "summary": "Access-review findings require attention: overly_broad_role",
    }
    assert posted.call_args.kwargs["headers"] == {
        "Idempotency-Key": sha256(b"investigation-1:data-platform").hexdigest()
    }


def test_silent_when_nothing_is_escalated(_endpoint):
    """An access review that pages a human on a clean run is one people turn off."""
    with patch.object(escalation.httpx, "Client") as client:
        result = escalation.notify_human("investigation-1", 0, [], "data-platform")

    assert result["delivered"] is False
    client.assert_not_called()


def test_missing_endpoint_fails_closed_for_the_outbox():
    """A worker must retain and retry delivery, not silently report it as skipped."""
    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(escalation.httpx, "Client") as c,
        pytest.raises(RuntimeError, match="BASTION_FINDINGS_ENDPOINT"),
    ):
        escalation.notify_human("investigation-1", 2, ["overly_broad_role"], "platform-infra")
    c.assert_not_called()


def test_the_client_carries_an_explicit_timeout(_endpoint):
    with patch.object(escalation.httpx, "Client") as client:
        escalation.notify_human("investigation-1", 1, ["overly_broad_role"], "security-engineering")

    timeout = client.call_args.kwargs["timeout"]
    assert isinstance(timeout, httpx.Timeout)
    assert timeout.connect == 3.0


def test_retries_cover_connection_failures_only(_endpoint):
    """httpx will not replay an already-sent request, which is right for a non-idempotent POST.

    Retrying a delivered notification would page a human twice for one finding.
    """
    with (
        patch.object(escalation.httpx, "Client"),
        patch.object(escalation.httpx, "HTTPTransport") as transport,
    ):
        escalation.notify_human("investigation-1", 1, ["overly_broad_role"], "security-engineering")

    assert transport.call_args.kwargs["retries"] == escalation.NOTIFY_RETRIES


def test_the_tool_cannot_be_handed_bindings():
    """The signature is the control: it takes a count, so there is nothing to leak.

    A compromised prompt cannot talk this tool into forwarding a principal identifier, because
    the tool is never given one.
    """
    params = inspect.signature(escalation.notify_human).parameters
    assert list(params) == [
        "investigation_id",
        "finding_count",
        "risk_categories",
        "department",
    ]
    # A string, not the type: `from __future__ import annotations` defers evaluation, so the
    # module's own annotations arrive here unresolved.
    assert params["finding_count"].annotation == "int"


def test_notification_rejects_model_supplied_text_and_unknown_categories(_endpoint):
    with pytest.raises(ValueError, match="investigation_id"):
        escalation.notify_human("", 1, ["overly_broad_role"], "security-engineering")
    with pytest.raises(ValueError, match="unknown or unsafe"):
        escalation.notify_human("investigation-1", 1, ["free text"], "security-engineering")


def test_the_module_holds_no_policy_client():
    """Zero-trust asserted offline, until a deployed service account can be denied for real.

    A client this module does not import is a capability an injected instruction cannot reach
    for. When the live 403 can be captured, that evidence replaces this test rather than
    deleting it (ADR-006).
    """
    source = inspect.getsource(escalation)
    for forbidden in ("asset_v1", "AssetServiceClient", "get_iam_policy", "securityReviewer"):
        assert forbidden not in source


def test_the_agent_is_an_adk_agent_with_the_guardrail_attached():
    from model_armor.guardrails import screen_after_model, screen_before_model

    assert escalation.escalation_agent.name == "escalation_agent"
    assert escalation.escalation_agent.before_model_callback is screen_before_model
    assert escalation.escalation_agent.after_model_callback is screen_after_model


def test_the_instruction_forbids_naming_principals():
    instruction = escalation.INSTRUCTION.lower()
    assert "never include email addresses" in instruction
