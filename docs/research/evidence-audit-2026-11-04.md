# Claim and measurement evidence audit — 4–5 November 2026

Started 4 November; completed 5 November 2026 (Europe/Stockholm). Original collection dates
remain unchanged; this audit does not constitute a new measurement cohort.

## Assessment and scope

**Share with noted caveats.** The retained bundles pass integrity checks and their core counts
agree with the promoted records. One reported latency median needs a numerical correction.
Some current summaries retain superseded statuses or turn configuration into a stronger claim
than the observations support. The technical report remains an interim draft pending cohort F
and the corrections identified below.

Reviewed all 14 [claim-matrix](claim-matrix.md) rows and all 23 numbered evidence records,
the public October source/data bundle and its CSV exports, nine sealed private measurement
bundles, the separately sealed E3 correlation addendum, the retained October census, and all
five promoted evidence screenshots. The archived demo's eight positive entries were checked
against its narration script; the public video upload was not independently re-watched.

This was an offline retained-artifact review. No GCP request, model call, event publication,
deployment, IAM change, report build or restoration of archived private history occurred.
The dated evidence records, screenshots, captured data, collectors and ZIPs remain unchanged.

## Integrity and calculation checks

- Nine private ZIPs passed CRC checks. Their manifests matched the working copies and all
  39 declared member hashes matched both working files and ZIP members.
- The E3 two-hop correlation addendum is outside the original E3 ZIP and has its own matching
  digest. It must not be described as part of that original seal.
- The public E14 bundle passed its outer hash, all 15 internal member hashes and ZIP CRC,
  including the nested original stopped-collector ZIP. All four public-file manifest hashes
  matched; the supplied summary and CSVs were byte-identical to their ZIP copies.
- Independently recalculated E14's 20 run rows, 120 stage rows, 560 unique audit records,
  60 invocation IDs, 40 model submissions, 40 review records and 60 delivered finding instances.
  Client-confirmation median is 20.461 s; Runtime-audit median is 15.9482065 s, reported as
  15.948207 s. The retained run-7 recovery preserves the initial 27-event observation, recovery
  to 28, no republish and the logging-visibility disclosure.
- E16's three deliveries are 1+2, 0+2 and 1+2, each with 28 audit events and no gaps. The retained
  identity comparison is true; R3 publication was 120.005 s after expiry and R2 completed within
  the approval window.
- E17 has nine approval probes, two peer-origin probes and four IAM/permission controls:
  all 15 expected outcomes match, with no exception-ledger change.
- E18's control completed, injection failed, refusal covered 141 characters in one part,
  and the retained post-refusal window contains no later activity. Its two-hop join matches
  the separately protected addendum.
- E19 retains both batches: seven successful runs plus one false completion in E7, followed
  by 20 successful runs in E7b. The 28 investigation IDs are distinct. E7b has 25 matched
  deliveries for 20 runs and five replays. Input/output token totals are 35,858/31,966;
  conventional medians are 1,787.5/1,600, with input rounded to 1,788 in prose.
- E20's 52+124 decisions total 176; 13 starts times 12 decisions total 156, with 20 remaining.
  The collector assigns each decision to the latest eligible preceding start, avoiding
  double-counting overlapping 90-second windows. The refused host has a Registry entry.
- E21 has five HTTP 400 deliveries, four start-to-start gaps of 32.348, 14.019, 17.180 and
  22.874 s, delivery-count attribute 5, a matching acknowledged probe, and zero investigation
  documents in the retained observation window. The original crash and resumed collector remain.
- E22 confirms both state-loss directions and both warnings on the locked source stack.
  E23's retained census is 56 bindings/three findings; the image has 161 distributions with
  `google-adk` 2.7.1 and `a2a-sdk` 1.1.2. Its requirements hash matches `f589b25`.
- In total, 78 retained-data integrity and consistency checks passed. A separate protected-shape
  scan of 29 structured files and nine capture logs found no service-account addresses, private Cloud Run origins,
  access-token/private-key shapes or raw IAM member/binding arrays. This is a finite scan,
  not a privacy guarantee. The repository redaction gate also passed.

## Corrections and proof limits

### E19 median correction

The original E7b collector computes `p50` by selecting the lower middle order statistic.
For its 20 runs, the two middle confirmation durations are **20.422 s and 20.766 s**.
The conventional sample median is therefore **20.594 s**, or **20.6 s** to one decimal.
The original record's phrase **median 20.4 s** used the stored `p50` value as the median.

