# Bastion — Devpost “My Project” worksheet

- **Hackathon:** All Things Agentic Hackathon
- **Track:** Fortified Enterprise Fleet
- **Submission owner:** Arjun Ganesh
- **Local status:** Drafting only — nothing in this file has been submitted or published.
- **Last reconciled:** 2026-08-27

- **Live Devpost draft:** <https://devpost.com/software/bastion-pfuy71>
- **Read-only check on 2026-08-27:** `submission_draft`; no submission timestamp; the live video
  field is empty. No Devpost write was made during this check.

This is the field-by-field source for the Devpost form shown in the four screenshots under
`.tmp/devpost-my-project-form-questions/`. Use it while filling the live form; do not substitute
mutable counts or links without the final checks listed at the end.

## Project Overview

### Project name

```text
Bastion
```

### Elevator pitch

149/200 characters:

```text
A private fleet of catalogued agents that audits live GCP IAM, remembers human decisions, and routes minimized findings without gaining write access.
```

### Thumbnail

- Required format: JPG, PNG, or GIF; maximum 5 MB; Devpost recommends 3:2.
- Prepared asset: `assets/brand/devpost-thumbnail-3x2.png`.
- Alt text: `Bastion: catalogued agents, durable context, and governed production access.`
- Upload manually only after opening the file and confirming the final crop.

## Project Details

### About the project

Paste the contents of [`submission/DEVPOST_README.md`](submission/DEVPOST_README.md). It is a
judge-facing submission narrative, not a mirror of the repository README. The repository README
remains the engineering source of truth; the Devpost version leads with value, proof, and limits.

The “How we built it” section explicitly records that the public GEAR badge was earned on August
10 before Bastion work began on August 15. It presents the badge as preparation—not as project
work, evidence, or a scoring bonus—and separates it from the individual-contribution response.

### Built with

Use no more than 25 tags. These are 24:

```text
Gemini 3.5 Flash, Vertex AI, Google ADK, A2A, Agent Runtime, Agent Identity,
Agent Gateway, Agent Registry, Identity-Aware Proxy, Memory Bank, Model Armor,
Cloud Run, Firestore, Pub/Sub, Eventarc, Cloud Asset Inventory, Cloud Logging,
Cloud Monitoring, Cloud Trace, Secret Manager, Workload Identity Federation,
Python, pytest, Vercel
```

Cloud Build and Artifact Registry are enabled and are genuinely used by `infrastructure/deploy.sh`,
but they are commodity build plumbing rather than an enforcement or observability boundary, so the
last slot stays empty rather than being spent on them. Cloud Storage is deliberately absent: the
retained audit bucket is a **Cloud Logging** bucket, so `Cloud Logging` already covers it and a
storage tag would overclaim.

### Try it out

1. Public evidence console: <https://bastion.arjunganesh.dev/>
2. Public repository: <https://github.com/iarjunganesh/bastion>

The hosted site is a static, sanitized evidence plane. It is intentionally not a public route to
the IAM-private production fleet.

### Image gallery

Upload only the five final files defined in
[`submission/CAPTURE_RUNBOOK.md`](submission/CAPTURE_RUNBOOK.md), in this order:

1. `01-enterprise-fleet-architecture.png`
2. `02-governed-agent-catalog.png`
3. `03-production-iam-routing.png`
4. `04-enforced-security-boundary.png`
5. `05-durable-context-and-audit.png`

All five exist as of 2026-08-27, are 1920×1080 dark PNGs under 1 MB each, and pass
`python scripts/redact_evidence.py --check`. Three carry narrowed captions because the panels they
originally planned were not captured; the exact wording to use is in
[`submission/CAPTURE_RUNBOOK.md`](submission/CAPTURE_RUNBOOK.md).

Each must be JPG, PNG, or GIF, no more than 5 MB, readable as a thumbnail, and free of private
origins, principals, tokens, prompts, responses, and raw IAM policy data.

### Demo video

```text
TODO — public YouTube or Vimeo URL after recording and signed-out verification
```

Requirements: public, English narration or English subtitles, under four minutes, live behavior,
and visible proof that the backend runs on Google Cloud. Follow
[`submission/DEMO_SCRIPT.md`](submission/DEMO_SCRIPT.md).

## Additional Info

### Created by — Describe your contribution

350 characters:

```text
I conceived, designed, and built Bastion as an individual project: the three-agent ADK/A2A workflow, deterministic IAM and delivery gates, durable state, identity and security controls, GCP deployment, tests, evidence console, architecture, documentation, and reproducibility proof. I also reported the deployed ADK A2A state-boundary issue upstream.
```

### Sponsor and special-prize selections

- Primary category: `Fortified Enterprise Fleet`
- Submitter Type: `Individuals`
- Country: `Sweden`
- Organization name: `N/A — submitting as an individual`
- Project start date: `08-15-26`

### Code repository

```text
https://github.com/iarjunganesh/bastion
```

