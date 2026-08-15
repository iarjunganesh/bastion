"""Fail a release if the deployed Bastion fleet is not private, regional, and catalogued."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, cast

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ["GCP_REGION"]
SERVICES = (
    "bastion-orchestrator",
    "bastion-access-auditor",
    "bastion-escalation-agent",
    "bastion-findings-api",
)
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
    for service in SERVICES:
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
        if annotations.get("run.googleapis.com/ingress") != "internal":
            errors.append(f"{service}: ingress is not internal")
        if not service_account or not service_account.endswith(".iam.gserviceaccount.com"):
            errors.append(f"{service}: missing workload service account")
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
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Verified {len(SERVICES)} private Bastion Cloud Run services in {REGION}.")


if __name__ == "__main__":
    main()
