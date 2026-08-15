"""The private human-review inbox accepts only Bastion's minimized schema."""

from __future__ import annotations

import pytest

from infrastructure.findings_api import Escalation, _validate


def payload(**overrides: object) -> Escalation:
    values: dict[str, object] = {
        "source": "bastion",
        "investigation_id": "investigation-1",
        "department": "security-engineering",
        "finding_count": 1,
        "risk_categories": ["overly_broad_role"],
        "summary": "Access-review findings require attention: overly_broad_role",
    }
    values.update(overrides)
    return Escalation.model_validate(values)


def test_accepts_the_count_only_allowlisted_escalation_shape():
    _validate(payload())


@pytest.mark.parametrize(
    "change",
    [
        {"source": "untrusted"},
        {"department": "everyone"},
        {"risk_categories": ["free text"]},
        {"summary": "a model-supplied narrative"},
    ],
)
def test_rejects_untrusted_routing_and_model_text(change: dict[str, object]):
    with pytest.raises(ValueError):
        _validate(payload(**change))
