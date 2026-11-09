"""Inventory, then optionally remove, Bastion's serving resources in dependency-safe order.

Dry run by default: it verifies the exact project, describes every allowlisted target read-only,
reconciles the regional Agent Registry against the allowlist, and prints an auditable JSON
inventory. Nothing is deleted without ``--apply --confirm-project <project>``, and ``--apply``
refuses to start unless a fresh inventory is clean.

What "clean" means, and why each rule exists (D4 dry run, 9 November 2026):

- A target is either *present* (describe succeeded) or *absent* (the primary gcloud error is
  that command's own not-found for that exact resource). Any other failure -- permission,
  authentication, quota, timeout, an unparseable error -- stops the run; errors are never
  broadly suppressed, and text elsewhere in stderr (an account name, for example) cannot turn a
  refusal into absence.
- gcloud stderr is never echoed: it can name the authenticated principal. Failures are reported
  as an allowlisted status code against the affected target.
- The legacy Cloud Run dispatcher's former registry card (``bastion-orchestrator``) is
  *expected* to be absent: ``register_agents`` deletes it. The previous script tried to delete
  it unconditionally and would have aborted halfway, before the Gateway.
- Every registry service in the location must be on the allowlist, which now includes the
  fourteen Google API endpoint registrations ``register_agents`` creates for Gateway egress.
  An unrecognised entry stops the run rather than being skipped or deleted, and so does any
  disagreement between the listing and the individual describes.
- A delete that times out has an unknown outcome: the run stops, reports how many deletions
  completed, and requires a fresh inventory before any retry.
- Each registry entry must look like Bastion's: exact resource name, the display name Bastion
  writes, and, for endpoint registrations, only Google API interface hosts.

Retained deliberately, and never touched here: Firestore, Secret Manager, the managed Runtime
and Memory, audit logs and buckets, images, service accounts, IAM. Removing any of those is a
separate platform-owner decision.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

PROJECT = os.environ["GCP_PROJECT_ID"]
RUN_REGION = os.environ.get("GCP_REGION", "europe-north2")
REGISTRY_REGION = os.environ.get("AGENT_REGISTRY_REGION", "europe-west4")
GATEWAY_REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")

WORKER_CARDS = ("bastion-access-auditor", "bastion-escalation-agent")
RUNTIME_CARD = "bastion-runtime-orchestrator"
RUNTIME_DISPLAY_NAME = "Bastion Governed Orchestrator Runtime"
LEGACY_EXPECTED_ABSENT = ("bastion-orchestrator",)
# Mirrors `register_agents.PLATFORM_ENDPOINTS`; a unit test keeps the two identical.
PLATFORM_ENDPOINTS = (
    "google-vertex-ai-global",
    "google-vertex-ai-runtime",
    "google-vertex-ai-runtime-mtls",
    "google-vertex-ai-runtime-rep",
    "google-agent-registry",
    "google-cloud-resource-manager",
    "google-cloud-resource-manager-mtls",
    "google-cloud-firestore",
    "google-cloud-logging",
    "google-cloud-telemetry",
    "google-cloud-telemetry-mtls",
    "google-iam-credentials",
    "google-iam-credentials-mtls",
    "google-model-armor",
)
CLOUD_RUN_SERVICES = (
    "bastion-orchestrator",
    "bastion-access-auditor",
    "bastion-escalation-agent",
    "bastion-findings-api",
)

# gcloud's primary error line: ``ERROR: (gcloud.<command>) <message>``. Only the first such line
# is parsed; the rest of stderr is ignored and never printed.
_PRIMARY_ERROR = re.compile(r"^ERROR: \(gcloud\.(?P<command>[\w.-]+)\) (?P<message>.*)$", re.M)
_STATUS = re.compile(r"(?P<code>[A-Z][A-Z_]+):")
# Canonical RPC status codes; anything else is reported as "unclassified".
_KNOWN_STATUS = frozenset(
    {
        "NOT_FOUND",
        "PERMISSION_DENIED",
        "UNAUTHENTICATED",
        "RESOURCE_EXHAUSTED",
        "FAILED_PRECONDITION",
        "INVALID_ARGUMENT",
        "ALREADY_EXISTS",
        "ABORTED",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "INTERNAL",
        "UNKNOWN",
        "CANCELLED",
        "UNIMPLEMENTED",
        "OUT_OF_RANGE",
        "DATA_LOSS",
    }
)
_REFUSALS = re.compile(r"\b(PERMISSION_DENIED|UNAUTHENTICATED|RESOURCE_EXHAUSTED)\b")


@dataclass(frozen=True)
class Target:
    kind: str
    name: str
    describe: tuple[str, ...]
    delete: tuple[str, ...]
    expected_absent: bool = False


def _registry(name: str, *, expected_absent: bool = False) -> Target:
    location = f"--location={REGISTRY_REGION}"
    return Target(
        "agent_registry_service",
        name,
        ("agent-registry", "services", "describe", name, location),
        ("agent-registry", "services", "delete", name, location),
        expected_absent,
    )


def targets() -> list[Target]:
    """The complete allowlist, in deletion order: ingress, transport, services, catalog, egress."""
    run_region = f"--region={RUN_REGION}"
    trigger = "bastion-investigations-to-orchestrator"
    result = [
        Target(
            "eventarc_trigger",
            trigger,
            ("eventarc", "triggers", "describe", trigger, f"--location={RUN_REGION}"),
            ("eventarc", "triggers", "delete", trigger, f"--location={RUN_REGION}"),
        ),
        Target(
            "pubsub_subscription",
            "bastion-dead-letter-review",
            ("pubsub", "subscriptions", "describe", "bastion-dead-letter-review"),
            ("pubsub", "subscriptions", "delete", "bastion-dead-letter-review"),
        ),
    ]
    result += [
        Target(
            "pubsub_topic",
            topic,
            ("pubsub", "topics", "describe", topic),
            ("pubsub", "topics", "delete", topic),
        )
        for topic in ("bastion-investigations-dead-letter", "bastion-investigations")
    ]
    result += [
        Target(
            "cloud_run_service",
            service,
            ("run", "services", "describe", service, run_region),
            ("run", "services", "delete", service, run_region),
        )
        for service in CLOUD_RUN_SERVICES
    ]
    result += [_registry(name) for name in (*WORKER_CARDS, RUNTIME_CARD, *PLATFORM_ENDPOINTS)]
    result += [_registry(name, expected_absent=True) for name in LEGACY_EXPECTED_ABSENT]
    gateway_location = f"--location={GATEWAY_REGION}"
    result.append(
        Target(
            "agent_gateway",
            "bastion-egress",
            ("network-services", "agent-gateways", "describe", "bastion-egress", gateway_location),
            ("network-services", "agent-gateways", "delete", "bastion-egress", gateway_location),
        )
    )
    return result


Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def gcloud_runner(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not executable:
        raise RuntimeError("gcloud must be installed for teardown")
    return subprocess.run(  # noqa: S603 - fixed allowlisted arguments only
        [executable, *args, f"--project={PROJECT}", "--quiet"],
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


class TeardownError(RuntimeError):
    """A condition that makes deletion unsafe; the run stops and says why."""


def _status(process: subprocess.CompletedProcess[str]) -> str:
    """An allowlisted status for a failed gcloud call; never any raw stderr text."""
    primary = _PRIMARY_ERROR.search(process.stderr or "")
    code = _STATUS.match(primary.group("message")) if primary else None
    if code and code.group("code") in _KNOWN_STATUS:
        return code.group("code")
    return f"unclassified gcloud error (exit {process.returncode})"


def _is_not_found(target: Target, process: subprocess.CompletedProcess[str]) -> bool:
    """True only for this command's own not-found naming this exact resource."""
    stderr = process.stderr or ""
    primary = _PRIMARY_ERROR.search(stderr)
    if not primary or primary.group("command") != ".".join(target.describe[:3]):
        return False
    if _REFUSALS.search(stderr):
        return False
    message = primary.group("message")
    name = re.escape(target.name)
    if target.kind == "cloud_run_service":
        pattern = rf"Cannot find service \[{name}\]"
    else:
        pattern = rf"NOT_FOUND: Resource (?:'[^']*/{name}'|not found \(resource={name}\))"
    return re.match(pattern, message) is not None


