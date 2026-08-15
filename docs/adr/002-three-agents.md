# ADR-002: Three agents, with policy enforcement inside the Orchestrator

**Status:** Accepted
**Date:** 2026-08-13
**Traces to:** [`submission/DEVPOST.md`](../../submission/DEVPOST.md)

## Decision

Bastion ships three agents — Orchestrator, Access Auditor, Escalation Agent. The Policy
Enforcer described in earlier drafts is merged into the Orchestrator as a set of explicit
policy rules. No fourth agent is reintroduced.

## Context

**No agent count is required anywhere.** Both ground-truth captures were re-read on
2026-08-13: the overview page states three mandatory technologies and names none of them a
quantity, and the rules page's sub-rubric uses only the words *"multi-agents"* and
*"sub-agents"*. Three specialised agents satisfy both. This is recorded because the
opposite was believed at one point in the build and acted on.

What *is* graded, verbatim from the rules page's closest thing to a rubric for this track:

> *"Is there a clear, strictly enforced separation of concerns between agents? Is the
> inter-agent routing logic failure-tolerant (e.g., how does the system recover if a worker
> agent loops or returns a hallucination)?"*

The build is solo, over 18 days, alongside seven pillars, a demo video, an architecture
diagram, a README, and the bonus posts. A fourth agent means a fourth deployable, a fourth
service account, a fourth registry entry, and a fourth failure mode.

## Rationale

- Three agents demonstrate the multi-agent shape completely: an orchestrator, a
  read-scoped worker, and a write-scoped worker that provably cannot read.
- **Separation of concerns is enforced in IAM, not convention.** The Escalation Agent holds
  no policy-read permission, so it cannot read what it escalates. That is the strongest
  available answer to *"strictly enforced"* — a reviewer can verify it in the console
  rather than taking the code's word.
- The Identity story is *sharper* with three, because the contrast that proves zero trust is
  Auditor-can-read versus Escalation-cannot, and a fourth agent adds no new contrast.
- Policy rules inside the Orchestrator keep the escalate-or-clear decision adjacent to the
  retry and escalation logic that acts on it, rather than splitting one decision across a
  network hop.

## Consequences

**The failure-tolerance half of that rubric is answered in code, not prose.**
ADK's orchestration agents and Agent Engine's own retry
delegates retry and backoff to Agent Engine, and bounds iteration with ADK's `LoopAgent`
guard — the last because a worker that keeps returning "not done yet" raises nothing and
times out on nothing, so neither retries nor breakers would ever see it. Hallucination
bounding rides on ADR-001's deterministic detection: a fabricated finding has no binding
behind it and is dropped before it reaches a human.

The Orchestrator carries two responsibilities — routing and policy. That is a real cohesion
cost, and it is why the policy rules stay a small, explicit, separately testable unit inside
it rather than being threaded through its routing code.

`agents/policy_enforcer/` is a **tombstone**, not dead code: it holds `MERGED.md` and a test
asserting it stays empty, so the merge is visible to a reviewer reading the tree rather than
only to one reading this file.

The rules page also asks for an *"Unlikely Hero" outside of standard corporate roles*.
Bastion is squarely a corporate compliance tool and does not fit that phrasing, which
appears aimed at the retired track framing. Recorded rather than papered over.

If the core loop is still not solid by Aug 23, the build plan's checkpoint cuts to two
agents. That would supersede this record.
