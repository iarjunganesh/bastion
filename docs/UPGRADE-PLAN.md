# ADK 2.13.0 upgrade and v0.8.0 plan

Requested 28 October 2026. Execute in the existing `feature/technical-report` branch.

**Sequencing note, 28 October:** the [report master plan](research/report-plan.md) proposes
decoupling this track from the report (decision D1). Until the maintainer answers D1, do not start
step 5; the control matrix below is scheduled there as evidence chunks E1–E6.

## Constraints

- Preserve starting report edits; keep manuscript changes uncommitted
  as explicitly requested; report sources/build tools are excluded from release commits.
- Latest stable ADK is 2.13.0 (PyPI/upstream verified 28 October); Python remains 3.12.
- Resolve required A2A, Google SDK, and telemetry dependencies together; regenerate the lock.
- Maintain three agents, deterministic gates, read-only IAM, payload-free audit, private origins,
  explicit project/quota selection, and current data regions. Do not weaken gates to upgrade.
- Preserve old sealed evidence bytes. Dated observations do not acquire new package versions.
- Target v0.8.0 because this includes a framework/SDK update and new evidence/documentation.

## Sequence and verification

1. Preservation: verify external ZIP and manifest; record starting Git state and report hash.
2. Shared continuity: root `AGENTS.md`, `HANDOFF.md`, report roadmap; thin Claude/Copilot files.
3. Dependencies: resolve production and development requirements on Python 3.12; inspect SDK
   and telemetry changes; run `pip check`, Ruff, mypy, 100%-coverage pytest, report/experiment tests.
4. Claims: reconcile every current Markdown/config/site reference; label historical versions.
   Run docs/version/redaction/diagram/site gates and rebuild/review the report.
5. Deployment: identify rollback revisions; update all four Cloud Run services and managed
   Runtime; verify readiness, installed resolution, route, private boundaries, and receipts.
6. Static console: deploy reviewed output separately through Vercel; verify production HTML,
   JSON, linked evidence, headers, mobile rendering, and absence of private network requests.
7. Controls: execute the matrix below in isolated, named cohorts with fresh evidence and stop
   rules. Compare with the old cohort without rewriting its facts.
8. Release: inspect full diff, validate release source, create v0.8.0 and verify Actions/release.
   A source-only release may state that production deployment is held; it must not mark the
   deployment/control steps complete or claim upgraded production.

## Control matrix

| Control / behavior | Existing evidence | Upgrade check and limits |
|---|---|---|
| Dependency and agent contracts | Offline core suite; A2A incident | Full suite, import/SDK smoke, structured state/content/receipt boundaries |
| Real IAM minimisation and findings | August capture; October successful runs | Count-only current census, canonical-field equality, no raw fields at model boundary |
| Durable asynchronous ingress | October 20 runs | Pilot, serial batch, correlated audit and attempt/receipt counts |
| Completed-event replay | Five publications; unchanged bounded effects | Verify individual delivery if available; distinguish acknowledgement from delivery |
| Gateway/Registry rejection | Negative managed refusal remains partial | Unregistered identity probe without changing production allowlists |
| Escalation IAM denial | August denied read | Re-probe using deployed identity; no IAM grants |
| Model Armor refusal | August authenticated A2A refusal | Approved injection fixture, fail-closed result, zero downstream tool/model activity |
| Human exception and expiry | Historical three-day suppression | Scoped test finding; approval, suppression, expiry; no forged elapsed-time claim |
| Timeout/retry/dead letter | Watched failure sequence remains partial | Isolated test subscription/service first; bounded retries and per-attempt evidence |
| Findings approval authorization | Offline/auth boundary checks | Missing/wrong token and invalid payload; no real human approval impersonation |
| Observability/retention/Scheduler | Historical configuration | Read-only configuration census; no bucket lock or retention mutation |
| Trace and audit correlation | Dated 22-span traces, payload-free audit | Capture upgraded trace schema; identify exact joins and sampling limitations |
| Load/concurrency and cost | Offline load; no attributed live currency cost | Bounded independent IDs; record tokens, elapsed time, errors and attributable cost |
| C4 comparison | Offline synthetic scaffold only | Separate matched-task protocol, synthetic data, pilot and cost-aware runner before batch |

## Execution limits to record before paid batches

Record confirmed credit expiry/balance, numeric study cap, per-phase event/call limits, wall-clock
limit, stop-on-failure behavior, and isolation/cleanup targets. Begin with one pilot. Stop on
missing required evidence, unexpected retry, protected-data exposure, or estimated budget
exhaustion. Cloud billing is delayed; a local guard is not a provider-enforced hard cap.

Production fault injection, policy changes, destructive cleanup, DOI deposits, and arXiv
submission are not routine verification actions. Use the narrowest test surface that proves
the control and keep actual human approval requirements intact.

## Credits-only execution and report order

Both rules are in [AGENTS.md](../AGENTS.md) and are not repeated here: paid work only within
allocated credits with no card charges, and one clean report generation after the evidence work.

## Release status

v0.8.0 is released as source on 28 October with one accepted, documented advisory; see
[DEPENDENCY-STATUS.md](DEPENDENCY-STATUS.md) and [issue #3](https://github.com/iarjunganesh/bastion/issues/3) for its removal. It does not
upgrade production: the fleet still runs its August deployment, and under decision D1 the
redeploy (step 5) waits until after the report's evidence freeze. The report remains
uncommitted and excluded from the release.

## Verified closeout

The static console was published from `d3fe889` and its public HTML/JSON/JavaScript match the
reviewed source. Desktop/mobile checks pass. The refreshed 150-package environment passes
321 core-suite cases at 100% configured coverage and mypy on 40 files. The existing fleet's
read-only configuration verifier passes with no new events, model calls or deployment.

PR #2 carried the security remediation; the remaining OpenTelemetry advisory was accepted for
v0.8.0 with a documented single-ID exception. The report is preserved locally; no further
manuscript/PDF edits occurred after the maintainer's correction.
