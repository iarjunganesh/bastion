# Bastion technical report — master plan

Proposed 28 October 2026 by Claude Code; **D1–D4 decided 28 October, D5 open**. This is the
single sequence for the report and its GCP evidence runs. [HANDOFF.md](../../HANDOFF.md) records
session state only. [docs/UPGRADE-PLAN.md](../UPGRADE-PLAN.md) covers the ADK/release track
(Track U) only. Private values (credit balances, ceilings, raw captures) go in ignored `.local/`;
its earlier history, including the old private roadmap, is in the maintainer's out-of-repo archive.

**Goal:** one coherent, citable technical report (C1–C3) in which every dated claim maps to
sealed evidence, using the remaining GCP credits in small, pre-registered chunks before expiry.

[AGENTS.md](../../AGENTS.md) governs everything else: three agents, read-only real IAM, payload-free
audit, the sensitive-output rule, dated cohorts never relabelled, the 62-binding figure dated
25 August, the author line, and the credits-only condition. This plan neither adds to nor relaxes
those rules.

## Grounded state, 28 October

A read-only census on 28 October (19:23 UTC) replaced several assumptions with observations:

- The fleet is the August deployment: all four Cloud Run services serve one image digest built
  23 August (same Auditor/Escalation revisions as evidence 11), the dispatcher's Runtime was last
  updated 23 August, and the repository's fleet verifier passes.
- The IAM policy changed: **56** bindings scanned (62 on 25 August), still three deterministic
  findings (`platform-infra` 1, `security-engineering` 2).
- The only human exception expired on **18 September**, which is consistent with October
  delivering three findings where August delivered two (not yet proven to be the same finding).
- Audit logs go to the `bastion-audit` log bucket: europe-west4, 365 days, unlocked. No
  Scheduler jobs. Investigations: 57 completed, 4 failed and 2 stale `running` records, all
  failures and stale records dated 15–22 August. 82 human-review records exist.
- Not readable by API here: credit balances, per-service cost (no billing export), and the
  installed packages of the deployed image and Runtime.

- **Report:** one source set in `report/` (untracked by request) assembles a 13-page PDF. Until
  the 28 October cleanup three builds circulated (two in `report/` with different hashes, one
  frozen private copy); only `report/bastion-technical-report-v1.pdf` remains.
- **Evidence:** E01–E13 (August), E14 (27 October 20-run repeatability study) and E15
  (28 October count-only inventory). E14 and E15 are on `main` since PR #1 (`75ab108`).
- **Code:** ADK 2.13.0 source upgrade released as v0.8.0 on 28 October, with one accepted
  OpenTelemetry advisory that every ADK release's version cap prevents fixing ([issue #3](https://github.com/iarjunganesh/bastion/issues/3)).
- **Fleet:** unchanged since August (same worker revisions, Runtime updated 23 August). No GCP
  work since the 27 October study. Credits expire 11–12 November.

## Why progress stalled

New GCP runs sat behind three chained gates: credit eligibility, then an upgraded deployment
(UPGRADE-PLAN step 5 precedes the controls in step 7), then a release blocked by an upstream
advisory. Only the first gate matters for the report. Meanwhile the manuscript grew by accretion:
the October study was attached as a "supplementary" §4.4 after a §4.3 table that already used
its results, and each session added caveats instead of restructuring.

## Structural problems the final report must fix

1. **Results before method.** §4.3 reports October results; the October method is in §4.4. There
   is no single evaluation-method section or cohort definition.
2. **Repetition.** The same caveats recur in three to five places ("60 instances are not 60
   distinct risks"; version provenance in §4.1, §6.2, A.1 and A.3; replay/trace limits in §4.3,
   §4.4 and §6.2). About 120 manuscript lines contain "not"; it reads as an audit ledger.
3. **Stale facts.** E14 is described as lacking an immutable reference but is on `main`.
   Repository links pin `a0e08fc` while E14/E15 live at later commits, so the report cites two
   revisions. "No fresh Scheduler census" is stale after E15. The version table names a v0.8.0
   target that does not exist.
4. **Source layout follows drafting history.** `sections-3-5.md` still carries its own title
   block, draft date and an editorial source key that the builder strips at assembly.
5. **Thin framing.** The threat model is folded into §3.1; related work has five references.
6. **Process narrative in results.** The collector pause and recovery occupy a results paragraph.

## Decisions for the maintainer

| ID | Decision | Status |
|---|---|---|
| D1 | Couple the report to the ADK 2.13.0 production upgrade? | **Decided: no.** All new evidence runs on the unchanged August deployment. The upgrade, its redeploy and any repository restructuring wait for Track U after the evidence freeze. |
| D2 | Include C4 in this report? | **Decided: deferred to v2**, revisited only at the 4 November gate as an automated-metric pilot on synthetic data. |
| D3 | Paid-run approval model | **Decided: per chunk**, each with its own written cost cap, count limit and stop rules. Read-only chunks need no cost cap. |
| D4 | Fleet end state before the credits expire | **Decided: teardown after the 8 November freeze, dry run first, before 11 November.** Open sub-choice at the freeze: export, remove or accept the residual storage teardown keeps (Firestore, secrets, Runtime, audit logs). |
| D5 | Publication reference | Open. Recommendation: a dedicated report tag (for example `report-v1.0`) independent of v0.8.0, archived to Zenodo. |

