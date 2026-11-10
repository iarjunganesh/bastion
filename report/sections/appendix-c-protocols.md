## Appendix C. Protocols, stop records and amendments

### C.1 Stop records

N7 and N7b denote E19's stopped batch and fresh batch, respectively.

| Run | Stop | Classification | Retained as |
|---|---|---|---|
| N7 | Run 8, false completion | System failure (E19) | Stopped; a fresh batch (N7b) followed with that case recorded |
| F pilot | Missing routing envelope across five deliveries | System failure, failed closed (E24) | Stopped; recovery recorded separately (E25) |
| F recovery X1 | Collector counted a pre-refusal plugin entry, 0.223021 s before the refusal | Instrument false positive (E25) | Original stop retained; exact-ID read-only query 393.306 s after the refusal verified the join |
| G | `collector_RetryError` at G5 | Instrument stop (E26) | 4 validated; G5 completed in the cloud |
| H | `unexpected_retry_or_failure` at H28 | System failure, failed closed (E26) | 27 validated; H28 redelivered and completed |
| I | `observation_read_unavailable_logging` at I99 | Instrument stop (E26) | 98 validated; I99 addendum separate |
| L | HTTP 400 on the first request-log read | Instrument failure; no valid injection (E29) | Stopped; restored and verified |
| M attempt 1 | `unexpected_backlog` in preflight | Protocol stop before injection (E29) | Amendment M-A1; attempt 2 ran the same pinned scripts |

### C.2 Amendments recorded before execution

- **J replay substitution.** I100 never ran, so its replay was replaced by I98. Recorded in J's protocol at 08:29:01Z; execution began at 08:29:29Z. [E27]
- **M-A1.** M's preflight read the source subscription's backlog metric. For its 09:23 and 09:24 points, the metric still showed L1's message, which had been delivered at 09:20:35Z and acknowledged at 09:21:49Z; it read 0 from 09:25. The amendment was recorded at 09:26:18Z. It notes that attempt 1 had measured, changed and published nothing, retains that attempt's record, and runs M once more under the same pinned script without changing its criteria. [E29]

### C.3 Post-hoc read-only analyses

- **I99 addendum (8 November, 08:55Z).** I's criteria were applied to I99, and all were met. It stays outside the 98. [E26]
- **Trace census (8 November).** Defined in Section 7.4. [E28]
- **M ordering analysis (8 November).** Worker audit records were grouped by invocation ID and compared with estimated caller boundaries (Section 7.5). [E29]
- **Dead-letter inspection (9 November).** See C.4.

### C.4 Dead-letter inspection, 9 November 2026

Before the review subscription was deleted, its two messages were pulled without acknowledgement. Each lease was released immediately (acknowledgement deadline 0), and nothing was acknowledged, deleted or republished. The subscription had no dead-letter policy of its own, so the pulls advanced no forwarding counter. The analysis record keeps only bounded metadata: for each message, its ID, publish time, delivery-attempt field and dead-letter attributes; the names of its other attributes and payload keys; the payload's size, SHA-256 hash, event ID and context ID; and the matching durable record's status, attempt count and update time. The inspection also retained the raw pull responses, including message payloads and attributes, in private evidence files. These raw responses are excluded from this report and its source snapshot. A second pull confirmed that both messages remained available.

| Dead-letter publish time | Source delivery count | Event | Durable record |
|---|---|---|---|
| 5 Nov 20:02:07Z | 5 | F pilot, F1 | Failed, 5 attempts |
| 8 Nov 09:30:04Z | 5 | M's investigation, M1 | Failed, 5 attempts |

This gives the exact event-ID join that E29's window attribution lacked. It is a separately dated, post-hoc read-only analysis. The sealed 8 November record is unchanged. The messages were deleted with the subscription during D4 (Appendix A.4).

### C.5 Cost admission

Every live chunk had written cost and count caps and a stop rule. It ran on credits only, within a total ceiling of 400 SEK, with unposted chunks reserved conservatively. Collector projections, for example J's final 11.57 SEK against a 20 SEK cap, are estimates, not measured costs.
