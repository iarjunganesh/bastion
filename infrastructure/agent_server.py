"""Production ASGI entry point with a durable Eventarc investigation boundary.

ADK's generated Eventarc handler creates a fresh session for each request. Bastion replaces
that route for the Orchestrator: the CloudEvent id is admitted atomically to Firestore and the
stable ``context_id`` becomes the ADK session id. Consequently a retry cannot run a completed
investigation twice, and an investigation resumed weeks later sees the same managed session.
"""

from __future__ import annotations

import asyncio
import hmac
import json
import os
import shutil
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import uvicorn
from agentplatform import Client
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.cli.trigger_routes import TriggerResponse

from gateway.cloud_run_auth import PEER_SECRET_ENV, PEER_SECRET_HEADER
from observability.audit import record
from runtime.durable import InvestigationEvent
from runtime.events import decode_pubsub_event
from runtime.firestore import FirestoreDurableStore

EVENTARC_PATH = "/apps/orchestrator/trigger/eventarc"
ADK_EVENTARC_PATH = "/apps/{app_name}/trigger/eventarc"
AGENTS_ROOT = "/app/agents"
A2A_PROTOCOL_BINDING = "JSONRPC"
DEFAULT_INVESTIGATION_LEASE_SECONDS = 660


def _a2a_card(agent_dir: str, service_url: str) -> dict[str, Any]:
    """Return the service-specific A2A card ADK discovers from ``agent.json``."""
    cards = {
        "access_auditor": {
            "name": "Bastion Access Auditor",
            "description": "Read-only live IAM audit and deterministic finding generation.",
            "skill": "audit_iam",
            "department": "security-engineering",
            "owner": "security-platform",
            "purpose": "Detect over-broad IAM access without exposing principal data.",
        },
        "escalation_agent": {
            "name": "Bastion Escalation Agent",
            "description": "Count-only, idempotent routing of approved human-review escalations.",
            "skill": "notify_department",
            "department": "security-engineering",
            "owner": "security-operations",
            "purpose": "Deliver minimized findings to the department that owns remediation.",
        },
        "orchestrator": {
            "name": "Bastion Orchestrator",
            "description": "Durable investigation admission, policy enforcement, and A2A dispatch.",
            "skill": "orchestrate_investigation",
            "department": "security-engineering",
            "owner": "security-platform",
            "purpose": "Coordinate durable, policy-governed cross-department access reviews.",
        },
    }
    try:
        definition = cards[agent_dir]
    except KeyError as exc:
        raise RuntimeError(f"Unknown Bastion agent directory: {agent_dir}") from exc
    return {
        "name": definition["name"],
        "description": definition["description"],
        "version": "1.0.0",
        "provider": {
            "organization": definition["owner"],
            "url": "https://github.com/iarjunganesh/bastion",
        },
        "documentation_url": "https://github.com/iarjunganesh/bastion#the-fleet",
        "supported_interfaces": [
            {
                "url": f"{service_url.rstrip('/')}/a2a/{agent_dir}",
                "protocol_binding": A2A_PROTOCOL_BINDING,
                "protocol_version": "1.0",
            }
        ],
        "skills": [
            {
                "id": definition["skill"],
                "name": definition["skill"],
                "description": definition["description"],
                "tags": [
                    "bastion",
                    "classification:internal",
                    f"department:{definition['department']}",
                    "policy:bastion-v1",
                ],
            }
        ],
        "default_input_modes": ["text/plain"],
        "default_output_modes": ["text/plain"],
        "capabilities": {
            "streaming": False,
            "push_notifications": False,
            "extensions": [
                {
                    "uri": "https://github.com/iarjunganesh/bastion/tree/main/docs",
                    "description": "Bastion institutional governance metadata v1.",
                    "required": True,
                    "params": {
                        "ownerDepartment": definition["department"],
                        "owner": definition["owner"],
                        "purpose": definition["purpose"],
                        "dataClassification": "internal",
                        "policyVersion": "bastion-v1",
                        "approvalStatus": "approved",
                        "healthPath": "/healthz",
                    },
                }
            ],
        },
    }


