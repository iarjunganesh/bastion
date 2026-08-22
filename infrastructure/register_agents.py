"""Register private Cloud Run agents for governed cross-department discovery."""

from __future__ import annotations

import json
import os
import shutil
import subprocess

from google.adk.a2a._compat import parse_agent_card
from google.protobuf.json_format import MessageToDict

from infrastructure.agent_server import _a2a_card

PROJECT = os.environ["GCP_PROJECT_ID"]
CLOUD_RUN_REGION = os.environ["GCP_REGION"]
REGISTRY_REGION = os.environ.get("AGENT_REGISTRY_REGION", CLOUD_RUN_REGION)
GCLOUD: str = shutil.which("gcloud") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for Agent Registry registration")

CATALOG: dict[str, tuple[str, str]] = {
    "bastion-access-auditor": (
        "access_auditor",
        "Read-only IAM anomaly investigation for Security Engineering.",
    ),
    "bastion-escalation-agent": (
        "escalation_agent",
        "Department-scoped human escalation with no IAM read access.",
    ),
}
LEGACY_DISPATCHER_SERVICE = "bastion-orchestrator"

# Agent-to-Anywhere denies destinations that are absent from the bound registry. These are
# the Google APIs the packaged Orchestrator itself uses; keeping them beside the A2A catalog
# makes the runtime's egress allowlist reviewable and reproducible.
PLATFORM_ENDPOINTS: dict[str, tuple[str, str]] = {
    "google-vertex-ai-global": (
        "https://aiplatform.googleapis.com",
        "Gemini inference and Agent Runtime session or memory operations.",
    ),
    "google-vertex-ai-runtime": (
        f"https://{REGISTRY_REGION}-aiplatform.googleapis.com",
        "Regional Agent Runtime control and data plane.",
    ),
    "google-vertex-ai-runtime-mtls": (
        f"https://{REGISTRY_REGION}-aiplatform.mtls.googleapis.com",
        "Regional mTLS Agent Runtime endpoint variant.",
    ),
    "google-vertex-ai-runtime-rep": (
        f"https://aiplatform.{REGISTRY_REGION}.rep.googleapis.com",
        "Regional replicated Agent Runtime endpoint variant.",
    ),
    "google-agent-registry": (
        "https://agentregistry.googleapis.com",
        "Automatic governed service discovery.",
    ),
    "google-cloud-resource-manager": (
        "https://cloudresourcemanager.googleapis.com",
        "Resolve the Runtime project number to its configured project ID.",
    ),
    # The Vertex AI client resolves the project number through the mTLS host, which is a
    # distinct endpoint as far as Agent-to-Anywhere is concerned. Registering only the plain
    # host fails the Runtime closed during initialization with "unregistered in the Agent
    # Registry" - the control behaving correctly against an incomplete catalog.
    "google-cloud-resource-manager-mtls": (
        "https://cloudresourcemanager.mtls.googleapis.com",
        "mTLS variant of the project-number resolution endpoint.",
    ),
    "google-cloud-firestore": (
        "https://firestore.googleapis.com",
        "Durable investigation leases and approved exception memory.",
    ),
    "google-cloud-logging": (
        "https://logging.googleapis.com",
        "Structured compliance audit log export.",
    ),
    "google-cloud-telemetry": (
        "https://telemetry.googleapis.com",
        "OpenTelemetry trace and metric export.",
    ),
    "google-model-armor": (
        "https://modelarmor."
        f"{os.environ.get('MODEL_ARMOR_LOCATION', 'europe-west4')}.rep.googleapis.com",
        "Regional prompt and response sanitization.",
    ),
}

GRPC_ENDPOINTS = {
    "google-cloud-firestore",
    "google-cloud-logging",
    "google-cloud-telemetry",
    "google-model-armor",
    "google-cloud-resource-manager",
    "google-cloud-resource-manager-mtls",
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
    # The Cloud Run Orchestrator is now durable Eventarc admission only. Keeping its former A2A
    # card would advertise a second production graph that bypasses the managed Runtime/Gateway.
    legacy = call(
        "agent-registry",
        "services",
        "describe",
        LEGACY_DISPATCHER_SERVICE,
        f"--location={REGISTRY_REGION}",
        check=False,
    )
    if legacy.returncode == 0:
        call(
            "agent-registry",
            "services",
            "delete",
            LEGACY_DISPATCHER_SERVICE,
            f"--location={REGISTRY_REGION}",
        )
    for service, (agent_name, description) in CATALOG.items():
        origin = call(
            "run",
            "services",
            "describe",
            service,
            f"--region={CLOUD_RUN_REGION}",
            "--format=value(status.url)",
        ).stdout.strip()
        if not origin.startswith("https://"):
            raise RuntimeError(f"Cloud Run returned no canonical URL for {service}")
        uri = f"{origin}/a2a/{agent_name}"
        # Registry validates the canonical A2A JSON form. The running service consumes the
        # protobuf field-name form; both are derived from the same reviewed card definition.
        card = MessageToDict(parse_agent_card(_a2a_card(agent_name, uri.rsplit("/a2a/", 1)[0])))
        card_json = json.dumps(card, separators=(",", ":"), sort_keys=True)
        existing = call(
            "agent-registry",
            "services",
            "describe",
            service,
            f"--location={REGISTRY_REGION}",
            "--format=json",
            check=False,
        )
        if existing.returncode == 0:
            call(
                "agent-registry",
                "services",
                "update",
                service,
                f"--location={REGISTRY_REGION}",
                f"--display-name={service}",
                f"--description={description}",
                "--agent-spec-type=a2a-agent-card",
                f"--agent-spec-content={card_json}",
                "--clear-interfaces",
            )
            continue
        call(
            "agent-registry",
            "services",
            "create",
            service,
            f"--location={REGISTRY_REGION}",
            f"--display-name={service}",
            f"--description={description}",
            "--agent-spec-type=a2a-agent-card",
            f"--agent-spec-content={card_json}",
        )
    for service, (uri, description) in PLATFORM_ENDPOINTS.items():
        # Agent Registry requires interface URLs to be unique, so one service cannot
        # advertise REST and gRPC against the same Google API hostname. Register the
        # transport actually used by Bastion's client library for that destination.
        protocol = "grpc" if service in GRPC_ENDPOINTS else "http-json"
        interfaces = [{"protocolBinding": protocol, "url": uri}]
        existing = call(
            "agent-registry",
            "services",
            "describe",
            service,
            f"--location={REGISTRY_REGION}",
            "--format=json",
            check=False,
        )
        operation = "create"
        if existing.returncode == 0:
            record = json.loads(existing.stdout)
            if "endpointSpec" in record:
                operation = "update"
            else:
                # Early Bastion revisions classified HTTP endpoints as NO_SPEC agents. The
                # API cannot change a spec oneof in-place, and IAP therefore cannot authorize
                # them as endpoints; replace only that exact derived registry service.
                call(
                    "agent-registry",
                    "services",
                    "delete",
                    service,
                    f"--location={REGISTRY_REGION}",
                )
        call(
            "agent-registry",
            "services",
            operation,
            service,
            f"--location={REGISTRY_REGION}",
            f"--display-name={service}",
            f"--description={description}",
            "--endpoint-spec-type=no-spec",
            f"--interfaces={json.dumps(interfaces, separators=(',', ':'))}",
        )
    print(
        f"Registered {len(CATALOG)} worker A2A cards and "
        f"{len(PLATFORM_ENDPOINTS)} platform endpoints in Agent Registry "
        f"location {REGISTRY_REGION}."
    )


if __name__ == "__main__":
    main()
