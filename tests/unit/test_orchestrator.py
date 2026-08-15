"""The Orchestrator composes the fleet and applies policy without judgement."""

from __future__ import annotations

import pytest
from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from agents.orchestrator import agent as orchestrator


def _finding(member: str, score: float) -> dict:
    return {
        "member": member,
        "role": "roles/editor",
        "reason": "overly_broad_role",
        "risk_score": score,
    }


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0.9, "escalate"), (0.7, "escalate"), (0.69, "clear"), (0.1, "clear")],
)
def test_the_threshold_is_policy_not_judgement(score: float, expected: str):
    """A model asked to apply a threshold can be argued out of it; a constant cannot."""
    (decision,) = orchestrator.apply_policy_rules([_finding("user:a@x.com", score)])["decisions"]
    assert decision["decision"] == expected


def test_the_threshold_boundary_is_inclusive():
    assert orchestrator.ESCALATION_THRESHOLD == 0.7
    (decision,) = orchestrator.apply_policy_rules(
        [_finding("user:a@x.com", orchestrator.ESCALATION_THRESHOLD)]
    )["decisions"]
    assert decision["decision"] == "escalate"


def test_counts_split_cleanly():
    result = orchestrator.apply_policy_rules(
        [_finding("user:a@x.com", 0.9), _finding("user:b@x.com", 0.2)]
    )
    assert result["escalate_count"] == 1
    assert result["clear_count"] == 1


def test_a_finding_without_a_score_is_rejected_rather_than_cleared():
    """A malformed finding cannot disappear into the clear path by omission."""
    (decision,) = orchestrator.apply_policy_rules([{"member": "user:a@x.com"}])["decisions"]
    assert decision["decision"] == "reject"
    assert decision["rejection_reason"] == "invalid_risk"


def test_an_out_of_range_score_is_rejected_rather_than_coerced():
    (decision,) = orchestrator.apply_policy_rules([_finding("user:a@x.com", 1.1)])["decisions"]
    assert decision["decision"] == "reject"


def test_no_findings_is_not_an_error():
    result = orchestrator.apply_policy_rules([])
    assert result == {"decisions": [], "escalate_count": 0, "clear_count": 0, "reject_count": 0}


def test_the_original_finding_survives_the_decision():
    """The decision annotates the finding; it never replaces it."""
    (decision,) = orchestrator.apply_policy_rules([_finding("user:a@x.com", 0.9)])["decisions"]
    assert decision["member"] == "user:a@x.com"
    assert decision["reason"] == "overly_broad_role"


def test_the_root_agent_is_a_sequential_adk_agent():
    """Audit must finish before policy can decide, so this is a chain, not a fan-out."""
    assert isinstance(orchestrator.root_agent, SequentialAgent)
    assert orchestrator.root_agent.name == "orchestrator"


def test_the_fleet_is_three_agents_in_order():
    """ADR-002 fixes the count; the order is the investigation."""
    assert [a.name for a in orchestrator.root_agent.sub_agents] == [
        "access_auditor",
        "policy_step",
        "escalation_agent",
    ]


def test_the_policy_step_routes_as_well_as_decides():
    """Cross-department routing is a tool call, not a model guess."""
    names = [getattr(t, "__name__", getattr(t, "name", "")) for t in orchestrator.policy_step.tools]
    assert "apply_policy_rules" in names
    assert "route_by_department" in names


def test_every_model_facing_agent_is_screened():
    """No agent reaches Gemini without Model Armor in front of it.

    This checks the *local* composition, where all three run in one process. In the deployed
    topology the peers are `RemoteA2aAgent`s and screen themselves inside their own services,
    which `test_remote_topology_replaces_the_peers` covers instead.
    """
    from model_armor.guardrails import screen_after_model, screen_before_model

    for sub in orchestrator.root_agent.sub_agents:
        assert sub.before_model_callback is screen_before_model, sub.name
        assert sub.after_model_callback is screen_after_model, sub.name


def test_the_policy_instruction_forbids_rescoring():
    assert "never" in orchestrator.POLICY_INSTRUCTION.lower()
    assert "do not guess" in orchestrator.POLICY_INSTRUCTION.lower()


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

    auditor, policy, escalation = orchestrator.build_sub_agents()

    assert auditor is access_auditor
    assert policy is orchestrator.policy_step
    assert escalation is escalation_agent


def test_remote_topology_replaces_the_peers(monkeypatch):
    monkeypatch.setenv(orchestrator.AUDITOR_CARD_VAR, "https://auditor.a.run.app")
    monkeypatch.setenv(orchestrator.ESCALATION_CARD_VAR, "https://escalation.a.run.app")

    auditor, policy, escalation = orchestrator.build_sub_agents()

    assert isinstance(auditor, RemoteA2aAgent)
    assert isinstance(escalation, RemoteA2aAgent)
    # The policy step is never remote: it is the Orchestrator's own decision, and ADR-002
    # deliberately kept it out of a fourth agent.
    assert policy is orchestrator.policy_step
    # Names are preserved across the transport change, so a trace reads the same either way.
    assert [auditor.name, escalation.name] == ["access_auditor", "escalation_agent"]


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