def _call(run: Runner, args: Sequence[str], what: str) -> subprocess.CompletedProcess[str]:
    try:
        return run(args)
    except subprocess.TimeoutExpired as exc:
        raise TeardownError(f"{what} timed out") from exc


def _registry_problems(target: Target, record: dict[str, Any]) -> list[str]:
    expected_name = f"projects/{PROJECT}/locations/{REGISTRY_REGION}/services/{target.name}"
    problems = []
    if record.get("name") != expected_name:
        problems.append("resource name is not this project's exact registry location")
    display = RUNTIME_DISPLAY_NAME if target.name == RUNTIME_CARD else target.name
    if record.get("displayName") != display:
        problems.append("display name is not the one Bastion writes")
    if target.name in PLATFORM_ENDPOINTS:
        hosts = [urlparse(i.get("url", "")).hostname or "" for i in record.get("interfaces", [])]
        if "endpointSpec" not in record or not hosts:
            problems.append("not an endpoint registration")
        elif not all(h == "googleapis.com" or h.endswith(".googleapis.com") for h in hosts):
            problems.append("endpoint interface is not a Google API host")
    return problems


def inventory(run: Runner) -> dict[str, Any]:
    """Read-only. Raises `TeardownError` on any condition that would make deletion unsafe."""
    project = _call(run, ("projects", "describe", PROJECT, "--format=json"), "project describe")
    if project.returncode != 0:
        raise TeardownError(f"cannot describe project {PROJECT}: {_status(project)}")
    if json.loads(project.stdout).get("projectId") != PROJECT:
        raise TeardownError("described project does not match GCP_PROJECT_ID")
    rows = []
    problems: list[str] = []
    for target in targets():
        process = _call(
            run, (*target.describe, "--format=json"), f"describe of {target.kind} {target.name}"
        )
        if process.returncode == 0:
            state = "present"
            if target.kind == "agent_registry_service":
                for problem in _registry_problems(target, json.loads(process.stdout or "{}")):
                    problems.append(f"{target.name}: {problem}")
            if target.expected_absent:
                problems.append(f"{target.name}: expected absent but present")
        elif _is_not_found(target, process):
            state = "absent"
        else:
            raise TeardownError(f"cannot describe {target.kind} {target.name}: {_status(process)}")
        rows.append(
            {
                "kind": target.kind,
                "name": target.name,
                "state": state,
                "expected_absent": target.expected_absent,
            }
        )
    listing = _call(
        run,
        ("agent-registry", "services", "list", f"--location={REGISTRY_REGION}", "--format=json"),
        "Agent Registry listing",
    )
    if listing.returncode != 0:
        raise TeardownError(f"cannot list the Agent Registry: {_status(listing)}")
    allowed = {t.name for t in targets() if t.kind == "agent_registry_service"}
    described: set[str] = {
        str(r["name"])
        for r in rows
        if r["kind"] == "agent_registry_service" and r["state"] == "present"
    }
    services = json.loads(listing.stdout or "[]")
    listed = {str(s.get("name", "")).rsplit("/", 1)[-1] for s in services}
    problems += [
        f"{name}: unrecognised Agent Registry service" for name in sorted(listed - allowed)
    ]
    # The listing and the describes must agree exactly; a disagreement means the catalog changed
    # mid-inventory (or one read is wrong), so nothing is deleted on the strength of either.
    problems += [
        f"{name}: listed in the Agent Registry but described as absent"
        for name in sorted((listed & allowed) - described)
    ]
    problems += [
        f"{name}: described as present but missing from the Agent Registry listing"
        for name in sorted(described - listed)
    ]
    return {
        "project": PROJECT,
        "regions": {
            "cloud_run": RUN_REGION,
            "agent_registry": REGISTRY_REGION,
            "agent_gateway": GATEWAY_REGION,
        },
        "targets": rows,
        "problems": problems,
        "would_delete": [r["name"] for r in rows if r["state"] == "present"],
        "retained_by_design": [
            "Firestore",
            "Secret Manager",
            "managed Runtime and Memory",
            "audit logs and buckets",
            "images",
            "service accounts",
            "IAM",
        ],
    }


