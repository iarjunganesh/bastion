# Assets index — judge-facing evidence

Everything a judge needs to believe Bastion's central claim **without running the code**:

> A fleet of agents audits a real cloud project's access policy — including its own
> agents' permissions — remembers what a human already approved, and cannot be talked into
> approving anything by the tickets it reads.

Three parts of that sentence are only credible if they are *shown*: the policy is real, the
memory suppresses a re-flag, and the injection is blocked. This directory is where that
proof lives.

> **Status — empty.** Nothing here has been captured yet. This file is the plan, written
> before the evidence exists so the demo is recorded against a known shot list rather than
> assembled afterwards from whatever happened to be on screen.

## Layout

```text
assets/
├── architecture/     # Level 1/2 SVG masters + light/dark variants + PNGs, and gcp-state.json
├── brand/            # logo (static + animated), banners, SVG, light and dark
├── evidence/         # machine-generated JSON: policy dumps, findings, traces. Redacted.
├── screenshots/      # console frames, numbered in walkthrough order
├── demo-video/       # the sources the final cut was made from
└── demo-voiceover/   # narration script and takes
```

## The diagrams, and the rule they are under

An earlier version of this repository committed a handsome diagram, drawn with Google's own
Cloud product icons, showing Firestore, Cloud Run services, Pub/Sub topics, BigQuery, Looker
Studio, Firebase Hosting and a Model Armor template. On the day it was committed the project
contained **one** resource — the default Compute Engine service account, which Google creates
automatically. Every other box was an intention drawn as a fact, in the first artifact a
judge would have opened, in a repository whose entire argument is that its claims are
checkable. It was deleted rather than corrected.

The diagrams that replaced it are hand-authored and gated:

