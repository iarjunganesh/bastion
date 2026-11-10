## 5. Evaluation method

### 5.1 Records and populations

The evaluation draws on dated records, each kept as its own population:

- **August–October observations** on the earlier deployment: E10–E14;
- **cohort N** (3–4 November) on the unchanged August build: E16–E23;
- **cohort F and its recovery** (5 November) after the first framework upgrade: E24, E25;
- **the final evaluation**, G–M (7–8 November), on v0.9.0 and v0.9.1: E26–E29.

Records are never pooled across deployments, cohorts or protocols. The final bounded evaluation in Section 7 is G–M. The August–October and N records form the pre-upgrade baseline (Section 7.6); F and its recovery are post-upgrade history (Section 6).

### 5.2 Workload

Every G–M preflight took a fresh count-only baseline of the production project, using a throwaway finding-ID key and checking that no exception was active: 62 IAM bindings, 3 findings, 2 departments (`platform-infra` 1, `security-engineering` 2). The baselines were taken at 18:55Z, 20:09Z and 22:44Z on 7 November for G, H and I, and at 08:27Z on 8 November for J. M's preflight repeated the check. This is a deliberately bounded configuration, not a representative sample of IAM estates. The August and October binding censuses (62 and 56 bindings) are never reused for November. [E11, E23, E26, E27]

### 5.3 Per-run pass criteria

A serial production investigation passes only if all of these hold. No other quantity is a criterion.

| Quantity | Requirement | Source |
|---|---|---|
| Durable investigation attempts | Exactly 1, status completed | Firestore record, by event ID |
| Audit trail | Gap-free under the sealed audit observer's contract | Cloud Logging, by investigation ID |
| Review records | 2, one per routed department, with finding counts equal to the fresh baseline | Firestore review store |
| Logical model completions | Exactly 2 Auditor `model.request/completed` records | Audit trail |
| Audited model retries (v0.9.1) | Counted separately as `model.request/retrying`; at most 6 per run, and an exhausted retry fails the run | Audit trail |
| Eventarc ingress deliveries | Exactly 1 to the dispatcher, HTTP 2xx | Cloud Run request log, by isolated time window (not message ID) |

Two quantities are explicitly not criteria: the findings API's notification status and the number of underlying provider attempts.

### 5.4 Design of the final cohorts

G and H, on v0.9.0, were each planned as a pilot plus 100 serial production investigations. Each plan included per-run tokens on every fifth run, five completed-event replays, a direct Runtime control, a direct refusal probe and a forged-envelope pair. I repeats the design on v0.9.1. Each cohort stops at its first failure, and each stop is classified before anything else runs. J executes, in I's order and with I's code, the steps that I never reached. K isolates Runtime trace export. L and M inject a worker timeout. [E26–E29]

### 5.5 Pre-specification and provenance

Three distinct statements apply to every G–M protocol:

1. The protocol and its criteria were documented before execution, according to the project's internal local records.

2. The execution scripts checked their hashes at start-up against the locally recorded protocol or cost-admission pins. This establishes that the specified consistency check ran at execution.

3. No independent external timestamp establishes when any protocol was fixed. The protocols are therefore described as **pre-specified**, never as pre-registered.

The sealed hashes were published on 9 November 2026 (manifest SHA-256 `274d9901…`). They establish integrity from that date onward. They are not retrospective proof of independent pre-registration. M's original protocol hash was not recorded at the time; it was reconstructed after the run by removing the amendment record (`5425df…`). This is an additional, explicit limitation. [E26, E29]

### 5.6 Instrument policy

- Collectors may retry observation reads within bounded windows. They do not manually repeat or replace measured publications or probes. Automatic Eventarc redelivery and v0.9.1 model retries are observed system behaviour and are counted separately.
- A stop caused by the measurement instrument is classified separately from a system failure.
- Stopped records are retained and never pooled. L and M retain separate protocols and results. L's instrument stop was followed by M under a corrected protocol with its own criteria. M's first attempt stopped in preflight before injection or publication; the second proceeded under amendment M-A1 (Appendix C.2).
- Post-hoc read-only analyses are labelled as such: the I99 addendum, the M ordering analysis, the trace census and the dead-letter inspection of 9 November.

### 5.7 Statistical interpretation

The primary observation of cohort I is 98 validated successes in 98 serial investigations. It is reported as a count. Suppose, hypothetically, that each investigation were an independent, identically distributed (i.i.d.) Bernoulli trial with a constant failure probability. Zero failures in 98 trials would then give a one-sided 95% Clopper–Pearson upper confidence limit of about 3.01% (1 − 0.05^(1/98)). [R9] The serial observations on shared infrastructure do not establish that model. The interval is illustrative. It is not a field reliability estimate or a service-level objective, and it appears only here and in Section 8.

### 5.8 Data handling and cost

Measurement bundles hold counts, statuses, timings, opaque IDs, bounded reason codes and public Google API hostnames. In the live measurement collectors, principals, private service origins, authentication tokens, prompts, response text and finding contents stayed in memory. The separate dead-letter inspection of 9 November also retained raw pull responses privately (Appendix C.4). Live runs used Google Cloud credits only, in pre-sized chunks with per-chunk caps and stop rules, within a fixed overall ceiling. Card charges were not authorised. Collector cost projections stayed below their stops; exact per-chunk cost was not measured. A hash establishes that retained bytes are consistent; it does not establish that the measurement was authentic.
