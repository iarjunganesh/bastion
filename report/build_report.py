"""Build the canonical sections and validate a local technical-report PDF; no fleet calls."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import statistics
import subprocess
import textwrap
import zipfile
from pathlib import Path
from typing import Any

import pymupdf as fitz
from PIL import Image as PILImage
from PIL import ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPORT_DATE = "November 2026"
GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("Git is required to identify the local source revision")
# Published link baseline for this dated edition. Local commits must not silently
# move citations to a revision that has not been published.
REVISION = "aa398f6953de6dd3d56d84b2ae981a4a06591474"
BASE = f"https://github.com/iarjunganesh/bastion/blob/{REVISION}/"
SECTION_NAMES = (
    "00-front.md",
    "01-introduction.md",
    "02-background.md",
    "03-threat-model.md",
    "04-design.md",
    "05-method.md",
    "06-failures.md",
    "07-evaluation.md",
    "08-not-demonstrated.md",
    "09-discussion.md",
    "10-conclusion.md",
    "appendix-a-reproducibility.md",
    "appendix-b-evidence.md",
    "appendix-c-protocols.md",
    "references.md",
)
FIGURES = ("figure1-topology.png", "figure2-chronology.png", "figure3-timeout.png")
PDF_NAME = "bastion-technical-report-2026-11.pdf"
LIVE_DATA = ROOT / "assets/evidence/live-validation-2026-10-27"
LIVE_BUNDLE = "bastion-live-validation-2026-10-27.zip"
LIVE_BUNDLE_SHA256 = "3f9acf4c82f390cd25091ec684c8a195af36388592363916742a6607e4a7d80c"
REPO_LINK = re.compile(
    r"\[([^\]]+)\]\(https://github\.com/iarjunganesh/bastion/blob/REVISION/([^)]+)\)"
)


def source_sections() -> list[Path]:
    """Use the explicit order and fail if a canonical source is missing."""
    paths = [HERE / "sections" / name for name in SECTION_NAMES]
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Missing canonical section: {path.name}")
    return paths


def repository_sources(text: str) -> list[str]:
    """Only cited public repository paths enter the source snapshot."""
    paths = {match.group(2) for match in REPO_LINK.finditer(text)}
    paths.update(
        {"requirements.txt", "requirements-runtime.txt", "requirements.lock", "pyproject.toml"}
    )
    for relative in paths:
        candidate = ROOT / relative
        public_roots = {
            "docs",
            "agents",
            "assets",
            "infrastructure",
            "tests",
            "registry",
            "runtime",
            "model_armor",
            "gateway",
            "identity",
            "observability",
            "archive",
        }
        public_files = {
            "AGENTS.md",
            "CLAUDE.md",
            "requirements.txt",
            "requirements-runtime.txt",
            "requirements.lock",
            "pyproject.toml",
        }
        relative_path = Path(relative)
        if relative_path.is_absolute() or any(part.startswith(".") for part in relative_path.parts):
            raise ValueError(f"Unsafe repository source: {relative}")
        allowed = relative_path.parts[0] in public_roots or relative in public_files
        resolved = candidate.resolve()
        if not resolved.is_relative_to(ROOT.resolve()):
            raise ValueError(f"Unsafe repository source: {relative}")
        resolved_relative = resolved.relative_to(ROOT.resolve())
        resolved_allowed = (
            resolved_relative.parts[0] in public_roots
            or resolved_relative.as_posix() in public_files
        )
        if allowed and resolved_allowed and candidate.is_file():
            continue
        raise ValueError(f"Missing or unsafe repository source: {relative}")
    return sorted(paths)


TEXT_SUFFIXES = frozenset({".md", ".py", ".txt", ".toml", ".lock", ".json", ".yml", ".yaml"})
TEXT_NAMES = frozenset({"LICENSE"})
# The snapshot bundles MIT-licensed code, which must keep its copyright and permission notice,
# and CC BY report content, whose scope notice must travel with it.
LICENCE_FILES = ("LICENSE", "LICENSE-CONTENT.md")


def canonical_bytes(path: Path) -> bytes:
    """Text with LF line endings, binary unchanged, so hashes survive a Windows checkout."""
    data = path.read_bytes()
    text = path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES
    return data.replace(b"\r\n", b"\n") if text else data


def is_base_file(relative: str) -> bool:
    """Do not invent a public commit link for a changed or new file."""
    original = subprocess.run(  # noqa: S603 - Git object read, no shell or external command text
        [GIT, "show", f"{REVISION}:{relative}"], cwd=ROOT, capture_output=True, check=False
    )
    current = (ROOT / relative).read_bytes()
    return original.returncode == 0 and original.stdout.replace(b"\r\n", b"\n") == current.replace(
        b"\r\n", b"\n"
    )


def source_manifest(text: str) -> dict[str, Any]:
    """Capture exact bytes, separately from the base commit's historical links."""
    paths = repository_sources(text)
    paths.extend(path.relative_to(ROOT).as_posix() for path in source_sections())
    build_inputs = ("build_report.py", "make_figures.py", "requirements-build.txt")
    paths.extend(f"report/{name}" for name in build_inputs)
    paths.extend(f"report/figures/{name}" for name in FIGURES)
    paths.extend(LICENCE_FILES)
    return {
        "base_revision": REVISION,
        "local_edition_date": REPORT_DATE,
        "files": {name: hashlib.sha256(canonical_bytes(ROOT / name)).hexdigest() for name in paths},
        "local_overlay": [name for name in repository_sources(text) if not is_base_file(name)],
        "scope": (
            "Cited public sources, canonical manuscript/build inputs and dependency provenance; "
            "no private captures, billing values or credentials"
        ),
    }


