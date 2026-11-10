"""Render the report's three diagrams offline, with readable final-size labels."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
FONTS = Path("C:/Windows/Fonts")
WIDTH = 1600
PLACED_WIDTH_PT = 595.2755905511812 - 96  # A4 less the builder's two 48 pt margins.
MIN_FONT_PX = 27  # 8.43 pt at the final placed width; never shrink text to fit.
INK = "#1F2A36"
MUTED = "#5B6875"
ACCENT = "#234C72"
FAIL = "#9C2F2F"
OK = "#2F6B3A"
BOX = "#EEF2F6"
BOUNDARY = "#B05A00"
LABELS: list[dict] = []
RECEIPTS: list[dict] = []


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    if size < MIN_FONT_PX:
        raise ValueError("A figure label would be smaller than eight points in the PDF")
    return ImageFont.truetype(str(FONTS / ("arialbd.ttf" if bold else "arial.ttf")), size)


def text_block(
    d: ImageDraw.ImageDraw,
    region: tuple[float, float, float, float],
    text: str,
    *,
    size: int = MIN_FONT_PX,
    bold: bool = False,
    color: str = INK,
    align: str = "left",
    valign: str = "top",
    leading: int = 36,
) -> None:
    """Wrap at the measured width and refuse clipping, without reducing the font."""
    x0, y0, x1, y1 = region
    face = font(size, bold)
    lines: list[str] = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}" if current else word
            if d.textlength(candidate, font=face) > x1 - x0:
                if not current or d.textlength(word, font=face) > x1 - x0:
                    raise ValueError(f"A word cannot fit its figure region: {word}")
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    height = len(lines) * leading
    if height > y1 - y0:
        raise ValueError(f"A figure text block is too tall: {text}")
    top = y0 + ((y1 - y0 - height) / 2 if valign == "center" else 0)
    for index, line in enumerate(lines):
        line_width = d.textlength(line, font=face)
        left = x0 + ((x1 - x0 - line_width) / 2 if align == "center" else 0)
        xy = (left, top + index * leading)
        bounds = d.textbbox(xy, line, font=face, anchor="lt")
        if bounds[0] < x0 - 1 or bounds[2] > x1 + 1 or bounds[3] > y1:
            raise ValueError(f"A figure label is clipped: {line}")
        d.text(xy, line, font=face, fill=color, anchor="lt")
        LABELS.append({"text": line, "bounds": bounds, "font_px": size})


def box(
    d: ImageDraw.ImageDraw,
    xy: tuple[float, float, float, float],
    title: str,
    lines: tuple[str, ...] | list[str] = (),
    *,
    fill: str = BOX,
    outline: str = ACCENT,
) -> None:
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, radius=15, fill=fill, outline=outline, width=3)
    text_block(
        d,
        (x0 + 18, y0 + 16, x1 - 18, y0 + 60),
        title,
        size=30,
        bold=True,
        align="center",
        leading=40,
    )
    if lines:
        text_block(
            d,
            (x0 + 18, y0 + 62, x1 - 18, y1 - 8),
            "\n".join(lines),
            color=MUTED,
            align="center",
        )


def arrow(
    d: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = INK,
    dashed: bool = False,
    head: int = 15,
) -> None:
    (x0, y0), (x1, y1) = start, end
    length = math.hypot(x1 - x0, y1 - y0)
    if dashed:
        steps = max(1, math.ceil(length / 18))
        for i in range(0, steps, 2):
            a, b = i / steps, min((i + 1) / steps, 1)
            d.line(
                [
                    (x0 + (x1 - x0) * a, y0 + (y1 - y0) * a),
                    (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b),
                ],
                fill=color,
                width=4,
            )
    else:
        d.line([start, end], fill=color, width=4)
    angle = math.atan2(y1 - y0, x1 - x0)
    d.polygon(
        [
            end,
            (x1 - head * math.cos(angle - 0.45), y1 - head * math.sin(angle - 0.45)),
            (x1 - head * math.cos(angle + 0.45), y1 - head * math.sin(angle + 0.45)),
        ],
        fill=color,
    )


def tag(d: ImageDraw.ImageDraw, xy: tuple[float, float], text: str) -> None:
    x, y = xy
    width = d.textlength(text, font=font(MIN_FONT_PX, True)) + 22
    d.rounded_rectangle(
        (x - width / 2, y - 25, x + width / 2, y + 25),
        radius=8,
        fill="white",
        outline=BOUNDARY,
        width=2,
    )
    text_block(
        d,
        (x - width / 2 + 8, y - 18, x + width / 2 - 8, y + 20),
        text,
        bold=True,
        color=BOUNDARY,
        align="center",
    )


def finish(img: Image.Image, name: str) -> None:
    """Check physical font size, canvas bounds and text collisions before saving."""
    for index, label in enumerate(LABELS):
        x0, y0, x1, y1 = label["bounds"]
        if x0 < 0 or y0 < 0 or x1 > img.width or y1 > img.height:
            raise ValueError(f"Figure text is outside its canvas: {label['text']}")
        for other in LABELS[index + 1 :]:
            ox0, oy0, ox1, oy1 = other["bounds"]
            if min(x1, ox1) > max(x0, ox0) + 1 and min(y1, oy1) > max(y0, oy0) + 1:
                raise ValueError(f"Overlapping labels: {label['text']} / {other['text']}")
    minimum = min(label["font_px"] for label in LABELS) * PLACED_WIDTH_PT / WIDTH
    if minimum < 8:
        raise ValueError("Figure labels do not meet the final-size minimum")
    img.save(OUT / name, optimize=True)
    RECEIPTS.append(
        {
            "file": name,
            "width_px": img.width,
            "height_px": img.height,
            "placed_width_pt": PLACED_WIDTH_PT,
            "minimum_font_pt": minimum,
            "label_lines": len(LABELS),
            "clipping": [],
            "text_collisions": [],
        }
    )
    LABELS.clear()


def figure1() -> None:
    img = Image.new("RGB", (WIDTH, 1880), "white")
    d = ImageDraw.Draw(img)
    text_block(
        d,
        (60, 30, 1540, 125),
        "Bastion v0.9.1: logical calls and trust boundaries",
        size=36,
        bold=True,
        leading=46,
    )
    box(
        d,
        (70, 160, 680, 305),
        "Pub/Sub + Eventarc",
        ["approved enterprise event", "retry, dead-letter review"],
    )
    box(
        d,
        (920, 160, 1530, 305),
        "Dispatcher (Cloud Run)",
        ["durable Firestore lifecycle", "completes only on confirmation"],
    )
    arrow(d, (680, 230), (920, 230))
    tag(d, (800, 195), "T1")
    arrow(d, (1230, 305), (1230, 410))
    tag(d, (1295, 357), "T2")

    d.rounded_rectangle((70, 410, 1530, 735), radius=15, fill="#F7F9FB", outline=ACCENT, width=3)
    text_block(
        d,
        (95, 430, 1505, 480),
        "Managed Agent Runtime: Orchestrator graph",
        size=32,
        bold=True,
        align="center",
        leading=42,
    )
    steps = ["Auditor", "policy_step", "policy_gate", "Escalation", "escalation_gate"]
    for index, name in enumerate(steps):
        left = 100 + index * 282
        d.rounded_rectangle(
            (left, 510, left + 260, 585), radius=10, fill=BOX, outline=ACCENT, width=2
        )
        text_block(d, (left + 6, 530, left + 254, 570), name, bold=True, align="center")
        if index < len(steps) - 1:
            arrow(d, (left + 260, 548), (left + 282, 548), head=10)
    text_block(
        d,
        (100, 615, 1500, 720),
        "policy_step, policy_gate, escalation_gate: deterministic, model-free\n"
        "routing crosses A2A as validated message content, never as session state",
        color=MUTED,
        align="center",
    )
    # The confirmation returns to the dispatcher; every outbound worker call goes via the Gateway.
    for a, b in [((70, 470), (30, 470)), ((30, 470), (30, 350)), ((30, 350), (920, 350))]:
        arrow(d, a, b, color=OK, dashed=True, head=1)
    arrow(d, (920, 350), (920, 290), color=OK)
    text_block(
        d,
        (100, 315, 885, 348),
        "confirmation event: escalation_confirmed",
        color=OK,
        bold=True,
        leading=32,
    )
    # Transport acknowledgement uses the same confirmed-completion chain.
    arrow(d, (1070, 160), (1070, 130), color=OK, dashed=True, head=1)
    arrow(d, (1070, 130), (380, 130), color=OK, dashed=True, head=1)
    arrow(d, (380, 130), (380, 160), color=OK)

    arrow(d, (800, 735), (800, 830))
    tag(d, (865, 783), "T4")
    box(
        d,
        (350, 830, 1250, 980),
        "Agent Gateway",
        ["egress only (AGENT_TO_ANYWHERE)", "fail-closed IAP, Registry"],
    )
    arrow(d, (800, 980), (800, 1030), head=1)
    arrow(d, (800, 1030), (405, 1030), head=1)
    arrow(d, (800, 1030), (1195, 1030), head=1)
    arrow(d, (405, 1030), (405, 1090))
    arrow(d, (1195, 1030), (1195, 1090))
    tag(d, (865, 1030), "T3")
    box(
        d,
        (70, 1090, 740, 1290),
        "Access Auditor (A2A)",
        ["read-only IAM identity", "fidelity check, model retry"],
    )
    box(
        d,
        (860, 1090, 1530, 1290),
        "Escalation Agent (A2A)",
        ["no IAM read, no model", "receipts name finding IDs"],
    )

    arrow(d, (405, 1290), (295, 1430))
    tag(d, (285, 1370), "T6")
    arrow(d, (405, 1290), (800, 1430))
    tag(d, (715, 1370), "T5")
    arrow(d, (1195, 1290), (1305, 1430))
    box(d, (60, 1430, 530, 1625), "IAM (Cloud Asset)", ["zero-argument minimising tool"])
    box(d, (565, 1430, 1035, 1625), "Gemini via Model Armor", ["screened in and out, fail closed"])
    box(d, (1070, 1430, 1540, 1625), "Findings API", ["idempotent review records"])
    box(
        d,
        (60, 1690, 1540, 1835),
        "Audit and telemetry",
        ["Audit: payload-free, investigation ID", "Cloud Trace: sampled, time-window joins"],
        outline=MUTED,
    )
    text_block(
        d,
        (60, 1840, 1540, 1876),
        "Dashed green: completion-confirmation chain. Orange tags: trust boundaries (Section 3).",
    )
    finish(img, "figure1-topology.png")


def figure2() -> None:
    img = Image.new("RGB", (WIDTH, 1900), "white")
    d = ImageDraw.Draw(img)
    text_block(
        d,
        (60, 30, 1540, 140),
        "Chronology: execution-boundary failures, repairs and evaluation runs (2026)",
        size=36,
        bold=True,
        leading=46,
    )
    panels = [
        (
            ["21 Aug", "22 Aug", "23 Aug"],
            [
                "D1 policy step refused,\nrun 'completed'\nD6 observed 21 Aug; fixed 22 Aug",
                "D8 decision lost at\nA2A hop (22 Aug)",
                "D9 failed task as empty event;\nhalf-updated deployment",
            ],
            [
                "",
                "deterministic policy_step,\npolicy_gate; explicit content",
                "tolerant parsing; both\ndeployment surfaces",
            ],
        ),
        (
            ["27 Oct", "3 Nov", "5 Nov"],
            [
                "",
                "E19 empty stream recorded\nas completed (1 in 28)",
                "E24 quoted-content wrapping:\npilot failed closed",
            ],
            [
                "E14: 20/20 live validation",
                "N7b 20/20; dispatcher must\nsee confirmation (deployed 5 Nov)",
                "recovery: 5 normal + control\n+ 2 replays passed",
            ],
        ),
        (
            ["7 Nov", "8 Nov", "9 Nov"],
            [
                "H28 model 429:\nfailed closed, redelivered",
                "M: worker kept running\nafter caller timeout",
                "",
            ],
            [
                "v0.9.0 G, H stopped; v0.9.1\nbounded retry; I 98/98",
                "J controls; K census\n5/142; L stop; M 8/8",
                "D4: 25/26 retired;\nbilling disconnected",
            ],
        ),
    ]
    columns = [(50, 515), (565, 1035), (1085, 1550)]
    for panel_index, (dates, failures, repairs) in enumerate(panels):
        origin = 170 + panel_index * 550
        axis = origin + 255
        d.line([(80, axis), (1520, axis)], fill=INK, width=4)
        for (left, right), date, failure, repair in zip(
            columns, dates, failures, repairs, strict=True
        ):
            center = (left + right) / 2
            d.line([(center, axis - 12), (center, axis + 12)], fill=INK, width=4)
            text_block(
                d,
                (left, axis + 22, right, axis + 65),
                date,
                size=30,
                bold=True,
                align="center",
                leading=40,
            )
            if failure:
                text_block(
                    d,
                    (left + 12, origin + 35, right - 12, axis - 25),
                    failure,
                    color=FAIL,
                    bold=True,
                    align="center",
                    valign="center",
                )
            if repair:
                text_block(
                    d,
                    (left + 12, axis + 85, right - 12, origin + 525),
                    repair,
                    color=OK,
                    align="center",
                )
    text_block(
        d,
        (60, 1815, 1540, 1895),
        "Red: failures (above each axis). Green: repairs and evaluation runs (below).\n"
        "Time axis compressed between August, October and November.",
        color=MUTED,
    )
    finish(img, "figure2-chronology.png")


def figure3() -> None:
    # Unchanged E29 values: seconds relative to each attempt's estimated boundary.
    attempts = [
        (1, 0.14, 31.1, "2 of 2", "1 of 1"),
        (2, -2.28, 18.4, "1 of 2", "1 of 1"),
        (3, -2.37, 10.5, "1 of 2", "1 of 1"),
        (4, -2.34, 8.1, "1 of 2", "0 of 1"),
        (5, -2.35, 12.6, "1 of 2", "0 of 1"),
    ]
    img = Image.new("RGB", (WIDTH, 1550), "white")
    d = ImageDraw.Draw(img)
    text_block(
        d,
        (60, 30, 1540, 135),
        "Run M: five timed-out attempts; worker runs continued past the caller boundary",
        size=36,
        bold=True,
        leading=46,
    )
    text_block(d, (60, 150, 1540, 190), "Each delivery: dispatcher 503; Auditor 504 at 2.999 s.")
    d.rectangle((60, 210, 105, 238), fill="#C9D3DD", outline=ACCENT, width=2)
    text_block(d, (120, 208, 650, 245), "Blue: A2A request")
    d.rectangle((750, 210, 795, 238), fill="#F3DADA", outline=FAIL, width=2)
    text_block(d, (810, 208, 1540, 245), "Red: worker run")
    text_block(
        d,
        (60, 265, 1540, 305),
        "Dashed: estimated caller boundary (request received + 3.0 s)",
        color=FAIL,
        bold=True,
    )

    def x(t):
        return 350 + (t + 6) / 40 * 1160

    for index, (attempt, start, end, models, tools) in enumerate(attempts):
        y = 330 + index * 210
        text_block(
            d, (60, y + 38, 320, y + 85), f"Attempt {attempt}", size=30, bold=True, leading=40
        )
        for tick in range(-5, 35, 5):
            d.line([(x(tick), y - 8), (x(tick), y + 100)], fill="#E1E6EB", width=2)
        # Dashes stop at the worker bar's bottom edge (y + 92), clear of the labels below.
        for offset in range(-8, 92, 22):
            d.line([(x(0), y + offset), (x(0), y + offset + 12)], fill=FAIL, width=3)
        d.rectangle((x(-3), y, x(0), y + 30), fill="#C9D3DD", outline=ACCENT, width=2)
        d.rectangle((x(start), y + 55, x(end), y + 92), fill="#F3DADA", outline=FAIL, width=2)
        text_block(
            d, (350, y + 115, 1540, y + 154), f"worker run ends {end} s after boundary", color=FAIL
        )
        text_block(
            d,
            (350, y + 153, 1540, y + 192),
            f"after boundary: models {models}, IAM tool {tools}",
            color=MUTED,
        )
    for tick in range(-5, 35, 5):
        text_block(
            d,
            (x(tick) - 42, 1380, x(tick) + 60, 1420),
            f"{tick:+d} s" if tick else "0",
            color=MUTED,
            align="center",
        )
    text_block(
        d,
        (60, 1445, 1540, 1540),
        "Totals after the boundaries: 6 of 10 model completions, 3 of 5 IAM tool calls.\n"
        "0 review records; dead-lettered. Post-hoc, read-only.",
        color=MUTED,
    )
    finish(img, "figure3-timeout.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    figure1()
    figure2()
    figure3()
    qa = HERE / "qa"
    qa.mkdir(exist_ok=True)
    (qa / "figure-layout.json").write_text(json.dumps(RECEIPTS, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(RECEIPTS, indent=2))
