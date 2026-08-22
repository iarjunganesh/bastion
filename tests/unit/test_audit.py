"""The audit plugin records every event, and leaks no identifiers doing it."""

from __future__ import annotations

import io
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from observability import audit


@pytest.fixture
def emitted():
    """Read the audit records emitted during one test.

    Capture is an explicit in-memory handler rather than `capsys`, because
    `logging.getLogger(name)` is a process-global singleton whose handler binds `sys.stdout`
    *once*. Under `capsys` that binding belongs to whichever test built the logger first, so
    records land on a stale stream and the assertions read as "nothing was emitted" while the
    code under test is working correctly.

    Pre-attaching this handler also exercises the real guard in `_logger()`: it adds its own
    stdout handler only when none is present, so a compliance record is never duplicated.
    """
    import logging

    logger = logging.getLogger(audit.AUDIT_LOGGER_NAME)
    audit._logger.cache_clear()
    logger.handlers.clear()

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    def _read() -> list[dict]:
        handler.flush()
        return [json.loads(line) for line in stream.getvalue().splitlines() if line.strip()]

    yield _read

    logger.handlers.clear()
    audit._logger.cache_clear()


def test_a_record_is_one_json_object_per_line(emitted):
    audit.record("gateway.route", outcome="admitted", actor="orchestrator", invocation_id="inv-1")
    (record,) = emitted()
    assert record["event"] == "gateway.route"
    assert record["outcome"] == "admitted"
    assert record["invocation_id"] == "inv-1"


def test_the_audit_logger_does_not_propagate():
    """An application handler must not be able to reformat or filter a compliance record."""
    assert audit._logger().propagate is False


@pytest.mark.asyncio
async def test_tool_calls_record_argument_names_never_values(emitted):
    """A tool argument here can carry a principal identifier; an audit log is retained forever."""
    plugin = audit.AuditPlugin()
    await plugin.after_tool_callback(
        tool=SimpleNamespace(name="audit_iam_policy"),
        tool_args={"member": "user:a.lee@example.com", "role": "roles/owner"},
        tool_context=SimpleNamespace(invocation_id="inv-2"),
        result={"count": 1},
    )
    (record,) = emitted()
    assert record["detail"]["args"] == ["member", "role"]
    assert "a.lee@example.com" not in json.dumps(record)


@pytest.mark.asyncio
async def test_tool_errors_record_the_type_not_the_message(emitted):
    """A Google API error message routinely quotes the resource that was denied."""
    plugin = audit.AuditPlugin()
    await plugin.on_tool_error_callback(
        tool=SimpleNamespace(name="audit_iam_policy"),
        tool_args={},
        tool_context=SimpleNamespace(invocation_id="inv-3"),
        error=PermissionError("denied on projects/secret-project/iam a.lee@example.com"),
    )
    (record,) = emitted()
    assert record["detail"] == {"error": "PermissionError"}
    assert "secret-project" not in json.dumps(record)


@pytest.mark.asyncio
async def test_model_requests_are_recorded_and_never_blocked(emitted):
    plugin = audit.AuditPlugin()
    result = await plugin.before_model_callback(
        callback_context=SimpleNamespace(invocation_id="inv-4", agent_name="access_auditor"),
        llm_request=SimpleNamespace(model="gemini-3.5-flash"),
    )
    assert result is None, "the audit plugin observes; screening is Model Armor's job"
    (record,) = emitted()
    assert record["actor"] == "access_auditor"


@pytest.mark.asyncio
async def test_run_and_agent_lifecycle_are_correlated(emitted):
    plugin = audit.AuditPlugin()
    context = SimpleNamespace(invocation_id="inv-life", agent=SimpleNamespace(name="orchestrator"))
    callback = SimpleNamespace(invocation_id="inv-life")
    agent = SimpleNamespace(name="access_auditor")

    assert await plugin.before_run_callback(invocation_context=context) is None
    assert await plugin.before_agent_callback(agent=agent, callback_context=callback) is None
    assert await plugin.after_agent_callback(agent=agent, callback_context=callback) is None
    assert await plugin.after_run_callback(invocation_context=context) is None

    records = emitted()
    assert [(item["event"], item["outcome"]) for item in records] == [
        ("investigation.run", "started"),
        ("agent.run", "started"),
        ("agent.run", "completed"),
        ("investigation.run", "completed"),
    ]
    assert {item["invocation_id"] for item in records} == {"inv-life"}


@pytest.mark.asyncio
async def test_model_completion_and_failure_are_payload_free(emitted):
    plugin = audit.AuditPlugin()
    context = SimpleNamespace(invocation_id="inv-model", agent_name="policy")
    request = SimpleNamespace(model="gemini-3.5-flash")

    assert (
        await plugin.after_model_callback(
            callback_context=context, llm_response=SimpleNamespace(content="secret")
        )
        is None
    )
    assert (
        await plugin.on_model_error_callback(
            callback_context=context,
            llm_request=request,
            error=RuntimeError("principal user:a@example.com"),
        )
        is None
    )

    records = emitted()
    assert records[0]["outcome"] == "completed"
    assert records[1]["detail"] == {"error": "RuntimeError", "model": "gemini-3.5-flash"}
    assert "a@example.com" not in json.dumps(records)


