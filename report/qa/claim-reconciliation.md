# Claim-by-claim reconciliation (corrected local draft, November 2026)

Each manuscript claim was checked against the cited evidence page, the v0.9.1 source or the claim matrix. Status values:

- **OK**: matches the source.
- **Fixed**: corrected in the dated 9–10 November review passes.
- **Open**: needs the maintainer.

The 9 November final review is retained in `final-review-2026-11-09.md`. The current
[10 November closeout](final-closeout-2026-11-10.md) verifies all 16 follow-up findings,
including the reopened I7/M4 residuals, against PDF `f3b2bb95…9071`. The rows below include
the additional summary, retention, provenance and full-page visual checks. A link resolving
to a file is checked separately from whether that file supports the sentence. Earlier citation
checks retain their original dates; they were not all fetched again for the closeout.

| § | Claim | Source checked | Status |
|---|---|---|---|
| Abstract, 7.2 | I: 98 of 98 validated, instrument stop at I99; G 4 validated (instrument stop); H 27 validated, H28 429 failed closed | E26 results tables | OK |
| Abstract, 7.4 | Runtime graph spans in 5 of 142 agent traces; 0 content-bearing attributes | E28 census table | OK |
| Abstract, 10 | No Clopper–Pearson figure in abstract or conclusion | Blueprint §5; enforced by a report test | OK |
| Abstract, 1, 6.1, 9.1, 10 | D1/D9/E19 recorded false completion; D6's refusal is stated in the body; D8's terminal status is unestablished. The five failures motivate the named policy/handoff/completion controls, without claiming they originated every design control | ADR-012 D6 amendment; observation backlog D1/D6/D8/D9; E19; CHANGELOG fidelity entry | Fixed (I2 and follow-up 6; checked in PDF pp.11, 19) |
| 1 | Later instances: quoted-content wrapping (E24), model 429 (H28) | E24, E26 | Fixed ("under load" removed; the cause of the 429 is not established) |
| 3 | T1–T6 trust boundaries; Gateway egress-only, never authorises callers | Blueprint §3; E05, E17, E20 | OK |
| 4.2 | Zero-argument tool, ≤500 results, Owner/Editor, score 0.8, HMAC-SHA256 first 24 hex | `agents/access_auditor/agent.py` (`MAX_POLICY_RESULTS = 500`, `risk_score=0.8`, `[:24]`) | OK |
| 4.3 | Rationale ≤280 chars; ID set, per-finding fields and count compared; out-of-schema fields refused since v0.9.0 | Same file (`max_length=280`, `_has_unexpected_field`, `AuditorFidelityError`) | OK |
| 4.4 | Routing attributed in relayed history must name `policy_step`; Auditor-attributed routing is rejected. Bare, unattributed JSON remains accepted on the authorised request path | `agents/escalation_agent/agent.py:164–191`; E27 | Fixed (follow-up 5; exception explicit in PDF p.6, no universal routing-authorisation guarantee) |
| 4.5 | `escalation_gate` emits `escalation_confirmed: true` only if receipts match routing; dispatcher raises `RuntimeIncompleteError` without it | `agents/orchestrator/agent.py` `EscalationCompletionGate`; `infrastructure/agent_server.py` `run_managed_runtime` | OK |
| 4.7 | Retry only on 429/500/502/503/504, before the first yield, at most 4 attempts; wait ceiling 2 s doubling to 10 s, 50–100% jitter; audited | `agents/model_retry.py` | Fixed (backoff wording made exact) |
| 4.8 | 600 s ack deadline, 10–600 s retry, dead-letter about 5 attempts, approximate | E06, E21; R11 (verified: "The maximum number of delivery attempts is approximate") | OK |
| 4.8 | Span-content setting restored after template set-up | `agents/orchestrator/runtime.py` (`ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`); E28 | OK |
| 5.2 | Baseline 62 bindings, 3 findings, 2 departments; times 18:55Z, 20:09Z, 22:44Z (7 Nov), 08:27Z (8 Nov) | Blueprint §5; E26, E27 | OK |
| 5.3 | Per-run criteria table | Blueprint §5; E26 shared method | OK |
| 5.5 | Three-part provenance; seal `274d9901…`; M's original hash reconstructed `5425df…` | E26, E29 | OK |
| Abstract, 1, 5.1, 7.1, 10 | G/H used v0.9.0; I–M used v0.9.1 | E26 deployments and run ledger | Fixed (I4: summary attribution now matches the detailed ledger) |
| 5.6 | Collectors retry only bounded observation reads; no manual repetition/replacement of measured actions. Automatic Eventarc and model retries are counted system behaviour | E26 H28/I57; E29 M; blueprint instrument policy | Fixed (I8, follow-up 16) |
| 5.6 | Stopped records retained and never pooled; L/M remain separate; M's preflight stop and second attempt under M-A1 are distinguished | E29:31–57; C.1/C.2 | Fixed (follow-up 9; PDF p.9) |
| 5.8, C.4 | Live-collector retention description is scoped; the separate inspection retained raw pull responses privately, excluded from the report/source snapshot | Private A0 script:12–13,82,109–131; source-snapshot member list | Fixed (Important follow-up 1; PDF pp.9, 23; raw contents not opened) |
| 5.7 | 1 − 0.05^(1/98) ≈ 3.01% | Recomputed: 0.030106 | OK |
| 6.1 | D1 two runs 16:27:49Z and 16:34:49Z; delivered twice; fixed in 0.2.0, 22 Aug | Observation backlog D1; CHANGELOG 0.2.0 | OK |
| 6.1 | D8 upstream: issue 6854, PR 6859, commit `d2cb22e`, first upstream release `v2.12.0` | U1–U4 (rechecked in the 9 Nov review) | OK |
| 6.1 | E19: 1 attempt, 81 s, no audit/review/model; two instances started; 1 of 28 | E19; blueprint | OK |
| 6.2 | E25 direct control, J0/K1/K2 positive; F pilot and M each show dispatcher rejection ×5; H28 policy path. None shows the completion gate rejecting an invalid receipt | Claim matrix "Durable completion integrity"; E24–E29 | Fixed (follow-up optional attribution; checked in PDF p.12) |
| 6 opening, 6.1 | Observation/repair/deployment/verification and classifications asserted where established; E19 repair deployed with the 5 November upgrade | Claim-matrix header; E24; dated chronology | Fixed (follow-up 10; PDF pp.9, 11) |
| 6.2 | The completion gate's rejection path is unit-tested | `tests/unit/test_orchestrator.py` (`EscalationNotConfirmedError`) | OK |
| 6.3 | 176 denial decisions, 88 lookups, 5 Oct – 4 Nov | E20 | OK |
| 6.3, 7.5, 8 | Continued execution is confined to M's tested configuration and five estimated boundaries; no universal timeout rule | E29 cancellation method and table; claim matrix limitation row | Fixed (I1) |
| 6.3 | Mechanism wording (non-standard hostnames) | Observation backlog D2 | Fixed (marked as inferred; the August count of six hostnames is no longer stated as current) |
| 6.3, A.4 | D4 deleted 25 of 26; Gateway refusal status separated from later Runtime/authz observations, cause unestablished. Billing sentence describes D4's action on this project only | Teardown status-only error handling; dated private D4 record; HANDOFF | Fixed (follow-up 7–8; PDF pp.13, 21) |
| 7.1 | Run ledger classifications G–M | E26–E29 | OK |
| 7.2 | Medians and ranges; 112/756/2,745 audit records; 8/54/196 reviews and completions; tokens 167,064/163,604; read retries 3 HTTP and 22 Logging | E26 tables | OK |
| 7.3 | J0 5 events, 94.2 s; R1–R5 one HTTP 200 each, 120 s windows; X1 75.8 s; envelope pair | E27 | OK |
| 7.3 | I98 substitution recorded at 08:29:01Z, execution at 08:29:29Z | E27 | OK |
| 7.3 | Five completed-event replay labels explicitly identified as E27's R1–R5, distinct from bibliography keys | E27; PDF p.14 | Fixed (follow-up 14) |
| 7.4 | 172-span trace; K1 47.5 s with graph spans, K2 13.9 s without; 63 pages; 7/63/72 by day; about 149 dispatches; 13/30 and 10/30 not comparable | E28 | OK |
| 7.5 | 3 s timeout (normally 300 s); fastest I run 7.09 s; 5 deliveries, gaps 20.4/23.0/20.6/24.6 s, 503 after 5.2–7.0 s; 5 × 504 at 2.999 s; 5 failed attempts; 0 reviews; backlog 1→2; control 20.5 s | E29 | OK |
| 7.5 | Cancellation table and "six of ten / three of five" statement (verbatim from the blueprint) | E29 | OK |
| 7.5, C.4 | Dead-letter join: F1 (5 Nov 20:02:07Z) and M1 (8 Nov 09:30:04Z), source delivery count 5 each, durable failed/5; post hoc, 9 Nov | `.local/d4/a0/a0-dead-letter-inspection.json` (private) | OK (stated as a separate post-hoc analysis; E29 unchanged) |
| 7.6 | E14: 20/20, 560 records, 40 submissions, 40 reviews, median 20.461 s | E14; verified by `load_live_validation()` at build | OK |
| 7.6 | E19: 20/20, median 20.6 s (conventional, corrected), 5 runs about 136–206 s | E19; S13 correction | OK |
| 6.2, 7.6 | E25: 5 normal, direct control, 2 replays; median 20.375 s. Post-upgrade recovery belongs in §6.2, outside the pre-upgrade baseline table | E25; blueprint §7.6 | Fixed (M2: result retained in the correct population) |
| 8 | Census dates: 62 bindings at 7–8 Nov G–M preflights; 56 bindings on 28 Oct, with no new binding census for N's 3–4 Nov runs | E23; E26/E27; blueprint workload | Fixed (I3) |
| 8 | Retry/dead-letter observations also retain the F pilot and H28; no general attempt-count bound | E21, E24, E26, E29; separate post-hoc A0 join in C.4 | Fixed (I9) |
| 8 | Limitations retain the frozen blueprint's bounds, including conditional statistics, routing, telemetry, cancellation and deferred C4 | Blueprint §8; E23/E26–E29 | Fixed (summary wording checked separately from the list of headings) |
| 9.2 | Cross-framework study proposed, not performed | Blueprint §9 | OK |
| 9.1 | G5 and L1 completed in the cloud; the corresponding protocols stopped and records remain separate | E26:48; E29:31–57 | Fixed (follow-up 13; PDF p.18) |
| A.1 | Tags, commits, digests, Runtime ready times, revisions 00036–00039 | E26, VERSIONS | OK |
| A.2 | Link base `aa398f6` is later than deployed `755dd07`; differences in production directories are the dispatcher docstring and teardown | Local Git diff over production directories; PDF p.20 | Fixed (follow-up 11) |
| A.3 | 398 core cases | README/AGENTS after PR #14 | OK |
| C.2 | M-A1 content | `.local/measurements/2026-11-08-M/protocol.json` amendment (private) | Fixed (the amendment re-runs the same script; it does not change acceptance logic) |
| C.5 | 400 SEK total ceiling; J's projection 11.57 SEK against 20 SEK | Report plan D3; E27 | OK |
| B | E14 collector-only repair/read-only recovery found all 28 events; E18 addendum separately sealed; E21 crash/resume and broader document query; original October census seal unavailable | E14; E21 collection note; retained-evidence audit | Fixed (I5 and follow-up 15; PDF p.22) |
| 3, 4.1, Figure 1 | Runtime-to-worker egress passes through the Gateway; worker-origin checks remain T3; audit joins by investigation ID while traces join by window | Architecture; E28; corrected figure source; PDF p. 5 | Fixed and visually verified (I6) |
| Figures 1–3 | Minimum label size 8.425 pt at a placed width of 499.276 pt; label guard passes; manual inspection separately confirms date wrapping and line-to-label clearance | `make_figures.py`; `figure-layout.json`; current PDF pp.5, 10, 15 | Fixed and visually verified (I7, follow-up 2–3; label-only automation not treated as a complete visual check) |
| Figure 2 | D6 observed 21 Aug, fixed 22 Aug; D8's complete 22 Aug date is legible; N7/N7b defined in caption; full stop ledger remains in C.1 | Observation backlog D6; E19; corrected source/caption; current PDF p.10 | Fixed and visually verified (M1, follow-up 2/4) |
| 4.5, 5.5 | Confirmation items and the three provenance statements are separated by blank lines | Canonical sections; PDF pp. 6, 8 | Fixed and visually verified (M3) |
| Abstract, 2, 3, 4.2, 5.7, 6.3, 7.4, Figure 2, C.1 | IAM/IAP/HMAC/LLM/GDPR/i.i.d. expanded; service-level objective written in full; census F1 labelled as recovery; N7/N7b defined at first use in the Figure 2 caption | Canonical sections; E24/E28; E19; current PDF pp.3, 9, 10 | Fixed (M4, follow-up 4 and optional first-use expansions) |
| Figure 3 | Six model completions and three IAM calls after estimated boundaries in total; post-boundary IAM calls only in attempts 1–3 | E29 cancellation table; corrected caption | Fixed (M5) |
| Abstract | Targeted control states rejection of a forged routing envelope | E27; current PDF p.1 | Fixed (follow-up 12) |