## Evaluation design: one primary cohort

The report evaluates **one primary cohort, N (November 2026)**, collected under the protocols
below on the unchanged deployment, with every metric defined before collection: census, negative
controls, refusal, exception lifecycle with expiry, a repeatability batch with token, cost and
ID-joined trace measurement, and the two formerly partial controls. Earlier observations are not
re-argued in the results:

- **August** appears only where it cannot be replaced: the deployment's provenance (built
  15–23 August, unchanged since) and the A2A state-loss incident behind C3, which is now
  re-demonstrated offline by O1 rather than narrated from retained evidence.
- **27 October** is cited once as the pilot that shaped cohort N's protocol, with its collector
  recovery disclosed in the appendix.

## Single source of truth

| What | Canonical | Everything else |
|---|---|---|
| Sequence | This file | Older private roadmaps are archived history |
| Session state | `HANDOFF.md` | Older private handoffs are archived history |
| Manuscript | `report/` sources | Archived private copies are never edited or cited |
| PDF | `report/bastion-technical-report-v1.pdf`, built once in Phase 5 | No other builds |
| Claims | Claim matrix plus the report claim map from Phase 1 | — |
| Evidence | `assets/evidence/NN-*.md` and sealed bundles | `.local/measurements/` until promoted |

## Phase 0 — Consolidate (today, local, no cost)

- [x] D1–D4 decided (28 October); D5 open until publication.
- [x] Delete the duplicate build, caches and temporary folders; archive `.local/` outside the
  repository; rebuild `.venv` from `requirements.lock` (28 October).
- [x] Archive the hackathon material under `archive/hackathon-2026/`; move the live ledgers and
  this plan to `docs/research/` (28 October).
- [x] Keep the "Report generation order" and "Credits-only" rules in AGENTS.md only; the copies
  in HANDOFF.md and docs/UPGRADE-PLAN.md are now pointers.

## Phase 1 — Paper blueprint and offline evidence (local, no cost)

The maintainer correction stands: no manuscript prose edits and no PDF builds in this phase.

- [ ] Write `report/OUTLINE.md` (uncommitted): target structure, a one-sentence thesis per
  section, and a claim map (claim ID → section → evidence ID → status: observed, configured,
  offline-tested, partial, stale). Target structure: 1 Introduction; 2 Background and related
  work; 3 Threat model and design goals; 4 System design; 5 Evaluation method (cohorts, metrics,
  timing definitions, data handling); 6 Results (route, repeatability, control probes, cost);
  7 A2A state-boundary case study; 8 Discussion and limitations (each limitation stated once);
  9 Conclusion and future work; Appendix A Reproducibility; Appendix B Evidence ledger; References.
- [ ] Derive the evidence-gap list from claim-map rows marked partial, stale or unobserved. It
  becomes the chunk backlog in Phase 3; a gap with no chunk is reported as a limitation.
- [ ] O1: rerun the localhost A2A reproduction on ADK 2.13.0 in a fresh Python 3.12 environment
  built from `requirements.lock`; record whether both upstream warnings fire. No model or cloud
  calls. This replaces "the reproduction was not rerun" in §5.3 with a result.
- [ ] List candidate related-work references; verify each against its primary source before use.

## Phase 2 — Credits gate (maintainer, about 15 minutes, read-only)

**Passed 28 October:** all October Bastion usage, the 27 October study included, was fully
offset by credits (net 0.00 SEK). Gross October usage was a little over 10 SEK, so the idle
fleet costs well under 1 SEK a day. Values are recorded privately in `.local/`.

- [x] In Cloud Billing Reports for `bastion-fleet-2026`, last 30 days, grouped by service and SKU
  with credits shown: confirm that the 27 October study day was fully offset by credits and note
  which credit applied. This establishes eligibility empirically for the services the fleet uses.
- [x] Note the idle fleet's standing daily cost.
- [x] Check the credit balance at billing-account level: credits are shared by every project
  on the same billing account, not reserved for this one.
- [x] Record both in `.local/credit-verification.json`. If any service shows a net charge, stop;
  no paid chunk runs until it is resolved.

Budget alerts notify; they do not cap. Billing data lags about a day, so every paid chunk is
followed by a next-day billing check before the next paid chunk starts.

## Phase 3 — Evidence chunks on GCP

Every chunk follows one protocol, and the protocol file is the approval artifact:

1. Pre-register `.local/measurements/<date>-<chunk>/protocol.json`: claim-map rows it closes,
   exact calls, count limit, cost cap, wall-clock limit, stop rules and cleanup targets.
2. The maintainer approves that protocol in-session. Earlier authorizations do not carry over.
3. Run one pilot unit; continue only if it passes.
4. Seal payload-free outputs with a hash manifest and ZIP; run the protected-shape scan.
5. Promote a redacted `assets/evidence/NN-*.md` (numbering continues at 16); update the claim map.
6. Next day, record the chunk's cost by SKU, net of credits.

