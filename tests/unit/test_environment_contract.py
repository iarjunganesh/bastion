"""`.env.example` declares every variable the code actually reads.

Reproducible setup is a graded submission criterion, and `CONTRIBUTING.md` tells a newcomer to
copy this file and go. When it drifts, the failure is silent and lands on someone with a clean
clone: `deploy.sh` aborts on a `${VAR:?}` guard, or the Runtime raises at import.

It had drifted badly - 15 declared against roughly 35 in use, missing three that `deploy.sh`
hard-requires and both Agent Engine IDs.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PRODUCTION_DIRS = (
    "agents",
    "gateway",
    "identity",
    "registry",
    "runtime",
    "model_armor",
    "observability",
    "infrastructure",
)

# `os.environ["X"]`, `os.environ.get("X")`, and the module-constant form `SOME_VAR = "X"` that
# is later passed to os.environ.get - all three appear in this codebase.
DIRECT = re.compile(r'os\.environ(?:\.get)?\(?\[?\s*"([A-Z][A-Z_0-9]{2,})"')
CONSTANT = re.compile(r'^[A-Z_0-9]*(?:VAR|ENV)[A-Z_0-9]* *= *"([A-Z][A-Z_0-9]{2,})"', re.MULTILINE)
# Only the `${VAR:?}` and `${VAR:-default}` forms read the environment. A bare `${VAR}` is a
# shell local that deploy.sh assigned itself, and treating those as contract entries would
# demand `.env` declare PROJECT_ID, REGION, and every intermediate the script computes.
SHELL = re.compile(r"\$\{([A-Z][A-Z_0-9]{2,}):[?-]")

# Injected by the platform or by deploy.sh itself, never authored by a human in `.env`.
PLATFORM_PROVIDED = {"GOOGLE_APPLICATION_CREDENTIALS", "K_SERVICE", "K_REVISION"}

# Read by the google-genai/ADK libraries rather than by Bastion code, so they appear in no
# source file here while still being required configuration.
LIBRARY_CONSUMED = {"GOOGLE_GENAI_USE_VERTEXAI"}


def declared() -> set[str]:
    """Variables `.env.example` tells a newcomer to set."""
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    return set(re.findall(r"^([A-Z][A-Z_0-9]+)=", text, re.MULTILINE))


def referenced() -> set[str]:
    """Variables the production code and deployment scripts actually read."""
    names: set[str] = set()
    for directory in PRODUCTION_DIRS:
        for path in (ROOT / directory).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            names.update(DIRECT.findall(source))
            names.update(CONSTANT.findall(source))
    for pattern in ("*.sh", "*.ps1"):
        for path in (ROOT / "infrastructure").rglob(pattern):
            names.update(SHELL.findall(path.read_text(encoding="utf-8")))
    return names - PLATFORM_PROVIDED


def test_every_variable_the_code_reads_is_declared_in_the_example():
    """A clean clone must be able to configure the fleet from this file alone."""
    missing = sorted(referenced() - declared())
    assert not missing, f".env.example is missing: {', '.join(missing)}"


def test_the_example_declares_nothing_the_code_ignores():
    """A stale variable is a reader following an instruction that stopped meaning anything."""
    unused = sorted(declared() - referenced() - LIBRARY_CONSUMED)
    assert not unused, f".env.example declares unused variables: {', '.join(unused)}"


def test_no_secret_value_is_committed_in_the_example():
    """Secret ids may live here; secret material may not."""
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith(("BASTION_FINDING_HMAC_KEY", "BASTION_A2A_SHARED_SECRET=")):
            assert line.split("=", 1)[1] == "", f"{line.split('=')[0]} carries a value"


def test_the_example_sources_cleanly_in_a_posix_shell():
    """`deploy.sh` is bash, so an unquoted value with shell syntax silently changes meaning.

    Firestore's default database is literally named `(default)`. Unquoted, bash reads `=(...)`
    as an array assignment and yields `default` — a different database, with no error anywhere.
    """
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        if not name.isupper():
            continue
        unquoted = not (value.startswith('"') and value.endswith('"'))
        assert not (unquoted and any(c in value for c in "()$`&|;<>*?")), (
            f"{name} carries shell-significant characters and must be quoted"
        )
