# Devpost submission handoff

**All Things Agentic Hackathon** · Track: **Fortified Enterprise Fleet** ·
Deadline **Aug 31, 2026, 5:00 PM PT** · Target submission date **Sat Aug 29**.

Some proof points below are checked. A box gets checked when the thing has been observed working,
not when it has been built. Scoring detail lives in
[`planning/00-judging-matrix.md`](planning/00-judging-matrix.md).

## Stage 1 — pass/fail. Any unchecked box here is a disqualification

- [x] **Gemini 3.5 Flash through Vertex AI**, at the three call sites in
      [ADR-001](../docs/adr/001-real-iam-not-mock-data.md), with a request visible in the Vertex AI
      logs on camera. *Five model calls are captured in evidence 02.*
- [x] **Google ADK** — the three agents are ADK agents
      ([ADR-005](../docs/adr/005-adk-as-the-agent-framework.md)); three `LlmAgent`s execute under
      a `SequentialAgent` as of 2026-08-15.
- [x] At least one GCP infrastructure service in use — Cloud Asset Inventory reads the live
      IAM policy. Managed fleet deployment is still outstanding.
- [ ] The submission reasonably addresses the Fortified Enterprise Fleet challenge: all
      seven pillars present with a visible artifact each.
- [ ] Repository history starts **inside the submission period (Aug 3–31, 2026)**; any
      reused snippet is disclosed in the README.
- [ ] Repository public with a license, **or** shared with `testing@devpost.com` and
      `cloudhackathons@google.com`.
- [ ] Category on the Devpost form set to **Fortified Enterprise Fleet**.
- [ ] Demo video public on YouTube or Vimeo, **under 4:00**, English narration.
- [ ] Architecture diagram attached as an image.
- [ ] Spin-up instructions in the README, written for someone who has never seen the repo.

- [ ] **Hosted Project URL** — *"a hosted project is highly encouraged."* Not pass/fail, and
      judges *"are not required to test the Project."* Plan: stay live through the Sept 1 –
      Oct 1 judging window, which costs nothing at `min-instances=0`.
- [ ] Pre-existing code, if any, disclosed in the README.

## Prerequisites

- [x] Hackathon GCP credits received and redeemed (account identifiers intentionally omitted).
- [x] GCP project created, APIs enabled, **budget alert set before the first deploy**.
- [ ] GEAR badge claimed via the Google Developer Program profile.
- [ ] Devpost registration complete.

## The evidence each pillar owes

Each row is a screenshot or clip that must exist before recording. The plan for capturing
them is [`../assets/README.md`](../assets/README.md).

- [ ] **Registry** — three agents listed with name, version, owner, declared scope.
- [ ] **Runtime** — an investigation still in progress across a gap in time, not one
      synchronous run.
- [x] **Real IAM, end to end** — one investigation read the live policy through Cloud Asset
      Inventory and produced 2 findings, **observed 2026-08-15**
      ([evidence 02](../assets/evidence/02-gemini-investigation.md)). No fixture, no seeded overlay.
- [x] **Cross-department routing** — those 2 findings routed to **2 different owning teams**
      in the same run, rather than to one central inbox.
- [ ] **Memory Bank** — a prior week's approved exception recalled and *not* re-flagged.
- [x] **Identity** — a mis-scoped call **failing**. The denial itself is the artifact.
      Captured 2026-08-15: `escalation-agent-sa` is refused `projects.getIamPolicy` while
      `access-auditor-sa` is permitted the same call in the same moment
      ([evidence 03](../assets/evidence/03-escalation-agent-denied.md)). Produced by
      impersonation from a workstation, **not** by a deployed agent refused mid-run — that
      stronger version arrives with the deployment.
- [ ] **Gateway** — an inter-agent call logged as an A2A task, and three refusals shown:
      an unregistered caller, an undeclared skill, and a rate limit.
- [ ] **Audit trail** — the records for one investigation, correlated by `context_id`,
      including at least one refusal. A trail showing only successes proves nothing about
      the guardrails.
- [x] **Model Armor** — the malicious ticket blocked, **observed 2026-08-15** against the
      live `bastion-guardrail` template in `europe-west4`
      ([evidence 01](../assets/evidence/01-model-armor-block.md)). The managed service
      ran, not a fallback. **Still owed:** the same block observed *through an agent*,
      via ADK's `before_model_callback`, rather than by calling `screen_prompt` directly.
- [ ] **Tool poisoning** — each agent's tool set fixed at construction, the Escalation Agent
      holding no policy tool at all ([ADR-007](../docs/adr/007-tool-poisoning.md)). The brief
      names three threats; this is the one screening more text does not answer. Testable
      offline, so it is earnable before deployment.
- [ ] **Observability, part 1** — the full reasoning chain for one investigation in Cloud Trace.
- [ ] **Observability, part 2** — structured **audit logs** in Cloud Logging. The brief says
      *"audit logs **and** reasoning chain traces"*; a sampled trace that expires is not an
      audit record for a compliance product.
- [ ] **Real data** — the IAM policy dump the findings were derived from, redacted.
- [ ] **Failure tolerance** — a sub-agent timing out, retried, then escalated.

## Bonus points

- [ ] Blog post on dev.to or Medium, explicitly marked as created for the All Things
      Agentic Hackathon (+0.2).
- [ ] Social post with `#AllThingsAgenticHackathon` (+0.2).
- [ ] Additional Google models (Gemma, Veo, Lyria) — stretch only, not core scope.

## Before submitting

- [ ] Re-check the overview and rules pages. As of Aug 13 they **still disagree**: the rules
      page uses three retired track names and states each criterion in its own words, with
      sub-questions absent from the overview. Both are captured in
      [`DEVPOST.md`](DEVPOST.md#judging); satisfy the union. *Two planning documents claimed
      this was resolved; both are corrected. Where a planning file and the capture disagree,
      the capture wins.*
- [ ] Cold self-scoring pass against the judging matrix, as a judge who has never seen it.
- [ ] Every version number, URL, and figure in the README and Devpost prose matches what
      is actually deployed and tagged.
- [ ] Services confirmed **still running** and reachable at the hosted URL, since judging runs
      Sept 1 – Oct 1. They are deliberately not torn down; at `min-instances=0` that costs
      nothing, and teardown would forfeit a submission field to save nothing.

## Do not claim until verified

- That Model Armor blocked a ticket **inside an investigation**. A direct `screen_prompt`
  call was observed blocking prompt injection on 2026-08-15; the agent-mediated path is
  not yet run. Name which one a claim refers to.
- That Model Armor stops tool poisoning. Measured on 2026-08-15: it does **not** —
  `blocked=False` for the tool-poisoning sample. The tool allowlist is that control.
- That findings came from real IAM, for any finding that came from the seeded overlay.
- That an agent "cannot" access something, without the denial captured. The Escalation
  Agent's denial **is** now captured (evidence 03); no other such claim is.
- That memory recall works, without a run showing a prior exception suppressing a
  re-flag — a document describing the mechanism is not evidence that it fired.
- Any latency, cost, or accuracy figure without a captured run behind it.
- A pillar as complete because its folder exists. Each of the seven owes one observable
  proof, listed in [ADR-006](../docs/adr/006-pillar-coverage.md).
- That Bastion uses a Google agent framework, while `google-adk` is only a line in
  `requirements.txt`. This was claimed in the README and the judging matrix for a day; it is
  the most serious documentation defect the project has produced, because it asserted a
  pass/fail requirement the code did not meet.
