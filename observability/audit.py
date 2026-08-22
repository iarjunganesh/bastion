"""Audit trail — Telemetry pillar, the half that is not the trace.

The brief asks for *"OpenTelemetry-compliant audit logs **and** end-to-end reasoning chain
traces"*. Two artifacts, joined by "and" ([ADR-006](../docs/adr/006-pillar-coverage.md)). The
traces are ADK's own OpenTelemetry spans, exported by `adk deploy cloud_run --trace_to_cloud`.
This file is the other half.

A trace is sampled and expires; an audit record for a compliance product is neither, so this
never derives from the trace and never shares its sink. Records are emitted as structured JSON
on stdout, which Cloud Logging ingests as `jsonPayload` — no client library, so the audit path
has no failure mode of its own and behaves identically in a test, a local run, and Cloud Run.

**It is a `BasePlugin`, which is the whole point.** Registered once on the `Runner`, it records
every agent, model and tool event across the fleet without a call site in any agent. The
previous version of this module was called explicitly from four places, which meant a new
call path was silently unaudited until someone remembered — and an agent that audits itself is
an agent that can decline to.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

AUDIT_LOGGER_NAME = "bastion.audit"

UNKNOWN = "unknown"

# The durable investigation id travels as ADK run-config metadata under this key, which is the
# one channel that survives both the managed-Runtime dispatch and the A2A hop without ever
# becoming model-visible content.
INVESTIGATION_METADATA_KEY = "bastion_investigation"

# ADK files inbound A2A request metadata one level down, under this literal.
A2A_METADATA_KEY = "a2a_metadata"

# The dispatcher only ever sends `InvestigationEvent.event_id`, which is UUID-validated before an
# investigation is admitted. Re-checking the shape here is not redundant: this value arrives over
# A2A from a peer, and audit records are retained for a year. Anything that is not a UUID is
# recorded as unknown rather than written through, so a peer cannot use the correlation field as
# a channel for arbitrary text into the compliance log.
_UUID = re.compile(
    r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\Z"
)


@lru_cache(maxsize=1)
def _logger() -> logging.Logger:
    """A logger that writes one JSON object per line to stdout, and nothing else.

    `propagate = False` so an application-level handler cannot reformat, duplicate, or filter
    an audit record. The compliance artifact must not depend on logging configuration set
    somewhere else.
    """
    logger = logging.getLogger(AUDIT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """One decision by one actor, in the shape Cloud Logging indexes.

    `invocation_id` groups the records of a single *agent run*, and only that. It is minted by
    ADK per run, so an investigation that crosses the A2A boundary produces several: one for
    the Runtime graph and one for each worker it calls. Tool records therefore sit under the
    worker's id rather than the orchestrator's.

    **Nothing in this record correlates an investigation end to end.** Reassembling one from
    the trail needs the durable `context_id`, which does not yet reach here; until it does,
    the Observability claim is per-agent, not per-investigation.
    """

    event: str
    outcome: str
    actor: str
    invocation_id: str
    investigation_id: str = UNKNOWN
    detail: dict[str, Any] = field(default_factory=dict)

    def emit(self) -> None:
        _logger().info(json.dumps(asdict(self), default=str, sort_keys=True))


def record(
    event: str,
    *,
    outcome: str,
    actor: str,
    invocation_id: str,
    investigation_id: str = UNKNOWN,
    detail: dict[str, Any] | None = None,
) -> None:
    AuditRecord(event, outcome, actor, invocation_id, investigation_id, detail or {}).emit()


def opaque_investigation_id(value: object) -> str:
    """The investigation id if it is a UUID, else the sentinel. Never raises."""
    return value if isinstance(value, str) and _UUID.match(value) else UNKNOWN


def _investigation(context: object) -> str:
    """The investigation this record belongs to, across every hop -- or a sentinel.

    `invocation_id` groups one agent run; it does not survive an A2A hop, so it cannot assemble
    an investigation. This reads the durable id that the dispatcher seeds into the run config
    and the Orchestrator forwards to each worker.

    Like `_invocation`, this never raises: an audit record that fails to write because a context
    attribute moved between ADK releases is worse than one carrying "unknown".
    """
    metadata = getattr(getattr(context, "run_config", None), "custom_metadata", None)
    if not isinstance(metadata, dict):
        return UNKNOWN
    direct = opaque_investigation_id(metadata.get(INVESTIGATION_METADATA_KEY))
    if direct != UNKNOWN:
        return direct
    nested = metadata.get(A2A_METADATA_KEY)
    if isinstance(nested, dict):
        return opaque_investigation_id(nested.get(INVESTIGATION_METADATA_KEY))
    return UNKNOWN


def _invocation(context: object) -> str:
    """The invocation id, or a sentinel — never an exception.

    An audit record that fails to write because a context attribute moved between ADK releases
    is worse than one carrying "unknown": the first loses the event, the second keeps it.
    """
    return str(getattr(context, "invocation_id", None) or UNKNOWN)


class AuditPlugin(BasePlugin):
    """Emits one audit record per agent, model, and tool event across the whole fleet."""

    def __init__(self, name: str = "bastion-audit") -> None:
        super().__init__(name=name)

    async def before_run_callback(self, *, invocation_context: InvocationContext) -> None:
        record(
            "investigation.run",
            outcome="started",
            actor=getattr(getattr(invocation_context, "agent", None), "name", "unknown"),
            invocation_id=_invocation(invocation_context),
            investigation_id=_investigation(invocation_context),
        )

    async def after_run_callback(self, *, invocation_context: InvocationContext) -> None:
        record(
            "investigation.run",
            outcome="completed",
            actor=getattr(getattr(invocation_context, "agent", None), "name", "unknown"),
            invocation_id=_invocation(invocation_context),
            investigation_id=_investigation(invocation_context),
        )

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        record(
            "agent.run",
            outcome="started",
            actor=agent.name,
            invocation_id=_invocation(callback_context),
            investigation_id=_investigation(callback_context),
        )

    async def after_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        record(
            "agent.run",
            outcome="completed",
            actor=agent.name,
            invocation_id=_invocation(callback_context),
            investigation_id=_investigation(callback_context),
        )

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> LlmResponse | None:
        record(
            "model.request",
            outcome="submitted",
            actor=getattr(callback_context, "agent_name", "unknown"),
            invocation_id=_invocation(callback_context),
            investigation_id=_investigation(callback_context),
            detail={"model": getattr(llm_request, "model", None)},
        )
        return None

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> None:
        del llm_response
        record(
            "model.request",
            outcome="completed",
            actor=getattr(callback_context, "agent_name", "unknown"),
            invocation_id=_invocation(callback_context),
            investigation_id=_investigation(callback_context),
        )

    async def on_model_error_callback(
        self,
        *,
        callback_context: CallbackContext,
        llm_request: LlmRequest,
        error: Exception,
    ) -> None:
        record(
            "model.request",
            outcome="failed",
            actor=getattr(callback_context, "agent_name", "unknown"),
            invocation_id=_invocation(callback_context),
            investigation_id=_investigation(callback_context),
            detail={
                "model": getattr(llm_request, "model", None),
                "error": type(error).__name__,
            },
        )

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
    ) -> None:
        record(
            "tool.call",
            outcome="started",
            actor=tool.name,
            invocation_id=_invocation(tool_context),
            investigation_id=_investigation(tool_context),
            detail={"args": sorted(tool_args)},
        )

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        # Argument *names* are recorded, never their values. A tool argument in this system can
        # carry a principal identifier, and an audit log is the one artifact guaranteed to be
        # retained and read by someone who was not there.
        record(
            "tool.call",
            outcome="completed",
            actor=tool.name,
            invocation_id=_invocation(tool_context),
            investigation_id=_investigation(tool_context),
            detail={"args": sorted(tool_args)},
        )
        return None

    async def on_tool_error_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict[str, Any],
        tool_context: ToolContext,
        error: Exception,
    ) -> dict[str, Any] | None:
        # The exception *type*, not its message: a Google API error message routinely quotes the
        # resource that was denied, which is a principal identifier by another name. The type is
        # what an auditor needs; the message is what leaks.
        record(
            "tool.call",
            outcome="failed",
            actor=tool.name,
            invocation_id=_invocation(tool_context),
            investigation_id=_investigation(tool_context),
            detail={"error": type(error).__name__},
        )
        return None
