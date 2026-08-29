# Release and submission plan

## Hosted evidence pre-tag gate

Complete this before preparing `v0.3.0`; the public site is part of that release boundary.

**Observed 2026-08-23:** complete at
[`bastion.arjunganesh.dev`](https://bastion.arjunganesh.dev/). Signed-out HTTPS, canonical
metadata, strict headers, desktop/mobile layouts, light/dark themes, reduced motion, keyboard
focus, 404 behavior, external links, and browser network isolation passed.

1. Import `iarjunganesh/bastion` through Vercel's GitHub integration with production branch
   `main`, Framework Preset **Other**, and Root Directory `site`.
2. Enable **Include source files outside of the Root Directory in the Build Step** so
   `site/build.mjs` can copy only the reviewed assets allowlisted in `site/asset-manifest.json`.
3. Keep the build/output settings from `site/vercel.json`: `node build.mjs` and `dist`. Configure
   no environment variables, storage, functions, integrations, or Railway service.
4. Verify the first production `vercel.app` URL signed out, then add
   `bastion.arjunganesh.dev` under Project Settings → Domains.
5. At the authoritative DNS provider, add the exact CNAME host/value Vercel requests. Wait for
   domain validation and managed HTTPS; do not publish a guessed generic DNS value.
6. Verify the custom domain, canonical behavior, headers, 404, mobile/desktop layout, reduced
   motion, external links, and a browser network log containing no private GCP request. Only then
   add the URL to README and the Devpost draft.

The detailed dashboard checklist and local build commands are in
[`site/README.md`](../../site/README.md).

## Engineering release gate

1. Confirm `main` has only intended code, documentation, evidence, and user-owned visual changes.
2. Run Ruff, format, mypy, pytest/coverage, dependency audit, secret scan, docs/version checks, and
   diagram verification under Python 3.12.
3. Run live fleet verifier and production smoke with explicit regions/engine ID.
4. Confirm rollback and teardown dry runs list only exact Bastion targets.
5. Recapture count-only GCP state and check all Markdown figures/claims against it.
6. Commit only the intended post-`v0.2.1` changes; do not amend, squash, or move an existing tag.
7. Push `main` and verify GitHub Actions green.

## Submission gate

1. Re-read [DEVPOST.md](../DEVPOST.md) and fill the official form, category, links, and disclosures.
2. Publish a public English demo under four minutes.
3. Upload the architecture image/GIF and verify legibility at Devpost size.
4. Confirm the repository and services remain available through judging.
5. Submit before Aug 31, 2026, 5:00 PM PT.

A release tag is a separate, explicit decision after the release commit and changelog are
verified—never a side effect of an engineering push. The existing decisions are `v0.1.0`,
`v0.2.0` carrying the seven deployed-fleet defects found after it, and `v0.2.1` carrying the
escalation hand-off fix.

`v0.3.0` shipped the public evidence surface, keyless deployment, release-log redaction, a
measured request-path visual, and new documentation and CI enforcement.

## v0.4.0 — deterministic delivery, deployed and re-verified

Changes after `v0.3.0`: P0.1 (Auditor fidelity validator), P0.2 (deterministic Escalation Agent,
replacing the `LlmAgent`), and P0.3 (`escalation_gate` completion confirmation) — the plan's own
"only mandatory new code" for this phase. Deployed to `bastion-fleet-2026` (both the four Cloud
Run services via `deploy.sh` **and** the managed Agent Runtime via
`infrastructure.deploy_agent_runtime` — a two-part deployment surface this release discovered the
hard way, see [ADR-012](../../docs/adr/012-structured-findings-across-a2a.md)'s 2026-08-23
amendment) and confirmed on a real triggered investigation: `escalation_gate` passing, and the
approved exception still correctly suppressing its finding. Also closed in the same tag:
P0.4 (live re-verification), P0.5 (event-driven wording confirmed, no Scheduler added), P1.1
(scalability wording), P1.2 (coverage-scope wording), and P1.4 (claim reconciliation across
ADRs/ledgers) — plus a full sweep of every tracked Markdown file for staleness.

1. commit the P0.1–P0.3 code, tests, and every reconciled document;
2. run every offline, live, and version-upstream gate;
3. change the changelog heading from `Unreleased` to `0.4.0` and bump `pyproject.toml`;
4. commit and push the release metadata, then verify `main` CI green;
5. create an annotated `v0.4.0` tag at that exact commit and push the tag separately.

## v0.7.0 — the demo is built, published, and threaded through every surface

Shipped 2026-08-29. A minor release: no production code changed, but the submission's one
mandatory missing artifact stopped being missing.

`assets/demo-video/bastion.mp4` is **3:53**, twelve beats, 1920×1080, published at
<https://youtu.be/Xpj8YmzFfpk> with a 36-cue English caption track. It is *assembled*, not edited:
[`scripts/assemble_demo_video.py`](../../scripts/assemble_demo_video.py) builds the timeline from
the measured narration, so the picture cannot drift from the sound. The opening is a real recording
of the live public console driven by `scripts/capture_site_hook.mjs`; the rest is the redacted
evidence retained as 11, 12 and 13 plus the generated masters — which is why the narration says the
cut was **captured from the deployed fleet** rather than claiming it happens live on camera.

Three defects were found and fixed in the making, each of the same shape — a generated artifact
silently describing a version of the cut that no longer existed:

- the caption sidecar was written when the hook still held for 3.0s, leaving every cue after the
  hook **2.000s late**; invisible on a thirteen-second cue and obvious only on the shortest, where
  "Thank you for watching" was captioned after the words had finished. The assembler now refuses to
  render unless each beat's first cue starts when the beat starts;
- the cross-dissolve surplus was added per beat while twelve transitions exist, so the picture
  finished 0.4s ahead of the narration;
- the governed-flow stop in the hook parked where the figure's bottom row fell out of frame.

**The published URL points at a fixed file.** Dropping a recording into `assets/demo-video/beats/`
still takes precedence automatically, but acting on it now means re-uploading rather than
re-rendering — and the Devpost description pulls its architecture image live from `main`, so after
submission neither `main`'s diagrams nor the video may change without re-checking what judges see.
That is the reason this tag exists before submission rather than after it.

**Re-check before the final freeze:** the clean-clone gate is due from the public `v0.7.0` tag —
the retained record still verifies `v0.5.1`, two releases back. The two deferred observations
(managed Gateway refusal, retry/dead-letter) stay deferred by decision, with the narrower wording
already in the claim matrix; closing either would mean changing the deployed fleet and
invalidating the captures this video is built from. Bonus publication (article, social post) and
the Devpost submission itself remain open and are not release work.

## v0.6.0 — every pin to the newest release the resolver allows

Shipped 2026-08-27. A minor release, not a patch: no production code changed, but the dependency
resolution the whole fleet is built on did, including the agent framework.

**The gate that should have surfaced this examined five pins of twenty-three.** `--check-upstream`
only ever queried the packages a document names, because its purpose was catching a false claim.
`v0.5.2` therefore shipped on a run that reported one problem and read as though everything else
had been checked, when ten other pins were behind. The survey added here is the actual fix; the
bump is the decision it made possible.

**`opentelemetry-api` and `-sdk` did not move**, because `google-adk==2.8.0` caps them at 1.42.1.
"Everything latest" is not a satisfiable resolution while the framework is pinned — the resolver
settled that, not a judgement call.

**The deployment did not move with the pin, and that is this tag's open item.** Both surfaces still
run the resolution `v0.4.0` deployed. Redeploying obliges re-capturing evidence 11, 12 and 13 —
they name the current Cloud Run revisions — and recomposing gallery images 03, 04 and 05 from them.
Until then "deployed and verified" means the older resolution; see
[ADR-005](../../docs/adr/005-adk-as-the-agent-framework.md).

**Re-check before the final freeze:** the clean-clone gate is due from the public `v0.6.0` tag,
and the demo video remains the only outstanding mandatory Devpost artifact. `gcp-state.json` was
re-measured 2026-08-27 — same 21/21 APIs and 39 resources, so every count in the diagrams and on
the public console is unchanged and only the disclosure date moved.

## v0.5.2 — the judge-facing image set, and the gate that clears it

Shipped 2026-08-27. A patch release on the same reasoning as `v0.5.1`: no production code changed,
and the defect is in a judge-facing artifact rather than in the fleet.

Two things made it worth a tag rather than a loose commit. The gallery is a required Devpost field
and now exists in full, so the repository's own claim ledger, runbook and public console had to
agree about it in one commit. And the redaction gate caught a real leak on its first run:
`assets/evidence/screenshots/` held verbatim copies of raw takes, two of them carrying the signed-in
operator's Google account photo, referenced by no evidence record and outside the gate's globs.

Also carries the dark architecture still, three deliberately narrowed gallery captions, and the
full Markdown sweep those changes forced.

**Pre-tag `--check-upstream` fails on purpose.** `google-adk` 2.8.0 exists against a 2.7.1 pin.
Declined for this tag and recorded in [ADR-005](../../docs/adr/005-adk-as-the-agent-framework.md):
the migration trigger has not fired, and the deployed fleet runs 2.7.1. Unlike the 2.7.0 → 2.7.1
bump in `v0.2.0`, taking this one would require redeploying both surfaces and re-verifying live.
Do not read a green `--check-upstream` as a precondition for this tag; read the ADR.

**Re-check before the final freeze:** `gcp-state.json` still records a 2026-08-23 capture, the
clean-clone gate is due again from the public `v0.5.2` tag, and the demo video remains the only
outstanding mandatory Devpost artifact.

## v0.5.1 — correct a dated claim on the Devpost architecture image

Shipped 2026-08-25, hours after `v0.5.0`. A patch release for one defect worth releasing quickly:
every architecture asset was stamped `2026-08-22` against a `2026-08-23` capture, and the affected
PNG is the required Devpost architecture upload. The count in that footer was gated; the date was
not.

Also carries the gate that would have caught it, plus two public-console additions — a relative
snapshot age beside the absolute stamp, and a release string gated against `pyproject.toml`.

No production code changed. **Re-upload `enterprise-fleet-architecture-light.png` to Devpost**
when the form is next touched; the previously uploaded copy carries the wrong date.

## v0.5.0 — reproducibility, submission prep, and five closed observations (pre-media)

Shipped 2026-08-25. The planned scope was P1.3 (an actual clean-clone reproducibility run), the
final claim matrix, and drafted-but-not-published Devpost, article and social copy. All three
landed — and the scope then grew, deliberately, because the evidence sprint ran before the tag
rather than after it.

What this tag actually carries beyond the plan: current-route IAM provenance, the agent-mediated
Model Armor refusal, the correlated payload-free audit trail, and the Cloud Trace chain
(evidence 11, 12, 13), plus the documentation reconciliation those captures forced. Splitting them
into a later tag would have released a claim matrix that disagreed with the evidence ledger beside
it.

No production code changed. The deployed fleet is the one `v0.4.0` deployed.

Explicitly excluded and still excluded: the demo video, the five composed gallery PNGs, and the
actual Devpost/article/social publication — human publication tasks per this file's own
"Submission gate," not release engineering. Also excluded on purpose: P0.10 managed Gateway
refusals and P0.11 timeout/retry/dead-letter, which take the sanctioned narrower wording.

Two mutable facts must be re-checked at the final freeze rather than trusted from this tag:
`gcp-state.json` was captured 2026-08-23 and is not recaptured here, and upstream issue/PR state
changed once already between a documented check and a release.
