# Local preparation validation - 11 October 2026

Later local update: nine tests now pass, including wrong-project/quota-project
rejection, in-memory credential selection and strict response validation controls.
Ruff check/format remain passing. Global gcloud/saved ADC unchanged; no model call.
`config.json` records a 200 SEK ceiling but the paid runner/cost limiter is not built.
Batch ingestion/aggregation, human ratings and paid adapter remain next work.

Branch: `feature/bastion-report-local`, base `a0e08fc`, uncommitted local changes.
Python 3.12.12 from the existing Bastion environment; no dependency installation.

- Five unittest controls passed, including production-import detector parity for
  all 50 synthetic policies. Socket connections were denied during generation and
  parity checks; the live IAM fetch function was replaced by a rejecting fixture.
- Ruff check and format check passed for the experiment.
- Repository documentation gate passed; version gate passed (41 documents, 17 pins).
- Dataset generated reproducibly: 50 policies, 20-80 bindings; five clean controls.
- Five model conditions times three replicate IDs: 750 request envelopes. No
  network/model runner exists; no requests were dispatched. No cost was incurred.
- All 50 fixed-template controls preserved scoped canonical findings with no
  matched synthetic raw strings. This validates controls only, not model privacy
  or explanation quality.
- Repeated preparation produced identical dataset/request/control hashes. The
  generated manifest records those hashes and the production detector source hash.

Outputs are ignored in `.tmp/minimisation-preparation/` within the worktree.
Production detector code, main, GitHub and GCP were unchanged. No commit or push.
Full production tests/coverage and live reproduction were not run for this change.

Next: strict response ingestion/schema validation; expanded synthetic edge cases,
per-class string exposure, rating sheets and paired attack criteria; then an
explicitly authorized capped model runner. Current preparation is not C4 results.
