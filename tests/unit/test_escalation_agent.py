"""The Escalation Agent notifies without ever holding what it escalates."""

from __future__ import annotations

import asyncio
import inspect
import json
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest

from agents.escalation_agent import agent as escalation
from observability.audit import INVESTIGATION_METADATA_KEY


@pytest.fixture
def _endpoint():
    with patch.dict(
        "os.environ",
        {escalation.NOTIFY_ENDPOINT_VAR: "https://findings.example.com/v1/escalations"},
    ):
        yield


FINDING_IDS = [
    "a1b2c3d4e5f60718293a4b5c",
    "b1b2c3d4e5f60718293a4b5c",
    "c1b2c3d4e5f60718293a4b5c",
]


def test_posts_when_something_needs_review(_endpoint):
    with patch.object(escalation.httpx, "Client") as client:
        result = escalation.notify_human(
            "investigation-1",
            3,
            ["overly_broad_role"],
            "data-platform",
            ["a1b2c3d4e5f60718293a4b5c", "b1b2c3d4e5f60718293a4b5c", "c1b2c3d4e5f60718293a4b5c"],
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
        "finding_ids": [
            "a1b2c3d4e5f60718293a4b5c",
            "b1b2c3d4e5f60718293a4b5c",
            "c1b2c3d4e5f60718293a4b5c",
        ],
        "risk_categories": ["overly_broad_role"],
        "summary": "Access-review findings require attention: overly_broad_role",
    }
    assert posted.call_args.kwargs["headers"] == {
        "Idempotency-Key": sha256(b"investigation-1:data-platform").hexdigest()
    }


def test_silent_when_nothing_is_escalated(_endpoint):
    """An access review that pages a human on a clean run is one people turn off."""
    with patch.object(escalation.httpx, "Client") as client:
        result = escalation.notify_human("investigation-1", 0, [], "data-platform", [])

    assert result["delivered"] is False
    client.assert_not_called()


def test_missing_endpoint_fails_closed_for_the_outbox():
    """A worker must retain and retry delivery, not silently report it as skipped."""
    with (
        patch.dict("os.environ", {}, clear=True),
        patch.object(escalation.httpx, "Client") as c,
        pytest.raises(RuntimeError, match="BASTION_FINDINGS_ENDPOINT"),
    ):
        escalation.notify_human(
            "investigation-1",
            2,
            ["overly_broad_role"],
            "platform-infra",
            ["a1b2c3d4e5f60718293a4b5c", "b1b2c3d4e5f60718293a4b5c"],
        )
    c.assert_not_called()


def test_the_client_carries_an_explicit_timeout(_endpoint):
    with patch.object(escalation.httpx, "Client") as client:
        escalation.notify_human(
            "investigation-1",
            1,
            ["overly_broad_role"],
            "security-engineering",
            ["a1b2c3d4e5f60718293a4b5c"],
        )

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
        escalation.notify_human(
            "investigation-1",
            1,
            ["overly_broad_role"],
            "security-engineering",
            ["a1b2c3d4e5f60718293a4b5c"],
        )

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
        "finding_ids",
    ]
    # A string, not the type: `from __future__ import annotations` defers evaluation, so the
    # module's own annotations arrive here unresolved.
    assert params["finding_count"].annotation == "int"


def test_notification_rejects_model_supplied_text_and_unknown_categories(_endpoint):
    with pytest.raises(ValueError, match="investigation_id"):
        escalation.notify_human(
            "", 1, ["overly_broad_role"], "security-engineering", ["a1b2c3d4e5f60718293a4b5c"]
        )
    with pytest.raises(ValueError, match="unknown or unsafe"):
        escalation.notify_human(
            "investigation-1",
            1,
            ["free text"],
            "security-engineering",
            ["a1b2c3d4e5f60718293a4b5c"],
        )


def test_the_module_holds_no_policy_client():
    """Zero-trust asserted offline, until a deployed service account can be denied for real.

    A client this module does not import is a capability an injected instruction cannot reach
    for. When the live 403 can be captured, that evidence replaces this test rather than
    deleting it (ADR-006).
    """
    source = inspect.getsource(escalation)
    for forbidden in ("asset_v1", "AssetServiceClient", "get_iam_policy", "securityReviewer"):
        assert forbidden not in source