### Reproducible testing instructions provided?

```text
Yes
```

### Hosted project URL

```text
https://bastion.arjunganesh.dev/
```

### Testing instructions

245/255 characters:

```text
Python 3.12: git clone https://github.com/iarjunganesh/bastion; cd bastion; py -3.12 -m venv .venv; .venv\Scripts\python -m pip install -r requirements-dev.txt; .venv\Scripts\python -m pytest tests --cov --cov-fail-under=100. Full gates: README.
```

The clean-clone measurement and environment notes are in
[`submission/planning/10-reproducibility.md`](submission/planning/10-reproducibility.md).

### Google SDKs used

Select:

```text
ADK
```

### Google Cloud services used

Select the available form choices:

```text
Cloud Run
Firestore
Pub/Sub
```

The write-up also identifies Eventarc, Cloud Asset Inventory, Vertex AI, Secret Manager, Cloud
Logging, Cloud Trace, Workload Identity Federation, and the managed enterprise-agent services.

### Architecture diagram

- Upload: `assets/architecture/enterprise-fleet-architecture-dark.png`
- Format: PNG, 1920×1080, below the 35 MB form limit.
- The draft already carries the dark architecture GIF, which shows the same diagram with motion
  and needs no replacement; the dark PNG is the static equivalent if the field rejects a GIF.
- Dark, not light, so the required image matches the five dark gallery images beside it.
- The source SVG, both theme variants, and both stills are generated and checked in CI.

### Startup prize fields

Leave the startup organization and corporate-email fields blank unless Devpost requires a literal
value for an individual entry. Do not invent an incorporated organization.

### Google AI models used

```text
Gemini 3.5 Flash via Vertex AI
```

Do not select or claim Gemma, Veo, or Lyria unless one is genuinely integrated and demonstrated
before submission.

### Bonus: public content URL

```text
TODO — publish submission/ARTICLE_DRAFT.md, then paste its public URL
```

The published article must retain the hackathon disclosure in the draft.

### Bonus: social post URL

```text
TODO — publish one approved variant from submission/SOCIAL_DRAFT.md, then paste its public URL
```

The public post must contain `#AllThingsAgenticHackathon` exactly.

## How We Used AI

Gemini 3.5 Flash contributes bounded explanations for deterministic IAM findings. It does not
choose the findings, risk scores, owning departments, or required deliveries. Bastion validates
the model output field-by-field against canonical tool output, screens input and output, and fails
closed when required policy services are unavailable.

## How We Used Codex

Codex was used as an engineering collaborator for repository-wide implementation/evidence audits,
test and documentation consistency work, architecture asset iteration, clean-clone verification,
and submission preparation. The important discipline was separating implemented, tested,
deployed, and observed behavior so the public submission does not turn a test result into a live
claim.

## Known limitations to keep in the form and video

- Bastion is read-only with respect to IAM; it never remediates or revokes a binding.
- The observed human-decision gap is three days across deployments and restarts, not a literal
  week; expiry firing is test-only.
- Gemini uses the Vertex AI `global` endpoint, so Bastion makes no end-to-end EU residency claim.
- The retained audit bucket has a 365-day policy but is not WORM/immutable.
- The current snapshot is event-driven and claims no deployed recurring Scheduler job.
- Two observations remain deliberately open: a managed Gateway refusal of an unregistered caller,
  and a watched timeout/retry/dead-letter sequence. Use the narrower wording in
  [`submission/planning/11-claim-matrix.md`](submission/planning/11-claim-matrix.md) for both, and
  never call the instance cap or delivery bound a per-caller rate limit. The agent-mediated Model
  Armor refusal and the current-route Cloud Trace chain closed on 2026-08-25 and may now be stated
  as observed.

## Final manual fields and gates

- [ ] Open and approve the 3:2 thumbnail.
- [x] Capture and approve all five gallery images. Composed 2026-08-27, all dark, all passing
      `python scripts/redact_evidence.py --check`; three captions narrowed — see the runbook.
- [ ] Record, redact-review, upload, and verify the video while signed out.
- [ ] Refresh mutable GCP counts and upstream issue/PR status. Checked 2026-08-27: issue #6854
      open with seven comments, PR #6859 open and unmerged, PR #6862 **closed unmerged**. Nothing
      is merged. A Google collaborator asked for a reproduction to test #6859 and one was supplied
      on 2026-08-27; their "can be merged if the reviewer approves" is conditional, not approval.
- [ ] Publish and verify the optional article and social post, or leave both bonus fields blank.
- [ ] Paste/save every field in Devpost and confirm the selected category.
- [ ] Re-open every public link while signed out.
- [ ] Ask for an explicit final go/no-go before any submission action.

## Draft completeness

The text fields, tags, links, testing instructions, service selections, architecture upload, AI
usage, Codex usage, and limitations are prepared. The remaining blanks are deliberately human
publication artifacts: five captures, one video URL, and the optional article/social URLs.
