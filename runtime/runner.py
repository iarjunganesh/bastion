"""The only supported local ADK runner construction path.

Keeping runner construction here makes audit registration non-optional. Deployment replaces the
in-memory services with managed equivalents through the same factory rather than constructing a
second, unaudited runner.
"""

from __future__ import annotations

from google.adk.agents.base_agent import BaseAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from observability.audit import AuditPlugin


def build_runner(agent: BaseAgent, *, app_name: str = "bastion") -> Runner:
    """Create an audited runner with an explicit session service."""
    return Runner(
        app=App(name=app_name, root_agent=agent, plugins=[AuditPlugin()]),
        session_service=InMemorySessionService(),
    )
