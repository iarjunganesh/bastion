"""Identity manifest cannot silently widen agent authority."""

from __future__ import annotations

import pytest

from identity.policy import IDENTITIES, WorkloadIdentity, validate_identities


def test_manifest_has_one_identity_per_agent_and_no_broad_roles():
    validate_identities()
    assert (
        IDENTITIES[1].email("example-project")
        == "access-auditor-sa@example-project.iam.gserviceaccount.com"
    )


def test_broad_role_is_rejected():
    changed = (WorkloadIdentity("orchestrator-sa", frozenset({"roles/owner"})), *IDENTITIES[1:])
    with pytest.raises(ValueError, match="broad"):
        validate_identities(changed)


def test_escalation_cannot_gain_policy_read():
    changed = (
        *IDENTITIES[:2],
        WorkloadIdentity("escalation-agent-sa", frozenset({"roles/cloudasset.viewer"})),
        *IDENTITIES[3:],
    )
    with pytest.raises(ValueError, match="may not read IAM"):
        validate_identities(changed)


def test_missing_or_extra_identity_is_rejected():
    with pytest.raises(ValueError, match="exactly"):
        validate_identities(IDENTITIES[:2])
