# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning per
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An entry describes **what became true**, not which files moved. Historical sections preserve the
state known on their date; current proof and limitations are recorded together.

The current release process is in
[`submission/planning/07-release-plan.md`](submission/planning/07-release-plan.md).

## [Unreleased]

### Fixed — the public console called a fleet inventory an evidence verification

- `site/index.html` labelled its timestamp "Last evidence verification" while the value is
  `gcp-state.json`'s `captured_utc` — a count-only inventory of enabled APIs and deployed
  resources. It is now "Fleet inventory captured". The old wording also made the evidence look
  older than it is: the observations in evidence 11, 12 and 13 were captured 2026-08-25, two days
  *after* the date the site presented as the last verification.

### Added — the demo video is generated, measured, and assembled at 3:53

- `scripts/generate_demo_voiceover.py` is now the source of truth for the narration. It synthesises
  twelve beats with Google Cloud Text-to-Speech (Chirp3-HD, same project as the fleet), measures
  every clip, emits the shot table into
  [`submission/DEMO_SCRIPT.md`](submission/DEMO_SCRIPT.md), and cuts a 35-cue caption track.
- **The cut is 3:53**, measured rather than estimated: 199s narrated across twelve beats plus 34s
  of holds for live action. The first attempt measured 4:14 and the second 4:12 — the ceiling is
  hard and judges have said they stop at four minutes, so the timeline is built from real clip
  durations instead of word-count estimates. A closing sign-off over a card carrying the
  repository and console URLs was added last, spending three of the eleven spare seconds.
- **Chirp3-HD returns a different duration for identical text on each call** — one beat measured
  16.2s, 18.9s and 16.2s across three runs. The committed MP3 is therefore the stable artifact, and
  a SHA-256 sidecar per clip means regeneration happens only when the words change, so a casual
  re-run cannot re-jitter every timing the shot table depends on.
- Caption cues come from per-sentence probe clips scaled to each beat's measured length, because no
  timepointing is exposed for Chirp3-HD. That is a scaled measurement, not a word-count estimate,
  and the script says so rather than implying precision it does not have.
- The upstream ADK finding is now mentioned twice by design: one clause in the hook so a judge
  knows it exists, and the full story with the maintainer's confirmation in the close — which is
  where the internal winning plan wanted it, and where the slot had been sitting empty.
- `google-cloud-texttospeech==2.37.0` pinned, `requirements.lock` regenerated, `make voiceover`
  added. Enabling the API did not move the gated `21/21` count, which counts named services.

### Added — the demo video is assembled from the narration, not edited by hand

- `scripts/assemble_demo_video.py` cuts the video from the committed narration and per-beat screen
  recordings. It imports the beat list from `scripts/generate_demo_voiceover.py` rather than
  re-describing it, so the picture cannot drift from the sound: each beat occupies its measured
  clip length plus its declared hold, a long take is trimmed and a short one holds its final
  frame. `make assemble-video` added; the plan reproduces the locked 3:53 exactly. The sign-off runs the
  animated brand banner — already rendered at 1920x1080 because `render_diagrams.py` covers
  `assets/brand` — with the repository and console URLs composited over it at render time, in the
  clear band beneath the banner's own stats row. The overlay is applied to the video frame and
  never to the SVG: `assets/brand/` is hand-reviewed artwork whose pair must stay visually
  aligned, and a URL line belongs to this one video rather than to every surface the banner
  appears on. A flat text card was built first and worked; the banner is simply the better
  closing image, and it captures nothing either, so the redaction gate has no opinion on it.
- **A build containing any placeholder still is a scaffold, not the submission**, and the
  difference is structural rather than a note to remember. A scaffold is written to the ignored
  `assets/demo-video/build/`; only a fully live cut earns `assets/demo-video/bastion.mp4`, which
  sits inside the redaction gate's watched globs and so must be declared in `VIDEO_REDACTIONS` and
  frame-reviewed before the offline gate goes green. The hook narration promises live footage and
  a screenshot reel would not keep that promise.
- Placeholder stills render motionless and pixel-exact. A slow Ken Burns push was tried first and
  rejected: `zoompan` driven off a `-loop 1` input advances `on` per emitted frame, so the zoom
  raced past its ceiling and cropped the left edge — on a terminal capture that silently amputates
  the very counts the narration cites.
- `scripts/capture_site_hook.mjs` records the opening beat from the **live** public console at
  `bastion.arjunganesh.dev`, driving a real browser rather than panning a screenshot: the hero
  route diagram carries 24 `animateMotion` and 20 `animate` elements that a still would discard.
  It records the page viewport from a fresh profile, so no browser chrome or account photo can
  enter frame at all — the leak the promoted `.takes/` captures had to be cropped around. Two
  traps are documented in the script because both are silent: the site's `scroll-behavior: smooth`
  makes a per-frame `scrollTo` crawl a few hundred pixels instead of travelling, and the obvious
  fix — Playwright's `reducedMotion` — would switch off the very route animation being captured.
  The override goes through the CSSOM because the site's strict `style-src 'self'` rejects an
  injected style tag, and that policy is part of the submission rather than something to defeat.
- **The hook claimed more than the cut delivers, and the claim was the thing that was wrong.**
  It said *"Everything after this is live"*, which turned every unrecorded beat into a blocker
  and made the master filename unreachable — while the pictures it disparaged are the redacted
  console and terminal captures retained as evidence 11, 12 and 13, real output from real
  deployed runs. The line is now *"Everything after this was captured from the deployed
  fleet"*, which is what the video actually shows. `assets/demo-video/bastion.mp4` follows at
  3:53, declared in `VIDEO_REDACTIONS` and reviewed at all twelve beat boundaries. The
  rewording cost 2.4s, paid for by trimming the hook's hold, which had only been cloning the
  final frame of a 34.3s recording.
- **The opening stops to be read.** A single 27s glide was tried first and nothing landed: text
  moved past faster than a viewer could take in, which made a page full of substance feel skimmed.
  The pan now rests on five measured section offsets — the hero with its route animation running,
  the fleet counters, the governed production-data path, the remembered human decision, and the
  seven managed pillars, which arrives under "deployed on Google's managed agent stack".
- **Beats are joined by a cross-dissolve** and the film opens and closes on black. The surplus each
  segment carries to feed its dissolve is per *segment*, not per beat: a beat holding two shots
  contributes two dissolves, and compensating per beat left the picture finishing 0.4s ahead of the
  narration.
- `model` and `deliver` had shown the **same frame for forty consecutive seconds**, the longest
  static stretch in the cut. `deliver` now shows the `escalation_agent` and `escalation_gate`
  events completing, which is the receipt that beat's narration describes.
- A shot can be marked `final`, meaning it is the intended finished picture rather than a
  stand-in. Without it the completeness check could never pass: the two closing beats are
  graphics by design and will never have a live take, so the master filename
  `assets/demo-video/bastion.mp4` was unreachable no matter how much footage was recorded.
  `--check` now names the beats still outstanding and marks placeholders with a `*`.
- [`CAPTURE_RUNBOOK.md`](submission/CAPTURE_RUNBOOK.md) gains a recording-session order. The
  nine outstanding beats are not independent: one successful investigation supplies six of
  them, and the Model Armor probe fails an investigation by design, so recording it early
  would leave a failed run beside the successful one in every console view captured
  afterwards. It goes last.
