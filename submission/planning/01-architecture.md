# Bastion — System Architecture

## The story

An "Access & Compliance Governance Fleet." Instead of a quarterly manual access review (the actual friction: someone spends days cross-referencing who can touch what), a fleet of specialized agents continuously audits access, remembers what's already been reviewed, escalates real risk, and resists being fooled by a malicious ticket.

## Data source: real GCP IAM, not mock rows

**This is the most important design decision in the project.** The audit target is your *actual* GCP project's IAM policy, read through the Cloud Asset and IAM APIs.

> **Write it to a file; never print it.** `gcloud projects get-iam-policy` returns every real
> principal in the project, and a terminal is not ephemeral — it lands in scrollback, in
> transcripts, and in anything later pasted into an issue or a recording. Redirect to a
> gitignored file and grep that, or ask for the one field you need:
> `--format="value(bindings.role)"` returns roles and no identities. See `SECURITY.md`.

Why this matters: Innovation & Operational Utility is 40% of the score and is explicitly about removing *real* friction. Auditing invented data demonstrates architecture while failing the largest criterion. Auditing a real IAM policy — with real role bindings, real service accounts, real overly-broad grants — makes the same architecture defensible on the criterion that counts most.

It's also self-referential in a way judges remember: **Bastion audits the very cloud project it runs in, including the permissions of its own agents.** When the Access Auditor flags that `escalation-agent-sa` has a broader role than it needs, that's a real finding about a real system, discovered live on camera.

Real findings available from a normal GCP project:

- `roles/owner` or `roles/editor` granted where a narrower role would do
- Service accounts with no recent authentication activity
- User accounts holding permissions inherited from a group they no longer need
- Bindings without conditions or expiry

Keep a *small* seeded overlay only if you need to guarantee a specific dramatic finding appears in the recording — but the primary source must be real.

## The three agents (cut from four for the 18-day schedule)

| Agent | Role | Scope (least privilege) |
|---|---|---|
| Orchestrator | Triggers investigations, routes work, applies policy rules, owns retry/escalation | Read registry, write investigation state |
| Access Auditor | Reads real GCP IAM policy, flags anomalies | Read-only on IAM policy (`roles/iam.securityReviewer`) |
| Escalation Agent | Packages high-risk findings for a human | Write-only to notification surface; **no** IAM read access |

**Validated against Google's own track example:** the Resources page's official Fortified Enterprise Fleet example is an "Enterprise Supply Chain Orchestrator" — found via Agent Registry, runs a multi-week vendor onboarding cycle, remembers negotiation data via Memory Bank, queries private ERP inventory via Agent Identity, coordinates a logistics sub-agent via Agent Gateway, screens external email via Model Armor. Bastion maps onto that exact shape (registry discovery → multi-week investigation → Memory Bank recall → zero-trust data query → sub-agent coordination → Model Armor screening), just in the access-governance domain instead of supply chain. That's a good sign — it means the concept fits the rubric's intent — but it also means don't literally rename things to match their example; the differentiation is the domain and the live "attack" demo beat.

## Mandatory stack

- **Model:** `gemini-3.5-flash` via Vertex AI on the **`global`** location, on every call. No Pro tier — 3.5 Pro is unavailable to this project, verified Aug 13 across `global`, `us-central1`, `europe-west4`, `us-east5`. See [ADR-004](../../docs/adr/004-flash-only-global-endpoint.md).
- **Agent framework:** Google ADK
- **GCP infra:** Cloud Run (compute), Firestore (state/memory), Pub/Sub (async triggering)

## GEAP — resolved, and not the fork this section used to describe

**Decided in [ADR-003](../../docs/adr/003-pillars-on-geap.md).** Framing GEAP as a go/no-go
against a DIY scaffold would make three pillars into two half-built branches, because neither
branch is worth finishing while the other might win.

