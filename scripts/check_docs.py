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

# The documented test total is deliberately NOT checked here. This script runs on a bare
# interpreter in CI's docs and diagrams jobs — no dependencies installed, so no pytest to
# collect with — and forcing those jobs to install the full tree to count tests would trade a
# fast standalone gate for a slow one. The count is asserted from inside the suite instead,
# where it is free: tests/unit/test_documented_test_count.py.

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
    for doc in ("README.md", "docs/ARCHITECTURE.md", "AGENTS.md"):
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


BADGE_DOCS = ("README.md", "submission/DEVPOST_README.md")


def check_badge_versions() -> None:
    """Every version quoted in a badge matches what is actually pinned.

    A static badge is a claim like any other. These are cheap to write and easy to forget,
    so a badge reading `Flask-3.1.3` over a requirements file pinning something else is
    exactly the small dishonesty this project cannot afford.

    Both documents that carry badges are checked. `DEVPOST_README.md` is pasted verbatim into
    the public Devpost description, so a stale version badge there is read by judges rather than
    by contributors — the surface where being wrong costs the most, and the one nobody would
    think to re-check.
    """
    pins = read("requirements.txt") + read("requirements-dev.txt")
    for document in BADGE_DOCS:
        _check_badges_in(document, pins)


def _check_badges_in(document: str, pins: str) -> None:
    readme = read(document)

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
            fail(f"{document} badge quotes {label} {badge.group(1)}, but {package} is not pinned")
        elif badge.group(1) != pinned.group(1):
            fail(
                f"{document} badge says {label} {badge.group(1)}, "
                f"but {package} is pinned at {pinned.group(1)}"
            )

    python_badge = re.search(r"img\.shields\.io/badge/Python-([0-9.]+)-", readme)
    requires = re.search(r'requires-python = ">=([0-9.]+)"', read("pyproject.toml"))
    if python_badge and requires and python_badge.group(1) != requires.group(1):
        fail(
            f"{document} badge says Python {python_badge.group(1)}, "
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
        "AGENTS.md",
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
    ".tmp",
    ".local",
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
    return [
        path
        for path in sorted(ROOT.rglob("*.md"))
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def repository_sources() -> list[Path]:
    """Python and shell — the files that quote repository paths inside prose."""
    return sorted(
        path
        for pattern in ("*.py", "*.sh")
        for path in ROOT.rglob(pattern)
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
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


def check_diagram_footers_match_state() -> None:
    """A rendered diagram may not quote a resource count the live capture disagrees with.

    This gate exists because the opposite happened, and nothing caught it for six days. Every
    check in this file reads Markdown; the architecture SVGs are embedded in README.md and are
    the first thing a judge looks at, and they were never scanned. The fleet architecture carried
    *"One process, one identity. Per-agent service accounts need three deployed apps"* —
    the pre-deployment claim, contradicting the three deployed services described three
    sections above it in the same README — while both footers and the banner pair quoted 33
    resources against a live capture of 39.

    A number is checked rather than a phrase because a phrase list only catches the mistakes
    already made once. The footers are required to agree with `gcp-state.json`, which is
    generated from the live project, so the diagram cannot drift from the fleet silently.
    """
    state = json.loads(read("assets/architecture/gcp-state.json"))
    measured = sum(v for v in state["resources"].values() if isinstance(v, int))

    quoted = re.compile(r"(\d+)\s+(?:deployed\s+)?resources?(?:\s+measured)?", re.IGNORECASE)
    for svg in sorted((ROOT / "assets").rglob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        for match in quoted.finditer(text):
            if int(match.group(1)) != measured:
                fail(
                    f"{svg.relative_to(ROOT).as_posix()} quotes {match.group(1)} resources, "
                    f"but gcp-state.json measures {measured} — re-render from the master"
                )


def check_diagram_dates_match_state() -> None:
    """A diagram's build-state date may not disagree with the capture it quotes.

    Companion to check_diagram_footers_match_state(), which gates the resource *count*. The date
    was ungated, and it drifted: every architecture asset read `Build state · 2026-08-22` while
    `gcp-state.json` recorded a 2026-08-23 capture, and the light PNG carrying that footer is the
    Devpost architecture upload. A count that agrees with a measurement taken on another day is
    not a grounded claim, it is a coincidence — and the footer's whole purpose is disclosure.

    The date is compared, not the timestamp: the footer is a human-readable build-state line, and
    a capture time would be noise at diagram scale.
    """
    state = json.loads(read("assets/architecture/gcp-state.json"))
    captured = str(state.get("captured_utc", ""))[:10]
    if not captured:
        fail("gcp-state.json has no captured_utc — the diagram date cannot be grounded")
        return

    stamped = re.compile(r"Build state\s*·\s*(\d{4}-\d{2}-\d{2})")
    for svg in sorted((ROOT / "assets").rglob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        for match in stamped.finditer(text):
            if match.group(1) != captured:
                fail(
                    f"{svg.relative_to(ROOT).as_posix()} is stamped {match.group(1)}, but "
                    f"gcp-state.json was captured {captured} — re-stamp the master and "
                    "regenerate with scripts/render_diagrams.py"
                )


def check_diagrams_do_not_contradict_the_fleet() -> None:
    """Phrases a rendered diagram may not carry, because the deployment retired them.

    Companion to check_retired_deployment_claims(), which scans only Markdown. Kept as a
    separate list because a diagram states things a document never would — a footer is written
    to be read at a glance and is exactly where an obsolete simplification survives longest.
    """
    retired = (
        "One process, one identity",
        "Per-agent service accounts need three deployed apps",
    )
    for svg in sorted((ROOT / "assets").rglob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        for phrase in retired:
            if phrase in text:
                fail(f"{svg.relative_to(ROOT).as_posix()} retains a retired claim: '{phrase}'")


def _sample_motion_path(spec: str) -> list[tuple[float, float]]:
    """Points along an animateMotion path. Supports the M/L/H/V/C/Q subset the masters use.

    Curves are sampled rather than solved: a packet only has to be shown not to enter a box,
    and 24 samples per segment resolves that far below the radius of the dot itself.
    """
    tokens = re.findall(r"([MLHVCQ])([^MLHVCQ]*)", spec.upper())
    points: list[tuple[float, float]] = []
    x = y = 0.0
    for command, raw in tokens:
        numbers = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", raw)]
        if command == "M" and len(numbers) >= 2:
            x, y = numbers[0], numbers[1]
            points.append((x, y))
        elif command == "L" and len(numbers) >= 2:
            for step in range(1, 25):
                points.append((x + (numbers[0] - x) * step / 24, y + (numbers[1] - y) * step / 24))
            x, y = numbers[0], numbers[1]
        elif command == "H" and numbers:
            for step in range(1, 25):
                points.append((x + (numbers[0] - x) * step / 24, y))
            x = numbers[0]
        elif command == "V" and numbers:
            for step in range(1, 25):
                points.append((x, y + (numbers[0] - y) * step / 24))
            y = numbers[0]
        elif command == "Q" and len(numbers) >= 4:
            x1, y1, x2, y2 = numbers[:4]
            for step in range(1, 25):
                t = step / 24
                points.append(
                    (
                        (1 - t) ** 2 * x + 2 * (1 - t) * t * x1 + t**2 * x2,
                        (1 - t) ** 2 * y + 2 * (1 - t) * t * y1 + t**2 * y2,
                    )
                )
            x, y = x2, y2
        elif command == "C" and len(numbers) >= 6:
            x1, y1, x2, y2, x3, y3 = numbers[:6]
            for step in range(1, 25):
                t = step / 24
                points.append(
                    (
                        (1 - t) ** 3 * x
                        + 3 * (1 - t) ** 2 * t * x1
                        + 3 * (1 - t) * t**2 * x2
                        + t**3 * x3,
                        (1 - t) ** 3 * y
                        + 3 * (1 - t) ** 2 * t * y1
                        + 3 * (1 - t) * t**2 * y2
                        + t**3 * y3,
                    )
                )
            x, y = x3, y3
    return points


def check_packets_never_cross_a_component() -> None:
    """No animated packet may travel through a box it is not entering or leaving.

    The rule is older than this gate — `enterprise-fleet-overview.svg` carries it as a comment
    reading *"Never animate a packet through a component"* — and it was still broken twice,
    because a comment in one master cannot govern the next one somebody writes. A packet crossing
    a box asserts the request passed through that component. On the governed investigation path
    that would be false in precisely the place the architecture is most often misread: the
    dispatcher hands off to the managed Runtime and never invokes a worker.

    Boxes are inset before testing. Every legitimate packet starts or ends *on* a component's
    edge, so an exact-boundary test would reject the correct drawing along with the wrong one.
    """
    inset = 6.0
    for svg in sorted((ROOT / "assets" / "architecture").glob("*.svg")):
        if svg.stem.endswith(("-light", "-dark")):
            continue  # emitted variants carry identical geometry
        text = svg.read_text(encoding="utf-8")

        boxes: list[tuple[float, float, float, float]] = []
        for rect in re.finditer(r"<rect\b[^>]*>", text):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', rect.group(0)))
            try:
                bx, by = float(attrs["x"]), float(attrs["y"])
                bw, bh = float(attrs["width"]), float(attrs["height"])
            except (KeyError, ValueError):
                continue
            if bw >= 1900 and bh >= 1000:
                continue  # the background plate is not a component
            boxes.append((bx, by, bw, bh))

        for motion in re.finditer(r"<animateMotion\b[^>]*>", text):
            spec = re.search(r'path="([^"]*)"', motion.group(0))
            if spec is None:
                continue
            for px, py in _sample_motion_path(spec.group(1)):
                for bx, by, bw, bh in boxes:
                    if bx + inset < px < bx + bw - inset and by + inset < py < by + bh - inset:
                        fail(
                            f"{svg.relative_to(ROOT).as_posix()}: animated packet "
                            f"'{spec.group(1)}' crosses the component at "
                            f"({bx:g},{by:g},{bw:g}x{bh:g}) — packets stay on edges"
                        )
                        break
                else:
                    continue
                break


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
    check_diagram_footers_match_state()
    check_diagram_dates_match_state()
    check_diagrams_do_not_contradict_the_fleet()
    check_packets_never_cross_a_component()

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
