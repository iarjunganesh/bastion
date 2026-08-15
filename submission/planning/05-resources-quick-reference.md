# Bastion — Hackathon Resources Quick Reference

Consolidated from the hackathon's Resources page. Keep this open during Week 1.

## GEAR vs. GEAP — don't confuse these

| | GEAR | GEAP |
|---|---|---|
| Full name | Gemini Enterprise Agent **Ready** | Gemini Enterprise Agent **Platform** |
| What it is | Free skilling/training program | Actual product/toolkit for building agents |
| Cost | Free, no prerequisites | Usage billed against your GCP project (covered by the $150 credit) |
| Contains | 35 monthly Google Skills lab credits, ADK training, skill badges | Agent Registry, Agent Runtime, Memory Bank, Identity, Gateway, guardrails, Observability |
| Action | Sign up via Google Developer Program profile — 10 minutes. **Still outstanding** | ✅ **Decided Aug 14** — a backend behind ADK's service interfaces, not a fork ([ADR-003](../../docs/adr/003-pillars-on-geap.md)) |

## Credits

- ✅ **Received and redeemed** (Aug 12–13). Billing identifiers and balances remain private.
- The credit form URL recorded here previously differed from the one in [`../DEVPOST.md`](../DEVPOST.md) — two files, two URLs, one of them wrong. Moot now that the credit has landed, and the canonical capture is DEVPOST.md.
- Free trial as a backup/supplement: <https://cloud.google.com/free>

## Webinars (all times PT, each offered twice — morning and evening slot)

| Date | Title | Relevance to Bastion |
|---|---|---|
| Aug 11, 8:30–10:00 AM / 9:00–10:30 PM | Architecting Multi-Agent Teams: Three Orchestration Patterns of ADK | High — watch before finalizing the Orchestrator design (Day 0–1) |
| Aug 13, 9:00–10:30 AM / PM | Build a Long-Running Agent: Persistent Workflows with ADK | High — crash recovery/idempotency directly feeds the Orchestrator's retry logic (Week 1) |
| Aug 20, 9:00–10:30 AM / PM | Build a Self-Evolving Agent: Autonomous Self-Improvement | Low — not in scope for this track's judging matrix; skip unless ahead of schedule |
| Aug 27, 9:00–10:30 AM / PM | Architecting Agent Memory: Session State, Vector Search, Managed Cloud Memory | Medium, but **timing is a trap** — this airs only 4 days before submission, well after Memory Bank must already be working (Week 2). Don't gate the build on it; watch for refinement only if time allows. |

## Getting unstuck

- Devpost Discord (peer help)
- Hackathon Discussion Forum
- FAQs page — covers credits, required tech, submission questions specifically
- Webinars, live or recorded

## Build-your-agent reference links (for whoever's doing the actual coding)

- Gemini API & Google AI Studio — models, quickstarts, multimodal guides
- Agent Development Kit (ADK): github.com/google/adk-python
- Antigravity SDK, Genkit — alternative agent frameworks (not used here; ADK chosen for Bastion)
- Cloud Run — deploy, scales to zero when idle
- Firestore — agent state/memory, behind ADK's `BaseMemoryService`
- GEAP docs: platform overview, docs home, Agent Runtime docs, Memory Bank docs, announcement blog

## Cost tips (folded into `01-architecture.md`'s cost strategy section — repeated here for quick lookup)

`gemini-3.5-flash` on the `global` location for every call, no Pro tier (ADR-004) · min-instances=0 · set a max-instances cap · no dedicated always-on vector DB · keep stored state light · budget alerts on Day 0 · auth-protect public Cloud Run URLs

**One cost tip is deliberately not followed.** The organizers say to tear down after recording; Bastion keeps services up through the Sept 1 – Oct 1 judging window, because a hosted URL is an encouraged submission field and an idle scale-to-zero service bills nothing. Every other tip is followed.
