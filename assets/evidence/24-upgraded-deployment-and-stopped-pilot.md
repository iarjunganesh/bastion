# Evidence 24 — upgraded deployment and stopped cohort F pilot

**Collected:** 5 November 2026, 19:50–20:14 UTC. Cohort N was frozen before this separate
post-upgrade cohort. The maintainer authorized the reviewed 20 SEK credits-only chunk on the
run-now request; this record does not authorize another chunk or claim final billing.

## Deployment established

One clean allowlisted export of `d7d6a99a5f1534f835235e21f95a0413f5027ecc`, plus the explicit
SDK client-access correction (`Client.agent_engines` to `Client.runtimes`), produced one image.
The candidate contained 52 files; report/private material and the uncommitted audit corrections
were excluded. The overlay SHA-256 is
`f383fca2aa08308f18404db031621998c4f3dd836be351cdb244a1e293c805ca` and source-manifest SHA-256 is
`1c10ce397d7b19d68d3ecc9eb069e9676c140f70c94bb2419c78bf89fbd56300`.

| Observation | Result |
|---|---|
| Explicit Cloud Build | One, successful; 19:50:55–19:53:22 UTC |
| Image digest | `sha256:34e00c30f2f394c613f88a3f6b283eff3d8ee6d6d555a222c431571ec125c8c0` |
| Image package check | A container run inside the same build asserted `google-adk` 2.13.0, `a2a-sdk` 1.3.0 and `google-cloud-agentplatform` 2.6.0; the step passed |
| Cloud Run | Four existing services updated to that digest; ready revisions, preserved container/security configuration and unchanged service IAM policies verified |
| Managed Runtime | One update of the existing engine; new update metadata at 19:58:03 UTC; identity, environment, versioned secret references, scaling and Gateway configuration preserved |
| Runtime declaration | Python 3.12, `agents.orchestrator.runtime:app`, `requirements-runtime.txt` with the source lock constraints |
| Fleet configuration verifier | Passed after both surfaces updated |

The Runtime's installed dependency resolution remains unreadable. Its successful source-update
operation and declared requirements do not constitute an independently measured package list.
No operator IAM grant, product enablement, new service/Runtime or storage deletion occurred.

## Pilot failed; the cohort stopped

A fresh count-only baseline expected three findings across two departments, with no active
exception. One real-IAM pilot event was published at 19:59:11 UTC. Its first durable attempt
failed, so the collector stopped new work. Pub/Sub automatically redelivered that same event;
there was no manual retry, substitute pilot or second publication.

| Retained observation | Count / status |
|---|---|
| Independent investigations / publications | 1 / 1 |
| Eventarc deliveries / durable attempts | 5 / 5, all HTTP 503 |
| Correlated audit records | 125 across the automatic attempts |
| Completed model audit records | 10; two per attempt |
| Escalation envelope rejections | 5, repository reason `missing_routing_envelope` |
| Ingress dispatch failures | 5, `RuntimeIncompleteError` |
| Human-review records for the pilot | 0 |
| Successful production cases | 0 |
| Separate wire control / completed-event replays / refusal-join probe | Not executed |

The policy step and gate ran, but Escalation could not parse its routing envelope. The completion
confirmation was absent and the ingress kept the durable investigation **failed**. This is a
live fail-closed observation of an unconfirmed stream, not a forced empty-stream experiment or
the planned positive completion-integrity closure.

## Diagnosis and transport closeout

The installed ADK 2.13 serializer attributes another agent's JSON and wraps it with quoted-content
markers. An offline synthetic reproduction using that actual SDK serializer returns no routing
envelope with the deployed parser, matching the observed rejection. A prepared correction accepts
one exact, complete quoted JSON block after the existing attribution prefix, then applies the
same deterministic envelope validation. No live routing payload, prompt, response or finding
was captured to diagnose this. The correction was not deployed by this cohort.

Read-only follow-up observed the source backlog at zero and the review backlog at one in two
fresh metric observations. The retained message was neither pulled nor acknowledged. This is
an isolated-publication, time-window attribution of the queue transition, not a per-message
dead-letter payload/ID join. Five deliveries were observed once; the configured attempt count
remains approximate.

## Collection disclosures and proof boundary

- Initial read-only preparation stopped on the SDK adding an implicit telemetry default. The
  reviewed request correction removed only that generated addition; exact existing environment
  and secret-reference equality was required before mutation.
- The collector stopped new work on the first failed attempt and retained subsequent attempts
  through read-only observation. Root completion audit events were absent after the exception,
  so its conservative drain predicate remained unresolved. Separate queue observations then
  established transport quiescence; only the verified local read-only collector process was
  stopped. Its original results/checkpoints are retained unchanged.
- Project-wide token metrics in the isolated deployment/cohort window recorded 8,755 input
  and 8,305 output tokens. This is not an exact request-ID attribution. Gross currency and
  post-credit net cost await the 6 November billing check.
- The stopped bundle has 25 verified member hashes and a CRC-checked ZIP. Its SHA-256 is
  `c271a4b986722d60bf9cdb14244647eaa99be1f6b9460896c48e7cf69d844760`.
  A finite structured-file protected-shape scan passed; this is not a privacy guarantee.

**Do not close B3 or B4.** Deployment is established and the unconfirmed investigation failed
closed, but none of the five planned positive cases passed. The separate true-wire confirmation,
replay and direct refusal-correlation controls were not run. Keep this failed cohort separate
from any approved recovery cohort and from cohort N; no reliability rate is established.
