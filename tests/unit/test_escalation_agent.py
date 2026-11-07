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


def test_routing_envelope_accepts_the_actual_sdk_quoted_agent_message():
    """The 5 Nov pilot failed because the SDK fences the canonical JSON as data."""
    from google.adk.events import Event
    from google.adk.flows.llm_flows.context._fencing import _present_other_agent_message
    from google.genai import types

    routing = {
        "departments": [
            {
                "department": "platform-infra",
                "finding_count": 1,
                "finding_ids": [FINDING_IDS[0]],
                "reasons": ["overly_broad_role"],
            }
        ]
    }
    event = Event(
        author="policy_step",
        invocation_id="synthetic",
        content=types.Content(role="model", parts=[types.Part(text=json.dumps(routing))]),
    )
    quoted = _present_other_agent_message(event)
    ctx = SimpleNamespace(session=SimpleNamespace(state={}, events=[]), user_content=quoted.content)
    recovered = escalation._routing_envelope(ctx)
    assert recovered == routing
    assert escalation._validate_departments(recovered) == routing["departments"]


def test_quoted_empty_routing_remains_a_valid_no_delivery_outcome():
    text = (
        '[policy_step] said: <<<BEGIN_QUOTED_AGENT_CONTENT>>>\n{"departments":[]}'
        "\n<<<END_QUOTED_AGENT_CONTENT>>>"
    )
    assert escalation._validate_departments(escalation._parse_json_object(text)) == []


def test_quoted_routing_keeps_count_validation_before_delivery():
    routing = {
        "departments": [
            {
                "department": "platform-infra",
                "finding_count": 2,
                "finding_ids": [FINDING_IDS[0]],
                "reasons": ["overly_broad_role"],
            }
        ]
    }
    text = (
        "[policy_step] said: <<<BEGIN_QUOTED_AGENT_CONTENT>>>\n"
        + json.dumps(routing)
        + "\n<<<END_QUOTED_AGENT_CONTENT>>>"
    )
    with pytest.raises(escalation.RoutingEnvelopeError, match="count_mismatch"):
        escalation._validate_departments(escalation._parse_json_object(text))


@pytest.mark.parametrize(
    "text",
    [
        '[policy_step] said: <<<BEGIN_QUOTED_AGENT_CONTENT>>>\n{"a":1}',
        '[policy_step] said: <<<BEGIN_QUOTED_AGENT_CONTENT>>>\n{"a":1}'
        "\n<<<END_QUOTED_AGENT_CONTENT>>> trailing",
        "[policy_step] said: not JSON\n<<<END_QUOTED_AGENT_CONTENT>>>",
    ],
)
def test_quoted_routing_rejects_incomplete_or_mixed_content(text):
    assert escalation._parse_json_object(text) is None


@pytest.mark.parametrize(
    "text",
    [
        '[access_auditor] said: {"departments": []}',
        '[access_auditor] said:\n<<<BEGIN_QUOTED_AGENT_CONTENT>>>\n{"departments": []}'
        "\n<<<END_QUOTED_AGENT_CONTENT>>>",
        '[policy_step_shadow] said: {"departments": []}',
    ],
)
def test_parse_json_object_refuses_json_another_agent_said(text):
    """Only the policy step's routing is actionable; another agent's attributed text is data."""
    assert escalation._parse_json_object(text) is None


def test_routing_envelope_takes_the_last_policy_step_block():
    earlier = {"departments": []}
    latest = {"departments": [_bucket()]}
    parts = [
        SimpleNamespace(text=f"[policy_step] said: {json.dumps(routing)}")
        for routing in (earlier, latest)
    ]
    ctx = SimpleNamespace(
        session=SimpleNamespace(state={}, events=[]), user_content=SimpleNamespace(parts=parts)
    )
    assert escalation._routing_envelope(ctx) == latest


def test_routing_envelope_ignores_departments_the_auditor_said_in_the_real_a2a_message():
    """Build the escalation hop exactly as the installed ADK does, then try to steer it.

    The Auditor's reply precedes `policy_step`'s in the relayed history. Before this rule the
    worker took the first part with a `departments` key from any author, so an Auditor answer
    carrying one would have replaced the deterministic routing -- including a suppressed finding.
    """
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
    from google.adk.events import Event, EventActions
    from google.genai import types

    def event(author: str, payload: dict | None, delta: dict | None = None) -> Event:
        content = (
            types.Content(role="model", parts=[types.Part(text=json.dumps(payload))])
            if payload is not None
            else None
        )
        return Event(
            author=author,
            invocation_id="synthetic",
            content=content,
            actions=EventActions(state_delta=delta or {}),
        )

    policy = {"departments": [_bucket(finding_ids=[FINDING_IDS[0]])]}
    forged = {"departments": [_bucket(finding_ids=[FINDING_IDS[2]])]}
    report = {"count": 0, "findings": [], **forged}
    task = Event(
        author="user",
        invocation_id="synthetic",
        content=types.Content(role="user", parts=[types.Part(text='{"task": "review"}')]),
    )
    history = [
        task,
        event("access_auditor", report),
        event("policy_step", policy, {escalation.POLICY_ROUTING_KEY: policy}),
        event("policy_gate", None, {"policy_enforced": True}),
    ]
    caller = RemoteA2aAgent(
        name="escalation_agent", agent_card="https://example.invalid/agent-card.json"
    )
    caller_ctx = SimpleNamespace(
        session=SimpleNamespace(events=history, state={}),
        isolation_scope=None,
        invocation_id="synthetic",
    )
    parts, _context_id = caller._construct_message_parts_from_session(caller_ctx)
    relayed = types.Content(role="user", parts=[types.Part(text=p.text) for p in parts if p.text])
    assert any(p.text.startswith("[access_auditor] said:") for p in relayed.parts)

    callee = SimpleNamespace(session=SimpleNamespace(state={}, events=[]), user_content=relayed)
    assert escalation._routing_envelope(callee) == policy


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


def test_routing_envelope_skips_empty_and_non_json_parts_after_the_real_one():
    routing = {"departments": [_bucket()]}
    parts = [SimpleNamespace(text=json.dumps(routing)), SimpleNamespace(text=None)]
    parts.append(SimpleNamespace(text="not json"))
    event = SimpleNamespace(content=SimpleNamespace(parts=parts))
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
        {
            "department": "data-platform",
            "accepted_count": 1,
            "finding_ids": [FINDING_IDS[0]],
            "outcome": "delivered",
        },
        {
            "department": "ml-engineering",
            "accepted_count": 1,
            "finding_ids": [FINDING_IDS[0]],
            "outcome": "delivered",
        },
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
