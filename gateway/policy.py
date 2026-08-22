"""Fail-closed Registry-backed admission for inter-agent calls.

The cloud Agent Gateway enforces this policy at runtime. This local evaluator is deliberately
the same contract exercised in tests and used by deployment smoke checks.

**That mirroring is why there is no rate limit here, and the omission is a decision.** Four
refusals are evaluated below — uncatalogued target, unauthorized caller, undeclared skill,
impermissible data classification — and every one of them is also enforced by the deployed
Gateway. A per-caller rate limit would be the only rule in this file that the managed control
does not apply, so the suite would assert a refusal production does not make. This repository has
now shipped three defects of exactly that shape (the policy step, the Auditor hand-off, the
escalation hand-off), each one true of the code and false of the deployed system, and each found
only by watching the fleet rather than by running the tests.

Measured 2026-08-22 against the live `bastion-egress` gateway: its configuration surface is
`agentGatewayCard`, `googleManaged.governedAccessPath`, `labels`, `protocols` and `registries`.
There is no rate or quota field, and `gcloud network-services agent-gateways update` exposes no
such flag. So the managed product does not offer this control, and
[ADR-003](../docs/adr/003-pillars-on-geap.md) says not to hand-roll a substitute for a managed
product and then describe it as the pillar.

The deployed system does bound throughput, by a different mechanism that is described as what it
is rather than as rate limiting: `BASTION_MAX_INSTANCES` caps Cloud Run concurrency, and Eventarc
delivery is bounded to five attempts before a message reaches the dead-letter subscription.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentCard:
    agent_id: str
    owner_department: str
    skills: frozenset[str]
    allowed_callers: frozenset[str]
    data_classification: str = "internal"


class GatewayDenied(PermissionError):
    """A policy refusal safe to record in the audit trail."""


CATALOG: dict[str, AgentCard] = {
    "access_auditor": AgentCard(
        "access_auditor",
        "security-engineering",
        frozenset({"audit_iam"}),
        frozenset({"orchestrator"}),
    ),
    "escalation_agent": AgentCard(
        "escalation_agent",
        "security-engineering",
        frozenset({"notify_department"}),
        frozenset({"orchestrator"}),
    ),
}


def admit(
    *,
    caller: str,
    target: str,
    skill: str,
    classification: str,
    catalog: dict[str, AgentCard] = CATALOG,
) -> AgentCard:
    """Return the target card only when caller, skill, and data class are declared."""
    card = catalog.get(target)
    if card is None:
        raise GatewayDenied("target is not cataloged")
    if caller not in card.allowed_callers:
        raise GatewayDenied("caller is not authorized")
    if skill not in card.skills:
        raise GatewayDenied("skill is not declared")
    if classification != card.data_classification:
        raise GatewayDenied("data classification is not permitted")
    return card
