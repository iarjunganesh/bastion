# Bastion — Judging Matrix

Project: **Bastion** — a fortified fleet of enterprise compliance/access-governance agents.
Track: **Fortified Enterprise Fleet**
Deadline: August 31, 2026, 5:00 PM PT
Last verified against the live hackathon page: **Aug 13, 2026** (field: 2,327 participants; prize pool: $180,000). The
capture itself is [`../DEVPOST.md`](../DEVPOST.md) — where this file and that one disagree, the capture wins.

Every feature below exists because it maps to a requirement, a judging criterion, or a bonus point. Nothing gets built that doesn't trace back to a row in this table.

## Stage 1 — Pass/Fail Baseline (must all be true or the submission is disqualified before scoring)

**Two of these three are not met in code**, and this table asserted them as
done. Corrected below; the gaps are recorded in
[ADR-005](../../docs/adr/005-adk-as-the-agent-framework.md) and
[ADR-001](../../docs/adr/001-real-iam-not-mock-data.md) rather than quietly repaired.

| Requirement | Plan | State at v0.1.0 |
|---|---|---|
| Gemini 3.5+ via Gemini API or Vertex AI | `gemini-3.5-flash` via Vertex AI on `global`, at the three call sites in ADR-001 (Flash is named explicitly on the overview) | ✅ **Met 2026-08-15** — 5 model calls in one investigation |
| At least one Google agent framework | Google ADK — one of the four the rules accept (*"Google ADK, GenAI SDK, Antigravity SDK or GenKit"*), chosen in ADR-005 | ✅ **Met 2026-08-15** — three ADK `LlmAgent`s executed |
| At least one GCP infra service | Cloud Run (compute) + Firestore (state) + Pub/Sub/Eventarc (async) | ✅ Private fleet deployed; retained end-to-end trace evidence pending |
| Reasonably addresses the Fortified Enterprise Fleet challenge | All seven components present with one observable proof each | ◐ **Two of seven proven** — the Model Armor block and the real-IAM investigation with cross-department routing; ledger in [ADR-006](../../docs/adr/006-pillar-coverage.md) |
| Newly built during Submission Period (Aug 3–31, 2026) | Repository history starts with the approved baseline inside the window | ✅ Initial commit `74bc831`; subsequent delivery is preserved on backup branches |
| Hosted Project URL | *"A hosted project is highly encouraged"* — a submission field, not pass/fail. Judges *"are not required to test the Project."* | ◐ Private Cloud Run fleet is deployed; there is no public judge UI or hosted URL yet |

## Stage 2 — Weighted Scoring

### Innovation & Operational Utility — 40%

The page's current wording: *"How much real-world friction does the agent remove on its own? We reward autonomous, high-value action over simple chat — agents that make decisions and complete tasks with little to no hand-holding."*

The brief's own wording, verbatim, and where each clause is answered:

| Fortified Enterprise Fleet sub-criteria | Evidence in Bastion |
|---|---|
| *"how agents are cataloged for cross-department use"* | Agent Registry contains the three private Bastion JSON-RPC services. Department ownership is enforced by repository routing policy; version/approval metadata is not yet demonstrated. |
| *"how they safely maintain context across weeks of asynchronous operations"* | Eventarc admission deduplicates into Firestore and maps a stable investigation ID to Agent Engine session/memory. A retained prior-week suppression replay is still owed. |
| *"how they interact with production data without violating enterprise compliance, data sovereignty, or security policies"* | Access Auditor reads the **real IAM policy of a live project**, read-only via `roles/iam.securityReviewer`, never written back. The Escalation Agent provably cannot read it at all. Infrastructure is pinned to `europe-north2`; **model traffic is `global` and cannot be region-pinned**, which is stated in the architecture rather than glossed |

### The seven components, in the brief's four groups

| Group | Component | The brief's definition |
|---|---|---|
| Discovery & Lifecycle | Agent Registry | *"central repository for publishing, versioning, and discovering enterprise-approved agents"* |
| Core Execution & State | Agent Runtime | *"long-running, asynchronous background execution"* |
| Core Execution & State | Memory Bank | *"persistent, secure cross-session context over extended timelines"* |
| Security & Governance | Agent Identity | *"zero-trust access control"* |
| Security & Governance | Agent Gateway | *"unified routing and policy enforcement"* |
| Security & Governance | Model Armor | *"inline guardrails to block prompt injection, tool poisoning, and PII leaks"* |
| Telemetry | Agent Observability | *"OpenTelemetry-compliant audit logs and end-to-end reasoning chain traces"* |

Two clauses are easy to under-deliver on and are called out because of it: **tool poisoning**
is a named Model Armor threat distinct from prompt injection, and **audit logs** are named
separately from **reasoning chain traces**. Each needs its own artifact.

The recommended toolkit is the **Gemini Enterprise Agent Platform**. Resolved on its due date
in [ADR-003](../../docs/adr/003-pillars-on-geap.md): GEAP is not an alternative to the
scaffold, it is a backend behind ADK's service interfaces. Memory Bank and Runtime take the
managed path; the Registry is the managed Agent Registry service, with three Bastion records
published. Rich version/ownership metadata is a remaining evidence gap, not a DIY substitute.

**Note the strongest claim available here:** the data is real, not simulated. Most hackathon submissions in this track will demo against invented enterprise data. Auditing a real IAM policy — including the permissions of Bastion's own agents — is the single biggest differentiator on this 40% criterion.

### Architectural Discipline & Tech Stack — 30%

