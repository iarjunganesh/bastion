"""A transient model rejection is retried briefly and audited; anything else still fails closed."""

from __future__ import annotations

import io
import json
import logging
import uuid

import pytest
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.models.google_llm import Gemini
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import errors as genai_errors
from google.genai import types

from agents import model_retry
from observability import audit
from runtime.runner import build_runner


@pytest.fixture
def emitted():
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


@pytest.fixture
def waits(monkeypatch):
    slept: list[float] = []

    async def _sleep(seconds: float) -> None:
        slept.append(seconds)

    monkeypatch.setattr(model_retry, "_sleep", _sleep)
    return slept


def _error(code: int) -> genai_errors.APIError:
    status = {429: "RESOURCE_EXHAUSTED", 400: "INVALID_ARGUMENT", 503: "UNAVAILABLE"}[code]
    body = {"error": {"code": code, "message": "m", "status": status}}
    cls = genai_errors.ClientError if code < 500 else genai_errors.ServerError
    return cls(code, body, None)


def _answer(text: str = "ok") -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


def _script(monkeypatch, outcomes: list, mutate: bool = False) -> list[LlmRequest]:
    """Replace ADK's call: each attempt raises or yields the next scripted outcome."""
    seen: list[LlmRequest] = []

    async def fake(self, llm_request, stream=False):
        seen.append(llm_request.model_copy(deep=True))
        if mutate:
            llm_request.contents.append(types.Content(role="user", parts=[types.Part(text="x")]))
        outcome = outcomes.pop(0)
        if isinstance(outcome, list):
            for item in outcome:
                if isinstance(item, Exception):
                    raise item
                yield item
            return
        if isinstance(outcome, Exception):
            raise outcome
        yield outcome

    monkeypatch.setattr(Gemini, "generate_content_async", fake)
    return seen


def _request() -> LlmRequest:
    return LlmRequest(
        model="gemini-3.5-flash",
        contents=[types.Content(role="user", parts=[types.Part(text="audit")])],
        config=types.GenerateContentConfig(),
    )


async def _collect(request: LlmRequest) -> list[LlmResponse]:
    model = model_retry.RetryingGemini(model="gemini-3.5-flash")
    return [response async for response in model.generate_content_async(request)]


@pytest.mark.asyncio
async def test_a_429_is_retried_and_the_retry_is_audited(monkeypatch, emitted, waits):
    _script(monkeypatch, [_error(429), _answer()])
    responses = await _collect(_request())
    assert [r.content.parts[0].text for r in responses] == ["ok"]
    (retry,) = emitted()
    assert (retry["event"], retry["outcome"]) == ("model.request", "retrying")
    assert retry["detail"]["attempt"] == 1 and retry["detail"]["status"] == 429
    assert retry["detail"]["delay_seconds"] == waits[0]


@pytest.mark.asyncio
async def test_every_retry_starts_from_the_request_as_handed_over(monkeypatch, waits):
    seen = _script(monkeypatch, [_error(503), _error(429), _answer()], mutate=True)
    await _collect(_request())
    assert len(seen) == 3
    assert all(s.contents == seen[0].contents for s in seen)
    assert len(seen[0].contents) == 1


@pytest.mark.asyncio
async def test_a_non_transient_error_is_raised_at_once(monkeypatch, emitted, waits):
    _script(monkeypatch, [_error(400), _answer()])
    with pytest.raises(genai_errors.ClientError) as raised:
        await _collect(_request())
    assert raised.value.code == 400
    assert emitted() == [] and waits == []


@pytest.mark.asyncio
async def test_exhausted_attempts_raise_the_original_error(monkeypatch, emitted, waits):
    _script(monkeypatch, [_error(429)] * model_retry.MAX_ATTEMPTS)
    with pytest.raises(genai_errors.ClientError) as raised:
        await _collect(_request())
    assert raised.value.code == 429
    records = emitted()
    assert [r["detail"]["attempt"] for r in records] == list(range(1, model_retry.MAX_ATTEMPTS))
    assert len(waits) == model_retry.MAX_ATTEMPTS - 1