## Citation verification

| Ref | Result |
|---|---|
| R1–R5 | Rechecked against the cited arXiv versions, EUR-Lex Article 5(1)(c), and official role-recommendation documentation in the 9 November review |
| U1–U4 | Rechecked live in the 9 November review: issue closed as completed; PR 6859 closed after import, including the author's two commits; PR 6862 closed unmerged; `d2cb22e` imported 12 Oct and included in v2.12.0 on 13 Oct |
| R6 | Verified via Crossref: title, authors, *ACM TOCS* 2(4):277–288, 1984 |
| R7 | Verified 9 Nov: ACM's deposited [Crossref record](https://api.crossref.org/works/10.1145/3102980.3103005) names Peng Huang as first author; the [published paper](https://web.eecs.umich.edu/~ryanph/paper/grayfailure-hotos17.pdf), p. 1 author list and ACM Reference format, agrees. Retain Peng Huang. The earlier author-name question is resolved |
| R8 | Verified on usenix.org: title, all eight authors in order, OSDI 2014, pp. 249–265 |
| R9 | Rechecked through Crossref in the 9 November review: Clopper/Pearson, Biometrika 26(4):404–413, 1934; publisher endpoint failed, so no new full-text verification is claimed |
| R10 | Official specification supports the independently deployed agents, messages and tasks description; mutable latest-version metadata is not used as deployment provenance |
| R11 | Official page title is Dead-letter topics; the maximum number of delivery attempts is approximate and forwarding is best effort |
| S, E link integrity | References resolve to existing files at base `aa398f6`; source snapshot hashes are checked separately from sentence-level support. Final build receipt records overlays and snapshot verification |

