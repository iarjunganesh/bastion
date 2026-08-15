"""Provisioning validates Model Armor through its regional runtime API."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from infrastructure import provision


def test_model_armor_access_uses_regional_rest_endpoint():
    token = subprocess.CompletedProcess(["gcloud"], 0, "access-token\n", "")
    response = MagicMock()
    response.__enter__.return_value = response
    with (
        patch.object(provision.subprocess, "run", return_value=token),
        patch.object(provision.urllib.request, "urlopen", return_value=response) as urlopen,
    ):
        assert provision.model_armor_template_accessible()

    assert "modelarmor.europe-west4.rep.googleapis.com" in urlopen.call_args.args[0].full_url


def test_model_armor_access_fails_closed_when_google_rejects_the_request():
    token = subprocess.CompletedProcess(["gcloud"], 0, "access-token\n", "")
    with (
        patch.object(provision.subprocess, "run", return_value=token),
        patch.object(provision.urllib.request, "urlopen", side_effect=TimeoutError),
    ):
        assert not provision.model_armor_template_accessible()
