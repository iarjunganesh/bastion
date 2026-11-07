"""Bounded, audited retry of transient model-service errors.

Cohort H stopped on 7 November when one Access Auditor call received `429 RESOURCE_EXHAUSTED`.
The fleet failed closed, as designed, and Pub/Sub redelivery completed the investigation on a
second attempt. ADK's `Gemini` never retries by default, so a single transient rejection from a
shared model service escalated to a whole failed investigation and a redelivery.

A production client retries a transient rejection itself, briefly and with backoff, and fails
closed only when the service stays unavailable. This module does exactly that, under three
rules:

* **Only transient statuses** (429 and 5xx) are retried. A 4xx such as 400 or 403 is a real
  error and raises at once.
* **Only before the first response.** A call that has yielded anything is never retried, so a
  partial answer can never be duplicated or spliced.
* **Every retry is an audit record.** `model.request` / `retrying` carries the attempt number,
  the HTTP status and the wait, so retries are counted, never hidden. When the attempts run out
  the original error propagates and the Orchestrator fails closed exactly as before.

The retry wraps ADK's call below the agent callbacks, so Model Armor screening, the fidelity
check and the `submitted`/`completed` audit pair run once per model call, not once per attempt.
"""

from __future__ import annotations

import asyncio
import copy
import random
from collections.abc import AsyncGenerator

from google.adk.models.google_llm import Gemini
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import errors as genai_errors

from observability.audit import record_model_retry

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 4
INITIAL_DELAY_SECONDS = 2.0
MAX_DELAY_SECONDS = 10.0

# Not a security boundary: jitter only spreads retries so that callers rejected together do not
# return together.
_jitter = random.SystemRandom()
_sleep = asyncio.sleep


def backoff_seconds(attempt: int) -> float:
    """The wait after failed attempt `attempt` (1-based): capped exponential, 50-100% jitter."""
    ceiling = min(MAX_DELAY_SECONDS, INITIAL_DELAY_SECONDS * 2 ** (attempt - 1))
    return float(round(ceiling * _jitter.uniform(0.5, 1.0), 3))


class RetryingGemini(Gemini):
    """ADK's `Gemini`, with a bounded, audited retry of transient errors before any response."""

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        # ADK's preprocessing mutates the request in place; every retry starts from the request
        # exactly as the flow handed it over.
        contents = copy.deepcopy(llm_request.contents)
        config = llm_request.config.model_copy(deep=True)
        attempt = 1
        while True:
            yielded = False
            try:
                async for response in super().generate_content_async(llm_request, stream):
                    yielded = True
                    yield response
                return
            except genai_errors.APIError as error:
                if yielded or error.code not in RETRYABLE_STATUS or attempt >= MAX_ATTEMPTS:
                    raise
                delay = backoff_seconds(attempt)
                record_model_retry(attempt=attempt, status=error.code, delay_seconds=delay)
                await _sleep(delay)
                llm_request.contents = copy.deepcopy(contents)
                llm_request.config = config.model_copy(deep=True)
                attempt += 1
