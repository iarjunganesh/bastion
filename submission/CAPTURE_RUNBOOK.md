# Final evidence and gallery capture runbook

**Purpose:** close only the observations required for safe public claims, then produce the five
Devpost gallery images. Raw captures belong in ignored `.takes/`; only reviewed, cropped, redacted
artifacts move into `assets/screenshots/` or `assets/evidence/`.

Do not start the video until this runbook's evidence sprint and gallery acceptance gate are
complete. Do not expose service-account principals, private origins, tokens, secrets, prompts,
responses, raw IAM members/roles/resources/bindings, or unredacted exception messages.

## Before the first capture

- [ ] Freeze the code revision that will appear in the video.
- [ ] Reconfirm the deployed revision matches it.
- [ ] Use a clean browser profile with notifications, bookmarks, extensions, and autofill hidden.
- [ ] Set the desktop and browser to 1920×1080 and at least 125% console text zoom.
- [ ] Prepare narrow, count-only console filters before recording anything.
- [ ] Create a fresh ignored directory under `.takes/` for raw screenshots and recordings.
- [ ] Confirm the healthy revision and rollback path before any staged failure.

## Evidence sprint — execute in this order

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

- Observe the intended unregistered destination/caller refusal on the managed path.
- Observe the undeclared-skill/destination refusal if the platform exposes that distinction.
- Capture the managed authorization result, not only local gateway-policy tests.
- Acceptance: name only the refusals actually observed. Never call the instance cap or delivery
  bound a per-caller rate limit.

### 6. Timeout, retry, and bounded failure — P0.11

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

### 01 — `assets/screenshots/01-enterprise-fleet-architecture.png`

Source: `assets/architecture/enterprise-fleet-architecture-light.png`.

Caption: **A managed, zero-trust institutional-agent fleet where raw IAM stops before the model.**

Acceptance: three agents, seven managed pillars, data-minimization boundary, durable state, and
audit/trace outputs are readable at gallery-thumbnail size.

### 02 — `assets/screenshots/02-governed-agent-catalog.png`

Show Runtime plus two worker cards in Agent Registry. Keep owner, department, version, skill,
classification, and approval metadata readable; hide origins and identities.

Caption: **Versioned institutional agents catalogued with explicit ownership, skills, and policy.**

### 03 — `assets/screenshots/03-production-iam-routing.png`

Show the final current-route binding count, deterministic findings, and owning departments. Do not
show principal/member values.

Caption: **One production IAM review routes minimized findings to the teams that actually own them.**

### 04 — `assets/screenshots/04-enforced-security-boundary.png`

Show Auditor read permitted and Escalation read denied; add the agent-mediated Model Armor refusal
only if both panels remain legible.

Caption: **Separation of concerns enforced by IAM and inline screening—not by agent instructions.**

### 05 — `assets/screenshots/05-durable-context-and-audit.png`

Show exception approval date, later suppression date, no notification for the suppressed
department, and one investigation ID across Runtime/workers. Label trace versus retained audit.

Caption: **A human decision survives deployments and remains reconstructable in retained audit records.**

## Gallery acceptance gate

- [ ] Exactly five ordered files exist under `assets/screenshots/`.
- [ ] Each is 1920×1080, under 5 MB, and legible at 480 px width.
- [ ] Captions describe visible proof rather than implementation intent.
- [ ] Every image passed a sensitive-data inspection at 200% zoom.
- [ ] The architecture image matches the final deployed inventory.
- [ ] No screenshot upgrades a `Partial` claim without an updated evidence record.
- [ ] A signed-out reviewer can understand the sequence without narration.