The data and original summary field remain unchanged. Current derived claims must use 20.6 s
when saying *median*, or explicitly identify 20.422 s as the collector's lower-middle `p50`.
Five slow runs range from 135.985 to 206.375 s; the original 136–206 s range rounds to whole
seconds. Two slow runs mainly waited before Runtime activity; three stalled inside model-free
stages. Three coincided with new Runtime instances, which does not establish causation.

### Completion integrity is source-complete and production-unverified

At the original audit's pre-F cutoff, the completion-confirmation fix and regression tests
existed: `Implemented` and `Tested` were Yes, while deployment, live observation and
`Safe to claim?` were No. Observing the earlier false completion did not verify its fix.
The subsequent 5 November [evidence 24](../../assets/evidence/24-upgraded-deployment-and-stopped-pilot.md)
establishes deployment and one failed-closed pilot, with positive verification still open.
The separate corrected recovery then passed the predefined positive controls and direct
refusal join ([evidence 25](../../assets/evidence/25-corrected-cohort-F-verification.md)). The
current matrix permits only that bounded functional claim; no reliability rate follows.

### Original census seal is unavailable

The available 28 October ground-truth directory contains `census.json` without an original
manifest or ZIP. Its values agree with E23, but it cannot be included in the claim that all
retained acquisition outputs have a verified original seal. Its checksum was recorded during
this audit; that does not retroactively establish an October seal or independent capture date.
The separate 4 November image-package bundle is sealed and passes verification.

### Configuration, observations and inference must stay distinct

