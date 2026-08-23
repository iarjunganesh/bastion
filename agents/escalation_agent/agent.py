"""Escalation Agent — delivers routed findings to the department that owns them.

Deterministic since P0.2 (ADR-012's 2026-08-23 amendment): this worker parses the
Orchestrator's validated routing envelope and calls `notify_human` for every department it
names, with no model in the path to skip a department, pick another one, or answer without the
required side effect. There is nothing here for a compromised prompt to persuade, because there
is no prompt — and, independent of that change, its service account has **no IAM read
permission at all** (`identity/identity_config.md`), so even a compromised *caller* cannot make
this worker read the policy it escalates. That denial is the artifact the demo captures
([ADR-006](../../docs/adr/006-pillar-coverage.md)).

It posts a **count**, never the bindings behind it. A notification surface is the least
controlled place a principal identifier can end up — searchable, forwardable, and outside the
audited project.

This module imports no IAM or Asset Inventory client, and no model client either. Neither is
tidiness: a client this module does not hold is a capability that neither a tampered routing
envelope nor a compromised peer can reach for, and a security test asserts the absence.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from collections.abc import AsyncGenerator
from hashlib import sha256
from typing import Any

import httpx
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from gateway.cloud_run_auth import CloudRunIdTokenAuth
from model_armor.redaction import (
    notification_summary,
    validate_finding_ids,
    validate_risk_categories,
)
from observability.audit import UNKNOWN, _investigation, _invocation, record
from registry.departments import department_by_id

# A timeout is not optional. Without one a hung notification surface blocks the escalation path
# indefinitely. Separate connect and read budgets: a refused connection should fail fast, while
# a slow-but-alive surface deserves a little patience.
NOTIFY_TIMEOUT_SECONDS = 10.0
NOTIFY_TIMEOUT = httpx.Timeout(NOTIFY_TIMEOUT_SECONDS, connect=3.0)

# Transport-level retries cover connection failures only — httpx will not replay a request that
# was already sent, which is correct for a non-idempotent POST. Retrying a delivered
# notification would page a human twice for one finding.
NOTIFY_RETRIES = 2

# **Not `SLACK_WEBHOOK_URL`, and this was a real disagreement rather than a rename.** The
# variable was Slack-shaped and so was the payload — a single `text` blob — while
# [ADR-003](../../docs/adr/003-pillars-on-geap.md) had already settled the escalation surface as
# the read-only findings API behind the dashboard, and Slack appears nowhere in the twenty
# services. Code contradicting a merged ADR is the one thing CLAUDE.md says may never sit
# silently, so the code moved to the decision rather than the other way round.
#
# The payload is structured rather than a sentence for a second reason: a `text` field invites
# writing identifiers into prose, and a typed body with a `finding_count` gives an injected
# instruction nothing to narrate into.
# Read from the environment rather than Secret Manager, deliberately. The value is the
# findings API's canonical origin, not secret material: the service is IAM-private, so
# knowing the URL grants nothing without an ID token minted for that audience, and this
# agent's service account is the only identity holding `run.invoker` on it. `deploy.sh`
# injects the origin at deploy time from the live service, which also keeps it from being
# copied by hand into a config file and drifting from the service it names.
NOTIFY_ENDPOINT_VAR = "BASTION_FINDINGS_ENDPOINT"


def notify_human(
    investigation_id: str,
    finding_count: int,
    risk_categories: list[str],
    department: str,
    finding_ids: list[str],
) -> dict[str, Any]:
    """Post a count and a summary to one department's notification surface.

    `department` is required rather than defaulted: a finding routed to "everyone" is the
    central-inbox failure this design exists to avoid, and a default would make that the
    quiet outcome of forgetting an argument.

    Takes a **count and opaque ids**, never the findings. The signature is still the control:
    this tool cannot leak bindings because it is never given them, so there is nothing for a
    compromised prompt to talk it into forwarding.

    `finding_ids` carries the Auditor's opaque HMAC identifiers so a human reviewer can approve
    a specific finding later. Without them the review record names no finding, and the exception
    ledger - which is keyed by finding id - is unreachable from the surface a human actually
    reads. They are validated to the exact opaque shape, so a fabricated id is inert: it grants
    nothing and can only key an exception no real finding will ever match.
    """
    if not investigation_id:
        raise ValueError("investigation_id is required")
    if finding_count <= 0:
        # An access review that pages a human on a clean run is one people turn off.
        return {"delivered": False, "department": department, "reason": "nothing to escalate"}

    categories = validate_risk_categories(risk_categories)
    identifiers = validate_finding_ids(finding_ids)
    if len(identifiers) != finding_count:
        # A count that disagrees with the ids it claims to summarise is either a model error or
        # an attempt to inflate urgency; either way the human review record must not carry it.
        raise ValueError("finding_count does not match the number of distinct finding ids")
    endpoint = os.environ.get(NOTIFY_ENDPOINT_VAR)
    if not endpoint:
        raise RuntimeError("BASTION_FINDINGS_ENDPOINT is not configured")

    # A language model may choose which routed department to notify, but it may not select a
    # delivery identity. This stable key lets the receiving system collapse Eventarc retries.
    idempotency_key = sha256(f"{investigation_id}:{department}".encode()).hexdigest()
    transport = httpx.HTTPTransport(retries=NOTIFY_RETRIES)
    with httpx.Client(
        timeout=NOTIFY_TIMEOUT,
        transport=transport,
        auth=CloudRunIdTokenAuth(endpoint),
    ) as client:
        response = client.post(
            endpoint,
            headers={"Idempotency-Key": idempotency_key},
            json={
                "source": "bastion",
                "investigation_id": investigation_id,
                "department": department,
                "finding_count": finding_count,
                "finding_ids": identifiers,
                "risk_categories": categories,
                "summary": notification_summary(categories),
            },
        )
        response.raise_for_status()
    return {"delivered": True, "department": department, "count": finding_count}


# The Orchestrator's `policy_step` writes routing under this key (`agents/orchestrator/agent.py`
# `POLICY_ROUTING_KEY`). Duplicated as a literal rather than imported: the Orchestrator depends
# on its workers, and a worker importing back from it would invert that, plus this module must
# stay independently deployable on its own image directory (`agent_server.stage_a2a_agent`).
POLICY_ROUTING_KEY = "policy_routing"


class RoutingEnvelopeError(RuntimeError):
    """Raised when the routing envelope this worker received cannot be trusted.

    The message is one of a small, bounded set of reason codes -- never a department, a finding
    id, or anything else the envelope carried -- so it is safe to both raise and audit-log.
    """


# ADK flattens a remote agent's multi-hop conversation history into attributed lines when it
# builds the next hop's request -- `[policy_step] said: {...}` -- rather than sending the prior
# turn's content verbatim. Observed in production 2026-08-23: `ctx.user_content` genuinely held
# the routing JSON, but wrapped in this prefix, so a bare `json.loads` on the raw text silently
# failed and was swallowed as "not JSON, skip". Stripped before parsing, not worked around by
# looking somewhere else -- the content channel was always the right one.
_SAID_PREFIX = re.compile(r"\A\[[^\]\n]*\]\s*said:\s*", re.DOTALL)


def _parse_json_object(text: str) -> Any:
    """Parse `text` as JSON, tolerating ADK's `"[agent] said: <json>"` history wrapping."""
    try:
        return json.loads(text)
    except ValueError:
        pass
    stripped = _SAID_PREFIX.sub("", text, count=1)
    if stripped == text:
        return None
    try:
        return json.loads(stripped)
    except ValueError:
        return None


