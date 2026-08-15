"""Fail-closed Registry-backed admission for inter-agent calls.

The cloud Agent Gateway enforces this policy at runtime. This local evaluator is deliberately
the same contract exercised in tests and used by deployment smoke checks.
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