def apply(run: Runner, record: dict[str, Any]) -> list[str]:
    """Delete exactly the present allowlisted targets, in order, stopping on the first failure."""
    if record["problems"]:
        raise TeardownError(
            "inventory is not clean; nothing deleted: " + "; ".join(record["problems"])
        )
    present = {(r["kind"], r["name"]) for r in record["targets"] if r["state"] == "present"}
    deleted: list[str] = []
    for target in targets():
        if (target.kind, target.name) not in present:
            continue
        try:
            process = run(target.delete)
        except subprocess.TimeoutExpired as exc:
            raise TeardownError(
                f"delete of {target.kind} {target.name} timed out after {len(deleted)} completed "
                "deletions; its outcome is unknown. Run the dry-run inventory again before any "
                "retry."
            ) from exc
        if process.returncode != 0:
            raise TeardownError(
                f"delete failed for {target.kind} {target.name} after {len(deleted)} deletions: "
                f"{_status(process)}. Run the dry-run inventory again before any retry."
            )
        deleted.append(target.name)
    return deleted


def main(argv: Sequence[str] | None = None, run: Runner = gcloud_runner) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-project")
    parser.add_argument("--inventory-out", help="also write the JSON inventory to this path")
    args = parser.parse_args(argv)
    if args.apply and args.confirm_project != PROJECT:
        print("--apply requires --confirm-project matching GCP_PROJECT_ID", file=sys.stderr)
        return 2
    try:
        record = inventory(run)
    except TeardownError as exc:
        print(f"Stopped before any deletion: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(record, indent=2)
    print(text)
    if args.inventory_out:
        with open(args.inventory_out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    if not args.apply:
        print("Dry run only; nothing was deleted.", file=sys.stderr)
        return 1 if record["problems"] else 0
    try:
        deleted = apply(run, record)
    except TeardownError as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        return 1
    print(
        f"Deleted {len(deleted)} serving resources; retained state was not touched.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
