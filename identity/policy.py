"""Least-privilege identity manifest used by provisioning and deployment."""

from __future__ import annotations

from dataclasses import dataclass

BROAD_ROLES = frozenset({"roles/owner", "roles/editor"})


@dataclass(frozen=True, slots=True)
class WorkloadIdentity:
    name: str
    roles: frozenset[str]

    def email(self, project_id: str) -> str:
        return f"{self.name}@{project_id}.iam.gserviceaccount.com"


IDENTITIES = (
    WorkloadIdentity(
        "orchestrator-sa",
        frozenset(
            {
                "roles/aiplatform.user",
                "roles/datastore.user",
                "roles/modelarmor.user",
                "roles/pubsub.publisher",
            }
        ),
    ),
    WorkloadIdentity(
        "access-auditor-sa",
        frozenset(
            {
                "roles/cloudasset.viewer",
                "roles/iam.securityReviewer",
                "roles/modelarmor.user",
                "roles/recommender.iamViewer",
            }
        ),
    ),
    WorkloadIdentity(
        "escalation-agent-sa",
        frozenset({"roles/secretmanager.secretAccessor", "roles/modelarmor.user"}),
    ),
)


def validate_identities(identities: tuple[WorkloadIdentity, ...] = IDENTITIES) -> None:
    """Reject broad grants and any policy-read capability on the escalation workload."""
    if {identity.name for identity in identities} != {
        "orchestrator-sa",
        "access-auditor-sa",
        "escalation-agent-sa",
    }:
        raise ValueError("exactly the three declared workload identities are required")
    for identity in identities:
        if identity.roles & BROAD_ROLES:
            raise ValueError("broad role is forbidden")
    escalation = next(identity for identity in identities if identity.name == "escalation-agent-sa")
    if any("securityReviewer" in role or "cloudasset" in role for role in escalation.roles):
        raise ValueError("escalation workload may not read IAM")
