# Evidence 16 — human exception approval, suppression and expiry

**Captured:** 3 November 2026, 19:19–19:46 UTC, evidence chunk E4 of cohort N. Three
investigations on the unchanged August deployment, one human exception approval, no retries
or replays, no deployment, IAM change or fault injection. The private bundle (collector,
protocol, per-run metrics, manifest) is sealed outside Git; this page records counts only.

## Protocol

1. **R1, baseline:** publish one investigation event and wait for its delivered findings.
2. **Approval:** the maintainer's identity, impersonating the configured approver service
   account, posts an exception for R1's `platform-infra` finding through the findings API,
   valid for 15 minutes. The maintainer authorized this approval for the test.
3. **R2, inside the window:** publish a second event and wait for completion.
4. **Wait** until 120 seconds after the exception's expiry.
5. **R3, after expiry:** publish a third event and wait for completion.

Stop rules: any run over 600 seconds, missing or failed audit events, or an unexpected
delivered count stops the chunk without a rerun.

## Result

| Run | Started (UTC) | Delivered `platform-infra` | Delivered `security-engineering` | Audit events | Audit gaps | Event to completion (s) |
|---|---|---:|---:|---:|---:|---:|
| R1 baseline | 19:19:29 | 1 | 2 | 28 | 0 | 121.3 |
| R2 inside window | 19:21:43 | 0 | 2 | 28 | 0 | 20.2 |
| R3 after expiry | 19:38:43 | 1 | 2 | 28 | 0 | 111.0 |

- The approval returned HTTP 201 and echoed the same finding and expiry. It replaced the only
  earlier exception record, which had expired on 18 September 2026 (policy `v0.1.0`). Its
  non-identity fields were recorded before replacement.
- R2 finished before the exception expired. It delivered no `platform-infra` finding.
- R3 started 120 seconds after expiry. It delivered the **same** `platform-infra` finding as
  R1, compared by finding ID inside the private collector.

Say **an approved exception suppressed one finding for its window and the finding returned
after expiry**. This is one lifecycle on one finding. It is not a rate, a load result, or
evidence about multiple concurrent exceptions.

## Limits observed

- **Durations:** R2 was faster at every stage, including the Access Auditor, which suppression
  does not affect. R1 followed about a week of idle time, so cold starts are a likely
  confounder. Do not attribute the 101-second difference to suppression.
- **Tokens:** the Vertex AI token metric is project-wide and minute-aligned. Back-to-back runs
  share minutes (R2's window counted more output tokens than R1's), so per-run token
  attribution from this chunk is not valid. E7 spaces its runs to fix this.
- **Traces:** Cloud Trace sampled four request-level traces in the window (two or three spans
  each, no agent or model spans). The audit log entries carry no trace ID, so audit records
  and traces join by time window only.
