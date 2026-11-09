"""Teardown is dry-run first, allowlisted, and stops on anything it cannot classify."""

from __future__ import annotations

import ast
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

from infrastructure import teardown

ROOT = Path(__file__).resolve().parents[2]
P = teardown.PROJECT
REG = teardown.REGISTRY_REGION


def _done(code: int = 0, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], code, out, err)


def _registry_record(name: str) -> dict[str, object]:
    record: dict[str, object] = {
        "name": f"projects/{P}/locations/{REG}/services/{name}",
        "displayName": teardown.RUNTIME_DISPLAY_NAME if name == teardown.RUNTIME_CARD else name,
    }
    if name in teardown.PLATFORM_ENDPOINTS:
        record["endpointSpec"] = {"type": "NO_SPEC"}
        record["interfaces"] = [{"url": "https://logging.googleapis.com"}]
    return record


class FakeCloud:
    """A scripted gcloud: everything present except the expected-absent legacy card."""

    def __init__(self) -> None:
        self.absent = set(teardown.LEGACY_EXPECTED_ABSENT)
        self.registry_overrides: dict[str, dict[str, object]] = {}
        self.extra_registry: list[str] = []
        self.errors: dict[str, str] = {}
        self.fail_delete: set[str] = set()
        self.project_id = P
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        args = tuple(args)
        self.calls.append(args)
        if args[:2] == ("projects", "describe"):
            return _done(out=json.dumps({"projectId": self.project_id}))
        if args[:3] == ("agent-registry", "services", "list"):
            names = [
                t.name
                for t in teardown.targets()
                if t.kind == "agent_registry_service" and t.name not in self.absent
            ]
            names += self.extra_registry
            return _done(
                out=json.dumps(
                    [{"name": f"projects/{P}/locations/{REG}/services/{n}"} for n in names]
                )
            )
        name = args[3]
        if name in self.errors:
            return _done(1, err=self.errors[name])
        if "delete" in args:
            return _done(1, err="ERROR: PERMISSION_DENIED") if name in self.fail_delete else _done()
        # The legacy registry card shares its name with a live Cloud Run service; absence is
        # scoped to the registry so the two are never conflated.
        if args[0] == "agent-registry" and name in self.absent:
            return _done(1, err=f"ERROR: NOT_FOUND: Resource '{name}' was not found.")
        if args[0] == "agent-registry":
            return _done(out=json.dumps(self.registry_overrides.get(name, _registry_record(name))))
        return _done(out="{}")


