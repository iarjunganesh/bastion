# Final evidence and gallery capture runbook

**Purpose:** close only the observations required for safe public claims, then produce the five
Devpost gallery images. Raw captures belong in ignored `.takes/`; only reviewed, cropped, redacted
artifacts move into `assets/screenshots/` or `assets/evidence/`.

The evidence sprint has reached its safe publication boundary: four observations are closed and
the other two are explicitly deferred under narrower wording. Do not start the video until the
gallery acceptance gate is complete. Do not expose service-account principals, private origins,
tokens, secrets, prompts, responses, raw IAM members/roles/resources/bindings, or unredacted
exception messages.

## Before the first capture

- [ ] Freeze the code revision that will appear in the video.
- [ ] Reconfirm the deployed revision matches it.
- [ ] Use a clean browser profile with notifications, bookmarks, extensions, and autofill hidden.
- [ ] Set the desktop and browser to 1920×1080 and at least 125% console text zoom.
- [ ] Prepare narrow, count-only console filters before recording anything.
- [ ] Create a fresh ignored directory under `.takes/` for raw screenshots and recordings.
- [ ] Confirm local `ffmpeg` and `ffprobe` are on `PATH` before recording video.
- [ ] Confirm the healthy revision and rollback path before any staged failure.

Raw files under `.takes/` remain untouched. For each promoted PNG or MP4, add an explicit reviewed
declaration to `scripts/redact_evidence.py`; an empty tuple means the final file was inspected and
needs no mask. The gate covers `assets/evidence/screenshots/` as well as the gallery, because a
supporting capture is promoted to back a written record rather than to be looked at, and so tends
to be copied from `.takes/` verbatim — two of the first five arrived carrying the operator's Google
account photo in the console header. Apply masks only to the promoted copy, then require
`python scripts/redact_evidence.py --check` to pass before committing it. Pillow handles lossless
PNG masks; local FFmpeg burns masks into videos and the checker samples the start, middle, and end.
Do not redact evidence-bearing metrics, counts, statuses, timestamps, queries, trace/investigation
IDs, or other values cited by the surrounding submission.

## Evidence sprint — execute in this order

**Status 2026-08-27 — four closed; two deferred with narrowed claims.** Steps 1, 2, 3 and 4 are
captured, reviewed and promoted; their retained records are evidence 11, 12, 13 and the refreshed
evidence 07. Their raw 1920×1080 sources stay ignored under `.takes/2026-08-25/` until the gallery
is composed. Steps 5 and 6 are post-hackathon evidence work; their claims remain narrowed — see
[11-claim-matrix.md](planning/11-claim-matrix.md).

| Step | Capture | State | Retained record |
|---|---|---|---|
| 1 | P0.9 current-route IAM provenance | **Closed** | [evidence 11](../assets/evidence/11-current-route-correlation.md) |
| 2 | P0.6 agent-mediated Model Armor refusal | **Closed** | [evidence 12](../assets/evidence/12-agent-mediated-model-armor-refusal.md) |
| 3 | P0.8 correlated retained audit | **Closed** | [evidence 11](../assets/evidence/11-current-route-correlation.md) + [evidence 07](../assets/evidence/07-observability.md) |
| 4 | P0.7 current-route Cloud Trace chain | **Closed** | [evidence 13](../assets/evidence/13-current-route-trace.md) |
| 5 | P0.10 managed Gateway refusals | Deferred | none — claim stays narrowed |
| 6 | P0.11 timeout, retry, bounded failure | Deferred | none — claim stays narrowed |

A note carried forward from step 5's attempt: every IAP authorization denial observable in this
project resolves to `unregisteredEndpoint` with an empty `authenticationInfo`, which is D2's
residual platform behaviour rather than a caller being refused. Producing the intended refusal
would require deploying a modified Runtime that attempts egress to an unregistered destination,
which this plan forbids at this stage.

### 1. Current-route IAM provenance — P0.9

Capture first because it establishes the successful investigation used by later audit/trace views.

