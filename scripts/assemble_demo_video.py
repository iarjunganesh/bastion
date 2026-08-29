"""Assemble the demo video from the committed narration and per-beat footage.

**The cut is defined by the audio, not by the editor.** Each beat's on-screen duration is the
measured length of its committed narration clip plus the deliberate hold declared beside the words
in `scripts/generate_demo_voiceover.py`. That module is imported here rather than re-described, so
a wording change cannot silently desynchronise the picture from the sound: re-run the voiceover
generator, re-run this, and the timeline follows.

Each beat resolves its picture in this order:

1. ``assets/demo-video/beats/<NN>-<slug>.mp4`` — a screen recording, if one exists for that beat.
2. the shots declared in ``PICTURES`` below. A beat may hold several: a still, a looped animated
   master, or a vertical scroll across a tall page capture.

**Both are finished pictures.** The declared shots are the redacted console and terminal captures
retained as evidence 11, 12 and 13 — real output from real deployed runs, not stand-ins — so the
narration says the cut was *captured from the deployed fleet* rather than claiming it happens live
on camera. An earlier version claimed the latter, which turned every unrecorded beat into a blocker
and made the master filename unreachable; the wording was the constraint, not the pictures.

A beat can still be upgraded by dropping a recording into ``beats/``, which simply takes precedence.
``Shot.final`` marks a shot as the intended finished picture; set it False to have ``--check`` flag
that beat as still wanting footage.

Usage:
    python scripts/assemble_demo_video.py --check          # what is live, what is still, runtime
    python scripts/assemble_demo_video.py                  # render assets/demo-video/bastion.mp4
    python scripts/assemble_demo_video.py --burn-captions  # hard-subtitle the render
    python scripts/assemble_demo_video.py --beat iam       # re-render one beat's segment only
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_demo_voiceover import (  # noqa: E402
    NARRATION,
    ROOT,
    Beat,
    clip_path,
    duration,
    split_sentences,
)

VIDEO_DIR = ROOT / "assets" / "demo-video"
BEATS_DIR = VIDEO_DIR / "beats"
BUILD_DIR = VIDEO_DIR / "build"
MASTER = VIDEO_DIR / "bastion.mp4"
SRT = VIDEO_DIR / "bastion.srt"

WIDTH, HEIGHT, FPS = 1920, 1080, 30

# Cross-dissolve between beats, and open and close on black. Eight of the twelve beats are static
# console captures, so with hard cuts the middle of the cut reads as a slideshow; a short dissolve
# is what makes a sequence of stills feel authored. Every segment after the first is rendered
# XFADE longer than its beat so the overlap consumes the extra rather than shortening the film —
# without that compensation twelve transitions would pull the picture 4.8s ahead of the narration.
XFADE = 0.4
FADE_IN = 0.6
FADE_OUT = 0.8


@dataclass(frozen=True)
class Shot:
    """One picture inside a beat.

    ``kind`` selects how the source becomes motion: a ``still`` is held, a ``gif`` is looped, and
    a ``scroll`` pans a tall page image top to bottom across its whole slot. ``seconds`` pins a
    shot's length; the last shot in a beat leaves it ``None`` and absorbs whatever remains, so a
    beat always sums to exactly its narration plus hold no matter how the earlier shots are cut.
    """

    source: str
    kind: str = "still"
    seconds: float | None = None
    # True when this shot is the intended finished picture rather than a stand-in for footage not
    # yet recorded. The closing beats are graphics by design and will never have a live take, so
    # without this the completeness check could never pass and the master filename would be
    # unreachable no matter how much was recorded.
    final: bool = False


# What a beat shows when it has no live take. Every source is an already-reviewed asset that
# passes `scripts/redact_evidence.py --check`; nothing enters a frame the redaction gate has not
# cleared. The two page captures were promoted out of `.takes/2026-08-29/` with their browser
# chrome cropped away and the remaining account photos masked, per the runbook in
# `assets/screenshots/README.md`.
PICTURES: dict[str, tuple[Shot, ...]] = {
    # The repository header is held just long enough to register the project identity — name,
    # commit count, releases, deployments — and the pan then starts at the README banner rather
    # than the file tree. Scrolling a directory listing was the first attempt and wasted the most
    # valuable twelve seconds in the cut on the least compelling thing on the page.
    "hook": (
        Shot("demo-video/statics/github-repository-header.png", "still", 5.0, final=True),
        Shot("demo-video/statics/github-repository.png", "scroll", final=True),
    ),
    # The investigation-flow master, animated: Pub/Sub opens it, Eventarc delivers with a
    # five-attempt dead letter, and Cloud Run admits it with inbox, lease, retry and dedup —
    # which is this beat's narration almost word for word.
    "event": (Shot("architecture/governed-investigation-flow-dark.gif", "gif", final=True),),
    "iam": (Shot("evidence/screenshots/11-current-route-count-only-summary.png", final=True),),
    "model": (Shot("screenshots/03-production-iam-routing.png", final=True),),
    # Deliberately not the same picture as `model`: the two beats ran back to back on one
    # identical frame for forty seconds, the longest static stretch in the cut. This shows the
    # escalation_agent and escalation_gate events completing, which is this beat's receipt.
    "deliver": (Shot("evidence/screenshots/11-current-route-audit-log.png", final=True),),
    "memory": (Shot("screenshots/05-durable-context-and-audit.png", final=True),),
    "identity": (Shot("screenshots/04-enforced-security-boundary.png", final=True),),
    "armor": (Shot("evidence/screenshots/12-agent-mediated-model-armor-refusal.png", final=True),),
    "audit": (Shot("evidence/screenshots/13-current-route-trace.png", final=True),),
    "cloud": (Shot("screenshots/02-governed-agent-catalog.png", final=True),),
    # The animated architecture master carries flow dots along the request path, so the close
    # moves rather than freezes; it then cuts to the coverage report on the same commit while the
    # narration reaches "a proof boundary in the public repository". The coverage page is shown
    # and never spoken to: 100% is evidence of test discipline, and this project's own upstream
    # finding is the standing proof that it is not evidence of correctness.
    "close": (
        Shot("architecture/enterprise-fleet-architecture-dark.gif", "gif", 13.0, final=True),
        Shot("demo-video/statics/codecov-coverage.png", final=True),
    ),
    # The animated brand master, with the two URLs a judge might type composited over it at render
    # time. A flat text card was built first and worked, but the banner is the project's own hero
    # — shield, orbiting control plane, live fleet counters — and it already exists at 1920x1080
    # because render_diagrams.py covers assets/brand. The overlay lands in the empty band under
    # the banner's own stats row, so the hand-reviewed SVG is never edited: only the video frame
    # carries the addition, and the narration says the thanks the picture then does not repeat.
    "thanks": (Shot("brand/banner-16x9-dark.gif", "signoff", final=True),),
}

SIGNOFF_URLS = "github.com/iarjunganesh/bastion   ·   bastion.arjunganesh.dev"
SIGNOFF_FONTS = ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf")


def tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(f"{name} is not on PATH — install FFmpeg to assemble the demo video")
    return executable


def run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True)  # noqa: S603
    if result.returncode != 0:
        tail = result.stderr.decode("utf-8", "replace").strip().splitlines()[-15:]
        raise SystemExit("\n".join([f"command failed: {Path(command[0]).name}", *tail]))


def beat_seconds(index: int, beat: Beat) -> float:
    """On-screen time: the measured narration plus the declared hold."""
    return duration(clip_path(index, beat)) + beat.hold


def live_take(index: int, beat: Beat) -> Path | None:
    path = BEATS_DIR / f"{index:02d}-{beat.slug}.mp4"
    return path if path.exists() else None


def is_finished(index: int, beat: Beat) -> bool:
    """A beat is finished when it has a live take, or when its shots are all final by design."""
    return live_take(index, beat) is not None or all(shot.final for shot in PICTURES[beat.slug])


def shots_for(beat: Beat, seconds: float) -> list[tuple[Shot, float]]:
    """Resolve a beat's shots to concrete lengths, the last one absorbing the remainder."""
    shots = PICTURES[beat.slug]
    pinned = sum(shot.seconds or 0.0 for shot in shots[:-1])
    remainder = seconds - pinned
    if remainder <= 0:
        raise SystemExit(
            f"{beat.slug}: pinned shots total {pinned:.1f}s but the beat is only {seconds:.1f}s"
        )
    return [*((shot, shot.seconds or 0.0) for shot in shots[:-1]), (shots[-1], remainder)]