def _content_json(content: Any) -> Any:
    """A JSON object with a `"departments"` key out of one `Content`'s text parts, or `None`."""
    for part in getattr(content, "parts", None) or []:
        text = getattr(part, "text", None)
        if not text:
            continue
        candidate = _parse_json_object(text)
        if isinstance(candidate, dict) and "departments" in candidate:
            return candidate
    return None


def _routing_envelope(ctx: InvocationContext) -> Any:
    """The routing decision: from state in-process, or the inbound A2A message deployed.

    Deployed, this agent is the A2A *callee*, and the routing JSON arrives as the current
    turn's own inbound content -- `InvocationContext.user_content` -- not as an event this
    worker's own session already held before the turn started. Scanning `ctx.session.events`
    instead -- the shape that correctly reads a *reply* on the *caller* side, as
    `agents/orchestrator/agent.py`'s `_audit_report` does for the Auditor's A2A reply -- found
    nothing here: session history and "what the current turn was asked" are not the same thing
    on the callee side of a hop. Observed in production 2026-08-23: every deployed escalation
    call was rejected as `missing_routing_envelope` until this also read `user_content`.
    """
    routing = ctx.session.state.get(POLICY_ROUTING_KEY)
    if isinstance(routing, dict) and "departments" in routing:
        return routing
    if envelope := _content_json(getattr(ctx, "user_content", None)):
        return envelope
    for event in reversed(list(getattr(ctx.session, "events", None) or [])):
        if envelope := _content_json(getattr(event, "content", None)):
            return envelope
    return None


