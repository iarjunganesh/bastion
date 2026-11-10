# ADK upgrade closeout

Updated 9 November 2026. v0.8.0 was released as source on 28 October with one accepted
OpenTelemetry advisory; v0.9.0 moves to ADK 2.14.0 and OpenTelemetry 1.45.2, which resolves it
([dependency status](DEPENDENCY-STATUS.md)). Source pins do not prove a
deployed resolution; [VERSIONS.md](VERSIONS.md) is the canonical provenance table.

## Completed

- Dependency/contract validation targets Python 3.12, Google ADK 2.14.0 and A2A SDK 1.3.0
  (v0.9.0; the 5 November deployments ran `google-adk` 2.13.0).
- Cohort N remained on the August deployment and was frozen before the upgrade.
- On 5 November, one image updated four existing Cloud Run services and managed Runtime was
  updated separately. Image package assertions and configuration checks passed; the F pilot
  failed closed on an Escalation routing-parser incompatibility ([E24](../assets/evidence/24-upgraded-deployment-and-stopped-pilot.md)).
- The separate exact parser correction was deployed in a new image. Five normal cases, a direct
  confirmation control and two replays passed. The refusal join was verified by a read-only
  addendum after a collector temporal false positive ([E25](../assets/evidence/25-corrected-cohort-F-verification.md)).
  Runtime stayed unchanged during recovery; its installed packages remain independently unreadable.
- The 6 November reported-usage billing check passed. Private values and late-posting limits
  are in the credit record; no new paid execution follows from this checklist.

## Current verification and remaining work

1. The 6 November reconciliation and local PDF are drafts, superseded. v0.9.0 and v0.9.1 were
   deployed on 7 November and cohorts G–M are recorded (evidence 26–29). One definitive report
   is written once from the blueprint frozen on 9 November.
   Preserve the audit corrections, collection disclosures and both separately sealed F records.
2. The final offline gates passed; commands remain in [AGENTS.md](../AGENTS.md): core coverage, Ruff, mypy, docs/version,
   evidence redaction, diagram freshness, static site and Markdown checks. Check diagrams only;
   rendering them changes assets embedded in the frozen Devpost entry.
3. The report sources were committed by PR #18 and released on 10 November as tag
   `report-2026-11`; build output stays ignored and is attached to the release. Report
   generation is not a routine code gate.
4. Follow D4's existing 8–10 November dry-run-first end-state window and residual-resource decision
   in the [report plan](research/report-plan.md). Do not broaden deletion targets.
5. Public code, documentation and E24/E25 are published through
   [PR #9](https://github.com/iarjunganesh/bastion/pull/9), with merge authorized after hosted CI.
   Site build checks do not verify deployed Vercel bytes; report publication remains separate.
   Vercel redeploys the console from `main`, so the PR #9 merge published its site changes: on
   7 November the live footer matched commit `2a12f5f`. Treat every merge to `main` as a site
   deployment; the maintainer kept this auto-deploy on 7 November.

## Boundaries for any later upgrade

Keep three agents, deterministic policy/completion, real read-only IAM, payload-free audit,
private worker origins, explicit project/quota values and current regions. Changes to the
Orchestrator graph require both Cloud Run and managed Runtime deployment surfaces.

Before any new paid batch, prepare a control matrix, eligible-credit check, numeric budget,
event/call/time limits and stop rules. Start with a pilot and stop on missing evidence, unexpected
retry, protected-data exposure or estimated exhaustion. Credit balances and budget alerts are
not hard caps. Preserve all older captures with their actual versions.

The source-only v0.8.0 closeout and earlier static-site publication are dated release history.
PR #9 records the current source integration; it does not perform another GCP deployment.
