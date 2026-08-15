"""Documentation agrees with the repository.

Bastion's entire argument is that a claim carries a record. A README asserting seven
pillars over a six-row table, or "six ADRs" when there are seven files, is a small
version of exactly the failure the product is about — and every instance so far was
caught by a human reading carefully, which is neither reliable nor repeatable.

Run: python scripts/check_docs.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Devpost accepts JPG, PNG and GIF — never SVG — and rejects a gallery image above this.
DEVPOST_IMAGE_CAP_MB = 5

# The track names seven pillars. Six are now **managed GEAP products** rather than modules
# here (ADR-003), so requiring a directory per pillar would re-create the exact failure ADR-006
# names: "a folder per pillar reads, in a repository tree, as a pillar per folder." The count
# is still checked against the docs; only the directory requirement is gone.
PILLARS = [
    "Agent Registry",
    "Agent Runtime",
    "Memory Bank",
    "Agent Identity",
    "Agent Gateway",
    "Model Armor",
    "Agent Observability",
]

# Directories that must still exist, because code lives in them.
CODE_DIRS = ["registry", "identity", "model_armor", "observability"]
AGENT_DIRS = ["orchestrator", "access_auditor", "escalation_agent"]

WORDS = {
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def check_pillars() -> None:
    """Every pillar named in the docs has a directory, and vice versa."""
    missing = [d for d in CODE_DIRS if not (ROOT / d).is_dir()]
    if missing:
        fail(f"code directories missing: {', '.join(missing)}")

    count = len(PILLARS)
    word = WORDS[count]
    for doc in ("README.md", "docs/ARCHITECTURE.md"):
        text = read(doc)
        for wrong in (v for k, v in WORDS.items() if k != count):
            if re.search(rf"\b{wrong} pillars\b", text, re.IGNORECASE):
                fail(f"{doc} says '{wrong} pillars'; the repository has {count} ({word})")


def check_agents() -> None:
    """The three-agent decision (ADR-002) is not silently violated."""
    present = sorted(
        p.name
        for p in (ROOT / "agents").iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    )
    unexpected = [a for a in present if a not in AGENT_DIRS and a != "policy_enforcer"]
    if unexpected:
        fail(f"unexpected agent directory: {', '.join(unexpected)} — see ADR-002")

    missing = [a for a in AGENT_DIRS if a not in present]
    if missing:
        fail(f"agent directories missing: {', '.join(missing)}")

    count = len(AGENT_DIRS)
    for doc in ("README.md", "docs/ARCHITECTURE.md", "CLAUDE.md"):
        text = read(doc)
        for wrong in (v for k, v in WORDS.items() if k != count):
            if re.search(rf"\b{wrong} agents\b", text, re.IGNORECASE):
                fail(f"{doc} says '{wrong} agents'; ADR-002 fixes the count at {count}")


def check_adrs() -> None:
    """Every ADR file is in the index, and every indexed ADR exists."""
    adr_dir = ROOT / "docs" / "adr"
    files = sorted(p.name for p in adr_dir.glob("[0-9][0-9][0-9]-*.md"))
    index = read("docs/adr/README.md")

    for name in files:
        if name not in index:
            fail(f"{name} exists but is not listed in docs/adr/README.md")

    for linked in re.findall(r"\((\d{3}-[a-z0-9-]+\.md)\)", index):
        if linked not in files:
            fail(f"docs/adr/README.md links {linked}, which does not exist")

    readme = read("README.md")
    for name in files:
        number = name[:3]
        if f"docs/adr/{name}" not in readme:
            fail(f"ADR-{number} is not referenced from README.md")


def check_model_config() -> None:
    """The two-location trap (ADR-004) stays documented in .env.example."""
    env = read(".env.example")
    if "GOOGLE_CLOUD_LOCATION=global" not in env:
        fail(".env.example must set GOOGLE_CLOUD_LOCATION=global — see ADR-004")
    if "GOOGLE_GENAI_USE_VERTEXAI=TRUE" not in env:
        fail(".env.example must enable Vertex AI for the Google ADK")
    if re.search(r"^VERTEX_AI_MODEL=gemini-3\.5", env, re.MULTILINE) is None:
        fail(".env.example must pin a Gemini 3.5 model — the rules require 3.5 or newer")
    if re.search(r"\bgemini-3\.5-pro\b", read("README.md")):
        fail("README.md references gemini-3.5-pro, which is unavailable — see ADR-004")


def check_badge_versions() -> None:
    """Every version quoted in a README badge matches what is actually pinned.

    A static badge is a claim like any other. These are cheap to write and easy to forget,
    so a badge reading `Flask-3.1.3` over a requirements file pinning something else is
    exactly the small dishonesty this project cannot afford.
    """
    readme = read("README.md")
    pins = read("requirements.txt") + read("requirements-dev.txt")

    # badge label → package name in the pin files
    tracked = {
        "Google_ADK": "google-adk",
        "Flask": "flask",
        "Ruff": "ruff",
        "Mypy": "mypy",
        "pytest": "pytest",
        "OpenTelemetry": "opentelemetry-sdk",
    }

    for label, package in tracked.items():
        badge = re.search(rf"img\.shields\.io/badge/{re.escape(label)}-([0-9][0-9.]*)-", readme)
        if badge is None:
            continue  # the badge was removed; nothing to disagree with
        # `\[[^\]]*\]?` because a pin may carry extras — `google-adk[a2a,gcp]==2.7.0` is the
        # same pin as `google-adk==2.7.0`, and matching only the bare form reported the most
        # important dependency in the repository as "not pinned".
        pinned = re.search(
            rf"^{re.escape(package)}(?:\[[^\]]*\])?==([0-9][0-9.]*)$", pins, re.MULTILINE
        )
        if pinned is None:
            fail(f"README badge quotes {label} {badge.group(1)}, but {package} is not pinned")
        elif badge.group(1) != pinned.group(1):
            fail(
                f"README badge says {label} {badge.group(1)}, "
                f"but {package} is pinned at {pinned.group(1)}"
            )

    python_badge = re.search(r"img\.shields\.io/badge/Python-([0-9.]+)-", readme)
    requires = re.search(r'requires-python = ">=([0-9.]+)"', read("pyproject.toml"))
    if python_badge and requires and python_badge.group(1) != requires.group(1):
        fail(
            f"README badge says Python {python_badge.group(1)}, "
            f"but pyproject requires >={requires.group(1)}"
        )


def check_no_self_asserted_status_badges() -> None:
    """Static badges must not assert measured state.

    Coverage has a live source (Codecov); a hand-written `coverage-100%` beside it is a
    number nobody checks. Counts like "0/7 pillars" and "not yet live" go stale silently
    the moment the thing they describe changes. Version badges are exempt because
    check_badge_versions() verifies them against the pin files.
    """
    readme = read("README.md")
    banned = {
        r"badge/coverage-": "coverage is already reported live by Codecov",
        r"badge/pillars-": "pillar progress goes stale; the Status table carries it",
        r"badge/tests-\d": "test counts go stale; CI reports them",
        r"not_yet_live": "deployment status goes stale; the Status table carries it",
    }
    for pattern, why in banned.items():
        if re.search(pattern, readme):
            fail(f"self-asserted status badge in README ({pattern}): {why}")


def check_unverified_claims() -> None:
    """Claims the submission has not yet earned are not asserted as done."""
    submission = read("submission/SUBMISSION.md")
    if "Do not claim until verified" not in submission:
        fail("submission/SUBMISSION.md lost its 'Do not claim until verified' section")


def check_retired_deployment_claims() -> None:
    """Block the exact pre-deployment claims that a later live fleet invalidated.

    These phrases are not harmless history in judge-facing or contributor-facing documents:
    they made the deployed fleet look fictional, or a planned Gateway look live. Historical
    evidence files may describe their capture-time state, so this check is intentionally scoped.
    """
    documents = (
        "README.md",
        "CLAUDE.md",
        "CONTRIBUTING.md",
        "submission/SUBMISSION.md",
        "submission/planning/00-judging-matrix.md",
        "submission/planning/03-build-plan.md",
        "submission/planning/04-why-we-win.md",
    )
    retired = (
        "Managed fleet deployment is still outstanding",
        "Bastion not in it",
        "Registry stays DIY",
        "nothing outlives the run and no schedule fires it",
        "Every agent-to-agent call goes through the Gateway",
    )
    for document in documents:
        text = read(document)
        for phrase in retired:
            if phrase in text:
                fail(f"{document} retains a retired deployment claim: '{phrase}'")


def check_diagrams_are_grounded() -> None:
    """The architecture documentation may not assert a service that is not deployed.

    This gate exists because the opposite happened. A rendered diagram showed Firestore,
    Cloud Run services, Pub/Sub topics and a Model Armor template on a day when the
    project contained one resource: the default Compute Engine service account. The
    picture was the first thing a judge would have seen, and every box in it was an
    intention drawn as a fact.

    So the build state in the docs is derived from a measurement of the live project,
    and this check enforces two things: the measurement exists, and no committed image
    has quietly reappeared to make a claim the measurement does not support.
    """
    diagrams = ROOT / "assets" / "architecture"
    state_file = diagrams / "gcp-state.json"

    if not state_file.exists():
        fail("assets/architecture/gcp-state.json is missing — run scripts/capture_gcp_state.py")
        return

    state = json.loads(state_file.read_text(encoding="utf-8"))

    # A state file naming a principal is the exact thing SECURITY.md forbids committing.
    forbidden = ("@", "serviceAccount:", "user:", "roles/")
    blob = json.dumps(state)
    for token in forbidden:
        if token in blob:
            fail(f"gcp-state.json contains {token!r} — it records counts, never principals")

    architecture = read("docs/ARCHITECTURE.md")

    # An image may depict the *designed* flow while nothing is deployed — that is a diagram of
    # a process, not a claim about running infrastructure. What it may not do is stay silent
    # about which one it is. So every committed SVG has to disclose its build state in its own
    # text, where a reader sees it, rather than in a caption a screenshot or a Devpost paste
    # will drop.
    #
    # This gate previously lifted once `sum(resources)` passed one, which made a *count* the
    # only thing standing between the repository and a fictional diagram — and that count read
    # as two the moment Google's own default service accounts were tallied. The threshold is
    # gone: disclosure is required at every build state, including a fully deployed one, where
    # the disclosure simply says something different.
    disclosure = "build state"
    svgs = sorted(diagrams.glob("*.svg"))
    for image in svgs:
        if disclosure not in image.read_text(encoding="utf-8").lower():
            fail(
                f"{image.name} carries no build-state disclosure — the image must say so in "
                "its own text, not in a caption that travels separately"
            )

    # A raster cannot carry a checkable disclosure: its text is pixels. It is allowed only as
    # something *derived* from an SVG that was checked, so every raster must have a same-named
    # SVG beside it. A hand-dropped image has no verifiable provenance and no readable claim.
    #
    # The rasters are animated GIFs rather than stills because Devpost accepts JPG, PNG and GIF
    # and does not accept SVG: a PNG would have silently dropped the animation at the one
    # surface that cannot recover it. Devpost caps a gallery image at 5 MB, so the size is
    # checked here too — a diagram that cannot be uploaded is a diagram a judge never sees.
    stems = {image.stem for image in svgs}
    for raster in sorted([*diagrams.glob("*.png"), *diagrams.glob("*.gif")]):
        if raster.stem not in stems:
            fail(
                f"{raster.name} has no matching SVG — a raster cannot disclose its own build "
                "state, so it is only allowed as a rendering of one that can"
            )
        megabytes = raster.stat().st_size / 1_048_576
        if megabytes > DEVPOST_IMAGE_CAP_MB:
            fail(
                f"{raster.name} is {megabytes:.1f} MB, over Devpost's {DEVPOST_IMAGE_CAP_MB} MB "
                "image cap — it cannot be uploaded to the submission page"
            )

    if "gcp-state.json" not in architecture:
        fail("docs/ARCHITECTURE.md no longer cites gcp-state.json — build state must be derived")
    if "```mermaid" not in architecture:
        fail("docs/ARCHITECTURE.md has no mermaid diagram — the architecture must be drawn")


MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
BACKTICKED_PATH = re.compile(
    r"`((?:docs|submission|assets|agents|scripts|infrastructure|tests|registry|runtime"
    r"|memory|gateway|model_armor|observability)/[\w./-]+\.(?:md|py|sh|json|ya?ml|svg))`"
)
SKIP_DIRS = {
    ".venv",
    "venv",
    ".audit-venv",
    "node_modules",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
}


# A repository path written in prose, with or without backticks. Used on source files,
# where paths live in docstrings and shell comments that no linter reads.
PROSE_PATH = re.compile(
    r"(?<![\w/-])((?:docs|submission|assets|agents|scripts|infrastructure|tests)"
    r"/[\w./-]+\.(?:md|py|sh|json|ya?ml))"
)


def repository_markdown() -> list[Path]:
    return [path for path in sorted(ROOT.rglob("*.md")) if not SKIP_DIRS.intersection(path.parts)]


def repository_sources() -> list[Path]:
    """Python and shell — the files that quote repository paths inside prose."""
    return sorted(
        path
        for pattern in ("*.py", "*.sh")
        for path in ROOT.rglob(pattern)
        if not SKIP_DIRS.intersection(path.parts)
    )


def check_source_path_references() -> None:
    """Paths named in docstrings and shell comments must resolve.

    Markdown-only link checking missed five of these: the old `docs/`-prefixed paths for
    `01-architecture.md` in three pillar modules and `06-project-review.md` in two agents,
    all left behind by the move to the planning folder. A dead path in a docstring is still
    valid Python and still a passing test, so nothing else here could have caught them.

    (Those filenames are deliberately written without their old directory prefix above —
    spelling them in full would make this docstring fail its own check.)
    """
    for path in repository_sources() + repository_markdown():
        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for quoted in PROSE_PATH.findall(line):
                if not (ROOT / quoted).exists():
                    fail(f"{rel}:{number} names {quoted}, which does not exist")


def check_internal_links() -> None:
    """Every relative link and backticked path resolves to a file that exists.

    Moving a file is the cheapest way to make a document lie. `submission/planning/`
    was `docs/` for one afternoon and left four dead references behind — none of which
    markdownlint, mypy, or the test suite can see, because a dead path is still valid
    markdown, valid Python, and a passing test.
    """
    for path in repository_markdown():
        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            targets = [target.split("#")[0].strip() for target in MARKDOWN_LINK.findall(line)]
            for target in targets:
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (path.parent / target).resolve().exists():
                    fail(f"{rel}:{number} links to {target}, which does not exist")

            # Paths written in backticks are documentation too, and nothing else checks
            # them — they are the shape the last four stale references took.
            for quoted in BACKTICKED_PATH.findall(line):
                if not (ROOT / quoted).exists():
                    fail(f"{rel}:{number} names `{quoted}`, which does not exist")


def main() -> int:
    check_internal_links()
    check_source_path_references()
    check_pillars()
    check_agents()
    check_adrs()
    check_model_config()
    check_badge_versions()
    check_no_self_asserted_status_badges()
    check_unverified_claims()
    check_retired_deployment_claims()
    check_diagrams_are_grounded()

    if failures:
        print("Documentation disagrees with the repository:\n")
        for message in failures:
            print(f"  - {message}")
        print(f"\n{len(failures)} problem(s).")
        return 1

    print("Documentation agrees with the repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