- Beats carry **shots**, not just stills: held, looped, or scrolled. Every diagram placeholder is
  now the **animated**
  master rather than the still: the event beat runs the governed investigation flow, whose dots
  travel Pub/Sub to Eventarc to the durable ingress exactly as that beat's narration describes,
  and the close loops the fleet architecture before cutting to the Codecov report. Two page captures were promoted out of ignored `.takes/2026-08-29/` under the
  gallery runbook: browser chrome cropped away, the three account photos still present in page
  content masked through `REDACTIONS`, and both now covered by the redaction gate.
- The coverage page is shown and never narrated. 100% is evidence of test discipline, and this
  project's own upstream ADK finding is the standing proof that it is not evidence of correctness.
- `--burn-captions` sizes against libass's 288px reference height, where the repo's first attempt
  produced 67px captions across the architecture diagram. Captions otherwise stay a sidecar for
  the YouTube upload.

### Changed — upstream contribution status moved, in both directions

- A second Google collaborator replied on
  [#6854](https://github.com/google/adk-python/issues/6854) on 2026-08-27, describing the
  `output_key` half as expected behaviour and asking for a reproduction to test community PR
  #6859. A verified self-contained reproduction was supplied the same day, along with the answer
  to the `Workflow`-versus-`SequentialAgent` question that had been open since #6862 was closed.
- The semantics point is conceded and was never disputed: the report's ask was that the silent
  boundary become observable, not that per-agent sessions change. Recorded in
  [ADR-012](docs/adr/012-structured-findings-across-a2a.md) with the exact wording, because
  *"can be merged if the reviewer approves"* is a conditional about a review that has not
  happened and must never be cited as approval.
- Every judge-facing surface that states this status was moved from its 2026-08-25 check to
  2026-08-27: the README, the Devpost write-up, the article and social drafts, and the
  publication checklists.

### Changed — the fleet inventory was re-measured, and every dated asset re-stamped

- `gcp-state.json` re-measured 2026-08-27: **21/21 APIs and 39 resources, identical to the
  2026-08-23 capture**. Nothing about the fleet changed; only the disclosure date moved.
- The three architecture masters were re-stamped and every variant, GIF and still regenerated, and
  gallery image 01 recopied from the dark still, because
  `check_diagram_dates_match_state()` gates the footer date against the capture it quotes.
- The Devpost draft's uploaded architecture GIF is now one capture behind and needs replacing;
  tracked in [SUBMISSION.md](submission/SUBMISSION.md). The counts it shows are still correct.

## [0.6.0] — 2026-08-27

Every pinned dependency moved to the newest release the resolver allows, including the agent
framework. A minor release rather than a patch: nothing in `agents/`, `runtime/` or the pillars
changed, but the resolution the whole fleet is built on did.

### Fixed — the pre-tag version gate examined five pins and read as though it examined all

- `scripts/check_versions.py --check-upstream` only ever queried the five packages named in a
  document, because its purpose was catching a *false claim* — a README badge disagreeing with a
  pin. That is a good purpose and it is unchanged. What was missing is that the other eighteen
  pins were never looked at, so a run reporting one problem read as "everything else is current"
  when nothing else had been examined. Ten of them were in fact behind PyPI, and `v0.5.2` shipped
  without anyone seeing them.
- The check now surveys every pin across `requirements.txt`, `requirements-dev.txt` and
  `requirements-media.txt`, and reports the ones behind. Tracked packages still fail; the rest are
  advisory, because a pin one patch behind is not a lie about anything and failing on it would
  make the gate permanently red and therefore ignored. The module docstring now states what a
  pass does and does not promise.

### Changed — every pin moved to the newest release the resolver allows

- `google-adk` 2.7.1 → **2.8.0**, plus `google-auth` 2.57.0, `google-cloud-firestore` 2.29.0,
  `google-cloud-bigquery` 3.44.0, `google-cloud-logging` 3.16.3,
  `opentelemetry-exporter-gcp-trace` 1.15.0, `python-dotenv` 1.2.3, `ruff` 0.16.5 and `mypy` 2.3.1,
  with `requirements.lock` regenerated.
- **`opentelemetry-api` and `opentelemetry-sdk` stay at 1.42.1, and 1.44.0 is unreachable rather
  than declined.** `google-adk==2.8.0` declares `opentelemetry-api<=1.42.1` and
  `opentelemetry-sdk<=1.42.1`, so "everything latest" is not a satisfiable resolution while the
  framework is pinned at all. The resolver said so; this is not a judgement call. One incidental
  benefit: the trace path that
  [evidence 13](assets/evidence/13-current-route-trace.md) rests on did not move.
- Verified on the new resolution before the pins were committed: 321 tests at 100% statement and
  branch coverage, Ruff, the type checker, every documentation gate, and a local A2A round-trip
  with a `RemoteA2aAgent` served over HTTP. [ADR-005](docs/adr/005-adk-as-the-agent-framework.md)'s
  import claim was re-run against 2.8.0 rather than re-dated, as it was for 2.7.1 before it.
- The migration trigger still has not fired: 2.8.0 changes neither `SequentialAgent`'s deprecation
  nor `Workflow`'s eligibility as an `LlmAgent` sub-agent. `SequentialAgent` remains
  deprecated-but-required.

### Still deliberately not claimed — the deployment did not move with the pin

**The repository now pins 2.8.0; the managed Agent Runtime and both Cloud Run workers still run
the 2.7.1 resolution `v0.4.0` deployed.** Nothing in the evidence set was re-observed, so every
"deployed and verified" claim describes the older resolution until both surfaces are redeployed
and re-verified live. Redeploying will mint new Cloud Run revisions, and
[evidence 11](assets/evidence/11-current-route-correlation.md) and
[12](assets/evidence/12-agent-mediated-model-armor-refusal.md) name the current ones explicitly, so
that step also obliges re-capturing evidence 11, 12 and 13 and recomposing gallery images 03, 04
and 05. The gap is recorded rather than closed by rewording, and ADR-005 carries the full cost.

The two open observations are unchanged, and no demo video exists yet.

No production code changed.

## [0.5.2] — 2026-08-27

The judge-facing image set existed only as raw takes, and the one promotion that had happened
copied a light architecture still into a gallery of dark console captures. This release composes
the five gallery images, and adds the gate that decides whether a promoted file is safe to publish.

### Added — a promoted image cannot reach Git without a recorded review decision

- Added `scripts/redact_evidence.py`. Every judge-facing PNG and MP4 must appear in `REDACTIONS`
  or `VIDEO_REDACTIONS`, including files reviewed and deliberately left unmasked, which are
  declared with an empty tuple. Undeclared media fails the check. PNG masks are applied losslessly
  with Pillow; MP4 masks are burned in with local FFmpeg and verified at the start, middle and end.
- Added a `media-safety` CI job, `make redact-evidence` and `make media-check`, and a
  `requirements-media.txt` pinning `Pillow==12.3.0`.
- `scripts/render_diagrams.py` now emits a dark 1920x1080 architecture still alongside the light
  one. The light still re-rendered byte-identical, so the renderer's determinism is unchanged.

### Fixed — the operator's account photo was about to be committed

- `assets/evidence/screenshots/` held five captures copied verbatim from `.takes/`, referenced by
  no evidence record and outside the redaction gate's globs. Two carried the signed-in operator's
  Google account photo in the console header. The gate now covers that directory, and both photos
  are masked. A supporting capture is promoted to back a written record rather than to be looked
  at, which is why it is the likelier place for this to happen than the gallery.

### Added — the five-image Devpost gallery

- All five are 1920x1080 and dark, including the architecture still: the sequence is otherwise
  entirely dark console and terminal captures, and one light panel reads as a different project.
- No gallery image needed a mask. Browser chrome, the project-bearing URL and the operator avatar
  were cropped out rather than covered, and every value that remains is already published in an
  evidence record.
- The runbook now carries a composition rule: an image may be cropped, may stack contiguous strips
  of one capture with dead space removed, and may carry a drawn label, but may not reorder, retime
  or recolour evidence, and may show no number absent from a retained record.

### Still deliberately not claimed

Three captions are narrower than the runbook originally planned, because the panels they assumed
were never captured. Image 02 shows the governed catalog but not per-agent ownership, skill,
classification or approval, which live on an uncaptured Agent Card detail view. Image 04 shows
inline screening but not the Auditor-permitted/Escalation-denied IAM split. Image 05 shows
correlation, minimization and retention but not cross-week human-decision continuity. Each
underlying claim keeps its existing status from evidence 05, 03 and 10 respectively; what narrowed
is what a screenshot proves.

The two open observations are unchanged: a managed Gateway refusal of an unregistered caller, and
a watched timeout/retry/dead-letter sequence. No demo video exists yet.

`google-adk` stays pinned at **2.7.1** although PyPI now carries 2.8.0, so
`scripts/check_versions.py --check-upstream` fails on this pin by design. 2.8.0 does not change
`SequentialAgent`'s deprecation or make `Workflow` usable as an `LlmAgent` sub-agent, so
[ADR-005](docs/adr/005-adk-as-the-agent-framework.md)'s migration trigger has not fired; two of its
additions land on `RemoteA2aAgent` task mode and Model Armor guardrails, which are the fleet's two
most sensitive seams and would need a live re-verification rather than a pin bump. The deployed
fleet runs 2.7.1. The reasoning is recorded in ADR-005 rather than left to a commit message.

No production code changed. The deployed fleet is the one `v0.4.0` deployed.

## [0.5.1] — 2026-08-25

A dated claim on a judge-facing image disagreed with the measurement it quoted, and nothing in the
repository could see it. This release fixes the date, closes the gap that let it drift, and makes
the public console honest about how old its snapshot is.

### Fixed — the diagram date was ungated, and it had drifted

- Every architecture asset was stamped `Build state · 2026-08-22` while
  `assets/architecture/gcp-state.json` recorded a capture of `2026-08-23T17:22:39Z`. The count in
  that footer was gated by `check_diagram_footers_match_state()`; the date beside it never was, so
  it went stale silently — including in
  `enterprise-fleet-architecture-light.png`, the image uploaded to Devpost as the required
  architecture diagram. Re-stamped and regenerated: three masters, six theme variants, nine
  animated GIFs, and the PNG.
- Added `check_diagram_dates_match_state()` to `scripts/check_docs.py`. A diagram's build-state
  date must now equal `gcp-state.json`'s capture date, exactly as its resource count already must.
  A count that agrees with a measurement taken on another day is a coincidence rather than a
  grounded claim, and the footer's entire purpose is disclosure.

### Added — the console shows how old its evidence is

- The verification stamp now carries a relative age beside the absolute UTC time. It is computed
  in the browser from the `datetime` attribute `check_site.py` already pins to `captured_utc`, so
  there is no second source and no request. The point is to make staleness visible rather than
  leave a reader subtracting dates.
- The footer names the release the page was built from, and `check_release_stamp()` fails if that
  string disagrees with `pyproject.toml`. It is a gated literal rather than a build-time
  substitution on purpose: the static build stays byte-identical to its reviewed source, so
  `check_site.py` can keep failing on any drift between what was inspected and what deploys.

### Unchanged

No production code, no deployed resource, and no evidence claim changed. The counts the corrected
footers quote — 21/21 APIs and 39 resources — are the same measurement they always were; only the
date beside them is now the one that measurement was taken on.

## [0.5.0] — 2026-08-25

Pre-media release. No production code changed: the fleet running on `bastion-fleet-2026` is the
same one `v0.4.0` deployed. What became true is that five of seven outstanding observations were
watched and retained, and the repository stopped describing them as pending.

### Added — five observations closed, and the proof they produced

- Added [evidence 11](assets/evidence/11-current-route-correlation.md): one investigation
  completed across the managed Runtime, the deployed Access Auditor, the deterministic policy
  gates, and the deployed Escalation Agent, assembling 28 unique payload-free events across three
  invocation ids under a single investigation id. A count-only companion probe measured 62 live
  IAM bindings, 3 deterministic findings, 2 canonical owning departments, and zero raw IAM fields
  at the model boundary (P0.8, P0.9).
- Added [evidence 12](assets/evidence/12-agent-mediated-model-armor-refusal.md): the deployed
  `before_model_callback` refused an approved injection sample sent through the Access Auditor's
  authenticated A2A surface. A benign control completed; the sample's task failed closed with
  `policy_match`, and zero model submissions, completions, or tool calls followed. This is the
  agent-mediated refusal that [evidence 01](assets/evidence/01-model-armor-block.md), a direct
  managed-template probe, was never proof of (P0.6).
- Added [evidence 13](assets/evidence/13-current-route-trace.md): one connected 22-span Cloud
  Trace over 1m 5.401s covering both A2A hops with their agent-card fetches, the Firestore
  exception lookup nested inside `policy_step`, and `escalation_gate`. D2's predicted risk — that
  IAP-mediated egress might impair the Runtime's OTel export and cost this capture — did not
  occur (P0.7).
- Added [10-reproducibility.md](submission/planning/10-reproducibility.md): a measured clean-clone
  run rather than a claim about one. A fresh unauthenticated clone reaches 321 passing tests at
  100% configured core coverage with every gate green and zero untracked files (P1.3).
- Added [11-claim-matrix.md](submission/planning/11-claim-matrix.md), the internal gate that stops
  public copy claiming more than the evidence shows. Eight of ten rows are now fully claimable;
  two remain narrowed.
- Added the judge-facing submission package: a paste-ready Devpost narrative, a field-by-field
  form worksheet, an ordered capture runbook, a shot-by-shot demo script, and technical-article
  and social drafts. None is published.
- Renamed the architecture masters from the internal `level-0/1/2` taxonomy to semantic names,
  added the required static 1920×1080 PNG and a 3:2 thumbnail, and regenerated every theme
  variant and GIF.

### Changed — the documentation caught up with what is now observed

- Model Armor and Agent Observability in [ADR-006](docs/adr/006-pillar-coverage.md) moved from
  configuration and test proof to observed proof, citing evidence 11, 12 and 13.
- Closed captures 2, 3, 4 and 5 in
  [09-capture-backlog.md](submission/planning/09-capture-backlog.md). Capture 4 closed with its
  boundary stated rather than smoothed: a refusal *is* recorded under the audit contract, but it
  comes from the Model Armor probe, not from the correlated investigation itself.
- Sharpened D2 with a second measurement. The 12 IAP denials on 2026-08-25 fell in a single
  1.2-second burst ending three seconds before the investigation's root span, which then ran
  clean. The denials belong to instance cold start, not the request path.
- Marked [evidence 02](assets/evidence/02-gemini-investigation.md) superseded as current-route
  proof and re-pointed ADR-004, the ADR index, and the judging matrix at evidence 11 and 13.
- Resolved the two coexisting IAM binding counts: 62 is current, and evidence 09's 52 is retained
  as its own dated measurement rather than overwritten.
- Superseded `02-demo-storyboard.md` with [DEMO_SCRIPT.md](submission/DEMO_SCRIPT.md), which had
  conflicting timings.
- Synchronised the public evidence console: refreshed the stale binding count and added cards for
  the refusal and the trace.

### Fixed — an upstream claim that went stale between a check and a release

- **PR `google/adk-python#6862` was closed unmerged on 2026-08-24**, and five documents still
  described it as open. A Google maintainer declined it in favour of community PR `#6859`,
  because `SequentialAgent` is deprecated and *"the session state boundary across A2A is a
  general transport property rather than an issue specific to `SequentialAgent`."* That is a
  maintainer confirming the finding and deciding where the fix belongs — not an accepted fix and
  not a rejected report. Issue `#6854` and PR `#6859` remain open. Nothing is merged. Corrected
  in README, [ADR-012](docs/adr/012-structured-findings-across-a2a.md), and the article, Devpost
  and social drafts.
- Corrected [10-reproducibility.md](submission/planning/10-reproducibility.md), which cited commit
  `4fe8d59` — squashed and force-pushed away, so the hash no longer resolved in a fresh clone. A
  reproducibility record naming an unreachable commit proves nothing, so it was re-run against
  `c81b4af` rather than re-pointed.
- Removed pre-capture wording that had become false: the Devpost narrative no longer says the
  agent-mediated refusal *"remains a named capture"* or that *"the immediate next step is
  evidence."*
- Documented the py-launcher gap in README and CONTRIBUTING: `py -3.12` resolves only a CPython
  registered with the Windows launcher, which uv, pyenv-win, conda and the Microsoft Store are
  not.

### Still deliberately not claimed

Two observations remain open and their claims stay narrowed: a managed Gateway refusal of an
unregistered caller, and a watched timeout/retry/dead-letter sequence. Every observable IAP denial
in this project resolves to `unregisteredEndpoint` with an empty `authenticationInfo`, which is
D2's residual platform behaviour rather than a caller being refused; producing the intended
refusal would require deploying a modified Runtime, which this stage forbids. No demo video and no
gallery image exists yet.

## [0.4.0] — 2026-08-23

### Added — a model cannot alter the authoritative finding set or skip a required delivery

- Added `validate_auditor_fidelity`, a deterministic post-model check that compares the Access
  Auditor's structured answer against `audit_iam_policy`'s own canonical output by `finding_id`.
  A model may write only the bounded `rationale` field; any other mismatch raises
  `AuditorFidelityError` with a payload-free, bounded reason (P0.1).
- Replaced the Escalation Agent's `LlmAgent` with a deterministic `BaseAgent`. It parses the
  Orchestrator's validated routing envelope, validates every department bucket completely before
  any delivery, and calls the fixed-schema notification function exactly once per routed
  department — with no model or tool declaration in the path to skip, redirect, or fabricate one
  (P0.2).
- Added `escalation_gate`, a fifth Orchestrator step that refuses to report an investigation
  complete unless every routed department's delivery was confirmed by the Escalation Agent's own
  reply (P0.3).

### Fixed — two more silent A2A content surprises, found deploying the above

- The Escalation Agent's inbound routing envelope was unreadable on the deployed A2A path: the
  correct channel is `InvocationContext.user_content` (the callee's current turn), not session
  history, and even that channel required stripping an ADK-generated `"[agent] said: ..."`
  history-attribution prefix before the JSON would parse.
- Documented, not fixed in this repository: `RemoteA2aAgent` converts a failed remote task into
  an ordinary, error-free, empty event rather than an exception, and `infrastructure/deploy.sh`
  alone does not redeploy the Orchestrator's actual agent graph (a separate Agent Runtime
  surface, updated by `infrastructure.deploy_agent_runtime`). Both compounded to make the first
  regression above invisible end-to-end before `escalation_gate` existed to catch it. Full account
  in [ADR-012](docs/adr/012-structured-findings-across-a2a.md)'s 2026-08-23 amendment.

### Changed — documentation reconciled with the deployed, re-verified fleet

- Corrected the fleet composition described in `ADR-005`, `ADR-README`, `ARCHITECTURE.md`, and
  `SECURITY.md`: one `LlmAgent` (the Access Auditor) and four model-free `BaseAgent` steps, not
  three `LlmAgent`s and two deterministic steps.
- Corrected the fleet-scalability claim in `README.md`: adding a new institutional agent is
  governed (Registry, Gateway, identity, and a deliberate orchestration change), not "one
  registration, no orchestrator change."
- Documented why `FirestoreDurableStore` keeps its blanket coverage exclusion in `CONTRIBUTING.md`.
- Re-confirmed the 2026-08-19/2026-08-22 approved-exception suppression
  ([evidence 10](assets/evidence/10-cross-week-suppression.md)) on the redeployed, deterministic
  path: exactly one human-review record created, for the correct department, with the suppressed
  department still paged zero times.
- Added `docs/ARCHITECTURE.md`'s missing "Request path" section using the existing
  `level-0-request-path` diagram, already used in `README.md` but absent from the deeper
  architecture reference.
- Refreshed the upstream `google/adk-python` issue/PR attribution (`#6854`, `#6859`, `#6862`) live
  via `gh`; all three remain open.

## [0.3.0] — 2026-08-23

The public evidence plane is live at
[`bastion.arjunganesh.dev`](https://bastion.arjunganesh.dev/). Its signed-out production behavior,
custom domain, HTTPS redirect, security headers, desktop/mobile layouts, theme variants, reduced
motion, navigation, 404 response, and browser network isolation were observed before release.

### Added — a public evidence plane without a public agent

- Added a dependency-free static evidence console under [`site/`](site/README.md). It reuses the
  reviewed brand and architecture light/dark SVG and GIF variants, follows the system theme,
  supports a local theme override, and replaces animation with matching SVGs under reduced motion.
- The browser receives only sanitized committed content. It has no server runtime, environment
  variable, GCP credential, private service origin, or production API fallback. Vercel is the
  presentation plane; the operational fleet remains IAM-private on Google Cloud. Railway is not
  part of the path.
- Added `scripts/check_site.py` and a CI build gate that scan the deployable bundle for private
  origins, credentials, raw principals/bindings, and snapshot drift before publication.

### Added — keyless, authority-bounded deployment

- Added a manual GitHub Actions deployment workflow backed by Workload Identity Federation. The
  short-lived deploy identity can update code and act as the three workload identities, but it
  cannot change IAM authority or impersonate the break-glass approver.
- Public workflow output redacts Cloud Run origins, service-account addresses, and IAM principals;
  `deploy.sh` suppresses commands that would otherwise print the resulting IAM policy.

### Changed — judge-facing proof follows the measured fleet

- Added a reviewed Level 0 request-path master and regenerated theme/GIF variants from existing
  visual assets. Diagram gates now bind displayed resource totals to the count-only live snapshot
  and reject retired topology claims or animation paths that cross a component.
- Recaptured 21/21 named APIs and 39 enumerated resources after adding the federated deploy
  identity. The Workload Identity pool and provider remain explicitly outside that counter.
- Reworked the README presentation and badge targets while retaining its earned architecture,
  evidence, limitations, and reproducible setup. Release documentation now distinguishes the
  static public evidence plane from the private GCP runtime.

### Fixed — release claims that had outlived their evidence

- Removed present-tense ADR and backlog statements that still described the pre-`v0.2.0` screening
  outage and unobserved suppression. Their historical diagnoses remain, with amendments pointing
  to the deployed successful run and evidence 10.
- Removed unsupported continuous-cadence wording while the measured fleet has zero Scheduler jobs;
  current behavior is described as event-driven.
- Qualified current 100% claims as configured core statement and branch coverage rather than an
  assertion about excluded infrastructure adapters or every repository line.

### Verified — hosted release boundary

- The canonical custom domain returns the static evidence console without Vercel authentication;
  generated project and branch aliases are not published as judge-facing URLs.
- Browser inspection observed only same-origin site assets and data. No request reached a private
  Cloud Run, Agent Runtime, Google Cloud API, Railway service, or other operational backend.
- Light and dark modes select their reviewed GIF variants; reduced motion selects matching static
  SVGs and runs no animation.

## [0.2.1] — 2026-08-22

A patch release with one defect and one capture. 0.2.0 fixed session state failing to cross the
A2A boundary in one direction; this fixes the other direction, which turned out to be the reason a
human-approved exception had never once been honoured in production.

### Fixed — a policy decision now survives the escalation hop

- An approved exception was scored as `suppress` and escalated anyway. Nothing was wrong with the
  policy: `apply_policy_rules_with_memory` marked it and `route_by_department` excluded it. Both
  results were discarded one hop later.
- `PolicyStep` yielded an event carrying only `state_delta`, and ADK builds the outgoing A2A
  message from `event.content.parts` — so a state-only event contributes nothing to it, and the
  most recent content the Escalation Agent saw was still the Auditor's report. The routing now
  travels as event content as well as state: state is what the gate reads in-process, content is
  the only thing that crosses.
- Sending the routing was necessary but not sufficient. `route_by_department` returned counts and
  reasons but **no finding ids**, so the Escalation Agent had to take ids from the raw report even
  when it read the routing. Each bucket now carries its own `finding_ids` — the only
  decision-filtered list of ids in the system. A finding without an id is counted and no id is
  invented for it, because a fabricated id matches no finding and can key no exception.
- **This is a class, not an incident.** 0.2.0 fixed the Auditor's report failing to reach the
  policy step; this fixes the policy step's decision failing to reach escalation. Same root cause,
  opposite direction, and any future step that assumes session state crosses A2A will fail the
  same way — silently, and only in the deployed topology.

### Observed — the track's cross-week obligation, with a real elapsed gap

- [Evidence 10](assets/evidence/10-cross-week-suppression.md): an exception approved **2026-08-19**
  suppressed its matching finding on **2026-08-22**, through the deployed Runtime and both
  workers. `notify_human` fired **once**; the department owning the suppressed finding received no
  notification at all rather than an empty one.
- The immediately preceding runs that day delivered the same finding to that department while the
  same exception was already live. That is the before-and-after this fix is measured by.
- This was the one open claim whose critical path was elapsed time rather than effort, and the
  repository deliberately did not claim it until now. The gap is three days, not a calendar week,
  and the write-up says so. Expiry firing has not elapsed and remains covered by tests only.

### Changed — the suite is 251 tests

- Up from 247, at 100% statement and branch coverage. The new tests pin both halves of the defect:
  that the routing leaves `policy_step` as content, and that a suppressed finding is absent from
  what crosses to escalation.

## [0.2.0] — 2026-08-22

The fleet was deployed at 0.1.0 and then watched. This release is what watching produced: seven
defects that no offline gate could have found, four new decision records, and a screening outage
whose cause was the fleet's own dispatch message. Two defects remain open; they are named here
rather than left for a reader to discover.

### Observed — one investigation, end to end, under a single correlation id

- 2026-08-22 16:49Z, against the live project: **34 audit records sharing one `investigation_id`**,
  spanning the managed Runtime and both Cloud Run workers. `investigation.run started` →
  Auditor (two model calls, `audit_iam_policy`, completion) → **`policy_step` ran and completed** →
  **`policy_gate` ran and completed** → Escalation Agent → `notify_human` **twice, to two
  departments** → `investigation.run completed`. No refusal, no error, no truncation.
- This is the first trail in the project's history that can be assembled across the A2A boundary,
  and it retires D6. D1's fix is observed rather than only tested: the deterministic step and its
  gate both executed inside the deployed Runtime.
- `python -m infrastructure.smoke_test` passes end to end — fleet, findings IAM and idempotency,
  durable async state, and Runtime.
- Not claimed: a refusal has not been captured on this route, so capture 4 in the observation
  backlog remains open. A trail of successes proves nothing about the guardrails.

### Fixed — the production smoke test exercises the path production actually uses

- `verify_runtime` let its client become a temporary. `Client(...).agent_engines.get(...)` leaves
  the client unreferenced, so garbage collection could close its aiohttp session mid-stream and
  surface as `assert self._connector is not None` deep inside aiohttp — an error naming nothing
  about ownership, which reads like a fleet fault during a release gate. `agent_server` had
  already learned this; the smoke path never had the lesson applied.
- It also sent an imperative sentence, which is the shape the dispatcher stopped sending because
  Model Armor scores an instruction addressed to an agent like a real injection. A smoke test
  that sends what production is forbidden to send is exercising a path no deployment uses. It now
  sends the same structured payload and run-config metadata as dispatch.
- Not unit-tested, and deliberately so: `infrastructure/smoke_test.py` requires `gcloud` at import
  and is outside the coverage source, so a test for it would be skipped on CI rather than run. It
  is verified by the gate itself passing.

### Fixed — the Auditor's report reaches the policy step over A2A

- Found by deploying, not by testing, and it is the defect this release exists to catch.
  `output_key` writes into the session of the agent that *declares* it. In-process that is the
  Orchestrator's own session, so `audit_findings` was simply there — for every local run, every
  integration test, and every CI job. Over A2A it is the **worker's** session, which never crosses
  back, so the deployed Orchestrator read an empty key.
- Observed 2026-08-22 on the live fleet: the Auditor produced a complete sub-trail — two model
  calls, `audit_iam_policy`, a clean completion — and `policy_step` then refused with *"the Access
  Auditor returned no structured report; refusing to score nothing"*. No test could have reached
  this, because the state key is populated in exactly the topology tests run in.
- This is the true cause of D6, and it reframes D1. The old model-driven policy step read the same
  empty key and escalated anyway, which is why humans were paged about findings no threshold had
  scored: the model was not merely retyping findings, it was inventing them from nothing. The
  deterministic step turned a silent fabrication into a visible refusal, which is precisely what
  [ADR-010](docs/adr/010-policy-enforcement-gate.md) promised it would do.
- `policy_step` now falls back to the Auditor's A2A reply when the state key is absent. Reading
  that reply is sound rather than a workaround **because** of `output_schema`: the content is
  validated `AuditReport` JSON, not prose to be interpreted. A reply that fails to parse is
  skipped rather than guessed at, and skipping everything still fails closed.

### Fixed — one investigation can be assembled into one trail

- ADK mints a fresh `invocation_id` per agent run, and a worker reached over A2A is a separate run
  in a separate process, so a single investigation scattered its audit records across three
  unrelated ids. The audit docstring claimed `invocation_id` grouped an investigation; it groups
  one agent run, and only inside that run.
- The durable event id is seeded into `RunConfig.custom_metadata` at dispatch and forwarded to each
  worker as A2A request metadata, so every record carries the same `investigation_id`. Metadata
  rather than message content: the id must reach the far side without becoming something a model
  reads, restates, or can be talked into changing.
- `event_id` is the correlation key rather than `context_id` because `InvestigationEvent` validates
  it as a UUID while `context_id` is only checked non-empty. The value crosses A2A from a peer and
  lands in a 365-day retained bucket, so an unvalidated field would be a channel for arbitrary text
  into the compliance log. The audit boundary re-validates the shape regardless of what upstream
  sent, and records `unknown` rather than writing through.

### Fixed — the deterministic threshold cannot be skipped, and findings are not retyped

- On 2026-08-21 two investigations escalated to humans with no threshold ever applied, and the
  lifecycle recorded `completed` with no error anywhere. Enforcement did not fail closed; it
  disappeared. `policy_step` was an `LlmAgent` whose deterministic tools a model chose to call, so
  a Model Armor refusal of that model call meant the tools never ran and the sequence continued.
- Even when the call succeeded the model was **retyping** the findings — reconstructing opaque ids,
  categories and scores from the Auditor's prose. A fabricated category is why `notify_human` failed
  intermittently; a mistyped 24-hex id is why an approved exception would never have matched.
- `policy_step` is now a `BaseAgent` calling the threshold and the routing catalog directly. There
  was never a decision here for a model to make. Because it reaches no model it declares no tools
  and needs no screening. [ADR-010](docs/adr/010-policy-enforcement-gate.md).
- The Auditor answers in a validated `AuditReport` schema, so findings cross A2A as data rather than
  prose, and a missing or misshapen report fails closed instead of scoring an empty list.
  [ADR-012](docs/adr/012-structured-findings-across-a2a.md). Whether the deployed Gemini call
  honours `output_schema` is enforced at the model layer and is **not** proven by the offline suite.
- `PolicyEnforcementGate` refuses to escalate unless the deterministic path left its own result in
  state. An `output_key` is not proof: ADK stores a screening refusal under that key too.

### Fixed — inbound screening covers tool results, not only the prompt

- `before_model_callback` read only text parts, so everything a tool returned reached the model
  unscreened, leaving the shorter and likelier path as the one neither callback looked at.
- Not theoretical: `apply_policy_rules` returns `exception_policy_version`, an operator-supplied
  string the findings API writes and the policy step hands straight to a model — free text crossing
  a trust boundary inside exactly the part type the screen skipped.
  [ADR-011](docs/adr/011-inbound-screening-covers-tool-results.md).

### Fixed — a declared-but-empty environment variable is treated as absent

- `os.environ.get(key, default)` returns an empty string for a key that is present and empty, so
  `BASTION_INVESTIGATION_LEASE_SECONDS` reached `int("")` and durable ingress died on its first
  delivery — at request time rather than startup, so the service reported healthy and failed only
  under traffic.
- The suite had the same defect from the other side via `os.environ.setdefault`: nine tests failed
  for contributors who export their environment, while CI — which exports nothing — stayed green. A
  gate that only passes on machines with an empty environment is not verifying what it appears to.

### Fixed — the Runtime screens and egresses under its own identity

- Agent-to-Anywhere refused every Runtime call as incorrect or unregistered. Three separate causes
  wore one error message.
- The managed Runtime does not run as `orchestrator-sa`; it runs as a GEAP Agent Identity
  principal, so granting the workload account `roles/modelarmor.user` changed nothing and the
  policy step reported `screening_unavailable` on every investigation. Deployment now grants the
  Agent Identity directly. The `orchestrator-sa` grant is reverted — durable ingress constructs no
  agent, so it calls no model — along with the test that required it, since an over-grant enforced
  by a gate is harder to remove than one nobody checks.
- `roles/iap.egressor` carries the permission the denial names, and nobody held it. Registering a
  destination is necessary but not sufficient. The catalog was also genuinely incomplete: Google API
  clients resolve to mTLS hosts when a client certificate is available, and each is a distinct
  endpoint. Both the role and the endpoints are applied by deployment and required by
  `verify_fleet`.
- Refusals inside the notification boundary all raised one `SensitiveDataError`, so the trail said
  only that something was rejected. `UnsafeRiskCategoryError` and `OpaqueFindingIdError` make the
  exception type the bounded reason, keeping events payload-free while making them answerable.

### Fixed — the dispatcher sends data, not an instruction

- Model Armor scored the dispatcher's own repository-owned sentence at HIGH confidence — the same
  as a genuine injection probe — and since screening fails closed it refused **every investigation
  the fleet had ever run**.
- Neither threshold separated them. To a prompt-injection classifier an imperative addressed to an
  agent is what an injection is; the difference is provenance, which content classification cannot
  see. `HIGH` was tried and reverted: it fixed nothing and detected less.
  [ADR-009](docs/adr/009-model-armor-threshold.md) records that the threshold is not the lever.
- The message is now a JSON object carrying the correlation id, with a test pinning the shape so the
  outage cannot return as a well-meaning rewording. Instructing the model to use only registered
  agents was never something it could honour or ignore — Registry and IAP authorize egress
  deterministically — so asking for it in prose bought nothing and cost the entire pipeline.

### Changed — the Model Armor template is configuration, not console state

- The deployed template enforced prompt-injection detection at `LOW_AND_ABOVE`, which matched the
  fleet's own prompts. Investigations completed in forty seconds having done nothing. A control
  that blocks all legitimate traffic supplies an outage, not security.
- The threshold was measured against the live template rather than guessed, and the configuration
  now lives in `model_armor/template.py` so the posture is diffable and restorable. `verify_fleet`
  fails when the deployed template drifts, including when it is merely unreadable — equally fatal
  under fail-closed screening.
- Refusals carry screened character and part counts. Sizes are not values: a length may travel where
  a principal may not, which keeps this inside the payload-free rule. A digest used during diagnosis
  was removed once it had served, because a fingerprint of a prompt is still derived from a prompt.

### Fixed — approval cannot be granted by an agent that can reach the endpoint

- `caller_identity` accepted any principal with a verifiable ID token carrying an email claim, and
  every worker identity that posts a review record necessarily holds `run.invoker` on the findings
  API. The Escalation Agent could approve the suppression of a finding it had just raised.
  Confirmed against the deployed service.
- ADR-008 had named `gcloud run services proxy` as the reviewer's path, and that path cannot work:
  Cloud Run accepts only a Google-signed ID token whose audience is the service, and no user
  credential can mint one. The record stated the constraint and then contradicted it.
- Approval now checks one deployment-configured approver identity and fails closed when unset. The
  human reaches it through a break-glass identity holding no project role and exactly one
  capability, which only the configured principal may impersonate — so the human stays named in the
  IAM audit log.
- Firestore's default database is literally named `(default)`; sourced unquoted into a POSIX shell
  that is array-assignment syntax yielding a different database name, with no error at any layer.

### Changed — the local permission grant is ignored by the repository

- `.claude/settings.local.json` authorizes an agent to deploy against the live project. It was
  untracked only because a personal `~/.config/git/ignore` rule matched it — a rule absent on CI, in
  a fresh clone, and on every other checkout. The protection held precisely where it was least
  needed.

### Known — two defects remain open

- **Model Armor egress from inside the Runtime is denied by IAP.** Five hypotheses were eliminated:
  global Registry registration, GRPC to HTTP_JSON rebinding, a Runtime redeploy, Registry
  `bindings`, and IAM. The Agent Identity holds `roles/iap.egressor` at project level and there are
  no IAP grants in the denial window. The deterministic policy step no longer depends on this path,
  so it is not blocking, but it is not solved.
- **Investigations truncating after the Auditor (D6) is closed** — fixed and observed
  completing end to end on 2026-08-22. Its cause is recorded above.
- Both are tracked in
  [09-capture-backlog.md](submission/planning/09-capture-backlog.md) alongside the observation
  backlog. Nothing in this release claims either is fixed.

### Changed — dependency pins raised for the tag

- `google-adk` 2.7.0 → **2.7.1** and `google-cloud-aiplatform` 1.164.0 → **1.165.1**, with
  `requirements.lock` regenerated. `scripts/check_versions.py --check-upstream` is the documented
  pre-tag gate and it failed on both; a tag is a claim that the pinned stack is current, so the
  pins move before the tag rather than after it.
- ADR-005's installation claim was **re-run** against 2.7.1 rather than re-dated. A verification
  line edited to match a new pin has stopped being a verification.
- No behavioural change surfaced: 247 tests at 100% statement and branch coverage, mypy, and every
  documentation gate pass identically on 2.7.1. `SequentialAgent` remains deprecated-but-required
  in 2.7.1, so ADR-005's migration trigger — `Workflow` becoming usable as an `LlmAgent` sub-agent
  — has still not fired.

### Changed — the suite is 247 tests

- Up from 208, at 100% statement and branch coverage under Python 3.12. Every new boundary added in
  this release carries tests at the layer it changed.

### Changed — the reviewer grant is applied by deployment

- `deploy.sh` applies `roles/run.invoker` on the findings API from `BASTION_APPROVER_PRINCIPAL`,
  and warns when it is unset. `gcloud run deploy` re-establishes the service IAM policy, so a
  grant made by hand does not survive the next deploy — and the only path that can create an
  exception would stop working with nothing reporting it.
- ADR-008 records how a human reaches an IAM-private service: `gcloud run services proxy`. A user
  credential cannot mint an audience-scoped identity token, and impersonating a service account
  would replace the human in the ledger with the identity the record exists to distinguish them
  from.

### Added — the secret scan covers principal inventories, not only credentials

- The scan now fails on any real service-account principal in a tracked file outside `tests/`,
  which carry `bastion-ci-mock` identities deliberately, and `.gitignore` excludes captured
  console output.
- The shape this covers: `gcloud ... add-iam-policy-binding` prints the resulting policy, so a
  redirected operator session is a principal inventory in an ordinary `.txt` — matched by none of
  the credential-filename, embedded-JSON, API-key or private-key rules.

### Added — the track's first obligation is now measured, not asserted

- Captured [evidence 09](assets/evidence/09-cross-department-routing.md): 52 live IAM bindings
  produced 3 overly-broad findings that routed to **2 different owning departments**,
  deterministically. Cross-department routing existed and was tested; nothing recorded that
  production data actually exercises it, which is the difference between a `department` column
  and cross-department support.

### Changed — sovereignty is stated as minimisation, not residency

- The README led with the disclaimer that Gemini runs on `global` and therefore claims no EU
  residency. True, but the weaker half of the argument: raw members, roles, resources and
  bindings never reach the model at all, so there is no prompt from which a principal could be
  recovered. Residency keeps regulated data in a region; this keeps it out of the model entirely.
  The disclosure stays — it is now the second point rather than the first.

### Added — "scalable network" is answered explicitly

- The track asks for a scalable network; the fleet is fixed at three agents by ADR-002, which a
  judge should not have to reconcile alone. The README now states the actual scaling axes —
  owning departments, catalogued agents, and bounded throughput — with evidence 09 as the
  measured proof that the first is real. `BASTION_MAX_INSTANCES=3` is named as a budget ceiling
  following the organizers' cost guidance, not an architectural limit.

### Changed — departments are repository-owned by decision, not by default

- `registry/departments.py` records why the catalog stays in static source: Agent Registry
  catalogs *agents*, and a routing table any registered agent could write to would let a
  compromised one redirect its own findings away from the team that owns them. `load_catalog()`
  remains the single seam if that reasoning ever changes.

### Changed — `.env.example` is the complete environment contract

- Every variable the code and deployment scripts read is declared, grouped by purpose: what is
  required with no default, the three region planes and why conflating them breaks, the managed
  governance surfaces, deployment shape, and which variables hold secret *ids* rather than secret
  values. A clean clone can configure the fleet from this file alone.
- `tests/unit/test_environment_contract.py` parses the code and the deployment scripts and fails
  on drift in either direction — a variable the code reads that the example omits, or one the
  example declares that nothing reads — and fails if a secret value is ever committed there.

### Added — the exception ledger has a production writer, and it is a human

- `POST /v1/exceptions` to the private findings API: the only path that creates an
  exception. The reviewer comes from the **verified caller ID token**, never the request body —
  a self-asserted reviewer field is an attestation the caller forges about itself. Expiry is
  capped at 90 days so a silent suppression cannot outlive its reasoning unnoticed.
- `notify_human` now carries opaque `finding_ids`. The signature is still the control: it is
  handed identifiers and counts, never bindings, and a fabricated id is inert because it can only
  key an exception no real finding will match.
- Recorded the decision in [ADR-008](docs/adr/008-human-approval-loop.md), and the boundary in
  SECURITY.md and DATA_GOVERNANCE.md. Approval is deliberately not an agent tool; the tool-surface
  security suite fails if any agent ever declares one.

### Changed — google-auth is pinned as the direct dependency it is

- `gateway/cloud_run_auth.py` mints Cloud Run ID tokens and the approval endpoint verifies them,
  both importing `google.auth`/`google.oauth2` by name, so the package is pinned directly rather
  than inherited from `google-cloud-firestore`'s constraint. Pinned at the version the lock
  already resolved, so install behaviour is unchanged.

### Changed — the test-count gate requires the claim to exist

- It asserts that at least one document states the suite total before comparing, so a claim that
  was removed cannot read as a claim that was met.

### Added — the tool-declaration boundary is now asserted, not only documented

- Added `tests/security/test_tool_surface.py`, the enforcement behind ADR-007's tool-declaration
  boundary. It asserts each agent's tool set by equality at construction, that the Escalation Agent
  holds neither a policy-reading tool nor an Asset client (differentially against the Auditor,
  which must still hold one), and that every tool description is repository-owned static source.
- Captured [evidence 08](assets/evidence/08-tool-poisoning.md), including confirmation that the
  assertions **fail** when the escalation agent is mutated in memory to hold `audit_iam_policy`.
  A guardrail test that has never been seen to fail is not evidence that the guardrail holds.

### Changed — the documented test total is verified, not asserted

- The suite total — the number that changes most often and is quoted in six documents — is now
  verified alongside the pillar, ADR, agent, badge, and diagram counts.
- The assertion lives in `tests/unit/test_documented_test_count.py` rather than in
  `check_docs.py`, because CI's docs and diagrams jobs run that script on a bare interpreter with
  no dependencies installed — there is no pytest there to collect with, and making those jobs
  install the full tree to count tests would trade a fast standalone gate for a slow one. Inside
  the suite the collected count is already known. It skips on a partial run, so narrowing to one
  directory does not fire it. Released CHANGELOG sections are exempt: they record what was true
  at their tag.

### Added — the observation backlog is tracked in the repository

- Added [09-capture-backlog.md](submission/planning/09-capture-backlog.md), which tracks what is
  deployed and tested but not yet observed. What remains before submission is observation, not
  construction, and that distinction is now a tracked document rather than an assumption.
- Records that the cross-week continuity seed targets the Firestore `bastion_exceptions`
  collection. Memory Bank backs managed session memory, so seeding it would produce a capture
  that proves nothing about suppression.
- Records that rate limiting is not implemented, with the three ways forward and the reason the
  choice precedes the capture attempt.

### Changed — release runs are named after the release

- The Release workflow names each run after the release ref rather than the tagged commit's full
  message, which for an annotated tag is several paragraphs.

## [0.1.0] — 2026-08-16

First tagged release. The production path is deployed and verified; the remaining work before
submission is observation and publication, not construction. What is deployed but **not yet
captured as an observed artifact** is recorded in
[`submission/SUBMISSION.md`](submission/SUBMISSION.md) rather than claimed here.

### Added — governed managed Runtime path

- Deployed the Orchestrator to Python 3.12 managed Agent Runtime with Agent Identity and
  Agent-to-Anywhere Gateway binding; catalogued it beside two institutionally described A2A
  worker cards and approved platform destinations.
- Reduced Cloud Run Orchestrator to durable Eventarc admission and Runtime dispatch. Deployment
  now reconciles away its peer secret, direct worker invoker grants, and obsolete Model Armor and
  Pub/Sub roles, leaving no production local-graph bypass.
- Added Firestore leases/reclaim, failure/retry semantics, five-attempt dead-letter delivery,
  idempotent findings, private findings IAM, full payload-free AuditPlugin lifecycle, fail-closed
  Model Armor, and deterministic protected-data screening.
- Added Windows 11 bootstrap, live fleet verification/smoke, safe rollback, dry-run-first teardown,
  count-only state capture, and idempotent observability provisioning.
- Provisioned a 365-day regional audit bucket and sink, four log metrics, five alert policies, and
  the Bastion Fleet Operations dashboard. The bucket remains unlocked; immutability is not claimed.
- Standardized Docker, Runtime, GitHub Actions, release workflow, commands, and documentation on
  Python 3.12.
- Expanded the suite to 161 tests with 100% statement and branch coverage across populated unit,
  integration, security, and load suites.
- Reconciled every Markdown claim and architecture/banner label with the 2026-08-16 measured live
  state: 21/21 APIs and 33 deployed resources.

### Changed — visual system

- Preserved the corrected architecture arrows/status dots and refreshed generated theme variants
  and GIFs from their reviewed masters.
- Updated banner and architecture facts for managed Runtime, Memory, Gateway, Registry, and the
  current count-only deployment measurement.

### Changed — documentation matches the deployed fleet

- The rubric self-assessment in [`submission/DEVPOST.md`](submission/DEVPOST.md) records managed
  retry as implemented and deployed, with the timeout → retry → escalate sequence marked as not
  yet captured rather than upgraded to observed.
- The `Makefile` exposes `verify`, `smoke`, `rollback`, and `teardown` against the real
  operator entry points, and `install` is interpreter-relative so one target serves the Windows
  authoring machine and Linux CI.
- The decision index dates ADR-003 as verified against the deployed fleet on 2026-08-16.

## Pre-deployment baseline — 2026-08-15

The first untagged baseline, before the managed deployment recorded above. Retained as
chronology; the current state is the sections above it.

### Added — the fleet, before it was deployed

- Three ADK agents under one `SequentialAgent`: a read-only Access Auditor over live Cloud
  Asset Inventory, deterministic policy enforcement inside the Orchestrator, and an Escalation
  Agent holding no policy-reading capability.
- Deterministic detection and scoring ahead of every model call, so a finding is produced by
  code and only explained by Gemini. Keyed opaque finding identifiers, allowlisted risk
  categories, and department routing derived from the principal string rather than a model
  judgement.
- A2A as the inter-agent contract: typed tasks carrying `task_id` and `context_id`, an explicit
  lifecycle, and agent cards. A policy refusal is recorded as its own outcome rather than as a
  failure, and a retry keeps its task id so one retried task does not read as three.
- A payload-free audit record per transition, written independently of tracing, because a trace
  is sampled and expires while a compliance record is neither.
- Durable runtime semantics: an inbox and leases, attempt counting, deduplication, terminal
  state, and separation of permanent failure from transient failure so a malformed message is
  not redelivered forever.
- Cloud Run deployment with one service account per workload, explicit regions with no default,
  bounded instance counts, and Secret Manager for the keyed identifier and origin credential.

### Added — judge-facing artifacts

- Level 1 and Level 2 architecture diagrams as hand-authored 1920×1080 SVG masters with light
  and dark variants and animated GIFs, each stating its own build state, with a documentation
  gate that fails the build when a diagram and the measured state disagree.
- A count-only live measurement of the project, generated rather than typed, excluding the
  service accounts Google creates for every project so the number answers what Bastion deployed.
- Thirteen decision records, each tracing to a quoted line in the captured brief, later
  consolidated to seven.

### Added — engineering gates

- Unit, integration, security, and load suites at 100% statement and branch coverage.
- `mypy --strict` with `warn_unreachable` and `disallow_any_generics`, Ruff lint and formatting,
  a transitive dependency lock with a vulnerability audit, and a secret scan.
- Clients constructed on first use rather than at import, so importing a module never attempts
  credential discovery and a missing setting explains itself.
- `httpx` with explicit connect and read budgets and transport-level retries that do not replay
  an already-sent request, since retrying a delivered notification pages a human twice.

### Verified — 2026-08-13

- `gemini-3.5-flash` answering through Vertex AI on the project.
- Application Default Credentials authenticating locally.
- The local quality gate passing end to end.
