# Bastion — Release Tag Plan (v0.1.0 → v1.0.0)

**Written Aug 13, 2026. 18 days to the Aug 31, 5:00 PM PT deadline.**

Companion to `03-build-plan.md`: that document says what gets built on which day, this one says what gets *tagged*. A tag is not a checkpoint in the work — it is a claim that something is now true and demonstrable. If you can't screenshot it or run it in front of a judge, it isn't a minor bump.

The repo is **still not initialized** as of Aug 14 — deliberately, by the author's instruction. `git init` and `v0.1.0` remain the first actions, and the first commit must land inside the submission period (Aug 3–31) to satisfy the Stage 1 pass/fail row in `00-judging-matrix.md`. The window is not the constraint; the ladder below is, because every tag after `v0.1.0` claims something that must already be true.

## Conventions

- **Annotated tags only.** `git tag -a v0.4.0 -m "..."`. Lightweight tags carry no author, date, or message, and the release history is itself evidence of build cadence inside the submission window.
- **The tag message names what became true**, not what changed. "the malicious ticket is blocked before it reaches Gemini" — not "add model_armor module".
- **Minor bump = a new capability a judge could watch.** Patch = a fix, a re-measurement, or captured evidence for a capability that already exists.
- **Never re-point a tag.** If `v0.6.0` was wrong, `v0.6.1` fixes it. A moved tag makes every earlier claim about that tag unverifiable.
- **Tag the same day the thing works.** Batched end-of-week tagging loses the timeline, and the timeline is part of what the history proves.
- **A slipped day does not shift the ladder.** The version after a slip is still the next number; only the date moves. Dates below are targets, versions are commitments.

## The ladder

| Tag | Target | The claim it makes | Build-plan milestone |
|---|---|---|---|
| `v0.1.0` | ~~Thu Aug 13~~ | Scaffold, docs, and a hello-world **ADK** agent calling Gemini 3.5 Flash through Vertex AI | **Slipped.** The scaffold and docs exist; the ADK call does not, and it is what the tag claims |
| `v0.2.0` | Fri Aug 14 | The GEAP decision recorded ([ADR-003](../../docs/adr/003-pillars-on-geap.md) ✅); real IAM policy pulled from a live project | Fri — commit to a path |
| `v0.3.0` | Sat Aug 15 | Access Auditor produces real findings from the real IAM policy — broad roles, `roles/owner`, stale service accounts | Weekend — core loop |
| `v0.4.0` | Sun Aug 16 | **One full investigation runs start to finish against real IAM data**, orchestrated, with state visible in Firestore/GEAP | **Sunday-night milestone** |
| `v0.5.0` | Mon Aug 17 | Agent Registry: all three agents registered with name, version, owner, scope | Pillar |
| `v0.6.0` | Tue Aug 18 | Agent Identity: three scoped service accounts, and **a mis-scoped call provably fails** | Pillar (the denial screenshot lives here) |
| `v0.7.0` | Wed Aug 19 | Agent Gateway: registration check and call logging, nothing more | Pillar (thin by design) |
| `v0.8.0` | Thu Aug 20 | The prompt-injection attempt is blocked before it reaches Gemini | Pillar — **highest-risk tag** |
| `v0.9.0` | Fri Aug 21 | Observability into Cloud Trace, and Memory Bank recalls last week's approved exception instead of re-flagging it | **Friday milestone: every pillar has an artifact** |
| `v0.9.1` | Sun Aug 23 | The fleet survives a sub-agent timing out — retry, then escalate to a human surface | Failure tolerance (directly graded, 30% criterion) |
| `v0.9.2` | Sun Aug 23 | Architecture diagram rendered as an image; README spin-up reproducible by someone who has never seen the repo | **Code freeze** — after this, changes are evidence and prose |
| `v0.9.3` | Wed Aug 26 | The demo is recorded and public, and the hosted URL is live | Video + hosted judge path |
| `v0.9.4` | Fri Aug 28 | Cold self-scoring pass against `00-judging-matrix.md` applied; blog and social posts live | Bonus points + the fixes that pass exposes |
| `v1.0.0` | **Sat Aug 29** | Submission-final | Submit two days early |

Fourteen tags across eighteen days — comfortable, not forced. (An earlier version justified the cadence by comparing it to two unrelated repositories by name. Nothing in this repository should reference a project a judge cannot open.)

## The two tags most likely to move

**`v0.8.0` — Model Armor.** The build plan sets a hard cutoff of Thursday Aug 20 and names a fallback (heuristic plus a Gemini yes/no injection check). The tag makes the claim *"the injection is blocked"*, which is deliberately implementation-neutral: the fallback earns `v0.8.0` exactly as the managed service does. What must not happen is `v0.8.0` slipping into Friday and taking Observability and Memory Bank down with it. If Thursday night arrives with nothing blocking, tag the fallback and move.

**`v0.9.2` as code freeze.** Everything after it is recording, writing, and scoring. If work is still landing in the code after Aug 23, the plan's own checkpoint applies — cut to two agents and protect the video. In that case `v0.9.1` becomes the last feature tag and the ladder continues unchanged from `v0.9.2`.

## Contingency

`v1.0.0` gets cut on Aug 29 from whatever exists on Aug 29. It is a submission marker, not a quality bar — do not withhold it because a pillar came out thinner than planned. If something material lands between the submission and the deadline, it is `v1.0.1`, tagged and noted in the Devpost description, not a re-pointed `v1.0.0`.

Patch numbers stay free for exactly this: `v0.4.1`, `v0.6.1`, and so on, whenever a demonstrated capability turns out to be broken. Reaching for a patch tag is normal and is cheaper than letting a broken claim stand in the history.

## Today

```bash
git init
git add -A
git commit -m "initial scaffold: seven pillars, three agents, hackathon docs"
git tag -a v0.1.0 -m "v0.1.0 — scaffold, and Gemini 3.5 Flash answering through Vertex AI"
```

The tag comes after the hello-world ADK call actually returns, not before. That is the whole discipline in one line: the tag follows the proof.
