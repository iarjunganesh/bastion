# Technical report plan

Updated 6 November 2026. [HANDOFF.md](../../HANDOFF.md) records current session state;
[AGENTS.md](../../AGENTS.md) governs architecture, privacy and operator authorization.

## Scope and current state

The report covers the minimisation design (C1), the pre-defined November evaluation (C2),
and silent success at agent boundaries (C3). C4's matched-explanation comparison is deferred;
the synthetic harness has no results and generation remains disabled.

| Record | State and boundary |
|---|---|
| Cohort N, 3–4 Nov | Complete and frozen on the unchanged August deployment: [E16–E23](../../assets/README.md) |
| Original F, 5 Nov | Both surfaces updated; one pilot failed closed on a routing-parser incompatibility ([E24](../../assets/evidence/24-upgraded-deployment-and-stopped-pilot.md)) |
| Separate corrected recovery, 5 Nov | Five normal cases, direct confirmation control and two replays passed; refusal join verified read-only after a collector false positive ([E25](../../assets/evidence/25-corrected-cohort-F-verification.md)) |
| Billing, 6 Nov | Daily reported-usage check passed, corroborated by the supplied CSV; balances/expiry refreshed privately. Final per-chunk cost and late postings remain bounded |
| Report, 6–7 Nov | Authorized final reconciliation complete; 14-page local PDF generated on 6 Nov. The 7 Nov independent review's corrections are applied to the sources; one rebuild follows the remediation merge. Keep `report/` uncommitted |
| Fleet end state | Still scheduled for 8–10 Nov, dry run first, before 11 Nov; no shutdown has been claimed |

The original F failure, recovery and N remain separate. Runtime did not change during recovery;
its installed package resolution remains unreadable. The claim matrix, version ledger and
collection disclosures bound the report; a passing batch is not a reliability rate.

## Maintainer decisions

| ID | Decision |
|---|---|
| D1 | Freeze primary cohort N before the upgrade; report post-upgrade F separately |
| D2 | Defer C4 to a later study. Injection fixtures exist; missing-workflow-step cases remain planned |
| D3 | Per-chunk approval with a written cost/count cap and stop rules, within the 100 SEK total upper bound. One daily billing check replaces a per-chunk overnight wait. Reserve unposted prior chunks conservatively |
| D4 | Reach the agreed fleet end state on 8–10 Nov, before 11 Nov. Dry run first; owner chooses export/removal/accepted costs for residual resources |
| D5 | Report publication reference, tag/DOI and release remain open. Public source integration is authorized on 6 Nov via [PR #9](https://github.com/iarjunganesh/bastion/pull/9) |

Credits are shared, scoped and expiring; availability is not a hard spending cap. Card charges
remain unauthorized. Numeric balances, reservations and billing receipts belong in ignored
`.local/credit-verification.json`. No further F probe is planned or authorized.

## Remaining sequence

1. Maintainer reviews the completed local PDF; public source integration proceeds through
   [PR #9](https://github.com/iarjunganesh/bastion/pull/9) after hosted CI passes.
   The offline sweep, primary-source refresh and source/builder reconciliation passed their checks.
2. Keep report sources/output uncommitted and retain the manifest, source snapshot and QA receipt.
   Validation corrected table widths and generated Markdown spacing; do not restart iterative drafting.
3. In the existing 8–10 Nov window, review the D4 dry run and agree residual-resource handling
   before applying it. Firestore, secrets, Runtime/Memory and audit state are retained by default;
   nothing here authorizes their deletion or an irreversible bucket lock.
4. At publication, refresh upstream status and public links, select the immutable reference,
   and obtain approval for report release/Zenodo/site actions. This local edition does not claim publication
   or a completed shutdown.

## Evidence and manuscript rules

- Each claim maps to the [claim matrix](claim-matrix.md) and a dated record in the
  [evidence index](../../assets/README.md). Source, deployment and observation are distinct.
- Apply the [4–5 November audit](evidence-audit-2026-11-04.md): conventional E19 median,
  tail grouping, missing census seal, separate E3 addendum and configured-versus-observed alerts.
- Retain the original F stop and recovery's raw X1/collector stop. The refusal addendum is a
  later exact-ID query, not continuous monitoring or directly measured provider transport.
- Current sources are `report/sections/`; the builder reads them in an explicit order.
  The local cited-source snapshot records working-tree content without inventing public links
  under a commit that lacks it. Report publication remains a separate step.
- Keep the author line “Independent researcher, Stockholm”; no award, universal privacy result,
  end-to-end EU model residency, immutable retention or historical SLO claim.

## Retained protocol history

The completed N protocols and E5/E6 design notes remain in the
[pre-sweep source plan](https://github.com/iarjunganesh/bastion/blob/d7d6a99a5f1534f835235e21f95a0413f5027ecc/docs/research/report-plan.md).
The exact F/recovery protocols, approval/admission receipts and collector sources are sealed
separately under `.local/measurements/`. The full pre-sweep dirty tree/report snapshot is retained
privately; shortening this active plan does not retroactively change an executed protocol.

v0.8.0 remains the 28 October source release. Dependency acceptance and later production
provenance are recorded once in [DEPENDENCY-STATUS](../DEPENDENCY-STATUS.md) and
[VERSIONS](../VERSIONS.md); the [upgrade plan](../UPGRADE-PLAN.md) is its closeout checklist.