def resolve_repository_links(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        label, relative = match.groups()
        if not (ROOT / relative).is_file():
            raise ValueError(f"Missing repository source: {relative}")
        if is_base_file(relative):
            return f"[{label}]({BASE}{relative})"
        return f"{label} (`{relative}`; local source snapshot)"

    return REPO_LINK.sub(replace, text)


def citation_keys(text: str) -> set[str]:
    """Expand ranges before checking keys; normalise E03 and E3 consistently."""

    def expand(match: re.Match[str]) -> str:
        prefix, first, second_prefix, last = match.groups()
        if second_prefix and second_prefix != prefix:
            raise ValueError("Citation range crosses reference families")
        if int(last) < int(first):
            raise ValueError("Reversed citation range")
        return ", ".join(f"{prefix}{i}" for i in range(int(first), int(last) + 1))

    expanded = re.sub(r"([RSEU])(\d+)[–-]([RSEU]?)(\d+)", expand, text)
    return {prefix + str(int(number)) for prefix, number in re.findall(r"([RSEU])(\d+)", expanded)}


def validate_manuscript(text: str) -> None:
    """Reject missing sources, incomplete assembly and undefined citations before a PDF is built."""
    if "[[" in text or "<!--" in text or "/blob/REVISION/" in text:
        raise ValueError("Unresolved manuscript placeholder or assembly marker")
    if "Independent researcher, Stockholm" not in text or REPORT_DATE not in text:
        raise ValueError("Missing author affiliation or report date")
    body, references = text.split("## References", 1)
    definitions = re.findall(r"^- \*\*([RSEU]\d+)\.\*\*", references, re.MULTILINE)
    known = citation_keys(" ".join(definitions))
    if len(definitions) != len(known):
        raise ValueError("Duplicate reference key")
    for match in re.finditer(r"\[((?:[RSEU]\d+)[^\]]*)\](?!\()", body):
        if re.search(r"\bE\d\b", match.group(1)):
            raise ValueError("Evidence citations use two digits (E03, not E3)")
        missing = citation_keys(match.group(1)) - known
        if missing:
            raise ValueError(f"Undefined citation keys: {sorted(missing)}")
    # Cohort chunks are N1-N7; E1-E7 would read as evidence records. Only the mapping names them.
    prose = re.sub(r"record them as E1[–-]E7", "", body)
    if re.search(r"\bE[1-9]b?\b", prose):
        raise ValueError("A chunk-style E name collides with evidence identifiers; use N1-N7")
    if re.search(r"[A-Za-z]-\n[A-Za-z]", text):
        raise ValueError("A hyphenated word is split across source lines")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith("https://"):
            continue
        if not (HERE / target).is_file():
            raise ValueError(f"Missing relative manuscript link: {target}")


def assemble() -> str:
    """Assemble the final sections in memory; tests never rebuild the report."""
    raw = "\n\n".join(path.read_text(encoding="utf-8").strip() for path in source_sections()) + "\n"
    # Sections link figures relative to sections/; the generated manuscript lives in report/.
    raw = raw.replace("](../figures/", "](figures/")
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    manifest = source_manifest(raw)
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    fingerprint = hashlib.sha256(manifest_bytes).hexdigest()
    provenance = (
        f"Cited-source manifest SHA-256: `{fingerprint}`. "
        "The manifest records canonical bytes for the listed cited sources, report scripts, "
        "sections, figures, dependency files and licence notices; the source snapshot carries "
        "those bytes.\n\n"
    )
    raw = raw.replace("### A.3 Offline checks", provenance + "### A.3 Offline checks")
    text = resolve_repository_links(raw)
    text = text.replace("–", "-").replace("—", "-").replace("\u2011", "-")
    validate_manuscript(text)
    return text


def write_source_snapshot() -> None:
    raw = "\n\n".join(path.read_text(encoding="utf-8") for path in source_sections())
    manifest = source_manifest(raw)
    data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    (HERE / "source-manifest.json").write_bytes(data)
    with zipfile.ZipFile(HERE / "source-snapshot.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("source-manifest.json", data)
        for relative in manifest["files"]:
            archive.writestr(relative, canonical_bytes(ROOT / relative))


def table_widths(columns: int, width: float, headers: tuple[str, ...] | None = None) -> list[float]:
    """Fit the canonical two- to five-column tables, giving prose columns the space."""
    weights = {
        2: (0.30, 0.70),
        3: (0.24, 0.38, 0.38),
        4: (0.13, 0.13, 0.34, 0.40),
        5: (0.12, 0.20, 0.22, 0.22, 0.24),
    }
    by_header = {
        ("boundary", "crossing"): (0.11, 0.33, 0.56),
        ("quantity", "requirement"): (0.27, 0.43, 0.30),
        ("control", "answers"): (0.28, 0.14, 0.58),
        ("run", "fleet"): (0.07, 0.10, 0.70, 0.13),
        ("run", "stop"): (0.13, 0.30, 0.30, 0.27),
        ("measure", "g (v0.9.0)"): (0.37, 0.21, 0.21, 0.21),
        ("record", "date"): (0.15, 0.10, 0.57, 0.18),
        ("fleet", "source"): (0.13, 0.52, 0.17, 0.18),
        ("id", "date"): (0.08, 0.13, 0.43, 0.36),
        ("dead-letter publish time", "source delivery count"): (0.28, 0.20, 0.28, 0.24),
        ("chunk", "question"): (0.10, 0.45, 0.32, 0.13),
        ("control", "probe"): (0.18, 0.29, 0.43, 0.10),
    }
    if headers and len(headers) >= 2:
        key = (headers[0].strip().lower(), headers[1].strip().lower())
        preset = by_header.get(key)
        if preset and len(preset) == columns:
            weights[columns] = preset
    if columns not in weights:
        raise ValueError(f"Unsupported table with {columns} columns")
    return [width * weight for weight in weights[columns]]


def load_live_validation() -> dict[str, Any]:
    """Verify the supplied immutable supplement without importing or invoking fleet code."""
    bundle = LIVE_DATA / LIVE_BUNDLE
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != LIVE_BUNDLE_SHA256:
        raise ValueError("Live-validation bundle does not match the reviewed capture")
    public_files = {LIVE_BUNDLE, "summary.json", "runs.csv", "stages.csv"}
    public_hashes = json.loads((LIVE_DATA / "sha256.json").read_text(encoding="utf-8"))
    if set(public_hashes) != public_files:
        raise ValueError("Live-validation public-file manifest is incomplete")
    if public_hashes[LIVE_BUNDLE] != LIVE_BUNDLE_SHA256:
        raise ValueError(f"Live-validation public-file hash mismatch: {LIVE_BUNDLE}")
    with zipfile.ZipFile(bundle) as archive:
        # The recorded hashes describe the bundle members' exact (CRLF) bytes. Git may check the
        # public copies out with LF endings, so those are compared after line-ending
        # normalisation; the bundle and its members are still checked byte for byte.
        for name in public_files - {LIVE_BUNDLE}:
            member = archive.read(name)
            checked_out = (LIVE_DATA / name).read_bytes()
            if hashlib.sha256(member).hexdigest() != public_hashes[name] or member.replace(
                b"\r\n", b"\n"
            ) != checked_out.replace(b"\r\n", b"\n"):
                raise ValueError(f"Live-validation public-file hash mismatch: {name}")
        if archive.testzip() is not None:
            raise ValueError("Live-validation bundle CRC check failed")
        member_hashes = json.loads(archive.read("sha256.json"))
        if set(archive.namelist()) != set(member_hashes) | {"sha256.json"}:
            raise ValueError("Live-validation bundle member manifest is incomplete")
        for name, digest in member_hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"Live-validation member hash mismatch: {name}")
        summary = json.loads(archive.read("summary.json"))
        metrics = json.loads(archive.read("metrics.json"))
    runs = metrics["runs"]
    replays = metrics["replays"]
    if metrics["phase"] != "completed" or len(runs) != 20 or len(replays) != 5:
        raise ValueError("Live-validation completed sample does not contain 20 runs and 5 replays")
    for field in ("event_id", "context_id"):
        if len({row["event"][field] for row in runs}) != 20:
            raise ValueError(f"Live-validation {field} values are not distinct")
    if any(
        row["validation"] != "passed"
        or row["durable"]["status"] != "completed"
        or row["durable"]["attempts"] != 1
        or row["event"]["mock_data"] is not False
        for row in runs
    ):
        raise ValueError("Live-validation includes an unverified or non-real-IAM run")
    expected = {
        "validated_run_audit_events": sum(len(row["audit_events"]) for row in runs),
        "validated_run_review_records": sum(len(row["reviews"]) for row in runs),
        "validated_run_delivered_findings": sum(
            review["finding_count"] for row in runs for review in row["reviews"]
        ),
    }
    if expected != {
        "validated_run_audit_events": 560,
        "validated_run_review_records": 40,
        "validated_run_delivered_findings": 60,
    } or any(summary[field] != value for field, value in expected.items()):
        raise ValueError("Live-validation reported totals disagree with the run data")
    invocations = sum(
        len({event["invocation_id"] for event in row["audit_events"]}) for row in runs
    )
    submissions = sum(
        event["event"] == "model.request" and event["outcome"] == "submitted"
        for row in runs
        for event in row["audit_events"]
    )
    if (
        invocations != 60
        or submissions != 40
        or summary["validated_run_invocations"] != invocations
        or sum(summary["model_submissions_captured"].values()) != submissions
    ):
        raise ValueError("Live-validation invocation/model counts disagree with the audit data")
    confirmation = [row["confirmation_seconds"] for row in runs]
    workflow = [row["audit_durations_seconds"]["orchestrator"] for row in runs]
    for values, recorded in (
        (confirmation, summary["counts"]["confirmation_seconds"]),
        (workflow, summary["audit_duration_seconds"]["orchestrator"]),
    ):
        if recorded != {
            "n": 20,
            "minimum": min(values),
            "median": statistics.median(values),
            "maximum": max(values),
        }:
            raise ValueError("Live-validation timing summary disagrees with the run data")
    if any(
        replay.get("observation") != "unchanged_effects_during_bounded_window"
        or replay.get("observation_window_seconds") != 120
        or replay.get("per_message_delivery_acknowledgement") != "not_available"
        for replay in replays
    ):
        raise ValueError("Live-validation replay observation boundary changed")
    return summary


def inline(text: str) -> str:
    """Translate the intentionally small Markdown inline subset to Paragraph markup."""
    parts = []
    pattern = r"\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*"
    cursor = 0
    for match in re.finditer(pattern, text):
        parts.append(html.escape(text[cursor : match.start()]))
        if match.group(1) is not None:
            href = html.escape(match.group(2), quote=True)
            label = html.escape(match.group(1))
            parts.append(f'<link href="{href}" color="#234C72">{label}</link>')
        elif match.group(3) is not None:
            # Narrow code tokens may be long; body font keeps identifiers from overflowing.
            # Neutral grey: inline code must not look like a link (#234C72).
            parts.append(f'<font name="Body" color="#4D4D4D">{html.escape(match.group(3))}</font>')
        elif match.group(4) is not None:
            parts.append(f"<b>{html.escape(match.group(4))}</b>")
        else:
            parts.append(f"<i>{html.escape(match.group(5))}</i>")
        cursor = match.end()
    parts.append(html.escape(text[cursor:]))
    return "".join(parts)


def build_pdf(manuscript: str, output: Path | None = None) -> None:
    fonts = Path("C:/Windows/Fonts")
    for name, filename in [
        ("Body", "times.ttf"),
        ("BodyBold", "timesbd.ttf"),
        ("BodyItalic", "timesi.ttf"),
        ("BodyBoldItalic", "timesbi.ttf"),
        ("Sans", "arial.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily(
        "Body", normal="Body", bold="BodyBold", italic="BodyItalic", boldItalic="BodyBoldItalic"
    )
    body = ParagraphStyle(
        "Body",
        fontName="Body",
        fontSize=10.5,
        leading=13.9,
        spaceAfter=6,
        splitLongWords=True,
        allowWidows=0,
        allowOrphans=0,
    )
    styles = {
        "body": body,
        "title": ParagraphStyle(
            "Title",
            parent=body,
            fontName="BodyBold",
            fontSize=19,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=13,
        ),
        "author": ParagraphStyle(
            "Author", parent=body, fontSize=11, alignment=TA_CENTER, spaceAfter=5
        ),
        "h2": ParagraphStyle(
            "Section",
            parent=body,
            fontName="BodyBold",
            fontSize=13,
            leading=16,
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "Subsection",
            parent=body,
            fontName="BodyBold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "caption": ParagraphStyle("Caption", parent=body, fontSize=9, leading=11.3, spaceAfter=8),
        "cell": ParagraphStyle("Cell", parent=body, fontSize=8.5, leading=10.5, spaceAfter=0),
        "code": ParagraphStyle(
            "Code",
            parent=body,
            fontName="Sans",
            fontSize=8.1,
            leading=11,
            leftIndent=8,
            rightIndent=8,
            spaceAfter=7,
            backColor=colors.HexColor("#F1F3F5"),
        ),
        "bullet": ParagraphStyle("Bullet", parent=body, leftIndent=11, firstLineIndent=-8),
    }
    width = A4[0] - 96
    story = []
    lines = manuscript.splitlines()
    cursor = 0
    title_region = True
    in_references = False
    while cursor < len(lines):
        line = lines[cursor].strip()
        if not line:
            cursor += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["title"]))
        elif line.startswith("## "):
            title_region = False
            in_references = line.startswith("## References")
            story.append(Paragraph(inline(line[3:]), styles["h2"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["h3"]))
        elif line.startswith("!["):
            match = re.match(r"!\[([^]]+)\]\(([^)]+)\)", line)
            source = HERE / match.group(2)
            image_width, image_height = PILImage.open(source).size
            picture = Image(str(source), width=width, height=width * image_height / image_width)
            cursor += 1
            while cursor < len(lines) and not lines[cursor].strip():
                cursor += 1
            caption_lines = []
            while cursor < len(lines) and lines[cursor].strip():
                caption_lines.append(lines[cursor].strip())
                cursor += 1
            caption = Paragraph(inline(" ".join(caption_lines)), styles["caption"])
            story.append(KeepTogether([Spacer(1, 7), picture, Spacer(1, 5), caption]))
            continue
        elif line.startswith("```"):
            cursor += 1
            code_lines = []
            while cursor < len(lines) and not lines[cursor].startswith("```"):
                for wrapped in textwrap.wrap(lines[cursor], width=89, subsequent_indent="  ") or [
                    ""
                ]:
                    code_lines.append(html.escape(wrapped))
                cursor += 1
            code = "<br/>".join(code_lines).replace("→", "-&gt;")
            story.append(Paragraph(code, styles["code"]))
        elif line.startswith("|"):
            table_lines = []
            while cursor < len(lines) and lines[cursor].strip().startswith("|"):
                raw = lines[cursor].strip()
                if not re.match(r"^\|[\s|:\-]+\|$", raw):
                    table_lines.append(
                        [
                            Paragraph(inline(cell.strip()), styles["cell"])
                            for cell in raw.strip("|").split("|")
                        ]
                    )
                cursor += 1
            table = Table(
                table_lines,
                colWidths=table_widths(
                    len(table_lines[0]),
                    width,
                    tuple(cell.getPlainText() for cell in table_lines[0]),
                ),
                repeatRows=1,
                hAlign="LEFT",
            )
            table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF4")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#F6F7F8")],
                        ),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#53687B")),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.extend([table, Spacer(1, 7)])
            continue
        else:
            bullet = line.startswith("- ")
            paragraph = [line[2:] if bullet else line]
            cursor += 1
            while (
                cursor < len(lines)
                and lines[cursor].strip()
                and not re.match(r"^(#|\||```|!\[|- )", lines[cursor])
            ):
                paragraph.append(lines[cursor].strip())
                cursor += 1
            content = inline(" ".join(paragraph))
            if bullet:
                content = "&#8226; " + content
            style = (
                styles["author"] if title_region else styles["bullet"] if bullet else styles["body"]
            )
            paragraph = Paragraph(content, style)
            story.append(KeepTogether([paragraph]) if in_references and bullet else paragraph)
            continue
        cursor += 1

    def page_decoration(canvas, doc):
        canvas.saveState()
        canvas.setFont("Sans", 8)
        canvas.setFillColor(colors.HexColor("#586574"))
        canvas.drawString(48, A4[1] - 29, "BASTION  |  Technical report")
        canvas.drawRightString(A4[0] - 48, A4[1] - 29, f"report-2026-11  |  {REPORT_DATE}")
        canvas.drawCentredString(A4[0] / 2, 27, str(doc.page))
        canvas.restoreState()

    output = output or HERE / PDF_NAME
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=45,
        bottomMargin=43,
        title=manuscript.splitlines()[0].removeprefix("# "),
        author="Arjun Ganesh",
        subject=(
            "Execution boundaries, control evolution and bounded evaluation "
            "of a governed agent fleet"
        ),
    )
    document.build(story, onFirstPage=page_decoration, onLaterPages=page_decoration)