def test_the_module_holds_no_model_client():
    """P0.2: no model in the delivery path means nothing here for a compromised prompt to reach.

    There is no prompt at all -- Model Armor's callbacks and the model env var this module used
    to read are gone, not merely unused. (`LlmAgent` itself still appears in prose explaining
    what this replaced, so that word is not part of this check.)
    """
    source = inspect.getsource(escalation)
    for forbidden in ("screen_before_model", "screen_after_model", "VERTEX_AI_MODEL"):
        assert forbidden not in source
    assert "import LlmAgent" not in source


def test_the_agent_is_a_deterministic_adk_agent_with_no_model():
    from google.adk.agents import BaseAgent, LlmAgent

    assert escalation.escalation_agent.name == "escalation_agent"
    assert isinstance(escalation.escalation_agent, BaseAgent)
    assert not isinstance(escalation.escalation_agent, LlmAgent)


def test_the_routing_key_matches_the_orchestrators():
    """Duplicated as a literal rather than imported (see the constant's own docstring);

    this is the drift guard for that duplication.
    """
    from agents.orchestrator import agent as orchestrator

    assert escalation.POLICY_ROUTING_KEY == orchestrator.POLICY_ROUTING_KEY


def test_a_count_that_disagrees_with_its_finding_ids_is_refused(_endpoint):
    """Inflating the count past the ids it claims to summarise never reaches a human."""
    with (
        patch.object(escalation.httpx, "Client") as client,
        pytest.raises(ValueError, match="finding_count does not match"),
    ):
        escalation.notify_human(
            "investigation-1", 5, ["overly_broad_role"], "data-platform", [FINDING_IDS[0]]
        )
    client.assert_not_called()


# --- P0.2: deterministic delivery -- no model decides whether or which department is notified -


def _bucket(department: str = "data-platform", finding_ids: list | None = None) -> dict:
    ids = finding_ids if finding_ids is not None else [FINDING_IDS[0]]
    return {
        "department": department,
        "finding_count": len(ids),
        "finding_ids": ids,
        "reasons": ["overly_broad_role"],
    }


def test_routing_envelope_prefers_state_when_present():
    routing = {"departments": [_bucket()]}
    ctx = SimpleNamespace(session=SimpleNamespace(state={escalation.POLICY_ROUTING_KEY: routing}))
    assert escalation._routing_envelope(ctx) is routing


def test_routing_envelope_reads_the_inbound_turns_user_content():
    """The actual production fix: on the A2A callee side the inbound message is
    `ctx.user_content`, set by the Runner for the current turn -- not something already sitting
    in this worker's own session history, which is empty for a fresh A2A call. It also arrives
    wrapped as ADK's flattened multi-hop history -- `"[policy_step] said: {...}"`, not bare
    JSON -- which is the exact shape observed in production on 2026-08-23 causing every deployed
    escalation call to be rejected as `missing_routing_envelope` until both gaps were closed.
    """
    routing = {"departments": [_bucket()]}
    wrapped = f"[policy_step] said: {json.dumps(routing)}"
    ctx = SimpleNamespace(
        session=SimpleNamespace(state={}, events=[]),
        user_content=SimpleNamespace(
            parts=[
                SimpleNamespace(text='{"task": "scheduled_iam_access_review"}'),
                SimpleNamespace(text="For context:"),
                SimpleNamespace(text=wrapped),
            ]
        ),
    )
    assert escalation._routing_envelope(ctx) == routing


def test_parse_json_object_accepts_bare_json():
    assert escalation._parse_json_object('{"a": 1}') == {"a": 1}


def test_parse_json_object_strips_the_said_attribution_prefix():
    assert escalation._parse_json_object('[policy_step] said: {"a": 1}') == {"a": 1}


def test_parse_json_object_rejects_text_that_is_neither():
    assert escalation._parse_json_object("For context:") is None
    assert escalation._parse_json_object("[policy_step] said: not json") is None


