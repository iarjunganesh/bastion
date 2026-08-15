"""The production Eventarc boundary admits each event before an ADK run begins."""

from __future__ import annotations

import base64
import json
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.adk.cli.trigger_routes import TriggerRouter

from infrastructure.agent_server import (
    ADK_EVENTARC_PATH,
    EVENTARC_PATH,
    install_durable_eventarc_route,
)


class FakeStore:
    def __init__(self) -> None:
        self.received: list[str] = []
        self.claimed: list[str] = []
        self.finished: list[tuple[str, bool]] = []
        self.claim_result = True

    def receive(self, event) -> bool:
        self.received.append(event.event_id)
        return True

    def claim(self, event_id: str) -> bool:
        self.claimed.append(event_id)
        return self.claim_result

    def finish(self, event_id: str, *, failed: bool = False) -> None:
        self.finished.append((event_id, failed))


def _app_with_adk_route(router: TriggerRouter) -> FastAPI:
    app = FastAPI()

    @app.post(ADK_EVENTARC_PATH)
    async def generated_adk_route() -> dict[str, str]:
        # Capturing the real router type models the ADK generated endpoint precisely.
        assert router is not None
        return {"status": "generated"}

    return app


def _event_body() -> dict[str, object]:
    payload = {"event_id": "00000000-0000-0000-0000-000000000001", "context_id": "week-42"}
    return {"message": {"data": base64.b64encode(json.dumps(payload).encode()).decode()}}


def test_durable_route_reuses_context_as_the_adk_session_id():
    router = TriggerRouter.__new__(TriggerRouter)
    router._run_agent = AsyncMock()  # type: ignore[method-assign]
    store = FakeStore()
    app = _app_with_adk_route(router)
    install_durable_eventarc_route(app, store)  # type: ignore[arg-type]

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.json() == {"status": "success"}
    assert store.received == ["00000000-0000-0000-0000-000000000001"]
    assert store.finished == [("00000000-0000-0000-0000-000000000001", False)]
    assert router._run_agent.await_args.kwargs["session_id"] == "week-42"


def test_duplicate_delivery_is_acknowledged_without_running_the_agent():
    router = TriggerRouter.__new__(TriggerRouter)
    router._run_agent = AsyncMock()  # type: ignore[method-assign]
    store = FakeStore()
    store.claim_result = False
    app = _app_with_adk_route(router)
    install_durable_eventarc_route(app, store)  # type: ignore[arg-type]

    response = TestClient(app).post(EVENTARC_PATH, json=_event_body(), headers={"ce-id": "123"})

    assert response.status_code == 200
    router._run_agent.assert_not_awaited()