- Run the current deployed Auditor route.
- Record binding count, canonical finding count, routed departments, model name, and revision.
- Confirm raw principals printed, persisted, or model-visible: zero.
- Promote only the redacted count-only record.
- Acceptance: a reviewer can connect live IAM input to deterministic department routing without
  seeing a policy dump.

### 2. Agent-mediated Model Armor refusal — P0.6

- Send the approved injection sample through the same authenticated A2A input surface as the
  deployed Access Auditor.
- Capture the callback refusal before Gemini and the payload-free audit event.
- Confirm the investigation remains failed/reclaimable rather than falsely completed.
- Acceptance: proof is agent-mediated, not only a direct template test; no unsafe payload is shown.

Until accepted, public wording remains: the managed template refused the sample, while callback
and fail-closed behavior are tested and deployed.

### 3. Correlated retained audit trail — P0.8

- Query one investigation ID across Runtime and both workers.
- Include a refusal event if step 2 safely produced one.
- Show `investigation_id` joining the full flow and `invocation_id` grouping one run.
- Capture the regional sink/bucket and 365-day configuration separately.
- Acceptance: the event query is payload-free and the retention configuration is not described as
  immutable/WORM.

### 4. Current-route Cloud Trace chain — P0.7

- Use the successful investigation from step 1.
- Capture Runtime → Auditor → policy/model → Escalation spans at readable zoom.
- State that trace is sampled/explanatory while retained audit is the compliance record.
- Acceptance: complete current-route chain is visible without prompts, responses, URLs, or
  principals.

### 5. Managed Gateway refusals — P0.10

**Post-hackathon only. Do not run during the final submission window.**

- Observe the intended unregistered destination/caller refusal on the managed path.
- Observe the undeclared-skill/destination refusal if the platform exposes that distinction.
- Capture the managed authorization result, not only local gateway-policy tests.
- Acceptance: name only the refusals actually observed. Never call the instance cap or delivery
  bound a per-caller rate limit.

### 6. Timeout, retry, and bounded failure — P0.11

**Post-hackathon only. Do not stage a production failure during the final submission window.**

- Use a temporary staged dependency failure; do not add a permanent production fault switch.
- Show the event remaining retryable/reclaimable after the first failure.
- If safe, observe Eventarc redelivery and the configured five-attempt dead-letter boundary.
- Restore and verify the healthy revision immediately.
- Acceptance: claim only the boundary actually observed. If fifth-attempt dead-letter is not
  captured safely, retain the narrower “configured bounded delivery; tested retry/idempotency.”

### 7. Reconcile the claim matrix

- Update the relevant evidence ledger for each accepted capture.
- Update `submission/planning/11-claim-matrix.md` column by column.
- Narrow any row that still lacks observed proof.
- Refresh mutable counts in `assets/architecture/gcp-state.json` and regenerate diagrams only if
  the deployed inventory changed.

## Five-image Devpost gallery

Export PNG at 1920×1080, sRGB, under 5 MB. Add no decorative panel that makes console text smaller.

**All five are dark.** Every promoted console and terminal capture is dark, so the architecture
still is taken from the dark master rather than the light one; a light panel in that sequence reads
as a different project. The same rule governs the demo video.

**Composition rule.** A promoted image may be cropped, may stack contiguous strips of a single
capture with dead space between them removed, and may carry a drawn label naming what a panel
shows. It may not reorder, retime, or recolour evidence, and every number it displays must already
appear in a retained evidence record.

### 01 — `assets/screenshots/01-enterprise-fleet-architecture.png`

Source: `assets/architecture/enterprise-fleet-architecture-dark.png`, emitted by
`scripts/render_diagrams.py` alongside the light still.

Caption: **A managed, zero-trust institutional-agent fleet where raw IAM stops before the model.**

Acceptance: three agents, seven managed pillars, data-minimization boundary, durable state, and
audit/trace outputs are readable at gallery-thumbnail size.

### 02 — `assets/screenshots/02-governed-agent-catalog.png`

