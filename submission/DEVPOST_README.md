# Bastion

**A private fleet of catalogued agents that audits live GCP IAM, remembers human decisions, and
routes minimized findings without gaining write access.**

<!-- Devpost renders the title and tagline above from its own form fields. Begin the pasted
     description at the link row below, or the live page repeats its own header. Observed
     duplicated on the draft 2026-08-25. -->

[Public evidence console](https://bastion.arjunganesh.dev/) ·
[Source code](https://github.com/iarjunganesh/bastion) ·
[Architecture](https://github.com/iarjunganesh/bastion/blob/main/docs/ARCHITECTURE.md) ·
[Evidence index](https://github.com/iarjunganesh/bastion/blob/main/assets/README.md)

## Inspiration

Enterprise permissions change continuously, while access reviews are periodic and forgetful.
The hard part is not generating another report. It is making an autonomous review safe enough to
run against production data, durable enough to remember a human decision days later, and governed
enough that every agent has an owner, identity, purpose, and bounded capability.

Bastion turns that problem inward: the agent fleet audits the IAM policy of the Google Cloud
project that runs it.

## What it does

An approved Pub/Sub event enters a private, event-driven workflow. The Orchestrator owns the
investigation lifecycle. The Access Auditor reads live IAM through a read-only identity and
deterministic rules convert it into opaque findings. Gemini 3.5 Flash may explain those findings,
but it cannot add, remove, re-score, redirect, or clear one. A model-free Escalation Agent then
delivers validated count-only reviews to the departments that own them.

The fleet remembers human-approved exceptions in durable state. A matching later finding is
suppressed rather than paged again. In the deployed proof, an exception remained effective after
a real three-day gap spanning deployments and restarts. We do not claim that a literal week
elapsed; the architecture is designed for longer asynchronous work and expiry behavior is tested.

## Why this is an enterprise fleet, not a chatbot

- Three institutional agents are catalogued with owner, department, purpose, skill,
  classification, version, and approval metadata.
- Agent Identity and IAM separate responsibilities. The Auditor can read policy; the Escalation
  identity is structurally denied the same read.
- Firestore supplies durable inbox, leases, retry, idempotency, exception, and delivery state;
  managed sessions and Memory Bank supply agent context.
- Gateway policy and registered destinations bound agent-to-agent access and fail closed.
- Model Armor refused a live injection attempt at the **deployed agent callback** on 2026-08-25:
  the A2A task failed closed and no model or tool call followed. The fail-closed path is
  additionally covered by tests.
- Payload-free audit events preserve investigation and invocation correlation without retaining
  prompts, responses, raw principals, bindings, or private endpoints.

## How we built it

Bastion uses Google ADK 2.8.0 and A2A for a three-agent graph, Gemini 3.5 Flash through Vertex AI,
and the managed enterprise-agent pillars: Agent Runtime, Registry, Identity, Gateway, Memory Bank,
Model Armor, and Observability. Cloud Run hosts private worker and receiver surfaces. Pub/Sub and
Eventarc provide durable event admission. Firestore holds operational continuity. Cloud Asset
Inventory supplies read-only production IAM data. Cloud Logging and Cloud Trace make the flow
inspectable, while Secret Manager and Workload Identity Federation avoid committed credentials.

Before beginning Bastion on August 15, 2026, I completed Google's Gemini Enterprise Agent Ready
(GEAR) program and earned the
[public badge](https://developers.google.com/profile/badges/community/gear?u=iarjunganesh) on
August 10. The program prepared me for the platform, but all Bastion design, implementation,
deployment, and evidence work began afterward during the hackathon period.

Raw IAM member, role, resource, and binding values stop before the model boundary. Deterministic
code produces the canonical finding set; the model contributes bounded rationale. Output is
validated against that canonical set and screened again before delivery.

![Bastion enterprise fleet architecture](https://raw.githubusercontent.com/iarjunganesh/bastion/main/assets/architecture/enterprise-fleet-architecture-light.png)

## Challenges we ran into

The most important failures appeared only after the in-process agent graph became a deployed A2A
topology. ADK session state belongs to the agent that declares it; it does not silently become
shared state across a remote boundary. A locally correct `output_key` flow could therefore lose
the value a caller expected. Bastion replaced that assumption with structured, validated content
across the A2A boundary and durable request metadata for correlation.

That production finding was reported upstream in
[google/adk-python#6854](https://github.com/google/adk-python/issues/6854), which is open. A
complementary PR of mine, [google/adk-python#6862](https://github.com/google/adk-python/pull/6862),
was closed unmerged on 2026-08-24 by a Google maintainer who confirmed the underlying point — the
A2A session-state boundary is a general transport property, not a `SequentialAgent` bug — and
directed the fix to community PR
[google/adk-python#6859](https://github.com/google/adk-python/pull/6859), which remains open.
Nothing is merged, and this status is re-verified against GitHub immediately before submission
rather than quoted from memory.

Other difficult boundaries were equally useful: a passing test does not prove a deployed route,
a configured retry policy does not prove redelivery was observed, and an architecture diagram can
overclaim as easily as prose. Bastion therefore treats implemented, tested, deployed, and observed
as separate states.

## Accomplishments that we're proud of

- Live read-only IAM produced deterministic findings routed to two owning departments without
  exposing principals or bindings to the model.
- The Escalation identity was observed failing the IAM read that the Auditor identity can perform.
- A human-approved exception suppressed a matching finding three days later across deployments and
  restarts, with no notification sent to the suppressed department.
- The model cannot change the authoritative finding set or required delivery; field-by-field and
  completion gates enforce both boundaries.
- The public evidence console is static and sanitized. It exposes no operational GCP endpoint and
  makes no request into the private fleet.
- A public clean clone passed the full offline gate under Python 3.12 with no credentials or
  undocumented files.

## What we learned

Agent state must be treated like state in any other distributed system: crossing a service
boundary requires an explicit schema, an ownership decision, and failure handling. Prompt wording
is not an authorization boundary. A catalog entry is useful only when identity and routing enforce
it. And a compliance claim is strongest when sensitive data never enters the model, rather than
when it is merely promised to remain confidential after the fact.

## What's next

Current-route IAM provenance, the agent-mediated Model Armor refusal, the correlated audit trail and
the Cloud Trace chain are captured and retained. Two observations are deliberately still open and
are not claimed: a managed Gateway refusal of an unregistered caller, and a watched
timeout/retry/dead-letter sequence. They are deferred behind the honest narrower wording in the
claim matrix; the five-image gallery is composed, so the remaining pre-submission work is the
under-four-minute live demo. After the hackathon, the most valuable extensions are closing those
two observations, adding governed department catalogs, introducing a deliberate recurring trigger
with an operational pause control, and hardening the retained audit store if an immutable retention
requirement is adopted.

## Reproduce it

The public repository's tests need no Google Cloud credentials:

```powershell
git clone https://github.com/iarjunganesh/bastion.git
Set-Location bastion
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
pytest tests --cov --cov-report=term-missing --cov-fail-under=100
```

The remaining lint, type, documentation, version, diagram, and static-site gates are listed in the
[README](https://github.com/iarjunganesh/bastion#quality-gates). Live deployment and verification
require a GCP project and are deliberately separate from the offline reproducibility claim.

## Honest boundaries

Bastion cannot modify IAM. Gemini uses the Vertex AI `global` endpoint. The audit bucket is not
immutable. The observed decision-memory gap is three days, not a literal week. The current
deployment is event-driven and claims no recurring Scheduler job. Those are design and evidence
boundaries, not capabilities hidden in fine print.
