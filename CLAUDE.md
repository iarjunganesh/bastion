# CLAUDE.md

Guidance for Claude Code working in this repository. Read the constraints before writing
code; several of them exist because violating them costs a day.

## What this project is

Bastion replaces the manual quarterly access review with three agents that continuously audit
a **live GCP IAM policy** — including the permissions of Bastion's own agents — remember what
a human already approved, and refuse to be instructed by the tickets they read.

Submission to the **Fortified Enterprise Fleet** track of the All Things Agentic Hackathon
(Google / Devpost). **Due Aug 31, 2026, 5:00 PM PT.** Judging runs Sept 1 – Oct 1.

**Current phase (2026-08-15): the fleet runs locally against live Google APIs; nothing is
deployed.** The repository is being prepared for its first untagged commit; no release exists.

On 2026-08-15 the seven DIY pillar modules were **deleted** (~3,460 lines across 27 files)
because each reimplemented a managed GEAP product ([ADR-003](docs/adr/003-pillars-on-geap.md)),
and the three agents were rewritten as ADK agents.

**All three pass/fail gates are now met in code that ran:**

| Gate | Evidence |
|---|---|
| Gemini 3.5+ via Vertex AI | 5 model calls in one investigation ([evidence 02](assets/evidence/02-gemini-investigation.md)) |
| One Google agent framework | `google-adk==2.7.0` — three `LlmAgent`s under a `SequentialAgent` |
| One Google Cloud infra service | Cloud Asset Inventory read the live IAM policy |

They were asserted as done in judge-facing documents for two days *before* they were true. That
is the failure mode this repository exists to argue against, so treat a green claim as owing
evidence, not the reverse.

**What exists:** three ADK agents, cross-department routing, Model Armor screening on
`before_model_callback`, an unregistered audit `BasePlugin`, 73 unit tests at 100% coverage, a six-job CI
workflow, **seven** ADRs (six merged away 2026-08-15), three documentation gates, and the
judge-facing document set.

**What does not exist:** any deployed Cloud Run service, any Agent Engine deployment, any Agent
Gateway, any registered Agent Registry entry, any Firestore database, any Pub/Sub topic, any
Cloud Trace span.

The latest counts-only state capture records four service accounts, one Model Armor template,
and one pre-existing Agent Registry entry; it records no deployed runtime, Gateway, database,
topic, or schedule. `scripts/capture_gcp_state.py` keeps counts separate and never commits
principal identifiers.

**Observed proof points so far.** The Model Armor block
([evidence 01](assets/evidence/01-model-armor-block.md)) and the real-IAM investigation with
cross-department routing ([evidence 02](assets/evidence/02-gemini-investigation.md)), plus the
Escalation Agent's IAM denial ([evidence 03](assets/evidence/03-escalation-agent-denied.md)).
These are proof points, not completed pillars: managed identity enforcement and the
memory-suppression run remain unfinished. `submission/SUBMISSION.md` is the ledger. The detail is
[ADR-006](docs/adr/006-pillar-coverage.md).

| Read this | For |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | The system as designed |
| [`docs/adr/`](docs/adr/README.md) | Why it is that way, and what may not change |
| [`submission/DEVPOST.md`](submission/DEVPOST.md) | **The ground truth.** The hackathon's own pages, quoted not paraphrased. Where any other file disagrees with it, it wins |
| [`submission/planning/03-build-plan.md`](submission/planning/03-build-plan.md) | What is supposed to be true today |
| [`submission/planning/08-audit-remediation-plan.md`](submission/planning/08-audit-remediation-plan.md) | The ordered post-audit build and verification contract |
| [`submission/SUBMISSION.md`](submission/SUBMISSION.md) | What may not yet be claimed |

## Live environment

Only commit details required to reproduce or evaluate the project. Project numbers, billing
account identifiers, balances, organization identifiers, and full principal emails stay in
private operator notes; they do not belong in a public access-governance repository.

| | |
|---|---|
| Project alias | `bastion-fleet-2026` |
| Model | `gemini-3.5-flash` at **`locations/global`** |
| Model Armor | `bastion-guardrail` at **`europe-west4`** |
| Regional target | `europe-north2` for compute and state; not yet deployed |
| Budget | Alert configured; account details intentionally omitted |
| Public URL | Not deployed |

