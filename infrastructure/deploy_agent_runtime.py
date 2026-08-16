"""Deploy Bastion's Orchestrator to Agent Runtime with identity and governed egress."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, cast

from agentplatform import Client, types

PROJECT = os.environ["GCP_PROJECT_ID"]
PROJECT_NUMBER = os.environ["GCP_PROJECT_NUMBER"]
REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
GATEWAY = os.environ.get("BASTION_AGENT_GATEWAY", "bastion-egress")
MEMORY_ENGINE_ID = os.environ["BASTION_MEMORY_AGENT_ENGINE_ID"]
ROOT = Path(__file__).resolve().parents[1]

SOURCE_PACKAGES = [
    "agents",
    "gateway",
    "model_armor",
    "observability",
    "registry",
    "runtime",
    "requirements.txt",
]

# The managed runtime contract needs explicit operation schemas for source deployments. This
# is the production subset Bastion exposes: durable sessions/memory and streamed investigation
# execution. Deprecated synchronous aliases are deliberately omitted.
CLASS_METHODS: list[dict[str, Any]] = [
    {
        "name": "async_create_session",
        "api_mode": "async",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "session_id": {"type": "string", "nullable": True},
                "state": {"type": "object", "nullable": True},
            },
            "required": ["user_id"],
        },
    },
    {
        "name": "async_get_session",
        "api_mode": "async",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "session_id": {"type": "string"},
            },
            "required": ["user_id", "session_id"],
        },
    },
    {
        "name": "async_add_session_to_memory",
        "api_mode": "async",
        "parameters": {
            "type": "object",
            "properties": {"session": {"type": "object", "additionalProperties": True}},
            "required": ["session"],
        },
    },
    {
        "name": "async_search_memory",
        "api_mode": "async",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "query": {"type": "string"},
            },
            "required": ["user_id", "query"],
        },
    },
    {
        "name": "async_stream_query",
        "api_mode": "async_stream",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "object", "additionalProperties": True},
                    ]
                },
                "user_id": {"type": "string"},
                "session_id": {"type": "string", "nullable": True},
                "session_events": {"type": "array", "nullable": True},
                "run_config": {"type": "object", "nullable": True},
            },
            "required": ["message", "user_id"],
        },
    },
]


def ensure_runtime_secret_access() -> None:
    """Authorize only Google's deployment identities on the one Runtime secret."""
    secret = os.environ.get("BASTION_A2A_SHARED_SECRET_ID", "bastion-a2a-shared-secret")
    gcloud = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not gcloud:
        raise RuntimeError("gcloud is required to authorize the Agent Runtime secret")
    for account in (
        f"service-{PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com",
        f"service-{PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com",
    ):
        subprocess.run(  # noqa: S603 - constant executable, reviewed arguments
            [
                gcloud,
                "secrets",
                "add-iam-policy-binding",
                secret,
                "--project",
                PROJECT,
                f"--member=serviceAccount:{account}",
                "--role=roles/secretmanager.secretAccessor",
                "--quiet",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    existing_id = os.environ.get("BASTION_RUNTIME_AGENT_ENGINE_ID")
    if existing_id:
        principal = (
            f"principal://agents.global.proj-{PROJECT_NUMBER}.system.id.goog/resources/"
            f"aiplatform/projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/"
            f"{existing_id}"
        )
        subprocess.run(  # noqa: S603 - constant executable, reviewed arguments
            [
                gcloud,
                "secrets",
                "add-iam-policy-binding",
                secret,
                "--project",
                PROJECT,
                f"--member={principal}",
                "--role=roles/secretmanager.secretAccessor",
                "--quiet",
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def gateway_config() -> dict[str, Any]:
    return {
        "agent_to_anywhere_config": {
            "agent_gateway": (f"projects/{PROJECT}/locations/{REGION}/agentGateways/{GATEWAY}")
        }
    }


def environment() -> dict[str, Any]:
    run_region = os.environ.get("GCP_REGION", "europe-north2")

    def card_url(service: str, agent: str) -> str:
        override = os.environ.get(f"BASTION_{agent.upper()}_CARD_URL")
        if override:
            return override
        gcloud = shutil.which("gcloud") or shutil.which("gcloud.cmd")
        if not gcloud:
            raise RuntimeError(f"gcloud is required to resolve canonical URL for {service}")
        result = subprocess.run(  # noqa: S603 - constant executable, reviewed arguments
            [
                gcloud,
                "run",
                "services",
                "describe",
                service,
                "--project",
                PROJECT,
                "--region",
                run_region,
                "--format=value(status.url)",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        origin = result.stdout.strip()
        if not origin.startswith("https://"):
            raise RuntimeError(f"Cloud Run returned no canonical URL for {service}")
        return f"{origin}/a2a/{agent}/.well-known/agent-card.json"

    return {
        "GCP_PROJECT_ID": PROJECT,
        "BASTION_MODEL_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "TRUE",
        # Agent Gateway's IAP policy must receive the workload's Agent Identity on Google API
        # calls. Runtime otherwise withholds that token and every correctly bound endpoint is
        # denied before the destination sees the request.
        "GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES": "false",
        "VERTEX_AI_MODEL": os.environ.get("VERTEX_AI_MODEL", "gemini-3.5-flash"),
        "AGENT_RUNTIME_REGION": REGION,
        "BASTION_MEMORY_AGENT_ENGINE_ID": MEMORY_ENGINE_ID,
        "BASTION_DURABLE_STORE_BACKEND": "firestore",
        "BASTION_A2A_SHARED_SECRET": {
            "secret": os.environ.get("BASTION_A2A_SHARED_SECRET_ID", "bastion-a2a-shared-secret"),
            "version": os.environ.get("BASTION_A2A_SHARED_SECRET_VERSION", "latest"),
        },
        "MODEL_ARMOR_TEMPLATE_ID": os.environ.get("MODEL_ARMOR_TEMPLATE_ID", "bastion-guardrail"),
        "MODEL_ARMOR_LOCATION": os.environ.get("MODEL_ARMOR_LOCATION", "europe-west4"),
        "BASTION_AUDITOR_CARD_URL": (card_url("bastion-access-auditor", "access_auditor")),
        "BASTION_ESCALATION_CARD_URL": (card_url("bastion-escalation-agent", "escalation_agent")),
        "ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS": "false",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "NO_CONTENT",
    }


def deploy() -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise RuntimeError(f"run this module from repository root: {ROOT}")
    ensure_runtime_secret_access()
    client = Client(project=PROJECT, location=REGION)
    config = {
        "display_name": "Bastion Governed Orchestrator",
        "description": (
            "Identity-bearing institutional access-review orchestrator with governed egress."
        ),
        # Relative paths are significant: absolute paths retain the host workspace hierarchy
        # in the SDK tarball and make top-level packages such as ``agents`` unimportable.
        "source_packages": SOURCE_PACKAGES,
        "entrypoint_module": "agents.orchestrator.runtime",
        "entrypoint_object": "app",
        "requirements_file": "requirements.txt",
        "class_methods": CLASS_METHODS,
        "env_vars": environment(),
        "identity_type": types.IdentityType.AGENT_IDENTITY,
        "agent_gateway_config": gateway_config(),
        "agent_framework": "google-adk",
        "python_version": "3.12",
        "min_instances": 0,
        "max_instances": 3,
        "resource_limits": {"cpu": "2", "memory": "2Gi"},
        "labels": {"app": "bastion", "role": "orchestrator", "policy": "bastion-v1"},
    }
    existing_id = os.environ.get("BASTION_RUNTIME_AGENT_ENGINE_ID")
    if existing_id:
        name = f"projects/{PROJECT_NUMBER}/locations/{REGION}/reasoningEngines/{existing_id}"
        engine = client.agent_engines.update(name=name, config=config)
    else:
        engine = client.agent_engines.create(config=config)
    resource = engine.api_resource
    if resource is None:
        raise RuntimeError("Agent Runtime deployment returned no resource")
    return cast(dict[str, Any], resource.model_dump(mode="json", exclude_none=True))


def main() -> None:
    print(json.dumps(deploy(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
