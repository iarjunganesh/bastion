# Evidence 25 — corrected cohort F functional verification

**Collected:** 5 November 2026, from 2026-11-05T21:30:02 UTC.
Separate recovery after the stopped pilot in [evidence 24](24-upgraded-deployment-and-stopped-pilot.md).
The original failed event and every automatic attempt remain retained; they are not replaced
or pooled with this recovery or with cohort N.

## Deployed source and preserved configuration

The clean 52-file export is the same pinned base `d7d6a99a5f1534f835235e21f95a0413f5027ecc`
and SDK-access correction used by evidence 24, plus the reviewed exact quoted-routing parser
correction. The source delta is confined to `agents/escalation_agent/agent.py`: recognize a
complete SDK quoted-content block after attribution, then apply full JSON parsing and the
existing deterministic routing validation. No model, IAM or notification authority was added.

- Source-manifest SHA-256: `06d203f1a0b6ad88921ee303b41c24469aeb301bdb7265819effc21296aeb734`.
- Routing-patch SHA-256: `3e8b76ab2f5e69e04206ca0d1c1cd54da2c46c5e67ed66dc84e87a2c68661759`.
- One successful image build; digest `sha256:ca432bf101c610c49a60d4effc2eff582612e9de884a7360f716d963b714f3fe`.
- The in-build container asserted `google-adk` 2.13.0, `a2a-sdk` 1.3.0 and SDK 2.6.0.
  Each of the four existing Cloud Run services was verified ready on that digest, with
  unchanged protected container/security settings and service IAM policy.
- **No Runtime update.** Its graph/source is unchanged from evidence 24, both remote-worker
  card settings are present, and complete in-memory resource equality was checked across
  the image rollout. Postflight verified its prior update metadata. Runtime installed
  packages remain independently unreadable; these observations are not a package inventory.

No new service/Runtime, IAM grant, product enablement, billing change or storage deletion.

## Predefined controls and results

A fresh count-only real-IAM baseline used a throwaway finding-ID key and expected three
findings across two departments, with no active exception. Raw IAM and the production HMAC
key were not retained or used as study fixtures. The existing review-queue message remained
untouched. Cases ran serially, pilot first, without manual retry or substitute event.

| Control | Observation |
|---|---|
| Normal production investigations | 5/5 passed, one durable attempt each; expected review counts and correlated audit |
| Separate direct Runtime control | One passed, trusted completion confirmation observed in the returned stream; outside the five-case population |
| Completed-event replays | Two passed; one HTTP 200 delivery each, with unchanged durable state, reviews and invocation/model population during the recorded 120-second effect windows |
| Direct Auditor refusal join | One approved injection request produced an Armor refusal with that request's investigation ID; independently verified read-only after the collector's temporal-filter false positive, disclosed below |
| Pub/Sub publications / observed Eventarc deliveries | 7 / 7, all HTTP 200; isolated publication-window joins, not embedded message-ID joins |
| Completed model audit records | 12, two per normal/direct case |
| Correlated audit records, normal plus direct control | 168 |
| Human-review records | 10 normal, plus 2 from the separate direct control |

Client-observed normal completion times were **66.172, 20.844, 20.375, 20.375, 15.313 seconds**; median
**20.375 seconds**. These include client polling
and collection overhead; five functional cases are not a latency benchmark or reliability rate.
Delivery-log observations are matched by isolated time windows and exact counts; publishing
acknowledgements alone are not treated as delivery evidence.

The normal dispatcher accepted completion only after the Runtime confirmation, and the
independent direct control observed that confirmation on the wire. This closes the bounded
positive verification planned as B3. Evidence 24 retains the natural failed-closed case;
no live forced-empty-stream experiment was performed. The direct investigation-ID refusal
join closes B4's narrower correlation observation without relabelling evidence 18's two-hop join.

## Cost, closeout and collection disclosures

- **Collector stopped at X1 validation.** Its original `stopped_no_rerun` /
  `work_after_refusal`, X1 `not_completed`, and unresolved drain record are retained. It checked
  all earlier model/tool audit entries rather than only entries after refusal. The one
  `model.request` / `submitted` entry was the plugin's pre-callback entry, **0.223021 s before**
  refusal, as already documented for the earlier deployment in evidence 18.
- An independent read-only exact-ID query obtained **393.306 s after refusal**
  found zero model completions, zero tool records and no model/tool event at or after refusal.
  The observer filters the exact investigation ID and asserts equality for every returned row,
  so this establishes B4's direct join. It is not continuous monitoring or direct measurement
  of production provider-request count. Seven synthetic regressions passed, including actual
  installed SDK callback ordering with no fake-model transport call. Independent review found
  no Important/Critical gap in this addendum. **No paid probe was rerun.**
- Once all normal/direct cases were terminal and independent postflight/queue checks passed,
  only the verified owned local read-only collector process was stopped. Its original results
  remain unchanged; the separate addendum and outcome record explain the closure.
- The maintainer approved the separate 20 SEK credits-only chunk, then confirmed same-day
  execution under D3's daily billing cadence. Both full chunk ceilings and shared/unposted
  reserves were retained; the previously imposed per-chunk overnight wait was corrected.
  No credit-card charges were authorized. Actual combined gross cost, promotional offsets
  and net remain pending the **6 November billing check**; budget alerts are not hard caps.
- Project-wide isolated-window token metrics recorded input **10,341** and
  output **10,074**. This is not exact request-ID attribution and does not
  establish attributed currency cost or unchanged provider pricing.
- Postflight configuration/baseline checks passed. The latest recorded source backlog was
  zero and review backlog one; the earlier message was never pulled or acknowledged.
  Queue metrics are aggregate samples, not an individual payload/ID inspection.
- The separate direct control generated real review records; those are disclosed separately
  and excluded from the five normal investigations. No exception or transport policy changed.
- The 35-member private bundle and CRC-checked ZIP have verified hashes.
  ZIP SHA-256: `02568ec62289adb8a3cc92780f744f725104b3b5b41622502e9ea00ca36a24ff`.
  A finite structured-file protected-shape scan passed; no universal privacy guarantee follows.
- Source/version pins and fresh observations describe this recovery only. The stopped F
  pilot, cohort N, August records and the fixed hackathon demo keep their original dates.
  Finite controls do not establish an SLO, indefinite exactly-once delivery, forced worker
  timeout behaviour or general reliability rate. No manuscript build or publication occurred.

## Billing addendum, 6 November 2026

The daily reported-usage check passed: the current-month Project report and daily SKU rows show
full offsets and zero displayed net cost, with current promotional balances/expiry refreshed.
The supplied CSV corroborates the daily rows and has no positive unrounded subtotal. Private
amounts and retained exports are outside Git. This does not establish an exact per-chunk cost,
final card transactions or absence of later postings; it does not alter the sealed measurement.