The project's default Compute Engine service account holds a broad predefined role. It is an
unseeded, real finding class and must be referenced generically in public evidence. Never commit
the full principal or a raw IAM-policy response.

## Key commands

**There is no `make` on this machine** — not in PowerShell, not in Git Bash. The `Makefile`
remains the canonical description of *what* each step does, and CI runs on Linux where `make`
exists, but anything typed here needs the direct command. Every judge-facing document that
shows a command (`README.md` Quick Start, `CONTRIBUTING.md`) must carry a runnable form.

| Intent | Makefile target | What actually runs here |
|---|---|---|
| Lint | `make lint` | `ruff check .` then `ruff format --check .` |
| Types | `make typecheck` | `mypy agents registry model_armor observability` |
| Tests | `make test` | `pytest tests -q --cov --cov-fail-under=100` |
| Docs gate | — | `python scripts/check_docs.py` |
| Versions | — | `python scripts/check_versions.py` (offline); `--check-upstream` before a tag |
| Markdown | — | `npx markdownlint-cli2 "**/*.md"` (config `.markdownlint.json`) |
| Diagrams | — | `python scripts/render_diagrams.py` (light/dark variants + animated GIFs) |
| Live state | — | `python scripts/capture_gcp_state.py` — needs gcloud; CI cannot run it |
| Everything | `make ci` | run the five rows above, in that order |

`ruff format --check` is a separate CI gate from `ruff check`; a change that lints clean can
still fail the build on formatting. Run `ruff format .` before assuming a gate is green.

### The gcloud quota-project trap

`gcloud billing` and several other commands bill their API quota to a *quota project*, which is
not the same as `core/project`. After the stray projects were deleted, every billing command
failed with `PERMISSION_DENIED: Cloud Billing API has not been used in project 681255809395` —
a **deleted project**, and an error that reads like a permissions problem rather than a stale
config. The fix is `gcloud config set billing/quota_project bastion-fleet-2026`, already
applied. If a Google API call fails with `SERVICE_DISABLED` naming a project number you do not
recognise, check the quota project before believing the permission story.

## Non-negotiable constraints

**The audit target is real IAM, never invented rows.** The largest judging criterion (40%)
rewards removing real friction, and ties break on that criterion first. If a change makes
Bastion audit synthetic data as its primary source, it has traded away the project's main
advantage. A small seeded overlay to guarantee one on-camera finding is allowed and must be
disclosed; replacing the real source is not. See [ADR-001](docs/adr/001-real-iam-not-mock-data.md).

**Three agents: Orchestrator, Access Auditor, Escalation Agent.** Policy enforcement lives
inside the Orchestrator. Do not reintroduce a fourth agent — agent count is not graded and the
schedule was cut for a reason. See [ADR-002](docs/adr/002-three-agents.md).

**`GOOGLE_CLOUD_LOCATION=global` and `GCP_REGION=europe-north2` are different settings.** Gemini
3.5 has no regional endpoint. Collapsing them into one variable — the obvious-looking
simplification — makes every model call return a 404 whose message reads like a permissions
error. This is the most expensive misconfiguration available in this repository. There is no
Pro tier; 3.5 Pro is not available to this project. See [ADR-004](docs/adr/004-flash-only-global-endpoint.md).

**Never commit credentials or a raw IAM policy dump.** Service-account keys, ADC files, and
`getIamPolicy` output contain real principals and real email addresses. `.gitignore` covers the
common shapes, but the obligation is the author's, not the glob's. Anything reaching
`assets/evidence/` is redacted deliberately, by hand or by script.

**Never print a secret or a raw policy, and never run a command that returns one.** This is the
second half of the rule above, and the one `.gitignore` cannot help with. Terminal output is not
ephemeral: it lands in scrollback, in session transcripts, and in anything later pasted into an
issue or a screen recording. A principal shown once on camera is a principal to explain forever.

- The trap is not `echo $KEY` — nobody writes that. It is a **broad read of a store that happens
  to contain one**. `gcloud projects get-iam-policy` returns every real principal in the project.
  Same shape: `gcloud secrets versions access`, `gcloud run services describe` with its full env,
  `gcloud iam service-accounts keys list`, `cat .env`, `printenv`, `gcloud config list`.
