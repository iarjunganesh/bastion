# Judge-facing assets and evidence

Bastion's central claim is backed by redacted captures rather than architecture prose alone:

> Three governed agents inspect real IAM, retain asynchronous context, cross only catalogued
> enterprise boundaries, and create a minimized human-review record without gaining write access
> to IAM.

## Evidence ledger

| Evidence | Captured fact | Boundary |
|---|---|---|
| [01 — Model Armor block](evidence/01-model-armor-block.md) | The live regional template refused a prompt-injection sample | Direct managed-service probe; callback wiring is additionally tested |
| [02 — Gemini investigation](evidence/02-gemini-investigation.md) | Gemini 3.5 Flash processed minimized state from a real IAM review | Historical pre-Gateway run; not proof of the current route |
| [03 — identity denial](evidence/03-escalation-agent-denied.md) | Escalation was denied IAM read while Auditor was permitted | Workstation impersonation of deployed identities |
| [04 — private fleet](evidence/04-private-fleet-deployment.md) | 21 APIs and 33 deployed resources measured without principals | Count-only inventory, not a request trace |
| [05 — Runtime and Gateway](evidence/05-runtime-gateway.md) | Managed Runtime session streamed events; Gateway/Registry/IAP configuration verified | Status and count proof; no private URLs or identities retained |
| [06 — durable findings](evidence/06-durable-findings.md) | Eventarc/Firestore completion plus findings IAM and idempotency | Live production smoke; payload intentionally omitted |
| [07 — observability](evidence/07-observability.md) | Regional audit retention, sink, metrics, alerts, and dashboard exist | Configuration proof; not historical SLO attainment |
| [08 — tool poisoning](evidence/08-tool-poisoning.md) | Fixed tool sets at construction; Escalation holds no policy tool or Asset client | Construction-time proof, verified to fail when widened; not a live refusal trace |

## Architecture and brand assets

`architecture/level-1-context.svg` and `level-2-container.svg` are the reviewed 1920×1080
masters. `scripts/render_diagrams.py` emits light/dark variants and animated GIFs. The README
banner uses hand-reviewed light/dark SVGs; the 16:9 Devpost banner is another generated master.

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
GIF stays under Devpost's 5 MB gallery limit.

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
