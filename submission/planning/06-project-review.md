# Bastion — Project Review (Aug 13, 2026, 18 days out)

An honest reassessment against the live hackathon page, not a pep talk.

## Correction: my earlier dates were wrong

The previous build plan was written as if today were Aug 10 and gave you "21 days." Today is **Aug 13** and you have **18 days**. Every date in `03-build-plan.md` has been shifted; the Day 0–1 setup block and the Aug 11 webinar are already in the past. That was my error, and it mattered — it inflated the schedule by three days at exactly the point where the schedule is the binding constraint.

## What changed on the hackathon page since we started

| | Before | Now |
|---|---|---|
| Participants | 963 | **2,327** (via 2,208) |
| Grand Prize | $40,000 | **$50,000** (total pool $180,000) |
| Model guidance | "Gemini 3.5 or newer" | Overview now says **"leveraging Gemini 3.5 Flash"** specifically (requirements still allow 3.5+) |
| Deployment at judging | Ambiguous | **Explicitly not required to be live** — proof of GCP deployment in video + repo is enough |
| Judging criteria wording | Rules page referenced three stale track names | **Still does.** This row said "cleaned up"; it was wrong. The overview is 40/30/30, the rules page states each criterion differently and still names *Continuous Action Engine / Evolving Knowledge Engine / Multi-Agent Nexus*. Both captured in [`../DEVPOST.md`](../DEVPOST.md#judging) — satisfy the union |

Three of these are actionable:

**The field more than doubled.** 2,327 participants, and registration is still open. Fortified Enterprise Fleet is still probably the thinnest of the three tracks, but "thin" is now relative to a much bigger pool. Differentiation matters more than it did a week ago.

**You don't have to keep it running.** This removes real cost pressure — your credit should be nowhere near exhausted.

> **Superseded later the same day.** A full read of the rules page found that a Hosted Project
> URL is a submission field described as *"highly encouraged"*, and that judging runs a full
> month (Sept 1 – Oct 1). Since an idle `min-instances=0` service bills nothing, teardown
> would forfeit a submission field to save nothing. The plan is now to **stay live through
> judging**; see `03-build-plan.md`. What remains true is the part that mattered: the video,
> not the deployment, carries the submission.

**Flash is explicitly blessed.** The Flash-first default in the architecture doc is now the officially suggested path, not just a cost hack.

## The biggest weakness in the current plan

**The mock entitlement dataset.**

Innovation & Operational Utility is 40% — the single largest criterion — and the page describes it as "how much real-world friction does the agent remove *on its own*." The hackathon's own tips say "solve a real, specific problem you actually have."

A fleet of governance agents auditing 30–50 hand-authored fake rows does not remove any real friction. It demonstrates architecture (the 30% criterion) while quietly failing the 40% one. Judges who have seen a hundred submissions will notice that the data is invented, and "enterprise" framing makes invented data *more* conspicuous, not less — there's no real enterprise behind it.

**The fix, and it's a good one:** audit your *actual GCP IAM policy* instead. You now have a real GCP project with real service accounts, real role bindings, and — once you deploy the three agents with their scoped service accounts — genuinely interesting access structure to reason about. One API call gives you real data; write it to a gitignored file rather than printing it, because it carries every principal in the project. Overly broad roles, unused service accounts, and `roles/owner` or `roles/editor` grants are real findings on a real system — and one already exists here unseeded, on the default Compute Engine service account.

That single change:

- Converts the 40% criterion from "simulated" to "real friction on real data"
- Costs you *less* work than authoring 50 fake rows
- Makes the demo more credible (judges recognize an IAM policy dump)
- Is self-referential in a way that's memorable: **Bastion audits the very cloud project it runs in**, including its own agents' permissions

Keep a small mock overlay only if you need to guarantee a specific finding appears on camera — but the primary data source should be real.

## Second concern: scope for 18 days, solo

Seven pillars, four agents, a gateway, OpenTelemetry, Model Armor, a demo video, an architecture diagram, a README, a blog post, and a social post — solo, in 18 days, while presumably also doing your normal life. That is a lot.

Recommended cuts, in order:

1. **Drop from 4 agents to 3.** Merge Policy Enforcer into the Orchestrator. Agent *count* is not graded; separation of concerns is, and three agents demonstrates it fine. Saves ~2 days.
2. **Gateway stays thin.** Registration check + logging, and no retries at the gateway layer — those live in the Orchestrator, next to the policy that acts on them ([ADR-002](../../docs/adr/002-three-agents.md)). It *does* carry rate limiting with eviction, which this line originally ruled out: an unbounded per-`agent_id` counter is a memory-exhaustion path, and `agent_id` is attacker-supplied.
3. **Escalation output: the dashboard.** Settled by [ADR-003](../../docs/adr/003-pillars-on-geap.md) — Slack is not among the twenty services, and the read-only findings API behind Firebase Hosting is already the judge path.
4. **Treat the blog post as Week 3 optional.** It's worth 0.2 and takes 2 hours; do it only if the demo video is already recorded.

What must *not* be cut: all seven pillars need at least a visible artifact, Model Armor's blocking moment, cross-session memory recall, and the video. Those are the scored items.

## What's still genuinely strong about this concept

- It maps cleanly onto Google's own published example for the track (supply chain orchestrator), which suggests the shape is what they're looking for
- The prompt-injection block is a real demo moment, not a slide
- Every pillar has an honest reason to exist in an access-governance product — nothing feels bolted on
- Solo entrants tend to avoid "enterprise fleet"; the structural advantage is real
- With the IAM change, the data is real, which very few hackathon submissions can claim

## Verdict

The concept is sound and worth continuing — with the mock data replaced by real GCP IAM, and the scope cut to 3 agents. The schedule is tight but workable if the core loop is running by Aug 20. If it isn't running by Aug 22, cut to 2 agents and protect the video instead.