- **Ask for the one field you need.** `--format="value(bindings.role)"` returns roles;
  `--format=json` returns identities. The narrow query is not merely tidier — it *is* the control.
- When output might contain principals, write it to the scratchpad and grep that file, or pipe it
  through the redaction step before anything is displayed.
- **Demo recordings are the highest-risk surface in this project**, because the whole point is
  showing a real policy on screen. The redaction pass runs before the capture is kept, never
  after it is uploaded.
- **If it happens anyway, say so immediately and plainly** — name what leaked, where it is now,
  and what must be rotated or re-recorded. A quietly-exposed identifier the author does not know
  about is far worse than an awkward correction.

**Cloud Run deploys with `min-instances=0` and an explicit `max-instances` cap**, and
authenticated by default. Exactly one service is deliberately public — the read-only findings
API behind the dashboard — and it never serves the raw policy.

**Do not write a claim before it is verified.** This project's entire pitch is auditability. A
README asserting a working Model Armor block before one has been observed is precisely the
failure the product is about. `submission/SUBMISSION.md` holds the list of claims not yet
earned; move an item out of it only after seeing the thing work.

**Every agent-to-agent call goes through the Gateway**, including when a direct call would be
shorter. The pattern is the point, and it is what the observability layer logs.

**Never reimplement a managed GEAP product.** Every pillar the track names has a managed
service behind it, and Bastion uses it ([ADR-003](docs/adr/003-pillars-on-geap.md)). This rule
was bought: `gateway/`, `registry/`, `runtime/`, `memory/`, `model_armor/` and `observability/`
were hand-rolled against products that already existed — `a2a-sdk` ships `AgentCard`, `Task`
and `TaskState`; Agent Gateway is `gcloud network-services agent-gateways`; Agent Registry
catalogs agents, tools and MCP servers; `--trace_to_cloud` is the tracer. **~3,460 lines were
deleted on 2026-08-15.** Before writing a pillar, check for the seam: `adk deploy cloud_run
--help` lists four of them as flags, and `google.adk.plugins.BasePlugin` has 15 hooks for
anything cross-cutting.

**Versions go stale silently, and the badge is what a judge reads.** ADK shipped 2.6.3 → 2.7.0
inside two days while six places in the repository asserted 2.6.3.
`scripts/check_versions.py` holds every document to `requirements.txt` offline on every push;
`--check-upstream` compares the pin against PyPI and must be run before any tag. A pin bump is
never complete until that gate is green — it touches `requirements.txt`, both README badge
blocks, and any ADR that names the version.

## Architecture in one pass

```text
Cloud Scheduler ─> Pub/Sub ─> Orchestrator ─(Gateway)─> Access Auditor ─> LIVE IAM
                                   │                          │
                                   │                    findings ─> Firestore ─> BigQuery
                                   │                          │
                              policy rules <── exception store ┘
                                   │
                                   └─(Gateway)─> Escalation Agent ─> human surface

Every model call screened by Model Armor. Every call traced into Cloud Trace.
Every agent under its own service account. The IAM policy read contains those
service accounts — Bastion audits itself.
```

Twenty GCP services, each with a job, listed in [ADR-003](docs/adr/003-pillars-on-geap.md).
That ADR also fixes the **cut order** if the schedule slips: BigQuery and Looker Studio go
first, then Cloud Asset Inventory, then Secret Manager. The judge path, Recommender API, and
Cloud Scheduler are not cut.

## Testing strategy

Tests exist to prove the claims the submission makes. **Coverage is 100% and the CI floor is
100%** — a floor below real coverage is a decoration, not a gate. If a change genuinely cannot
be covered, lower the floor deliberately and say why; never let it drift.

Four layers, each answering a different question:

| Layer | Question it answers | Run |
|---|---|---|
| `tests/unit/` | Does this function behave? | `make test-unit` |
| `tests/integration/` | Placeholder — deployed wiring | not yet available |
| `tests/security/` | Placeholder — end-to-end controls | not yet available |
| `tests/load/` | Placeholder — Gateway concurrency | not yet available |

