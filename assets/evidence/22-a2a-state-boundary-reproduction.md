# Evidence 22 — the A2A state boundary, reproduced on the locked stack

**Collected:** 4 November 2026, offline reproduction O1. Localhost only: no model, no cloud and no
credentials. A fresh Python 3.12.12 environment was built from `requirements.lock`
(`google-adk` 2.13.0, `a2a-sdk` 1.3.0, `uvicorn` 0.54.0, `sse-starlette` 3.6.0).

## What was run

1. **The original reproduction, unchanged.** This is the script supplied upstream on 27 August
   in [google/adk-python#6854](https://github.com/google/adk-python/issues/6854). A sequential
   pipeline runs a content step, then a policy step that writes only a session state delta,
   then a `RemoteA2aAgent` served over A2A on localhost. The script prints what the remote agent
   received.
2. **An extended run.** This is the same construction, except the remote agent also writes a
   state delta of its own. Every warning emitted by the ADK loggers is captured.

## Result

| Direction | Observed on 2.13.0 | On 2.7.1 and 2.8.0 (27 Aug) |
|---|---|---|
| Caller → remote: a state-only event before the remote agent | Value present in the caller's state, absent from the request; the remote received the *earlier* step's content instead | Same |
| Caller-side warning | `RemoteA2aAgent 'notifier' cannot forward the preceding state-only event across A2A. Session state is local to each agent; include the required values in event content instead.` | None (silent) |
| Remote → caller: the remote writes a state delta | Not applied to the caller's state | Same |
| Peer-side warning | `Ignoring a session state delta from a remote A2A peer. Session state is local to each agent; return values needed by the caller as event content or task output instead.` | None (silent) |
| Substituted content | Wrapped in `<<<BEGIN_QUOTED_AGENT_CONTENT>>>` markers, with a preamble marking it as data | Markers present on 2.8.0 |

The original script still prints `REPRODUCED - state-only event dropped silently`, because its
check predates the upstream change. The run's log shows the caller-side warning, so on 2.13.0
the drop happens but is no longer silent.

Say **on the locked stack the per-agent session boundary behaves as it did in August, in both
directions, and both upstream warnings now fire. The boundary is observable but is still not
transport.** Bastion's correctness still rests on its explicit message contracts and completion
gate, not on these warnings.

## What this does not show

- **The deployed fleet.** Production still runs `google-adk` 2.7.1, built 23 August, which has
  neither warning. This is a source-target result.
- **Anything beyond the two warnings.** The other transport behaviours recorded in
  [ADR-012](../../docs/adr/012-structured-findings-across-a2a.md) were not re-run. These are the
  attributed-history wrapping and the contentless failed-task event.

The same run printed `SequentialAgent`'s deprecation warning unchanged: *"Workflow cannot yet be
used as an LlmAgent sub-agent."* The migration trigger in
[ADR-005](../../docs/adr/005-adk-as-the-agent-framework.md) is therefore still unmet on 2.13.0.