def test_routing_envelope_prefers_state_over_user_content():
    """In-process, state is already the routing decision; user_content is the top-level
    investigation task, not this hop's envelope, and must not shadow the correct answer."""
    routing = {"departments": [_bucket()]}
    other_content = {"task": "scheduled_iam_access_review"}
    ctx = SimpleNamespace(
        session=SimpleNamespace(state={escalation.POLICY_ROUTING_KEY: routing}, events=[]),
        user_content=SimpleNamespace(parts=[SimpleNamespace(text=json.dumps(other_content))]),
    )
    assert escalation._routing_envelope(ctx) == routing


def test_routing_envelope_reads_the_inbound_message_by_shape():
    routing = {"departments": [_bucket()]}
    part = SimpleNamespace(text=json.dumps(routing))
    event = SimpleNamespace(content=SimpleNamespace(parts=[part]))
    ctx = SimpleNamespace(session=SimpleNamespace(state={}, events=[event]))
    assert escalation._routing_envelope(ctx) == routing


def test_routing_envelope_skips_empty_and_non_json_parts_before_the_real_one():
    routing = {"departments": [_bucket()]}
    empty_part = SimpleNamespace(text=None)
    prose_part = SimpleNamespace(text="not json")
    good_part = SimpleNamespace(text=json.dumps(routing))
    event = SimpleNamespace(content=SimpleNamespace(parts=[empty_part, prose_part, good_part]))
    ctx = SimpleNamespace(session=SimpleNamespace(state={}, events=[event]))
    assert escalation._routing_envelope(ctx) == routing


def test_routing_envelope_ignores_unrelated_content_and_returns_none():
    part = SimpleNamespace(text=json.dumps({"receipts": []}))
    event = SimpleNamespace(content=SimpleNamespace(parts=[part]))
    ctx = SimpleNamespace(session=SimpleNamespace(state={}, events=[event]))
    assert escalation._routing_envelope(ctx) is None
    assert escalation._routing_envelope(SimpleNamespace(session=SimpleNamespace(state={}))) is None


def test_validate_departments_accepts_a_faithful_envelope():
    validated = escalation._validate_departments({"departments": [_bucket()]})
    assert validated == [
        {
            "department": "data-platform",
            "finding_count": 1,
            "finding_ids": [FINDING_IDS[0]],
            "reasons": ["overly_broad_role"],
        }
    ]


def test_validate_departments_accepts_no_departments():
    assert escalation._validate_departments({"departments": []}) == []


@pytest.mark.parametrize(
    ("routing", "reason"),
    [
        (None, "missing_routing_envelope"),
        ({}, "missing_routing_envelope"),
        ({"departments": "not-a-list"}, "missing_routing_envelope"),
        ({"departments": ["not-a-dict"]}, "malformed_department_bucket"),
        ({"departments": [_bucket(), _bucket()]}, "duplicate_department_bucket"),
        ({"departments": [_bucket(department="not-a-real-department")]}, "unknown_department"),
        ({"departments": [_bucket(finding_ids=["not-opaque"])]}, "invalid_finding_id"),
        ({"departments": [_bucket(finding_ids=[])]}, "invalid_finding_id"),
        (
            {
                "departments": [
                    {**_bucket(), "reasons": ["not-a-real-reason"]},
                ]
            },
            "invalid_risk_category",
        ),
        ({"departments": [{**_bucket(), "finding_count": 0}]}, "count_mismatch"),
        ({"departments": [{**_bucket(), "finding_count": 2}]}, "count_mismatch"),
    ],
    ids=[
        "none",
        "empty-dict",
        "departments-not-a-list",
        "bucket-not-a-dict",
        "duplicate-bucket",
        "unknown-department",
        "malformed-id",
        "no-ids",
        "unsafe-reason",
        "zero-count",
        "count-does-not-match-ids",
    ],
)
def test_validate_departments_rejects_every_untrusted_shape(routing, reason):
    with pytest.raises(escalation.RoutingEnvelopeError, match=reason):
        escalation._validate_departments(routing)


INVESTIGATION_ID = "11111111-1111-1111-1111-111111111111"


def _ctx(
    state: dict | None = None,
    events: list | None = None,
    investigation_id: str | None = INVESTIGATION_ID,
) -> SimpleNamespace:
    metadata = {INVESTIGATION_METADATA_KEY: investigation_id} if investigation_id else {}
    return SimpleNamespace(
        session=SimpleNamespace(state=state or {}, events=events or []),
        invocation_id="inv-escalation",
        run_config=SimpleNamespace(custom_metadata=metadata),
    )


