"""Every documented test total matches the suite that actually ran.

The suite size is the most drift-prone number in the repository: it changes on any commit that
adds a test, and six documents quote it. It has already gone stale twice — once as "132 unit
tests", once as 161 when the tool-surface security suite landed — because `check_docs.py`
verified pillar, ADR, agent, badge and diagram counts but never this one.

It is asserted here rather than there on purpose. `check_docs.py` runs on a bare interpreter in
CI's docs and diagrams jobs, with no dependencies installed and therefore no pytest to collect
with. Inside the suite the collected count is already known, so the check costs nothing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# "170 tests", "170 unit tests", "170 passed". Two digits minimum, so prose like "3 agents"
# and "5 alert policies" cannot be mistaken for a suite total.
TEST_COUNT_CLAIM = re.compile(r"\b(\d{2,4})\s+(?:\w+\s+)?tests?\b|\b(\d{2,4})\s+passed\b")

SKIP_DIRS = {".git", ".venv", "venv", ".audit-venv", "node_modules", ".tmp", ".mypy_cache"}

# Released sections record what was true at their tag. Rewriting them to match today would
# falsify the release record rather than correct it.
EXEMPT = {"CHANGELOG.md"}


def documented_counts() -> list[tuple[str, int, int]]:
    """Return (relative path, line number, claimed count) for every documented suite total."""
    claims: list[tuple[str, int, int]] = []
    for path in sorted(ROOT.rglob("*.md")):
        if SKIP_DIRS.intersection(path.parts) or path.name in EXEMPT:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in TEST_COUNT_CLAIM.finditer(line):
                claims.append((relative, number, int(match.group(1) or match.group(2))))
    return claims


def test_documented_test_totals_match_the_collected_suite(request):
    """A documented total is a claim; this is its record.

    Skips on a partial run rather than failing: `pytest tests/security` collects a subset, and
    a gate that fires on every narrowed run would be trained away rather than trusted.
    """
    items = request.session.items
    collected_files = {Path(item.location[0]).name for item in items}
    on_disk = {path.name for path in (ROOT / "tests").rglob("test_*.py")}
    if collected_files != on_disk:
        pytest.skip(f"partial run: {len(collected_files)} of {len(on_disk)} test files collected")

    total = len(items)
    wrong = [claim for claim in documented_counts() if claim[2] != total]
    assert not wrong, "documented test totals disagree with the collected suite: " + "; ".join(
        f"{path}:{line} claims {claimed}, collected {total}" for path, line, claimed in wrong
    )
