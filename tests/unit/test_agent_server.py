"""The production Eventarc boundary admits each event before an ADK run begins."""

from __future__ import annotations

import asyncio
import base64
import json
from concurrent.futures import CancelledError
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure import agent_server
from infrastructure.agent_server import EVENTARC_PATH, install_durable_eventarc_route
from runtime.durable import InvestigationEvent


class FakeStore:
    def __init__(self) -> None:
        self.received: list[str] = []
        self.claimed: list[str] = []
        self.finished: list[tuple[str, bool]] = []
        self.claim_result = True
        self.current_status = "received"

    def receive(self, event) -> bool:
        self.received.append(event.event_id)
        return True

    def claim(self, event_id: str, *, lease_seconds: int) -> bool:
        assert lease_seconds > 300
        self.claimed.append(event_id)
        return self.claim_result

    def status(self, event_id: str) -> str | None:
        assert event_id
        return self.current_status

    def finish(self, event_id: str, *, failed: bool = False) -> None:
        self.finished.append((event_id, failed))


def _app_with_adk_route() -> FastAPI:
    return FastAPI()


def _event_body() -> dict[str, object]:
    payload = {
        "event_id": "00000000-0000-0000-0000-000000000001",
        "context_id": "week-42",
        "schema_version": 1,
        "classification": "internal",
        "mock_data": False,
    }
    return {"message": {"data": base64.b64encode(json.dumps(payload).encode()).decode()}}


def test_durable_route_dispatches_the_same_event_to_managed_runtime():
    store = FakeStore()
    runtime_runner = AsyncMock()
    app = _app_with_adk_route()
    install_durable_eventarc_route(  # type: ignore[arg-type]
        app, store, runtime_runner=runtime_runner
    )

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.json() == {"status": "success"}
    assert store.received == ["00000000-0000-0000-0000-000000000001"]
    assert store.finished == [("00000000-0000-0000-0000-000000000001", False)]
    dispatched = runtime_runner.await_args.args[0]
    assert dispatched.context_id == "week-42"


def test_duplicate_delivery_is_acknowledged_without_running_the_agent():
    store = FakeStore()
    store.claim_result = False
    store.current_status = "completed"
    runtime_runner = AsyncMock()
    app = _app_with_adk_route()
    install_durable_eventarc_route(  # type: ignore[arg-type]
        app, store, runtime_runner=runtime_runner
    )

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.status_code == 200
    runtime_runner.assert_not_awaited()


def test_failed_runtime_releases_the_event_for_retry():
    store = FakeStore()
    runtime_runner = AsyncMock(side_effect=RuntimeError("dependency unavailable"))
    app = _app_with_adk_route()
    install_durable_eventarc_route(  # type: ignore[arg-type]
        app, store, runtime_runner=runtime_runner
    )

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.status_code == 503
    assert response.json() == {"detail": "managed runtime unavailable"}
    assert store.finished == [("00000000-0000-0000-0000-000000000001", True)]


def test_cancelled_runtime_releases_the_event_for_retry():
    store = FakeStore()
    runtime_runner = AsyncMock(side_effect=asyncio.CancelledError())
    app = _app_with_adk_route()
    install_durable_eventarc_route(  # type: ignore[arg-type]
        app, store, runtime_runner=runtime_runner
    )

    with pytest.raises(CancelledError):
        TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert store.finished == [("00000000-0000-0000-0000-000000000001", True)]


def test_inflight_delivery_is_retried_until_a_stale_lease_can_be_reclaimed():
    store = FakeStore()
    store.claim_result = False
    store.current_status = "running"
    runtime_runner = AsyncMock()
    app = _app_with_adk_route()
    install_durable_eventarc_route(  # type: ignore[arg-type]
        app, store, runtime_runner=runtime_runner
    )

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.status_code == 503
    runtime_runner.assert_not_awaited()


