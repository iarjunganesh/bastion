# Technical report plan

Updated 10 November 2026. [HANDOFF.md](../../HANDOFF.md) records the current session state, and
[AGENTS.md](../../AGENTS.md) governs architecture, privacy and operator authorization.

## One definitive report

The maintainer will publish **one** definitive technical report with one immutable reference. It
is not a series of editions. The local PDFs of 6–7 November are drafts, not editions, and are
never published.

Title: *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed
Agent Fleet.* Contributions:

- **C1:** the governed architecture.
- **C2:** dated execution-boundary failures and the controls that answered them.
- **C3:** a bounded, pre-specified deployment evaluation, including stopped and negative cases.

C4 (matched explanation) is deferred to future work. The primary future direction is a separate
cross-framework study of execution contracts across local and remote A2A composition.

**The blueprint was frozen on 9 November 2026** (`report/OUTLINE.md`, local) after two external
reviews and the maintainer's approval. From here, changes are limited to verified evidence
corrections, manuscript accuracy, publication integrity and artifact validation.

## Evidence state: frozen

Live measurement ended with run M on 8 November. No further experiment is planned or authorized.

| Record | State and boundary |
|---|---|
| August–October | E10–E14: route, refusal, trace, correlation and continuity captures on the earlier deployment |
| Cohort N, 3–4 Nov | Frozen on the unchanged August deployment (E16–E23) |
| F and its recovery, 5 Nov | The pilot failed closed (E24); the corrected recovery passed (E25) |
| G, H, I, 7–8 Nov | v0.9.0 and v0.9.1 cohorts, with I's read-only I99 addendum ([E26](../../assets/evidence/26-cohorts-g-h-i.md)) |
| J, 8 Nov | I's unreached controls and probes on the same fleet ([E27](../../assets/evidence/27-targeted-controls-j.md)) |
| K, 8 Nov | Trace-export isolation and the read-only 142-trace census ([E28](../../assets/evidence/28-telemetry-census-k.md)) |
| L and M, 8 Nov | Timeout fault injection: L stopped on an instrument fault; M met its criteria ([E29](../../assets/evidence/29-timeout-fault-injection-l-m.md)) |
| Billing | Daily checks passed on 6 and 8 Nov (the 2–8 Nov gross was fully offset by credits, net 0). Per-chunk cost stays bounded, never measured |
| Fleet end state | D4 closed on 9 Nov. 25 of 26 serving resources deleted; Gateway retained after `FAILED_PRECONDITION` (Runtime reference and authz policy found afterwards; refusal cause not established); image repository and build buckets deleted; billing disconnected from this project only. Firestore, secrets, Runtime/Memory, the audit bucket and IAM are retained and may become inaccessible |

## Provenance boundaries

These apply to every G–M claim:

1. Protocols and criteria were documented before execution, according to the project's local
   records.
2. The execution scripts checked their pinned hashes at start-up.
3. No independent external timestamp fixes when any protocol was written. Hence
   **pre-specified**, never "pre-registered".

The seal of 9 November (hashes published in E26–E29) establishes integrity from that date only.
M's original protocol hash is reconstructed, an explicit additional limitation. Post-hoc
read-only analyses are labelled as such. Stopped records are retained and never pooled. L and M
retain separate protocols and results, including M's preflight stop and amendment M-A1.

## Maintainer decisions

| ID | Decision |
|---|---|
| D1 | Freeze primary cohort N before the upgrade; report post-upgrade work separately |
| D2 | Defer C4 to a later study |
| D3 | Per-chunk approval with written cost/count caps and stop rules, within 400 SEK in total (7 Nov). Credits only; card charges unauthorized. Reserve unposted chunks conservatively |
| D4 | Reach the agreed fleet end state before 11 Nov. Dry run first; the owner chooses export, removal or accepted cost for each residual resource. Editorial approval is not deletion authority |
| D5 | Report reference, tag/DOI and release need maintainer approval. The deployed code is v0.9.1; the report cites a later source reference (`report-2026-11` recommended) |
| D6 | One definitive report and a frozen blueprint (9 Nov) |

Numeric balances and billing receipts stay in ignored `.local/`.

## Remaining sequence

1. Done: the docs PR (#13) and the teardown fix (#14).
2. Done: D4 (9 Nov). Recorded in HANDOFF and in `.local/d4/d4-closeout-2026-11-09.json`.
3. Done: all 16 follow-up findings (1 Important, 15 Minor) are verified in the 25-page PDF
   (`f3b2bb95…9071`). All 25 pages received full visual inspection. Reconciliation, dated
   closeout, integrity/privacy receipts and report README now identify this build. The 17
   report checks, all 70 source/snapshot hashes/CRC, Ruff, docs/version and Markdown checks pass.
   R7 remains confirmed; the blueprint and stopped/amended protocol records are unchanged.
   See `report/qa/final-closeout-2026-11-10.md`. Next: prepare the publication manifest for
   the maintainer's final manuscript/manifest approval. No rebuild was needed for QA closeout;
   earlier reviewer authorship and the actual visual-review scope remain disclosed.
4. Final billing check after late postings.
5. Release, only on the maintainer's approval of the manuscript and publication manifest: refresh
   public links, then the `report-2026-11` tag, the DOI (Zenodo) and the site.

## Evidence and manuscript rules

- Each claim maps to the [claim matrix](claim-matrix.md) and a dated record in the
  [evidence index](../../assets/README.md). Source, deployment and observation are distinct.
- The 98/98 result is the headline. The Clopper–Pearson bound appears only as a conditional
  illustration in the method and limitations sections.
- Apply the [4–5 November audit](evidence-audit-2026-11-04.md) to cohort N's figures.
- Keep the author line "Independent researcher, Stockholm". No award, universal privacy result,
  end-to-end EU model residency, immutable retention or SLO claim.

## Retained protocol history

The N protocols remain in the
[pre-sweep source plan](https://github.com/iarjunganesh/bastion/blob/d7d6a99a5f1534f835235e21f95a0413f5027ecc/docs/research/report-plan.md).
F–M protocols, approval and admission receipts, collector sources and the 9 November seal are
kept under `.local/measurements/`. Release and dependency provenance live in
[VERSIONS](../VERSIONS.md) and [DEPENDENCY-STATUS](../DEPENDENCY-STATUS.md).