def test_allowlist_covers_every_endpoint_register_agents_creates():
    tree = ast.parse((ROOT / "infrastructure" / "register_agents.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and getattr(node.target, "id", "") == "PLATFORM_ENDPOINTS"
        ):
            created = {key.value for key in node.value.keys}  # type: ignore[union-attr]
            break
    else:  # pragma: no cover - the constant is part of register_agents' contract
        raise AssertionError("PLATFORM_ENDPOINTS not found")
    assert created == set(teardown.PLATFORM_ENDPOINTS)
    assert len(teardown.PLATFORM_ENDPOINTS) == 14


def test_deletion_order_is_ingress_transport_services_catalog_egress():
    kinds = [t.kind for t in teardown.targets()]
    order = [
        "eventarc_trigger",
        "pubsub_subscription",
        "pubsub_topic",
        "cloud_run_service",
        "agent_registry_service",
        "agent_gateway",
    ]
    assert [k for i, k in enumerate(kinds) if i == 0 or kinds[i - 1] != k] == order
    assert all(f"--project={P}" not in " ".join(t.delete) for t in teardown.targets())


def test_dry_run_is_read_only_and_classifies_the_legacy_card_as_expected_absent():
    cloud = FakeCloud()
    record = teardown.inventory(cloud)
    assert record["problems"] == []
    legacy = [
        r
        for r in record["targets"]
        if r["name"] == "bastion-orchestrator" and r["kind"] == "agent_registry_service"
    ]
    assert legacy == [
        {
            "kind": "agent_registry_service",
            "name": "bastion-orchestrator",
            "state": "absent",
            "expected_absent": True,
        }
    ]
    assert not any("delete" in call for call in cloud.calls)
    assert "bastion-egress" in record["would_delete"]


def test_main_dry_run_never_deletes_and_writes_the_inventory(tmp_path, capsys):
    cloud = FakeCloud()
    out = tmp_path / "inventory.json"
    assert teardown.main(["--inventory-out", str(out)], run=cloud) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["project"] == P
    assert not any("delete" in call for call in cloud.calls)
    assert "Dry run only" in capsys.readouterr().err


def test_apply_requires_the_exact_project():
    cloud = FakeCloud()
    assert teardown.main(["--apply", "--confirm-project", "someone-else"], run=cloud) == 2
    assert cloud.calls == []


def test_apply_deletes_present_targets_in_order_and_skips_the_absent_legacy_card():
    cloud = FakeCloud()
    assert teardown.main(["--apply", "--confirm-project", P], run=cloud) == 0
    deleted = [call[3] for call in cloud.calls if "delete" in call]
    assert deleted[0] == "bastion-investigations-to-orchestrator"
    assert deleted[-1] == "bastion-egress"
    registry_deletes = [
        c[3] for c in cloud.calls if c[:3] == ("agent-registry", "services", "delete")
    ]
    assert "bastion-orchestrator" not in registry_deletes
    assert len(registry_deletes) == 2 + 1 + 14


def test_an_unrecognised_registry_entry_stops_apply_before_any_deletion():
    cloud = FakeCloud()
    cloud.extra_registry = ["someone-elses-agent"]
    assert teardown.main(["--apply", "--confirm-project", P], run=cloud) == 1
    assert not any("delete" in call for call in cloud.calls)


def test_a_registry_entry_that_does_not_look_like_bastions_stops_the_run():
    cloud = FakeCloud()
    record = _registry_record("google-cloud-logging")
    record["interfaces"] = [{"url": "https://attacker.example"}]
    cloud.registry_overrides["google-cloud-logging"] = record
    cloud.registry_overrides["bastion-access-auditor"] = {
        "name": f"projects/other/locations/{REG}/services/bastion-access-auditor",
        "displayName": "bastion-access-auditor",
    }
    problems = teardown.inventory(cloud)["problems"]
    assert "google-cloud-logging: endpoint interface is not a Google API host" in problems
    assert any(p.startswith("bastion-access-auditor: resource name") for p in problems)
    with pytest.raises(teardown.TeardownError):
        teardown.apply(cloud, teardown.inventory(cloud))


def test_a_present_legacy_card_or_missing_endpoint_spec_is_a_problem():
    cloud = FakeCloud()
    cloud.absent = set()
    cloud.registry_overrides["google-model-armor"] = {
        "name": f"projects/{P}/locations/{REG}/services/google-model-armor",
        "displayName": "google-model-armor",
    }
    problems = teardown.inventory(cloud)["problems"]
    assert "bastion-orchestrator: expected absent but present" in problems
    assert "google-model-armor: not an endpoint registration" in problems


def test_permission_errors_are_never_treated_as_absence(capsys):
    cloud = FakeCloud()
    cloud.errors["bastion-findings-api"] = "ERROR: PERMISSION_DENIED: denied"
    assert teardown.main([], run=cloud) == 1
    assert "cannot describe cloud_run_service bastion-findings-api" in capsys.readouterr().err


def test_a_different_project_identity_stops_the_run():
    cloud = FakeCloud()
    cloud.project_id = "another-project"
    with pytest.raises(teardown.TeardownError, match="does not match"):
        teardown.inventory(cloud)


def test_an_unreadable_project_or_registry_listing_stops_the_run():
    def refuse(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(1, err="ERROR: PERMISSION_DENIED")

    with pytest.raises(teardown.TeardownError, match="cannot describe project"):
        teardown.inventory(refuse)

    cloud = FakeCloud()
    original = cloud.__call__

    def no_listing(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
        if tuple(args[:3]) == ("agent-registry", "services", "list"):
            return _done(1, err="ERROR: UNAVAILABLE")
        return original(args)

    with pytest.raises(teardown.TeardownError, match="cannot list the Agent Registry"):
        teardown.inventory(no_listing)


def test_a_failed_delete_stops_immediately_and_reports_progress(capsys):
    cloud = FakeCloud()
    cloud.fail_delete = {"bastion-orchestrator"}
    assert teardown.main(["--apply", "--confirm-project", P], run=cloud) == 1
    deletes = [c[3] for c in cloud.calls if "delete" in c]
    assert deletes[-1] == "bastion-orchestrator" and "bastion-egress" not in deletes
    assert "after 4 deletions" in capsys.readouterr().err


def test_main_stops_before_deletion_when_the_inventory_is_unsafe(capsys):
    cloud = FakeCloud()
    cloud.project_id = "another-project"
    assert teardown.main(["--apply", "--confirm-project", P], run=cloud) == 1
    assert "Stopped before any deletion" in capsys.readouterr().err
    cloud = FakeCloud()
    cloud.extra_registry = ["unknown"]
    assert teardown.main([], run=cloud) == 1
