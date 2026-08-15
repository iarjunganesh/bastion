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