@pytest.mark.asyncio
async def test_nothing_is_retried_after_a_response_was_yielded(monkeypatch, emitted, waits):
    _script(monkeypatch, [[_answer("partial"), _error(503)], _answer()])
    model = model_retry.RetryingGemini(model="gemini-3.5-flash")
    received = []
    with pytest.raises(genai_errors.ServerError):
        async for response in model.generate_content_async(_request()):
            received.append(response)
    assert len(received) == 1
    assert emitted() == [] and waits == []


def test_backoff_is_capped_exponential_with_bounded_jitter():
    for attempt in range(1, 8):
        ceiling = min(
            model_retry.MAX_DELAY_SECONDS, model_retry.INITIAL_DELAY_SECONDS * 2 ** (attempt - 1)
        )
        for _ in range(50):
            assert ceiling * 0.5 <= model_retry.backoff_seconds(attempt) <= ceiling
    worst = sum(
        min(model_retry.MAX_DELAY_SECONDS, model_retry.INITIAL_DELAY_SECONDS * 2 ** (n - 1))
        for n in range(1, model_retry.MAX_ATTEMPTS)
    )
    assert worst <= 30, "the retry budget must stay far inside the investigation lease"


def test_a_retry_outside_a_model_call_is_recorded_as_unknown(emitted):
    audit._MODEL_CALL.set(None)
    audit.record_model_retry(attempt=1, status=429, delay_seconds=1.0)
    (record,) = emitted()
    assert record["actor"] == record["invocation_id"] == record["investigation_id"] == "unknown"


def test_the_access_auditor_uses_the_retrying_model():
    from agents.access_auditor.agent import access_auditor

    assert isinstance(access_auditor.model, model_retry.RetryingGemini)


@pytest.mark.asyncio
async def test_through_the_audited_runner_a_retry_is_attributed_and_paired_once(
    monkeypatch, emitted, waits
):
    """End to end through ADK: the retry record carries the call's actor, invocation and
    investigation, and the agent-level `submitted`/`completed` pair is emitted once."""
    _script(monkeypatch, [_error(429), _answer("done")])
    agent = LlmAgent(name="probe", model=model_retry.RetryingGemini(model="gemini-3.5-flash"))
    runner = build_runner(agent)
    session = await runner.session_service.create_session(app_name="bastion", user_id="u")
    investigation = str(uuid.uuid4())
    events = [
        event
        async for event in runner.run_async(
            user_id="u",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text="go")]),
            run_config=RunConfig(custom_metadata={audit.INVESTIGATION_METADATA_KEY: investigation}),
        )
    ]
    assert any(e.content and e.content.parts and e.content.parts[0].text == "done" for e in events)
    model_records = [r for r in emitted() if r["event"] == "model.request"]
    assert [r["outcome"] for r in model_records] == ["submitted", "retrying", "completed"]
    retry = model_records[1]
    assert retry["actor"] == "probe"
    assert retry["investigation_id"] == investigation
    assert retry["invocation_id"] == model_records[0]["invocation_id"] != "unknown"


# --- the production callbacks across a retry -------------------------------------------------


def _counted(callback, calls: dict[str, int]):
    """Wrap a production callback so the test can count how often ADK invokes it."""

    def wrapper(*args, **kwargs):
        calls[callback.__name__] = calls.get(callback.__name__, 0) + 1
        return callback(*args, **kwargs)

    return wrapper


def _guarded_auditor(calls: dict[str, int]) -> LlmAgent:
    """An agent wired with the Access Auditor's own screening and fidelity callbacks."""
    from agents.access_auditor import agent as auditor
    from model_armor import guardrails

    return LlmAgent(
        name="access_auditor",
        model=model_retry.RetryingGemini(model="gemini-3.5-flash"),
        before_model_callback=_counted(guardrails.screen_before_model, calls),
        after_model_callback=[
            _counted(guardrails.screen_after_model, calls),
            _counted(auditor.validate_auditor_fidelity, calls),
        ],
    )


