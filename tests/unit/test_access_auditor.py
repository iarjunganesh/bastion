"""The Access Auditor reads a real policy and detects deterministically."""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agents.access_auditor import agent as auditor


def _binding(role: str, members: list[str]) -> SimpleNamespace:
    return SimpleNamespace(role=role, members=members)


def _result(bindings: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(policy=SimpleNamespace(bindings=bindings))


@pytest.fixture(autouse=True)
def _clear_client_cache():
    auditor.asset_client.cache_clear()
    yield
    auditor.asset_client.cache_clear()


def test_fetch_reads_through_cloud_asset_inventory_not_a_subprocess():
    """The read path is a client library, because a Cloud Run image has no gcloud binary."""
    with patch.object(auditor, "asset_client") as client:
        client.return_value.search_all_iam_policies.return_value = iter(
            [_result([_binding("roles/owner", ["user:a@example.com"])])]
        )
        policy = auditor.fetch_iam_policy()

    assert policy == {"bindings": [{"role": "roles/owner", "members": ["user:a@example.com"]}]}
    request = client.return_value.search_all_iam_policies.call_args.kwargs["request"]
    assert request.scope == f"projects/{os.environ['GCP_PROJECT_ID']}"


def test_fetch_stops_at_the_result_cap():
    """An unbounded walk over a large scope is not something an agent turn should do."""
    many = iter([_result([_binding("roles/owner", ["user:a@example.com"])])] * 900)
    with patch.object(auditor, "asset_client") as client:
        client.return_value.search_all_iam_policies.return_value = many
        policy = auditor.fetch_iam_policy()

    assert len(policy["bindings"]) == auditor.MAX_POLICY_RESULTS


def test_project_id_error_names_the_fix_not_the_traceback():
    with patch.dict("os.environ", {}, clear=True), pytest.raises(RuntimeError) as raised:
        auditor.project_id()
    assert "GCP_PROJECT_ID" in str(raised.value)


@pytest.mark.parametrize("role", sorted(auditor.OVERLY_BROAD_ROLES))
def test_broad_roles_are_flagged(role: str):
    findings = auditor.find_anomalies(
        {"bindings": [{"role": role, "members": ["serviceAccount:x@y.iam.gserviceaccount.com"]}]}
    )
    assert len(findings) == 1
    assert findings[0]["reason"] == "overly_broad_role"
    assert findings[0]["risk_score"] == 0.8


def test_narrow_roles_are_not_flagged():
    findings = auditor.find_anomalies(
        {"bindings": [{"role": "roles/iam.securityReviewer", "members": ["user:a@example.com"]}]}
    )
    assert findings == []


def test_every_member_of_a_broad_binding_is_flagged_separately():
    findings = auditor.find_anomalies(
        {"bindings": [{"role": "roles/editor", "members": ["user:a@x.com", "user:b@x.com"]}]}
    )
    assert len({f["finding_id"] for f in findings}) == 2
    assert all(f["department"] == "security-engineering" for f in findings)
    assert all("member" not in finding and "role" not in finding for finding in findings)


def test_finding_id_requires_a_long_secret_and_changes_with_the_key(monkeypatch):
    monkeypatch.delenv(auditor.FINDING_HMAC_KEY_VAR)
    with pytest.raises(RuntimeError, match=auditor.FINDING_HMAC_KEY_VAR):
        auditor.finding_id("user:a@example.com", "roles/owner")
    monkeypatch.setenv(auditor.FINDING_HMAC_KEY_VAR, "a" * 32)
    first = auditor.finding_id("user:a@example.com", "roles/owner")
    monkeypatch.setenv(auditor.FINDING_HMAC_KEY_VAR, "b" * 32)
    assert first != auditor.finding_id("user:a@example.com", "roles/owner")


def test_an_empty_policy_yields_no_findings():
    assert auditor.find_anomalies({}) == []


def test_audit_tool_takes_no_arguments():
    """The tool cannot be redirected at another project, because it accepts no target.

    This is the tool-poisoning control from ADR-007 expressed as a signature rather than as a
    check someone has to remember to write.
    """
    import inspect

    assert list(inspect.signature(auditor.audit_iam_policy).parameters) == []


def test_audit_tool_returns_a_count_and_the_findings():
    with patch.object(auditor, "fetch_iam_policy") as fetch:
        fetch.return_value = {
            "bindings": [{"role": "roles/owner", "members": ["user:a@example.com"]}]
        }
        result = auditor.audit_iam_policy()

    assert result["count"] == 1
    assert result["findings"][0]["reason"] == "overly_broad_role"
    assert "member" not in result["findings"][0]


def test_the_agent_is_an_adk_agent_with_the_guardrail_attached():
    from model_armor.guardrails import screen_after_model, screen_before_model

    assert auditor.access_auditor.name == "access_auditor"
    assert auditor.access_auditor.model == "gemini-3.5-flash"
    assert auditor.access_auditor.before_model_callback is screen_before_model
    assert auditor.access_auditor.after_model_callback is screen_after_model


def test_the_asset_client_is_built_once_and_cached():
    """Built on first use, not at import: importing this module must not authenticate."""
    with patch.object(auditor.asset_v1, "AssetServiceClient") as ctor:
        first = auditor.asset_client()
        second = auditor.asset_client()
    assert first is second
    ctor.assert_called_once()