| Artifact | Where | Kept honest by |
|---|---|---|
| Level 1 (Context), Level 2 (Container) | `architecture/level-*.svg` — one master each, 1920×1080 | Every box carries a build-state marker, and **the image states its own build state in its own text**; `check_docs.py` fails the build if one does not |
| Level 3 (task lifecycle) | inline ` ```mermaid ` fence in `docs/ARCHITECTURE.md` | A state machine needs no layout decisions, so there is nothing to draw wrong |
| Light and dark variants, and the GIFs | `*-light.svg`, `*-dark.svg`, `*.gif` | `python scripts/render_diagrams.py` emits all of them from the master; CI fails if a variant is stale. **Never hand-edit one** |
| Build state per box (`●` `◐` `○`) | `architecture/gcp-state.json` | `python scripts/capture_gcp_state.py` queries the live project — the state is measured, never typed |

**Why two variants rather than one file with a media query.** An SVG referenced by an `<img>`
tag — how GitHub renders every README image — does not inherit the host page's colour scheme,
so `prefers-color-scheme` in the master resolves against the browser default and a light-mode
reader gets the dark palette. Measured in a headless browser, not assumed. GitHub's supported
answer is a `<picture>` element with two files, which is what the README and
`docs/ARCHITECTURE.md` use.

**Why the raster is an animated GIF and not a still PNG.** Devpost accepts JPG, PNG and GIF
and **does not accept SVG**, so the animation that carries these diagrams on GitHub cannot
reach a judge on the submission page in its own format. A still would have discarded the motion
at exactly the surface that cannot recover it. Devpost caps a gallery image at **5 MB** and
`check_docs.py` fails above that, because a diagram that cannot be uploaded is a diagram nobody
sees; all six render at roughly 0.5 MB at full 1920×1080.

Two things about that pipeline were measured rather than assumed, and both changed it:
Chromium's `--virtual-time-budget` does **not** advance SMIL — four renders at different
budgets came back byte-identical, so every "frame" was time zero — and seeking has to be
explicit via `setCurrentTime`. And batching fifteen frames into one tall page, which is seven
times faster, is **wrong**: two cells at the *same* animation time differed in 7% of their
pixels, which destroyed inter-frame compression and took the banner GIF from 0.5 MB to 6.5 MB,
over Devpost's cap. One launch per frame is byte-identical across runs, so that is what runs.

**Why 1920×1080.** The demo is recorded in OBS at 16:9. A 3.75:1 banner or an arbitrary-ratio
diagram has to be letterboxed into that scene, wasting most of the frame; a master authored at
the output ratio drops straight in. `brand/banner-16x9.svg` exists for the same reason — the
1200×320 pair stays, because that is the shape a README header wants.

Regenerate the measurement with `python scripts/capture_gcp_state.py`, and verify it with
`--check` before tagging. CI cannot run it — this repository holds no GCP credentials on
purpose — so `scripts/check_docs.py` enforces the parts that can be checked offline:
`gcp-state.json` exists, `docs/ARCHITECTURE.md` still cites it, every committed SVG discloses
its build state, and every PNG has the SVG it was rendered from beside it.

Two rules that do not lift:

- **An image may only draw what `gcp-state.json` says exists**, and must say so in its own
  text. A caption is separable from the picture; a screenshot or a Devpost paste drops it.
  That is why the disclosure lives inside the SVG, where `check_docs.py` can read it.
- **`gcp-state.json` records counts, never principals.** A state file naming a service
  account is the same disclosure as a committed policy dump. Both `check_docs.py` and a CI
  step fail on `@`, `roles/`, `user:` or `serviceAccount:` appearing in it. The count also
  **excludes the service accounts Google creates for a project** — counting them made an
  empty project read as two resources, which was one row from lifting the image gate.

**No image generator produced anything here, and none should.** Image models garble small
dense labels, and a misspelled service name in the one artifact the rules require would
undercut the submission's whole premise.

## The animated mark

`brand/logo-animated.svg` is hand-authored SMIL: a key turns in a shield-mounted padlock, the
shackle lifts, an audit sweep passes over the shield, and the lock closes again. The closing is
the point — an access review that leaves the door open has not finished.

Two constraints shaped it, and both are easy to get wrong:

- **SMIL, not CSS keyframes.** CSS animation is ignored inside an SVG loaded through `<img>`,
  which is how GitHub renders a README. A CSS version looks right in a browser tab and is a
  still image everywhere it is actually used.
- **No `prefers-color-scheme`.** Inside an `<img>`-loaded SVG it follows the *system* setting
  rather than the host page, so it cannot be trusted to match a README. Every colour is explicit
  and the shield supplies its own ground instead of borrowing the page's.

Motion is decoration, never information: every element is present and correct at the first
frame, so a reader who suppresses animation loses nothing. That is also why there is no
reduced-motion fallback drawing — the still frame *is* the logo.

This is a **brand** asset, not an architecture one. `check_docs.py` requires a build-state
disclosure inside every SVG under `architecture/`; nothing under `brand/` asserts a build
state, so nothing here can go stale against the live project. The one exception is
`banner-16x9.svg`, which names the phase in its own footer — it is a title card for a demo,
and a title card that says nothing about the build state is a title card that implies one.

## The shot list

Numbered in walkthrough order, matching
[`../submission/planning/02-demo-storyboard.md`](../submission/planning/02-demo-storyboard.md). Each is a real screen
capture; nothing here is a mockup.

| # | Shot | What it proves | Captured |
|---|---|---|---|
| 01 | Terminal: Pub/Sub trigger fires an investigation | The run is real and starts from outside the agent | ☐ |
| 02 | Cloud Run logs: Orchestrator picks it up and dispatches | Async runtime, not a synchronous script | ☐ |
| 03 | The same investigation still in progress after a visible time gap | "Weeks of async operation" in miniature | ☐ |
| 04 | Agent Registry: the fleet's A2A cards, **and Google's own Workspace Agent already listed beside them** | Cross-department discovery in a shared catalog | ☐ |
| 05 | A **redacted excerpt** of the IAM policy the findings came from | **The data is real** — the 40% criterion | ◐ [02](evidence/02-gemini-investigation.md) proves the read; the excerpt is not captured |
| 06 | Access Auditor's findings, including one against Bastion's own service accounts | The self-referential audit | ☐ |
| 07 | Memory Bank: a prior week's exception recalled, the finding *not* re-raised | Cross-session memory | ☐ |
| 08 | A mis-scoped call denied — the Escalation Agent refused IAM read | Zero trust is enforced, not documented | ☐ |
| 09 | Malicious ticket submitted; blocked before reaching Gemini | The moment judges remember | ✅ [01](evidence/01-model-armor-block.md) |
| 10 | Escalation Agent flags the ticket itself as suspicious | The system responds, it does not just refuse | ☐ |
| 11 | One investigation fans out to **several departments**, each notified separately | Cross-department routing at scale (graded) | ◐ [02](evidence/02-gemini-investigation.md) — 2 findings, 2 owning teams |
| 12 | Cloud Run dashboard: service list and live request count | Visible GCP deployment | ☐ |
| 13 | Vertex AI request log showing a real Gemini 3.5 Flash call | Mandatory-stack proof | ☐ |
| 14 | Cloud Trace: the full reasoning chain for the run just performed | Auditability — the actual product | ☐ |
| 15 | Cloud Logging: the structured audit records for the same run | The brief names *"audit logs **and** reasoning chain traces"* — two artifacts ([ADR-006](../docs/adr/006-pillar-coverage.md)) | ☐ |

Shots 05, 07, 08, and 09 are the load-bearing ones. If time runs short, they are the last
to be cut, and 08 and 09 are the two that must run clean on camera without a retake
visible in the edit.

## Rules for what lands here

**Redact before committing.** A real IAM policy carries real principals and real email
addresses. Raw dumps are gitignored; anything published here has been redacted
deliberately, and the redaction is part of the artifact, not a step someone remembers to
do. An access-governance project leaking an identifier discredits the whole submission.

**Machine-generated evidence and screenshots are separate.** `evidence/` holds what a
script wrote; `screenshots/` holds what a console showed. When they disagree, the JSON is
right and something needs re-recording.

**Capture during the run, not after.** An artifact assembled afterwards from memory is how
a file ends up disagreeing with the run that produced it. If a claim needs evidence, the
script that produces the claim writes the evidence.

**A shot that had to be staged says so.** If the seeded overlay from
[ADR-001](../docs/adr/001-real-iam-not-mock-data.md) produced a finding, that is disclosed
here and on camera.

## Video

The exported cut is uploaded to YouTube and is the artifact of record; this directory
carries the sources it was cut from. Raw takes live in a gitignored `.takes/` folder —
the ones that survive are copied into `demo-video/` under the names the demo script gives
them.
