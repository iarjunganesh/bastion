# Bastion architecture decision records

These records capture decisions that constrain the implementation. They are short by design;
[`../ARCHITECTURE.md`](../ARCHITECTURE.md) explains how the decisions compose.

**The ground truth is [`../../submission/DEVPOST.md`](../../submission/DEVPOST.md)**, which
quotes the hackathon's overview, rules, and resources pages rather than paraphrasing them.
Every record below traces to a line there.

| ADR | Decision | Status |
| --- | --- | --- |
| [001](001-real-iam-not-mock-data.md) | Audit a real GCP IAM policy, not mock entitlement rows; detection stays deterministic | Accepted |
| [002](002-three-agents.md) | Three agents; policy enforcement inside the Orchestrator | Accepted |
| [003](003-pillars-on-geap.md) | All seven pillars run on their managed GEAP product; no reimplementation | Accepted; **amended 2026-08-15** |
| [004](004-flash-only-global-endpoint.md) | Gemini 3.5 Flash on `global`, no Pro tier; infrastructure in `europe-north2` | Accepted; **verified** against the live project |
| [005](005-adk-as-the-agent-framework.md) | **Google ADK** as the agent framework; A2A as the inter-agent contract | Accepted; **amended 2026-08-15** |
| [006](006-pillar-coverage.md) | One observable proof closes each of the seven pillars, and each submission artifact | Accepted |
| [007](007-tool-poisoning.md) | Tool poisoning defended at the tool-declaration boundary, not the prompt | Accepted |

## Why there are seven

**Thirteen records were cut to seven on 2026-08-15**, and the survivors renumbered `001`–`007`.
Six described a premise that had stopped existing: Model Armor's fallback (the service
shipped), the DIY registry and gateway (both are managed GEAP products), the A2A envelope
(`a2a-sdk` ships it). Their substance was merged rather than dropped — each survivor carries an
*"Absorbed record"* section naming what it took on and which number it came from.

This repository is days old and has no external citations, so contiguous numbering costs
nothing and reads as a considered set rather than the residue of one. **The reversal that is
worth reading is preserved in place**: [ADR-003](003-pillars-on-geap.md) records its own scope
error and corrects it, which is the point of keeping decision records at all.

## The pass/fail gates

The overview names three mandatory technologies:

| Gate | Record | State |
|---|---|---|
| Gemini 3.5+ via Gemini API or Vertex AI | [001](001-real-iam-not-mock-data.md) | ✅ **Met.** 5 model calls in one investigation, 2026-08-15 ([evidence 02](../../assets/evidence/02-gemini-investigation.md)) |
| One Google Agent Framework | [005](005-adk-as-the-agent-framework.md) | ✅ **Met.** ADK 2.7.0 — three `LlmAgent`s under a `SequentialAgent`, executed |
| One Google Cloud infrastructure service | [003](003-pillars-on-geap.md) | ✅ **Met.** Cloud Run, Firestore, Pub/Sub, Eventarc, Agent Engine, and Model Armor are deployed; live-policy and Armor evidence are retained |

**All three are met in code and live infrastructure.** The 2026-08-16 fleet adds an
identity-bearing managed Runtime, Gateway/IAP egress, two protected A2A workers, durable Eventarc
delivery, and retained payload-free operations telemetry. Evidence is indexed in
[`../../assets/README.md`](../../assets/README.md).

## Conventions

- **Renumbering is a deliberate, whole-set operation, never a one-off.** Records are cited
  from `README.md`, `CLAUDE.md`, source docstrings, and `scripts/check_docs.py`; the docs
  gate fails on any citation that does not resolve, which is what makes a sweep safe.
- **When implementation invalidates a decision, amend that record or add a new one in the same
  change.** The code and the decision history are never allowed to disagree quietly.
- **A record whose premise is gone is merged into the record that replaced it**, and the
  survivor names what it absorbed. A record that was *reversed* keeps its amendment history —
  the reasoning that was wrong is the part worth reading.
- Status is one of Proposed, Accepted, or Superseded, and carries the date it changed. Where a
  claim rests on a measurement, the record says what was measured and when.
