"""Validate or apply an exact Cloud Run revision rollback for the Bastion fleet."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ.get("GCP_REGION", "europe-north2")
SERVICES = (
    "bastion-orchestrator",
    "bastion-access-auditor",
    "bastion-escalation-agent",
    "bastion-findings-api",
)
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for rollback")


def call(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - reviewed gcloud-only arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=True,
        text=True,
        capture_output=True,
    )


def revisions(service: str) -> list[str]:
    result = call(
        "run",
        "revisions",
        "list",
        f"--service={service}",
        f"--region={REGION}",
        "--sort-by=~metadata.creationTimestamp",
        "--format=value(metadata.name)",
        "--limit=10",
    )
    return [revision for revision in result.stdout.splitlines() if revision_is_safe(revision)]


def revision_is_safe(revision: str) -> bool:
    result = call(
        "run",
        "revisions",
        "describe",
        revision,
        f"--region={REGION}",
        "--format=json",
    )
    record = json.loads(result.stdout)
    environment = record.get("spec", {}).get("containers", [{}])[0].get("env", [])
    service_urls = [
        item.get("value") for item in environment if item.get("name") == "BASTION_SERVICE_URL"
    ]
    return "https://placeholder.invalid" not in service_urls


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--service", choices=SERVICES)
    parser.add_argument("--revision")
    args = parser.parse_args()
    if args.apply and (not args.service or not args.revision):
        raise SystemExit("--apply requires --service and --revision")
    for service in SERVICES:
        available = revisions(service)[:2]
        if len(available) < 2:
            raise SystemExit(f"{service} has no prior ready revision")
        print(f"{service}: current={available[0]} rollback_candidate={available[1]}")
    if args.apply:
        if args.revision not in revisions(args.service)[:2]:
            raise SystemExit("requested revision is not one of the service's two newest revisions")
        call(
            "run",
            "services",
            "update-traffic",
            args.service,
            f"--region={REGION}",
            f"--to-revisions={args.revision}=100",
        )
        print(f"Rolled {args.service} to {args.revision}.")


if __name__ == "__main__":
    main()