| Chunk | Closes | Surface | Model calls | Creates resources | Target |
|---|---|---|---|---|---|
| E1 Census | Fresh binding and pre-policy finding counts; exception-ledger state; retention configuration; deployed package provenance | Read-only APIs | 0 | No | **Done 28 Oct** except image packages |
| E2 Negative authorization | Escalation IAM-read denial; findings API missing/wrong token and invalid payload | Impersonation and HTTP probes | 0 | No | 30 Oct |
| E3 Screening refusal | Agent-mediated Model Armor refusal with a benign control | Direct authenticated Auditor | At most 2 | No | 30 Oct |
| E4 Exception lifecycle | Approval, suppression and **expiry firing** (never yet observed); an ID-joined trace; per-run tokens and cost | Production path, maintainer as reviewer | About 6 | One real, self-expiring approval | 30–31 Oct |
| E5 Gateway refusal (P0.10) | Unregistered-caller refusal at Gateway/Registry/IAP | Design note first | 0 | Possibly a test identity | 2–3 Nov |
| E6 Retry and dead letter (P0.11) | Watched redelivery and fifth-attempt dead letter | Isolated topic, trigger and service with equivalent policy | 0 | Yes, removed afterwards | 3–4 Nov |
| E7 Repeatability | Twenty serial investigations with per-run tokens, attributable cost, ID-joined traces and per-message replay delivery | Production path | About 40 | No | 31 Oct – 1 Nov |
| E8 (optional) | C4 automated-metric pilot | Synthetic policies only | Separately budgeted | No | After the 4 Nov gate |

- **E1:** done read-only on 28 October (results under Grounded state; private outputs in
  `.local/measurements/2026-10-28-ground-truth/`). The census used the Auditor's own fetch and
  detector with a throwaway in-memory ID key, so no production secret was read. Remaining: list
  the installed packages by pulling the deployed image (tiny billable egress, after Phase 2).
  The Runtime API does not return its source archive, so its installed resolution stays
  undeclared; say so rather than infer it.
- **E2:** if the maintainer's impersonation right on the Escalation identity no longer exists,
  stop; do not grant it.
- **E4:** the findings API accepts any future `approved_until` up to 90 days, so expiry can be
  observed within an hour. The approval is a real maintainer decision on a real finding; it is
  the chunk's only state change and it expires by construction.
- **E5/E6:** each needs a short design note and explicit approval because it may create an
  identity or resources. Production allowlists, retry policy and IAM bindings stay unchanged.
  E6 results are claimed for an isolated, configuration-equivalent path, not production fault
  injection.
- **E7:** reuses the October protocol with the instrumentation October lacked. Validate the
  token, trace and delivery measurements on E4's runs first.
- **Order:** E1 → Phase 2 billing check → E2, E3 → E4 → E7 → E5, E6 → freeze.
- **4 November gate:** review spend, remaining days and open claim-map rows; decide E8 or
  proceed to the freeze.

## Phase 4 — Evidence freeze and fleet end state

- [ ] 8 November: evidence freeze. The claim map is final; no new runs.
- [ ] Before 11 November: execute the D4 end state (dry run first). Confirm in Billing that
  nothing continues to accrue once the credits end.

## Phase 5 — Write the report once (8–13 November)

- [ ] Restructure sources to the outline: one file per top-level section and one references file.
  Drop the legacy `sections-3-5.md` header and editorial source key; update the builder to match.
- [ ] Pin every repository link to one revision: the commit containing the final evidence. The
  builder's S5/S11 entries still name their `a0e08fc` paths; repoint them to
  `docs/research/claim-matrix.md` and `archive/hackathon-2026/submission/ARTICLE_DRAFT.md`
  in the same change (until then `check_docs.py` reports those two paths locally).
- [ ] Writing rules: each limitation once (§8), cited elsewhere by section; each dated number in
  exactly one results table; cohort and version provenance once (§5); process narrative such as
  collector recovery in Appendix A; abstract at most 200 words with at most four numbers.
- [ ] Build once; run integrity, citation and layout checks; review visually; maintainer reads
  the whole draft. Batch revisions into one rebuild rather than rebuilding per comment.

## Phase 6 — Publish (14–16 November; every step needs explicit approval)

- [ ] Commit report sources and final evidence on a branch; open a PR; merge.
- [ ] Tag per D5; create the GitHub release with the PDF; mint the Zenodo DOI.
- [ ] On publication day, refresh U1–U4 and public links.

## Track U — ADK 2.13.0 and v0.8.0

v0.8.0 was released as source on 28 October with one accepted OpenTelemetry advisory, whose
removal is tracked in [issue #3](https://github.com/iarjunganesh/bastion/issues/3). Under D1 the fleet redeploy, the ADK bump that closes
issue #3 and any per-agent restructuring all come after the evidence freeze, so the report keeps
measuring one unchanged deployment.