async def _run(agent: LlmAgent) -> list:
    runner = build_runner(agent)
    session = await runner.session_service.create_session(app_name="bastion", user_id="u")
    return [
        event
        async for event in runner.run_async(
            user_id="u",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text="audit the policy")]),
        )
    ]


def _texts(events: list) -> list[str]:
    return [
        part.text
        for event in events
        if event.content and event.content.parts
        for part in event.content.parts
        if part.text
    ]


@pytest.fixture
def armor(monkeypatch):
    """Model Armor configured, with the screening call stubbed and its verdicts recorded."""
    from model_armor import guardrails

    monkeypatch.setenv("GCP_PROJECT_ID", "bastion-test-project")
    monkeypatch.setenv("MODEL_ARMOR_TEMPLATE_ID", "bastion-guardrail")
    verdicts: list[bool] = []

    def screen(text, *, project_id, template_id):
        return verdicts.pop(0) if verdicts else False

    monkeypatch.setattr(guardrails, "screen_prompt", screen)
    return verdicts


@pytest.mark.asyncio
async def test_screening_and_fidelity_run_once_across_a_recovered_retry(
    monkeypatch, emitted, waits, armor
):
    seen = _script(monkeypatch, [_error(429), _answer("A broad role needs review.")])
    calls: dict[str, int] = {}
    events = await _run(_guarded_auditor(calls))
    assert len(seen) == 2, "one rejected attempt, one recovered attempt"
    assert calls == {
        "screen_before_model": 1,
        "screen_after_model": 1,
        "validate_auditor_fidelity": 1,
    }
    assert "A broad role needs review." in _texts(events)
    outcomes = [r["outcome"] for r in emitted() if r["event"] == "model.request"]
    assert outcomes == ["submitted", "retrying", "completed"]


@pytest.mark.asyncio
async def test_blocked_input_makes_no_model_attempt(monkeypatch, emitted, waits, armor):
    from model_armor import guardrails

    armor.append(True)
    seen = _script(monkeypatch, [_error(429), _answer()])
    calls: dict[str, int] = {}
    events = await _run(_guarded_auditor(calls))
    assert seen == [] and waits == []
    assert guardrails.BLOCKED_MESSAGE in _texts(events)
    assert not any(r["outcome"] == "retrying" for r in emitted())


@pytest.mark.asyncio
async def test_a_blocked_response_stays_blocked_after_retry_recovery(
    monkeypatch, emitted, waits, armor
):
    from model_armor import guardrails

    leaked = "user:a.lee@example.com holds roles/owner"
    _script(monkeypatch, [_error(503), _answer(leaked)])
    calls: dict[str, int] = {}
    events = await _run(_guarded_auditor(calls))
    texts = _texts(events)
    assert guardrails.BLOCKED_OUTPUT_MESSAGE in texts
    assert not any("a.lee@example.com" in text for text in texts)
    assert calls["screen_after_model"] == 1
    assert "validate_auditor_fidelity" not in calls, "a withheld response has nothing to check"


@pytest.mark.asyncio
async def test_a_fabricated_report_is_still_rejected_after_retry_recovery(
    monkeypatch, emitted, waits, armor
):
    from agents.access_auditor import agent as auditor

    fabricated = json.dumps(
        {
            "findings": [
                {
                    "finding_id": "a" * 24,
                    "department": "platform-infra",
                    "reason": "broad_role",
                    "risk_score": 9,
                    "rationale": "Invented.",
                }
            ],
            "count": 1,
        }
    )
    _script(monkeypatch, [_error(429), _answer(fabricated)])
    calls: dict[str, int] = {}
    with pytest.raises(auditor.AuditorFidelityError):
        await _run(_guarded_auditor(calls))
    assert calls["validate_auditor_fidelity"] == 1
