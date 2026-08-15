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
    completed = subprocess.run(  # noqa: S603 - constant executable and repository-owned arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed


def main() -> None:
    project_number = call(
        "projects", "describe", PROJECT, "--format=value(projectNumber)"
    ).stdout.strip()
    if not project_number:
        raise RuntimeError("could not resolve the project number for canonical Cloud Run URLs")
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
        agent_name = service.removeprefix("bastion-").replace("-", "_")
        # Agent Registry's interface enum names the A2A transport as JSON-RPC.  The
        # agent card is a discovery document; consumers invoke this private endpoint.
        uri = f"https://{service}-{project_number}.{REGION}.run.app/a2a/{agent_name}"
        call(
            "agent-registry",
            "services",
            "create",
            service,
            f"--location={REGION}",
            f"--display-name={service}",
            f"--description={description}",
            "--agent-spec-type=no-spec",
            f'--interfaces=[{{"protocolBinding":"jsonrpc","url":"{uri}"}}]',
        )
    print(f"Registered {len(CATALOG)} Bastion agents in Agent Registry location {REGION}.")


if __name__ == "__main__":
    main()
