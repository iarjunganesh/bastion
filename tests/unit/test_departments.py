"""Findings reach the team that owns the principal, not one central inbox."""

from __future__ import annotations

import pytest

from registry import departments

COMPUTE_DEFAULT = "serviceAccount:123456789012-compute@developer.gserviceaccount.com"


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("serviceAccount:data-warehouse@p.iam.gserviceaccount.com", "data-platform"),
        ("serviceAccount:bq-loader@p.iam.gserviceaccount.com", "data-platform"),
        ("serviceAccount:ml-training@p.iam.gserviceaccount.com", "ml-engineering"),
        ("serviceAccount:vertex-tuning@p.iam.gserviceaccount.com", "ml-engineering"),
        ("serviceAccount:gke-node@p.iam.gserviceaccount.com", "platform-infra"),
        (COMPUTE_DEFAULT, "platform-infra"),
        ("user:someone@example.com", "security-engineering"),
    ],
)
def test_principals_resolve_to_their_owning_department(member: str, expected: str):
    assert departments.resolve_owning_department(member)["department"] == expected


def test_the_default_compute_account_belongs_to_platform_not_security():
    """The fleet's own real over-permission routes to whoever owns compute.

    Google creates this account with roles/editor and nothing Bastion builds uses it. Routing
    it to security engineering would be the central-inbox failure in miniature.
    """
    routed = departments.resolve_owning_department(COMPUTE_DEFAULT)
    assert routed["department"] == "platform-infra"
    assert routed["escalation_target"] == "platform-oncall"


def test_an_unrecognised_principal_still_gets_an_owner():
    """A routing function that can return nothing will one day drop a finding silently."""
    routed = departments.resolve_owning_department("!!!not-a-principal!!!")
    assert routed["department"] == departments.UNASSIGNED


def test_only_escalating_findings_are_routed():
    decisions = [
        {"member": "serviceAccount:data-x@p.iam.gserviceaccount.com", "decision": "escalate"},
        {"member": "serviceAccount:ml-y@p.iam.gserviceaccount.com", "decision": "clear"},
    ]
    routed = departments.route_by_department(decisions)
    assert routed["escalated_total"] == 1
    assert [b["department"] for b in routed["departments"]] == ["data-platform"]


def test_a_team_with_nothing_to_review_is_not_notified():
    """An access review that pages every team on every run is one every team mutes."""
    routed = departments.route_by_department([{"member": COMPUTE_DEFAULT, "decision": "clear"}])
    assert routed["departments"] == []
    assert routed["department_count"] == 0


def test_one_investigation_fans_out_to_several_departments():
    decisions = [
        {"member": "serviceAccount:data-a@p.iam.gserviceaccount.com", "decision": "escalate"},
        {"member": "serviceAccount:ml-b@p.iam.gserviceaccount.com", "decision": "escalate"},
        {"member": COMPUTE_DEFAULT, "decision": "escalate"},
    ]
    routed = departments.route_by_department(decisions)
    assert routed["department_count"] == 3
    assert routed["escalated_total"] == 3


def test_findings_for_one_department_are_counted_together():
    decisions = [
        {"member": "serviceAccount:data-a@p.iam.gserviceaccount.com", "decision": "escalate"},
        {"member": "serviceAccount:dbt-b@p.iam.gserviceaccount.com", "decision": "escalate"},
    ]
    (bucket,) = departments.route_by_department(decisions)["departments"]
    assert bucket["department"] == "data-platform"
    assert bucket["finding_count"] == 2


def test_reasons_are_deduplicated_per_department():
    decisions = [
        {
            "member": "serviceAccount:data-a@p.iam.gserviceaccount.com",
            "decision": "escalate",
            "reason": "overly_broad_role",
        },
        {
            "member": "serviceAccount:data-b@p.iam.gserviceaccount.com",
            "decision": "escalate",
            "reason": "overly_broad_role",
        },
    ]
    (bucket,) = departments.route_by_department(decisions)["departments"]
    assert bucket["reasons"] == ["overly_broad_role"]


def test_the_catalog_carries_no_endpoints():
    """A catalog holding webhooks becomes a thing worth attacking; Secret Manager holds those."""
    for department in departments.load_catalog():
        assert "://" not in department["escalation_target"]


def test_routing_is_not_a_model_judgement():
    """Same principal, same department, every time — an org-chart fact, not a guess."""
    first = departments.resolve_owning_department(COMPUTE_DEFAULT)
    second = departments.resolve_owning_department(COMPUTE_DEFAULT)
    assert first == second


def test_a_catalog_without_a_catch_all_still_routes(monkeypatch):
    """The fallback exists because a catalog edit must not be able to drop a finding.

    Unreachable while the shipped catalog ends in `.*` — which is exactly why it needs a test:
    the day someone tightens that last pattern, this is what stops findings vanishing.
    """
    narrow = [d for d in departments.load_catalog() if d["id"] != departments.UNASSIGNED]
    narrow.append(
        {
            **next(d for d in departments.load_catalog() if d["id"] == departments.UNASSIGNED),
            "principal_patterns": [r"^serviceAccount:sec-"],
        }
    )
    monkeypatch.setattr(departments, "load_catalog", lambda: narrow)

    routed = departments.resolve_owning_department("user:nobody-owns-me@example.com")
    assert routed["department"] == departments.UNASSIGNED
