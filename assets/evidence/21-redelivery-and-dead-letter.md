# Evidence 21 — a rejected event is redelivered and dead-lettered on the production subscription

**Collected:** 4 November 2026, 20:35–20:40 UTC, evidence chunk E6 of cohort N. One synthetic
event was published to the production topic `bastion-investigations`, with explicit approval
for this single fault injection. Nothing else changed: no subscription, retry policy, IAM
binding or deployment was touched. The private bundle records statuses, timings, counts and
Pub/Sub's own dead-letter attributes; no principal, private URL or token.

## Setup

| Preflight, read just before publishing | Value |
|---|---|
| Source subscription | Eventarc push subscription to the Orchestrator trigger path |
| Ack deadline / retry backoff | 600 s / exponential, 10–600 s |
| `maxDeliveryAttempts`, dead-letter topic | 5, `bastion-investigations-dead-letter` |
| Pub/Sub service agent: publisher on the dead-letter topic, subscriber on the source | both held |
| Dead-letter review queue backlog, last hour | empty |
| Investigations in flight, last hour / trigger requests, last 15 min | 0 / 0 |

The probe was a well-formed investigation event with fresh IDs and `mock_data: true`, plus a
message attribute marking it as the E6 probe. The deployed ingress validates events before any
state write and refuses mock data, answering HTTP 400. Pub/Sub treats any status other than
102, 200, 201, 202 or 204 as a negative acknowledgement and redelivers.

## Observed

| Delivery | Orchestrator request log (UTC) | Status | Response time | Gap from previous start |
|---:|---|---:|---:|---:|
| 1 | 20:35:52.28 | 400 | 18.59 s | — |
| 2 | 20:36:24.63 | 400 | 0.002 s | 32.3 s (13.8 s after response 1) |
| 3 | 20:36:38.65 | 400 | 0.003 s | 14.0 s |
| 4 | 20:36:55.83 | 400 | 0.003 s | 17.2 s |
| 5 | 20:37:18.70 | 400 | 0.003 s | 22.9 s |

- **Dead-lettered after 5 deliveries.** The message reached the review queue and was pulled
  104.7 s after publication. It carried `CloudPubSubDeadLetterSourceDeliveryCount = 5` and
  named the production source subscription, matching the five deliveries in the request log.
- **The forwarded message was the probe.** It carried the probe marker and the `mock_data: true`
  payload; it was acknowledged, leaving the review queue empty.
- **Nothing was written.** No investigation document was created between publication and the
  end of the run, and no further delivery arrived in a two-minute quiet period after the
  forward.
- **Backoff grew.** Intervals rose from about 14 s to 23 s, consistent with the 10 s minimum
  backoff plus Pub/Sub's best-effort exponential increase and push backoff. The first response
  took 18.6 s, most likely an idle instance starting; the later rejections took 3 ms.

Pub/Sub's own metrics agree: the push-request count shows five `remote_server_4xx` responses
and the dead-letter count shows one forwarded message from the source subscription, both
between 20:37 and 20:39.

Say **on the production subscription, an event the ingress rejected was redelivered with
growing backoff, five times as configured, then forwarded to the dead-letter topic, where
review found and cleared it, and no investigation state was written.**

## What this does not show

- **Transient failure and reclaim.** The probe is a permanent rejection (HTTP 400). Recovery from
  a transient dependency failure is still evidenced by the August failed-and-reclaimable
  observation ([evidence 06](06-durable-findings.md)), not by this run.
- **A guaranteed count.** Google documents the dead-letter attempt count as approximate. Five
  was observed once; another event could be forwarded after slightly fewer or more attempts.
- **Alerting.** Nothing pages on a dead-lettered message. Review is a pull queue someone reads.

## Collection note

The first collector crashed about 20 s after publishing: an empty synchronous pull on the
review queue raises `DeadlineExceeded` instead of returning no messages. Pub/Sub redelivery does
not depend on the collector, so the run continued unobserved for about a minute. The event was
not republished. A resume script treated an empty pull as empty and, because the probe's event
ID was held only by the crashed process, checked that *no* investigation document had been
written since publication instead of looking up the probe's own. Every delivery was recovered
from the request log. The bundle keeps the original collector, the patched one, the resume
script and the crash log.
