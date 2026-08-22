"""Data-minimisation helpers for model and notification boundaries.

The global Gemini endpoint and a human-notification endpoint are separate trust boundaries.
Neither receives IAM principals, resource paths, or government identifiers. Model Armor is a
managed classifier; these deterministic checks are the complementary data-loss-prevention
control that still works when a classifier is unavailable.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
GCP_RESOURCE = re.compile(r"\b(?:projects|folders|organizations)/[A-Za-z0-9._/-]+")

SAFE_RISK_CATEGORIES = frozenset({"overly_broad_role", "missing_condition", "stale_identity"})


class SensitiveDataError(ValueError):
    """Raised when a payload would cross a boundary with protected data."""


def contains_sensitive(text: str) -> bool:
    """Whether text contains a principal, government ID, or fully-qualified GCP resource."""
    return bool(EMAIL.search(text) or SSN.search(text) or GCP_RESOURCE.search(text))


def redact(text: str) -> str:
    """Replace protected values with stable class labels, never partial identifiers."""
    redacted = EMAIL.sub("[REDACTED:principal]", text)
    redacted = SSN.sub("[REDACTED:government-id]", redacted)
    return GCP_RESOURCE.sub("[REDACTED:resource]", redacted)


def require_safe_text(text: str, *, field: str) -> str:
    """Return bounded safe text or reject it before it crosses a trust boundary."""
    if contains_sensitive(text):
        raise SensitiveDataError(f"{field} contains protected data")
    if len(text) > 280:
        raise SensitiveDataError(f"{field} exceeds the 280-character boundary")
    return text


def validate_risk_categories(categories: Iterable[str]) -> list[str]:
    """Accept only deterministic policy reason codes, in stable order."""
    values = sorted(set(categories))
    invalid = [value for value in values if value not in SAFE_RISK_CATEGORIES]
    if invalid:
        raise SensitiveDataError("unknown or unsafe risk category")
    return values


def notification_summary(categories: Iterable[str]) -> str:
    """Build notification text from allowlisted reason codes, never model output."""
    values = validate_risk_categories(categories)
    return "Access-review findings require attention: " + ", ".join(values)


# The Access Auditor emits `hmac_sha256(...).hexdigest()[:24]`. Validating the exact shape means
# a model that fabricates an identifier produces something inert rather than something stored:
# an opaque ID grants nothing, reveals nothing, and can only ever key an exception that no real
# finding will match.
OPAQUE_FINDING_ID = re.compile(r"\A[0-9a-f]{24}\Z")

# One investigation escalating more findings than this is a policy failure worth seeing, not a
# payload worth storing.
MAX_FINDING_IDS = 100


def validate_finding_ids(finding_ids: Iterable[str]) -> list[str]:
    """Accept only opaque Auditor finding identifiers, deduplicated and in stable order."""
    values = sorted(set(finding_ids))
    if not values:
        raise SensitiveDataError("at least one opaque finding id is required")
    if len(values) > MAX_FINDING_IDS:
        raise SensitiveDataError(f"more than {MAX_FINDING_IDS} finding ids in one escalation")
    if any(not OPAQUE_FINDING_ID.match(value) for value in values):
        raise SensitiveDataError("finding id is not an opaque Auditor identifier")
    return values
