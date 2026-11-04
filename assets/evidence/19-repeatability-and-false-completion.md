# Evidence 19 — repeatability batch and a false completion

**Captured:** 3 November 2026, evidence chunks E7 (20:20–20:37 UTC) and E7b (20:46–21:48 UTC)
of cohort N, on the unchanged August deployment. Serial investigations published to the
production topic, each checked for its durable status, delivered review records and the
28-event correlated audit trail. No retries, deployments, IAM or exception changes. The private
bundles record counts, timings and opaque event IDs only.

## E7: stopped at run 8 by design

Runs 1–7 passed. Run 8's durable record reads **completed, one attempt, 81 seconds**, but no
audit record, review record or model call exists for it: no investigation ran. The stop rule
(delivered counts must equal 1 `platform-infra` + 2 `security-engineering`) halted the batch.

Runtime logs show the request reached the managed Agent Runtime and two new Runtime instances
started during the run. The durable ingress (`run_managed_runtime`) records success when the
Runtime's response stream ends, without checking that an investigation ran, so an empty stream
becomes a completed investigation. Say **the durable lifecycle can record a completion for work
that never ran**. This deployment does not detect it; only the external stop rule did.

## E7b: fresh 20-run batch

E7b was set to record a false completion and continue, stopping only after three in a row;
every other check still stopped the batch. No false completion occurred in E7b.

| Measure | Result |
|---|---|
| Investigations published / passed | 20 / 20 |
| False completions | 0 |
| Durable attempts per run | 1 in every run |
| Correlated audit events per run | 28 in every run, no gaps |
| Model calls per run | 2 (`gemini-3.5-flash`), 40 in total |
| Delivered findings per run | 1 `platform-infra` + 2 `security-engineering` |
| Eventarc deliveries | 25 requests for 25 publications (20 runs + 5 replays), all 200, none unmatched |
| Completed-event replays | 5 of 5 left durable, review and agent-invocation state unchanged |
| Publish to observed completion | median 20.4 s; 15 of 20 under 45 s; 5 between 136 and 206 s |
| Tokens per run (input / output) | median 1,788 / 1,600; ranges 1,349–2,288 / 1,050–1,959 |
| Tokens in total (input / output) | 35,858 / 31,966; no minute left unattributed |
| Runs with a sampled trace | 18 of 20, matched by time window only |

Per-run tokens come from the project-wide Vertex AI token metric. Runs were separated by two
idle minute boundaries, and each minute was assigned to the latest run published before it.
Currency cost is not derived here; the billing record is the source.

## The latency tail

Five runs took 136–206 seconds. None failed, and each delivered the expected findings.

| Run | Total (s) | Where the time went | Runtime instance start during the run |
|---|---:|---|---|
| 8 | 206 | `policy_gate` 186 s (normally 0.3 s) | Yes |
| 10 | 196 | `policy_step` 175 s (normally about 1 s) | No |
| 13 | 191 | 174 s before the Runtime's first audit record | Yes |
| 17 | 136 | `policy_step` 113 s | No |
| 19 | 186 | 169 s before the Runtime's first audit record | Yes |

Two patterns: a wait before the Runtime starts the investigation, which coincided with a new
Runtime instance both times, and a stall inside a stage that makes no model call. The cause of
the stage stalls is not established. Do not attribute them to the model.

## Proof boundary

One batch of 20 is not a reliability rate. Together E7 and E7b give 28 investigations with one
false completion; report that count with its denominator, not as a percentage. Traces are
sampled request-level spans with no investigation or invocation ID, so audit-to-trace
correlation is by time window only.
