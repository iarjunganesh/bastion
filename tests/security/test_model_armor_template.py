"""The guardrail configuration is reviewable, enforcing, and cannot drift silently."""

from __future__ import annotations

from model_armor.template import FILTER_CONFIG, template_drift


def deployed(**overrides: object) -> dict[str, object]:
    settings = dict(FILTER_CONFIG["piAndJailbreakFilterSettings"])
    settings.update(overrides)
    return {"piAndJailbreakFilterSettings": settings}


def test_the_declared_configuration_matches_itself():
    assert template_drift(deployed()) == []


def test_enforcement_stays_enabled():
    """Tuning the threshold is a judgement call; switching the filter off is not the same act."""
    assert FILTER_CONFIG["piAndJailbreakFilterSettings"]["filterEnforcement"] == "ENABLED"
    drift = template_drift(deployed(filterEnforcement="DISABLED"))
    assert drift and "filterEnforcement" in drift[0]


def test_a_changed_threshold_is_reported():
    """A guardrail retuned in the console still answers, so nothing else would notice."""
    drift = template_drift(deployed(confidenceLevel="LOW_AND_ABOVE"))
    assert drift and "confidenceLevel" in drift[0]


def test_an_absent_template_is_drift_not_silence():
    """Model Armor fails closed, so an unreadable template stops the whole fleet."""
    assert template_drift(None) == ["Model Armor template is absent or unreadable"]
    assert template_drift({}) == ["Model Armor template is absent or unreadable"]


def test_a_template_without_the_injection_filter_is_rejected():
    drift = template_drift({"someOtherFilter": {}})
    assert drift == ["Model Armor template declares no prompt-injection filter"]


def test_the_threshold_still_refuses_a_high_confidence_injection():
    """Measured on the live template: the evidence 01 probe scores HIGH, while the fleet's own
    instructions and internal hand-off score below it. HIGH is the only setting that refuses the
    injection without refusing the fleet, so this pins it rather than leaving it to preference."""
    assert FILTER_CONFIG["piAndJailbreakFilterSettings"]["confidenceLevel"] == "MEDIUM_AND_ABOVE"
