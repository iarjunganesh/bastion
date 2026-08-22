"""The Model Armor template Bastion requires, as reviewable configuration.

A guardrail that lives only as a console artifact cannot be diffed, reviewed, or restored, and
nobody notices when it drifts. Holding the filter configuration here makes the security posture
part of the repository: provisioning applies it, and `verify_fleet` fails when the deployed
template stops matching.

**Why `MEDIUM_AND_ABOVE`.** Measured against the live template on 2026-08-19 rather than
reasoned about. The evidence 01 injection probe scores `HIGH`; the `access_auditor` instruction
scores `LOW`; the investigation envelope and a benign control do not match at all. `LOW` refused
the agents' own instructions, and Model Armor fails closed, so that refusal stopped every model
call in the fleet.

`HIGH` was tried and reverted. It did not clear the remaining false positive -- the fleet's
internal A2A hand-off scores at the same confidence as a real injection, because structurally a
message instructing an agent *is* an injection and only its provenance differs. So the threshold
is not the lever, and `HIGH` would have traded sensitivity for nothing. The real fix is to narrow
what gets screened; see [ADR-009](../docs/adr/009-model-armor-threshold.md).

Enforcement stays `ENABLED`: the threshold moves, the filter is not switched off. Changing either
is a security decision and belongs in an ADR.
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