async def _drain(agent, ctx) -> list:
    return [event async for event in agent._run_async_impl(ctx)]


def test_delivers_every_routed_department_exactly_once(_endpoint):
    routing = {"departments": [_bucket("data-platform"), _bucket("ml-engineering")]}
    ctx = _ctx(state={escalation.POLICY_ROUTING_KEY: routing})
    with patch.object(escalation.httpx, "Client") as client:
        (event,) = asyncio.run(_drain(escalation.escalation_agent, ctx))

    assert client.return_value.__enter__.return_value.post.call_count == 2
    receipts = json.loads(event.content.parts[0].text)["receipts"]
    assert receipts == [
        {"department": "data-platform", "accepted_count": 1, "outcome": "delivered"},
        {"department": "ml-engineering", "accepted_count": 1, "outcome": "delivered"},
    ]


def test_zero_routed_departments_calls_notify_human_zero_times(_endpoint):
    ctx = _ctx(state={escalation.POLICY_ROUTING_KEY: {"departments": []}})
    with patch.object(escalation.httpx, "Client") as client:
        (event,) = asyncio.run(_drain(escalation.escalation_agent, ctx))

    client.assert_not_called()
    assert json.loads(event.content.parts[0].text) == {"receipts": []}


def test_a_failure_on_the_second_department_fails_the_whole_run(_endpoint, monkeypatch):
    """No receipt is returned for a partially delivered investigation: the caller must retry."""
    routing = {"departments": [_bucket("data-platform"), _bucket("ml-engineering")]}
    ctx = _ctx(state={escalation.POLICY_ROUTING_KEY: routing})
    calls = []
    real = escalation.notify_human

    def _flaky(*args):
        calls.append(args)
        if len(calls) == 2:
            raise RuntimeError("findings API unavailable")
        return real(*args)

    monkeypatch.setattr(escalation, "notify_human", _flaky)
    with patch.object(escalation.httpx, "Client"), pytest.raises(RuntimeError, match="unavailable"):
        asyncio.run(_drain(escalation.escalation_agent, ctx))
    assert len(calls) == 2


def test_a_missing_investigation_id_is_rejected_before_any_delivery(monkeypatch):
    calls = []
    monkeypatch.setattr(escalation, "record", lambda *a, **k: calls.append(k))
    ctx = _ctx(
        state={escalation.POLICY_ROUTING_KEY: {"departments": [_bucket()]}},
        investigation_id=None,
    )
    with (
        patch.object(escalation.httpx, "Client") as client,
        pytest.raises(escalation.RoutingEnvelopeError, match="missing_investigation_id"),
    ):
        asyncio.run(_drain(escalation.escalation_agent, ctx))
    client.assert_not_called()
    (kwargs,) = calls
    assert kwargs["detail"] == {"reason": "missing_investigation_id"}


def test_the_receipts_event_carries_no_state_delta(_endpoint):
    """P0.3's gate reads receipts from A2A content only; this pins that the worker side of the

    same contract holds too -- nothing here relies on state crossing the hop, the direction of
    ADK issue #6854 this fleet already learned to distrust once (ADR-012).
    """
    ctx = _ctx(state={escalation.POLICY_ROUTING_KEY: {"departments": []}})
    with patch.object(escalation.httpx, "Client"):
        (event,) = asyncio.run(_drain(escalation.escalation_agent, ctx))
    assert not event.actions.state_delta


def test_a_malformed_envelope_is_rejected_before_any_delivery(monkeypatch):
    calls = []
    monkeypatch.setattr(escalation, "record", lambda *a, **k: calls.append(k))
    ctx = _ctx(state={})
    with (
        patch.object(escalation.httpx, "Client") as client,
        pytest.raises(escalation.RoutingEnvelopeError, match="missing_routing_envelope"),
    ):
        asyncio.run(_drain(escalation.escalation_agent, ctx))
    client.assert_not_called()
    (kwargs,) = calls
    assert kwargs["detail"] == {"reason": "missing_routing_envelope"}
