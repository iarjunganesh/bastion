# Devpost submission handoff

**All Things Agentic Hackathon** · **Fortified Enterprise Fleet** · deadline Aug 31, 2026,
5:00 PM PT.

This file separates engineering closure from human publication. A checked engineering claim has
code, deployment, and evidence; an unchecked publication task must still be completed in Devpost
or a media platform.

## Pass/fail technology gates

- [x] Gemini 3.5 Flash through Vertex AI `global`; live calls captured in
      [evidence 02](../assets/evidence/02-gemini-investigation.md).
- [x] Google ADK 2.7.0; three ADK agents, A2A workers, plugins, tools, and managed Runtime.
- [x] Google Cloud infrastructure; measured deployment in
      [evidence 04](../assets/evidence/04-private-fleet-deployment.md).
- [x] Fortified Enterprise Fleet brief addressed across Registry, Runtime, Memory, Identity,
      Gateway, Model Armor, and Observability.
- [x] Public MIT-licensed repository with history inside the submission period.
- [x] Python 3.12 spin-up, bootstrap, verifier, smoke, rollback, and teardown instructions.
- [ ] Devpost category selected and all required fields saved.
- [ ] Public English demo video under four minutes.
- [ ] Architecture GIF/image uploaded to Devpost.
- [ ] Final submission sent before the deadline.

## Three track obligations

| Requirement | Closed by |
|---|---|
| Catalog agents for cross-department use | Managed Registry has the Runtime and two worker cards; cards contain owner/department/purpose/skill/classification/version/approval metadata; deterministic routing rejects unknown departments. |
| Safely maintain context across weeks of asynchronous operations | Firestore IDs/leases/retry/dedup, managed sessions and Memory Bank, expiring approved exceptions, five-attempt DLQ, and idempotent notification. Restart and simulated prior-week suppression are integration-tested; no wall-clock-week claim is made. |
| Use production data without violating policy | Read-only live IAM/Asset access; deterministic minimisation; opaque IDs; fail-closed Model Armor; post-model protected-data screen; separated identities; count-only private findings record; explicit regional/global disclosure. |

## Seven-pillar proof

- [x] **Registry:** three governed Bastion agent records and approved platform destinations.
- [x] **Runtime:** identity-bearing Python 3.12 managed Runtime streamed live events through its
      Gateway-bound configuration ([evidence 05](../assets/evidence/05-runtime-gateway.md)).
- [x] **Memory Bank:** managed endpoint live; restart, retrieval, suppression, expiry, stale-memory,
      and failure branches covered by integration/unit tests.
- [x] **Identity:** deployed Escalation identity denied IAM read while Auditor was permitted
      ([evidence 03](../assets/evidence/03-escalation-agent-denied.md)).
- [x] **Gateway:** IAP fail-closed policy and per-destination Runtime identity grants verified;
      dispatcher direct-peer credential and invoker grants removed.
- [x] **Model Armor:** managed template refused injection
      ([evidence 01](../assets/evidence/01-model-armor-block.md)); callback fail-closed behavior and
      protected-output screening tested.
- [x] **Observability:** payload-free audit lifecycle, retained regional sink/bucket, four metrics,
      five alerts, and operations dashboard ([evidence 07](../assets/evidence/07-observability.md)).

## Safety, durability, and failure proof

- [x] Missing/invalid risk fails closed.
- [x] Raw IAM member/binding data stops before the model; unsafe output stops before notification.
- [x] Fixed tool declarations and allowlists defend the tool-metadata boundary.
- [x] Worker timeout/malformed response, hallucinated arguments, Model Armor/dependency outage,
      notification failure, duplicate event, expired lease, retry, dead letter, and stale memory
      are exercised across populated unit, integration, security, and load suites.
- [x] Real findings endpoint denies anonymous traffic and collapses an authorized duplicate
      ([evidence 06](../assets/evidence/06-durable-findings.md)).
- [x] 161 tests pass with 100% statement and branch coverage under Python 3.12.
- [x] Ruff, formatting, mypy, dependency audit, secret scan, docs/version checks, and diagram
      determinism are release gates.
- [x] ADK deprecation/experimental risk consciously accepted and pinned in
      [ADR-005](../docs/adr/005-adk-as-the-agent-framework.md).

## Prerequisites and bonus

- [x] Hackathon credits/project available; sensitive account details omitted.
- [x] [Gemini Enterprise Agent Ready badge](https://developers.google.com/profile/badges/community/gear?u=iarjunganesh)
      claimed and linked from README.
- [ ] Devpost registration/submission ownership reconfirmed.
- [ ] Billing budget/anomaly notification reconfirmed in the console before final recording.
- [ ] Optional launch blog published with the hackathon disclosure.
- [ ] Optional social post published with `#AllThingsAgenticHackathon`.

## Do not claim until verified

The following claims are deliberately not made:

- no automated IAM remediation or permission write;
- no WORM/immutable audit storage—the 365-day bucket is unlocked;
- no end-to-end EU residency—Gemini uses Vertex AI `global`;
- no legal compliance certification;
- no historical 99% availability, latency, cost, or accuracy figure;
- no claim that a wall-clock week elapsed during the deterministic prior-week simulation;
- no claim that Model Armor alone prevents tool poisoning—the fixed tool and IAM boundaries do.

## Final publication pass

- [ ] Record the catalog → event → Runtime/Gateway → IAM denial → Armor refusal → idempotent review
      → audit dashboard story without exposing a principal or endpoint.
- [ ] Verify every Devpost number against `gcp-state.json` immediately before submission.
- [ ] Keep private services running through judging; do not expose an agent merely to create a
      public hosted-project URL.
- [ ] Run the complete local and live release gates, push `main`, and confirm GitHub Actions green.
- [ ] Create a release tag only if explicitly desired after the submission commit; no tag is
      required for engineering closure.
