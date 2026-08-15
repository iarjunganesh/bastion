# Why Bastion Wins

Not for the judges — for us. Every feature has to answer yes to at least one of these before it gets built.

## What judges will remember

A live prompt-injection attack, on camera, getting blocked by Model Armor in real time. The block is real and captured ([evidence 01](../../assets/evidence/01-model-armor-block.md)). The second half of this clip — *the system then flagging the attack attempt itself as the real finding* — is **not implemented**, and describing it as a remembered moment before it exists is the habit this repository argues against.

The stronger clip may be the one nobody planned: the policy Bastion reads contains the service accounts Bastion runs under, and the default Compute Engine account holds `roles/editor` — an unseeded, genuinely real over-permission in its own project.

## Why this isn't a chatbot

Nothing about Bastion waits for a person to type a question. An investigation is triggered, runs across multiple agents, and only surfaces a human when there is something a human actually needs to decide. The chat-loop pattern never appears anywhere in the architecture.

**The durable admission path is deployed, but its strongest proof is still owed.** Eventarc
admits a Pub/Sub investigation into Firestore and Agent Engine session/memory; no Scheduler job
is provisioned. A retained cross-week replay, not the configuration itself, is the remaining
evidence for the second track demand.

## Why "enterprise" is earned, not decorative

Every one of the **seven** required pillars exists because access governance genuinely needs it — not because the rules said to include it. A registry matters because a security team actually would want to know what agents exist before trusting one. Zero-trust identity matters because a compromised agent shouldn't be able to read data outside its job. Observability matters because "we can't explain why the system made this decision" is disqualifying in a compliance product specifically, not just nice-to-have.

(The brief names seven. This line said six, inherited from a wrong header in `01-architecture.md`. Both are corrected; the count is worth getting right in a document arguing the pillars aren't decorative.)

## Why "Bastion"

A bastion is a fortified projecting structure — the part of a fortress built to see attacks coming and hold the line. It's a direct, non-cute match to the track name ("Fortified Enterprise Fleet") instead of a generic AI-product name, and it gives the demo a natural framing: "Bastion watches the walls so a human doesn't have to check every gate by hand."

## Multimodal UX angle (for the Best Multimodal UX bonus prize)

The Escalation Agent's output is a schema-limited, count-only review record in Bastion's private
Firestore-backed findings inbox. A public Firebase-hosted judge dashboard is a future submission
surface, not a deployed feature.

**Not a voice/audio digest.** An earlier version of this section proposed one. It would mean a second Google model, and [ADR-002](../../docs/adr/002-three-agents.md) fixed bonus scope: blog and social post in, additional models out. Adding a model to collect 0.2 is the same mistake as adding a service to lengthen the stack list, which [ADR-003](../../docs/adr/003-pillars-on-geap.md) already refuses. Best Multimodal UX is a prize to be *eligible* for, not one to bend the architecture toward.

## What we will not do

Add a vector database, a second LLM provider, or a general-purpose policy DSL just to look sophisticated. If it doesn't make the demo stronger or the architecture more defensible under the judging matrix, it's stretch-goal, not core scope.
