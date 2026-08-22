"""The Model Armor template Bastion requires, as reviewable configuration.

A guardrail that lives only as a console artifact cannot be diffed, reviewed, or restored, and
nobody notices when it drifts. Holding the filter configuration here makes the security posture
part of the repository: provisioning applies it, and `verify_fleet` fails when the deployed
template stops matching.

**Why `MEDIUM_AND_ABOVE` and not the stricter `LOW_AND_ABOVE`.** The stricter setting was
deployed and measured against the live template on 2026-08-19. It refused the fleet's own
repository-owned prompts, and because Model Armor fails closed, every agent stopped producing
output at all: no tool calls, no findings, no escalation. A control that blocks 100% of
legitimate traffic supplies an outage, not security. The measurement separates the two cases
cleanly:

| Prompt screened | Match | Confidence |
|---|---|---|
| The injection probe from evidence 01 | yes | `HIGH` |
| `access_auditor` instruction (legitimate) | yes | `LOW` |
| `escalation_agent` instruction (legitimate) | no | -- |
| Benign control | no | -- |

`MEDIUM_AND_ABOVE` therefore still refuses the real injection while clearing the false positive.
Enforcement stays `ENABLED`: the threshold moves, the filter is not turned off, and nothing here
weakens the separate deterministic controls -- the fixed tool allowlist defends tool poisoning
([ADR-007](../docs/adr/007-tool-poisoning.md)) and post-model screening defends protected data.
Raising the threshold further, or disabling enforcement, is a deliberate security change and
should be argued for in an ADR rather than made here.
"""

from __future__ import annotations

from typing import Any

# The filter configuration the deployed template must carry, exactly.
FILTER_CONFIG: dict[str, Any] = {
    "piAndJailbreakFilterSettings": {
        "filterEnforcement": "ENABLED",
        "confidenceLevel": "MEDIUM_AND_ABOVE",
    }
}


def template_drift(observed: dict[str, Any] | None) -> list[str]:
    """Report how a deployed template differs from the configuration above.

    Absence is drift, not an empty result: a missing template means Model Armor screening is
    unavailable, and unavailable screening fails every model call closed.
    """
    if not observed:
        return ["Model Armor template is absent or unreadable"]
    errors: list[str] = []
    settings = observed.get("piAndJailbreakFilterSettings")
    if not isinstance(settings, dict):
        return ["Model Armor template declares no prompt-injection filter"]
    expected = FILTER_CONFIG["piAndJailbreakFilterSettings"]
    for key, want in expected.items():
        got = settings.get(key)
        if got != want:
            errors.append(f"Model Armor {key} is {got!r}, expected {want!r}")
    return errors
