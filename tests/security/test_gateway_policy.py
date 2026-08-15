"""Gateway policy refuses every undeclared remote call."""

from __future__ import annotations

import pytest

from gateway.policy import CATALOG, GatewayDenied, admit


def test_catalog_exposes_cross_department_agent_metadata():
    assert CATALOG["access_auditor"].owner_department == "security-engineering"
    assert "audit_iam" in CATALOG["access_auditor"].skills


def test_declared_call_is_admitted():
    assert (
        admit(
            caller="orchestrator",
            target="access_auditor",
            skill="audit_iam",
            classification="internal",
        ).agent_id
        == "access_auditor"
    )


@pytest.mark.parametrize(
    ("caller", "target", "skill", "classification"),
    [
        ("unknown", "access_auditor", "audit_iam", "internal"),
        ("orchestrator", "access_auditor", "notify_department", "internal"),
        ("orchestrator", "missing", "audit_iam", "internal"),
        ("orchestrator", "access_auditor", "audit_iam", "restricted"),
    ],
)
def test_undeclared_call_is_denied(caller, target, skill, classification):
    with pytest.raises(GatewayDenied):
        admit(caller=caller, target=target, skill=skill, classification=classification)