- Pub/Sub's configured delivery-attempt count is approximate. E21 observed five deliveries
  once; it does not prove an at-most-five guarantee. The backoff policy is also best effort.
  [Google's dead-letter documentation](https://docs.cloud.google.com/pubsub/docs/dead-letter-topics),
  [retry-policy documentation](https://docs.cloud.google.com/pubsub/docs/subscription-retry-policy)
  (checked 4 November 2026).
- E07 establishes alert-policy configuration. E21 does not demonstrate delivery of a paging
  notification. These statements are compatible; "no alerting exists" is too broad.
- E20's refusal is defect D2's unmatched registered host, not discrimination between registered
  and unregistered destinations. Missing customer admin-activity entries are consistent with
  platform-side updates but do not independently prove who made an update or its cause.
- The measured `google-adk` 2.7.1 package version belongs to the Cloud Run image. The managed
  Runtime's installed resolution was not read back. The source target 2.13.0 and offline O1
  results must not become an upgraded-production claim.
- E17 contains 13 expected negative outcomes and two positive controls. One negative is a
  permission test reporting "not held", rather than an HTTP denial; avoid calling all 13
  HTTP refusals. The probes are finite, not universal caller or payload coverage.
- E01's unblocked text sample and E08's construction tests establish specific boundaries;
  they do not prove immunity to all workflow manipulation or tool poisoning. Zero raw fields
  in a schema is not a measured zero-leakage probability. Opaque IDs remain linkable.

## Record-by-record coverage

| Record | Rechecked basis | Boundary retained |
|---|---|---|
| [E01](../../assets/evidence/01-model-armor-block.md) | 15 Aug direct-template result, three cases | Historical threshold and finite samples; no live callback or general attack-immunity proof |
| [E02](../../assets/evidence/02-gemini-investigation.md) | 15 Aug local live-API run, five model calls, two findings | Pre-Gateway, three `LlmAgent`s; historical only |
| [E03](../../assets/evidence/03-escalation-agent-denied.md) | 15 Aug impersonation success followed by IAM denial; Auditor control | Workstation probe; old role inventory is dated |
| [E04](../../assets/evidence/04-private-fleet-deployment.md) | 21 APIs and 39 enumerated resources | Scoped census excludes the Workload Identity pool/provider; not a route trace |
| [E05](../../assets/evidence/05-runtime-gateway.md) | Session/stream and Gateway/IAP/Registry configuration | Earlier catalog size; no complete IAP discrimination proof |
| [E06](../../assets/evidence/06-durable-findings.md) | Completion, dependency-failure state, IAM and idempotent receiver outcomes | Failure/reclaimability observation, not a worker-timeout retry sequence |
| [E07](../../assets/evidence/07-observability.md) | Retention screenshot agrees with 365 days, region and analytics | Lock field is not pictured; no notification-delivery or historical-SLO proof |
| [E08](../../assets/evidence/08-tool-poisoning.md) | Construction surface and recorded mutation control | Offline capability restriction, not a live attack refusal |
| [E09](../../assets/evidence/09-cross-department-routing.md) | 18 Aug 52 bindings, three findings, two departments | Companion routing measurement, not a completed investigation or current census |
| [E10](../../assets/evidence/10-cross-week-suppression.md) | 19–22 Aug three-day gap, 23 Aug recheck | Original record does not show expiry; later E16 does |
| [E11](../../assets/evidence/11-current-route-correlation.md) | Count screenshot agrees with 62/3/2 and 28 unique audit events | Companion census separate from route telemetry; Logs Explorer displays 56 search results, so its image alone does not reproduce the unique-event count |
| [E12](../../assets/evidence/12-agent-mediated-model-armor-refusal.md) | Screenshot agrees with 141-character refusal and zero downstream activity | Authenticated direct Auditor request; no durable Runtime investigation |
| [E13](../../assets/evidence/13-current-route-trace.md) | Screenshot shows 22 spans and 65.401 s | One sampled trace; unopened attributes do not establish zero leakage from every attribute |
| [E14](../../assets/evidence/14-live-validation.md) | Full public bundle, manifests, CSVs, totals and recovery | One project; time-window trace join; replay effects without per-message delivery proof |
| [E15](../../assets/evidence/15-fleet-inventory.md) | JSON independently sums to 21 enabled APIs/39 resources | Counts/existence only; same enumerator scope as E04 |
| [E16](../../assets/evidence/16-exception-lifecycle.md) | Sealed three-run lifecycle and retained same-finding comparison | One real approved exception; cold-start and token-attribution limits retained |
| [E17](../../assets/evidence/17-negative-authorization.md) | Sealed 9+2+4 probes, statuses, booleans and unchanged ledger | 13 negative outcomes, two controls; not 13 HTTP denials or fuzzing |
| [E18](../../assets/evidence/18-model-armor-refusal-reprobe.md) | Sealed control/refusal window and separate addendum digest | Two-hop correlation; not the undeployed single-hop fix |
| [E19](../../assets/evidence/19-repeatability-and-false-completion.md) | Both sealed batches, per-run values, tokens and delivery counts | Median corrected above; 1 false completion in the 28-run E7/E7b population, not a reliability rate |
| [E20](../../assets/evidence/20-gateway-unmatched-egress-refusal.md) | Sealed counts, startup assignment code and registered-host check | Incidental D2 misclassification; no matched allow; update provenance remains inference |
| [E21](../../assets/evidence/21-redelivery-and-dead-letter.md) | Sealed five deliveries, forwarding, marker, acknowledgement and zero-document window | Permanent ingress rejection; approximate policy; crash/resume disclosed |
| [E22](../../assets/evidence/22-a2a-state-boundary-reproduction.md) | Sealed versions, both state-loss results and warnings | Offline localhost only; remaining ADR-012 behaviours not re-run |
| [E23](../../assets/evidence/23-deployment-census.md) | Retained census plus sealed image package/runtime-spec data | Census originally unsealed; Runtime installed packages remain unreadable |

## Resolution, 6 November 2026

The maintainer authorized the final repository/manuscript reconciliation and local PDF on
6 November. The original findings and capture bytes above remain unchanged. Current corrections:

| Finding | Resolution and retained limit |
|---|---|
| E19 median and slow-run grouping | Conventional median and two pre-Runtime/three in-stage grouping applied to the manuscript; original lower-middle p50 and collector record retained |
| E19 false completion / post-fix controls | N, failed F (E24) and corrected recovery (E25) remain separate; bounded positive controls and read-only direct refusal join recorded, with the raw collector stop/X1/drain disclosure |
| Census seal and E3 addendum | Method/Appendix A disclose the missing original census seal and the addendum outside its original ZIP; a later checksum does not restore an original seal |
| Image versus Runtime versions | Outline/method/Appendix A distinguish measured/asserted image packages from unreadable Runtime installed resolution |
| Retry and operations | Approximate delivery target distinguished from one observed five-delivery event; configured alert policies do not establish paging delivery |
| Authorization and Gateway wording | Thirteen negative outcomes plus two controls; registered-host mismatch/inferred cause and absent matched-allow evidence retained |
| Dated counts, opaque IDs and C4 | Census dates, linkability, finite probes and deferred comparison preserved; no universal security/privacy result |
| Report layout and references | Builder reads canonical sections; retired paths and placeholders removed; source snapshot distinguishes local changes from existing public commit links |
| Billing | Daily reported-usage check passed on 6 November, corroborated by the supplied CSV; amounts private, late postings and exact per-chunk/payment attribution remain bounded |

The report remains uncommitted and unpublished. Final layout/check results are in the
[handoff](../../HANDOFF.md). The [report plan](report-plan.md) governs the remaining fleet end
state and publication steps; neither is implied by a local PDF. Historical records without raw
exports were checked for consistency with retained screenshots, not independently re-measured.
