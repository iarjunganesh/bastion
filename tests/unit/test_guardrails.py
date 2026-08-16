"""Model Armor screening fails closed, and short-circuits the model when it fires."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from model_armor import guardrails


def _request(*texts: str) -> SimpleNamespace:
    return SimpleNamespace(
        model="gemini-3.5-flash",
        contents=[
            SimpleNamespace(parts=[SimpleNamespace(text=t) for t in texts]),
        ],
    )


@pytest.fixture(autouse=True)
def _configured():
    with patch.dict(
        "os.environ",
        {"GCP_PROJECT_ID": "bastion-test-project", "MODEL_ARMOR_TEMPLATE_ID": "bastion-tmpl"},
    ):
        guardrails.client.cache_clear()
        yield
        guardrails.client.cache_clear()


def test_a_clean_prompt_proceeds_to_the_model():
    with patch.object(guardrails, "screen_prompt", return_value=False):
        assert guardrails.screen_before_model(MagicMock(), _request("list the findings")) is None


def test_a_malicious_prompt_never_reaches_the_model():
    """Returning an LlmResponse replaces the model call — the injected text is not sent.

    A callback that screened and then called anyway would be theatre; this is the property the
    demo has to show.
    """
    with patch.object(guardrails, "screen_prompt", return_value=True):
        response = guardrails.screen_before_model(
            MagicMock(), _request(guardrails.MALICIOUS_TICKET_EXAMPLE)
        )

    assert response is not None
    assert guardrails.BLOCKED_MESSAGE in response.content.parts[0].text


def test_an_unprovisioned_template_blocks_rather_than_skips():
    """A missing environment variable must not silently disable a security control."""
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "p"}, clear=True):
        response = guardrails.screen_before_model(MagicMock(), _request("anything"))
    assert response is not None


def test_a_screening_failure_blocks_rather_than_opens():
    """An exception on the screening path is not an open door."""
    with patch.object(guardrails, "screen_prompt", side_effect=RuntimeError("armor down")):
        response = guardrails.screen_before_model(MagicMock(), _request("anything"))
    assert response is not None


def test_empty_content_is_not_screened():
    with patch.object(guardrails, "screen_prompt") as screen:
        assert guardrails.screen_before_model(MagicMock(), _request("   ")) is None
    screen.assert_not_called()


def test_sensitive_model_output_is_withheld():
    response = guardrails._refusal()
    response.content.parts[0].text = "user:a.lee@example.com has roles/owner"
    blocked = guardrails.screen_after_model(MagicMock(), response)
    assert blocked is not None
    assert guardrails.BLOCKED_OUTPUT_MESSAGE in blocked.content.parts[0].text


def test_safe_model_output_is_not_replaced():
    response = guardrails._refusal()
    response.content.parts[0].text = "A policy category needs review."
    assert guardrails.screen_after_model(MagicMock(), response) is None


def test_sensitive_structured_model_output_is_withheld():
    response = MagicMock()
    response.content.parts = [
        SimpleNamespace(
            text=None,
            function_response=SimpleNamespace(response={"member": "a@x.com"}),
        )
    ]
    assert guardrails.screen_after_model(MagicMock(), response) is not None


def test_refusals_emit_only_a_bounded_reason():
    context = SimpleNamespace(invocation_id="inv-refusal")
    with (
        patch.object(guardrails, "screen_prompt", return_value=True),
        patch.object(guardrails, "record") as record,
    ):
        guardrails.screen_before_model(context, _request("user:a@example.com"))
    record.assert_called_once_with(
        "model_armor.input",
        outcome="refused",
        actor="model-armor",
        invocation_id="inv-refusal",
        detail={"reason": "policy_match"},
    )
    assert "a@example.com" not in str(record.call_args)


def test_screen_prompt_reports_blocked_not_safe():
    """The boolean is "blocked" deliberately: a falsy error default must not read as safe."""
    from google.cloud import modelarmor_v1 as modelarmor

    with patch.object(guardrails, "client") as client:
        client.return_value.sanitize_user_prompt.return_value = SimpleNamespace(
            sanitization_result=SimpleNamespace(
                filter_match_state=modelarmor.FilterMatchState.MATCH_FOUND
            )
        )
        assert guardrails.screen_prompt("x", project_id="p", template_id="t") is True


def test_the_endpoint_is_not_gcp_region():
    """Model Armor does not serve europe-north2, so it cannot reuse GCP_REGION."""
    with patch.object(guardrails.modelarmor, "ModelArmorClient") as client:
        guardrails.client()
    endpoint = client.call_args.kwargs["client_options"]["api_endpoint"]
    assert endpoint == "modelarmor.europe-west4.rep.googleapis.com"


def test_the_template_path_is_regional():
    path = guardrails.template_path("bastion-fleet-2026", "tmpl")
    assert path == "projects/bastion-fleet-2026/locations/europe-west4/templates/tmpl"
