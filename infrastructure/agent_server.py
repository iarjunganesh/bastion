"""Production ASGI entry point with a durable Eventarc investigation boundary.

ADK's generated Eventarc handler creates a fresh session for each request. Bastion replaces
that route for the Orchestrator: the CloudEvent id is admitted atomically to Firestore and the
stable ``context_id`` becomes the ADK session id. Consequently a retry cannot run a completed
investigation twice, and an investigation resumed weeks later sees the same managed session.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.cli.trigger_routes import TriggerResponse, TriggerRouter

from runtime.events import decode_pubsub_event
from runtime.firestore import FirestoreDurableStore

EVENTARC_PATH = "/apps/orchestrator/trigger/eventarc"
ADK_EVENTARC_PATH = "/apps/{app_name}/trigger/eventarc"
AGENTS_ROOT = "/app/agents"
A2A_PROTOCOL_BINDING = "JSONRPC"


def _a2a_card(agent_dir: str, service_url: str) -> dict[str, Any]:
    """Return the service-specific A2A card ADK discovers from ``agent.json``."""
    cards = {
        "access_auditor": {
            "name": "Bastion Access Auditor",
            "description": "Read-only live IAM audit and deterministic finding generation.",
            "skill": "audit_iam",
        },
        "escalation_agent": {
            "name": "Bastion Escalation Agent",
            "description": "Count-only, idempotent routing of approved human-review escalations.",
            "skill": "notify_department",
        },
        "orchestrator": {
            "name": "Bastion Orchestrator",
            "description": "Durable investigation admission, policy enforcement, and A2A dispatch.",
            "skill": "orchestrate_investigation",
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
                "tags": ["bastion", "internal"],
            }
        ],
        "default_input_modes": ["text/plain"],
        "default_output_modes": ["text/plain"],
        "capabilities": {"streaming": False, "push_notifications": False},
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


def _trigger_router(app: FastAPI) -> TriggerRouter:
    """Recover the ADK router so its vetted runner/session construction is retained."""
    for route in app.router.routes:
        if getattr(route, "path", None) != ADK_EVENTARC_PATH:
            continue
        endpoint = getattr(route, "endpoint", None)
        for cell in getattr(endpoint, "__closure__", ()) or ():
            candidate = cell.cell_contents
            if isinstance(candidate, TriggerRouter):
                return candidate
    raise RuntimeError("ADK Eventarc trigger route was not registered")


def install_durable_eventarc_route(app: FastAPI, store: FirestoreDurableStore) -> None:
    """Replace ADK's ephemeral Eventarc endpoint with Bastion's durable boundary."""
    router = _trigger_router(app)
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
        if not store.claim(event.event_id):
            return TriggerResponse(status="success")

        message = json.dumps(
            {
                "investigation_id": event.event_id,
                "context_id": event.context_id,
                "classification": event.classification,
            },
            sort_keys=True,
        )
        try:
            await router._run_agent(
                app_name="orchestrator",
                user_id="eventarc-investigation",
                message_text=message,
                session_id=event.context_id,
            )
        except Exception:
            store.finish(event.event_id, failed=True)
            raise
        store.finish(event.event_id)
        return TriggerResponse(status="success")


def build_app() -> FastAPI:
    """Build the private A2A service and attach the durable route only to the Orchestrator."""
    agent_dir = os.environ["BASTION_AGENT_DIR"]
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
        trigger_sources=["eventarc"] if agent_dir == "orchestrator" else None,
    )
    if agent_dir == "orchestrator":
        install_durable_eventarc_route(
            app, FirestoreDurableStore(os.environ["GOOGLE_CLOUD_PROJECT"])
        )
    return app


def main() -> None:
    uvicorn.run(build_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))  # noqa: S104


if __name__ == "__main__":
    main()
