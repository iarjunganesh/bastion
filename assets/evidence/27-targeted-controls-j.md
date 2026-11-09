# Evidence 27 — targeted controls J on the v0.9.1 fleet

**Collected:** 8 November 2026, 08:29–08:55 UTC. Chunk J deployed nothing. Its read-only
preflight (08:27Z) confirmed the fleet was exactly [evidence 26](26-cohorts-g-h-i.md)'s v0.9.1
deployment, with the same 62-binding / 3-finding baseline.

J runs only the steps that cohort I pre-specified but never reached, in I's order and with I's
code unchanged. It is reported separately and is never pooled with I's 98 investigations.

## Protocol and amendment

- **Replay substitution.** The protocol was recorded at 08:29:01Z and execution started at
  08:29:29Z. I100 was never run, so its replay was replaced by I98, I's last validated run. The
  substitution was written into J's protocol before execution.
- **Cap.** 20 SEK, credits only. The collector's final projection was 11.57 SEK, an estimate
  rather than a measured cost.

## Results (all passed)

| Case | Observation |
|---|---|
| **J0** direct Runtime control (08:31Z) | Trusted completion confirmation observed in the returned stream (5 events, 94.2 s, first run after an idle period). 28 correlated audit records, 2 model completions, 2 review records equal to baseline, no retries |
| **R1–R5** completed-event replays of I1, I25, I50, I75, I98 | One HTTP 200 delivery each. Within each 120-second window the replays produced **no additional durable, review, agent-invocation or model effects** against the originals' recorded state. Delivery population re-verified |
| **X1** direct Auditor refusal (08:49Z) | Exactly one Model Armor input refusal, joined to the probe's own investigation ID. The task state was `TASK_STATE_FAILED`. Detail below this table |
| **Envelope positive control** (policy-step zero departments) | Task completed, no rejection reason, 0 review records |
| **Forged envelope** (model-written departments attributed to the Auditor) | Rejected as `missing_routing_envelope`, task failed, 0 review records |

X1 detail:

- No model or tool work occurred at or after the refusal over the 75.8-second observation.
- The only earlier work record is the audit plugin's own pre-callback `submitted` entry.
- No review record was created.

Publications: 5 (the replays only). Project-wide isolated-window tokens: input 1,750, output
1,879.

## What this establishes, and what it does not

- **Routing provenance.** v0.9.1 rejects routing attributed to the Auditor in the relayed
  history. Bare JSON on the authorized request path is still accepted by design, and is bounded
  by the worker-origin credential. This test does not prove that unauthorized routing content
  can never be accepted.
- **J0** shows a positive completion confirmation directly. It is not a test of the completion
  gate's rejection path.
- **Replays.** These are five bounded duplicate-delivery observations, not a guarantee of
  exactly-once delivery.
- The direct control and the refusal probe created their own records, disclosed here and
  excluded from any cohort population.

**Seal:** J set `c16cc6d73935d542…`, in the 9 November manifest
`274d9901e84a9d45154c8bdc072e2ed00d3117e5a42a93a16ab3c81bb2d80e85`. It establishes integrity
from that date only.
