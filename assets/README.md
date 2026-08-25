# Judge-facing assets and evidence

Bastion's central claim is backed by redacted captures rather than architecture prose alone:

> Three governed agents inspect real IAM, retain asynchronous context, cross only catalogued
> enterprise boundaries, and create a minimized human-review record without gaining write access
> to IAM.

## Evidence ledger

| Evidence | Captured fact | Boundary |
|---|---|---|
| [01 — Model Armor block](evidence/01-model-armor-block.md) | The live regional template refused a prompt-injection sample | Direct managed-service probe; callback wiring is additionally tested |
| [02 — Gemini investigation](evidence/02-gemini-investigation.md) | Gemini 3.5 Flash processed minimized state from a real IAM review | Historical pre-Gateway run; **superseded 2026-08-25 by evidence 11** as current-route proof and retained as history only |
| [03 — identity denial](evidence/03-escalation-agent-denied.md) | Escalation was denied IAM read while Auditor was permitted | Workstation impersonation of deployed identities |
| [04 — private fleet](evidence/04-private-fleet-deployment.md) | 21 APIs and 39 deployed resources measured without principals | Count-only inventory, not a request trace |
| [05 — Runtime and Gateway](evidence/05-runtime-gateway.md) | Managed Runtime session streamed events; Gateway/Registry/IAP configuration verified | Status and count proof; no private URLs or identities retained |
| [06 — durable findings](evidence/06-durable-findings.md) | Eventarc/Firestore completion plus findings IAM and idempotency | Live production smoke; payload intentionally omitted |
| [07 — observability](evidence/07-observability.md) | Regional audit retention, sink, metrics, alerts, and dashboard exist | Reviewed bucket capture proves region, 365-day retention, and analytics; not immutability/WORM or historical SLO attainment |
| [08 — tool poisoning](evidence/08-tool-poisoning.md) | Fixed tool sets at construction; Escalation holds no policy tool or Asset client | Construction-time proof, verified to fail when widened; not a live refusal trace |
| [09 — cross-department routing](evidence/09-cross-department-routing.md) | 52 live bindings produced 3 findings routed to 2 owning departments | Counts and department ids only; routing measurement, not a completed investigation. Its 52 bindings are that date's measurement — evidence 11 measured 62 on 2026-08-25 and is the current figure |
| [10 — cross-week suppression](evidence/10-cross-week-suppression.md) | A human exception approved 2026-08-19 suppressed its matching finding on 2026-08-22, on the deployed path; re-confirmed 2026-08-23 after the deterministic-delivery rewrite (P0.1–P0.3) | Three-day gap, not a calendar week; expiry firing is covered by tests only |
| [11 — current-route correlation](evidence/11-current-route-correlation.md) | One fresh investigation completed across Runtime, deployed Auditor and Escalation revisions, and Gemini 3.5 Flash; a companion probe measured 62 bindings, 3 canonical findings, and 2 post-policy deliveries | Payload-free route correlation plus count-only companion measurement; reviewed raw source awaits final gallery composition |
| [12 — agent-mediated Model Armor refusal](evidence/12-agent-mediated-model-armor-refusal.md) | The deployed Auditor callback refused the approved injection sample and its A2A task failed before another model or tool call | Direct authenticated Auditor probe, not a durable Runtime investigation; reviewed raw source awaits the IAM-denial composite |
| [13 — current-route trace](evidence/13-current-route-trace.md) | One connected 22-span Cloud Trace covered the managed Runtime, both A2A workers with their agent-card fetches, the Firestore exception lookup inside the policy step, and the completion gate | Sampled explanatory telemetry with span attributes deliberately unopened; not the retained compliance record and not a latency claim |

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
GIF stays under Devpost's 5 MB gallery limit. `enterprise-fleet-architecture-light.png` is the
static 1920×1080 upload for Devpost's required architecture field.
`brand/devpost-thumbnail-3x2.svg` is the editable source for the 1200×800
`brand/devpost-thumbnail-3x2.png` project thumbnail. The final five-image packet belongs under
`screenshots/` and is governed by
[`submission/CAPTURE_RUNBOOK.md`](../submission/CAPTURE_RUNBOOK.md).

## Evidence rules

- Redact before committing, never after upload.
- Never retain raw IAM, principals, tokens, secret values, private endpoint inventories, prompts,
  responses, or trace payloads.
- Label historical topology evidence as historical.
- Distinguish configuration, deployment, one observed run, and historical SLO attainment.
- A simulated prior-week timestamp proves deterministic expiry/retrieval logic, not that a
  wall-clock week elapsed during the capture.

Screenshots and video remain publication artifacts. The under-four-minute demo should show the
catalog, durable state, identity denial, Model Armor refusal, minimized review record, and the
correlated operations surface without exposing a principal.
