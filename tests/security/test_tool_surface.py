"""The tool-declaration boundary that [ADR-007] defends against tool poisoning.

Model Armor screens prompts; it does not screen tool metadata, and evidence 01 measured it
declining to block a tool-poisoning sample. The control that does hold is here: a fixed tool
set per agent, repository-owned descriptions, and an Escalation Agent that holds no
policy-reading capability at all.

These assertions are deliberately construction-time and offline. They prove what an agent
*can* reach before any model runs, which is the only moment at which a poisoned instruction
has nothing left to talk the agent into.

[ADR-007]: ../../docs/adr/007-tool-poisoning.md
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from agents.access_auditor import agent as auditor
from agents.escalation_agent import agent as escalation
from agents.orchestrator import agent as orchestrator

# The fixed surface, written here rather than derived from the agents, so that widening a tool
# set in the agent module fails this test instead of silently redefining its own expectation.
EXPECTED_TOOLS = {
    "access_auditor": {"audit_iam_policy"},
    "policy_step": {"apply_policy_rules", "route_by_department"},
    "escalation_agent": {"notify_human"},
}

AGENTS = {
    "access_auditor": auditor.access_auditor,
    "policy_step": orchestrator.policy_step,
    "escalation_agent": escalation.escalation_agent,
}

# Any attribute name on an agent module that would mean it can reach the IAM policy directly.
POLICY_CAPABILITY_MARKERS = ("asset_v1", "AssetServiceClient", "iam_policy", "get_iam_policy")

REPO_ROOT = Path(__file__).resolve().parents[2]


def tool_names(agent_name: str) -> set[str]:
    """Return the declared tool names for one agent, as passed at construction."""
    tools = AGENTS[agent_name].tools
    return {getattr(tool, "__name__", getattr(tool, "name", "")) for tool in tools}


@pytest.mark.parametrize("agent_name", sorted(EXPECTED_TOOLS))
def test_each_agent_declares_exactly_its_fixed_tool_set(agent_name):
    """No agent reaches a tool the repository did not declare for it at construction."""
    assert tool_names(agent_name) == EXPECTED_TOOLS[agent_name]


def test_the_escalation_agent_holds_no_policy_reading_tool():
    """The distinct control of ADR-007: absence of a capability, not an instruction to avoid it.

    A compromised prompt cannot call a tool that was never declared, which is why this is
    asserted as set equality rather than as the absence of one known-bad name.
    """
    assert tool_names("escalation_agent") == {"notify_human"}
    assert "audit_iam_policy" not in tool_names("escalation_agent")


def test_the_escalation_module_imports_no_iam_or_asset_client():
    """`agents/escalation_agent/agent.py` claims a security test asserts this absence.

    Differential rather than absolute: the Access Auditor must hold the Asset client for the
    comparison to prove separation instead of merely proving both modules are empty.
    """
    escalation_namespace = vars(escalation)
    for marker in POLICY_CAPABILITY_MARKERS:
        assert marker not in escalation_namespace, f"escalation agent reached {marker}"
    assert "asset_v1" in vars(auditor), "the differential is meaningless if the Auditor lost it"


def test_the_notification_tool_is_never_handed_a_binding():
    """The signature is the control: a tool given only a count cannot forward a principal."""
    parameters = set(inspect.signature(escalation.notify_human).parameters)
    assert parameters == {
        "investigation_id",
        "finding_count",
        "risk_categories",
        "department",
        # Opaque HMAC identifiers, never bindings. They exist so a human can approve a specific
        # finding later; the exception ledger is keyed by finding id and is otherwise unreachable
        # from the surface a reviewer actually reads.
        "finding_ids",
    }


@pytest.mark.parametrize("agent_name", sorted(EXPECTED_TOOLS))
def test_tool_descriptions_are_repository_owned(agent_name):
    """A tool's description comes from its own docstring, never from ingested text.

    Registry records, findings, and model output are all writable by something other than this
    repository. A description assembled from any of them is the poisoned-declaration threat
    arriving through the catalog rather than through the prompt.
    """
    for tool in AGENTS[agent_name].tools:
        # Repository-owned means inside this checkout, not inside `agents/`: the policy step's
        # `route_by_department` lives in `registry/`, which is the catalog supply chain ADR-007
        # names. That is fine while the definition is static source; it would not be if the
        # description were ever read from a Registry record at runtime.
        source = inspect.getsourcefile(tool)
        assert source is not None
        assert Path(source).resolve().is_relative_to(REPO_ROOT)
        # An f-string or concatenation in the docstring would have resolved at import time,
        # so an interpolated description is detectable as a docstring the source does not
        # literally contain.
        docstring = inspect.getdoc(tool)
        assert docstring, f"{tool.__name__} has no repository-owned description"
        assert docstring.splitlines()[0] in inspect.getsource(tool)
