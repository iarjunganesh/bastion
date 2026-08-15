# All Things Agentic Hackathon — the source of truth

Captured on **2026-08-13** from every tab of
[allthingsagentichackathon.devpost.com](https://allthingsagentichackathon.devpost.com/):

| Tab | Captured | Notes |
|---|---|---|
| [Overview](https://allthingsagentichackathon.devpost.com/) | ✅ | Tracks, criteria, prizes, required stack |
| [Rules](https://allthingsagentichackathon.devpost.com/rules) | ✅ | Eligibility, submission contents, IP, governing law |
| [Resources](https://allthingsagentichackathon.devpost.com/resources) | ✅ | Credits, webinars, GEAR, tooling, cost tips |
| [Updates](https://allthingsagentichackathon.devpost.com/updates) | ✅ | Three posts, all captured below |
| [Participants](https://allthingsagentichackathon.devpost.com/participants) | ✅ | Count only — no rules stated there |
| `details/prizes`, `details/fortified-enterprise-fleet` | — | **404** — no separate prize or track-detail pages exist |

This file is the requirement, not the plan. It is quoted rather than paraphrased so that
every claim Bastion makes can be traced back to a line here.

**The overview and the rules page do not agree**, and the difference is not cosmetic: the
rules page still uses three retired track names and states each judging criterion in its own
words, including sub-questions that appear nowhere on the overview. Both are captured below
under [Judging](#judging). Where they conflict, satisfy the union rather than picking one.

Bastion's response to each requirement is in
[`planning/00-judging-matrix.md`](planning/00-judging-matrix.md); what has and has not been
earned is in [`SUBMISSION.md`](SUBMISSION.md).

**Re-verify this file before submitting.** Devpost pages change during a hackathon — the
participant count, the prize pool, and the criteria wording have all moved once already.

---

## At a glance

| | |
|---|---|
| Name | **All Things Agentic Hackathon: Ready, Set, Agent!** |
| Tagline | *"Build next-generation agents that run in the background, handle the heavy lifting of massive datasets, and automate complex workflows asynchronously."* |
| Organizer | Google, managed by Devpost |
| Format | Online, public |
| Prize pool | **$180,000** in cash, plus Google Cloud credits on every prize |
| Participants | **2,327** as of 2026-08-13 (963 → 2,208 → 2,327; still climbing) |
| Credits provided | $150 in Google Cloud credits per participant |
| **Bastion's track** | **The Fortified Enterprise Fleet** |

## Dates

| Milestone | When |
|---|---|
| Submission period opens | **Aug 3, 2026**, 09:00 PT |
| **Submission deadline** | **Aug 31, 2026, 5:00 PM PT** |
| Judging period | **Sept 1 – Oct 1, 2026** |
| Winners announced | On or around **Oct 8, 2026** |
| Winner response window | **2 days** from first notification, or disqualified |

The month-long judging window is why Bastion's services stay up rather than being torn down
after recording — an idle scale-to-zero service costs nothing across it.

---

## The mission

> Build one autonomous AI agent using Gemini and Google Cloud — moving beyond static chatbots
> toward systems that *"take a goal, make a plan, and actually carry it out — pulling
> information, making decisions, and completing multi-step tasks on their own."*

---

## The three tracks

A project may enter **exactly one**.

### 1. The Taskmaster

> *"Build a complete workflow, not just a chatbot. Don't just make an agent that writes text.
> Make one that takes action. Find a messy, multi-step chore in your job, classes, or personal
> life. Build an agent that handles the details, sends the right info to the right places, and
> proves it can do the heavy lifting for you."*

### 2. The Collaborative Partner

> *"Build an agent that leads the way and takes notes. It should ask clarifying questions,
> guide the user step-by-step, and have a clear way to capture feedback, so it constantly
> adapts to the user's unique way of thinking."*

### 3. The Fortified Enterprise Fleet — **Bastion's track**

> *"Build a scalable network of institutional agents that hook into official enterprise
> infrastructure. Teams must demonstrate how agents are cataloged for cross-department use, how
> they safely maintain context across weeks of asynchronous operations, and how they interact
> with production data without violating enterprise compliance, data sovereignty, or security
> policies."*

Three demonstrations are demanded by that sentence, and each is a separate obligation:

1. **Agents cataloged for cross-department use**
2. **Safely maintain context across weeks of asynchronous operations**
3. **Interact with production data without violating enterprise compliance, data sovereignty,
   or security policies**

#### The seven components, in the brief's four groups

| Group | Component | The brief's definition |
|---|---|---|
| **Discovery & Lifecycle** | Agent Registry | *"the central repository for publishing, versioning, and discovering enterprise-approved agents"* |
| **Core Execution & State** | Agent Runtime | *"for long-running, asynchronous background execution"* |
| **Core Execution & State** | Memory Bank | *"for persistent, secure cross-session context over extended timelines"* |
| **Security & Governance** | Agent Identity | *"for zero-trust access control"* |
| **Security & Governance** | Agent Gateway | *"for unified routing and policy enforcement"* |
| **Security & Governance** | Model Armor | *"inline guardrails to block prompt injection, tool poisoning, and PII leaks"* |
| **Telemetry** | Agent Observability | *"OpenTelemetry-compliant audit logs and end-to-end reasoning chain traces"* |

**Recommended tech:** Gemini Enterprise Agent Platform (GEAP).

Two clauses are easy to under-read, and Bastion calls them out for that reason:
**tool poisoning** is a named threat distinct from prompt injection, and **audit logs** are
named separately from **reasoning chain traces**. Each needs its own artifact.

---

## Mandatory stack — Stage 1, pass/fail

Every project must include all three:

1. **"Gemini 3.5 or newer accessed through Gemini API or Vertex AI"**
2. **"At least one Google Agent Framework: Google ADK, GenAI SDK, Antigravity SDK or GenKit"**
3. **"At least one Google Cloud infrastructure service (such as Cloud Run, Cloud SQL,
   Firestore, GKE, Pub/Sub)"**

Note the framework requirement names **four** acceptable options, not just ADK.

Also pass/fail: the project must be **newly created during the submission period**, any
pre-existing code must be **disclosed**, and the work must be *"the original work of the
Entrant"* and *"solely owned by the Entrant"*.

---

## What a submission must contain

| Item | Requirement |
|---|---|
| Category | Exactly one of the three tracks |
| **Hosted project URL** | *"A hosted project is highly encouraged"* — encouraged, not pass/fail |
| Text description | Features, functionality, technologies, data sources, findings |
| Code repository | GitHub, GitLab, or Bitbucket. If private, share with `testing@devpost.com` and `cloudhackathons@google.com` |
| **Spin-up instructions** | *"Step-by-step guide in your README.md explaining how to set up and run the project locally or deploy it to the cloud"* |
| **Architecture diagram** | *"Clear visual representation of your system (e.g., how Gemini connects to your backend, database, and frontend)"* — an image, not ASCII |
| **Demo video** | See below |

### Demo video

- **Length:** *"Should not be longer than 4 minutes. If it is longer than 4 minutes, only the
  first 4 minutes may be evaluated."*
- **Must contain:** a short overview of the problem, the value proposition, and a demo of the
  application in action.
- **Must prove Google Cloud:** *"Must demonstrate the backend is running on Google Cloud (ie:
  Google Cloud Console, Cloud Run dashboard, Vertex AI logs, URL of .run, etc)."*
- **Hosting:** public on **YouTube or Vimeo**.
- **Language:** English, or English subtitles.

> *"Judges are not required to test the Project and may choose to judge based solely on the
> text description, images, and video provided."*

That single line is why the video carries the submission, and why a hosted URL is a bonus
rather than a dependency.

---

## Judging

### Stage 1 — pass/fail

Baseline viability: does the submission meet the requirements above at all.

### Stage 2 — weighted scoring, 1–5 per criterion, then averaged

| Weight | Criterion | The exact wording |
|---|---|---|
| **40%** | Innovation & Operational Utility | *"How much real-world friction does the agent remove on its own? We reward autonomous, high-value action over simple chat — agents that make decisions and complete tasks with little to no hand-holding."* |
| **30%** | Architectural Discipline & Tech Stack | *"How sound are your engineering choices? We look at how you decouple systems, manage state and memory, secure credentials, and handle failures — robust, production-minded agents, not brittle scripts."* |
| **30%** | Demo & Production Readiness | *"How clearly do your video and repo prove it works? We want a live, unedited demo, a clean architecture diagram, reproducible setup, and visible proof it runs on Google Cloud."* |

### The rules page disagrees with the overview — read both

The overview's criteria wording (above) is not what the rules page carries. The rules page
states each criterion differently **and still uses three retired track names** —
*"The Continuous Action Engine"*, *"The Evolving Knowledge Engine"*, *"The Multi-Agent
Nexus"* — where the overview says Taskmaster, Collaborative Partner, and Fortified Enterprise
Fleet. Re-verified live on 2026-08-13. **The Multi-Agent Nexus is this track under its old
name.**

The rules page adds, verbatim:

| Criterion | The rules page's wording |
|---|---|
| Innovation & Operational Utility (40%) | *"Does the system eliminate real-world friction? Is the 'Twist' present? We are looking for high-value, autonomous execution over simple chat queries."* |
| Architectural Discipline (30%) | *"We are evaluating your engineering decisions, not just your ability to call an API. How well did your team decouple systems, manage state, and design robust, failure-tolerant agentic systems?"* |
| Demo & Production Readiness (30%) | *"The clarity of the technical documentation and the undeniable proof of execution in the video pitch."* |

**The "Twist" is never defined.** The word appears exactly once, in the 40% criterion, with no
explanation anywhere in the rules. Treat it as the unique angle of the entry — for Bastion, the
system auditing its own permissions — but do not assume a judge reads it that way.

The **Multi-Agent Nexus** sub-bullets are the closest thing to a scoring rubric for this
track, and none of them appears on the overview page:

> *"Is the task complex enough to warrant a multi-agents system? Does the system
> intelligently delegate tasks to specialized sub-agents? Did they build this for an
> 'Unlikely Hero' outside of standard corporate roles?"*
>
> *"Judges are looking for good use of agent workflows. Is there a clear, strictly enforced
> separation of concerns between agents? Is the inter-agent routing logic failure-tolerant
> (e.g., how does the system recover if a worker agent loops or returns a hallucination)?"*

What that means for Bastion, stated plainly:

| Sub-question | Bastion | Status |
|---|---|---|
| *"complex enough to warrant a multi-agents system?"* | Three agents with different data access; the Escalation Agent provably cannot read what it escalates | Answered by design |
| *"intelligently delegate to specialized sub-agents?"* | A `SequentialAgent` runs Auditor → policy step → Escalation, each an `LlmAgent` with its own tools. Agent Gateway is the designed call path and **is not provisioned** | ◐ Runs; the Gateway hop does not exist |
| *"strictly enforced separation of concerns between agents?"* | Enforced in **IAM**, not convention — the strongest answer available to this rubric. But the binding does not exist yet: the three agents share one identity as `sub_agents` of one process | The best card, **not yet played** |
| *"inter-agent routing logic failure-tolerant… if a worker agent loops or returns a hallucination"* | **Half answered.** Hallucination is bounded: detection is deterministic and runs before any model call, so a fabricated finding has no binding behind it. Retry is *not* — the hand-rolled backoff, circuit breaker and loop guard were deleted with `resilience.py` on 2026-08-15, and Agent Engine's managed retry needs a deployment that does not exist | ◐ Hallucination bounded; **retry unimplemented** |
| *"an 'Unlikely Hero' outside of standard corporate roles"* | Bastion is squarely a corporate compliance tool | **Does not fit** — appears aimed at the retired track framing |

No count of agents is required anywhere on either page. *"Multi-agents"* and *"sub-agents"*
are the only quantity words used, and three specialised agents satisfy both.

### Stage 3 — bonus points

| Bonus | Maximum |
|---|---|
| Published content — blog, podcast, or video — on a public platform | **0.2** |
| Social media post featuring the project with **#AllThingsAgenticHackathon** | **0.2** |
| Each additional Google AI model integrated (Gemma, Veo, Lyria) — 0.2 each | **0.6** |

**Maximum final score: 6.0** (5.0 scored + 1.0 bonus).

Bonuses reward additional Google **models**, not additional Google Cloud **services** — a
distinction worth remembering before adding infrastructure for score.

### Tiebreaker

Scores are compared *"on each criterion in the order listed"* — so **Innovation & Operational
Utility breaks ties first**. That is the strongest single argument for auditing real data.

---

## Prizes

Every prize carries Google Cloud credits alongside the cash. **A project is eligible for at
most one prize**, so these are alternative outcomes rather than additive.

| Prize | Cash | Credits | Winners | Bastion eligible? |
|---|---|---|---|---|
| **Grand Prize** | $50,000 | $5,000 | 1 | ✅ |
| **The Fortified Enterprise Fleet** | $20,000 | $2,000 | 1 | ✅ — Bastion's track |
| The Taskmaster | $20,000 | $2,000 | 1 | ❌ other track |
| The Collaborative Partner | $20,000 | $2,000 | 1 | ❌ other track |
| Startup Excellence | $20,000 | $5,000 | 1 | ❌ incorporated organizations only |
| **Individual / Hobbyist** | $10,000 | $1,000 | 2 | ✅ — solo entrant |
| **Best Architectural Design** | $5,000 | $1,000 | 2 | ✅ |
| **Best Multimodal UX** | $5,000 | $1,000 | 2 | ✅ |
| **Honorable Mentions** | $2,000 | $500 | 5 | ✅ |

Grand, Track, Startup, and Individual prizes also include a virtual coffee with the Google
team and a social promotion.

**Thirteen winning slots are open to this submission.** Eleven of them are not the Grand
Prize, so a strong-but-not-best entry still has realistic landing spots.

---

## Eligibility

- Above the age of majority in your jurisdiction (at least 20 in Taiwan).
- **Excluded residents:** Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan,
  Belarus, Russia.
- Not subject to U.S. export controls or sanctions.
- Not an employee, intern, or contractor of Google, Devpost, or related organizations, nor
  their immediate family.
- Internet access as of Aug 3, 2026.
- Governing law: **State of California**, with a binding arbitration requirement.

An entrant may submit more than one project, but each *"must be unique and substantially
different"*.

**Intellectual property:** the entrant retains ownership but grants Google a *"perpetual,
irrevocable, worldwide, royalty-free, and non-exclusive license"* for evaluation and
promotion.

---

## Resources tab

### Credits and support

| | |
|---|---|
| Cloud credits | **$150**, requested via <https://forms.gle/5PtXmw1dSbDnpYke9> |
| Free trial | <https://cloud.google.com/free> |
| Discord | <https://discord.gg/HP4BhW3hnp> |
| Discussion forum | <https://allthingsagentichackathon.devpost.com/forum_topics> |

### Webinars — August 2026

Each runs twice, morning and evening PT, to cover time zones. Both slots cover the same
material and include participant Q&A.

| Date | Session | Times (PT) |
|---|---|---|
| Aug 11 | *"Architecting Multi-Agent Teams: Mastering the Three Orchestration Patterns of ADK 2"* | 8:30–10:00 AM · 9:00–10:30 PM |
| **Aug 13** | *"Build a Long-Running Agent: Persistent Workflows"* | 9:00–10:30 AM · 9:00 PM |
| Aug 20 | *"Build a Self-Evolving Agent: Autonomous Self-Improvement"* | 9:00–10:30 AM · 9:00 PM |
| Aug 27 | *"Architecting Agent Memory"* | 9:00–10:30 AM · 9:00 PM |

Two of these land on Bastion's critical path. **Aug 13 — long-running agents** is the
Orchestrator's retry and idempotency problem. **Aug 27 — agent memory** is the exception store,
though it falls after the code freeze, so it is reference material rather than build input.

### GEAR programme

Free skilling initiative at <https://developers.google.com/program/gear>. Start with the
*"Introduction to Agents"* path. The badge is free and takes about ten minutes.

### Development tools named by the organizers

| Tool | Link |
|---|---|
| Gemini API · AI Studio | <https://ai.google.dev> · <https://aistudio.google.com> |
| **Agent Development Kit (ADK)** | <https://google.github.io/adk-docs> · <https://github.com/google/adk-python> |
| Genkit | <https://firebase.google.com/docs/genkit> |
| Cloud Run · Firestore | Deployment and state management |

### The organizers' cost-optimisation guidance

> Use Gemini Flash first, scale to zero, set instance caps, use serverless vector search,
> minimise storage, enable billing alerts, secure endpoints, and clean up resources after
> demos.

Bastion follows all of these except the last: services stay up through judging because a hosted
URL is an encouraged submission field and an idle scale-to-zero service bills nothing.

### The official Fortified Enterprise Fleet example

An **Enterprise Supply Chain Orchestrator**: discovered via Agent Registry, running a multi-week
vendor onboarding cycle, remembering negotiation data via Memory Bank, querying private ERP
inventory via Agent Identity, coordinating a logistics sub-agent via Agent Gateway, and
screening external email via Model Armor.

Bastion maps onto that exact shape in the access-governance domain — which is a signal the
concept fits the rubric's intent, and also a reason not to rename components to match their
example. The differentiation is the domain and the live attack beat.

---

## Updates tab

Three posts as of capture. Summarised, with anything that changes the plan called out.

**"4 live workshops are here — and the first one's tomorrow 🎓"** *(3 days before capture)* —
announces the four webinars above, each running twice for time zones, with time for questions.

**"Find your crew (or fly solo) — how's your agent coming along?"** *(6 days)* — entrants may
compete individually, as teams, or on behalf of organizations. The Participants tab supports
flagging availability, filtering, and direct messaging. **There is no maximum team size**, and
one person is designated Representative for the submission. Bastion is a solo entry, so this
only matters for the Individual/Hobbyist prize eligibility.

**"How to Plan your Project"** *(9 days)* — the organizers' suggested timeline: brainstorm in
week one, pick idea and track by **Aug 7**, sketch architecture by **Aug 10**, begin development
**Aug 10**. It stresses planning before building and reiterates that **an architecture sketch is
a required submission item**.

Bastion is behind that suggested timeline: development started Aug 13 rather than Aug 10. The
artifact the update names — an architecture image, not ASCII — now **exists**: Level 1 and
Level 2 are hand-authored 1920×1080 SVGs with light and dark variants and an animated GIF of
each, and Level 3 stays inline mermaid. Every one of them states its own build state in its own
text, and `scripts/check_docs.py` fails the build if one does not.

That disclosure requirement is why they can exist while nothing is deployed. An earlier
rendered diagram was deleted for showing Firestore, Cloud Run services, Pub/Sub topics and a
Model Armor template on a day the project held one resource, and this paragraph then claimed
for a while that no image could be drawn at all until something was deployed. Both were wrong
in opposite directions: a diagram of a *designed* flow is legitimate, provided it cannot be
mistaken for a diagram of a running one.

---

## Participants tab

**2,327 participants** at capture, up from 963 → 2,208 over the preceding days. No team
rules are stated on this tab; they are in Rules and in the update above.

## The organizers' own success tips

> Solve real, specific problems. Demonstrate autonomous action rather than conversation. Keep
> demo videos tight and live. Write clear project documentation for judges.

The first of those is the reason Bastion audits a live IAM policy rather than invented rows.

---

## Changes observed during the build

Tracked because a requirement that moved once can move again.

| | Earlier | As of 2026-08-13 |
|---|---|---|
| Participants | 963 → 2,208 | **2,327** |
| Grand Prize | $40,000 | **$50,000** (pool now $180,000) |
| Model guidance | "Gemini 3.5 or newer" | Overview names **Gemini 3.5 Flash** specifically; requirements still allow 3.5+ |
| Deployment at judging | Ambiguous | Hosted URL *"highly encouraged"*; judges need not test the project |
| Criteria wording | Rules page carried three stale track names | **Not resolved.** Re-verified 2026-08-13: the rules page still names *Continuous Action Engine / Evolving Knowledge Engine / Multi-Agent Nexus* and states each criterion differently from the overview. Both are captured above; treat the union as the requirement |
