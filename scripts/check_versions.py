"""Pinned versions agree with the documents, and with the index.

Two different lies are possible about a version, and they need different checks.

The first is **internal drift**: `requirements.txt` pins `google-adk==2.7.0` while a README
badge still reads `ADK-2.6.3`. A judge reads the badge, not the lockfile. This is the same
failure `check_docs.py` exists for — a claim that outran the thing it describes — and it is
checkable without a network, so it runs in CI on every push.

The second is **upstream drift**: the pin itself is stale because a new release landed. That
one needs the index, so it is opt-in (`--check-upstream`) and belongs to the pre-tag sweep
rather than to every push. It has already bitten once: ADK 2.7.0 shipped while every document
in the repository asserted 2.6.3.

**What `--check-upstream` does and does not promise.** Only `TRACKED` packages *fail* the
check, because only those are named in a document a judge reads, so only those can turn into a
false claim. Every other pin is surveyed and reported, never failed — a pin being one patch
behind is not a lie about anything.

That distinction was invisible before `v0.5.2` and cost a real decision: the pre-tag run
reported one problem, the release proceeded on the reading that everything else had been
checked, and eleven other pins were in fact never looked at because the survey did not exist.
A gate that examines five of twenty-three pins must say so out loud, or its silence gets read
as coverage.

Run: python scripts/check_versions.py                 # offline, CI-safe
     python scripts/check_versions.py --check-upstream # queries PyPI, run before a tag
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPI_TIMEOUT_SECONDS = 15

# Packages whose version a judge can see, so a stale one is a visible false claim rather
# than only a lockfile detail. Keys are PyPI names; the patterns are the shapes the docs
# actually use to name them (an ADK badge reads `ADK-2.7.0`, not `google-adk==2.7.0`).
TRACKED: dict[str, tuple[str, ...]] = {
    # No `\b` before ADK: the README badge reads `Google_ADK-2.6.3`, and `_` is a word
    # character, so a word boundary never matches there — which silently exempted the most
    # visible version claim in the repository, the badge a judge actually reads.
    "google-adk": (r"google-adk[=\s]*v?", r"ADK[-_ ]v?"),
    "a2a-sdk": (r"a2a-sdk[=\s]*v?",),
    "google-genai": (r"google-genai[=\s]*v?",),
    "google-cloud-aiplatform": (r"google-cloud-aiplatform[=\s]*v?",),
    "google-cloud-modelarmor": (r"google-cloud-modelarmor[=\s]*v?",),
}

DOC_GLOBS = (
    "*.md",
    "docs/**/*.md",
    "archive/**/*.md",
    "report/*.md",
    "site/*.md",
    "assets/**/*.md",
    "experiments/**/*.md",
    ".github/*.md",
)

# Every file holding exact pins. requirements.txt alone drives the document check, because a
# document names a shipped dependency rather than a linter; the upstream survey reads all of
# them, because staleness is not confined to what the docs happen to mention.
REQUIREMENT_FILES = ("requirements.txt", "requirements-dev.txt", "requirements-media.txt")

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def pinned() -> dict[str, str]:
    """Every exact pin in requirements.txt, as {package: version}.

    Only `==` pins are read. A range is not a claim about a specific version, so there is
    nothing for a document to contradict.
    """
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    found: dict[str, str] = {}
    for line in text.splitlines():
        bare = line.split("#", 1)[0].strip()
        match = re.fullmatch(r"([A-Za-z0-9._-]+)\[?[^\]]*\]?==([0-9][0-9A-Za-z.+-]*)", bare)
        if match:
            found[match.group(1).lower()] = match.group(2)
    return found


def every_pin() -> dict[str, str]:
    """Every exact pin across all requirement files, as {package: version}."""
    found: dict[str, str] = {}
    for name in REQUIREMENT_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            bare = line.split("#", 1)[0].strip()
            match = re.fullmatch(r"([A-Za-z0-9._-]+)\[?[^\]]*\]?==([0-9][0-9A-Za-z.+-]*)", bare)
            if match:
                found[match.group(1).lower()] = match.group(2)
    return found


def doc_files() -> list[Path]:
    seen: dict[Path, None] = {}
    for pattern in DOC_GLOBS:
        for path in ROOT.glob(pattern):
            if ".mypy_cache" not in path.parts:
                seen.setdefault(path, None)
    return sorted(seen)


def check_documents(pins: dict[str, str]) -> None:
    """No document names a tracked package at a version other than the pinned one."""
    for path in doc_files():
        text = path.read_text(encoding="utf-8")
        for package, prefixes in TRACKED.items():
            expected = pins.get(package)
            if expected is None:
                continue
            for prefix in prefixes:
                for match in re.finditer(rf"{prefix}([0-9]+\.[0-9]+\.[0-9]+)", text):
                    if match.group(1) != expected:
                        line = text[: match.start()].count("\n") + 1
                        rel = path.relative_to(ROOT).as_posix()
                        fail(
                            f"{rel}:{line} says {package} {match.group(1)}; "
                            f"requirements.txt pins {expected}"
                        )


def latest_on_pypi(package: str) -> str | None:
    """The newest non-prerelease version on PyPI, or None if the index cannot be reached.

    A network failure is reported as a skip rather than a gate failure: this check is
    advisory about the outside world, and a flaky index must not be able to fail a build
    that is otherwise correct.
    """
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=PYPI_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as problem:
        print(f"  ? {package}: index unreachable ({type(problem).__name__})")
        return None
    version = payload.get("info", {}).get("version")
    return str(version) if version else None


def check_upstream(pins: dict[str, str]) -> None:
    """Tracked pins must be newest; every other pin is surveyed and reported.

    Only a tracked package can fail here. A stale tracked pin contradicts a version printed in
    the README badge or a submission document, which is a false claim; a stale untracked pin is
    only a stale pin, and failing the release for it would make this gate permanently red and
    therefore ignored. The survey exists so the difference is a stated decision rather than an
    unexamined one.
    """
    print("Checking PyPI for newer releases:")
    for package in TRACKED:
        current = pins.get(package)
        if current is None:
            continue
        newest = latest_on_pypi(package)
        if newest is None:
            continue
        if newest != current:
            fail(
                f"requirements.txt pins {package}=={current}; PyPI has {newest}. "
                f"Bump the pin and every document that names it, then re-run."
            )
        else:
            print(f"  OK {package} {current}")

    survey = {name: version for name, version in every_pin().items() if name not in TRACKED}
    behind: list[str] = []
    for package in sorted(survey):
        newest = latest_on_pypi(package)
        if newest is not None and newest != survey[package]:
            behind.append(f"  .. {package} {survey[package]} -> {newest}")

    print(f"\nSurveyed {len(survey)} further pin(s) named in no document:")
    if behind:
        print("\n".join(behind))
        print(
            f"\n{len(behind)} pin(s) behind PyPI. Not a failure and not a false claim — but a "
            "release decision, so decide it rather than inherit it. A production bump also "
            "needs requirements.lock regenerated and, to keep every deployed-and-verified "
            "claim honest, a redeploy of both surfaces."
        )
    else:
        print("  all current")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-upstream",
        action="store_true",
        help="also query PyPI for newer releases (run before tagging)",
    )
    args = parser.parse_args()

    pins = pinned()
    if not pins:
        print("no exact pins found in requirements.txt", file=sys.stderr)
        return 1

    check_documents(pins)
    if args.check_upstream:
        check_upstream(pins)

    if failures:
        print(f"\n{len(failures)} problem(s):", file=sys.stderr)
        for problem in failures:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"\nversions agree across {len(doc_files())} documents and {len(pins)} pins.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
