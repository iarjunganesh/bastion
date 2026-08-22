# ADR-006: Observable proof closes each pillar

**Status:** Accepted 2026-08-13; proof ledger refreshed 2026-08-16  
**Traces to:** [hackathon brief](../../submission/DEVPOST.md)

## Decision

A pillar is complete only when implementation, deployment, and an observable proof agree. An
enabled API or folder name is not proof.

| Pillar | Observable proof | Current state |
|---|---|---|
| Agent Registry | Three governed agents and approved platform destinations are discoverable; routing rejects unknown departments | **Deployed and verified.** Two worker cards plus managed Runtime entry; metadata/routing tests pass. |
| Agent Runtime | A managed identity-bearing Runtime accepts a session and streams events | **Observed.** A live session returned streamed events through the Gateway-bound deployment. |
| Memory Bank | Durable context and an approved exception survive process restart and suppress a later matching opaque finding | **Implemented and integration-tested.** Managed Memory endpoint is live; no claim that a wall-clock week elapsed during testing. |
| Agent Identity | The write-scoped agent is denied a real IAM read while the read-scoped agent succeeds | **Observed.** Redacted denial is [evidence 03](../../assets/evidence/03-escalation-agent-denied.md). |
| Agent Gateway | Runtime is Gateway-bound, IAP is fail-closed, and no production direct-peer credential remains | **Deployed and verified, with one open defect.** Fleet verifier checks Gateway policy and dispatcher bypass removal. IAP also denies a *catalogued* destination called from inside the Runtime — Model Armor's regional endpoint — with the endpoint registered and `roles/iap.egressor` held. Refusing is observed; correctly admitting from the Runtime is not. Tracked as D2 in [09-capture-backlog.md](../../submission/planning/09-capture-backlog.md). |
| Model Armor | Injection is refused by the managed template; unavailable screening also refuses | **Observed and tested.** Direct managed refusal is [evidence 01](../../assets/evidence/01-model-armor-block.md); callback/refusal seams are covered. |
| Agent Observability | Payload-free correlated actions are retained and operational signals are alertable | **Deployed and verified.** Regional sink/bucket, four metrics, five policies, and dashboard are live. |

## Two different kinds of proof

Reasoning traces explain a run; compliance audit records establish what actions occurred. Bastion
configures both and never treats a sampled trace as the retained audit record. Audit events are
payload-free and correlate by invocation/event ID.

## Submission artifact constraints

| Artifact | Closure rule |
|---|---|
| Architecture image | Generated variants match reviewed SVG masters and measured GCP counts |
| Spin-up instructions | Python 3.12 Windows bootstrap uses explicit project/region/engine inputs |
| Deployment proof | Count-only capture plus live verifier and smoke results |
| Demo video | Under four minutes, public, and shows load-bearing proof without sensitive data |

The first three are repository-complete. Video publication and Devpost form submission remain
human publication tasks and are not infrastructure defects.

## Consequences

Documentation must use **implemented**, **deployed**, **observed**, and **not claimed** precisely.
The evidence index is [assets/README.md](../../assets/README.md), the deployment inventory is
[gcp-state.json](../../assets/architecture/gcp-state.json), and the handoff checklist is
[submission/SUBMISSION.md](../../submission/SUBMISSION.md).
