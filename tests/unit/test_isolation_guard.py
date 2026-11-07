"""The suite-wide isolation guard refuses what the 7 November incident did, and nothing local."""

from __future__ import annotations

import socket
import subprocess

import pytest

from tests.conftest import IsolationBreach


def test_a_unit_test_cannot_run_gcloud_or_reach_a_google_api(isolation_guard):
    with pytest.raises(IsolationBreach, match="start a process"):
        subprocess.run(["gcloud", "run", "services", "describe", "x"], check=False)
    with pytest.raises(IsolationBreach, match="resolve"):
        socket.create_connection(("run.googleapis.com", 443), timeout=1)
    with pytest.raises(IsolationBreach, match="connect"):
        socket.socket().connect(("203.0.113.10", 443))

    assert len(isolation_guard) == 3
    isolation_guard.clear()  # These breaches were deliberate; any other one fails its test.


def test_loopback_stays_available_for_in_process_transports():
    left, right = socket.socketpair()
    try:
        left.sendall(b"ok")
        assert right.recv(2) == b"ok"
    finally:
        left.close()
        right.close()