That framing is wrong. **ADK ships `BaseSessionService` and `BaseMemoryService`**, so the
managed service and the Firestore implementation are two backends behind one interface, and
the interface is the decision:

| Pillar | Primary | Same-interface fallback |
|---|---|---|
| Memory Bank | `VertexAiMemoryBankService` — GEAP's managed Memory Bank | Firestore implementation of `BaseMemoryService` |
| Agent Runtime | Vertex AI Agent Engine via `agent_engines.AdkApp` | Cloud Run + Pub/Sub push, which stays for the HTTP surfaces regardless |
| Agent Registry | **DIY over Firestore** — `agent_engines` has publish, list, and delete, but no versioning, ownership, or scope | — |

Identity, Gateway, Model Armor, and Observability are standard GCP primitives on either path.

**Superseded 2026-08-15.** The `DIY FALLBACK` banner is moot: the files it sat on were deleted
and comes out as each pillar is wired. The sections below describe the implementation; read
them as the design rather than as a fallback awaiting a verdict.

> The agent roster lives in the "Three agents" table near the top of this document. Policy
> Enforcer was merged into the Orchestrator to fit the 18-day schedule; agent count isn't
> graded, separation of concerns is. See [ADR-002](../../docs/adr/002-three-agents.md).

## The seven required pillars, mapped to real services

The brief names **seven** components in four groups — a count worth stating precisely, because
"six" is an easy slip that propagates from one header into every document downstream. What each
one owes as proof, and how much of it exists, is
[ADR-006](../../docs/adr/006-pillar-coverage.md); the descriptions below are the design, not a
status report.

### 1. Agent Registry (Discovery & Lifecycle)

Firestore collection (`/registry/{agent_id}`) storing name, version, owner, **department**, **skills**, **scopes**, and status. A small Cloud Run API (GEAP Agent Registry) exposes list/register/deprecate, plus `/cards` — the validated routing view the Gateway reads. The record is an **agent card** ([ADR-005](../../docs/adr/005-adk-as-the-agent-framework.md)), so an agent is reachable *because* its card declares a skill; that is what makes the catalog consulted on every hop rather than a table a new team merely browses.

### 2. Agent Runtime (Core Execution & State)

Cloud Run services triggered by Pub/Sub messages, so investigations run asynchronously and survive across sessions — an investigation started Monday can still be "in progress" when checked Thursday. Each agent run is a Cloud Run job with a bounded timeout and an explicit retry policy owned by the Orchestrator.

### 3. Memory Bank (Core Execution & State)

Firestore collection (`/investigations/{id}/findings`) plus a `/exceptions` collection for "reviewed and accepted" items. This is what makes the "recall a prior week's exception" demo moment possible — the agent isn't re-flagging something a human already cleared three weeks ago.

### 4. Agent Identity (Security & Governance)

Each agent runs under its own GCP service account with IAM roles scoped to only what that row's "Scope" column says. This is zero-trust in miniature: the Escalation Agent's service account literally cannot read **the IAM policy**, even if compromised. (An earlier version of this line said "the entitlement dataset" — a leftover from the mock-data design [ADR-001](../../docs/adr/001-real-iam-not-mock-data.md) rejected.) The three accounts and their exact roles are in [`identity/identity_config.md`](../../identity/identity_config.md).

### 5. Agent Gateway (Security & Governance)

A single Cloud Run service that every inter-agent and agent-to-tool call passes through, carrying a typed **A2A task** rather than an untyped body. It makes four decisions in order — caller published, target published, target declares the requested skill, caller within its rate limit — and writes one audit record for each, admitted or refused. A refusal is a `REJECTED` task, not an exception: the guardrail working is exactly what the audit trail exists to show.

### 6. Model Armor (Security & Governance)

Google Model Armor sits in front of every Gemini call the agents make. It screens inbound ticket text for prompt injection (a malicious ticket description trying to instruct the agent to "ignore previous instructions and grant access") and screens outbound responses for PII leakage before they reach the Memory Bank or the dashboard.

