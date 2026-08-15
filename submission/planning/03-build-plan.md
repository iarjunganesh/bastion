# Bastion — 18-Day Build Plan (Solo)

**Written Thu Aug 13, 2026. Deadline: Aug 31, 2026, 5:00 PM PT.**

Supersedes the earlier 21-day version, which was mis-dated (see `06-project-review.md`).

> **Reality check, Fri Aug 14 — superseded 2026-08-15.** Thursday's list did not complete:
> `git init`, the first commit, the GEAR badge, Devpost registration, and the hello-world ADK
> call were all outstanding, and two of the three pass/fail requirements were unmet in code.
>
> **What changed on Aug 15.** The seven DIY pillar modules were deleted (~3,460 lines) as
> reimplementations of managed GEAP products
> ([ADR-003](../../docs/adr/003-pillars-on-geap.md)); the three agents were rewritten on ADK
> 2.7.0; and all three pass/fail requirements were met in code that ran
> ([evidence 02](../../assets/evidence/02-gemini-investigation.md)). What stands today is three
> ADK agents, cross-department routing, 132 tests at 100% coverage, seven ADRs, and the current
> Historical build-plan note. The initial commit and private fleet deployment are complete; use
> the current release ledger for active proof work.

## Status of prerequisites

- [x] **$150 GCP credit code received** (Aug 12) — the Aug 28 form deadline no longer applies to you
- [x] **Hackathon credit redeemed and visible** (Aug 13). Billing identifiers and balances are
  retained only in private operator notes.
- [x] GCP project created, APIs enabled, and budget alert set. Account identifiers and private
  balance details are intentionally omitted. The budget excludes credits so it tracks
  gross usage. A trial account cannot charge a card: when credits are exhausted, services
  stop and a manual upgrade is required. That is a harder guarantee than a budget alert.
- [ ] GEAR badge claimed (free, 10 min, via Google Developer Program profile)
- [ ] Devpost registration + category = Fortified Enterprise Fleet
- [ ] Repo initialized, first commit inside the Submission Period

## Scope, as cut for 18 days solo

**Three agents, not four** — Policy Enforcer merges into the Orchestrator. **Real GCP IAM data, not mock rows.** Thin gateway. One escalation output surface. See `06-project-review.md` for the reasoning.

| Agent | Role |
|---|---|
| Orchestrator | Triggers investigations, routes work, applies policy rules, owns retry/escalation |
| Access Auditor | Reads real GCP IAM policy, flags overly broad/stale/unused grants |
| Escalation Agent | Packages high-risk findings for a human; write-only, no data read access |

## Today (Thu Aug 13) — setup + catch tonight's webinar

- Create GCP project; enable Vertex AI, Cloud Run, Firestore, Pub/Sub, Cloud Trace, Cloud Logging, Model Armor
- **Set a budget alert before deploying anything**
- ~~Redeem the $150 credit code~~ — done; account identifier intentionally omitted
- Claim the GEAR badge
- Register on Devpost, select Fortified Enterprise Fleet
- `git init`, first commit of the scaffold
- Confirm a hello-world ADK agent calls **Gemini 3.5 Flash** via Vertex AI
- **Tonight, 9:00–10:30 PM PT: "Build a Long-Running Agent: Persistent Workflows with Google ADK."** This is today's webinar and it's the single most relevant one to your Orchestrator's retry/idempotency logic. Catch the evening slot if the morning one has passed.

## Fri Aug 14 — GEAP decided ✅, then close the two pass/fail gaps

- [x] **GEAP go/no-go — decided inside the cap.** The question was answerable from the SDK
      surface without provisioning anything: ADK's `BaseMemoryService`/`BaseSessionService` make
      GEAP a backend rather than a fork. **Amended 2026-08-15:** the conclusion that the
      Registry had no managed equivalent was wrong — Agent Registry and Agent Gateway are both
      managed GEAP products, and all seven pillars now take the managed path.
      [ADR-003](../../docs/adr/003-pillars-on-geap.md).
- [x] **Make the agents ADK agents.** Done 2026-08-15 — three `LlmAgent`s under a
      `SequentialAgent`, each with Model Armor on `before_model_callback`. *(Was: pinned and
      importable, imported nowhere — a pinned dependency is not a framework.)*
- [x] **Write the first Gemini call site.** Done 2026-08-15 — 5 model calls in one
      investigation over the live IAM policy, detection still deterministic.
- [ ] Pull the real IAM policy **to a gitignored file** and eyeball what a real finding looks
      like. Redirect it; do not print it — see `SECURITY.md`.

## Weekend Aug 15–16 — core loop end to end

- Orchestrator: triggers from Pub/Sub, writes investigation state
- Access Auditor: parses real IAM policy, flags 3–5 real anomalies (broad roles, `roles/owner` grants, service accounts with no recent activity)
- Policy rules (now inside Orchestrator): 3–4 hardcoded rules deciding clear vs escalate
- **Milestone by Sun night: one full investigation runs start to finish against real IAM data, state visible in Firestore/GEAP console**

