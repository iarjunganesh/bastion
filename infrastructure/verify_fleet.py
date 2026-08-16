"""Fail a release if the deployed Bastion fleet is not private, regional, and catalogued."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, cast

from infrastructure import provision_gateway

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ["GCP_REGION"]
REGISTRY_REGION = os.environ.get("AGENT_REGISTRY_REGION", "europe-west4")
SERVICES = {
    "bastion-orchestrator": "internal",
    "bastion-access-auditor": "all",
    "bastion-escalation-agent": "all",
    "bastion-findings-api": "all",
}
PEERS = {"bastion-access-auditor", "bastion-escalation-agent"}
REQUIRED_REGISTRY_SERVICES = {
    "bastion-access-auditor",
    "bastion-escalation-agent",
    "bastion-runtime-orchestrator",
    "google-cloud-firestore",
    "google-cloud-logging",
    "google-cloud-resource-manager",
    "google-cloud-telemetry",
    "google-model-armor",
    "google-vertex-ai-global",
    "google-vertex-ai-runtime",
}
GCLOUD: str = shutil.which("gcloud") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for fleet verification")


def describe(service: str) -> dict[str, Any]:
    result = subprocess.run(  # noqa: S603 - constant executable and repository-owned query
        [
            GCLOUD,
            "run",
            "services",
            "describe",
            service,
            "--project",
            PROJECT,
            "--region",
            REGION,
            "--format=json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return cast(dict[str, Any], json.loads(result.stdout))


def main() -> None:
    errors: list[str] = []
    for service, expected_ingress in SERVICES.items():
        record = describe(service)
        metadata = record.get("metadata", {})
        template = record.get("spec", {}).get("template", {})
        # Cloud Run stores ingress on service metadata; template annotations contain only
        # revision settings such as autoscaling. Checking the latter reports an internal
        # service as public even though the platform has enforced internal ingress.
        annotations = metadata.get("annotations", {})
        service_account = template.get("spec", {}).get("serviceAccountName")
        if metadata.get("labels", {}).get("classification") != "internal":
            errors.append(f"{service}: missing internal classification")
        if annotations.get("run.googleapis.com/ingress") != expected_ingress:
            errors.append(f"{service}: ingress does not match {expected_ingress}")
        if not service_account or not service_account.endswith(".iam.gserviceaccount.com"):
            errors.append(f"{service}: missing workload service account")
        environment = template.get("spec", {}).get("containers", [{}])[0].get("env", [])
        secret_names = {
            item.get("name")
            for item in environment
            if item.get("valueFrom", {}).get("secretKeyRef")
        }
        if service in PEERS and "BASTION_A2A_SHARED_SECRET" not in secret_names:
            errors.append(f"{service}: missing origin-bound A2A credential")
        if service == "bastion-orchestrator":
            values = {item.get("name"): item.get("value") for item in environment}
            if "BASTION_A2A_SHARED_SECRET" in secret_names:
                errors.append(f"{service}: dispatcher retains a direct-peer credential")
            if not values.get("BASTION_RUNTIME_AGENT_ENGINE_ID"):
                errors.append(f"{service}: managed Runtime target is missing")
    trigger = subprocess.run(  # noqa: S603 - constant gcloud executable and deployment identifier
        [
            GCLOUD,
            "eventarc",
            "triggers",
            "describe",
            "bastion-investigations-to-orchestrator",
            "--project",
            PROJECT,
            "--location",
            REGION,
            "--format=value(destination.cloudRun.path)",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if trigger.returncode != 0 or trigger.stdout.strip() != "/apps/orchestrator/trigger/eventarc":
        errors.append("Eventarc investigation trigger is absent or routed to the wrong path")
    subscription = subprocess.run(  # noqa: S603 - fixed gcloud query
        [
            GCLOUD,
            "pubsub",
            "subscriptions",
            "list",
            "--project",
            PROJECT,
            "--filter=topic:bastion-investigations",
            "--format=json(ackDeadlineSeconds,deadLetterPolicy)",
            "--limit=1",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    policies = json.loads(subscription.stdout or "[]") if subscription.returncode == 0 else []
    dead_letter = policies[0].get("deadLetterPolicy", {}) if policies else {}
    if not policies or policies[0].get("ackDeadlineSeconds") != 600:
        errors.append("Eventarc transport ack deadline is shorter than managed Runtime work")
    if dead_letter.get("maxDeliveryAttempts") != 5:
        errors.append("Eventarc transport lacks the five-attempt dead-letter policy")
    registry = subprocess.run(  # noqa: S603 - fixed gcloud query
        [
            GCLOUD,
            "agent-registry",
            "services",
            "list",
            "--project",
            PROJECT,
            f"--location={REGISTRY_REGION}",
            "--format=value(name.basename())",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    registered = set(registry.stdout.splitlines()) if registry.returncode == 0 else set()
    missing_registry = REQUIRED_REGISTRY_SERVICES - registered
    if missing_registry:
        errors.append(f"Agent Registry is missing: {', '.join(sorted(missing_registry))}")
    errors.extend(
        provision_gateway.validate(
            provision_gateway.describe(),
            provision_gateway.describe_auth_extension(),
            provision_gateway.describe_auth_policy(),
        )
    )
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Verified {len(SERVICES)} governed services, durable DLQ, Registry catalog, "
        f"and Agent Gateway in {REGION}/{REGISTRY_REGION}."
    )


if __name__ == "__main__":
    main()
