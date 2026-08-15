"""Private Cloud Run A2A calls carry an audience-bound workload identity token."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from gateway.cloud_run_auth import CloudRunIdTokenAuth, audience, private_a2a_client


def test_audience_strips_path_and_accepts_only_https():
    assert audience("https://fleet-x.a.run.app/.well-known/agent-card.json") == (
        "https://fleet-x.a.run.app"
    )
    with pytest.raises(ValueError):
        audience("http://localhost:8080/card")


def test_auth_flow_attaches_google_id_token():
    auth = CloudRunIdTokenAuth("https://fleet-x.a.run.app/card")
    request = httpx.Request("GET", "https://fleet-x.a.run.app/card")
    with patch("gateway.cloud_run_auth.id_token.fetch_id_token", return_value="signed-token"):
        (authenticated,) = auth.auth_flow(request)
    assert authenticated.headers["Authorization"] == "Bearer signed-token"


def test_private_client_uses_the_auth_contract():
    client = private_a2a_client("https://fleet-x.a.run.app/card")
    assert isinstance(client._auth, CloudRunIdTokenAuth)
