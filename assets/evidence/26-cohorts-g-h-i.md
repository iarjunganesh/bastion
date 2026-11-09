# Evidence 26 — cohorts G, H and I on the v0.9.0 and v0.9.1 deployments

**Collected:** 7–8 November 2026, three separately pre-specified cohorts, plus one read-only addendum
on 8 November. Each cohort is retained as executed. None was rerun, and none is pooled with
another or with N, F or the recovery ([evidence 24](24-upgraded-deployment-and-stopped-pilot.md),
[25](25-corrected-cohort-F-verification.md)). Only counts, statuses, timings, opaque IDs and
bounded reason codes were persisted.

## Shared method

- **Design.** G and H were planned as a pilot plus 100 serial production investigations, with
  per-run tokens on every fifth run, five completed-event replays, a direct Runtime control, a
  direct refusal probe and a forged-envelope pair. I repeats the design on v0.9.1. Each
  stops on its first failure.
- **Per-run pass criteria.** All of these must hold:
  - exactly one durable attempt, completed;
  - a gap-free correlated audit trail;
  - two review records whose finding counts equal a fresh count-only baseline
    ({platform-infra 1, security-engineering 2});
  - exactly two Auditor model completions;
  - exactly one HTTP 2xx Eventarc delivery to the dispatcher, matched by an isolated time
    window rather than message ID.

  On v0.9.1, audited model retries are counted separately and allowed up to six per run.
- **Baseline.** Each preflight measured 62 bindings and 3 findings, using a throwaway
  finding-ID key, with no active exception.
- **Pre-specification.** Protocols, caps and criteria were written down locally before each
  cohort, and each collector checked its pinned script hashes at start. No external timestamp
  establishes when a protocol was fixed. See *Provenance* below.

## Deployments

| | v0.9.0 (G, H) | v0.9.1 (I, and later J–M) |
|---|---|---|
| Source | Tag `v0.9.0`, `be5c6216796362e3689886f19d9e5778f0c2550c`, 52-file clean export | Tag `v0.9.1`, `755dd07211c178e958f6930d3bbbc4196acbb9ce`, 53-file clean export |
| Image | `sha256:bf3a89dc25974e934ca87a4ab0b921481ada93fe586b1050670333add8e4356f` | `sha256:435604e0610286f052f16bcdaec394631eda22ad39b58b38a2ce48d8b048196e` |
| In-build assertion | `google-adk` 2.14.0, `a2a-sdk` 1.3.0, SDK 2.6.0 | same |
| Runtime source update | ready 2026-11-07T19:30:14Z | ready 2026-11-07T22:53:07Z |
| Cloud Run | four existing services on that digest, protected configuration and IAM unchanged | same |

The Runtime's installed package resolution remains independently unreadable. H deployed nothing
and ran on G's verified fleet; its preflight checked that the fleet was unchanged.

## Results

| Cohort | Outcome | Classification |
|---|---|---|
| **G** (from 19:31Z, 7 Nov) | 4 validated, then stopped at G5 (`collector_RetryError`) | **Instrument stop.** The first Firestore read after a 2-minute token idle exhausted its 20-second retry deadline. A read-only drain found that G5 had completed in one attempt with 28 audit records. A read-only reproduction (20:07–20:14Z) did not fail, so the classification is transient Firestore unavailability |
| **H** (from 20:14Z) | 27 validated, then stopped at H28 (`unexpected_retry_or_failure`) | **System failure, failed closed.** The Auditor's model call got 429 `RESOURCE_EXHAUSTED`, ADK raised it, the Orchestrator raised `PolicyNotEnforcedError`, and the run was marked failed. Pub/Sub then redelivered it and attempt 2 completed (read-only follow-up). Under the protocol, the retry itself is the stop |
| **I** (22:53Z, 7 Nov – 01:52Z, 8 Nov) | **98 validated**, then stopped at I99 (`observation_read_unavailable_logging`) | **Instrument stop.** Cloud Logging returned HTTP 500 intermittently from 01:47 to 01:56Z, beyond the 180-second read window. I99 itself completed in one attempt |

| Measure | G | H | I |
|---|---|---|---|
| Validated investigations | 4 | 27 | 98 |
| Publications | 5 | 28 | 99 |
| Client confirmation median (min–max), s | 18.258 (15.485–31.172) | 15.484 (15.250–86.094) | 15.453 (15.250–60.781) |
| Correlated audit records, validated runs | 112 | 756 | 2,745 |
| Review records, validated runs | 8 | 54 | 196 |
| Model completions observed | 8 | 54 | 196 |
| Audited model retries | — | — | 1 (I57: one 429, recovered, one durable attempt) |
| Isolated-window project tokens, input / output | 7,046 / 6,666 | 43,751 / 44,676 | 167,064 / 163,604 |

- Confirmation times include 5-second client polling.
- The token figures are project-wide counts over each isolated window, not request-ID
  attribution.
- Observation read retries during I: 3 HTTP and 22 Logging.

**Cohort I's statistic.** The primary observation is 98 validated successes in 98. Under a
hypothetical independent, identically distributed Bernoulli model with constant failure
probability, zero failures in 98 trials gives a one-sided 95% Clopper–Pearson upper confidence
limit of about 3.01%. The serial, shared-infrastructure observations do not establish that
model, so the interval is illustrative. It is not a field reliability estimate or SLO.

Not reached in any of the three cohorts: the direct control, the replays, the refusal probe and
the envelope pair. [Evidence 27](27-targeted-controls-j.md) runs I's unreached steps separately.

## I99 read-only addendum (8 November, post hoc)

After I stopped, I's per-run criteria were applied to I99, read-only, at 08:55Z:

- one completed durable attempt;
- a gap-free trail of 28 audit records;
- delivered counts equal to the baseline;
- two model completions and no retries;
- one HTTP 200 delivery.

All criteria were met. **I99 stays outside I's 98.** The addendum does not change I's result.

## Disclosures

- **v0.9.1 exists because of H.** H28's 429 led to the bounded, audited model retry
  (429/500/502/503/504 only, at most 4 provider attempts per logical call, only before the
  first response). I57 shows one successful model-level retry, not general recovery from
  service failure.
- **Cost.** Credits only, under per-chunk caps. Collector projections stayed below their stops.
  Exact per-chunk cost is not measured.
- **Provenance.** Integrity runs from the seal (9 November 2026), whose manifest SHA-256 is
  `274d9901e84a9d45154c8bdc072e2ed00d3117e5a42a93a16ab3c81bb2d80e85`. Set hashes:

  | Set | SHA-256 |
  |---|---|
  | G | `ca29e9fb59a49bb8…` |
  | H | `aa5101d6877d9f92…` |
  | I | `56c138aa1784d429…` |
  | I99 addendum | `bef124e9d7f9ecfd…` |

  The seal establishes integrity from its date onward. It is not retrospective proof of when
  any protocol was fixed. The private records stay outside Git.
- Finite cohorts do not establish an SLO, general reliability, concurrency or scale behaviour.