## Mon Aug 17 – Fri Aug 21 — the pillars become real

- **Mon:** Agent Registry — register all 3 agents with name/version/owner/scope
- **Tue:** Agent Identity — 3 scoped service accounts; *verify a mis-scoped call actually fails* and screenshot the denial
- **Wed:** Agent Gateway (thin) — registration check + call logging, nothing more
- **Thu:** Model Armor — wire in front of Gemini calls; confirm the malicious-ticket case is blocked. **This is the riskiest component; if it's not working by end of Thursday, switch to the documented fallback** (heuristic + a Gemini yes/no injection check) rather than burning Friday on it
- **Fri:** OpenTelemetry → Cloud Trace, **plus structured audit logs to Cloud Logging** — the
  brief names *"audit logs **and** reasoning chain traces"*, two artifacts, and a sampled trace
  is not an audit record ([ADR-006](../../docs/adr/006-pillar-coverage.md)). Memory Bank
  exception recall working: two consecutive runs, raised then suppressed
- **Milestone by Fri night: every pillar has a screenshot-able artifact**

## Weekend Aug 22–23 — failure tolerance + diagram + README

- Orchestrator retry/escalation when the Auditor times out or returns low confidence (directly graded under Architecture)
- Escalation Agent → the dashboard. One surface, and it was settled by
  [ADR-003](../../docs/adr/003-pillars-on-geap.md) — Slack is not among the twenty-one services
- Render the architecture diagram as an actual image
- README spin-up instructions, written for someone who has never seen the repo
- **Checkpoint: if the core loop still isn't solid by Sun Aug 23, cut to 2 agents and protect the video**

## Mon Aug 24 – Wed Aug 26 — record and write

- Record the shot list from `02-demo-storyboard.md` — raw clips first, edit after
- Rehearse the Model Armor block and the memory-recall beat until they run clean on camera; these are the two moments that carry the demo
- Edit to under 4:00, upload public to YouTube
- Write the Devpost description: features, technologies, data sources, findings/learnings
- **Keep the services running — do not tear down.** Rechecked against the rules page Aug 13:
  a Hosted Project URL is a submission field and *"a hosted project is highly encouraged."*
  Judging runs **Sept 1 – Oct 1**, and at `min-instances=0` an idle Cloud Run service bills
  nothing, so staying live through judging is close to free and fills a field that teardown
  forfeits. The safety net if something breaks unattended: *"judges are not required to test
  the Project and may choose to judge based solely on the text description, images, and video
  provided."* The video still carries the submission.

## Thu Aug 27 – Fri Aug 28 — bonus points and buffer

- Blog post on dev.to/Medium covering how it was built, with explicit "created for the All Things Agentic Hackathon" language (+0.2)
- Social post with #AllThingsAgenticHackathon (+0.2)
- Cold self-scoring pass: score your own submission against `00-judging-matrix.md` as if you were a judge who has never seen it
- Fix whatever that pass exposes

## Sat Aug 29 – Sun Aug 30 — submit

- **Submit Saturday Aug 29 if at all possible.** The deadline is Monday 5 PM PT; submitting two days early costs nothing and protects against platform issues that Devpost explicitly disclaims responsibility for
- Final checks: category = Fortified Enterprise Fleet · repo public (or shared with <testing@devpost.com> and <cloudhackathons@google.com>) · video public on YouTube/Vimeo · architecture diagram attached · spin-up instructions present

## Mon Aug 31 — buffer only

Do not plan work here. This day exists to absorb something going wrong.

## Risk register

| Risk | Mitigation |
|---|---|
| ~~Model Armor doesn't work in time~~ | **Retired.** It works, and was observed blocking on Aug 15; [ADR-003](../../docs/adr/003-pillars-on-geap.md) withdrew the Gemini-based fallback rather than leave a weaker control described in stronger words |
| ~~GEAP evaluation eats the schedule~~ | **Retired.** Decided Aug 14 inside the cap ([ADR-003](../../docs/adr/003-pillars-on-geap.md)) |
| ~~Pass/fail gates unmet~~ | **Retired Aug 15.** All three met in code that ran: 5 Gemini calls, three ADK `LlmAgent`s, and Cloud Asset Inventory against the live policy |
| **Private fleet deployed** | The one requirement with no partial credit is met ([ADR-006](../../docs/adr/006-pillar-coverage.md)); remaining work is retained operational evidence |
| Core loop slips past Aug 23 | Cut to 2 agents; the video matters more than agent count |
| Demo recording goes badly | Raw clips recorded Aug 24, three days before they're needed |
| Field is now 2,327 participants | Differentiation comes from real IAM data + the live injection block + the captured denial, not more features |