def _validate_departments(routing: Any) -> list[dict[str, Any]]:
    """The envelope's departments, fully validated, or a `RoutingEnvelopeError`.

    Every bucket is checked before this returns, and this returns before `notify_human` is
    called for any of them -- so an envelope that is bad in its second bucket never delivers its
    first. `notify_human` still re-validates each call independently; that is not redundant,
    it is the same invariant enforced at the two different layers that can each be reached on
    their own (this function, and a direct unit-tested call to `notify_human`).
    """
    if not isinstance(routing, dict) or not isinstance(routing.get("departments"), list):
        raise RoutingEnvelopeError("missing_routing_envelope")

    validated: list[dict[str, Any]] = []
    seen: set[Any] = set()
    for entry in routing["departments"]:
        if not isinstance(entry, dict):
            raise RoutingEnvelopeError("malformed_department_bucket")
        department_id = entry.get("department")
        if department_id in seen:
            raise RoutingEnvelopeError("duplicate_department_bucket")
        seen.add(department_id)
        try:
            department_by_id(str(department_id))
        except ValueError as exc:
            raise RoutingEnvelopeError("unknown_department") from exc
        try:
            identifiers = validate_finding_ids(entry.get("finding_ids", []))
        except (ValueError, TypeError) as exc:
            raise RoutingEnvelopeError("invalid_finding_id") from exc
        try:
            categories = validate_risk_categories(entry.get("reasons", []))
        except (ValueError, TypeError) as exc:
            raise RoutingEnvelopeError("invalid_risk_category") from exc
        finding_count = entry.get("finding_count")
        if not finding_count or finding_count != len(identifiers):
            raise RoutingEnvelopeError("count_mismatch")
        validated.append(
            {
                "department": department_id,
                "finding_count": finding_count,
                "finding_ids": identifiers,
                "reasons": categories,
            }
        )
    return validated


class EscalationAgent(BaseAgent):
    """Deliver every routed department's findings, with no model deciding whether or which.

    The `LlmAgent` this replaced could skip a routed department, pick a different one, fabricate
    a schema-valid opaque id, or finish without the notification its instruction described --
    all while the sequence still reported success. This has none of that discretion: it parses
    the routing envelope, validates it completely, and calls `notify_human` exactly once for
    every bucket it names -- zero times when there are none. `notify_human`'s own httpx call is
    synchronous, so each is run off the event loop with `asyncio.to_thread`, the same way ADK
    itself runs a plain tool function.

    A delivery failure -- an unreachable findings API, a rejected payload -- raises out of this
    method uncaught. That fails the remote A2A task the same way `PolicyNotEnforcedError` fails
    the Orchestrator: visibly and retryably, with `notify_human`'s own idempotency key making a
    retry safe rather than a duplicate human-review record.
    """

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        investigation_id = _investigation(ctx)
        try:
            if investigation_id == UNKNOWN:
                raise RoutingEnvelopeError("missing_investigation_id")
            departments = _validate_departments(_routing_envelope(ctx))
        except RoutingEnvelopeError as error:
            record(
                "escalation.envelope",
                outcome="rejected",
                actor=self.name,
                invocation_id=_invocation(ctx),
                investigation_id=investigation_id,
                detail={"reason": str(error)},
            )
            raise

        receipts: list[dict[str, Any]] = []
        for department in departments:
            result = await asyncio.to_thread(
                notify_human,
                investigation_id,
                department["finding_count"],
                department["reasons"],
                department["department"],
                department["finding_ids"],
            )
            receipts.append(
                {
                    "department": department["department"],
                    "accepted_count": department["finding_count"],
                    "outcome": "delivered" if result.get("delivered") else "skipped",
                }
            )

        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            # Content, not state: state is what the in-process topology happens to share, but
            # the only channel that reaches the Orchestrator once this runs behind A2A -- the
            # same lesson `policy_step`'s routing event already had to learn (ADR-012).
            content=types.Content(
                role="model",
                parts=[types.Part(text=json.dumps({"receipts": receipts}, sort_keys=True))],
            ),
        )


escalation_agent = EscalationAgent(
    name="escalation_agent",
    description="Delivers each routed department's findings to its notification surface.",
)

# `adk deploy cloud_run` looks for a module-level `root_agent`. This package deploys on its own
# so it can run under `escalation-agent-sa`, which holds **no IAM read permission of any kind**.
# That denial is the pillar's proof, and it is unobservable while this agent runs in the
# Orchestrator's process under the Orchestrator's identity.
root_agent = escalation_agent
