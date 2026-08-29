"""Demo narration: text, audio, measured durations, and captions.

**This file is the source of truth for the narration.** The shot table in
`submission/DEMO_SCRIPT.md`, the MP3s under `assets/demo-voiceover/`, and the caption track are
all generated from ``NARRATION`` below. Edit the words here, re-run, and paste the emitted table
back into the shooting script. Editing the table in the doc instead is how a script and its
committed audio drift apart, which is worse than either being wrong alone: the recording session
trusts the doc and the timeline trusts the audio.

Synthesised with **Google Cloud Text-to-Speech** (Chirp3-HD) rather than a third-party service —
the same project as the rest of the fleet, and one less vendor in a submission whose whole claim
is that it runs on the sponsor's stack. Devpost permits AI narration explicitly. A full
regeneration costs well under a dollar at Chirp3-HD rates, billed per character.

**How the caption timings are obtained, precisely.** Chirp3-HD accepts SSML but this client
exposes no timepointing, so there are no speech marks to cut cues from. Each beat is therefore
synthesised **once, continuously**, which is what the viewer hears and what keeps prosody natural
across a sentence boundary. Every sentence is then synthesised again on its own purely to be
measured, and those real per-sentence durations are scaled to the beat clip's measured length.
So a cue boundary is a *measurement scaled by a measured ratio*, never a word-count estimate —
but it is a scaled measurement, not a direct one, and it is written down here rather than implied.

Narration wording is bounded by `submission/planning/11-claim-matrix.md`. Every sentence below
must be defensible against a row in that matrix; the two `Partial` rows — managed Gateway refusal
and retry/dead-letter — are deliberately absent from the script entirely rather than narrowed.

Usage:
    python scripts/generate_demo_voiceover.py             # synthesise every clip, then captions
    python scripts/generate_demo_voiceover.py --table     # measure existing clips, print the table
    python scripts/generate_demo_voiceover.py --clip hook # re-do one beat after a wording change
    python scripts/generate_demo_voiceover.py --audition  # one line in every candidate voice
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "demo-voiceover"
SRT_PATH = ROOT / "assets" / "demo-video" / "bastion.srt"

VOICE = "en-US-Chirp3-HD-Kore"
LANGUAGE = "en-US"
AUDITION_VOICES = ("Kore", "Aoede", "Zephyr", "Autonoe", "Sulafat", "Leda")

# The brief's hard ceiling is four minutes and judges have said they stop at it, so the cut is
# built to land here with room for a render that comes out a second long. The window moved from
# 225-230s when the closing sign-off was added: three seconds bought a warm ending and still
# leaves seven in hand, which is a deliberate trade rather than drift. Widen it again only for a
# reason worth writing down, and never past the ceiling.
TARGET_LOW, TARGET_HIGH = 230.0, 236.0


@dataclass(frozen=True)
class Beat:
    """One shot: what is on screen, and what is said over it."""

    slug: str
    screen: str
    text: str
    # Spoken variant where an acronym or version number must not be read as a word.
    spoken: str | None = None
    # Seconds of deliberate silence after the narration, while the viewer watches a live step.
    hold: float = 0.0
    sentences: list[str] = field(default_factory=list)

    def to_speak(self) -> str:
        return self.spoken or self.text


NARRATION: list[Beat] = [
    Beat(
        "hook",
        "The live public evidence console, scrolled: the hero claim, the fleet counters, the "
        "governed production-data path, and the remembered human decision",
        "Enterprise permissions change every day. Access reviews don't. Bastion is a fleet of "
        "three governed agents that audits the Google Cloud project it runs inside — reading "
        "production IAM read-only. It can ask a human to review a permission. It cannot change "
        "one. It's deployed on Google's managed agent stack, not a local script — and building "
        "it there surfaced a real defect in Google's own ADK, which we reported upstream. "
        "Everything after this was captured from the deployed fleet.",
        "Enterprise permissions change every day. Access reviews don't. Bastion is a fleet of "
        "three governed agents that audits the Google Cloud project it runs inside — reading "
        "production I-A-M read-only. It can ask a human to review a permission. It cannot change "
        "one. It's deployed on Google's managed agent stack, not a local script — and building "
        "it there surfaced a real defect in Google's own A-D-K, which we reported upstream. "
        "Everything after this was captured from the deployed fleet.",
        # The opening take runs 34.3s, so a long hold here only clones its final frame. Trimmed to
        # 1.0s when the honest-capture rewording added 2.4s of speech and pushed the cut to 3:55.
        hold=1.0,
    ),
    Beat(
        "event",
        "Publish the approved event; show the durable inbox admitting it",
        "An approved enterprise event opens the investigation. Pub/Sub and Eventarc give it a "
        "durable inbox with a lease, so the work survives a restart. This deployment is "
        "event-triggered — there is no recurring schedule in this snapshot.",
        hold=4.0,
    ),
    Beat(
        "iam",
        "Live IAM counts landing, then the canonical deterministic findings",
        "The Access Auditor reads production IAM with read-only authority — sixty-two live "
        "bindings on this route. Deterministic rules, not the model, produce the findings: "
        "three, across two owning teams. Raw principals, roles and bindings stop inside that tool.",
        "The Access Auditor reads production I-A-M with read-only authority — sixty-two live "
        "bindings on this route. Deterministic rules, not the model, produce the findings: "
        "three, across two owning teams. Raw principals, roles and bindings stop inside that tool.",
        hold=4.0,
    ),
    Beat(
        "model",
        "Gemini rationale appearing, then the fidelity check passing",
        "Gemini 3.5 Flash writes a bounded rationale for one finding. It cannot add, drop, "
        "re-score or redirect one. Every field is checked against the tool's canonical output; "
        "if they disagree, the investigation fails closed.",
        "Gemini three point five Flash writes a bounded rationale for one finding. It cannot "
        "add, drop, re-score or redirect one. Every field is checked against the tool's "
        "canonical output; if they disagree, the investigation fails closed.",
        hold=4.0,
    ),
    Beat(
        "deliver",
        "Two department deliveries and the single durable review record",
        "The Escalation Agent holds no IAM read role at all, and no model. It delivers count-only "
        "reviews to the teams that own them — two findings to security-engineering, one durable "
        "review record. Completion requires a receipt from every required delivery.",
        "The Escalation Agent holds no I-A-M read role at all, and no model. It delivers "
        "count-only reviews to the teams that own them — two findings to security-engineering, "
        "one durable review record. Completion requires a receipt from every required delivery.",
        hold=3.0,
    ),
    Beat(
        "memory",
        "The approved exception, then the later suppression and the absent notification",
        "A human approved an exception for platform-infra. Three days later, across redeployments "
        "and restarts, the matching finding was suppressed and that team was not paged again. The "
        "decision was remembered across a real elapsed gap — not re-derived by a model.",
        hold=4.0,
    ),
    Beat(
        "identity",
        "Auditor identity permitted, Escalation identity denied the same read",
        "Separation is enforced by IAM, not prompt wording. The Auditor identity performs this "
        "read; the Escalation identity is denied the same call. This denial is reproduced by "
        "impersonation, not captured mid-investigation.",
        "Separation is enforced by I-A-M, not prompt wording. The Auditor identity performs "
        "this read; the Escalation identity is denied the same call. This denial is reproduced "
        "by impersonation, not captured mid-investigation.",
        hold=3.0,
    ),
    Beat(
        "armor",
        "The agent-mediated Model Armor refusal on the Auditor's own A2A surface",
        "A compromised authorized caller sends an injection through the Auditor's own A2A "
        "surface. The deployed callback refuses it before Gemini. The task fails closed, and zero "
        "model submissions, completions or tool calls follow.",
        "A compromised authorized caller sends an injection through the Auditor's own A-two-A "
        "surface. The deployed callback refuses it before Gemini. The task fails closed, and zero "
        "model submissions, completions or tool calls follow.",
        hold=3.0,
    ),
    Beat(
        "audit",
        "Cloud Trace span tree, then the correlated payload-free audit query",
        "Cloud Trace shows one connected chain — twenty-two spans across the Runtime and both "
        "workers. Separately, a payload-free audit joins every event under one investigation ID, "
        "retained a year in europe-west4. The trace expires; the audit is the compliance record.",
        "Cloud Trace shows one connected chain — twenty-two spans across the Runtime and both "
        "workers. Separately, a payload-free audit joins every event under one investigation "
        "I-D, retained a year in europe-west four. The trace expires; the audit is the "
        "compliance record.",
        hold=3.0,
    ),
    Beat(
        "cloud",
        "Deployment overview across the managed Google Cloud surface",
        "All of it runs privately on Google Cloud — managed Agent Runtime, Gateway, Registry and "
        "Memory Bank, with Cloud Run, Firestore, Pub/Sub and Vertex AI behind an "
        "IAM-private boundary.",
        "All of it runs privately on Google Cloud — managed Agent Runtime, Gateway, Registry and "
        "Memory Bank, with Cloud Run, Firestore, Pub/Sub and Vertex A-I behind an "
        "I-A-M private boundary.",
        hold=2.0,
    ),
    Beat(
        "close",
        "The architecture flow animating, then the coverage report on the same commit",
        "Bastion turns real IAM into remembered, department-owned action — without ever giving an "
        "agent write access. The ADK defect it surfaced is now an open issue upstream, "
        "confirmed by a Google maintainer. Every claim here has a proof boundary in the "
        "public repository.",
        "Bastion turns real I-A-M into remembered, department-owned action — without ever "
        "giving an agent write access. The A-D-K defect it surfaced is now an open issue upstream, "
        "confirmed by a Google maintainer. Every claim here has a proof boundary in the "
        "public repository.",
        hold=2.0,
    ),
    # A short sign-off over a closing card carrying the repository, the console and the track.
    # It costs three seconds of a four-minute ceiling, which the measured cut can afford; the
    # card, not the narration, is what carries the two URLs a judge might want to type.
    Beat(
        "thanks",
        "The animated brand banner, with the repository and public evidence console URLs",
        "Thank you for watching.",
        hold=1.6,
    ),
]


def _client():  # noqa: ANN202 - the SDK type is only needed at the call site
    from google.cloud import texttospeech

    return texttospeech


def synthesise(text: str, voice: str = VOICE) -> bytes:
    tts = _client()
    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=tts.SynthesisInput(text=text),
        voice=tts.VoiceSelectionParams(language_code=LANGUAGE, name=voice),
        audio_config=tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3, speaking_rate=1.0),
    )
    return bytes(response.audio_content)


def _ffprobe() -> str:
    """Absolute path to ffprobe, resolved once. Same rule as scripts/redact_evidence.py."""
    found = shutil.which("ffprobe")
    if found is None:
        raise SystemExit("ffprobe is not on PATH — install FFmpeg to measure narration clips")
    return found


def duration(path: Path) -> float:
    result = subprocess.run(  # noqa: S603 - the executable is an absolute resolved path
        [
            _ffprobe(),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        capture_output=True,
        check=True,
    )
    return float(result.stdout.decode().strip())


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def clip_path(index: int, beat: Beat) -> Path:
    return OUT_DIR / f"vo_{index:02d}-{beat.slug}.mp3"


def timestamp(seconds: float) -> str:
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    return f"{whole // 3600:02d}:{whole % 3600 // 60:02d}:{whole % 60:02d},{ms:03d}"


def write_captions(measured: dict[str, float]) -> int:
    """Cue boundaries from per-sentence probe clips, scaled to each beat's measured length."""
    SRT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cues: list[str] = []
    clock = 0.0
    index = 0
    for position, beat in enumerate(NARRATION):
        total = measured[beat.slug]
        sentences = split_sentences(beat.to_speak())
        display = split_sentences(beat.text)
        probes = [duration_of_probe(s, position, n) for n, s in enumerate(sentences)]
        scale = total / sum(probes) if sum(probes) else 1.0
        for n, probe in enumerate(probes):
            index += 1
            span = probe * scale
            line = display[n] if n < len(display) else sentences[n]
            cues.append(f"{index}\n{timestamp(clock)} --> {timestamp(clock + span)}\n{line}\n")
            clock += span
        clock += beat.hold
    SRT_PATH.write_text("\n".join(cues), encoding="utf-8")
    return index


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def is_stale(path: Path, text: str) -> bool:
    """A clip is stale when the words that produced it changed.

    Without this, editing NARRATION silently keeps the old audio: the file exists, so nothing
    re-synthesises, and the committed timings then describe words nobody will say.
    """
    sidecar = path.with_suffix(".sha256")
    return not path.exists() or not sidecar.exists() or sidecar.read_text().strip() != digest(text)


