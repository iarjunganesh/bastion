# ADR-006: What "done" means for each of the seven pillars

**Status:** Accepted
**Date:** 2026-08-13

## Decision

Each of the seven components the track names has **one observable proof** that closes it.
A pillar is done when that proof exists and has been seen — not when its module compiles,
and not when its service is enabled.

| Pillar | The proof that closes it | State on 2026-08-15 |
|---|---|---|
| **Agent Registry** | The fleet is published in the managed Agent Registry, and a finding routes to the department the catalog says owns it | ✅ **Published 2026-08-15.** The three private JSON-RPC/A2A Cloud Run services are registered and projected as managed agent records; cross-department routing ran live — one investigation, two findings, two owning teams ([evidence 02](../../assets/evidence/02-gemini-investigation.md)). |
| **Agent Runtime** | An investigation started, survives the process that started it, and is still resumable later ([ADR-003](003-pillars-on-geap.md)) | Private Cloud Run + Eventarc admission and Agent Engine session/memory are deployed; a retained cross-week replay remains the proof artifact |
| **Memory Bank** | A finding suppressed on run *n+1* because a human approved it on run *n* | Managed Agent Engine session/memory endpoints and Firestore investigation identity are deployed; **retained suppression replay still owed** |
| **Agent Identity** | The Escalation Agent's `403 PERMISSION_DENIED`, captured, on a real IAM policy read | Separate deployed service accounts and private IAM-authenticated calls enforce least privilege; a retained live denial capture is still owed |
| **Agent Gateway** | Every inter-agent call routed through it, with the route decision logged and an unregistered target rejected | **Planned proof, not current path.** `networkservices` is enabled; deployed peers use private Cloud Run A2A with IAM authentication. |
| **Model Armor** | A malicious ticket blocked before it reaches the model | ✅ **Earned 2026-08-15.** Prompt injection blocked live by the `bastion-guardrail` template in `europe-west4` ([evidence 01](../../assets/evidence/01-model-armor-block.md)). **Still owed:** the same block observed *through* an agent |
| **Agent Observability** | Two artifacts, not one — see below | Payload-free structured audit logging and no-content ADK telemetry are deployed; a retained successful multi-agent trace is still owed |

This ledger distinguishes deployed controls from proof artifacts still being retained, rather
than treating an enabled API or a passing unit test as a completed pillar.

## Context

The track names seven components in four groups, and the temptation with a list like that is
to create seven folders and treat the list as satisfied. That is what happened: every pillar
has a module, and on 2026-08-13 exactly one of them — Memory Bank — had a working
implementation of the thing its name promises. Six had a docstring and a `TODO`.

The failure mode is specific and worth naming: **a folder per pillar reads, in a repository
tree, as a pillar per folder.** The architecture diagram, the README, and this ADR set all
inherited that reading.

Observability is the clearest case. The track asks for *"OpenTelemetry-compliant **audit
logs** and end-to-end **reasoning chain traces**"* — two artifacts, joined by "and". Audit
logs answer *what did the fleet do*, and survive for compliance. Reasoning-chain traces
answer *why did it decide that*, and are what a judge follows in Cloud Trace. It is easy to
build the second and call the pillar done; the first is what a compliance product is actually
for.

## Rationale

- **A proof is falsifiable; a checklist is not.** "Registry: done" invites the question of
  what done meant. "The Orchestrator refuses an unregistered target" can be attempted and
  can fail.
- Each proof above is something a **camera can point at**, which matters because the video
  carries the submission — judges are explicitly not required to run anything.
- Three of the seven proofs are already the claims `submission/SUBMISSION.md` lists as
  unearned: the Identity denial, the Model Armor block, and the memory suppression run. This
  record does not add new obligations so much as extend the existing ledger to all seven.
- Ordering falls out of dependency rather than preference: Registry and Gateway unblock the
  routing that Identity's denial is observed *through*, so they precede it.

## Consequences

**Observability needs a second artifact.** Structured audit logs to Cloud Logging — one
record per agent decision, with the investigation id, the actor, and the outcome — are
separate from the trace and must not be derived from it. A trace is sampled and expires; an
audit log for a compliance product is neither.

**`traced_agent_call` having one call site, in a test, is the tell** that half the pillar was
built and never connected. The audit half is now called from four modules; the trace half is
wired into each agent's decision step as part of the ADK rewrite
([ADR-005](005-adk-as-the-agent-framework.md)), not a later pass.

The Registry proof has a **deploy-time registration step** in
`infrastructure/register_agents.py`: it idempotently publishes the three canonical private
JSON-RPC endpoints. The managed Registry then projects them as discoverable Agent records.

If the schedule forces a cut, the cut is a **pillar's proof downgraded and disclosed**, not a
pillar quietly left in the diagram. The cut order for services is fixed in
[ADR-003](003-pillars-on-geap.md); pillars are not on that list, because all seven are
named by the track and dropping one silently is the failure this record exists to prevent.

## Absorbed record: submission artifacts are engineering constraints (was ADR-012)

Folded in on 2026-08-15, because it is the same idea as this record applied to the submission
rather than to the pillars: **an artifact is done when it exists and has been seen.**

The architecture diagram, the spin-up instructions, the ~4-minute video, and the proof the
backend ran on Google Cloud are required submission fields. Treating them as a filing step at
the end makes them the first things to be cut when the schedule slips, which inverts their
value — judges are explicitly not required to run anything, so the video and the diagram carry
the submission.

They are therefore build constraints with the same standard of proof as a pillar:

| Artifact | Done when |
|---|---|
| Architecture diagram | It is derived from `assets/architecture/gcp-state.json`, which is measured from the live project |
| Spin-up instructions | Someone other than the author has run them start to finish |
| Demo video | The four load-bearing shots are captured, redacted, and in order |
| Deployment proof | A console frame showing the service running, not a claim that it did |

`scripts/check_docs.py` fails the build on a committed architecture image while fewer than two
resources are deployed — the gate lifts itself once there is a real system to draw.
