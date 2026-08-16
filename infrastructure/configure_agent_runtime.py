"""Register and authorize one deployed, identity-bearing Bastion Agent Runtime."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any

from agentplatform import Client

PROJECT = os.environ["GCP_PROJECT_ID"]
PROJECT_NUMBER = os.environ["GCP_PROJECT_NUMBER"]
REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
RUN_REGION = os.environ.get("GCP_REGION", "europe-north2")
ENGINE_ID = os.environ["BASTION_RUNTIME_AGENT_ENGINE_ID"]
SERVICE = "bastion-runtime-orchestrator"
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for Agent Runtime authorization")

PROJECT_ROLES = (
    "roles/aiplatform.user",
    "roles/datastore.user",
    "roles/modelarmor.user",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/monitoring.metricWriter",
)


def call(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(  # noqa: S603 - reviewed gcloud-only arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def runtime_resource() -> Any:
    name = f"projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/{ENGINE_ID}"
    resource = Client(project=PROJECT, location=REGION).agent_engines.get(name=name).api_resource
    if resource is None:
        raise RuntimeError(f"Agent Runtime resource is absent: {name}")
    return resource


def effective_principal() -> str:
    identity = getattr(runtime_resource().spec, "effective_identity", None)
    if not identity:
        raise RuntimeError("Agent Runtime has no effective Agent Identity")
    return f"principal://{identity}"


def register_runtime() -> str:
    interface = (
        f"https://{REGION}-aiplatform.mtls.googleapis.com/v1/projects/{PROJECT_NUMBER}"
        f"/locations/{REGION}/reasoningEngines/{ENGINE_ID}"
    )
    existing = call(
        "agent-registry",
        "services",
        "describe",
        SERVICE,
        f"--location={REGION}",
        check=False,
    )
    operation = "update" if existing.returncode == 0 else "create"
    call(
        "agent-registry",
        "services",
        operation,
        SERVICE,
        f"--location={REGION}",
        "--display-name=Bastion Governed Orchestrator Runtime",
        "--description=Identity-bearing Bastion orchestrator behind Agent Gateway.",
        "--endpoint-spec-type=no-spec",
        f"--interfaces=protocolBinding=jsonrpc,url={interface}",
    )
    return interface


def authorize() -> str:
    principal = effective_principal()
    services = call(
        "agent-registry",
        "services",
        "list",
        f"--location={REGION}",
        "--format=value(registryResource)",
    ).stdout.splitlines()
    if not services:
        raise RuntimeError("regional Agent Registry is empty")
    for resource in services:
        resource_id = resource.rsplit("/", 1)[-1]
        # The current Registry API returns ``.../agents/...`` even for NO_SPEC HTTP
        # services; older documentation shows those as endpoint resources. Bind to the
        # authoritative resource type rather than guessing from the service's spec.
        selector = "--agent" if "/agents/" in resource else "--endpoint"
        call(
            "iap",
            "web",
            "add-iam-policy-binding",
            "--resource-type=agent-registry",
            f"{selector}={resource_id}",
            f"--region={REGION}",
            f"--member={principal}",
            "--role=roles/iap.egressor",
        )
    for service in ("bastion-access-auditor", "bastion-escalation-agent"):
        call(
            "run",
            "services",
            "add-iam-policy-binding",
            service,
            f"--region={RUN_REGION}",
            f"--member={principal}",
            "--role=roles/run.invoker",
        )
    for role in PROJECT_ROLES:
        call(
            "projects",
            "add-iam-policy-binding",
            PROJECT,
            f"--member={principal}",
            f"--role={role}",
            "--condition=None",
        )
    return principal


def main() -> None:
    interface = register_runtime()
    principal = authorize()
    # Do not print the complete SPIFFE principal in routine output; the resource ID is enough
    # to correlate IAM and deployment evidence without turning logs into an identity catalog.
    print(f"Authorized Agent Runtime {ENGINE_ID} for {interface} ({principal.split('/')[2]}).")


if __name__ == "__main__":
    main()
