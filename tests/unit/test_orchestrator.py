"""The Orchestrator composes the fleet and applies policy without judgement."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from agents.orchestrator import agent as orchestrator


def _finding(member: str, score: float) -> dict:
    return {
        "finding_id": f"opaque-{member}",
        "department": "security-engineering",
        "reason": "overly_broad_role",
        "risk_score": score,
    }


def _tool_context() -> SimpleNamespace:
    """The slice of ToolContext the policy tool touches: a mutable state mapping."""
    return SimpleNamespace(state={})


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0.9, "escalate"), (0.7, "escalate"), (0.69, "clear"), (0.1, "clear")],
)
def test_the_threshold_is_policy_not_judgement(score: float, expected: str):
    """A model asked to apply a threshold can be argued out of it; a constant cannot."""
    (decision,) = orchestrator.apply_policy_rules(
        [_finding("user:a@x.com", score)], _tool_context()
    )["decisions"]
    assert decision["decision"] == expected


def test_the_threshold_boundary_is_inclusive():
    assert orchestrator.ESCALATION_THRESHOLD == 0.7
    (decision,) = orchestrator.apply_policy_rules(
        [_finding("user:a@x.com", orchestrator.ESCALATION_THRESHOLD)], _tool_context()
    )["decisions"]
    assert decision["decision"] == "escalate"


def test_counts_split_cleanly():
    result = orchestrator.apply_policy_rules(
        [_finding("user:a@x.com", 0.9), _finding("user:b@x.com", 0.2)], _tool_context()
    )
    assert result["escalate_count"] == 1
    assert result["clear_count"] == 1


def test_a_finding_without_a_score_is_rejected_rather_than_cleared():
    """A malformed finding cannot disappear into the clear path by omission."""
    (decision,) = orchestrator.apply_policy_rules([{"member": "user:a@x.com"}], _tool_context())[
        "decisions"
    ]
    assert decision["decision"] == "reject"
    assert decision["rejection_reason"] == "invalid_risk"


def test_an_out_of_range_score_is_rejected_rather_than_coerced():
    (decision,) = orchestrator.apply_policy_rules([_finding("user:a@x.com", 1.1)], _tool_context())[
        "decisions"
    ]
    assert decision["decision"] == "reject"


def test_no_findings_is_not_an_error():
    result = orchestrator.apply_policy_rules([], _tool_context())
    assert result == {
        "decisions": [],
        "escalate_count": 0,
        "clear_count": 0,
        "reject_count": 0,
        "suppress_count": 0,
    }


def test_the_original_finding_survives_the_decision():
    """The decision annotates the finding; it never replaces it."""
    (decision,) = orchestrator.apply_policy_rules([_finding("user:a@x.com", 0.9)], _tool_context())[
        "decisions"
    ]
    assert decision["finding_id"] == "opaque-user:a@x.com"
    assert decision["reason"] == "overly_broad_role"


def test_current_approved_exception_is_suppressed_without_exposing_reviewer():
    class Memory:
        def approved_exception(self, finding_id: str, *, at: str | None = None):
            assert finding_id == "opaque-user:a@x.com"
            assert at is None
            return {
                "approved_until": "2099-01-01T00:00:00+00:00",
                "reviewer": "sensitive-reviewer-reference",
                "policy_version": "iam-policy-v3",
            }

    result = orchestrator.apply_policy_rules_with_memory([_finding("user:a@x.com", 0.9)], Memory())
    (decision,) = result["decisions"]
    assert decision["decision"] == "suppress"
    assert result["suppress_count"] == 1
    assert result["escalate_count"] == 0
    assert "reviewer" not in decision


def test_missing_exception_memory_never_suppresses_a_risky_finding():
    result = orchestrator.apply_policy_rules_with_memory([_finding("user:a@x.com", 0.9)], None)
    assert result["decisions"][0]["decision"] == "escalate"


def test_exception_memory_supports_local_and_firestore_backends(monkeypatch):
    orchestrator.exception_memory.cache_clear()
    monkeypatch.setenv(orchestrator.MEMORY_BACKEND_VAR, "local")
    assert orchestrator.exception_memory() is None

    orchestrator.exception_memory.cache_clear()
    monkeypatch.setenv(orchestrator.MEMORY_BACKEND_VAR, "firestore")
    monkeypatch.setenv("GCP_PROJECT_ID", "bastion-test-project")
    memory = object()
    monkeypatch.setattr(orchestrator, "FirestoreDurableStore", lambda project: memory)
    assert orchestrator.exception_memory() is memory
    orchestrator.exception_memory.cache_clear()


def test_exception_memory_rejects_unknown_or_incomplete_backends(monkeypatch):
    orchestrator.exception_memory.cache_clear()
    monkeypatch.setenv(orchestrator.MEMORY_BACKEND_VAR, "unknown")
    with pytest.raises(RuntimeError, match="unsupported durable store backend"):
        orchestrator.exception_memory()

    orchestrator.exception_memory.cache_clear()
    monkeypatch.setenv(orchestrator.MEMORY_BACKEND_VAR, "firestore")
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    with pytest.raises(RuntimeError, match="GCP_PROJECT_ID is required"):
        orchestrator.exception_memory()
    orchestrator.exception_memory.cache_clear()


def test_the_root_agent_is_a_sequential_adk_agent():
    """Audit must finish before policy can decide, so this is a chain, not a fan-out."""
    assert isinstance(orchestrator.root_agent, SequentialAgent)
    assert orchestrator.root_agent.name == "orchestrator"


def test_the_fleet_is_three_agents_in_order():
    """ADR-002 fixes the count; the order is the investigation.

    `policy_gate` is a deterministic step, not a fourth agent: it has no model, no instruction
    and no tools. It sits between the policy step and escalation because that is the only place
    it can stop an un-scored finding from reaching a human.
    """
    assert [a.name for a in orchestrator.root_agent.sub_agents] == [
        "access_auditor",
        "policy_step",
        "policy_gate",
        "escalation_agent",
    ]
    assert not isinstance(orchestrator.policy_gate, LlmAgent)


def test_the_policy_step_scores_and_routes_without_a_model():
    """Cross-department routing was a tool call a model chose to make; now it always happens."""
    import asyncio

    report = {"count": 1, "findings": [_finding("user:a@x.com", 0.9)]}
    events = asyncio.run(_drain(orchestrator.policy_step, _gate_ctx({"audit_findings": report})))
    delta = events[0].actions.state_delta
    assert delta[orchestrator.POLICY_DECISIONS_KEY]["escalate_count"] == 1
    assert delta[orchestrator.POLICY_ROUTING_KEY]


def test_a_clean_run_scores_zero_findings_rather_than_failing():
    """No anomalies is a real outcome, not a malformed report."""
    import asyncio

    events = asyncio.run(
        _drain(
            orchestrator.policy_step, _gate_ctx({"audit_findings": {"count": 0, "findings": []}})
        )
    )
    assert events[0].actions.state_delta[orchestrator.POLICY_DECISIONS_KEY]["escalate_count"] == 0


@pytest.mark.parametrize(
    "report",
    [None, "The auditor found two overly broad roles.", {"count": 1}, {"findings": "two"}],
    ids=["absent", "prose", "no-findings-key", "not-a-list"],
)
def test_a_missing_or_misshapen_audit_report_fails_closed(report):
    """Scoring nothing and calling it clean is the fail-open shape this whole chain avoids.

    The `prose` case is the one that actually happened: before the Auditor answered in a schema,
    this state key held the model's sentences, and the policy model reconstructed findings from
    them — retyping opaque ids and risk scores on the way.
    """
    import asyncio

    with pytest.raises(orchestrator.PolicyNotEnforcedError):
        asyncio.run(_drain(orchestrator.policy_step, _gate_ctx({"audit_findings": report})))


def test_pydantic_findings_are_accepted_as_well_as_dicts():
    """ADK may hand back the validated model or its dict form; both are the Auditor's answer."""
    import asyncio

    from agents.access_auditor.agent import AuditReport

    report = AuditReport(
        count=1,
        findings=[
            {
                "finding_id": "a" * 24,
                "department": "security-engineering",
                "reason": "overly_broad_role",
                "risk_score": 0.9,
                "rationale": "An overly broad role is held without a condition.",
            }
        ],
    )
    events = asyncio.run(_drain(orchestrator.policy_step, _gate_ctx({"audit_findings": report})))
    assert events[0].actions.state_delta[orchestrator.POLICY_DECISIONS_KEY]["escalate_count"] == 1


