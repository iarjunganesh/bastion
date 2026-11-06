"""Agent Runtime entry point for the governed Bastion Orchestrator."""

from __future__ import annotations

import os

# Agent Runtime injects its regional GOOGLE_CLOUD_LOCATION and reserves that environment
# variable. Gemini 3.5 is global-only, so switch the model client location in process before
# importing the agent graph. The runtime's own region remains explicit and separate below.
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("BASTION_MODEL_LOCATION", "global")

from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService
from vertexai.agent_engines import AdkApp

from agents.orchestrator.agent import root_agent
from observability.audit import AuditPlugin


def _memory_engine_id() -> str:
    try:
        return os.environ["BASTION_MEMORY_AGENT_ENGINE_ID"]
    except KeyError:
        raise RuntimeError(
            "BASTION_MEMORY_AGENT_ENGINE_ID is required for durable Agent Runtime context"
        ) from None


def _session_service() -> VertexAiSessionService:
    return VertexAiSessionService(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["AGENT_RUNTIME_REGION"],
        agent_engine_id=_memory_engine_id(),
    )


def _memory_service() -> VertexAiMemoryBankService:
    return VertexAiMemoryBankService(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ["AGENT_RUNTIME_REGION"],
        agent_engine_id=_memory_engine_id(),
    )


# Written, never read: restored after the template overwrites it.
SPAN_CONTENT_SETTING = "ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"


class GovernedAdkApp(AdkApp):
    """`AdkApp` that keeps trace export but keeps message content out of ADK's spans.

    The managed template treats `enable_tracing=True` as its legacy opt-in for span content, and
    its `set_up()` overwrites `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS` with "true" -- replacing the
    "false" that `infrastructure/deploy_agent_runtime.py` deploys. ADK reads the variable each time
    it traces a model or tool call, which would put requests, responses and tool values on spans.
    This graph makes no model or tool call in the Runtime today, so no content reached a span;
    restoring the deployed value keeps that true if a step ever does. Tracing stays enabled.
    """

    def set_up(self) -> None:
        super().set_up()  # type: ignore[no-untyped-call]  # template method is untyped
        os.environ[SPAN_CONTENT_SETTING] = "false"


# Builders defer ADC and client construction until the managed process starts. AuditPlugin is
# registered once at the Runner seam, covering every agent/model/tool event in the sequence.
app = GovernedAdkApp(
    agent=root_agent,
    plugins=[AuditPlugin()],
    enable_tracing=True,
    session_service_builder=_session_service,
    memory_service_builder=_memory_service,
)
