"""Managed Agent Runtime entrypoint is configured without constructing clients eagerly."""

from __future__ import annotations

from unittest.mock import MagicMock

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