| Sub-criteria | Evidence |
|---|---|
| Clean, modularized, maintainable system | **Six of the seven pillars are managed GEAP products, and Bastion holds the seam rather than a module** — ~3,460 lines that reimplemented them were deleted 2026-08-15 ([ADR-003](../../docs/adr/003-pillars-on-geap.md)). What survives is one callback or one function per pillar. **A folder is not a pillar** — what "done" means for each is [ADR-006](../../docs/adr/006-pillar-coverage.md) |
| State management | Managed Agent Engine session/memory URIs plus Firestore's durable Eventarc inbox ([ADR-003](../../docs/adr/003-pillars-on-geap.md)). The Firestore-backed implementation that used to sit here was deleted. **Deployed;** a retained cross-week replay is still owed |
| Tools isolated and scoped for security | Each agent's tool set is a fixed allowlist, and the Escalation Agent's tool takes a **count** rather than findings — the signature is the control ([ADR-007](../../docs/adr/007-tool-poisoning.md)). Per-agent service accounts and the Agent Gateway hop are **designed and unbuilt**: the three agents currently share one identity as `sub_agents` of one process |
| Failure-tolerant multi-agent routing | ◐ **Half answered.** *Hallucination* is bounded and always was: detection is deterministic and runs before any model call, so a fabricated finding has no binding behind it. *Retry* is **not** — the hand-rolled backoff, circuit breaker and loop guard went with `resilience.py` on 2026-08-15, and Agent Engine's managed retry needs a deployment that does not exist. The rules page asks this directly, so the gap is named rather than glossed |

### Demo & Production Readiness — 30%

| Sub-criteria | Evidence |
|---|---|
| Live, unedited proof of execution | Demo shows Cloud Run logs and Cloud Trace updating in real time as agents run |
| Clean architecture diagram + reproducible setup | ✅ Level 1 and Level 2 are hand-authored 1920×1080 SVGs with light/dark variants and an animated GIF of each; Level 3 stays inline mermaid. The Devpost attachment the rules require now exists. Every committed SVG **states its own build state in its own text**, and `scripts/check_docs.py` fails the build if one does not — a caption is separable from the picture, a footer is not |
| Visual proof of Google Cloud deployment | Cloud Run dashboard and Vertex AI request logs shown on camera |

## Stage 3 — Bonus Points (added on top, max ~1.0)

| Bonus item | Points | Plan |
|---|---|---|
| Public blog/video post about the build | +0.2 | Short dev.to post written in Week 3, marked as created for this hackathon |
| Social post w/ #AllThingsAgenticHackathon | +0.2 | One X or LinkedIn post at submission time |
| Additional Google AI models (Gemma, Veo, Lyria) | up to +0.6 | Stretch goal only if Weeks 1–2 finish early — not core scope |

## Cross-cutting prizes this submission is also eligible for

Total pool is now **$180,000**. As a solo entrant, this one submission is in contention for:

| Prize | Amount | Winners |
|---|---|---|
| Grand Prize | **$50,000** (raised from $40,000) | 1 |
| The Fortified Enterprise Fleet | $20,000 | 1 |
| Individual/Hobbyist (Best Team/Solo Build) | $10,000 | 2 |
| Best Architectural Design | $5,000 | 2 |
| Best Multimodal UX | $5,000 | 2 |
| Honorable Mentions | $2,000 | 5 |

Not eligible: Startup Excellence (requires submitting on behalf of an incorporated organization with a corporate email — you're entering solo).

Note that a project can win **a maximum of one prize**, so these are alternative outcomes, not additive. The practical implication: eleven of the winning slots above are non-Grand-Prize, so a strong-but-not-best submission still has multiple realistic landing spots.

## Not resolved — the rules page still disagrees with the overview

**This section previously claimed the conflict was resolved. It is not, and
[`../DEVPOST.md`](../DEVPOST.md#judging) — the capture of the pages themselves — said so at
the same time.** Two documents in this folder asserted opposite facts about the same web
page; the capture wins, and this is corrected to match it.

Re-verified 2026-08-13: the rules page still names *"The Continuous Action Engine"*, *"The
Evolving Knowledge Engine"*, and *"The Multi-Agent Nexus"* where the overview says Taskmaster,
Collaborative Partner, and Fortified Enterprise Fleet. **Multi-Agent Nexus is this track under
its old name**, and its sub-bullets are the closest thing to a rubric this track has:

> *"Is there a clear, strictly enforced separation of concerns between agents? Is the
> inter-agent routing logic failure-tolerant (e.g., how does the system recover if a worker
> agent loops or returns a hallucination)?"*

Both pages are captured verbatim in [`../DEVPOST.md`](../DEVPOST.md#judging). **Where they
conflict, satisfy the union rather than picking one.** Re-check both before submitting.

What the recheck confirmed, beyond the criteria:

- **Judging runs Sept 1 – Oct 1, 2026**; winners announced on or around Oct 8. The month-long
  judging window is why the services stay up rather than being torn down.
- Scoring is **1–5 per criterion**, averaged, plus bonus points, for a **maximum final score
  of 6**. Bonus items: blog/podcast/video max 0.2, social post max 0.2, each additional Google
  AI model 0.2 up to 0.6.
- The Innovation criterion asks whether the system *"eliminates real-world friction"* and
  whether a **"Twist"** is present for high-value autonomous execution.
- **Tiebreaker:** criterion-by-criterion in the order listed — so Innovation & Operational
  Utility breaks ties first. Another reason the real-IAM decision is the one that matters.
- Pre-existing code must be **disclosed**; the project must otherwise be newly created in the
  submission period and solely owned by the entrant.
- Each project is eligible for **at most one prize**, and every cash prize carries Google
  Cloud credits alongside it (Grand $5,000; category and Startup $2,000–$5,000; the rest
  $500–$1,000).