def source_of(shot: Shot) -> Path:
    return ROOT / "assets" / shot.source


def render_still(source: Path, seconds: float, out: Path) -> None:
    """Hold a placeholder frame, pixel-exact.

    Deliberately motionless. A slow Ken Burns push was tried first and rejected: ``zoompan``
    driven off a ``-loop 1`` input advances ``on`` per emitted frame, so the zoom raced well past
    its 1.05 ceiling and cropped the left edge — on a terminal capture that silently amputates the
    very counts the narration is citing. A sharp, uncropped, legible frame beats a moving one, and
    the motion that matters belongs to the live takes anyway.
    """
    fit = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,format=yuv420p"
    )
    run(
        [
            tool("ffmpeg"),
            "-y",
            "-loop",
            "1",
            "-i",
            str(source),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            fit,
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def render_signoff(source: Path, seconds: float, out: Path) -> None:
    """Loop the brand banner with the repository and console URLs drawn over it.

    Composited here rather than added to the SVG because `assets/brand/` is hand-reviewed artwork
    and the banner pair has to stay visually aligned; a URL line belongs to this one video, not to
    every surface the banner appears on. It sits in the clear band below the banner's own stats
    row, in the same typographic voice, so it reads as one more measured fact rather than a caption
    stuck on afterwards.
    """
    font = next((name for name in SIGNOFF_FONTS if Path(name).exists()), None)
    if font is None:
        raise SystemExit(f"no sign-off font found; looked for {', '.join(SIGNOFF_FONTS)}")

    # drawtext parses ':' as its own option separator, so a Windows drive letter must be escaped.
    escaped = font.replace(":", r"\:")
    fit = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={FPS},"
        f"drawtext=fontfile='{escaped}':text='{SIGNOFF_URLS}':fontsize=30:"
        f"fontcolor=0xC9D6E8:x=(w-text_w)/2:y=1030,"
        f"format=yuv420p"
    )
    run(
        [
            tool("ffmpeg"),
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(source),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            fit,
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def render_gif(source: Path, seconds: float, out: Path) -> None:
    """Loop an animated master for the length of its slot.

    The architecture GIFs run 6s of flow dots travelling the request path, which loops cleanly
    because the motion is continuous traffic rather than a build-up with a beginning and an end.
    """
    fit = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={FPS},format=yuv420p"
    )
    run(
        [
            tool("ffmpeg"),
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(source),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            fit,
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def render_scroll(source: Path, seconds: float, out: Path) -> None:
    """Pan a tall page capture from its top edge to its bottom across the whole slot.

    Only crop's y offset varies with time; the output stays a fixed 1920x1080. Animating a crop's
    width or height instead would change the frame size mid-stream, which downstream filters
    handle badly — this is the same class of mistake as the zoompan crop recorded in
    ``render_still``.
    """
    travel = f"(ih-oh)*min(t/{seconds:.3f},1)"
    pan = f"scale={WIDTH}:-2,crop={WIDTH}:{HEIGHT}:0:'{travel}',setsar=1,format=yuv420p"
    run(
        [
            tool("ffmpeg"),
            "-y",
            "-loop",
            "1",
            "-i",
            str(source),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            pan,
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def render_take(source: Path, seconds: float, out: Path) -> None:
    """Fit a live take to its beat: trim if long, hold the final frame if short."""
    fit = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,tpad=stop_mode=clone:stop_duration=600,format=yuv420p"
    )
    run(
        [
            tool("ffmpeg"),
            "-y",
            "-i",
            str(source),
            "-vf",
            fit,
            "-t",
            f"{seconds:.3f}",
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def render_audio(out: Path) -> None:
    """Narration then hold, beat by beat, concatenated into one master track."""
    inputs: list[str] = []
    filters: list[str] = []
    labels: list[str] = []
    for index, beat in enumerate(NARRATION):
        inputs += ["-i", str(clip_path(index, beat))]
        filters.append(
            f"[{index}:a]aresample=48000,"
            f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"apad=pad_dur={beat.hold:.3f}[a{index}]"
        )
        labels.append(f"[a{index}]")
    graph = ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(NARRATION)}:v=0:a=1[out]"
    run(
        [
            tool("ffmpeg"),
            "-y",
            *inputs,
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(out),
        ]
    )


RENDERERS = {
    "still": render_still,
    "gif": render_gif,
    "scroll": render_scroll,
    "signoff": render_signoff,
}


def segments(only: str | None) -> tuple[list[Path], int]:
    """Render every segment in order and return their paths plus the count of finished beats."""
    paths: list[Path] = []
    live = 0
    # The surplus is per *segment*, not per beat. A beat holding two shots contributes two
    # segments and therefore two dissolves, so compensating once per beat leaves the seam inside
    # it uncovered and the picture finishes a transition short of the narration.
    for index, beat in enumerate(NARRATION):
        take = live_take(index, beat)
        seconds = beat_seconds(index, beat)
        wanted = only is None or only == beat.slug
        live += is_finished(index, beat)
        if take is not None:
            out = BUILD_DIR / f"{index:02d}-{beat.slug}.mp4"
            if wanted:
                render_take(take, seconds + (XFADE if paths else 0.0), out)
            paths.append(out)
            continue
        for position, (shot, length) in enumerate(shots_for(beat, seconds)):
            out = BUILD_DIR / f"{index:02d}-{beat.slug}-{position}.mp4"
            if wanted:
                RENDERERS[shot.kind](source_of(shot), length + (XFADE if paths else 0.0), out)
            paths.append(out)
    return paths, live


def render_picture(paths: list[Path], out: Path) -> None:
    """Join every segment with a cross-dissolve, opening and closing on black.

    Chained rather than concatenated, because a dissolve has to overlap two clips. Each transition
    consumes ``XFADE`` from the running stream, which is exactly the surplus `segments` rendered
    into every clip after the first, so the joined picture lands on the narration's own length
    instead of drifting a transition earlier at every seam.
    """
    inputs: list[str] = []
    for path in paths:
        inputs += ["-i", str(path)]

    steps: list[str] = []
    label = "0:v"
    running = duration(paths[0])
    for index in range(1, len(paths)):
        nxt = "out" if index == len(paths) - 1 else f"v{index}"
        steps.append(
            f"[{label}][{index}:v]xfade=transition=fade:duration={XFADE}"
            f":offset={running - XFADE:.3f}[{nxt}]"
        )
        label = nxt
        running += duration(paths[index]) - XFADE

    steps.append(
        f"[{label}]fade=t=in:st=0:d={FADE_IN},"
        f"fade=t=out:st={running - FADE_OUT:.3f}:d={FADE_OUT},format=yuv420p[picture]"
    )
    run(
        [
            tool("ffmpeg"),
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(steps),
            "-map",
            "[picture]",
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            str(out),
        ]
    )


def prune(paths: list[Path]) -> None:
    """Delete build files no longer named by the current plan.

    Changing a beat's shots renames its segments — a single `01-event.mp4` becomes `01-event-0.mp4`,
    a two-shot beat gains `-1`, a beat that turns into a live take loses its numbered parts. The
    old files are inert, because the concat list is written from the plan rather than from a
    directory listing, but leaving them makes the build directory an unreliable record of what the
    cut currently is. That is exactly the drift this whole pipeline exists to prevent, so the
    directory is reconciled on every run instead of being allowed to accumulate.
    """
    keep = {path.name for path in paths} | {
        "narration.m4a",
        "picture.mp4",
        "bastion-scaffold.mp4",
    }
    for stale in sorted(BUILD_DIR.iterdir()):
        if stale.is_file() and stale.name not in keep:
            stale.unlink()
            print(f"  pruned stale build file {stale.name}")


def timecode(seconds: float) -> str:
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def check() -> int:
    total = 0.0
    outstanding: list[str] = []
    print(f"{'beat':<10} {'source':<8} {'len':>7}  {'ends':>5}  picture")
    for index, beat in enumerate(NARRATION):
        take = live_take(index, beat)
        seconds = beat_seconds(index, beat)
        total += seconds
        if take is not None:
            picture = take.relative_to(ROOT).as_posix()
            print(f"{beat.slug:<10} {'LIVE':<8} {seconds:>6.1f}s  {timecode(total):>5}  {picture}")
            continue
        if not is_finished(index, beat):
            outstanding.append(f"{index:02d}-{beat.slug}")
        for position, (shot, length) in enumerate(shots_for(beat, seconds)):
            label = beat.slug if position == 0 else ""
            ends = timecode(total) if position == len(PICTURES[beat.slug]) - 1 else ""
            kind = shot.kind if shot.final else f"{shot.kind}*"
            print(f"{label:<10} {kind:<8} {length:>6.1f}s  {ends:>5}  {shot.source}")
    print(f"\nTotal {timecode(total)} ({total:.1f}s) across {len(NARRATION)} beats.")
    print("A * marks a placeholder standing in for footage that has not been recorded.")
    if outstanding:
        print(
            f"\n{len(outstanding)} of {len(NARRATION)} beats still need a live take:\n"
            f"  {', '.join(outstanding)}\n"
            "This build is a timing scaffold, not the submission: the hook narration promises\n"
            "live footage. Record into assets/demo-video/beats/<NN>-<slug>.mp4 to replace them."
        )
        return 1
    print("\nEvery beat is finished — recorded, or final by design.")
    return 0


def check_captions() -> None:
    """Fail unless `bastion.srt` was generated from the narration this render is cutting.

    The sidecar is written by generate_demo_voiceover.py and the picture by this script, and
    nothing forced them to agree: editing a beat's `hold` changes the beat clock here and in the
    audio, but leaves an already-written SRT describing the old clock. That shipped once — the
    hook's hold went 3.0 -> 1.0 and the SRT was not regenerated, so every cue after the hook sat
    2.0s late. It survived review because the drift is invisible on a thirteen-second cue and
    obvious only on the shortest: "Thank you for watching" was captioned a half-second *after* the
    words had finished, ending past the end of the video.

    So check the one invariant that ties the two together — a beat's first cue starts when the
    beat starts. Cue boundaries *inside* a beat come from per-sentence probe clips this script
    never sees, and are not checked; the cumulative clock is what drifts, and it is enough.
    """
    if not SRT.exists():
        raise SystemExit(f"{SRT.relative_to(ROOT).as_posix()} is missing; run make voiceover")
    blocks = [b for b in SRT.read_text(encoding="utf-8").strip().split("\n\n") if b.strip()]
    starts: list[float] = []
    for block in blocks:
        opening = block.split("\n")[1].split(" --> ")[0]
        hours, minutes, rest = opening.split(":")
        whole, millis = rest.split(",")
        starts.append(int(hours) * 3600 + int(minutes) * 60 + int(whole) + int(millis) / 1000)

    cue = 0
    clock = 0.0
    for index, beat in enumerate(NARRATION):
        lines = len(split_sentences(beat.text))
        if cue >= len(starts):
            raise SystemExit(f"{SRT.name} has no cue for {beat.slug}; regenerate it")
        # A quarter of a second is looser than any rounding this pipeline produces and far tighter
        # than a drift a viewer would notice, so it catches the stale sidecar without tripping on
        # the millisecond timestamps.
        if abs(starts[cue] - clock) > 0.25:
            raise SystemExit(
                f"{SRT.relative_to(ROOT).as_posix()} is stale: beat {index:02d}-{beat.slug} "
                f"starts at {clock:.3f}s but its first cue is at {starts[cue]:.3f}s "
                f"({starts[cue] - clock:+.3f}s). Re-run generate_demo_voiceover.py."
            )
        cue += lines
        clock += beat_seconds(index, beat)
    if cue != len(starts):
        raise SystemExit(f"{SRT.name} has {len(starts)} cues; the narration has {cue}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble the Bastion demo video.")
    parser.add_argument("--check", action="store_true", help="report the plan without rendering")
    parser.add_argument("--beat", help="re-render only this beat's segment")
    parser.add_argument("--burn-captions", action="store_true", help="hard-subtitle the render")
    args = parser.parse_args()

    if args.check:
        check_captions()
        return check()

    # Before rendering, not after: a mismatched sidecar means the words on screen and the words
    # in the ear describe different clocks, and that is not something to discover in a re-watch.
    check_captions()

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    paths, live = segments(args.beat)
    prune(paths)

    audio = BUILD_DIR / "narration.m4a"
    render_audio(audio)

    silent = BUILD_DIR / "picture.mp4"
    render_picture(paths, silent)

    mux = [tool("ffmpeg"), "-y", "-i", str(silent), "-i", str(audio)]
    if args.burn_captions:
        # libass renders a converted SRT against a 288px-tall reference, so every size here is in
        # that space and lands on screen multiplied by 1080/288 = 3.75. FontSize=12 is therefore
        # about 45px at 1080p; the repo's first attempt used 18 and produced 67px captions that
        # covered the architecture diagram. BorderStyle=3 puts the text in an opaque box so it
        # stays readable over a bright console panel as well as a dark still.
        style = (
            "FontName=Arial,FontSize=12,Bold=1,BorderStyle=3,Outline=1,Shadow=0,"
            "BackColour=&H99000000,MarginV=24,MarginL=120,MarginR=120"
        )
        srt = SRT.as_posix().replace(":", "\\:")
        mux += [
            "-vf",
            f"subtitles='{srt}':force_style='{style}'",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
        ]
    else:
        mux += ["-c:v", "copy"]
    # The master path is earned, not chosen. `assets/demo-video/bastion.mp4` sits inside the
    # redaction gate's VIDEO_GLOBS, so anything written there must be declared in VIDEO_REDACTIONS
    # and frame-reviewed before the offline gate goes green again. A scaffold has not been reviewed
    # and is not the submission, so it stays in the ignored build directory where it cannot be
    # mistaken for the final cut or quietly uploaded.
    scaffold = live < len(NARRATION)
    out = (BUILD_DIR / "bastion-scaffold.mp4") if scaffold else MASTER
    mux += ["-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)]
    run(mux)

    length = duration(out)
    print(
        f"Wrote {out.relative_to(ROOT).as_posix()} — {timecode(length)} ({length:.1f}s), "
        f"{live}/{len(NARRATION)} beats finished."
    )
    if scaffold:
        print(
            "Scaffold build — rehearsal and timing only, not the submission. See --check.\n"
            "The reviewed cut is written to assets/demo-video/bastion.mp4 once every beat is live."
        )
    else:
        print(
            "Every beat is finished. Declare this file in VIDEO_REDACTIONS and run\n"
            "`python scripts/redact_evidence.py --check` before it goes anywhere public."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
