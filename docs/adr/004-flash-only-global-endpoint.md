# ADR-004: Gemini 3.5 Flash on the global endpoint, with no Pro tier

**Status:** Accepted; **verified against the live project.** This is the only record in the
set whose central claim rests on a measurement rather than a judgement.
**Date:** 2026-08-13

## Decision

Every model call in Bastion uses **`gemini-3.5-flash`** through the Vertex AI **`global`**
location. There is no Pro tier and no per-step model split.

Cloud Run and regional state are deployed in **`europe-north2`** (Stockholm). The model location
and infrastructure region are independent settings and must not
be conflated in configuration.

## Context

This record answers the first mandatory technology, quoted verbatim: *"Gemini 3.5 or newer
accessed through Gemini API or Vertex AI."* The overview also names **Gemini 3.5 Flash**
specifically in its opening requirement sentence, so Flash is the blessed path rather than a
budget compromise.

The architecture previously reserved Gemini Pro for the single escalate-or-clear decision, on
the reasoning that it is the lowest-volume and highest-stakes step in the fleet. Probing the
project on 2026-08-13 established what is actually reachable:

| Model | `global` | `us-central1` | `europe-north1`/`north2`/`west1`/`west4` | `us-east5` |
|---|---|---|---|---|
| `gemini-3.5-flash` | ✅ | ❌ | ❌ | — |
| `gemini-3.5-flash-lite` | ✅ | — | — | — |
| `gemini-3.5-pro` | ❌ | ❌ | ❌ | ❌ |
| `gemini-2.5-flash` | — | ✅ | — | — |
| `gemini-2.5-pro` | ✅ | — | — | — |

Two facts follow. Gemini 3.5 has **no regional endpoint at all** — `global` is the only
location that serves it. And **Gemini 3.5 Pro is not available to this project** in any
region tested, so the Pro step had no model to run on.

## Rationale

- An all-Flash fleet is what the overview names, so it needs no defending.
- `gemini-2.5-pro` is reachable and would preserve a reasoning tier, but it mixes model
  generations. A fleet that is uniformly 3.5 is a simpler and more defensible claim than one
  that is 3.5 except for the one decision that matters most.
- One model across three agents means one quota, one latency profile, one failure mode, and
  no routing logic deciding which model a step deserves.
- Cost is not the constraint. A budget alert exists, and Flash is selected for availability,
  operational simplicity, and alignment with the challenge guidance rather than a private
  billing-account detail.

## Consequences

The escalate-or-clear decision runs on the same model as everything else. If that decision
proves unreliable in testing, the fallback is `gemini-2.5-pro` on `global` for that step
alone, and this record is amended to say so — it is not adopted pre-emptively.

**Configuration carries two separate location values.** `GOOGLE_CLOUD_LOCATION=global` for
model calls and `GCP_REGION=europe-north2` for Cloud Run and Firestore. Collapsing them into
one variable — the obvious-looking simplification — breaks every model call with a 404 that
reads like a permissions error. That is the single most expensive misconfiguration available
in this project and the reason both names appear in `.env.example` and are asserted by
`scripts/check_docs.py`.

Model traffic on the `global` endpoint is not pinned to a region, and neither is GEAP's
managed Memory Bank ([ADR-003](003-pillars-on-geap.md)). State is in `europe-north2`; model
traffic and managed memory are not. For a hackathon build auditing the author's own project
this is acceptable, and `README.md` must say it rather than imply full EU residency — the
track's own sentence names **data sovereignty** as a thing not to violate, so an
overstatement here is a claim against a criterion rather than a footnote.

The endpoint is both reachable and exercised by the ADK fleet; the captured run is recorded in
[evidence 02](../../assets/evidence/02-gemini-investigation.md).
