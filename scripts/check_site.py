"""Fail closed if the public evidence site drifts or contains sensitive material.

The site is intentionally static, so every deployable byte is available for inspection before
Vercel sees it. This gate checks the full site directory, aligns its evidence timestamp with the
count-only GCP snapshot, and rejects the credential, principal, binding, and private-origin shapes
that are prohibited from judge-facing artifacts.

Run: python scripts/check_site.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
STATE = ROOT / "assets" / "architecture" / "gcp-state.json"
CONTENT = SITE / "data" / "site-content.json"

TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".mjs", ".svg", ".txt", ".xml"}
ALLOWED_HTTPS_HOSTS = {
    "bastion.arjunganesh.dev",
    "github.com",
    "openapi.vercel.sh",
    "player.vimeo.com",
    "www.sitemaps.org",
    "www.youtube-nocookie.com",
}
ALLOWED_HTTP_NAMESPACE_HOSTS = {"www.sitemaps.org", "www.w3.org"}

FORBIDDEN_PATTERNS = {
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "OAuth access token": re.compile(r"ya29\.[0-9A-Za-z_-]+"),
    "JWT-like token": re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential field": re.compile(
        r"[\"']?(?:access_token|client_secret|private_key|refresh_token)[\"']?\s*[:=]",
        re.IGNORECASE,
    ),
    "service-account principal": re.compile(
        r"[a-z0-9._%+-]+@[a-z0-9.-]+\.iam\.gserviceaccount\.com", re.IGNORECASE
    ),
    "raw IAM principal": re.compile(r"\b(?:serviceAccount|user|group|domain):\S+"),
    "raw IAM role": re.compile(r"\broles/[A-Za-z0-9_.]+"),
    "private Cloud Run origin": re.compile(r"https?://[^\s\"'<>]+\.run\.app\b", re.IGNORECASE),
    "private service URL": re.compile(
        r"https?://[^\s\"'<>]*(?:private|internal)[^\s\"'<>]*", re.IGNORECASE
    ),
}

REQUIRED_HEADERS = {
    "Content-Security-Policy",
    "Referrer-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
}

REQUIRED_SECTIONS = {"system", "evidence", "limits", "testing", "video"}
URL_PATTERN = re.compile(r"https?://[^\s\"'<>)}]+")
STATIC_SOURCE_FILES = {
    "404.html",
    "app.js",
    "data/site-content.json",
    "favicon.svg",
    "index.html",
    "robots.txt",
    "sitemap.xml",
    "styles.css",
}


def site_files() -> list[Path]:
    """Return every deployable text file under the static root."""
    return sorted(
        path
        for path in SITE.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES and "dist" not in path.parts
    )


def reviewed_asset_sources() -> tuple[list[Path], list[str]]:
    """Resolve only the reviewed brand/architecture assets named by the site manifest."""
    failures: list[str] = []
    manifest = json.loads((SITE / "asset-manifest.json").read_text(encoding="utf-8"))
    sources: list[Path] = []
    outputs: set[str] = set()
    allowed_roots = {
        (ROOT / "assets" / "brand").resolve(),
        (ROOT / "assets" / "architecture").resolve(),
    }

    for asset in manifest.get("assets", []):
        source = (SITE / asset.get("source", "")).resolve()
        output = asset.get("output", "")
        if source.parent not in allowed_roots:
            failures.append(f"asset source is outside reviewed brand/architecture roots: {source}")
            continue
        if source.suffix not in {".gif", ".svg"} or not source.is_file():
            failures.append(f"reviewed asset source is missing or unsupported: {source}")
            continue
        if output in outputs or not output.startswith("assets/") or ".." in Path(output).parts:
            failures.append(f"asset output is duplicated or unsafe: {output!r}")
            continue
        outputs.add(output)
        if source.suffix in TEXT_SUFFIXES:
            sources.append(source)

    expected = {
        f"assets/{group}/{name}-{theme}.{suffix}"
        for group, name in (
            ("brand", "banner-16x9"),
            ("architecture", "governed-investigation-flow"),
        )
        for theme in ("dark", "light")
        for suffix in ("gif", "svg")
    }
    if outputs != expected:
        failures.append("asset manifest must contain both light/dark GIF and SVG variants")
    return sources, failures


def scan_sensitive_content(paths: list[Path]) -> list[str]:
    """Report secrets, principals, bindings, private origins, and unapproved URL hosts."""
    failures: list[str] = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for name, pattern in FORBIDDEN_PATTERNS.items():
            match = pattern.search(text)
            if match is not None:
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{relative}:{line} contains {name}")

        for match in URL_PATTERN.finditer(text):
            value = match.group(0).rstrip(".,;")
            parsed = urlparse(value)
            if parsed.scheme == "http" and parsed.hostname in ALLOWED_HTTP_NAMESPACE_HOSTS:
                continue
            if parsed.scheme != "https":
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{relative}:{line} uses a non-HTTPS URL")
            elif parsed.hostname not in ALLOWED_HTTPS_HOSTS:
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{relative}:{line} uses unapproved URL host {parsed.hostname!r}")
    return failures


def check_snapshot_alignment() -> list[str]:
    """The displayed verification time must come from the committed count-only capture."""
    failures: list[str] = []
    state = json.loads(STATE.read_text(encoding="utf-8"))
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    captured = state.get("captured_utc")

    if content.get("snapshotSource") != "assets/architecture/gcp-state.json":
        failures.append("site content does not name the sanitized committed snapshot as its source")
    if content.get("verifiedAt") != captured:
        failures.append("site verifiedAt disagrees with gcp-state.json captured_utc")

    index = (SITE / "index.html").read_text(encoding="utf-8")
    if f'datetime="{captured}"' not in index:
        failures.append("site timestamp is not rendered from the captured_utc value")
    return failures


def check_static_contract() -> list[str]:
    """Verify required pages, sections, metadata, and strict Vercel browser headers."""
    failures: list[str] = []
    required_files = {
        "index.html",
        "404.html",
        "app.js",
        "asset-manifest.json",
        "build.mjs",
        "styles.css",
        "favicon.svg",
        "robots.txt",
        "sitemap.xml",
        "vercel.json",
    }
    missing = sorted(name for name in required_files if not (SITE / name).is_file())
    if missing:
        failures.append(f"site files missing: {', '.join(missing)}")

    index = (SITE / "index.html").read_text(encoding="utf-8")
    missing_sections = sorted(
        section for section in REQUIRED_SECTIONS if f'id="{section}"' not in index
    )
    if missing_sections:
        failures.append(f"judge-facing sections missing: {', '.join(missing_sections)}")
    if "Public evidence console" not in index or "IAM-private on Google Cloud" not in index:
        failures.append(
            "opening page does not separate the public evidence and private operational planes"
        )
    if '<link rel="canonical" href="https://bastion.arjunganesh.dev">' not in index:
        failures.append("canonical production URL metadata is missing")
    for marker in (
        "data-theme-toggle",
        "data-light-gif",
        "data-dark-gif",
        "data-light-static",
        "data-dark-static",
    ):
        if marker not in index:
            failures.append(f"theme-aware asset marker missing: {marker}")

    config = json.loads((SITE / "vercel.json").read_text(encoding="utf-8"))
    if config.get("buildCommand") != "node build.mjs" or config.get("outputDirectory") != "dist":
        failures.append("Vercel must build the allowlisted static dist output")
    global_rules = [rule for rule in config.get("headers", []) if rule.get("source") == "/(.*)"]
    if len(global_rules) != 1:
        failures.append("vercel.json must contain exactly one global header rule")
    else:
        present = {header.get("key") for header in global_rules[0].get("headers", [])}
        missing_headers = sorted(REQUIRED_HEADERS - present)
        if missing_headers:
            failures.append(f"security headers missing: {', '.join(missing_headers)}")

        csp = next(
            (
                header.get("value", "")
                for header in global_rules[0].get("headers", [])
                if header.get("key") == "Content-Security-Policy"
            ),
            "",
        )
        for directive in ("default-src 'none'", "frame-ancestors 'none'", "object-src 'none'"):
            if directive not in csp:
                failures.append(f"Content-Security-Policy is missing {directive!r}")
    return failures


def check_built_output() -> list[str]:
    """When a local build exists, require an exact allowlisted static bundle."""
    output_root = SITE / "dist"
    if not output_root.is_dir():
        return []

    failures: list[str] = []
    manifest = json.loads((SITE / "asset-manifest.json").read_text(encoding="utf-8"))
    asset_map = {
        asset["output"]: (SITE / asset["source"]).resolve() for asset in manifest["assets"]
    }
    expected = STATIC_SOURCE_FILES | set(asset_map)
    actual = {
        path.relative_to(output_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            failures.append(f"static build files missing: {', '.join(missing)}")
        if unexpected:
            failures.append(f"static build contains unexpected files: {', '.join(unexpected)}")

    for relative in sorted(STATIC_SOURCE_FILES):
        if (output_root / relative).is_file() and (output_root / relative).read_bytes() != (
            SITE / relative
        ).read_bytes():
            failures.append(f"static build drifted from site source: {relative}")
    for relative, source in asset_map.items():
        if (output_root / relative).is_file() and (
            output_root / relative
        ).read_bytes() != source.read_bytes():
            failures.append(f"static build drifted from reviewed asset: {relative}")
    return failures


def main() -> int:
    """Run the public-site safety gate."""
    if not SITE.is_dir():
        print("Public site safety gate failed:\n\n  - site/ does not exist")
        return 1

    reviewed_assets, manifest_failures = reviewed_asset_sources()
    failures = [
        *scan_sensitive_content([*site_files(), *reviewed_assets]),
        *manifest_failures,
        *check_snapshot_alignment(),
        *check_static_contract(),
        *check_built_output(),
    ]
    if failures:
        print("Public site safety gate failed:\n")
        for failure in failures:
            print(f"  - {failure}")
        print(f"\n{len(failures)} problem(s).")
        return 1

    print("Public site is snapshot-aligned and contains no prohibited data shapes or origins.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