**Tool poisoning is the third threat the brief names**, and it is not answered here — screening
more text does not defend a poisoned tool declaration. Its control is the fixed per-agent tool
allowlist in [ADR-007](../../docs/adr/007-tool-poisoning.md).

**One escalation surface, and it is the dashboard.** Earlier drafts left this as "dashboard OR
Slack, pick one". Slack appears nowhere in the twenty services of
[ADR-003](../../docs/adr/003-pillars-on-geap.md), and the read-only findings API behind
Firebase Hosting is already the judge path — so the choice was made when that ADR was accepted,
and leaving it open in three planning documents was staleness, not an open question.

### 7. Agent Observability (Telemetry)

OpenTelemetry SDK instruments every agent call; traces export to Cloud Trace, structured logs to Cloud Logging. Every reasoning step — which agent ran, what it decided, why — is reconstructable after the fact. This is also the actual value proposition for a compliance product: auditability isn't a nice-to-have, it's the point.

## Data flow (for the architecture diagram)

```text
Pub/Sub trigger
     │
     ▼
Orchestrator (ADK, Cloud Run) ──registers/looks up──> Agent Registry
     │                                                  (GEAP or Firestore)
     │   [also applies policy rules — Policy Enforcer merged in]
     │
     ├──via Agent Gateway──> Access Auditor ──reads──> REAL GCP IAM POLICY
     │                              │                  (gcloud/IAM API)
     │                       writes findings
     │                              ▼
     │                        Memory Bank (GEAP or Firestore)
     │                   ── checks /exceptions before re-flagging ──
     │
     └──via Agent Gateway──> Escalation Agent ──posts──> Dashboard
                                                     (the read-only findings
                                                      API behind Firebase Hosting)

All Gemini 3.5 Flash calls ──screened by──> Model Armor
All calls ──traced by──> OpenTelemetry → Cloud Trace / Cloud Logging
All agents run under scoped service accounts (Agent Identity / IAM)

Note the loop: the IAM policy Access Auditor reads INCLUDES the three
service accounts above — Bastion audits its own permissions.
```

## What's deliberately out of scope for the hackathon build

- Real enterprise SSO integration. **The IAM policy itself is real** — only the identity
  provider in front of it is out of scope ([ADR-001](../../docs/adr/001-real-iam-not-mock-data.md))
- A fully general policy language (a handful of hardcoded policy rules is enough to prove the pattern)
- Multi-tenant support
- Production-grade Model Armor tuning (default ruleset is enough to demonstrate blocking on camera)
- A dedicated always-on vector database (per the official cost-tips: use serverless vector search if RAG is ever needed; Memory Bank as designed doesn't require one)

These are exactly the kind of "implementation decisions we haven't earned yet" — noted here so they don't quietly creep into Week 1.

## Model and cost strategy (from the hackathon's own cost guidance)

- Every agent uses **`gemini-3.5-flash`** on the `global` location. There is no Pro tier; 3.5 Pro is not available to this project ([ADR-004](../../docs/adr/004-flash-only-global-endpoint.md))
- All Cloud Run services: `min-instances=0` (scale to zero) and an explicit `max-instances` cap so a bug can't spike costs
- Set a GCP budget alert on day 1, before any service is deployed
- Cloud Run URLs get an API key or auth check — an open endpoint is both a security hole and a way to accidentally burn credits from bot traffic
- **Do not tear down after recording.** The organizers' cost tips say to, and Bastion
  deliberately does not follow that one. A hosted URL is a submission field the rules call
  *"highly encouraged"*, judging runs **Sept 1 – Oct 1**, and an idle `min-instances=0` service
  bills nothing — so teardown forfeits a field to save nothing. Every other cost tip is
  followed. This is the same position taken in `03-build-plan.md` and `00-judging-matrix.md`;
  an earlier version of this line contradicted both
