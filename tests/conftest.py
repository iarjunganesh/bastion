"""Test bootstrap.

Bastion's clients are built on first use — `asset_client()` in the Access Auditor, `client()`
in the Model Armor guardrail — so importing a module no longer attempts credential discovery.
The environment defaults below still run at conftest *import* time rather than in a fixture,
because pytest imports every test module during collection and a fixture would be too late for
anything that reads configuration at import.

CI holds no GCP credentials and is not meant to. A test suite able to reach a real IAM policy
would be a credential path into the very project Bastion audits — so every outbound call in
this suite is mocked, and a test that needs Google APIs is a test that is checking the wrong
thing.
"""

from __future__ import annotations

import os
import socket
import subprocess
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

import google.auth
import pytest
from google.auth.credentials import AnonymousCredentials


def lazy_client_mock() -> MagicMock:
    """A MagicMock that returns itself when called.

    The pillars use cached `client()` factories, so with a plain MagicMock every recorded call
    would sit one level deeper — `client.return_value.method(...)` — and each assertion would
    describe the patching mechanism instead of the behaviour under test.
    """
    mock = MagicMock()
    mock.return_value = mock
    return mock


def _default(key: str, value: str) -> None:
    """Set a test default when the variable is missing **or set to an empty string**.

    `os.environ.setdefault` only fills a missing key, so a `.env` that declares a placeholder
    with no value — `BASTION_FINDING_HMAC_KEY=` — silently defeats it, and the suite then fails
    only for contributors who export their environment before running it. CI, which exports
    nothing, stayed green throughout. Nine tests failed this way before it was noticed.

    Treating empty as unset here matches what the production code now does for the same reason;
    it does not weaken any assertion, because every value below is a test fixture rather than a
    credential the suite is allowed to reach a real project with.
    """
    if not os.environ.get(key, "").strip():
        os.environ[key] = value


_default("GCP_PROJECT_ID", "bastion-test-project")
_default("GCP_REGION", "europe-north2")
_default("GOOGLE_CLOUD_PROJECT", "bastion-test-project")
_default("GOOGLE_CLOUD_LOCATION", "global")
_default("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
_default("VERTEX_AI_MODEL", "gemini-3.5-flash")
_default("BASTION_FINDING_HMAC_KEY", "test-key-which-is-at-least-thirty-two-chars")


def _anonymous_default(*args: object, **kwargs: object) -> tuple[AnonymousCredentials, str]:
    """Return credentials that cannot authenticate, and the mock project."""
    del args, kwargs
    return AnonymousCredentials(), os.environ["GOOGLE_CLOUD_PROJECT"]


# Application Default Credentials are neutralised for the whole suite, at conftest import time
# for the same reason as the environment above: `AdkApp` resolves the ambient project through
# `google.auth.default()` while the managed Agent Runtime entrypoint module is imported, and
# that import happens during collection.
#
# Without this, the suite passes on a workstation that happens to hold ADC and fails only in
# CI, which holds none deliberately — the result depends on whose machine it runs on rather
# than on the code. Anonymous credentials make the contract explicit and enforce it: no test
# can reach a real project, whatever the ambient gcloud configuration says.
google.auth.default = _anonymous_default  # type: ignore[assignment]


LOOPBACK = frozenset({"127.0.0.1", "::1", "localhost"})


class IsolationBreach(RuntimeError):
    """A test tried to start a process or reach beyond the loopback interface."""


@pytest.fixture(autouse=True)
def isolation_guard(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[str]]:
    """Refuse every child process and non-loopback connection, and fail the test that tried.

    Neutralising ADC above does not bind the `gcloud` CLI, which carries the operator's own login.
    On 7 November a new test set the wrong override variable, an operator module fell back to
    `gcloud run services describe`, and two read-only calls reached Google Cloud for a project
    that does not exist. They failed harmlessly; this guard makes the class impossible rather than
    unlikely. Each breach is recorded as well as raised, so a library that swallows the exception
    still fails the test at teardown. The suite needed no exemption when this was added.
    """
    attempts: list[str] = []
    connect, connect_ex = socket.socket.connect, socket.socket.connect_ex
    getaddrinfo = socket.getaddrinfo

    def breach(action: str, target: object) -> IsolationBreach:
        attempts.append(f"{action}: {target}")
        return IsolationBreach(f"unit tests may not {action}: {target}")

    def remote(address: object) -> bool:
        return isinstance(address, tuple) and str(address[0]) not in LOOPBACK

    class NoProcess:
        def __init__(self, args: object, *_args: Any, **_kwargs: Any) -> None:
            raise breach("start a process", args)

    def guarded_connect(sock: socket.socket, address: Any) -> None:
        if remote(address):
            raise breach("connect", address)
        connect(sock, address)

    def guarded_connect_ex(sock: socket.socket, address: Any) -> int:
        if remote(address):
            raise breach("connect", address)
        return connect_ex(sock, address)

    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        if host is not None and str(host) not in LOOPBACK:
            raise breach("resolve", host)
        return getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", NoProcess)
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    yield attempts
    if attempts:
        pytest.fail(f"Test isolation breached: {attempts}")
