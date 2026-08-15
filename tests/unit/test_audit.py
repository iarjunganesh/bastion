"""The audit plugin records every event, and leaks no identifiers doing it."""

from __future__ import annotations

import io
import json
from types import SimpleNamespace

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
