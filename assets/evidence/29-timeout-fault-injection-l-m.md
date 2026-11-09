# Evidence 29 — worker timeout fault injection: runs L and M

**Collected:** 8 November 2026 on the v0.9.1 fleet ([evidence 26](26-cohorts-g-h-i.md)).

These runs observe **capture 7**, open since August: a worker times out, the investigation is
retried, and it escalates to human review. [Evidence 21](21-redelivery-and-dead-letter.md)
covered a permanent ingress rejection, not a worker timeout. The maintainer authorized a
temporary, reversible change to production configuration.

## Design (pre-specified)

| Element | Detail |
|---|---|
| Fault | The Access Auditor's Cloud Run request timeout cut from 300 s to 3 s, on a new revision of the same image. Cohort I's fastest Auditor run took 7.09 s |
| Isolation | Everything else verified identical by protected-configuration projection before publishing |
| Investigation | One, watched until it had at least 5 deliveries, a failed durable record and 240 s with no new delivery |
| Restore | 300 s restored in a `finally` block; protected configuration, image and IAM verified equal to the original |
| Control | One normal investigation must then pass cohort I's criteria |

Eight criteria for the injected investigation, all of which must hold:

1. It never completed.
2. Every delivery returned non-2xx.
3. Durable attempts equal deliveries.
4. There were at least 5 deliveries.
5. Auditor 504s were observed.
6. No review record was created.
7. One audited dispatch failure per delivery.
8. The dead-letter review backlog went from 1 to 2, with the message left untouched.

## Run L: instrument stop, observed nothing

- 09:20:34Z: the fault was ready (revision 00036) and L1 was published.
- The first request-log read used an invalid Cloud Logging field mask and failed with HTTP 400.
  This was reproduced read-only afterwards.
- The `finally` block restored 300 s at 09:20:59Z (revision 00037), verified equal to the
  original.
- L1's Auditor call reached the *restored* revision at 09:21:17Z (200, 12.7 s). L1 completed
  normally, in one attempt with 2 reviews.
- The fault never reached L1, so **no valid injection occurred.** L is retained as stopped and is
  not rerun.

## Run M: corrected repeat

**Changes from L:**

- a valid field mask;
- every read exercised read-only on L1 before injecting;
- the preflight accepts L's restored Auditor revision.

**Attempt 1** stopped in preflight at 09:25:19Z with `unexpected_backlog`, **before any injection
or publication**:

- The source subscription's backlog metric still showed L1's in-flight message for its 09:23 and
  09:24 points. It read 0 from 09:25.
- Amendment M-A1 was recorded at 09:26:18Z. Attempt 2 then ran the same pinned scripts.
- These preflight attempts are protocol execution attempts, not durable attempts.

**Attempt 2: all 8 criteria met (M-Safety).**

| Measure | Result |
|---|---|
| Fault ready | 09:27:57Z, revision 00038 |
| Eventarc deliveries to the dispatcher | 5, start-to-start 20.4, 23.0, 20.6 and 24.6 s; each **503** after 5.2–7.0 s |
| Auditor A2A POSTs | 5 × **504** at 2.999 s |
| Durable record (exact, by event ID) | 5 attempts, final status **failed** |
| Audited dispatch failures | 5 × `runtime.dispatch/failed` (`RuntimeIncompleteError`) |
| Review records / Escalation execution | **0** / none |
| Dead-letter review backlog | 1 → **2**, untouched |
| Restore | 300 s, revision 00039, ready 09:34:15Z; protected configuration, image and IAM equal to the original |
| Normal control (09:34Z) | One attempt, gap-free audit, baseline counts, 2 model completions, one 2xx delivery; 20.5 s; no retries |

Dead-letter attribution is not a message-ID join. It rests on the backlog rising within the
isolated window: the message was never pulled. The controls that operated were fail-closed
handling, redelivery and dead-lettering.

What M shows about attribution:

- The dispatcher rejected a missing completion confirmation (`RuntimeIncompleteError`).
- It is **not** evidence that `EscalationCompletionGate` ran and rejected an invalid receipt.
  Escalation never executed.

## Continued worker execution (M-Cancellation, post hoc, read-only)

Method:

- The Auditor's own audit records were grouped by worker invocation ID.
- Each group was matched to its 504.
- The caller-visible timeout boundary was **estimated** as the request-received time + 3.0 s.
  That is not necessarily the instant the caller received its 504.

| Attempt | Worker run start vs boundary | Model completions after boundary | IAM tool calls after boundary | Worker run completed after boundary |
|---|---|---|---|---|
| 1 | +0.14 s | 2 of 2 | 1 of 1 | 31.1 s |
| 2 | −2.28 s | 1 of 2 | 1 of 1 | 18.4 s |
| 3 | −2.37 s | 1 of 2 | 1 of 1 | 10.5 s |
| 4 | −2.34 s | 1 of 2 | 0 of 1 | 8.1 s |
| 5 | −2.35 s | 1 of 2 | 0 of 1 | 12.6 s |

> In one controlled timeout-injection investigation, worker-side execution continued beyond
> five estimated three-second caller timeout boundaries. Six of ten model completions and three
> of five IAM tool calls were recorded after those boundaries. The investigation failed closed
> with no review records and was dead-lettered. These observations establish incomplete
> cancellation propagation in the tested configuration, not a universal timeout rule.

`policy_step` started five times and never completed, and nothing reached Escalation. This is a
resource-efficiency and cancellation-propagation observation. It is not a demonstrated
denial-of-wallet vulnerability, and no cost is attributed to it.

## Provenance and disclosures

- **What was fixed before the run.** M's criteria were written into its local protocol and its
  pinned execution script before execution, and the script checked its hash against the
  protocol at start-up.
- **What cannot be shown.** M's *original* protocol hash was not recorded at the time. It was
  reconstructed afterwards by removing the amendment record (`5425df627c19f1eb…`). No external
  timestamp fixes when the protocol was written. The result is therefore reported as meeting
  the documented protocol criteria, not as cryptographically verified pre-registration.
- **Fleet after M:**
  - the Auditor serves revision 00039, with I's image and verified configuration;
  - the other services are unchanged;
  - the dead-letter review queue holds 2 untouched messages.
- **Cost.** Credits only, within a 20 SEK cap; not measured.
- **Seal:** L set `7aa93746eb4d07af…` and M set `2a4eacd0d6ed4077…` (including
  `ordering-addendum.json` and the attempt-1 record). Both are in the 9 November manifest
  `274d9901e84a9d45154c8bdc072e2ed00d3117e5a42a93a16ab3c81bb2d80e85`, which establishes integrity
  from that date only.
