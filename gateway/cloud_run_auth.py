"""Audience-bound Cloud Run authentication for private A2A peers."""

from __future__ import annotations

import os
from collections.abc import Generator
from urllib.parse import urlsplit

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import id_token

PEER_SECRET_ENV = "BASTION_A2A_SHARED_SECRET"  # noqa: S105 - environment variable name
PEER_SECRET_HEADER = "X-Bastion-A2A-Token"  # noqa: S105 - HTTP header name


def audience(url: str) -> str:
    """Cloud Run validates the service origin, never the AgentCard path."""
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc:
        raise ValueError("a private Cloud Run peer must use an https URL")
    return f"{parts.scheme}://{parts.netloc}"


class CloudRunIdTokenAuth(httpx.Auth):
    """Fetch an ID token from the workload identity for every protected peer request."""

    def __init__(self, service_url: str, *, peer_origin: bool = False) -> None:
        self.target_audience = audience(service_url)
        self.request = Request()
        self.peer_origin = peer_origin

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        shared_secret = os.environ.get(PEER_SECRET_ENV) if self.peer_origin else None
        if shared_secret:
            # Agent Gateway authenticates the Agent Identity at egress. This separate
            # origin-bound credential prevents callers from bypassing Gateway and invoking a
            # network-reachable Cloud Run peer directly.
            request.headers[PEER_SECRET_HEADER] = shared_secret
            yield request
            return
        token = id_token.fetch_id_token(  # type: ignore[no-untyped-call]
            self.request, self.target_audience
        )
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


def private_a2a_client(card_url: str) -> httpx.AsyncClient:
    """Authenticate both private AgentCard lookup and A2A task messages."""
    return httpx.AsyncClient(
        auth=CloudRunIdTokenAuth(card_url, peer_origin=True), timeout=httpx.Timeout(600.0)
    )
