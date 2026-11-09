# Evidence 28 — Runtime trace export: isolation run K and a read-only census

**Collected:** 8 November 2026 on the v0.9.1 fleet ([evidence 26](26-cohorts-g-h-i.md)). The
observations are read-only, plus two direct investigations (K1, K2). Only span names, counts,
attribute-key names and booleans were persisted; no attribute values were kept.

## Why

Two items were open:

- [Evidence 13](13-current-route-trace.md)'s 7 November follow-up recorded that Runtime span
  attributes had never been opened, so "no content on Runtime spans" was a configuration
  inference.
- The v0.9.0 source fix restores `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false` after the managed
  template's set-up. It had not been verified as deployed.

## J0's trace

[Evidence 27](27-targeted-controls-j.md)'s direct control produced **one connected trace of 172
spans**. It contained the Runtime graph (`invoke_workflow orchestrator`, `policy_step`,
`policy_gate`, `escalation_gate`), both worker workflows, two `generate_content` spans and one
`execute_tool` span. **Zero content-bearing attributes** were present: only metadata such as
token counts, model names and IDs.

## Isolation run K (08:56–08:58Z)

Two direct investigations ran back to back with J0's procedure. Both confirmed, had 2 model
completions, a gap-free audit trail and counts equal to the baseline.

| | Stream | Runtime graph spans in its window |
|---|---|---|
| K1 (about 25 minutes after J0) | 47.5 s | yes |
| K2 (immediately after K1) | 13.9 s | no |

Worker, model and tool spans were exported for both.

## Census (post hoc, read-only)

- **Unit:** one Cloud Trace trace ID that contains any `invoke_workflow` span, starting between
  2026-11-05T00:00Z and 2026-11-08T10:00Z.
- **Collection:** the Cloud Trace v1 list API, fully paginated (63 pages, no page left).

| Measure | Value |
|---|---|
| Traces in the population | 142 (7 on 5 Nov, 63 on 7 Nov, 72 on 8 Nov) |
| Traces carrying Runtime graph spans | 5, starting 5 Nov 21:34:50, 7 Nov 20:15:21, 8 Nov 08:31:40, 08:57:01, 09:21:16 UTC |
| Cases those match by time window | F1, H1, J0, K1, L1 |
| Content-bearing attributes (request/response/tool payload keys) | 0 keys present; 0 non-empty values |

Limits:

- Traces are **not** joined one-to-one to investigations: about 149 dispatches fall in the
  window, against 142 traces.
- Cloud Trace sampling is unknown.
- Pre-upgrade comparison: in one sample of 30 traces per period (the first page of a
  `span:invoke_agent` listing), **13 of 30** traces on 27 October and **10 of 30** on 3–4 November
  contained Runtime graph spans (`invoke_workflow orchestrator`). Worker spans were separate
  traces then, so one investigation produced up to three traces. These sample denominators are
  therefore not comparable with the census's 5 of 142, which counts traces of a different shape.

## Findings, bounded

- **Observed incomplete Runtime graph-span export** on the upgraded fleet. Each of the five
  traces carrying the graph belonged to the first investigation after a pause. The converse (that
  every post-pause investigation exports them) was not tested. The root cause, inside the
  managed Runtime, is unresolved. Runtime warnings during I showed only the known start-up
  project-lookup refusal ([evidence 20](20-gateway-unmatched-egress-refusal.md)). No platform rule
  is claimed.
- **Span content.** No content-bearing attribute appeared in any inspected trace, including the
  Runtime graph on v0.9.0 (H1) and v0.9.1 (J0, K1). This bounds what was inspected. It is not a
  guarantee that telemetry can never carry protected content.
- Evidence 13's connected-trace observation is reproduced on v0.9.1 by J0. End-to-end tracing of
  every investigation is not claimed.

**Seal:** K set `6e27f7d4d4644bca…` (including `trace-census.json`), in the 9 November manifest
`274d9901e84a9d45154c8bdc072e2ed00d3117e5a42a93a16ab3c81bb2d80e85`.
