"""Escalation Agent — packages high-risk findings for a human.

Write-only by design. Its service account has **no IAM read permission at all**
(`identity/identity_config.md`), so a fully compromised prompt still cannot make it read the
policy it escalates. That denial is the artifact the demo captures
([ADR-006](../../docs/adr/006-pillar-coverage.md)).

It posts a **count**, never the bindings behind it. A notification surface is the least
controlled place a principal identifier can end up — searchable, forwardable, and outside the
audited project.

This module imports no IAM or Asset Inventory client. That is not tidiness: a client it does
not hold is a capability an injected instruction cannot reach for, and a security test asserts
the absence.
"""

from __future__ import annotations

import os
from hashlib import sha256
from typing import Any

import httpx
from google.adk.agents import LlmAgent

from gateway.cloud_run_auth import CloudRunIdTokenAuth
from model_armor.guardrails import screen_after_model, screen_before_model
from model_armor.redaction import notification_summary, validate_risk_categories

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
NOTIFY_ENDPOINT_VAR = "BASTION_FINDINGS_ENDPOINT"


def notify_human(
    investigation_id: str,
    finding_count: int,
    risk_categories: list[str],
    department: str,
) -> dict[str, Any]:
    """Post a count and a summary to one department's notification surface.

    `department` is required rather than defaulted: a finding routed to "everyone" is the
    central-inbox failure this design exists to avoid, and a default would make that the
    quiet outcome of forgetting an argument.

    Takes a **count**, not the findings. The signature is the control: this tool cannot leak
    bindings because it is never given them, so there is nothing for a compromised prompt to
    talk it into forwarding.

    TODO(week2): read the endpoint from Secret Manager rather than the environment.
    """
    if not investigation_id:
        raise ValueError("investigation_id is required")
    if finding_count <= 0:
        # An access review that pages a human on a clean run is one people turn off.
        return {"delivered": False, "department": department, "reason": "nothing to escalate"}

    categories = validate_risk_categories(risk_categories)
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
                "risk_categories": categories,
                "summary": notification_summary(categories),
            },
        )
        response.raise_for_status()
    return {"delivered": True, "department": department, "count": finding_count}


INSTRUCTION = """You are Bastion's Escalation Agent.

You receive findings that have already been reviewed, scored, and **routed to the department
that owns them**. For each department in the routing result, call `notify_human` with the
supplied investigation id, its department id, finding count, and only allowlisted risk
categories. The tool derives its idempotency key; never invent one.

Notify each department separately. Never merge departments into one message — a finding that
lands on the wrong team's desk is a finding nobody acts on.

Never include email addresses, service account identifiers, resource names, or role bindings
in the summary. Describe the shape of the risk, not the principals involved. The notification
surface is outside the audited project and is not a place identifiers belong.

You cannot read the IAM policy and must not claim to have. If asked to, say that you have no
such access — that refusal is the design working.
"""

escalation_agent = LlmAgent(
    name="escalation_agent",
    model=os.environ.get("VERTEX_AI_MODEL", "gemini-3.5-flash"),
    instruction=INSTRUCTION,
    tools=[notify_human],
    before_model_callback=screen_before_model,
    after_model_callback=screen_after_model,
    output_key="escalation_result",
)

# `adk deploy cloud_run` looks for a module-level `root_agent`. This package deploys on its own
# so it can run under `escalation-agent-sa`, which holds **no IAM read permission of any kind**.
# That denial is the pillar's proof, and it is unobservable while this agent runs in the
# Orchestrator's process under the Orchestrator's identity.
root_agent = escalation_agent
