# What 100% Test Coverage Missed: State Across Google ADK A2A Boundaries

> Publication draft. Refresh all issue, pull-request, release, test-count, and demo-link facts
> immediately before publishing.

I created this article for the purpose of entering the All Things Agentic Hackathon.

## The system that passed

Bastion is a three-agent access-governance fleet built with Google ADK and A2A. An Orchestrator
owns investigation state, an Access Auditor reads production IAM through a read-only identity, and
a model-free Escalation Agent delivers validated count-only reviews. The local graph passed its
configured core statement and branch coverage gate.

Then the same graph was split across deployed A2A workers, and an assumption that looked natural
in-process became false.

## The boundary we had not modeled

An ADK `output_key` writes to the session owned by the agent that declares it. In an in-process
graph, that state can appear shared because parent and child participate in one session. Across a
remote A2A boundary, the worker and caller do not suddenly share that session.

That creates two easy-to-confuse directions:

1. A remote worker can write its `output_key` into its own session without making that state
   available in the caller's session.
2. A caller-side event whose useful result exists only as state may contribute no outgoing A2A
   content for the next remote step.

Neither failure requires a crash. Plausible older content can remain in the caller and make the
workflow look successful while the new state never crossed the boundary. That is more dangerous
than an obvious exception.

## The production fix

Bastion stopped treating remote session state as transport. The authoritative findings now cross
the A2A boundary as structured, validated message content. The caller verifies that content
field-by-field against the deterministic tool output: IDs, categories, departments, scores, and
required routing must all match. A model may supply bounded rationale, but it cannot author or
alter the finding set.

Correlation uses durable request metadata rather than model-visible prose. `invocation_id` groups
one ADK run; `investigation_id` joins the complete distributed flow. Completion is also explicit:
the Orchestrator cannot mark an investigation done until every required department delivery has a
validated receipt.

The result is not a workaround that copies more state. It is a service-boundary contract.

## What we reported upstream

The deployed reproducer and both loss directions are recorded in
[google/adk-python#6854](https://github.com/google/adk-python/issues/6854). A complementary
construction-time warning for the adjacent `LlmAgent(output_key) -> RemoteA2aAgent` pattern is in
[google/adk-python#6862](https://github.com/google/adk-python/pull/6862). Another community change,
[google/adk-python#6859](https://github.com/google/adk-python/pull/6859), addresses related
state-only outbound loss and rejected inbound remote-state-delta cases.

These links describe complementary work; authorship and current merge state must be checked on
GitHub at publication time.

## The general rule

Treat remote agent state exactly like state across any other service boundary:

- decide which service owns it;
- serialize only the fields the next service needs;
- validate the schema and semantics on receipt;
- carry correlation separately from model content;
- make completion depend on acknowledged side effects;
- test the deployed topology, not only an in-process imitation.

One hundred percent configured coverage can prove every local branch ran. It cannot prove the
deployment topology preserved an assumption the local topology made invisible.

## Why this matters for institutional agents

Long-running agents remember approvals, retries, leases, exceptions, and delivery receipts. If
that context crosses departments or identities implicitly, the system cannot explain who owned a
decision or whether it arrived. An explicit state boundary makes the fleet easier to secure,
audit, recover, and extend.

Bastion's repository, evidence, and final demo links:

- <https://github.com/iarjunganesh/bastion>
- <https://bastion.arjunganesh.dev/>
- `TODO — public Devpost project URL`
- `TODO — public demo video URL`