def test_every_model_facing_agent_is_screened():
    """No agent reaches Gemini without Model Armor in front of it.

    This checks the *local* composition, where all three run in one process. In the deployed
    topology the peers are `RemoteA2aAgent`s and screen themselves inside their own services,
    which `test_remote_topology_replaces_the_peers` covers instead.
    """
    from model_armor.guardrails import screen_after_model, screen_before_model

    for sub in orchestrator.root_agent.sub_agents:
        if not isinstance(sub, LlmAgent):
            # The policy gate never reaches Gemini, so there is nothing to screen in front of.
            continue
        assert sub.before_model_callback is screen_before_model, sub.name
        assert sub.after_model_callback is screen_after_model, sub.name


def test_the_auditor_instruction_forbids_rescoring():
    """The instruction still matters: the model writes the rationale and copies the rest."""
    from agents.access_auditor.agent import INSTRUCTION

    lowered = " ".join(INSTRUCTION.lower().split())
    assert "never add, drop, or re-score a finding" in lowered
    assert "as the tool returned them" in lowered


# --- The two topologies -------------------------------------------------------------------
#
# Locally the three agents run in one process. Deployed, each is its own Cloud Run service under
# its own service account, and the Orchestrator reaches its peers over A2A. Both are tested
# because the difference is not cosmetic: it is the difference between the least-privilege
# claim being enforced by IAM and merely being described.


