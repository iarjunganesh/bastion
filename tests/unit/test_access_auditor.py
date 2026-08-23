"""The Access Auditor reads a real policy and detects deterministically."""

from __future__ import annotations

import json
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
    assert auditor.access_auditor.after_model_callback == [
        screen_after_model,
        auditor.validate_auditor_fidelity,
    ]
    assert auditor.access_auditor.after_tool_callback is auditor.persist_canonical_findings


def test_the_asset_client_is_built_once_and_cached():
    """Built on first use, not at import: importing this module must not authenticate."""
    with patch.object(auditor.asset_v1, "AssetServiceClient") as ctor:
        first = auditor.asset_client()
        second = auditor.asset_client()
    assert first is second
    ctor.assert_called_once()


# --- P0.1: the model's answer is checked against the tool's, not trusted on its shape alone --


def test_persist_canonical_findings_writes_the_tools_real_answer():
    state: dict = {}
    tool_context = SimpleNamespace(state=state)
    auditor.persist_canonical_findings(
        tool=SimpleNamespace(name="audit_iam_policy"),
        args={},
        tool_context=tool_context,
        tool_response={"count": 1, "findings": [{"finding_id": "a" * 24}]},
    )
    assert state[auditor.CANONICAL_FINDINGS_KEY] == [{"finding_id": "a" * 24}]


def test_persist_canonical_findings_ignores_a_different_tool():
    """Only one tool exists today, but the guard is the point, not a no-op detail."""
    state: dict = {}
    tool_context = SimpleNamespace(state=state)
    auditor.persist_canonical_findings(
        tool=SimpleNamespace(name="some_other_tool"),
        args={},
        tool_context=tool_context,
        tool_response={"findings": [{"finding_id": "a" * 24}]},
    )
    assert state == {}


def _part(text: str | None = None, function_call: object | None = None) -> SimpleNamespace:
    return SimpleNamespace(text=text, function_call=function_call)


def test_final_answer_text_is_none_for_a_tool_call_turn():
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(function_call=object())]))
    assert auditor._final_answer_text(response) is None


def test_final_answer_text_is_none_when_there_is_no_text():
    assert auditor._final_answer_text(SimpleNamespace(content=SimpleNamespace(parts=[]))) is None
    assert auditor._final_answer_text(SimpleNamespace(content=None)) is None


def test_final_answer_text_joins_every_text_part():
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(text="a"), _part(text="b")]))
    assert auditor._final_answer_text(response) == "a\nb"


_CANONICAL = [
    {
        "finding_id": "a" * 24,
        "department": "security-engineering",
        "reason": "overly_broad_role",
        "risk_score": 0.8,
    }
]


def _reported(**overrides) -> dict:
    finding = dict(_CANONICAL[0], rationale="An overly broad role is held without a condition.")
    finding.update(overrides)
    return finding


def test_fidelity_accepts_an_exact_copy_with_only_rationale_changed():
    assert auditor._fidelity_mismatch(_CANONICAL, [_reported()], 1) is None


def test_fidelity_accepts_a_genuinely_clean_run():
    assert auditor._fidelity_mismatch([], [], 0) is None


def test_fidelity_rejects_a_missing_canonical():
    """The model answered without the tool ever having run in this turn."""
    assert auditor._fidelity_mismatch(None, [], 0) == "missing_canonical"


def test_fidelity_rejects_a_fabricated_id():
    assert (
        auditor._fidelity_mismatch(_CANONICAL, [_reported(finding_id="b" * 24)], 1)
        == "id_set_mismatch"
    )


def test_fidelity_rejects_a_dropped_finding():
    two = _CANONICAL + [{**_CANONICAL[0], "finding_id": "c" * 24}]
    assert auditor._fidelity_mismatch(two, [_reported()], 1) == "id_set_mismatch"


def test_fidelity_rejects_an_added_finding():
    extra = _reported(finding_id="d" * 24)
    assert auditor._fidelity_mismatch(_CANONICAL, [_reported(), extra], 2) == "id_set_mismatch"


def test_fidelity_rejects_a_changed_score():
    assert (
        auditor._fidelity_mismatch(_CANONICAL, [_reported(risk_score=0.5)], 1) == "field_mismatch"
    )


def test_fidelity_rejects_a_changed_reason():
    assert (
        auditor._fidelity_mismatch(_CANONICAL, [_reported(reason="stale_identity")], 1)
        == "field_mismatch"
    )


def test_fidelity_rejects_a_changed_department():
    assert (
        auditor._fidelity_mismatch(_CANONICAL, [_reported(department="ml-engineering")], 1)
        == "field_mismatch"
    )


def test_fidelity_rejects_duplicate_ids():
    assert (
        auditor._fidelity_mismatch(_CANONICAL, [_reported(), _reported()], 2)
        == "duplicate_finding_id"
    )


def test_fidelity_rejects_a_wrong_count():
    assert auditor._fidelity_mismatch(_CANONICAL, [_reported()], 2) == "count_mismatch"


def test_fidelity_rejects_a_malformed_finding():
    assert auditor._fidelity_mismatch(_CANONICAL, [{"department": "x"}], 1) == "malformed_finding"


def _callback_ctx(state: dict) -> SimpleNamespace:
    return SimpleNamespace(state=state)


def test_validate_auditor_fidelity_skips_a_tool_call_turn():
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(function_call=object())]))
    assert auditor.validate_auditor_fidelity(_callback_ctx({}), response) is None


def test_validate_auditor_fidelity_skips_prose():
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(text="Two findings.")]))
    assert auditor.validate_auditor_fidelity(_callback_ctx({}), response) is None


def test_validate_auditor_fidelity_skips_a_shape_that_is_not_a_report():
    response = SimpleNamespace(
        content=SimpleNamespace(parts=[_part(text=json.dumps({"count": 0}))])
    )
    assert auditor.validate_auditor_fidelity(_callback_ctx({}), response) is None


def test_validate_auditor_fidelity_accepts_a_faithful_report():
    report = {"count": 1, "findings": [_reported()]}
    state = {auditor.CANONICAL_FINDINGS_KEY: _CANONICAL}
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(text=json.dumps(report))]))
    assert auditor.validate_auditor_fidelity(_callback_ctx(state), response) is None


def test_validate_auditor_fidelity_rejects_a_mismatch_and_emits_a_bounded_audit_record(
    monkeypatch,
):
    calls = []
    monkeypatch.setattr(auditor, "record", lambda *args, **kwargs: calls.append(kwargs))
    report = {"count": 1, "findings": [_reported(risk_score=0.1)]}
    state = {auditor.CANONICAL_FINDINGS_KEY: _CANONICAL}
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(text=json.dumps(report))]))

    with pytest.raises(auditor.AuditorFidelityError, match="field_mismatch"):
        auditor.validate_auditor_fidelity(_callback_ctx(state), response)

    (kwargs,) = calls
    assert kwargs["detail"] == {"reason": "field_mismatch"}


def test_validate_auditor_fidelity_rejects_when_the_tool_never_ran():
    report = {"count": 0, "findings": []}
    response = SimpleNamespace(content=SimpleNamespace(parts=[_part(text=json.dumps(report))]))
    with pytest.raises(auditor.AuditorFidelityError, match="missing_canonical"):
        auditor.validate_auditor_fidelity(_callback_ctx({}), response)