## Final local build verification — 10 November

All 16 follow-up findings are closed in `final-closeout-2026-11-10.md`, including the original
I7/M4 residuals. This supersedes the earlier all-14 closure summary, retained in the dated
historical review and preserved draft archive. The current PDF has 25 pages and 62 clickable
HTTPS links. All 25 full-page renders were visually inspected and matched to the PDF; automated
layout findings are empty. Figures/captions, table continuations and numbered lists agree.

The frozen outline, C.1/C.2 records and C.4 table remain unchanged. The statistical illustration
remains confined to §§5.7 and 8. Canonical assembly matches after CRLF/LF normalisation. All 70
source/snapshot hashes and ZIP CRC pass, with no public-source overlay. Finite pattern checks
of canonical sections, manuscript, PDF text, metadata and links found no prohibited patterns;
the privacy receipt states the scope and limits. The affiliation is exactly
“Independent researcher, Stockholm”.

PDF SHA-256: `f3b2bb95f5ae52b9e9d964519f92dd367fceeb58342e0570d07274692e5f9071`.
Source-manifest SHA-256: `923952eb7c1f6f9f4081405642d20b4714add7c3678c68b0f5fcf354fee7bd3f`.
Detailed results are in `checks.json`, `figure-layout.json` and `final-fix-integrity.json`.

## Release build — 10 November

The release build for `report-2026-11` supersedes the hashes above. It changes only the running
header and the Appendix A.2 release sentence and provenance line; every claim row above is
unchanged and was not re-adjudicated. Page-by-page text, link and figure comparisons against
the verified build are recorded in `release-build-2026-11-10.md`.

PDF SHA-256: `81c2dfce5886426bde5ee81f5db461d2c83dc79a37b3c949c066f94c6220c706`.
Source-manifest SHA-256: `0e399dc83af237e7df127dd5ec8dd2b95017d40810daf8136ab1d2863c46a342`.
Receipts: `checks.json`, `figure-layout.json` and `release-integrity.json`.

## Final build — 10 November

The final build adds the ORCID iD, reserved DOI and licence line on p.1 and the DOI and licence
scope in Appendix A.2; the snapshot carries both licence notices. No claim row changed.

PDF SHA-256: `ec710124910bba89dcb4fd3bbd769f714347074f3989869c00b74f31a013dcb3`.
Source-manifest SHA-256: `b8606936efff176be3b89f2de77fa6fec59095530ff235ad66c5fb6aebbf891a`.