def stage_a2a_agent(agent_dir: str, service_url: str) -> str:
    """Stage exactly one app and its card so a peer cannot impersonate another service.

    ADK discovers A2A apps by scanning child directories that contain ``agent.json``.  The
    production image deliberately contains the whole source tree for shared reviewed code; a
    temporary one-agent root gives each Cloud Run service exactly one public A2A identity.
    """
    source = Path(AGENTS_ROOT) / agent_dir
    if not source.is_dir():
        raise RuntimeError(f"Bastion agent source is missing: {source}")
    root = Path(tempfile.mkdtemp(prefix="bastion-a2a-"))
    destination = root / agent_dir
    shutil.copytree(source, destination)
    (destination / "agent.json").write_text(
        json.dumps(_a2a_card(agent_dir, service_url), sort_keys=True), encoding="utf-8"
    )
    return str(root)


def cloud_event_envelope(body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    """Normalize Eventarc's binary and structured CloudEvents forms."""
    if isinstance(body.get("data"), dict) and "message" in body["data"]:
        return body
    event_id = headers.get("ce-id")
    if not event_id:
        raise ValueError("Eventarc CloudEvent is missing ce-id")
    return {"id": event_id, "data": body}


async def run_managed_runtime(event: InvestigationEvent) -> None:
    """Dispatch durable Eventarc work into the identity-bearing, Gateway-bound Runtime."""
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    project_number = os.environ["GCP_PROJECT_NUMBER"]
    region = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
    engine_id = os.environ.get("BASTION_RUNTIME_AGENT_ENGINE_ID")
    if not engine_id:
        raise RuntimeError("BASTION_RUNTIME_AGENT_ENGINE_ID is required; no local fallback exists")
    name = f"projects/{project_number}/locations/{region}/reasoningEngines/{engine_id}"
    # Keep the owning client alive until every async method completes. The SDK's Engine proxy
    # delegates to the client's aiohttp connector; constructing Client as a temporary lets CPython
    # finalize that connector between ``get`` and ``async_create_session`` under Cloud Run load.
    client = Client(project=project, location=region)
    engine = client.agent_engines.get(name=name)
    session = await engine.async_create_session(user_id=event.context_id)
    async for _event in engine.async_stream_query(
        user_id=event.context_id,
        session_id=session["id"],
        # Structured data, not an imperative sentence. The previous wording -- "Run the
        # scheduled governed IAM investigation. Use only registered agents and correlate..." --
        # is, to a prompt-injection classifier, exactly what an injection looks like: an
        # instruction telling an agent what to do. Model Armor scored it at HIGH confidence,
        # the same as a real attack, and because screening fails closed it refused every
        # investigation the fleet ever ran. Provenance is what distinguishes the two, and a
        # content classifier cannot see provenance.
        #
        # Restating the constraint as data also matches where it is actually enforced. "Use
        # only registered agents" was never a request the model could honour or ignore --
        # Registry and IAP authorize egress deterministically -- so asking for it in prose
        # bought nothing and cost the whole pipeline.
        message=json.dumps(
            {"task": "scheduled_iam_access_review", "investigation_id": event.event_id},
            sort_keys=True,
        ),
    ):
        pass


def install_durable_eventarc_route(
    app: FastAPI,
    store: FirestoreDurableStore,
    runtime_runner: Callable[[InvestigationEvent], Awaitable[None]] = run_managed_runtime,
) -> None:
    """Replace ADK's ephemeral Eventarc endpoint with Bastion's durable boundary."""
    app.router.routes[:] = [
        route for route in app.router.routes if getattr(route, "path", None) != ADK_EVENTARC_PATH
    ]

    @app.post(EVENTARC_PATH, response_model=TriggerResponse)
    async def durable_eventarc(request: Request) -> TriggerResponse:
        try:
            body = await request.json()
            if not isinstance(body, dict):
                raise ValueError("Eventarc body must be an object")
            event = decode_pubsub_event(cloud_event_envelope(body, dict(request.headers)))
        except (ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        # A duplicate completed or in-flight delivery is acknowledged. A previous failed
        # execution is reclaimed so Eventarc's retry policy can safely resume it.
        store.receive(event)
        lease_seconds = int(
            os.environ.get(
                "BASTION_INVESTIGATION_LEASE_SECONDS",
                str(DEFAULT_INVESTIGATION_LEASE_SECONDS),
            )
        )
        if not store.claim(event.event_id, lease_seconds=lease_seconds):
            if store.status(event.event_id) == "completed":
                return TriggerResponse(status="success")
            # A process can disappear after claiming but before recording failure.  Acking an
            # in-flight duplicate would consume Eventarc's only remaining retry and strand the
            # investigation forever. A 503 preserves the delivery until the lease expires.
            raise HTTPException(
                status_code=503,
                detail="investigation is active; retry after its durable lease expires",
            )

        try:
            await runtime_runner(event)
        except asyncio.CancelledError:
            # Cloud Run request cancellation must release durable state immediately rather than
            # strand it as running until lease expiry.
            store.finish(event.event_id, failed=True)
            record(
                "runtime.dispatch",
                outcome="failed",
                actor="durable_ingress",
                invocation_id=event.event_id,
                detail={"error_type": "CancelledError"},
            )
            raise
        except Exception as exc:
            store.finish(event.event_id, failed=True)
            record(
                "runtime.dispatch",
                outcome="failed",
                actor="durable_ingress",
                invocation_id=event.event_id,
                detail={"error_type": type(exc).__name__},
            )
            raise HTTPException(status_code=503, detail="managed runtime unavailable") from None
        store.finish(event.event_id)
        return TriggerResponse(status="success")


def install_peer_origin_auth(app: FastAPI, secret: str) -> None:
    """Require an origin credential on every peer route except liveness."""

    @app.middleware("http")
    async def peer_origin_auth(request: Request, call_next: Any) -> Any:
        if request.url.path == "/health":
            return await call_next(request)
        supplied = request.headers.get(PEER_SECRET_HEADER, "")
        if not supplied or not hmac.compare_digest(
            supplied.encode("utf-8"), secret.encode("utf-8")
        ):
            return JSONResponse(status_code=401, content={"detail": "unauthorized peer"})
        return await call_next(request)


def build_app() -> FastAPI:
    """Build the private A2A service and attach the durable route only to the Orchestrator."""
    agent_dir = os.environ["BASTION_AGENT_DIR"]
    if agent_dir == "orchestrator":
        # This service is durable admission, not another copy of the agent graph. All scheduled
        # work enters the managed Runtime so Agent Identity and Gateway remain unavoidable.
        app = FastAPI(title="Bastion durable investigation ingress", docs_url=None, redoc_url=None)
        install_durable_eventarc_route(
            app, FirestoreDurableStore(os.environ["GOOGLE_CLOUD_PROJECT"])
        )
        return app
    service_url = os.environ.get("BASTION_SERVICE_URL", "https://placeholder.invalid")
    if not service_url.startswith("https://"):
        raise RuntimeError("BASTION_SERVICE_URL must be an https Cloud Run origin")
    app = get_fast_api_app(
        agents_dir=stage_a2a_agent(agent_dir, service_url),
        session_service_uri=os.environ["BASTION_SESSION_SERVICE_URI"],
        memory_service_uri=os.environ["BASTION_MEMORY_SERVICE_URI"],
        use_local_storage=False,
        web=False,
        a2a=True,
        trace_to_cloud=True,
        otel_to_cloud=True,
        extra_plugins=["observability.audit.AuditPlugin"],
        trigger_sources=None,
    )
    secret = os.environ.get(PEER_SECRET_ENV)
    if not secret:
        raise RuntimeError(f"{PEER_SECRET_ENV} is required for a deployed A2A peer")
    install_peer_origin_auth(app, secret)
    return app


def main() -> None:
    uvicorn.run(build_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))  # noqa: S104


if __name__ == "__main__":
    main()
