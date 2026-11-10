# Bastion handoff

Read [AGENTS.md](AGENTS.md), this file, the [report plan](docs/research/report-plan.md) and
[upgrade closeout](docs/UPGRADE-PLAN.md). Update Current state, Next step and Session log before stopping.

## Current state — 10 November 2026

- **Evidence is frozen.** v0.9.0 (cohorts G, H) and v0.9.1 (cohort I, chunks J–M) were deployed
  and measured on 7–8 November ([E26–E29](assets/README.md)). I validated 98 of 98, and its I99
  addendum is separate. J's controls passed. K plus a 142-trace census show incomplete Runtime
  graph-span export. M observed a worker timeout reaching dead-letter review, with worker
  computation continuing after the timeout. L (an instrument stop) and M's preflight amendment are
  retained. L and M retain separate protocols/results, including M's preflight amendment; stopped
  records are never pooled. Protocols are **pre-specified**, not pre-registered. Sealed
  hashes: `.local/measurements/seal-2026-11-09.json`.
- **Fleet retired (D4 closed 9 November).** Teardown A (`teardown.py` from `8f63fc6`) deleted
  25 of 26 allowlisted serving resources. Gateway deletion returned `FAILED_PRECONDITION`;
  read-only checks then found a retained Runtime engine reference and a targeting authz policy.
  The cause of the refusal is not independently established. It was not retried, by the
  maintainer's decision. The image repository
  and both build buckets are deleted (B). The 2 dead-letter messages were captured first by a
  separately dated, non-acknowledging read-only inspection (A0): exact event-ID joins to F1 and M1.
  The deployed v0.9.0/v0.9.1 images were exported by digest and verified.
- **Report:** one definitive report. The blueprint was frozen on 9 November (`report/OUTLINE.md`,
  local) after two external reviews and the maintainer's approval. The 6–7 November PDFs are drafts.
  Title: *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed
  Agent Fleet.*
- **Technical verification closed (10 November):** all 16 follow-up findings, including I7/M4,
  are corrected and verified in the 25-page PDF (`f3b2bb95…9071`). All 25 full-page renders were
  inspected; figures, captions and repeated table headers agree. The 17 report checks, all 70
  source/snapshot hashes and ZIP CRC, Ruff, docs/version and Markdown checks pass. Reconciliation,
  the dated closeout, integrity/privacy receipts and report README now describe this build:
  `report/qa/final-closeout-2026-11-10.md`. Finite text/metadata/link checks found no prohibited
  private-value patterns. The closeout changed QA/status records only; the PDF was not rebuilt.
  The reviewer's earlier authorship remains disclosed; no independent peer review is claimed.
  R7 remains confirmed as Peng Huang. Sources/output stay uncommitted; the blueprint, stop
  records and evidence are unchanged. The report is ready for the publication-manifest step.
- **Git housekeeping (10 November):** `main` was fast-forwarded through PR #16 (`8f52fc3`). The
  four branches for merged PRs #13–#16 were removed locally and from `origin` after
  exact-head/ancestry checks and a verified recovery bundle. The review-status update `835df67`
  was then committed directly on `main` and pushed without a PR; its CI run failed because three
  handoff lines read as suite test-count claims. This branch corrects that record and the
  wording. `report/` remains intentionally untracked and `.local/` ignored; nothing was published.
  Preservation and cleanup receipts: `.local/git-cleanup/2026-11-10T012206/`.
- **Billing:** daily checks passed on 6 and 8 November (2–8 November fully offset by credits, net
  0). On 9 November billing was disconnected from `bastion-fleet-2026` only (verified: no billing
  account, billing disabled). D4 made no change to the shared account or other projects. Charges
  incurred earlier, including soft-deleted storage, may still post.
- **Retained, not deleted:** the Gateway (with its authz policy and extension), 2 Runtime engines
  with Sessions/Memory, Firestore, 2 secrets, the `bastion-audit` log bucket, service accounts and
  IAM. With billing off, billing-gated APIs refuse access, and these may become unrecoverable.
- **Known teardown gap:** `teardown.py` does not inventory the Gateway's dependants (the authz
  policy, the extension, the Runtime gateway reference). Its dry runs therefore could not predict
  the stop.
- **Preservation:** the local archives and an encrypted, independently verified off-laptop copy
  (695 files: the seal, A0 and both OCI images). Records are in `.local/d4/`, including
  `d4-closeout-2026-11-09.json`.

## Next step

1. **Technical review complete (local, uncommitted `report/`):** all 16 follow-up findings are
   verified in the current 25-page PDF. Full visual review, reconciliation and QA receipts are
   complete; no further manuscript correction was found.
   Public guidance is recorded separately in Git; the only remaining untracked work is the
   intentionally private report directory. Only `main` remains locally and on `origin`.
