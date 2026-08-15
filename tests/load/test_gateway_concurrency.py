"""Gateway policy remains deterministic under modest concurrent fan-in."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from gateway.policy import GatewayDenied, admit


@pytest.mark.load
def test_gateway_admission_is_stable_under_concurrent_requests():
    def admitted(_: int) -> str:
        return admit(
            caller="orchestrator",
            target="access_auditor",
            skill="audit_iam",
            classification="internal",
        ).agent_id

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(admitted, range(500)))
    assert results == ["access_auditor"] * 500


@pytest.mark.load
def test_gateway_rejection_is_stable_under_concurrent_attacks():
    def denied(_: int) -> bool:
        with pytest.raises(GatewayDenied):
            admit(
                caller="unregistered",
                target="access_auditor",
                skill="audit_iam",
                classification="internal",
            )
        return True

    with ThreadPoolExecutor(max_workers=16) as pool:
        assert all(pool.map(denied, range(500)))
