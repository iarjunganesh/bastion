# Bastion technical report roadmap

Current roadmap, 28 October 2026. Read [HANDOFF.md](HANDOFF.md) for session state.
The original dated planning history remains private in `.local/BASTION-REPORT-ROADMAP.md`.

## Sources and claim boundaries

- Canonical source: `report/front-matter.md`, `report/sections-3-5.md`, and
  `report/back-matter.md`; assemble and validate with `report/build_report.py`.
- C1: deterministic minimisation and governance design. C2: dated deployment/control
  observations, including the 27 October repeatability study. C3: A2A boundary analysis.
- C4: synthetic comparative minimisation study remains unmeasured. Its offline scaffold
  is under `experiments/minimisation/`; preparation is not a result.
- Historical observations retain their actual framework/deployment versions and dates.
  The upgrade is a separate cohort. Never relabel August/October observations as ADK 2.13.0.
- The claim matrix in `submission/planning/11-claim-matrix.md` bounds all claims.
  Two controls remain partial until new evidence closes them.
- Keep private captures and working notes in `.local/`. Promote only reviewed, redacted
  evidence; no private handoff, credential, IAM payload, model text, or service origin.

## Work sequence

- [x] Preserve the current feature-branch report and private working state externally.
- [x] Put shared agent instructions and session state at the repository root.
- [x] Establish one report version/provenance table and remove conflicting current-pin prose.
- [ ] Complete ADK upgrade, redeploy both surfaces, and create a separate validation cohort.
- [ ] Run the feasible control matrix and record observed/configured/unobserved outcomes.
- [ ] Integrate new results with exact denominators, timing definitions, costs, and limits.
- [ ] Rebuild PDF; run integrity, citation, layout, and visual checks; obtain author review.
- [ ] Establish immutable references to the report/evidence source revision.
- [ ] Release v0.8.0 after code and deployment verification. Keep manuscript approval distinct.
- [ ] Decide report publication venue/licence and final draft marking; DOI/arXiv are separate
  publication steps, not consequences of a GitHub release.

## Credit window

Allocated credits expire in November. Verify the private expiry, eligible services and ceiling
before any paid work. The maintainer requires credits-only usage with no card charges; current
paid-account spillover protection is unresolved. Paid deployment/studies remain held.
Prioritize unobserved controls and upgrade regression coverage once eligible execution is
established. Reserve time for repairs and evidence capture before expiry.

## Report generation order (maintainer correction, 28 October)

Stop iterative manuscript/PDF amendments and rebuilds. Finish the code, dependency, site,
deployment and feasible control/evidence work first. Then reconcile the final evidence and
generate one clean technical report. The current report is an interim local draft; preserve
it uncommitted. Do not rebuild it as a routine gate during the remaining implementation.