def stamp(path: Path, text: str) -> None:
    path.with_suffix(".sha256").write_text(digest(text), encoding="utf-8")


def duration_of_probe(sentence: str, position: int, n: int) -> float:
    """Measure one sentence alone. Keyed by content, so an edit cannot reuse a stale probe."""
    probe_dir = OUT_DIR / "probes"
    probe_dir.mkdir(parents=True, exist_ok=True)
    path = probe_dir / f"p_{position:02d}_{n:02d}_{digest(sentence)}.mp3"
    if not path.exists():
        path.write_bytes(synthesise(sentence))
    return duration(path)


def report(measured: dict[str, float]) -> None:
    print(f"\n{'beat':<10} {'speech':>7} {'hold':>6} {'slot':>7}   cumulative")
    clock = 0.0
    for beat in NARRATION:
        speech = measured[beat.slug]
        slot = speech + beat.hold
        clock += slot
        print(
            f"{beat.slug:<10} {speech:6.1f}s {beat.hold:5.1f}s {slot:6.1f}s   "
            f"{int(clock) // 60}:{int(clock) % 60:02d}"
        )
    speech_total = sum(measured.values())
    print(
        f"\ntotal {clock:.1f}s ({int(clock) // 60}:{int(clock) % 60:02d}), "
        f"narrated {speech_total:.0f}s ({speech_total / clock * 100:.0f}%)"
    )
    if clock > 240:
        print("OVER the four-minute ceiling — trim a hold or a sentence.")
    elif not TARGET_LOW <= clock <= TARGET_HIGH:
        print(f"outside the {TARGET_LOW:.0f}-{TARGET_HIGH:.0f}s target window — adjust holds.")
    else:
        print("within the target window.")


