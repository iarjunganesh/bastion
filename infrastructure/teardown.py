"""Print or apply the exact Bastion resource teardown in dependency-safe order."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess

PROJECT = os.environ["GCP_PROJECT_ID"]
RUN_REGION = os.environ.get("GCP_REGION", "europe-north2")
RUNTIME_REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for teardown")


def commands() -> list[list[str]]:
    values = [
        [
            "eventarc",
            "triggers",
            "delete",
            "bastion-investigations-to-orchestrator",
            f"--location={RUN_REGION}",
        ],
        ["pubsub", "subscriptions", "delete", "bastion-dead-letter-review"],
        ["pubsub", "topics", "delete", "bastion-investigations-dead-letter"],
        ["pubsub", "topics", "delete", "bastion-investigations"],
    ]
    values.extend(
        ["run", "services", "delete", service, f"--region={RUN_REGION}"]
        for service in (
            "bastion-orchestrator",
            "bastion-access-auditor",
            "bastion-escalation-agent",
            "bastion-findings-api",
        )
    )
    values.extend(
        ["agent-registry", "services", "delete", service, f"--location={RUNTIME_REGION}"]
        for service in (
            "bastion-runtime-orchestrator",
            "bastion-orchestrator",
            "bastion-access-auditor",
            "bastion-escalation-agent",
        )
    )
    values.append(
        [
            "network-services",
            "agent-gateways",
            "delete",
            "bastion-egress",
            f"--location={RUNTIME_REGION}",
        ]
    )
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-project")
    args = parser.parse_args()
    if not args.apply:
        for command in commands():
            print("gcloud", *command, "--project", PROJECT, "--quiet")
        print("Dry run only; Firestore, secrets, retained audit logs, and Runtime are preserved.")
        return
    if args.confirm_project != PROJECT:
        raise SystemExit("--apply requires --confirm-project matching GCP_PROJECT_ID")
    for command in commands():
        subprocess.run(  # noqa: S603 - exact allowlisted teardown resources above
            [GCLOUD, *command, "--project", PROJECT, "--quiet"], check=True
        )
    print("Removed Bastion serving resources; retained state and compliance records remain.")


if __name__ == "__main__":
    main()
