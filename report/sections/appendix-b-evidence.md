## Appendix B. Evidence index

Evidence identifiers keep the repository's numbering, and dates are collection dates. Each public record states its own proof boundary. Original captures are never rewritten; corrections are recorded separately. [S13]

| ID | Date | Content | Boundary |
|---|---|---|---|
| E03 | 15 Aug | Escalation identity denied an IAM read; Auditor control | Workstation impersonation probe |
| E05 | 16 Aug | Runtime bound to the Gateway; fail-closed IAP policy | Configuration |
| E06 | 16 Aug | Durable lifecycle, idempotency, failure reclaim, dead-letter configuration | Configuration and single observations |
| E07 | 16/25 Aug | Audit sink, 365-day retention, metrics and alerts | Retention configured, not locked |
| E09 | 18 Aug | 52 bindings, 3 findings routed to 2 departments | Routing measurement, not a completed investigation |
| E10 | 19–23 Aug | Exception remembered across a three-day gap; D8 fix verified | Not expiry |
| E11 | 25 Aug | Route correlation; 62 bindings, 3 findings, 0 raw finding-schema fields | One run |
| E12 | 25 Aug | Agent-mediated Model Armor refusal | Direct Auditor request |
| E13 | 25 Aug | Connected 22-span trace | One sampled trace |
| E14 | 27 Oct | 20-run live validation | Collector recovery disclosed |
| E15 | 28 Oct | Count-only inventory: 21 APIs, 39 resources, 0 Scheduler jobs | Existence and counts |
| E16 | 3 Nov | Exception approval, suppression and expiry | One lifecycle |
| E17 | 3 Nov | 13 negative outcomes and 2 positive controls | Single probes |
| E18 | 3 Nov | Screening refusal re-probe with benign control | Two-hop ID join |
| E19 | 3 Nov | False completion; 20/20 fresh batch | One batch |
| E20 | 4 Nov | 176 Gateway/IAP denial decisions | Incidental; defect D2 |
| E21 | 4 Nov | Redelivery and dead letter of one rejected event | One permanent rejection |
| E22 | 4 Nov | A2A state boundary re-run on `google-adk` 2.13.0 | Offline |
| E23 | 28 Oct / 4 Nov | Census (56 bindings) and image packages | Runtime packages unreadable |
| E24 | 5 Nov | Upgraded deployment; stopped F pilot | Failed closed; time-window join |
| E25 | 5 Nov | Corrected F recovery | Refusal join verified read-only |
| E26 | 7–8 Nov | Cohorts G, H and I; I99 addendum | Stopped cohorts retained; not pooled |
| E27 | 8 Nov | Targeted controls J | Bounded replays; provenance test |
| E28 | 8 Nov | Trace isolation K and census | Post hoc; sampling unknown |
| E29 | 8 Nov | Timeout fault injection L and M | Estimated boundaries; reconstructed hash |

Private acquisition records, collectors and seals are retained outside Git. The 9 November seal covers 8 sets and 73 files (G, H, I, the I99 addendum, J, K, L and M), with manifest SHA-256 `274d9901e84a9d45154c8bdc072e2ed00d3117e5a42a93a16ab3c81bb2d80e85`. The 27 October bundle is public, with its hashes.

Earlier records have distinct acquisition limits. E14 paused after seven investigations when one audit entry was absent from the query result; a collector-only repair and a read-only recovery then found all 28 events without republishing a successful investigation. E18's two-hop correlation addendum is outside the original acquisition ZIP and has its own digest. E21's collector crashed after publication; its resumed observer recovered the delivery logs without republishing and checked for any investigation document since publication rather than querying the probe's event ID. The 28 October census has no original manifest or ZIP; its later checksum does not establish an October seal or an independent capture date. [S13]
