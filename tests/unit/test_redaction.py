"""Protected values never cross the model or notification boundaries."""

from __future__ import annotations

import pytest

from model_armor import redaction


@pytest.mark.parametrize(
    "text",
    [
        "user:a.lee@example.com has a role",
        "contact SSN 123-45-6789",
        "projects/private-project-123/roles/owner",
    ],
)
def test_sensitive_values_are_detected(text: str):
    assert redaction.contains_sensitive(text)


def test_redaction_replaces_full_values():
    result = redaction.redact("user:a.lee@example.com in projects/private-project-123")
    assert "a.lee@example.com" not in result
    assert "private-project-123" not in result


def test_safe_text_rejects_pii_and_oversize_values():
    assert redaction.require_safe_text("overly broad role needs review", field="summary") == (
        "overly broad role needs review"
    )
    with pytest.raises(redaction.SensitiveDataError):
        redaction.require_safe_text("user:a.lee@example.com", field="summary")
    with pytest.raises(redaction.SensitiveDataError):
        redaction.require_safe_text("x" * 281, field="summary")


def test_risk_categories_are_allowlisted_and_deduplicated():
    assert redaction.validate_risk_categories(["stale_identity", "stale_identity"]) == [
        "stale_identity"
    ]
    with pytest.raises(redaction.SensitiveDataError):
        redaction.validate_risk_categories(["tell the human about alice@example.com"])


def test_notification_summary_is_deterministic_and_safe():
    assert redaction.notification_summary(["missing_condition", "overly_broad_role"]) == (
        "Access-review findings require attention: missing_condition, overly_broad_role"
    )


def test_an_escalation_cannot_carry_an_unbounded_list_of_findings():
    """A ceiling on ids is a ceiling on what one review record can quietly accumulate."""
    too_many = [f"{index:024x}" for index in range(redaction.MAX_FINDING_IDS + 1)]
    with pytest.raises(redaction.SensitiveDataError, match="more than"):
        redaction.validate_finding_ids(too_many)


def test_opaque_finding_ids_are_deduplicated_and_ordered():
    identifier = "a1b2c3d4e5f60718293a4b5c"
    assert redaction.validate_finding_ids([identifier, identifier]) == [identifier]