def test_managed_runtime_keeps_client_for_async_session_and_stream(monkeypatch):
    calls: list[tuple[str, object]] = []

    class FakeEngine:
        async def async_create_session(self, *, user_id):
            calls.append(("session", user_id))
            return {"id": "session-1"}

        async def async_stream_query(self, **kwargs):
            calls.append(("stream", kwargs))
            yield {"event": "complete"}

    class FakeAgentEngines:
        def get(self, *, name):
            calls.append(("get", name))
            return FakeEngine()

    class FakeClient:
        def __init__(self, *, project, location):
            calls.append(("client", (project, location)))
            self.agent_engines = FakeAgentEngines()

    monkeypatch.setattr(agent_server, "Client", FakeClient)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bastion-test-project")
    monkeypatch.setenv("GCP_PROJECT_NUMBER", "123")
    monkeypatch.setenv("AGENT_RUNTIME_REGION", "europe-west4")
    monkeypatch.setenv("BASTION_RUNTIME_AGENT_ENGINE_ID", "runtime-1")
    event = InvestigationEvent(
        event_id="00000000-0000-0000-0000-000000000001", context_id="week-42"
    )

    asyncio.run(agent_server.run_managed_runtime(event))

    assert calls[0] == ("client", ("bastion-test-project", "europe-west4"))
    assert calls[1] == (
        "get",
        "projects/123/locations/europe-west4/reasoningEngines/runtime-1",
    )
    assert calls[2] == ("session", "week-42")
    assert calls[3][0] == "stream"


def test_the_runtime_dispatch_message_is_data_not_an_instruction(monkeypatch):
    """Prose addressed to an agent is indistinguishable from a prompt injection.

    The dispatcher once sent "Run the scheduled governed IAM investigation. Use only registered
    agents and correlate the result to opaque investigation <id>." Model Armor scored that at
    HIGH confidence -- the same as a real attack -- and since screening fails closed it refused
    every investigation the fleet ran. Neither raising nor lowering the threshold separated the
    two, because what differs is provenance and a content classifier cannot see provenance.

    So the message must stay structured data. This asserts the shape rather than the wording:
    valid JSON carrying the correlation id, with no imperative prose for a classifier to read.
    """
    import json as _json

    captured: dict[str, object] = {}

    class _Engine:
        async def async_create_session(self, user_id):
            return {"id": "session-1"}

        async def async_stream_query(self, *, user_id, session_id, message, run_config=None):
            captured["message"] = message
            captured["run_config"] = run_config
            return
            yield  # pragma: no cover - generator protocol only

    class _Client:
        def __init__(self, **_kwargs):
            self.agent_engines = SimpleNamespace(get=lambda name: _Engine())

    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "p")
    monkeypatch.setenv("GCP_PROJECT_NUMBER", "1234567890")
    monkeypatch.setenv("BASTION_RUNTIME_AGENT_ENGINE_ID", "engine-1")
    monkeypatch.setattr(agent_server, "Client", _Client)

    event_id = "3f2504e0-4f89-11d3-9a0c-0305e82c3301"
    event = InvestigationEvent(event_id=event_id, context_id="8e4767d4-8801-44ea-a050-26fb4bb1867a")
    asyncio.run(agent_server.run_managed_runtime(event))

    message = captured["message"]
    assert isinstance(message, str)
    payload = _json.loads(message)  # prose would raise here
    assert payload["investigation_id"] == event_id
    lowered = message.lower()
    for imperative in ("run the", "use only", "you must", "please ", "ignore "):
        assert imperative not in lowered, f"dispatch message reads as an instruction: {imperative}"

    # The id the audit trail correlates on travels as run-config metadata, not as message
    # content. The message copy is for the model; this copy is the one nothing can retype.
    run_config = captured["run_config"]
    assert isinstance(run_config, dict)
    metadata = run_config["custom_metadata"]
    assert metadata[agent_server.INVESTIGATION_METADATA_KEY] == event_id


def test_an_empty_lease_variable_falls_back_rather_than_crashing(monkeypatch):
    """`os.environ.get(key, default)` returns "" for a declared-but-empty variable, not the
    default, so `int("")` took the service down on its first delivery. A deployment that
    declares the variable without a value is a realistic mistake, and a placeholder-shaped
    `.env` is exactly that shape."""
    monkeypatch.setenv("BASTION_INVESTIGATION_LEASE_SECONDS", "")
    assert agent_server._lease_seconds() == agent_server.DEFAULT_INVESTIGATION_LEASE_SECONDS


def test_a_configured_lease_is_honoured(monkeypatch):
    monkeypatch.setenv("BASTION_INVESTIGATION_LEASE_SECONDS", "900")
    assert agent_server._lease_seconds() == 900


def test_an_absent_lease_variable_uses_the_default(monkeypatch):
    monkeypatch.delenv("BASTION_INVESTIGATION_LEASE_SECONDS", raising=False)
    assert agent_server._lease_seconds() == agent_server.DEFAULT_INVESTIGATION_LEASE_SECONDS