def shot_table(measured: dict[str, float]) -> str:
    rows = ["| Time | Screen and action | Narration |", "|---|---|---|"]
    clock = 0.0
    for beat in NARRATION:
        start = clock
        clock += measured[beat.slug] + beat.hold
        stamp = f"{int(start) // 60}:{int(start) % 60:02d}–{int(clock) // 60}:{int(clock) % 60:02d}"
        rows.append(f"| {stamp} | {beat.screen} | “{beat.text}” |")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", action="store_true", help="measure existing clips only")
    parser.add_argument("--clip", help="regenerate a single beat by slug")
    parser.add_argument("--audition", action="store_true", help="one line in each candidate voice")
    arguments = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if arguments.audition:
        line = split_sentences(NARRATION[0].to_speak())[0]
        for short in AUDITION_VOICES:
            name = f"en-US-Chirp3-HD-{short}"
            path = OUT_DIR / "auditions" / f"audition-{short}.mp3"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(synthesise(line, voice=name))
            print(f"  {path.name}  {duration(path):.1f}s")
        return 0

    measured: dict[str, float] = {}
    for position, beat in enumerate(NARRATION):
        path = clip_path(position, beat)
        stale = arguments.clip == beat.slug or is_stale(path, beat.to_speak())
        if arguments.table and not path.exists():
            print(f"missing clip for {beat.slug}; run without --table first")
            return 1
        if not arguments.table and stale:
            path.write_bytes(synthesise(beat.to_speak()))
            stamp(path, beat.to_speak())
            print(f"  wrote {path.name}")
        measured[beat.slug] = duration(path)

    report(measured)
    if not arguments.table:
        cues = write_captions(measured)
        print(f"\nwrote {SRT_PATH.relative_to(ROOT).as_posix()} ({cues} cues)")
    print("\nShot table for submission/DEMO_SCRIPT.md:\n")
    print(shot_table(measured))
    return 0


if __name__ == "__main__":
    sys.exit(main())