def test_card_url_accepts_a_service_origin():
    """Give it an origin and it derives the well-known card path."""
    assert (
        orchestrator.card_url("https://bastion-access-auditor-x.a.run.app", "access_auditor")
        == "https://bastion-access-auditor-x.a.run.app/a2a/access_auditor/.well-known/agent-card.json"
    )
    assert orchestrator.card_url("https://x.a.run.app/", "escalation_agent") == (
        "https://x.a.run.app/a2a/escalation_agent/.well-known/agent-card.json"
    )


def test_card_url_passes_a_full_card_url_through():
    full = "https://x.a.run.app/a2a/auditor/.well-known/agent-card.json"
    assert orchestrator.card_url(full, "access_auditor") == full


def test_local_topology_composes_the_peers_in_process(monkeypatch):
    monkeypatch.delenv(orchestrator.AUDITOR_CARD_VAR, raising=False)
    monkeypatch.delenv(orchestrator.ESCALATION_CARD_VAR, raising=False)

    from agents.access_auditor.agent import access_auditor
    from agents.escalation_agent.agent import escalation_agent

    auditor, policy, gate, escalation = orchestrator.build_sub_agents()

    assert auditor is access_auditor
    assert policy is orchestrator.policy_step
    assert escalation is escalation_agent
    assert gate is orchestrator.policy_gate