Source: `.takes/2026-08-27/02a-agent-registry-list.png`, cropped to the breadcrumb, the Registry
title, and the filtered catalog; the empty search hero between them is removed.

Show all three governed agents in one `europe-west4` catalog with their runtime type, version, and
purpose. Browser chrome, the project-bearing URL, and the signed-in avatar are cropped away rather
than masked.

Caption: **Three institutional agents in one governed catalog: two A2A workers and one managed
Runtime, versioned and regional.**

Acceptance: a reviewer sees the Agent Registry product, the region, and exactly three Bastion
records without a worker origin or an operator identity.

**Narrowed against the original plan.** The list view does not expose owner, department, skill,
classification, or approval; those fields live on each record's Agent Card detail view, which has
not been captured. Do not caption this image as showing ownership or policy metadata until that
capture exists. The fields themselves are asserted by
[evidence 05](../assets/evidence/05-runtime-gateway.md), not by this screenshot.

### 03 — `assets/screenshots/03-production-iam-routing.png`

Source: `.takes/2026-08-25/11-current-route-count-only-summary.png`, cropped to the evidence block.
The invoking command line is dropped so the counts scale up; its provenance is
[evidence 11](../assets/evidence/11-current-route-correlation.md).

Show the final current-route binding count, deterministic findings, and owning departments. Do not
show principal/member values.

Caption: **One production IAM review routes minimized findings to the teams that actually own them.**

### 04 — `assets/screenshots/04-enforced-security-boundary.png`

Source: `.takes/2026-08-25/12-agent-mediated-model-armor-refusal.png`, cropped to the evidence
block.

Show the refusal reached through the deployed Access Auditor's own A2A surface: the control run
completing, the blocked run failing closed, the callback refusal observed, and zero model
submissions, completions, or tool calls after it.

Caption: **A prompt-injection probe is refused at the deployed agent's own boundary — by an inline
screening callback, not by agent instructions.**

**Narrowed against the original plan.** The planned side-by-side of Auditor read permitted and
Escalation read denied has not been captured, so this image proves inline screening only, not the
IAM split. The IAM split remains asserted by
[evidence 03](../assets/evidence/03-escalation-agent-denied.md). Do not caption this image as
showing an IAM denial.

### 05 — `assets/screenshots/05-durable-context-and-audit.png`

Sources, composed into three labelled panels: `.takes/2026-08-25/11-current-route-audit-log.png`,
`07-audit-bucket-retention.png`, and `13-current-route-trace.png`.

Show one `investigation_id` joining Runtime and both workers with every `detail` object collapsed,
the regional 365-day retention configuration, and the same investigation as one 22-span trace. The
trace panel stops left of the Service/workload column and expands no span, so no worker origin can
appear.

Caption: **One investigation stays reconstructable across the Runtime and both workers — correlated,
payload-free, and retained for a year.**

**Narrowed against the original plan.** The planned exception-approval and later-suppression dates,
and the absent notification for the suppressed department, have not been captured. This image
therefore proves correlation, minimization, and retention — not cross-week human-decision
continuity, which remains asserted by
[evidence 10](../assets/evidence/10-cross-week-suppression.md).

## Gallery acceptance gate

- [x] Exactly five ordered files exist under `assets/screenshots/`.
- [x] Each is 1920×1080, under 5 MB, and legible at 480 px width.
- [x] Captions describe visible proof rather than implementation intent. Three were narrowed on
      2026-08-27 to the panels that were actually captured; see each entry above.
- [x] Every image passed a sensitive-data inspection at 200% zoom. None needed a mask: the private
      surfaces were cropped out rather than covered, and every retained value already appears in a
      published evidence record.
- [x] `python scripts/redact_evidence.py --check` passes for every final PNG and MP4.
- [x] The architecture image matches the final deployed inventory; its footer date and resource
      count are gated against `gcp-state.json` by `scripts/check_docs.py`.
- [x] No screenshot upgrades a `Partial` claim without an updated evidence record.
- [ ] A signed-out reviewer can understand the sequence without narration.
