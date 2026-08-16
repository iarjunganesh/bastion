"""Private Cloud Run A2A calls carry an audience-bound workload identity token."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest

from gateway.cloud_run_auth import (
    PEER_SECRET_HEADER,
    CloudRunIdTokenAuth,
    audience,
    private_a2a_client,
)


def test_audience_strips_path_and_accepts_only_https():
    assert audience("https://fleet-x.a.run.app/.well-known/agent-card.json") == (
        "https://fleet-x.a.run.app"
    )
    with pytest.raises(ValueError):
        audience("http://localhost:8080/card")


def test_auth_flow_attaches_google_id_token(monkeypatch):
    monkeypatch.delenv("BASTION_A2A_SHARED_SECRET", raising=False)
    auth = CloudRunIdTokenAuth("https://fleet-x.a.run.app/card", peer_origin=True)
    request = httpx.Request("GET", "https://fleet-x.a.run.app/card")
    with patch("gateway.cloud_run_auth.id_token.fetch_id_token", return_value="signed-token"):
        (authenticated,) = auth.auth_flow(request)
    assert authenticated.headers["Authorization"] == "Bearer signed-token"


def test_auth_flow_uses_origin_secret_behind_managed_gateway(monkeypatch):
    monkeypatch.setenv("BASTION_A2A_SHARED_SECRET", "separate-origin-credential")
    auth = CloudRunIdTokenAuth("https://fleet-x.a.run.app/card", peer_origin=True)
    request = httpx.Request("GET", "https://fleet-x.a.run.app/card")
    with patch("gateway.cloud_run_auth.id_token.fetch_id_token") as fetch:
        (authenticated,) = auth.auth_flow(request)
    assert authenticated.headers[PEER_SECRET_HEADER] == "separate-origin-credential"
    fetch.assert_not_called()


def test_non_peer_cloud_run_call_never_substitutes_the_peer_secret(monkeypatch):
    monkeypatch.setenv("BASTION_A2A_SHARED_SECRET", "separate-origin-credential")
    auth = CloudRunIdTokenAuth("https://findings-x.a.run.app/v1/escalations")
    request = httpx.Request("POST", "https://findings-x.a.run.app/v1/escalations")
    with patch("gateway.cloud_run_auth.id_token.fetch_id_token", return_value="identity-token"):
        (authenticated,) = auth.auth_flow(request)
    assert authenticated.headers["Authorization"] == "Bearer identity-token"
    assert PEER_SECRET_HEADER not in authenticated.headers


def test_private_client_uses_the_auth_contract():
    client = private_a2a_client("https://fleet-x.a.run.app/card")
    assert isinstance(client._auth, CloudRunIdTokenAuth)
    assert client._auth.peer_origin is True