2. **Next:** prepare the publication manifest against the verified local artifact hashes, then
   obtain the maintainer's final manuscript/manifest approval before release. The existing
   PDF is current and the frozen blueprint remains unchanged.
   The local build does not create a tag, DOI or site release.
3. Run the final billing check after late postings.
4. Only after the maintainer approves the manuscript and the publication manifest: the
   `report-2026-11` tag, the DOI (Zenodo) and the site release. No new experiments.

## Session log

### 28 October–4 November

v0.8.0 source release and D1–D4 decisions; cohort N collected, audit corrections prepared,
main manuscript rewrite and T1–T3 wording approved. The full earlier journal is retained privately
in the pre-sweep snapshot; current evidence and protocols are linked from the report plan.

### 5 November

Original F failed closed after deployment. Separately approved same-day recovery deployed the
exact Escalation parser correction with Runtime unchanged and observed the bounded controls.
Its final refusal collector stopped on a temporal false positive; read-only exact-ID validation
closed the observation without rerunning a paid probe. Both cohorts were sealed separately.

### 6 November — billing and final sweep

Reviewed Overview, daily SKU, Project, Credits and the supplied CSV; recorded a passed daily
reported-usage check with attribution/late-posting limits. CLI/API metadata alone exposed no
accessible billing export. The maintainer then authorized the final PDF and shorter current docs.
Preserved the dirty tree/report and requested independent review. Corrected stale F/billing,
security/dependency and approximate-dead-letter claims; retained original capture disclosures.
Final validation: 336 core cases at 100% configured statements/branches, 12 report checks,
9 study cases plus 6 subtests, Ruff/format, mypy (40 files), docs/version, redaction, diagram
freshness, static site build/check and Markdown lint passed. The 14-page PDF passed automated
and full visual review after table-width and generated-Markdown spacing corrections; all collection disclosures remain.
Original F/recovery seals and the pre-sweep preservation ZIP were rechecked. No cloud call,
new paid probe, commit, push, tag, publication or shutdown occurred in this sweep.

### 6 November — local Git cleanup

The maintainer asked why public changes were still uncommitted. The sweep had completed;
only the report was required to remain uncommitted. Finalized the reviewed public code,
documentation, evidence and site-source changes in a local commit after an explicit-path
staging check. `report/` and `.local/` were excluded. The completed PDF/source snapshot retain
their original bytes and base-revision provenance; Git housekeeping does not rebuild the report.
No push, tag, cloud action or publication.

### 6 November — explicit release/deployment provenance

Added the missing v0.8.0 release row and commit to Appendix A, retaining the distinction from
the later deployed image/source overlays. Verified GitHub release/tag metadata and local Git
ancestry. Pinned the report's public-link base so unpublished local commits cannot silently
replace it. The 14-page PDF has 38 clickable references and a 58-file source snapshot; twelve
report checks, automated layout checks and changed-page visual review passed. Version-ledger
and handoff corrections are committed locally; report sources/output remain uncommitted.
No push, retag, deployment or new probe.

### 6 November — public source integration

