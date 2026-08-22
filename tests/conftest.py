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
from unittest.mock import MagicMock

import google.auth
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
