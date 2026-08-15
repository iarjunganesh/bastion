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


def lazy_client_mock() -> MagicMock:
    """A MagicMock that returns itself when called.

    The pillars use cached `client()` factories, so with a plain MagicMock every recorded call
    would sit one level deeper — `client.return_value.method(...)` — and each assertion would
    describe the patching mechanism instead of the behaviour under test.
    """
    mock = MagicMock()
    mock.return_value = mock
    return mock


os.environ.setdefault("GCP_PROJECT_ID", "bastion-test-project")
os.environ.setdefault("GCP_REGION", "europe-north2")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "bastion-test-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("VERTEX_AI_MODEL", "gemini-3.5-flash")
os.environ.setdefault("BASTION_FINDING_HMAC_KEY", "test-key-which-is-at-least-thirty-two-chars")
