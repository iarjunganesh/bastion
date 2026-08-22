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
                "roles/cloudtrace.agent",
                "roles/logging.logWriter",
                "roles/monitoring.metricWriter",
            }
        ),
    ),
    WorkloadIdentity(
        "access-auditor-sa",
        frozenset(
            {
                "roles/cloudasset.viewer",
                "roles/aiplatform.user",
                "roles/cloudtrace.agent",
                "roles/iam.securityReviewer",
                "roles/logging.logWriter",
                "roles/modelarmor.user",
                "roles/monitoring.metricWriter",
                "roles/recommender.iamViewer",
                "roles/secretmanager.secretAccessor",
            }
        ),
    ),
    WorkloadIdentity(
        "escalation-agent-sa",
        frozenset(
            {
                "roles/aiplatform.user",
                "roles/cloudtrace.agent",
                "roles/logging.logWriter",
                "roles/modelarmor.user",
                "roles/monitoring.metricWriter",
            }
        ),
    ),
    WorkloadIdentity("findings-api-sa", frozenset({"roles/datastore.user"})),
    # The break-glass identity a human approves through. Cloud Run only accepts an ID token
    # whose audience is the service, and no user credential can mint one, so a human reaches
    # the approval endpoint by impersonating this identity. It holds no project role at all:
    # its sole capability is run.invoker on the findings API, granted per-service in deploy.sh,
    # and only the configured approver may impersonate it. Impersonation is itself an
    # authenticated act, so the human stays named in the IAM audit log.
    WorkloadIdentity("approver-sa", frozenset()),
    # Eventarc's delivery identity is not an agent and never receives production-data access.
    # It can receive the Pub/Sub event; its only Cloud Run permission is granted per-service in
    # deploy.sh, so it cannot invoke a peer or the findings inbox.
    WorkloadIdentity("eventarc-invoker-sa", frozenset({"roles/eventarc.eventReceiver"})),
)


def validate_identities(identities: tuple[WorkloadIdentity, ...] = IDENTITIES) -> None:
    """Reject broad grants and any policy-read capability on the escalation workload."""
    if {identity.name for identity in identities} != {
        "orchestrator-sa",
        "access-auditor-sa",
        "escalation-agent-sa",
        "findings-api-sa",
        "eventarc-invoker-sa",
        "approver-sa",
    }:
        raise ValueError("exactly the declared Bastion identities are required")
    for identity in identities:
        if identity.roles & BROAD_ROLES:
            raise ValueError("broad role is forbidden")
    escalation = next(identity for identity in identities if identity.name == "escalation-agent-sa")
    if any("securityReviewer" in role or "cloudasset" in role for role in escalation.roles):
        raise ValueError("escalation workload may not read IAM")
    # The approver exists only to carry a human through Cloud Run's audience requirement.
    # Any project role on it would turn a break-glass credential into a standing one.
    approver = next(identity for identity in identities if identity.name == "approver-sa")
    if approver.roles:
        raise ValueError("approver identity may hold no project role")
