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


def test_approver_cannot_gain_a_standing_project_role():
    """The approver is a break-glass credential a human borrows, not a workload.

    Its only capability is run.invoker on the findings API, granted per-service at deploy time.
    Any project role would make the identity itself powerful, and the human who may impersonate
    it would inherit that power for every purpose rather than for approving one exception.
    """
    changed = tuple(
        WorkloadIdentity("approver-sa", frozenset({"roles/datastore.user"}))
        if identity.name == "approver-sa"
        else identity
        for identity in IDENTITIES
    )
    with pytest.raises(ValueError, match="no project role"):
        validate_identities(changed)


def test_every_agent_identity_can_reach_model_armor():
    """A screening callback that cannot call Model Armor refuses rather than skips.

    This is the failure the Orchestrator actually had: the role was missing, every screen
    raised, fail-closed turned that into a refusal, and the policy step produced no output on
    any investigation while the documentation still claimed screening worked.
    """
    from identity.policy import SCREENING_IDENTITIES

    for name in SCREENING_IDENTITIES:
        identity = next(item for item in IDENTITIES if item.name == name)
        assert "roles/modelarmor.user" in identity.roles, name

    stripped = tuple(
        WorkloadIdentity(item.name, item.roles - {"roles/modelarmor.user"})
        if item.name == "orchestrator-sa"
        else item
        for item in IDENTITIES
    )
    with pytest.raises(ValueError, match="modelarmor.user"):
        validate_identities(stripped)
