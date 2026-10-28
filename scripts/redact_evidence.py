"""Apply and verify declared masks on Bastion's judge-facing screenshots and videos.

Raw captures under ignored ``.takes/`` are immutable source material. This script touches only
promoted media under ``assets/evidence/screenshots/`` and the archived hackathon gallery and demo
video under ``archive/hackathon-2026/assets/``, which stay public in the repository. Every promoted
PNG or MP4 must be listed below by its repository-relative path, including files that were reviewed
and need no mask.

``assets/evidence/screenshots/`` is covered because it is the likelier place to slip: a supporting
capture is promoted to back a written record rather than to be looked at, so it tends to be copied
from ``.takes/`` verbatim. Two of the first five carried the operator's Google account photo in the
console header, which is exactly the kind of thing nobody re-reads a supporting file to find.

Usage:
    python scripts/redact_evidence.py
    python scripts/redact_evidence.py --check
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
# The hackathon gallery and demo media were archived with the rest of the submission material.
HACKATHON = "archive/hackathon-2026/assets"

SCREENSHOT_GLOBS = (
    f"{HACKATHON}/screenshots/*.png",
    "assets/evidence/screenshots/*.png",
    f"{HACKATHON}/demo-video/*.png",
    f"{HACKATHON}/demo-video/statics/*.png",
)
VIDEO_GLOBS = (f"{HACKATHON}/demo-video/*.mp4", f"{HACKATHON}/demo-video/beats/*.mp4")
VIDEO_SAMPLES = (0.1, 0.5, 0.9)

# A neutral opaque fill makes the removal explicit and survives H.264 chroma subsampling.
PLACEHOLDER = (42, 45, 50)


@dataclass(frozen=True)
class Region:
    """One pixel rectangle to mask; circles are ellipses inscribed in the rectangle."""

    box: tuple[int, int, int, int]
    why: str
    circle: bool = False
    fill: tuple[int, int, int] | None = None


# A file with an empty tuple is explicitly reviewed and deliberately unmasked. Add a declaration
# only after inspecting the final promoted asset at 200% zoom. Never mask an evidence-bearing
# metric, count, timestamp, status, query, trace/investigation id, or other corroborating value.
REDACTIONS: dict[str, tuple[Region, ...]] = {
    # Generated from the dark architecture master. Carries no captured console surface at all,
    # and its build-state footer is gated against gcp-state.json by scripts/check_docs.py.
    f"{HACKATHON}/screenshots/01-enterprise-fleet-architecture.png": (),
    # Agent Registry catalog. Browser chrome, the project-bearing URL, and the signed-in avatar
    # are absent because the promoted copy is cropped from below them, not masked. The reasoning
    # engine id in the Agent ID and Identity columns is the same opaque workload id that
    # assets/evidence/13-current-route-trace.md already retains and cites, so masking it here
    # would contradict a published record without removing the value from the evidence set.
    f"{HACKATHON}/screenshots/02-governed-agent-catalog.png": (),
    # Count-only IAM provenance. Every value shown — binding count, finding count, owning
    # departments, model, worker revisions, investigation id — is published in
    # assets/evidence/11-current-route-correlation.md. The invoking command line was cropped
    # away for legibility, not for safety.
    f"{HACKATHON}/screenshots/03-production-iam-routing.png": (),
    # Agent-mediated Model Armor refusal. The probe text is never printed by the capture script,
    # and the correlation and invocation ids are cited by
    # assets/evidence/12-agent-mediated-model-armor-refusal.md.
    f"{HACKATHON}/screenshots/04-enforced-security-boundary.png": (),
    # --- Supporting captures backing the written evidence records. -------------------------
    # The console header carries the signed-in operator's Google account photo. It is masked
    # rather than cropped so the retained record keeps the same framing as the raw take it cites.
    "assets/evidence/screenshots/07-audit-bucket-retention.png": (
        Region(
            box=(1868, 6, 1909, 47),
            why="signed-in operator account photo in the console header",
            circle=True,
        ),
    ),
    "assets/evidence/screenshots/11-current-route-audit-log.png": (
        Region(
            box=(1868, 6, 1909, 47),
            why="signed-in operator account photo in the console header",
            circle=True,
        ),
    ),
    # Terminal captures with no console header, and the Cloud Trace details panel, which opens
    # over the console and shows no account photo.
    "assets/evidence/screenshots/11-current-route-count-only-summary.png": (),
    "assets/evidence/screenshots/12-agent-mediated-model-armor-refusal.png": (),
    "assets/evidence/screenshots/13-current-route-trace.png": (),
    # Retained audit, retention configuration, and the trace tree. The trace panel stops left of
    # the Service/workload column and expands no span, so no http.url or private worker origin
    # can appear. The audit rows show `"detail":{…}` collapsed, which is the deployed shape
    # rather than an applied mask.
    f"{HACKATHON}/screenshots/05-durable-context-and-audit.png": (),
    # --- Stills the demo video cuts to, promoted from .takes/2026-08-29/. ------------------
    # Codecov coverage. Browser chrome — the tab strip, the project-bearing URL, the signed-in
    # account photo, and the vendor announcement banner — is absent because the promoted copy is
    # cropped from below it, not masked, exactly as gallery image 02 is. Nothing masked: the
    # branch, commit sha, per-module line counts and percentages are the evidence.
    f"{HACKATHON}/demo-video/statics/codecov-coverage.png": (),
    # The repository header, held for five seconds so the project identity registers before the
    # scroll starts. The signed-in header avatar went with the rest of the browser chrome, but two
    # copies of the same photo sit in page content rather than chrome, so they are masked instead.
    # Masking them is a deliberate choice over leaving them: the account is the author's and the
    # repository is public, so this is consistency with the console captures above, not a secret.
    f"{HACKATHON}/demo-video/statics/github-repository-header.png": (
        Region(
            box=(320, 54, 344, 78),
            why="owner account photo beside the repository name",
            circle=True,
        ),
        Region(
            box=(332, 182, 356, 206),
            why="author account photo in the latest-commit row",
            circle=True,
        ),
    ),
    # The README itself, scrolled under the opening narration. Cropped to start below the file
    # tree and the About sidebar, so unlike the header above it contains no commit row and no
    # contributor list — and therefore no account photo to mask. Nothing else here is private:
    # it is the rendered README of a public repository.
    f"{HACKATHON}/demo-video/statics/github-repository.png": (),
}
VIDEO_REDACTIONS: dict[str, tuple[Region, ...]] = {
    # The opening beat, recorded from the live public console by the archived capture_site_hook.mjs.
    # Nothing to mask, and the reason is structural rather than lucky: Playwright records the page
    # viewport, so there is no browser chrome in the frame at all, and it drives a fresh profile,
    # so no account photo, bookmark or open tab exists to leak. Every value on screen is published
    # copy from site/data/site-content.json. Absent on a clean clone, where the gate skips it.
    f"{HACKATHON}/demo-video/beats/00-hook.mp4": (),
    # The finished cut. Nothing to mask, and it inherits rather than assumes that: every frame
    # comes from a source already declared above — the console and terminal captures retained as
    # evidence 11, 12 and 13, the generated architecture and brand masters, the two promoted page
    # captures, and the site recording. The sign-off URLs are drawn from repository-authored text.
    # Reviewed at the beat boundaries as well as the sampled points, because a transition is where
    # an unreviewed frame would hide.
    f"{HACKATHON}/demo-video/bastion.mp4": (),
}


def _tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(f"{name} is not on PATH — install FFmpeg to process judge-facing video")
    return executable


def _run(command: list[str], *, capture_output: bool = False) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(  # noqa: S603 - executables are resolved to absolute trusted paths
        command,
        capture_output=capture_output,
        check=True,
    )


def _duration(path: Path) -> float:
    result = _run(
        [
            _tool("ffprobe"),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
    )
    return float(result.stdout.decode().strip())


def _frame_at(path: Path, seconds: float) -> Image.Image:
    result = _run(
        [
            _tool("ffmpeg"),
            "-v",
            "error",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-",
        ],
        capture_output=True,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def _fill(region: Region) -> tuple[int, int, int]:
    return region.fill or PLACEHOLDER


def _draw(draw: ImageDraw.ImageDraw, region: Region, *, alpha: bool = False) -> None:
    fill: tuple[int, ...] = (*_fill(region), 255) if alpha else _fill(region)
    if region.circle:
        draw.ellipse(region.box, fill=fill)
    else:
        draw.rectangle(region.box, fill=fill)


def _is_masked(image: Image.Image, region: Region, *, tolerance: int = 0) -> bool:
    patch = image.crop(region.box).convert("RGB")
    colours = patch.getcolors(maxcolors=1 << 20)
    if colours is None:
        return False
    expected = _fill(region)
    matching = sum(
        count
        for count, colour in colours
        if max(abs(actual - wanted) for actual, wanted in zip(colour, expected, strict=True))
        <= tolerance
    )
    total = sum(count for count, _ in colours)
    threshold = 0.6 if region.circle else 0.98
    return matching / total > threshold


def _mask_video(path: Path, regions: tuple[Region, ...]) -> None:
    frame = _frame_at(path, 0.0)
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for region in regions:
        _draw(draw, region, alpha=True)

    with tempfile.TemporaryDirectory() as directory:
        mask = Path(directory) / "mask.png"
        output = Path(directory) / path.name
        overlay.save(mask)
        _run(
            [
                _tool("ffmpeg"),
                "-y",
                "-v",
                "error",
                "-i",
                str(path),
                "-i",
                str(mask),
                "-filter_complex",
                "[0:v:0][1:v:0]overlay=0:0[v]",
                "-map",
                "0:a?",
                "-map",
                "[v]",
                "-c:a",
                "copy",
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "16",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        shutil.copyfile(output, path)


def _found(patterns: tuple[str, ...]) -> set[str]:
    return {
        path.relative_to(ROOT).as_posix() for pattern in patterns for path in ROOT.glob(pattern)
    }


def _process_pngs(check_only: bool, missing: list[str], changed: list[str]) -> None:
    for name, regions in REDACTIONS.items():
        path = ROOT / name
        if not path.exists():
            print(f"  [skip] {name} — not present")
            continue
        if not regions:
            print(f"  [none] {name} — reviewed, nothing to mask")
            continue

        image = Image.open(path).convert("RGB")
        draw = ImageDraw.Draw(image)
        touched = False
        for region in regions:
            if _is_masked(image, region):
                continue
            if check_only:
                missing.append(f"{name}: {region.why} at {region.box}")
            else:
                _draw(draw, region)
                touched = True
        if touched:
            image.save(path, format="PNG", optimize=True)
            changed.append(name)
            print(f"  [mask] {name} — {len(regions)} declared region(s)")
        elif not check_only:
            print(f"  [ok  ] {name} — already redacted")


def _process_videos(check_only: bool, missing: list[str], changed: list[str]) -> None:
    for name, regions in VIDEO_REDACTIONS.items():
        path = ROOT / name
        if not path.exists():
            print(f"  [skip] {name} — not present")
            continue
        if not regions:
            print(f"  [none] {name} — reviewed, nothing to mask")
            continue

        duration = _duration(path)
        unmasked = {
            region
            for region in regions
            for ratio in VIDEO_SAMPLES
            if not _is_masked(_frame_at(path, duration * ratio), region, tolerance=6)
        }
        if not unmasked:
            print(f"  [ok  ] {name} — already redacted")
        elif check_only:
            missing.extend(f"{name}: {region.why} at {region.box}" for region in unmasked)
        else:
            _mask_video(path, regions)
            changed.append(name)
            print(f"  [mask] {name} — {len(regions)} declared region(s)")


def apply(check_only: bool) -> int:
    missing: list[str] = []
    changed: list[str] = []
    _process_pngs(check_only, missing, changed)
    _process_videos(check_only, missing, changed)

    undeclared = sorted(
        (_found(SCREENSHOT_GLOBS) - set(REDACTIONS)) | (_found(VIDEO_GLOBS) - set(VIDEO_REDACTIONS))
    )
    if check_only and (missing or undeclared):
        if missing:
            print("Unredacted declared regions:")
            for item in missing:
                print(f"  {item}")
        if undeclared:
            print("Judge-facing files without a reviewed declaration:")
            for item in undeclared:
                print(f"  {item}")
        print("\nDeclare each final asset, then run: python scripts/redact_evidence.py")
        return 1

    if undeclared:
        print("WARNING — undeclared judge-facing files:")
        for item in undeclared:
            print(f"  {item}")
    if check_only:
        print(
            f"Redaction gate passed: {len(REDACTIONS)} PNG(s), "
            f"{len(VIDEO_REDACTIONS)} video(s) declared."
        )
    else:
        print(f"{len(changed)} file(s) modified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on undeclared or unmasked media")
    return apply(parser.parse_args().check)


if __name__ == "__main__":
    raise SystemExit(main())