The maintainer requested branch publication and merge into `main`. Published the two public
commits and opened [PR #9](https://github.com/iarjunganesh/bastion/pull/9); integration requires
passing hosted CI on the final head and uses a merge commit to preserve history. The final
local rerun passed 336 cases at 100% configured coverage after using a writable pytest temporary
directory. Public guidance now records this authorization separately from report publication.
The report/PDF bytes and private captures are preserved; no rebuild, retag, GCP deployment,
paid probe or shutdown is part of this integration. The GCP deploy workflow remains manual-only.

### 6 November — late link review

PR #9 merged with history preserved; all eight post-merge CI jobs passed. An automated review
arrived after merge and identified removed README anchors still advertised by the Agent Card
and frozen submission. Verified both references and restored `the-fleet` and `quality-gates`
beside the replacement sections. Runtime metadata and archived files need no changes.
Report sources/output remain uncommitted and byte-identical; no report rebuild or cloud action.

### 7 November — independent review and remediation

An independent read-only review cross-checked code, evidence 16–25, the sealed F/recovery and
billing records, and the PDF. It verified the numbers and seals and found two code-level gaps,
an undisclosed v0.8.0 deployability issue, documentation drift and report clarity issues. Merged
branches were deleted locally and on `origin`; `main` was backed up as a verified bundle.
Remediation on `fix/review-remediation-2026-11-07`: source-only code fixes with tests (`84b9d86`),
documentation and append-only evidence notes (`55e3647`), and uncommitted report-source and
builder corrections. While the new SDK-surface tests were being written, two read-only
`gcloud run services describe` calls against a non-existent test project ran because of a wrong
override variable name; both failed and nothing changed. A suite-wide isolation guard now refuses
child processes and non-loopback network or DNS in every test (the suite needed no exemption).
Receipts now name their finding IDs and the completion gate compares them; deploy both surfaces
together.
Gates: Ruff/format, mypy (41 files), 373 core cases at 100% configured coverage, docs, versions, site,
diagram, redaction, Markdown lint, 9 study cases and 16 report checks. No push, merge, deployment,
paid probe, PDF rebuild or publication.

### 7–9 November — final deployment, measurement and blueprint freeze

PR #11 (v0.9.0) and PR #12 (v0.9.1, the bounded audited model retry, after H28's 429) were merged
and tagged. Measurement covered G and H on v0.9.0, and I–M on v0.9.1. Billing was checked on
8 November. After a GPT/Codex second opinion, the maintainer chose one definitive report and
approved a frozen blueprint (9 November), using "pre-specified" wording, three-part provenance
statements and M's reconstructed protocol hash as a disclosed limitation. Read-only post-hoc
analyses (the M ordering check and the trace census) are labelled as such. The G–M records were
sealed on 9 November.

### 9 November — D4 closeout

PR #13 (E26–E29 and the documentation sweep) and PR #14 were merged. PR #14 is the
inventory-first, allowlisted teardown, with four review findings fixed: status-only errors, exact
not-found parsing, list/describe reconciliation and delete timeouts. Before teardown:

- A0 inspected the 2 dead-letter messages without acknowledging them and joined them to F1 and
  M1 by event ID. It is post hoc and separately dated; E29 is unchanged.
- The two deployed images were exported by digest.
- The cohort build sources were verified against the source manifests.
- The encrypted off-laptop backup was independently verified.

Then A deleted 25 of 26 resources; the Gateway was retained because of the Runtime dependency.
The maintainer then ran B (the repository and 2 buckets) and C (billing unlinked from this project
only) in their own terminal, because local permission rules blocked Claude's delete commands.
Read-only checks confirmed the end state. The seals are unchanged (73/73 files).

Then the complete manuscript was written once from the frozen blueprint. The previous drafts are
archived privately. It has 3 new figures (topology and trust boundaries, chronology, M's timeout
timeline), was reconciled claim by claim against E01–E29 and the v0.9.1 source, and was built to
a 23-page review draft with no layout or citation findings. The tag and DOI are not created.

### 9 November — final report review

Reviewed the frozen blueprint, canonical manuscript, author reconciliation and all 23 rendered
PDF pages. Read E14, E19 and E24–E29 line by line; checked the v0.9.1 production contracts,
version provenance and primary external/upstream citations. R7's published paper names Peng
Huang. The 17 report checks pass; the assembled manuscript matches its sections, and all 70
source-snapshot hashes and the ZIP CRC verify. Finite text/link checks found no prohibited
private material or employer affiliation.

Verdict: ready after the listed fixes (9 Important, 5 Minor). The local review gives exact
wording for the cancellation overstatement, historical success attribution, dated census,
fleet-version summaries, collection disclosures, retry/dead-letter scope and figure/layout
issues. The required stopped records and frozen C1–C3 framing are retained. No manuscript,
PDF, figure or evidence edit/rebuild, cloud call, experiment, commit or publication occurred.

### 9 November — final review corrections and local build

The maintainer authorised all listed fixes. Applied the exact evidence-wording corrections to
canonical sections, retained the dated populations and stop records, expanded the acquisition
disclosures, and resolved R7 in the reconciliation. Corrected the report-only figures: mandatory
Gateway transit, distinct audit/trace joins, D6's date, readable labels and M's caption. The frozen
blueprint and public evidence bytes are unchanged. The earlier draft was preserved privately.

Built once to 25 pages. All 14 items are closed; 17 report checks, scoped Ruff/format,
documentation/version checks, Markdown lint, all 70 source-snapshot hashes and ZIP CRC pass.
All 25 pages were visually inspected. Labels measure at least 8.425 points in the final PDF,
and the numbered confirmation/provenance statements are distinct. Finite text/metadata/link
scans found no prohibited private-value patterns. QA receipts identify the corrected PDF.
Report sources and output remain uncommitted. No new experiment, cloud action, commit, push,
tag, DOI or site publication occurred.

### 9 November — independent verification prompt

Prepared a copy/paste prompt for Claude to independently verify all 14 corrections against
the current 25-page PDF, canonical sections, frozen blueprint and dated evidence. Rechecked
the PDF and source-manifest hashes. The prompt requires read-only review and chat findings;
it does not authorise edits, rebuilds, Git mutations, cloud work or publication. No request
was sent to Claude and no independent review outcome is claimed.

### 10 November — check of Claude verification

Read the supplied review and checked targeted manuscript/code/evidence passages plus PDF pages
10 and 15. Confirmed the C.4 retention disclosure error, both figure defects and the unresolved
first-use N7b issue. The review contains 1 Important and 15 Minor findings; several proposed
replacements need narrower language about stopped records, classifications and retained data.
Confirmed that the frozen outline matches its preserved pre-correction copy byte for byte.
Recorded the assessment in `.local/reviews/report-verification-response-2026-11-10.md` and
superseded the current all-14-closed status. The reviewer disclosed earlier authorship and
limited full-page visual coverage. No raw payload contents, credentials, IAM or unrelated
billing records were opened. No manuscript, PDF, figure, evidence or historical QA edit/rebuild,
experiment, cloud action, commit or publication occurred.

### 10 November — assessment after Claude's rate-limit interruption

Compared the interrupted pass with all 16 findings and the preserved pre-verification draft.
All text/figure corrections and the optional terminology/reference edits are present in the
canonical sources and new 25-page PDF (`f3b2bb95…9071`). The PDF embeds the current figure
images, and rendered pages 5, 10 and 15 were visually checked. The manuscript matches the
canonical assembly after newline normalisation; all 70 source/snapshot hashes and ZIP CRC
pass. Re-ran the 17 report checks, scoped Ruff/format, docs/version checks and Markdown lint: passed.
The frozen outline and Appendix C.1/C.2 stop/amendment records are unchanged. The remaining
work is visual sign-off and updating reconciliation, closeout, integrity/privacy receipts and
report README; those still describe the previous build. Wrote the detailed private assessment
and updated current state/next steps. No manuscript/PDF/figure or report QA record was edited
or rebuilt in this assessment; no cloud action, experiment, commit or publication occurred.

### 10 November — full visual and QA closeout

Completed the remaining technical checks rather than asking the maintainer to repeat the
25-page inspection. Inspected all 25 complete page renders, matched them pixel for pixel to
the current PDF and checked all figures/captions and table continuations. No additional layout
defect was found. Confirmed all 70 source/snapshot hashes, ZIP CRC, assembly after newline
normalisation, the frozen outline and preserved stop/amendment/dead-letter rows. Finite scans
of canonical sections, manuscript, PDF text, metadata and links found no prohibited patterns;
the author affiliation is exactly “Independent researcher, Stockholm”. Updated reconciliation,
the dated closeout, integrity and visual receipts, report README and current handoff/plan state.
The 17 report checks and scoped Ruff/format, docs/version and Markdown checks pass. The PDF,
canonical sections, figures, manifest and snapshot were not changed or rebuilt. Ready for the
publication-manifest step; author approval and publication remain separate. No experiment,
cloud action, commit, push, tag, DOI or site release occurred.

### 10 November — merged-branch cleanup and public guidance commit

The maintainer requested an explanation of uncommitted work and cleanup of merged branches.
The report directory is deliberately untracked under the standing instruction; the two tracked
edits are the public handoff/report-plan review updates. Preserved those exact files and their
patch, all 65 report files in a hash-verified ZIP, and all Git refs in a verified recovery bundle
under `.local/git-cleanup/2026-11-10T012206/`. Refreshed `origin`; checked merged PRs #13–#16,
their exact branch heads and merge ancestry, unique-commit counts and the sole worktree.

Fast-forwarded local `main` through PR #16 and restored the tracked edits byte for byte. Deleted
`docs/definitive-report-evidence`, `fix/teardown-d4`, `docs/d4-closeout` and
`docs/manuscript-review-draft` locally and on `origin`; the remote deletion was atomic and
guarded by each expected head. Only `main` remains on both sides. Recorded the public guidance
updates in a documentation commit after docs/version/Markdown checks. Report files and
private material were excluded; report hashes remain unchanged. No report rebuild, tag, DOI,
site release, experiment or cloud action was part of this housekeeping.

### 10 November — correction of the direct `main` commit

Claude re-checked the housekeeping. Commit `835df67` had been pushed directly to `main` at
01:28 without a PR, although this log and the cleanup receipt recorded it as unpushed. Its CI
run failed (`test_documented_test_count`): three lines described the report's own checks with a
phrase the suite count guard reads as a total. On branch `fix/handoff-ci-and-disclosure`, those lines now say
"report checks", the push is recorded accurately, and private-context material that does not
belong in public guidance was removed. Report sources and evidence are unchanged. Redundant
local caches and duplicate Git bundles were removed after reachability checks against `origin`.
