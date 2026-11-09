# Assets and evidence

Bastion's central claim is backed by redacted captures rather than architecture prose alone:

> Three governed agents inspect real IAM, retain asynchronous context, call catalogued workers,
> and create a minimized human-review record without gaining write access
> to IAM.

## Evidence ledger

The [4–5 November audit and corrections](../docs/research/evidence-audit-2026-11-04.md) cover the
first 23 records; evidence 24–29 carry their own disclosures. Keep original captures unchanged and use the corrected derived values and proof
boundaries when making current claims.

| Evidence | Captured fact | Boundary |
|---|---|---|
| [01 — Model Armor block](evidence/01-model-armor-block.md) | The live regional template refused a prompt-injection sample | Direct managed-service probe; callback wiring is additionally tested |
| [02 — Gemini investigation](evidence/02-gemini-investigation.md) | Gemini 3.5 Flash processed minimized state from a real IAM review | Historical pre-Gateway run; **superseded 2026-08-25 by evidence 11** as current-route proof and retained as history only |
| [03 — identity denial](evidence/03-escalation-agent-denied.md) | Escalation was denied IAM read while Auditor was permitted | Workstation impersonation of deployed identities |
| [04 — private fleet](evidence/04-private-fleet-deployment.md) | 21 APIs and 39 enumerated resources measured without principals | Scoped count-only inventory, not a request trace; the Workload Identity pool and provider are excluded |
| [05 — Runtime and Gateway](evidence/05-runtime-gateway.md) | Managed Runtime session streamed events; Gateway/Registry/IAP configuration verified | Status and count proof; no private URLs or identities retained |
| [06 — durable findings](evidence/06-durable-findings.md) | Eventarc/Firestore completion plus findings IAM and idempotency | Live production smoke; payload intentionally omitted |
| [07 — observability](evidence/07-observability.md) | Regional audit retention, sink, metrics, alerts, and dashboard exist | Reviewed bucket capture proves region, 365-day retention, and analytics; not immutability/WORM or historical SLO attainment |
| [08 — tool poisoning](evidence/08-tool-poisoning.md) | Fixed tool sets at construction; Escalation holds no policy tool or Asset client | Construction-time proof, verified to fail when widened; not a live refusal trace |
| [09 — cross-department routing](evidence/09-cross-department-routing.md) | 18 Aug: 52 live bindings produced 3 findings routed to 2 owning departments | Routing measurement, not a completed investigation. Later censuses are separately dated: E11 measured 62 on 25 Aug; E23 measured 56 on 28 Oct |
| [10 — cross-week suppression](evidence/10-cross-week-suppression.md) | A human exception approved 2026-08-19 suppressed its matching finding on 2026-08-22, on the deployed path; re-confirmed 2026-08-23 after the deterministic-delivery rewrite (P0.1–P0.3) | Three-day gap, not a calendar week; expiry is not in this historical capture but was observed separately in E16 on 3 Nov |
| [11 — current-route correlation](evidence/11-current-route-correlation.md) | One fresh investigation completed across Runtime, deployed Auditor and Escalation revisions, and Gemini 3.5 Flash; a companion probe measured 62 bindings, 3 canonical findings, and 2 post-policy deliveries | Payload-free route correlation plus count-only companion measurement; composed into gallery images 03 and 05 on 2026-08-27 |
| [12 — agent-mediated Model Armor refusal](evidence/12-agent-mediated-model-armor-refusal.md) | The deployed Auditor callback refused the approved injection sample and its A2A task failed before another model or tool call | Direct authenticated Auditor probe, not a durable Runtime investigation; gallery image 04 shows screening only, with IAM denial covered separately by E03 |
| [13 — current-route trace](evidence/13-current-route-trace.md) | One connected 22-span Cloud Trace covered the managed Runtime, both A2A workers with their agent-card fetches, the Firestore exception lookup inside the policy step, and the completion gate | Sampled explanatory telemetry with span attributes deliberately unopened; not the retained compliance record and not a latency claim |
| [14 - bounded live validation](evidence/14-live-validation.md) | 27 Oct: 20 real-IAM investigations completed in one durable attempt each; 560 audit records/60 invocations, 40 model submissions, 40 review records and three delivered finding instances per run | Post-hackathon report supplement, not the submitted demo; one project, documented collector recovery, 5s-poll confirmation timing, bounded replay observations and one time-matched trace; no new binding census, C4 result or historical SLO claim |
| [15 - fleet inventory](evidence/15-fleet-inventory.md) | 28 Oct: 21 enabled APIs and 39 enumerated resources, including zero Scheduler jobs | Existence/counts only, with the same enumerator scope as E04; not package resolution or a binding census |
| [16 - exception lifecycle](evidence/16-exception-lifecycle.md) | 3 Nov: a 15-minute human approval suppressed one finding, and the same finding returned after expiry | Cohort N; one lifecycle on one finding, not a rate; durations cold-start confounded |
| [17 - negative authorization](evidence/17-negative-authorization.md) | 3 Nov: all 15 checks matched their expected outcome, 13 negative outcomes and 2 positive controls, with no ledger write | One negative is a permission test reporting not held, rather than an HTTP refusal; single probes, not fuzzing or the Gateway/Registry refusal |
| [18 - Model Armor refusal re-probe](evidence/18-model-armor-refusal-reprobe.md) | 3 Nov: benign control completed; the injection fixture was refused with `policy_match` and nothing ran after it | Direct authenticated Auditor request; refusal joins its investigation in two hops via the invocation ID |
| [19 - repeatability and false completion](evidence/19-repeatability-and-false-completion.md) | 3 Nov: E7 stopped on a run recorded completed with no work done; E7b passed 20/20 with per-run tokens and per-message delivery | One batch, not a reliability rate; 1 false completion in 28 investigations; [corrected median 20.6 s](../docs/research/evidence-audit-2026-11-04.md#e19-median-correction); original capture unchanged |
| [20 - Gateway unmatched-egress refusal](evidence/20-gateway-unmatched-egress-refusal.md) | 4 Nov, read-only: 176 fail-closed IAP denial decisions (88 failed SDK project lookups) on Runtime egress resolved to `unregisteredEndpoint`: 156 at the 13 instance starts, 20 during runs; investigations continued | Incidental SDK lookup of a registered host, matching the August defect D2; cause inferred, not confirmed by Google; no allow decision logged |
| [21 - redelivery and dead letter](evidence/21-redelivery-and-dead-letter.md) | 4 Nov: one rejected event on the production subscription, 5 HTTP 400 deliveries, dead-lettered with delivery count 5, cleared; no state written | One event, a permanent rejection; attempt count approximate; paging delivery not verified, distinct from E07's configured alert policies |
| [22 - A2A state boundary reproduction](evidence/22-a2a-state-boundary-reproduction.md) | 4 Nov, offline on `google-adk` 2.13.0: state does not cross A2A in either direction; both upstream warnings fire | At collection, Cloud Run still had 2.7.1; the later deployment is evidence 24. Runtime packages remain unreadable; other ADR-012 behaviours not re-run |
| [23 - deployment census and packages](evidence/23-deployment-census.md) | 28 Oct census (56 bindings, 3 findings) and 4 Nov image packages: one digest across four services, `google-adk` 2.7.1, 161 distributions | Runtime packages unreadable; no census on the evaluation days; original census seal unavailable, while the separate package bundle is sealed |
| [24 - upgraded deployment and stopped F pilot](evidence/24-upgraded-deployment-and-stopped-pilot.md) | 5 Nov: four Cloud Run image updates and one Runtime update verified; one pilot failed across five automatic deliveries, with 10 completed model audit records and no reviews | Missing routing envelope; completion stayed failed. Source drained, one review-queue message retained; aggregate time-window join only. Positive completion/refusal-join controls were not run in this stopped chunk; the later recovery is evidence 25 |
| [25 - corrected F functional verification](evidence/25-corrected-cohort-F-verification.md) | 5 Nov: five normal investigations, one separate true-wire control, two completed-event replays and one direct refusal join passed; 12 model completions | One-attempt normal cases; delivery joins use isolated time windows, not message IDs. Refusal join uses a read-only addendum after a collector temporal false positive. Original failed F retained separately; 6 Nov daily billing check passed for reported usage; no exact per-chunk cost or reliability rate |
| [26 - cohorts G, H and I](evidence/26-cohorts-g-h-i.md) | 7–8 Nov: v0.9.0 cohorts G (4 validated, instrument stop) and H (27 validated, then H28's model 429 failed closed); v0.9.1 cohort I: 98 of 98 validated, one audited model retry (I57), instrument stop at I99 on a Cloud Logging outage | Separate stopped cohorts, never pooled or rerun; I99's read-only addendum is outside the 98; pre-specified (local records, no external timestamp); the 3.01% bound is a conditional illustration only; no SLO or reliability rate |
| [27 - targeted controls J](evidence/27-targeted-controls-j.md) | 8 Nov, I's fleet: direct Runtime control, five completed-event replays (I98 for the never-run I100), one direct Model Armor refusal and the forged-envelope pair all passed | Routing test shows Auditor-attributed routing rejected, not that unauthorized routing is impossible; replays show no additional effects in 120 s windows, not exactly-once delivery |
| [28 - telemetry census and isolation K](evidence/28-telemetry-census-k.md) | 8 Nov: J0's connected 172-span trace; K1 exported Runtime graph spans and K2 did not; read-only census of 142 agent traces (5–8 Nov) found the Runtime graph in 5 and zero content-bearing attributes | Post-hoc; traces not joined one-to-one to investigations; sampling unknown; root cause unresolved; bounds inspected traces only |
| [29 - timeout fault injection L and M](evidence/29-timeout-fault-injection-l-m.md) | 8 Nov: L stopped on an instrument fault before its fault reached anything; M's injected 3 s Auditor timeout gave 5 failed attempts (503 after 504), 0 reviews and dead-letter review; worker execution continued past estimated timeout boundaries | Dead-letter attribution by isolated window, not message ID; cancellation analysis post hoc with estimated boundaries; M's original protocol hash reconstructed; configuration restored and verified |

The August captures and gallery remain dated publication records. Evidence 14 adds a
separately dated operational validation and verified data bundle; it does not refresh the
27 August infrastructure inventory, replace evidence 11's 25 August binding count, or close
the two controls that were then open. Evidence 20 and 21 subsequently close narrower report
observations; their original unregistered-caller and worker-timeout forms remain unclaimed.

## Architecture and brand assets

`architecture/enterprise-fleet-architecture.svg`, `enterprise-fleet-overview.svg`, and
`governed-investigation-flow.svg` are the reviewed 1920×1080 masters.
`scripts/render_diagrams.py` emits light/dark variants and animated GIFs. The judge-facing names
describe the story directly; internal level numbers are deliberately absent. The README banner
uses hand-reviewed light/dark SVGs; the 16:9 Devpost banner is another generated master.

Every architecture master carries a `Build state · <date> · 21/21 APIs · 39 resources measured`
footer. Both halves are gated: `check_diagram_footers_match_state()` has always compared the count,
and `check_diagram_dates_match_state()` now compares the date, because the date was ungated and
drifted — every asset read `2026-08-22` against a `2026-08-23` capture, including the PNG uploaded
to Devpost. A count that agrees with a measurement taken on another day is a coincidence, not a
grounded claim.

The diagrams are checked against [gcp-state.json](architecture/gcp-state.json), which is generated
from the live project and contains counts only. No image names a principal, secret, private URL,
or policy binding. Run:

```powershell
python scripts/capture_gcp_state.py
python scripts/capture_gcp_state.py --check
python scripts/render_diagrams.py
python scripts/render_diagrams.py --check
```

The committed visuals preserve motion as decoration: every first frame communicates the full
architecture, while arrows, route pulses, and status dots improve scanning. SVG is used on GitHub;
GIF stays under Devpost's 5 MB gallery limit. `enterprise-fleet-architecture-light.png` and
`enterprise-fleet-architecture-dark.png` are both emitted as static 1920×1080 stills: the light one
sits inside the light-background judge write-up, and the dark one is the Devpost architecture
upload and gallery image 01, because every other promoted capture is dark.
`brand/devpost-thumbnail-3x2.svg` is the editable source for the 1200×800
`brand/devpost-thumbnail-3x2.png` project thumbnail. The final five-image packet belongs under
`screenshots/` and is governed by
[`archive/hackathon-2026/submission/CAPTURE_RUNBOOK.md`](../archive/hackathon-2026/submission/CAPTURE_RUNBOOK.md).

## Demo video assets

`demo-voiceover/` holds twelve narration clips with a SHA-256 sidecar each, generated by
[`archive/hackathon-2026/scripts/generate_demo_voiceover.py`](../archive/hackathon-2026/scripts/generate_demo_voiceover.py), which is the source
of truth for the words. Chirp3-HD returns a slightly different duration for identical text on each
call, so the committed MP3 is the stable artifact and the sidecar stops a casual re-run from
re-jittering every timing the shot table depends on. `demo-video/bastion.srt` is the 36-cue caption
track emitted alongside them.

[`archive/hackathon-2026/scripts/assemble_demo_video.py`](../archive/hackathon-2026/scripts/assemble_demo_video.py) cuts the video from that
audio: each beat occupies its measured clip length plus its declared hold, so the picture cannot
drift from the sound and no timeline editor is involved. Four directories feed or receive it:

| Path | Tracked | What it holds |
|---|---|---|
| `demo-video/beats/` | no | Raw per-beat screen recordings. `00-hook.mp4` is produced by [`archive/hackathon-2026/scripts/capture_site_hook.mjs`](../archive/hackathon-2026/scripts/capture_site_hook.mjs) from the live public console. |
| `demo-video/statics/` | yes | Reviewed page captures the cut uses, promoted from ignored `.takes/` under the rules in [`screenshots/README.md`](../archive/hackathon-2026/assets/screenshots/README.md). |
| `demo-video/build/` | no | Per-beat segments and intermediates, reconciled against the current plan on every run so the directory cannot describe an older cut. |
| `demo-video/bastion.mp4` | no | The finished cut. Untracked because it is ~20 MB and rewritten on every render, which would add a blob to history each time; it is published at [https://youtu.be/Xpj8YmzFfpk](https://youtu.be/Xpj8YmzFfpk). |

A beat whose shots are not marked `final` is a stand-in for footage still to be recorded, and a
build containing one is written to `demo-video/build/` instead. The master name sits inside the
redaction gate's watched globs, so anything written there must be declared in `VIDEO_REDACTIONS`
and frame-reviewed before the offline gate passes again.

## Evidence rules

- Redact before committing, never after upload.
- Never retain raw IAM, principals, tokens, secret values, private endpoint inventories, prompts,
  responses, or trace payloads.
- Label historical topology evidence as historical.
- Distinguish configuration, deployment, one observed run, and historical SLO attainment.
- A simulated prior-week timestamp proves deterministic expiry/retrieval logic, not that a
  wall-clock week elapsed during the capture.

The five gallery screenshots were composed on 2026-08-27 and live under `screenshots/`; the video
remains a publication artifact. The under-four-minute demo should show the catalog, durable state,
identity denial, Model Armor refusal, minimized review record, and the correlated operations
surface without exposing a principal.

Supporting captures promoted under `evidence/screenshots/` are covered by the same redaction gate
as the gallery, because a file promoted to back a written record is likelier to be copied from
`.takes/` unreviewed.

Current inventory is separately recorded in [evidence 15](evidence/15-fleet-inventory.md):
28 October count-only census, 21 APIs/39 resources. It does not update the historical
binding count, prove a framework upgrade, or replace the August architecture masters.
