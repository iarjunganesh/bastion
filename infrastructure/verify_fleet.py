"""Fail a release if the deployed Bastion fleet is not private, regional, and catalogued."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, cast

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ["GCP_REGION"]
SERVICES = ("bastion-orchestrator", "bastion-access-auditor", "bastion-escalation-agent")
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
        annotations = template.get("metadata", {}).get("annotations", {})
        service_account = template.get("spec", {}).get("serviceAccountName")
        if metadata.get("labels", {}).get("classification") != "internal":
            errors.append(f"{service}: missing internal classification")
        if annotations.get("run.googleapis.com/ingress") != "internal":
            errors.append(f"{service}: ingress is not internal")
        if not service_account or not service_account.endswith(".iam.gserviceaccount.com"):
            errors.append(f"{service}: missing workload service account")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Verified {len(SERVICES)} private Bastion Cloud Run services in {REGION}.")


if __name__ == "__main__":
    main()