@pytest.mark.asyncio
async def test_tool_start_records_names_not_values(emitted):
    plugin = audit.AuditPlugin()
    assert (
        await plugin.before_tool_callback(
            tool=SimpleNamespace(name="audit_iam_policy"),
            tool_args={"member": "user:a@example.com"},
            tool_context=SimpleNamespace(invocation_id="inv-tool"),
        )
        is None
    )
    (record,) = emitted()
    assert record["outcome"] == "started"
    assert record["detail"] == {"args": ["member"]}
    assert "a@example.com" not in json.dumps(record)


def test_a_missing_invocation_id_is_recorded_not_raised():
    """Losing the event is worse than recording 'unknown'."""
    assert audit._invocation(SimpleNamespace()) == "unknown"


def test_the_logger_builds_its_own_stdout_handler_when_none_exists():
    """The production path: no handler pre-attached, so `_logger()` installs one.

    The `emitted` fixture deliberately pre-attaches a handler, which exercises the *guard* but
    never the construction. Both branches matter — a compliance record that is written twice is
    as wrong as one never written.
    """
    import logging

    audit._logger.cache_clear()
    logging.getLogger(audit.AUDIT_LOGGER_NAME).handlers.clear()
    try:
        logger = audit._logger()
        assert len(logger.handlers) == 1
        assert logger.level == logging.INFO
        assert audit._logger() is logger, "cached, so the handler is never added twice"
    finally:
        logging.getLogger(audit.AUDIT_LOGGER_NAME).handlers.clear()
        audit._logger.cache_clear()


# --- Correlating one investigation across the A2A boundary -------------------------------
#
# `invocation_id` is minted per agent run, so one investigation produced three of them: the
# Runtime graph and each worker. These pin the field that does survive the hop.

UUID_ONE = "b3a214ba-6715-4ca6-9090-bb584fdd6768"


def _ctx(metadata):
    return SimpleNamespace(run_config=SimpleNamespace(custom_metadata=metadata))


def test_the_investigation_id_is_read_from_run_config():
    assert audit._investigation(_ctx({audit.INVESTIGATION_METADATA_KEY: UUID_ONE})) == UUID_ONE


def test_the_investigation_id_survives_the_a2a_hop():
    """ADK files inbound A2A request metadata one level down, so a worker sees it nested."""
    nested = {audit.A2A_METADATA_KEY: {audit.INVESTIGATION_METADATA_KEY: UUID_ONE}}
    assert audit._investigation(_ctx(nested)) == UUID_ONE


@pytest.mark.parametrize(
    "metadata",
    [None, {}, {audit.A2A_METADATA_KEY: "not-a-dict"}, {audit.A2A_METADATA_KEY: {}}],
    ids=["absent", "empty", "nested-not-a-dict", "nested-empty"],
)
def test_a_missing_investigation_id_is_a_sentinel_not_an_error(metadata):
    """An audit record that fails to write is worse than one carrying "unknown"."""
    assert audit._investigation(_ctx(metadata)) == audit.UNKNOWN


def test_a_context_without_a_run_config_is_tolerated():
    assert audit._investigation(SimpleNamespace()) == audit.UNKNOWN


@pytest.mark.parametrize(
    "value",
    ["", "ignore previous instructions", UUID_ONE[:-1], 12345, None, UUID_ONE + "x"],
    ids=["empty", "prose", "truncated", "int", "none", "suffixed"],
)
def test_only_a_uuid_is_accepted_as_a_correlation_id(value):
    """This value arrives over A2A from a peer and is retained for a year. A correlation field
    that accepts arbitrary text is a channel into the compliance log, so the shape is checked
    here as well as upstream."""
    assert audit.opaque_investigation_id(value) == audit.UNKNOWN


def test_a_record_carries_the_investigation_it_belongs_to():
    emitted = []
    with patch.object(audit, "_logger") as logger:
        logger.return_value.info = emitted.append
        audit.record(
            "investigation.run",
            outcome="started",
            actor="orchestrator",
            invocation_id="e-one-run-of-one-agent",
            investigation_id=UUID_ONE,
        )
    payload = json.loads(emitted[0])
    assert payload["investigation_id"] == UUID_ONE
    assert payload["invocation_id"] == "e-one-run-of-one-agent"


def test_the_orchestrator_forwards_the_investigation_id_to_a_worker():
    from agents.orchestrator import agent as orchestrator

    forwarded = orchestrator._forward_investigation(
        _ctx({audit.INVESTIGATION_METADATA_KEY: UUID_ONE}), object()
    )
    assert forwarded == {audit.INVESTIGATION_METADATA_KEY: UUID_ONE}


def test_forwarding_without_an_id_sends_an_empty_value_rather_than_failing():
    """A dispatch that lost its metadata must still reach the worker; the far side records
    `unknown` and the gap is visible in the trail instead of aborting the investigation."""
    from agents.orchestrator import agent as orchestrator

    assert orchestrator._forward_investigation(SimpleNamespace(), object()) == {
        audit.INVESTIGATION_METADATA_KEY: ""
    }
