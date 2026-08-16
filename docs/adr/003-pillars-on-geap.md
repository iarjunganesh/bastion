# ADR-003: Use the managed enterprise agent platform

**Status:** Accepted 2026-08-13; amended 2026-08-15 and verified 2026-08-16  
**Traces to:** [hackathon brief](../../submission/DEVPOST.md)

## Decision

Bastion composes the seven named pillars from managed Google Cloud products rather than
reimplementing them.

| Pillar | Deployed implementation |
|---|---|
| Agent Registry | Regional Registry catalog for the managed Orchestrator, two worker Agent Cards, and approved Google API endpoints |
| Agent Runtime | Python 3.12 managed Runtime source deployment with Agent Identity |
| Memory Bank | Separate managed engine used for durable sessions and memory |
| Agent Identity | Runtime Agent Identity plus distinct Cloud Run workload service accounts |
| Agent Gateway | `bastion-egress`, IAP authorization extension, and fail-closed auth policy |
| Model Armor | Regional template used by fail-closed ADK pre-model callbacks |
| Agent Observability | ADK no-content telemetry, payload-free audit logs, regional retention, metrics, alerts, and dashboard |

Firestore and Eventarc complement the managed Runtime: they own trigger admission, leases, retry,
deduplication, and dead-letter delivery across process loss.

## Context and amendment

The first version incorrectly concluded that Registry had no managed equivalent and implemented a
DIY catalog and Gateway. That conclusion came from searching one SDK namespace rather than the
platform. On 2026-08-15 those substitutes were removed in favor of the actual managed services.
The amendment remains recorded because it explains the current architecture and prevents a
future return to parallel, weaker control planes.

## Rationale

- The track asks how institutions adopt official enterprise infrastructure; the managed products
  are the architecture, not decorative API enablement.
- Gateway, IAP, Agent Identity, Registry, and Model Armor compose an authorization and content-
  safety chain that a repository-owned proxy would only imitate.
- ADK 2.7 supplies managed session/memory seams, A2A agents, plugins, and Agent Runtime support.
- The public proof can distinguish platform enforcement from local policy code.

## Regions

Cloud Run, Firestore, Pub/Sub, and Eventarc use `europe-north2`. Runtime, Memory Bank, Gateway,
Registry, Model Armor, and the audit bucket use `europe-west4`. Gemini 3.5 Flash uses Vertex AI
`global`; that is not an EU residency claim.

## Consequences

- Runtime egress is bound to Gateway and IAP grants its Agent Identity per Registry resource.
- The Cloud Run dispatcher has no peer credential or worker invoker grant, so it cannot bypass
  the managed path.
- Model Armor fails closed; there is no fallback model classifier.
- Agent Cards and A2A types come from the official SDK/protocol, while department routing and
  classification remain deterministic repository policy.
- Versions and managed configuration are release gates. Experimental/deprecated ADK surfaces are
  pinned and explicitly accepted in [ADR-005](005-adk-as-the-agent-framework.md).

The live measured state is [gcp-state.json](../../assets/architecture/gcp-state.json); observable
closure for each pillar is [ADR-006](006-pillar-coverage.md).