`tests/conftest.py` patches the import-time clients — `firestore.Client()`, the Cloud Trace
exporter, `os.environ["GCP_PROJECT_ID"]` — at conftest import time, not in a fixture, because
pytest imports test modules during collection before any fixture runs.

**CI holds no GCP credentials, deliberately.** A workflow able to read a real IAM policy would
be a credential path into the project Bastion audits. Every outbound call is mocked; a test
that needs Google APIs is testing the wrong thing.

The IAM-denial contrast and direct Model Armor block are captured as evidence, but the security
test directory is empty. Model Armor is wired as a `before_model_callback`; outbound response
sanitization and the through-agent proof are still owed. No document may collapse those partial
proofs into an end-to-end security claim.

Python is type-hinted on public functions, `ruff` clean, no bare `except`. `make ci` runs lint,
typecheck, tests, coverage, markdown, and the documentation gate, and must pass before a commit.

## Release discipline — apply on every change, not at release time

- Annotated tags only, `vX.Y.Z`. The tag message names what became true, not what changed.
- Minor bump = a capability a judge could watch. Patch = a fix or captured evidence.
- **Never re-point a tag.** If `v0.6.0` was wrong, `v0.6.1` fixes it.
- `CHANGELOG.md` is updated in the change that earns the entry.
- When implementation invalidates a decision in `docs/adr/`, amend that ADR or add a new one
  in the same change. The code and the decision record are never allowed to disagree silently.
- The tag follows the proof. Verify, then tag — not the other way round.

### The staleness sweep — run it before any tag, and after any requirement changes

Documents rot in a specific, repeatable way here, and each shape below has actually occurred:

- **A claim that outran the code.** `README.md` asserted *"Google ADK — orchestrates the three
  agents"* with an ADK badge while nothing imported it, and `00-judging-matrix.md` said
  *"All agents call Gemini 3.5 Flash"* with zero call sites. Both were **pass/fail** rows.
  Grep for the capability, not the prose: `google.adk`, `generate_content`, an actual import.
- **Two files asserting opposite facts.** `00-judging-matrix.md` and `06-project-review.md` both
  said the rules page had been cleaned up; `DEVPOST.md` — the capture of that page — said it had
  not. **Where a planning file disagrees with `DEVPOST.md`, the capture wins.**
- **A count that drifted from the brief.** "Six pillars" above a seven-row table, propagated
  from one header into a second document. The brief names seven; the number is checkable.
- **A decision left open in prose after an ADR closed it.** "Dashboard OR Slack, pick one"
  survived in three files after ADR-003 fixed the service surface without Slack in it.
- **A resolved fork still described as pending.** ADR-003's half-day GEAP cap appeared as live
  future work in four documents the day after it was decided.
- **Superseded guidance still readable as current.** `01-architecture.md` told the reader to tear
  down after the demo while three other files said stay up through judging.

Grep candidates that catch most of it: the pillar count, agent count, participant count,
`make` invocations (there is no `make` on this machine), `get-iam-policy` shown as a command to
run unredirected, and any ADR number whose status changed.

