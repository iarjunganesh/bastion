"""Every supported runner registers the audit plugin."""

from __future__ import annotations

from agents.orchestrator.agent import root_agent
from observability.audit import AuditPlugin
from runtime.runner import build_runner


def test_runner_registers_one_audit_plugin():
    runner = build_runner(root_agent)
    assert len(runner.plugin_manager.plugins) == 1
    assert isinstance(runner.plugin_manager.plugins[0], AuditPlugin)


def test_runner_allows_an_explicit_application_name():
    assert build_runner(root_agent, app_name="bastion-test").app_name == "bastion-test"
