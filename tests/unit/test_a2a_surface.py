"""The deployed A2A surface must expose one service-specific card, never an assumed route."""

from __future__ import annotations

import json
from pathlib import Path

from infrastructure.agent_server import _a2a_card, stage_a2a_agent


def test_a2a_card_has_the_service_specific_jsonrpc_endpoint():
    card = _a2a_card("access_auditor", "https://bastion-access-auditor.example")
    assert card["supported_interfaces"] == [
        {
            "url": "https://bastion-access-auditor.example/a2a/access_auditor",
            "protocol_binding": "JSONRPC",
            "protocol_version": "1.0",
        }
    ]


def test_staged_agent_has_one_parseable_card(monkeypatch, tmp_path):
    source = tmp_path / "agents" / "access_auditor"
    source.mkdir(parents=True)
    (source / "agent.py").write_text("# fixture\n", encoding="utf-8")
    monkeypatch.setattr("infrastructure.agent_server.AGENTS_ROOT", str(tmp_path / "agents"))
    staged = Path(stage_a2a_agent("access_auditor", "https://service.example"))
    card = json.loads((staged / "access_auditor" / "agent.json").read_text(encoding="utf-8"))
    assert card["name"] == "Bastion Access Auditor"