The full ladder from `v0.1.0` to `v1.0.0`, with dates, is in
[`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md).

## Where things live

| Path | What it holds |
|---|---|
| `agents/` | The three agents; each folder is one deployable |
| `registry/` `runtime/` `memory/` | Pillars GEAP may replace — see [ADR-003](docs/adr/003-pillars-on-geap.md) |
| `identity/` `gateway/` `model_armor/` `observability/` | Pillars that stay DIY either way |
| `infrastructure/` | Firestore setup, investigation trigger, Cloud Run deploy |
| `docs/ARCHITECTURE.md`, `docs/adr/` | Judge-facing architecture and decision history |
| `submission/planning/00-07` | Working notes: judging matrix, build plan, storyboard, release plan |
| `submission/DEVPOST.md` | The hackathon requirements, captured verbatim — the source of truth |
| `submission/` | Devpost checklist; the Devpost prose arrives around `v0.9.x` |
| `assets/brand/` | Logo and banners, SVG, light and dark |
| `assets/architecture/` | `gcp-state.json` (measured build state) + the Level 1/2 SVG masters, their light/dark variants and animated GIFs. Level 3 is inline mermaid in `docs/ARCHITECTURE.md` |
| `assets/evidence/` `assets/screenshots/` | Captured proof — redacted, numbered in walkthrough order |

## Style

- Prose states what is true, then what is not yet true, in that order. Hedged language about
  an unbuilt feature reads to a judge as a feature that failed.
- Documents name the thing that actually ran. If the Model Armor fallback shipped, say
  fallback — claiming the managed service would be a false claim about a security control, in
  a security product, in a repository whose whole argument is auditability.
- **A diagram is a claim, and it is the first one a judge reads.** Every box carries a build
  state derived from `assets/architecture/gcp-state.json`, which `scripts/capture_gcp_state.py`
  writes by querying the live project — measured, never typed. That count excludes the service
  accounts Google creates for a project; counting them made an empty project read as two
  resources.
- **Levels 1 and 2 are hand-authored SVGs at 1920×1080; Level 3 is inline mermaid.** 16:9
  because a frame has to drop into an OBS scene without letterboxing. Box positions are placed
  by hand: auto-layout is what produced the unreadable version. Level 3 is a state machine and
  needs no layout decisions, so it stays a ` ```mermaid ` fence.
- **Theme handling is two files and a `<picture>`, never `prefers-color-scheme` alone.** An SVG
  loaded through an `<img>` tag — how GitHub renders every README image — does not inherit the
  page's colour scheme, so the media query resolves against the browser default and a
  light-mode reader gets the dark palette. Measured in a headless browser, not assumed. One
  master carries `PALETTE:LIGHT` / `PALETTE:DARK` sentinels; `scripts/render_diagrams.py`
  emits the variants and the GIFs. Never hand-edit a `-light` or `-dark` file.
- **The raster is an animated GIF, never a still PNG, and that is a Devpost constraint.**
  Devpost accepts JPG, PNG and GIF and does **not** accept SVG, so a still would throw the
  animation away at the one surface that cannot recover it. Gallery images cap at **5 MB**;
  `check_docs.py` fails above it, because a diagram that cannot be uploaded is a diagram no
  judge sees. All six render at roughly 0.5 MB.
- **This rule was bought.** A rendered diagram was committed showing Firestore, Cloud Run
  services, Pub/Sub topics, BigQuery and a Model Armor template on a day the project held one
  resource — the default Compute Engine service account. It looked professional and was
  entirely fictional. So **every committed SVG states its build state inside its own text**,
  and `check_docs.py` fails the build if one does not — a caption is separable from the image
  and the image is what gets screenshotted. A PNG cannot carry a checkable disclosure, so it is
  allowed only alongside the SVG it was rendered from.
- **Fewer boxes, more diagrams.** The unreadable version tried to show twenty services, the
  call path, memory feedback and telemetry at once. Split by C4 level — Context, then
  Container — and leave enabled-but-unwired services in ADR-003's table where they belong.

## Judging, in one paragraph

40% Innovation & Operational Utility (real friction removed autonomously — **ties break here
first**), 30% Architectural Discipline & Tech Stack, 30% Demo & Production Readiness. Scoring
is 1–5 per criterion, averaged, plus bonuses to a maximum of 6. Bonuses: blog 0.2, social post
0.2, each additional Google AI *model* 0.2 up to 0.6 — services do not count. The overview
names the models it means: **Gemma, Veo or Lyria**. A hosted URL is
*"highly encouraged"* but not pass/fail, and judges need not run anything, so the video carries
the submission. The overview is explicit that the app *"does not need to be publicly accessible
or live at the exact moment of submission or judging"* — proof it was built and deployed is
what counts, which is what makes teardown-after-capture safe rather than a risk to the score.
Full matrix in [`submission/planning/00-judging-matrix.md`](submission/planning/00-judging-matrix.md).

**Bastion is eligible for four prizes, not one**, and chasing the other three changes nothing
about the build: the track prize ($20k), **Individual/Hobbyist — Best Team/Solo Build** ($10k,
*two* winners, and this is a solo build), **Best Architectural Design** ($5k, two winners —
which is what the ADR set and `docs/ARCHITECTURE.md` already are), and the Grand Prize ($50k).
Best Multimodal UX is the one that would require redirecting the build; it is not pursued.
