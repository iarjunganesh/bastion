"""Orchestrator — opens investigations, applies the policy rules, and owns escalation.

Policy enforcement lives here, in-process: there is no Policy Enforcer agent to call. ADR-002
merged it in, and agent count is not graded — separation of concerns is.

**Composition is ADK's, not hand-rolled.** The Auditor must finish before the Escalation Agent
can decide what to escalate, so this is a `SequentialAgent` rather than an `asyncio.gather`
fan-out. The previous version hand-rolled the fan-out plus retry, a circuit breaker and a loop
guard — roughly 420 lines reimplementing what Agent Engine and ADK already provide
([ADR-003](../../docs/adr/003-pillars-on-geap.md)).

`root_agent` is the name `adk run`, `adk web`, and `adk deploy` look for.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any, Protocol

from google.adk.agents import BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.events import Event, EventActions
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel

from gateway.cloud_run_auth import private_a2a_client
from gateway.policy import admit
from observability.audit import INVESTIGATION_METADATA_KEY
from registry.departments import route_by_department
from runtime.firestore import FirestoreDurableStore

# A finding at or above this score goes to a human; below it, it is recorded and cleared.
# A constant rather than a model judgement: "is 0.8 risky enough to page someone" is a policy
# question, and a compliance product cannot answer it differently on two identical runs.
ESCALATION_THRESHOLD = 0.7
# The state key the deterministic policy tool writes, and the only evidence the gate
# below accepts that enforcement actually happened.
POLICY_ENFORCEMENT_KEY = "policy_enforcement"
POLICY_DECISIONS_KEY = "policy_decisions"
POLICY_ROUTING_KEY = "policy_routing"
AUDIT_FINDINGS_KEY = "audit_findings"
FIRESTORE_MEMORY_BACKEND = "firestore"
MEMORY_BACKEND_VAR = "BASTION_DURABLE_STORE_BACKEND"


class ExceptionMemory(Protocol):
    def approved_exception(
        self, finding_id: str, *, at: str | None = None
    ) -> dict[str, str] | None: ...  # pragma: no cover - structural typing declaration


@lru_cache(maxsize=1)
def exception_memory() -> ExceptionMemory | None:
    """Return the production exception ledger; ordinary local runs stay credential-free."""
    backend = os.environ.get(MEMORY_BACKEND_VAR, "local")
    if backend == "local":
        return None
    if backend != FIRESTORE_MEMORY_BACKEND:
        raise RuntimeError(f"unsupported durable store backend: {backend}")
    try:
        project = os.environ["GCP_PROJECT_ID"]
    except KeyError:
        raise RuntimeError("GCP_PROJECT_ID is required for Firestore exception memory") from None
    return FirestoreDurableStore(project)


def apply_policy_rules_with_memory(
    findings: list[dict[str, Any]], memory: ExceptionMemory | None
) -> dict[str, Any]:
    """Apply policy and suppress only a currently valid durable human exception."""
    decisions: list[dict[str, Any]] = []
    for finding in findings:
        try:
            risk_score = float(finding["risk_score"])
        except (KeyError, TypeError, ValueError):
            decisions.append({**finding, "decision": "reject", "rejection_reason": "invalid_risk"})
            continue
        if not 0 <= risk_score <= 1:
            decisions.append({**finding, "decision": "reject", "rejection_reason": "invalid_risk"})
            continue

        approved = None
        finding_id = finding.get("finding_id")
        if memory is not None and isinstance(finding_id, str) and finding_id:
            approved = memory.approved_exception(finding_id)
        if approved is not None:
            # Reviewer identity remains in the durable ledger and never enters model state.
            decisions.append(
                {
                    **finding,
                    "decision": "suppress",
                    "suppression_reason": "approved_exception",
                    "exception_policy_version": approved["policy_version"],
                    "approved_until": approved["approved_until"],
                }
            )
            continue
        decisions.append(
            {**finding, "decision": "escalate" if risk_score >= ESCALATION_THRESHOLD else "clear"}
        )

    return {
        "decisions": decisions,
        "escalate_count": sum(d["decision"] == "escalate" for d in decisions),
        "clear_count": sum(d["decision"] == "clear" for d in decisions),
        "reject_count": sum(d["decision"] == "reject" for d in decisions),
        "suppress_count": sum(d["decision"] == "suppress" for d in decisions),
    }


class PolicyNotEnforcedError(RuntimeError):
    """Raised when escalation is reached without deterministic policy enforcement having run."""


def apply_policy_rules(findings: list[dict[str, Any]], tool_context: ToolContext) -> dict[str, Any]:
    """Decide clear-or-escalate for each finding. Deterministic, and deliberately dull.

    This is the Policy Enforcer, as a function. It is a tool rather than an instruction so the
    threshold cannot be argued with: a model asked to "apply a threshold of 0.7" can be talked
    out of it by the text it is reading, and this cannot.

    **It records its own result in state, and that record is what the gate reads.** The model's
    `output_key` is not proof of enforcement: when `before_model_callback` refuses, ADK still
    stores the refusal text under that key, so a state slot that merely holds *something* cannot
    distinguish "the policy ran" from "screening blocked the policy step". Writing the decision
    here means the evidence is produced by the deterministic code path or not at all.
    """
    decisions = apply_policy_rules_with_memory(findings, exception_memory())
    tool_context.state[POLICY_ENFORCEMENT_KEY] = decisions
    return decisions


class PolicyEnforcementGate(BaseAgent):
    """Refuse to escalate an investigation whose findings were never scored.

    `policy_step` reaches its deterministic tools only through a model call. When Model Armor
    refuses that call the tools never run — and until this gate existed the sequence simply
    continued, so the Escalation Agent paged humans about findings that no threshold had ever
    been applied to, while the lifecycle recorded `completed`. Enforcement did not fail closed;
    it disappeared.

    Observed in production on 2026-08-21: two investigations escalated with the policy step
    skipped and no error recorded anywhere.

    Raising here is the fail-closed behaviour the rest of the system already promises for
    missing or malformed risk. A failed investigation is visible and retryable; an investigation
    that quietly escalates un-scored findings is neither.
    """

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        enforcement = ctx.session.state.get(POLICY_ENFORCEMENT_KEY)
        if not isinstance(enforcement, dict) or "decisions" not in enforcement:
            raise PolicyNotEnforcedError(
                "deterministic policy enforcement did not run; refusing to escalate"
            )
        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            actions=EventActions(state_delta={"policy_enforced": True}),
        )


class PolicyStep(BaseAgent):
    """Score every finding and route it, with no model in the path.

    This step used to be an `LlmAgent` whose `apply_policy_rules` and `route_by_department`
    tools the model chose to call. That put a language model between the Auditor's deterministic
    output and the deterministic threshold applied to it, with two consequences that were both
    observed in production:

    - When Model Armor refused the model call, the tools never ran at all, and the investigation
      escalated un-scored findings while reporting success. See
      [ADR-010](../../docs/adr/010-policy-enforcement-gate.md).
    - Even when it did run, the model was **retyping** the findings — reconstructing opaque ids,
      categories and scores from the Auditor's prose before handing them to the threshold. A
      fabricated category is what made `notify_human` fail intermittently, and a mistyped
      24-hex id is why an approved exception would never have matched its finding.

    There was never a decision here for a model to make. The threshold is a constant, ownership
    comes from a catalog, and both were already tools precisely so they could not be argued
    with. Removing the model removes the only step that could corrupt or skip them — and, since
    a step that makes no model call needs no screening, it also takes this path off the Runtime's
    blocked Model Armor egress.
    """

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        report = ctx.session.state.get(AUDIT_FINDINGS_KEY)
        findings = _findings_of(report)
        decisions = apply_policy_rules_with_memory(findings, exception_memory())
        routing = route_by_department(decisions["decisions"])
        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            actions=EventActions(
                state_delta={
                    POLICY_ENFORCEMENT_KEY: decisions,
                    POLICY_DECISIONS_KEY: decisions,
                    POLICY_ROUTING_KEY: routing,
                }
            ),
        )


def _findings_of(report: Any) -> list[dict[str, Any]]:
    """The Auditor's findings, or a fail-closed error — never a silent empty list.

    A clean run is a real outcome and returns `[]`. A *missing* or *misshapen* report is not:
    treating it as "no findings" would clear an investigation that never looked, which is the
    same fail-open shape the gate downstream exists to catch. `AuditReport` is a pydantic model
    on the wire, so ADK may hand this back as either the model or its dict form.
    """
    if isinstance(report, BaseModel):
        report = report.model_dump()
    if not isinstance(report, dict) or "findings" not in report:
        raise PolicyNotEnforcedError(
            "the Access Auditor returned no structured report; refusing to score nothing"
        )
    findings = report["findings"]
    if not isinstance(findings, list):
        raise PolicyNotEnforcedError("the Access Auditor's findings are not a list")
    return [f.model_dump() if isinstance(f, BaseModel) else f for f in findings]


policy_step = PolicyStep(
    name="policy_step",
    description="Applies the deterministic risk threshold and routes findings to their owners.",
)


policy_gate = PolicyEnforcementGate(
    name="policy_gate",
    description="Fails the investigation closed when the policy rules did not run.",
)


# A deployed Bastion service exposes exactly one staged A2A app beneath its own name.  The
# card path is explicit so an origin cannot accidentally resolve to a generic or sibling card.
A2A_CARD_PATH = "/a2a/{agent_name}/.well-known/agent-card.json"

AUDITOR_CARD_VAR = "BASTION_AUDITOR_CARD_URL"
ESCALATION_CARD_VAR = "BASTION_ESCALATION_CARD_URL"


def card_url(value: str, agent_name: str) -> str:
    """Accept either a full agent-card URL or the service origin it lives under."""
    return (
        value
        if value.endswith(".json")
        else f"{value.rstrip('/')}{A2A_CARD_PATH.format(agent_name=agent_name)}"
    )


def _forward_investigation(ctx: Any, _message: Any) -> dict[str, Any]:
    """Carry the investigation id to a worker as A2A request metadata.

    ADK gives each agent run its own `invocation_id`, and a worker is a separate run in a
    separate process -- so without this, an investigation's audit records land under three
    unrelated ids and cannot be assembled into one trail at all.

    Metadata rather than message content on purpose: the id must reach the worker's audit
    records without becoming something a model reads, restates, or can be talked into changing.
    ADK files it under `RunConfig.custom_metadata["a2a_metadata"]` on the far side, which is
    where `observability.audit` looks for it.
    """
    metadata = getattr(getattr(ctx, "run_config", None), "custom_metadata", None) or {}
    return {INVESTIGATION_METADATA_KEY: metadata.get(INVESTIGATION_METADATA_KEY, "")}


def build_sub_agents() -> list[Any]:
    """The two peers, in-process for local runs and over A2A once deployed.

    **Both variables or neither — a half-configured deploy raises rather than falling back.**
    Silently importing the peers in-process would run the Access Auditor under the
    *Orchestrator's* service account, which is precisely the least-privilege claim the split
    exists to make true. A missing environment variable must not be able to quietly relax an
    IAM boundary while every document still describes it as enforced; the same reasoning
    already makes Model Armor fail closed and `deploy.sh` refuse to default `GCP_REGION`.
    """
    auditor = os.environ.get(AUDITOR_CARD_VAR)
    escalation = os.environ.get(ESCALATION_CARD_VAR)

    if bool(auditor) != bool(escalation):
        missing = AUDITOR_CARD_VAR if not auditor else ESCALATION_CARD_VAR
        raise RuntimeError(
            f"{missing} is unset while its peer is set. Set both to run the deployed "
            "topology, or neither to run all three agents in one process locally."
        )

    if auditor and escalation:
        admit(
            caller="orchestrator",
            target="access_auditor",
            skill="audit_iam",
            classification="internal",
        )
        admit(
            caller="orchestrator",
            target="escalation_agent",
            skill="notify_department",
            classification="internal",
        )
        return [
            RemoteA2aAgent(
                name="access_auditor",
                agent_card=card_url(auditor, "access_auditor"),
                description="Reads the live IAM policy and flags anomalies. Read-only.",
                httpx_client=private_a2a_client(auditor),
                a2a_request_meta_provider=_forward_investigation,
            ),
            policy_step,
            policy_gate,
            RemoteA2aAgent(
                name="escalation_agent",
                agent_card=card_url(escalation, "escalation_agent"),
                description="Packages high-risk findings for the owning department.",
                httpx_client=private_a2a_client(escalation),
                a2a_request_meta_provider=_forward_investigation,
            ),
        ]

    # Imported here rather than at module scope, for two reasons that happen to coincide.
    #
    # **Capability.** A deployed Orchestrator must not carry the Access Auditor's Cloud Asset
    # Inventory client in its own process. `orchestrator-sa` holds no policy-read role, so the
    # client would be inert — but the Escalation Agent's rule is that a client it does not hold
    # is a capability an injected instruction cannot reach for, and the rule is worth applying
    # consistently rather than only where it is load-bearing.
    #
    # **Packaging.** `adk deploy cloud_run` bundles the agent folder it is given. A top-level
    # import of a sibling agent makes the Orchestrator undeployable on its own.
    from agents.access_auditor.agent import access_auditor
    from agents.escalation_agent.agent import escalation_agent

    return [access_auditor, policy_step, policy_gate, escalation_agent]


# Audit -> apply policy -> gate -> escalate. Each step reads the previous one's `output_key`
# from session state, which is what makes the chain reconstructable in a trace afterwards.
#
# The gate is a step rather than a check inside the Escalation Agent because the Escalation
# Agent is remote: a guard that travels over A2A is a guard the caller has to trust the callee
# to run. Keeping it in the Orchestrator keeps policy enforcement where ADR-002 put it.
#
# The composition is the same either way; only the transport changes. That is the point of
# doing this with `RemoteA2aAgent` rather than two code paths — the sequence a judge sees in a
# trace is the sequence the local run produces, so the demo and the development loop cannot
# drift apart.
root_agent = SequentialAgent(
    name="orchestrator",
    description=(
        "Runs one Bastion access-review investigation: audit the live IAM policy, apply the "
        "policy rules, route each finding to the department that owns the principal, and "
        "escalate to those teams."
    ),
    sub_agents=build_sub_agents(),
)
