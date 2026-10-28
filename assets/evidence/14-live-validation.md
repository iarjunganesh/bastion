# Evidence 14 - bounded live validation, 27 October 2026

**Observed:** 2026-10-27, 21:56:32.597197-22:33:49.371032 UTC

**Record prepared:** 2026-10-28

**Scope:** 20 serial real-IAM investigations on one project, followed by five
completed-event replay publications. No deployed code, IAM, configuration or
human exception was changed for the study.

This post-hackathon report supplement is separate from the August captures and
the submitted demo. It does not replace evidence 11's dated 62-binding census.

## Results

| Measurement | Observed value | Boundary |
|---|---|---|
| Distinct investigations and contexts | 20; all completed in one durable attempt | Repeated executions on one project, not 20 independent policies |
| Retained structured audit records | 560 across 60 invocation IDs | Metadata-only export; no prompts, responses, raw IAM or private origins |
| Model submissions recorded | 40 to Gemini 3.5 Flash | Audit milestones, not token usage or attributed monetary cost |
| Human-review records | 40; two per investigation | Real records retained in Firestore; none deleted or reset |
| Delivered findings | Three per run: `platform-infra` 1, `security-engineering` 2 | 60 finding instances, not a count of distinct risks or a new pre-policy census |
| Client completion confirmation | Median 20.461s; minimum 20.219s; maximum 116.266s | Publish start to first completed-state poll; 5s polling interval |
| Runtime audit duration | Median 15.948207s; minimum 13.238595s; maximum 101.587660s | Paired Orchestrator audit timestamps; not the client interval or pure model time |
| Completed-event replays | Five Pub/Sub publication acknowledgements | Unchanged durable state, review counts and invocation sets observed for 120s; per-message Eventarc delivery not independently confirmed |
| Pilot trace | One connected 22-span tree, all five steps in order | Unique workflow-name/start/end match within 1s of pilot audit; not an embedded investigation-ID join |

All 560 audit records were re-read after collection. Every investigation's worker
records matched the expected immutable revisions: 200 Auditor records and 80
Escalation records. All 280 Runtime audit records matched the dispatcher's actual
target. The four ready Cloud Run revisions and managed Runtime update time
(2026-08-23) were unchanged before and after the study. Runtime metadata declares
Python 3.12; installed package resolution was not freshly enumerated.

## Collector pause and evidence recovery

After seven acknowledged investigations, all seven durable executions had completed.
The collector nevertheless stopped: its query returned 27 rather than 28 run-7 audit
events, and its readiness predicate checked step completions without requiring every
start needed for duration calculation. The missing entry was `escalation_gate`'s start.

The entry's receive timestamp preceded the stopped checkpoint; this establishes a
query-visibility/readiness issue, not a demonstrated logging outage or late ingestion.
An approved collector-only repair required paired start/completion milestones.
Read-only recovery found all 28 events and the unchanged review records. No successful
investigation was rerun, excluded or assigned a new identity.

The original source, seven-run checkpoint and initial 27-event observation are
preserved alongside the recovery and both collector versions. The remaining 13
investigations and five replays retained the original 20/5 publication caps,
first-publication time and 60-minute window. Fourteen offline collector/evidence
guard tests and scoped Ruff checks passed.

## Reusable data

- [Data and verification guide](live-validation-2026-10-27/README.md)
- [Verified source/data bundle](live-validation-2026-10-27/bastion-live-validation-2026-10-27.zip)
- [Summary and methodology](live-validation-2026-10-27/summary.json)
- [Run-level CSV](live-validation-2026-10-27/runs.csv)
- [Stage-level CSV](live-validation-2026-10-27/stages.csv)
- [Public-file SHA-256 manifest](live-validation-2026-10-27/sha256.json)

The bundle is byte-identical to the verified local capture:
`3f9acf4c82f390cd25091ec684c8a195af36388592363916742a6607e4a7d80c`.
Its internal 15 member hashes and ZIP CRC, the 20 run rows, 120 stage rows and
original source/checkpoint lineage were verified. Protected-shape scans passed.
Span attributes were not requested; unknown span names were coarsened before export.

## Proof boundary

- This supports bounded repeatability, correlated lifecycle and successful deterministic
  gates/delivery on the existing real-IAM path during the recorded window.
- Human-exception elapsed-gap/expiry behavior, Escalation's IAM-read denial and an
  agent-mediated injection refusal were not re-probed. Their August captures remain
  dated evidence; successful October executions do not constitute fresh negative tests.
- It is not detector accuracy, explanation usefulness, a leakage rate, a privacy/utility
  comparison, historical SLO attainment or continuous operation between August and October.
- No new binding count or canonical pre-policy finding census was exported. Do not infer
  today's exception state or expiry behavior from the changed delivered count.
- Replay publication acknowledgement is not per-message delivery proof. The two open
  captures - managed Gateway refusal and watched retry/fifth-attempt dead-letter behavior -
  remain open.
- The trace is one time-matched sample, separate from the 560 audit records. It does not
  establish that all 20 traces were sampled or joined by investigation ID.
- Actual currency cost is not attributable from these payload-free records. The recorded
  authorization ceiling is not measured spend or an independently enforced billing cap.
- C4 remains deferred and synthetic-only. The study did not upgrade the fleet, rerun the
  historical localhost reproduction, create exceptions or modify IAM.
