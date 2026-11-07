"""Managed Agent Runtime entrypoint is configured without constructing clients eagerly."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from agents.orchestrator import runtime


def test_memory_engine_id_is_required(monkeypatch):
    monkeypatch.delenv("BASTION_MEMORY_AGENT_ENGINE_ID", raising=False)
    with pytest.raises(RuntimeError, match="BASTION_MEMORY_AGENT_ENGINE_ID is required"):
        runtime._memory_engine_id()


def test_runtime_builders_use_the_regional_memory_engine(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bastion-test-project")
    monkeypatch.setenv("AGENT_RUNTIME_REGION", "europe-west4")
    monkeypatch.setenv("BASTION_MEMORY_AGENT_ENGINE_ID", "memory-engine-1")
    session = MagicMock()
    memory = MagicMock()
    session_factory = MagicMock(return_value=session)
    memory_factory = MagicMock(return_value=memory)
    monkeypatch.setattr(runtime, "VertexAiSessionService", session_factory)
    monkeypatch.setattr(runtime, "VertexAiMemoryBankService", memory_factory)

    assert runtime._session_service() is session
    assert runtime._memory_service() is memory
    expected = {
        "project": "bastion-test-project",
        "location": "europe-west4",
        "agent_engine_id": "memory-engine-1",
    }
    session_factory.assert_called_once_with(**expected)
    memory_factory.assert_called_once_with(**expected)


def test_runtime_registers_the_agent_and_audit_plugin():
    template = runtime.app._tmpl_attrs
    assert template["agent"] is runtime.root_agent
    assert template["plugins"][0].name == "bastion-audit"
    assert template["enable_tracing"] is True
    assert isinstance(runtime.app, runtime.GovernedAdkApp)


def _set_up_offline(app, monkeypatch) -> None:
    """Run the installed template's real `set_up()` with only its network edges replaced."""
    from vertexai.agent_engines.templates import adk as template

    monkeypatch.setattr(template, "_warn_if_telemetry_api_disabled", lambda: None)
    monkeypatch.setattr(template, "_default_instrumentor_builder", lambda *a, **k: None)
    monkeypatch.setattr(runtime, "VertexAiSessionService", MagicMock())
    monkeypatch.setattr(runtime, "VertexAiMemoryBankService", MagicMock())
    app.set_up()


def test_runtime_tracing_keeps_message_content_out_of_spans(monkeypatch):
    """The stock template turns span content on with `enable_tracing=True`; ours turns it off.

    The deployment sets `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false`, but the template's
    `set_up()` overwrote it with "true" because `enable_tracing=True` is its legacy content
    opt-in. ADK reads the variable whenever it traces a model or tool call, so the override was
    effective. Tracing itself must stay on (evidence 13 and 19 rely on sampled traces).
    """
    from vertexai.agent_engines import AdkApp

    environment = {
        "GOOGLE_CLOUD_PROJECT": "bastion-test-project",
        "AGENT_RUNTIME_REGION": "europe-west4",
        "BASTION_MEMORY_AGENT_ENGINE_ID": "memory-engine-1",
        "ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS": "false",
    }
    with patch.dict(os.environ, environment):
        stock = AdkApp(agent=runtime.root_agent, enable_tracing=True)
        _set_up_offline(stock, monkeypatch)
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "true"

        governed = runtime.app.clone()
        assert isinstance(governed, runtime.GovernedAdkApp)
        _set_up_offline(governed, monkeypatch)
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"
        assert governed._tracing_enabled() is True
