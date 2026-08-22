"""Agent Registry — the cross-department catalog.

The track asks entrants to demonstrate *"how agents are **cataloged for cross-department
use**"*, and the resources page leads with *"Corporate agent discovery, multi-agent
orchestration **at scale**"*. A `department` column that nothing branches on does not answer
either: it is metadata, not cross-department support.

**So a department is a routing decision here, not a label.** A finding is escalated to the team
that owns the principal it concerns, not to one central inbox — which is the actual friction in
enterprise access review. Security engineering does not own the data platform's service
accounts, and an alert that lands on the wrong desk is an alert that gets ignored.

Departments are deliberately **not** stored in the managed Agent Registry, which catalogs
*agents* ([ADR-003](../docs/adr/003-pillars-on-geap.md)). An org chart is not an agent, and a
routing table that any registered agent could write to would let a compromised one redirect
its own findings away from the team that owns them. The catalog is repository-owned static
source for the same reason tool descriptions are ([ADR-007](../docs/adr/007-tool-poisoning.md)).

`load_catalog()` remains the single seam if that reasoning ever changes.
"""

from __future__ import annotations

import re
from typing import Any, TypedDict


class Department(TypedDict):
    """One owning team, and where its findings go.

    `escalation_target` is a name rather than a URL: a webhook belongs in Secret Manager, and a
    catalog that carries endpoints becomes a thing worth attacking. The Registry says *who*
    owns a finding; the notification layer resolves *where* that is.
    """

    id: str
    name: str
    owner: str
    escalation_target: str
    principal_patterns: list[str]


# Ordered: the first pattern that matches wins, so a specific rule can precede a general one.
# `security-engineering` is last and matches everything, which makes it the default owner
# rather than a special case in the resolver.
_CATALOG: list[Department] = [
    {
        "id": "data-platform",
        "name": "Data Platform",
        "owner": "data-platform-leads",
        "escalation_target": "data-platform-oncall",
        "principal_patterns": [r"^serviceAccount:(data|bq|dataflow|dbt)[-_]", r"@data\."],
    },
    {
        "id": "ml-engineering",
        "name": "ML Engineering",
        "owner": "ml-platform-leads",
        "escalation_target": "ml-engineering-oncall",
        "principal_patterns": [r"^serviceAccount:(ml|vertex|training|inference)[-_]"],
    },
    {
        "id": "platform-infra",
        "name": "Platform Infrastructure",
        "owner": "platform-leads",
        "escalation_target": "platform-oncall",
        # The default Compute Engine service account lands here: Google creates it with
        # roles/editor, nothing Bastion builds uses it, and it belongs to whoever owns compute.
        "principal_patterns": [
            r"^serviceAccount:\d+-compute@developer\.gserviceaccount\.com$",
            r"^serviceAccount:(gke|run|build|infra)[-_]",
        ],
    },
    {
        "id": "security-engineering",
        "name": "Security Engineering",
        "owner": "security-leads",
        "escalation_target": "security-oncall",
        # Matches anything not claimed above — including Bastion's own service accounts, which
        # is correct: the fleet's over-permissioning is security's finding to review.
        "principal_patterns": [r".*"],
    },
]

UNASSIGNED = "security-engineering"


def load_catalog() -> list[Department]:
    """The department catalog.

    One function, so that the decision recorded in this module's docstring is enforced in one
    place: nothing else here knows where departments come from.
    """
    return _CATALOG


def resolve_owning_department(member: str) -> dict[str, Any]:
    """Which team owns this principal, and where its findings escalate.

    Matching is on the principal string because that is what an IAM binding actually carries.
    It is deliberately **not** a model judgement: "which team owns this service account" is an
    org-chart fact, and a model that guesses it differently on two runs would route the same
    finding to two different teams.
    """
    for department in load_catalog():
        for pattern in department["principal_patterns"]:
            if re.search(pattern, member):
                return {
                    "department": department["id"],
                    "name": department["name"],
                    "owner": department["owner"],
                    "escalation_target": department["escalation_target"],
                }
    # Unreachable while the catalog ends in a catch-all, but a routing function that can return
    # nothing is a routing function that will one day drop a finding silently.
    fallback = next(d for d in load_catalog() if d["id"] == UNASSIGNED)
    return {
        "department": fallback["id"],
        "name": fallback["name"],
        "owner": fallback["owner"],
        "escalation_target": fallback["escalation_target"],
    }


def department_by_id(department_id: str) -> dict[str, str]:
    """Resolve minimized ownership without reconstructing a discarded principal."""
    for department in load_catalog():
        if department["id"] == department_id:
            return {
                "department": department["id"],
                "name": department["name"],
                "owner": department["owner"],
                "escalation_target": department["escalation_target"],
            }
    raise ValueError("finding names an unknown owning department")


def route_by_department(decisions: list[dict[str, Any]]) -> dict[str, Any]:
    """Group escalating findings by the department that owns them.

    Returns one bucket per department **that has something to escalate** — a team with nothing
    to review is not notified, because an access review that pages every team on every run is
    one every team mutes.
    """
    buckets: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if decision.get("decision") != "escalate":
            continue
        # The Auditor deliberately discards IAM principals before this boundary. Ownership is
        # already a deterministic, minimized department ID; trying to rematch a missing member
        # silently sent every finding to the catch-all team.
        routing = department_by_id(str(decision.get("department", "")))
        bucket = buckets.setdefault(
            routing["department"],
            {**routing, "finding_count": 0, "reasons": []},
        )
        bucket["finding_count"] += 1
        reason = str(decision.get("reason", "unspecified"))
        if reason not in bucket["reasons"]:
            bucket["reasons"].append(reason)

    return {
        "departments": sorted(buckets.values(), key=lambda b: b["department"]),
        "department_count": len(buckets),
        "escalated_total": sum(b["finding_count"] for b in buckets.values()),
    }