def test_remote_topology_replaces_the_peers(monkeypatch):
    monkeypatch.setenv(orchestrator.AUDITOR_CARD_VAR, "https://auditor.a.run.app")
    monkeypatch.setenv(orchestrator.ESCALATION_CARD_VAR, "https://escalation.a.run.app")

    auditor, policy, gate, escalation = orchestrator.build_sub_agents()

    assert isinstance(auditor, RemoteA2aAgent)
    assert isinstance(escalation, RemoteA2aAgent)
    # The policy step is never remote: it is the Orchestrator's own decision, and ADR-002
    # deliberately kept it out of a fourth agent.
    assert policy is orchestrator.policy_step
    # Names are preserved across the transport change, so a trace reads the same either way.
    assert [auditor.name, escalation.name] == ["access_auditor", "escalation_agent"]
    # The gate is local in both topologies: a guard that travels over A2A is one the
    # caller must trust the callee to run.
    assert gate is orchestrator.policy_gate


@pytest.mark.parametrize(
    "present,missing",
    [
        ("BASTION_AUDITOR_CARD_URL", "BASTION_ESCALATION_CARD_URL"),
        ("BASTION_ESCALATION_CARD_URL", "BASTION_AUDITOR_CARD_URL"),
    ],
)
def test_half_configured_topology_raises_rather_than_falling_back(monkeypatch, present, missing):
    """A missing variable must not quietly relax an IAM boundary.

    Falling back to the in-process peers on a half-configured deploy would run the Access
    Auditor under the Orchestrator's service account while every document still described it as
    separately scoped. Failing closed is the same rule Model Armor and deploy.sh follow.
    """
    monkeypatch.setenv(present, "https://x.a.run.app")
    monkeypatch.delenv(missing, raising=False)

    with pytest.raises(RuntimeError, match=missing):
        orchestrator.build_sub_agents()


# --- The policy gate ----------------------------------------------------------------------
#
# Observed in production on 2026-08-21: Model Armor refused `policy_step`, so its tools never
# ran, and the investigation escalated anyway and reported `completed`. These pin the fix.


def _gate_ctx(state: dict[str, object]) -> SimpleNamespace:
    return SimpleNamespace(session=SimpleNamespace(state=state), invocation_id="inv-gate")


async def _drain(agent, ctx) -> list[object]:
    return [event async for event in agent._run_async_impl(ctx)]


def test_the_policy_tool_records_its_own_result_in_state():
    """The gate's evidence must come from the deterministic path, not from model output."""
    context = _tool_context()
    orchestrator.apply_policy_rules([_finding("user:a@x.com", 0.9)], context)
    recorded = context.state[orchestrator.POLICY_ENFORCEMENT_KEY]
    assert recorded["escalate_count"] == 1


def test_the_gate_refuses_to_escalate_when_the_policy_step_never_ran():
    """A screening refusal skips the tools; escalating anyway pages humans about un-scored
    findings, which is precisely what happened in production before this existed."""
    import asyncio

    with pytest.raises(orchestrator.PolicyNotEnforcedError):
        asyncio.run(_drain(orchestrator.policy_gate, _gate_ctx({})))


def test_the_gate_refuses_model_prose_in_place_of_a_decision():
    """When the callback refuses, ADK still stores the refusal text under the step's
    `output_key`. A gate that accepted any non-empty state would wave that through."""
    import asyncio

    state = {orchestrator.POLICY_ENFORCEMENT_KEY: "This input was blocked by Model Armor."}
    with pytest.raises(orchestrator.PolicyNotEnforcedError):
        asyncio.run(_drain(orchestrator.policy_gate, _gate_ctx(state)))


def test_the_gate_rejects_a_decision_shaped_object_without_decisions():
    import asyncio

    state = {orchestrator.POLICY_ENFORCEMENT_KEY: {"escalate_count": 1}}
    with pytest.raises(orchestrator.PolicyNotEnforcedError):
        asyncio.run(_drain(orchestrator.policy_gate, _gate_ctx(state)))


def test_the_gate_passes_once_the_rules_have_actually_run():
    import asyncio

    context = _tool_context()
    orchestrator.apply_policy_rules([_finding("user:a@x.com", 0.9)], context)
    events = asyncio.run(_drain(orchestrator.policy_gate, _gate_ctx(dict(context.state))))
    assert events and events[0].actions.state_delta == {"policy_enforced": True}
