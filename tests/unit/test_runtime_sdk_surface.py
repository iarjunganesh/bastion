"""Operator scripts reach the installed Agent Platform SDK's real client surface.

v0.8.0 called `Client.agent_engines`, which its own pin, google-cloud-agentplatform 2.6.0, does
not provide. A hand-written client double hid the rename, and strict mypy sees the untyped
`Client` as `Any`. These tests build the real `Client`, bind each call against the real method
signature, and patch only that method, so a renamed or reshaped call fails here, not at deploy.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import subprocess
import sys
from collections.abc import Callable, Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from agentplatform import Client
from google.auth.credentials import AnonymousCredentials

ENVIRONMENT = {
    "GCP_PROJECT_ID": "bastion-test-project",
    "GCP_PROJECT_NUMBER": "123",
    "AGENT_RUNTIME_REGION": "europe-west4",
    "BASTION_RUNTIME_AGENT_ENGINE_ID": "engine-1",
    "BASTION_MEMORY_AGENT_ENGINE_ID": "memory-1",
    # `environment()` derives these override names from the agent names; with them set it never
    # needs `gcloud` to resolve a worker origin.
    "BASTION_ACCESS_AUDITOR_CARD_URL": "https://auditor.example.invalid/a2a/access_auditor/card.json",
    "BASTION_ESCALATION_AGENT_CARD_URL": "https://escalation.example.invalid/a2a/escalation/card.json",
}
ENGINE_NAME = "projects/123/locations/europe-west4/reasoningEngines/engine-1"
CONFIRMED = {
    "author": "escalation_gate",
    "actions": {"state_delta": {"escalation_confirmed": True}},
}


@pytest.fixture
def load(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[[str], ModuleType]]:
    """Import an operator module fresh under test configuration, and forget it afterwards.

    Every subprocess is refused: these scripts shell out to `gcloud`, and a unit test must never
    reach a live project, even read-only.
    """
    for key, value in ENVIRONMENT.items():
        monkeypatch.setenv(key, value)

    def refuse(*args: Any, **kwargs: Any) -> None:
        raise AssertionError(f"unit test attempted a subprocess: {args[:1]}")

    monkeypatch.setattr(subprocess, "run", refuse)
    loaded: list[str] = []

    def _load(name: str) -> ModuleType:
        sys.modules.pop(name, None)
        loaded.append(name)
        return importlib.import_module(name)

    yield _load
    for name in loaded:
        sys.modules.pop(name, None)


class _Recorder:
    """Patch real `runtimes` methods after proving each call binds to the real signature."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, engine: Any) -> None:
        self.client = Client(
            project=ENVIRONMENT["GCP_PROJECT_ID"],
            location=ENVIRONMENT["AGENT_RUNTIME_REGION"],
            credentials=AnonymousCredentials(),
        )
        self.calls: list[tuple[str, dict[str, Any]]] = []
        runtimes = type(self.client.runtimes)
        for method in ("get", "update", "create"):
            real = getattr(runtimes, method)  # AttributeError here is the regression being caught

            def fake(self_: Any, *args: Any, _real: Any = real, _name: str = method, **kwargs: Any):
                inspect.signature(_real).bind(self_, *args, **kwargs)
                self.calls.append((_name, kwargs))
                return engine

            monkeypatch.setattr(runtimes, method, fake)

    def factory(self, *, project: str, location: str) -> Client:
        self.calls.append(("client", {"project": project, "location": location}))
        return self.client


def _resource_engine() -> SimpleNamespace:
    resource = SimpleNamespace(model_dump=lambda **_: {"name": ENGINE_NAME})
    return SimpleNamespace(api_resource=resource)


def test_configure_reads_the_runtime_resource_through_runtimes_get(load, monkeypatch):
    configure = load("infrastructure.configure_agent_runtime")
    recorder = _Recorder(monkeypatch, _resource_engine())
    monkeypatch.setattr(configure, "Client", recorder.factory)

    assert configure.runtime_resource().model_dump() == {"name": ENGINE_NAME}
    assert recorder.calls[-1] == ("get", {"name": ENGINE_NAME})


@pytest.mark.parametrize("existing", [True, False], ids=["update", "create"])
def test_deploy_uses_runtimes_update_or_create_with_the_reviewed_config(
    load, monkeypatch, existing
):
    deploy = load("infrastructure.deploy_agent_runtime")
    recorder = _Recorder(monkeypatch, _resource_engine())
    monkeypatch.setattr(deploy, "Client", recorder.factory)
    monkeypatch.setattr(deploy, "ensure_runtime_secret_access", lambda: None)
    monkeypatch.setattr(deploy, "ensure_runtime_model_armor_access", lambda: None)
    monkeypatch.chdir(deploy.ROOT)
    if not existing:
        monkeypatch.delenv("BASTION_RUNTIME_AGENT_ENGINE_ID")

    assert deploy.deploy() == {"name": ENGINE_NAME}

    method, kwargs = recorder.calls[-1]
    assert method == ("update" if existing else "create")
    assert ("name" in kwargs) is existing
    config = kwargs["config"]
    assert config["entrypoint_module"] == "agents.orchestrator.runtime"
    assert config["requirements_file"] == "requirements-runtime.txt"
    environment = config["env_vars"]
    assert environment["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"
    assert environment["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "NO_CONTENT"
    # Declared so the SDK's default-on addition is visible in source rather than implicit.
    assert environment["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] == "unspecified"


class _StreamingEngine:
    def __init__(self, events: list[Any]) -> None:
        self.events = events

    async def async_create_session(self, *, user_id: str) -> dict[str, str]:
        return {"id": "session-1"}

    async def async_stream_query(self, **_kwargs: Any):
        for event in self.events:
            yield event


def _verify_runtime(load, monkeypatch, events: list[Any]) -> list[tuple[str, dict[str, Any]]]:
    smoke = load("infrastructure.smoke_test")
    recorder = _Recorder(monkeypatch, _StreamingEngine(events))
    monkeypatch.setattr(smoke, "Client", recorder.factory)
    asyncio.run(smoke.verify_runtime())
    return recorder.calls


def test_smoke_runtime_check_passes_only_on_the_completion_gate_confirmation(load, monkeypatch):
    calls = _verify_runtime(load, monkeypatch, [{"author": "orchestrator"}, CONFIRMED])
    assert ("get", {"name": ENGINE_NAME}) in calls


@pytest.mark.parametrize(
    ("events", "message"),
    [
        ([], "no streamed events"),
        ([{"author": "orchestrator"}, {"author": "escalation_gate"}], "without a confirmed"),
    ],
    ids=["empty", "unconfirmed"],
)
def test_smoke_runtime_check_refuses_a_stream_without_confirmation(
    load, monkeypatch, events, message
):
    """Evidence 19: a stream can end without the investigation having run at all."""
    with pytest.raises(RuntimeError, match=message):
        _verify_runtime(load, monkeypatch, events)