def validate_and_render(output: Path | None = None) -> dict[str, Any]:
    """Render every page and check text, bounds, links and source preservation."""
    output = output or HERE / PDF_NAME
    qa_dir = HERE / "qa"
    qa_dir.mkdir(exist_ok=True)
    findings: list[str] = []
    pages: list[Path] = []
    texts: list[str] = []
    links = 0
    with fitz.open(output) as doc:
        for number, page in enumerate(doc, 1):
            text = page.get_text()
            texts.append(text)
            if len(text.strip()) < 100:
                findings.append(f"Sparse page {number}")
            if "\ufffd" in text or "\u25a0" in text:
                findings.append(f"Unsupported glyph on page {number}")
            for link in page.get_links():
                if link.get("uri"):
                    links += 1
                    if not link["uri"].startswith("https://"):
                        findings.append(f"Non-public link on page {number}")
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        if (
                            x0 < 46
                            or x1 > page.rect.width - 46
                            or y0 < 15
                            or y1 > page.rect.height - 14
                        ):
                            findings.append(
                                f"Text out of bounds on page {number}: {span['text'][:55]}"
                            )
            path = qa_dir / f"page-{number:02}.png"
            page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(path)
            pages.append(path)
    extracted = "\n\n".join(texts)
    (qa_dir / "extracted-text.txt").write_text(extracted, encoding="utf-8")
    required = (
        "Abstract",
        "6.2 Corrective controls and verified recovery",
        "7.5 Timeout fault injection",
        "8. What the evaluation does not demonstrate",
        "10. Conclusion",
        "Appendix A",
        "Appendix B",
        "Appendix C",
        "98 of 98",
        "3.01%",
        "5 of 142",
        "Six of ten model completions",
        "E29.",
        "U4.",
        "Independent researcher, Stockholm",
        "pre-specified",
        REPORT_DATE,
    )
    for value in required:
        if value not in extracted:
            findings.append(f"Missing extracted content: {value}")
    if "[[" in extracted or "/blob/REVISION/" in extracted:
        findings.append("Unresolved placeholder in PDF")
    columns, tile_width, tile_height = 3, 310, 460
    contact = PILImage.new(
        "RGB", (columns * tile_width, ((len(pages) + 2) // 3) * tile_height), "#E0E3E6"
    )
    draw = ImageDraw.Draw(contact)
    for index, path in enumerate(pages):
        with PILImage.open(path) as image:
            image.thumbnail((tile_width - 16, tile_height - 30))
            x = index % columns * tile_width + (tile_width - image.width) // 2
            y = index // columns * tile_height + 23
            contact.paste(image, (x, y))
            draw.text((x, y - 18), f"Page {index + 1}", fill="#182531")
    contact.save(qa_dir / "contact-sheet.png")
    figures_present = all((HERE / "figures" / name).is_file() for name in FIGURES)
    if not figures_present:
        findings.append("A report figure is missing")
    manifest = json.loads((HERE / "source-manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        if hashlib.sha256(canonical_bytes(ROOT / name)).hexdigest() != digest:
            findings.append(f"Cited source changed after snapshot: {name}")
    with zipfile.ZipFile(HERE / "source-snapshot.zip") as archive:
        if archive.testzip() is not None:
            findings.append("Source snapshot CRC failed")
        for name, digest in manifest["files"].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                findings.append(f"Snapshot member mismatch: {name}")
    qa = {
        "pages": len(pages),
        "pdf_bytes": output.stat().st_size,
        "clickable_https_links": links,
        "figures_present": figures_present,
        "findings": findings,
        "visual_review": "pending",
        "base_revision": REVISION,
        "local_snapshot_sources": manifest["local_overlay"],
        "pdf_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    (qa_dir / "checks.json").write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, indent=2))
    if findings:
        raise ValueError("PDF validation findings require review")
    return qa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="Alternate PDF path if a viewer locks the default"
    )
    args = parser.parse_args()
    manuscript = assemble()
    load_live_validation()
    write_source_snapshot()
    (HERE / "manuscript.md").write_text(manuscript, encoding="utf-8")
    build_pdf(manuscript, args.output)
    validate_and_render(args.output)
