"""Register private Cloud Run agents for governed cross-department discovery."""

from __future__ import annotations

import os
import shutil
import subprocess

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ["GCP_REGION"]
GCLOUD: str = shutil.which("gcloud") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for Agent Registry registration")

CATALOG = {
    "bastion-access-auditor": "Read-only IAM anomaly investigation for Security Engineering.",
    "bastion-escalation-agent": "Department-scoped human escalation with no IAM read access.",
    "bastion-orchestrator": "Policy-owned workflow coordinator for approved Bastion peers.",
}


def call(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - constant executable and repository-owned arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=check,
        text=True,
        capture_output=True,
    )


def main() -> None:
    for service, description in CATALOG.items():
        existing = call(
            "agent-registry",
            "services",
            "describe",
            service,
            f"--location={REGION}",
            check=False,
        )
        if existing.returncode == 0:
            continue
        uri = call(
            "run",
            "services",
            "describe",
            service,
            f"--region={REGION}",
            "--format=value(status.url)",
        ).stdout.strip()
        if not uri:
            raise RuntimeError(f"Cloud Run service {service} has no URL")
        call(
            "agent-registry",
            "services",
            "create",
            service,
            f"--location={REGION}",
            f"--display-name={service}",
            f"--description={description}",
            "--agent-spec-type=no-spec",
            f"--interfaces=protocolBinding=a2a,url={uri}",
        )
    print(f"Registered {len(CATALOG)} Bastion agents in Agent Registry location {REGION}.")


if __name__ == "__main__":
    main()
