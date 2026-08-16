# Release and submission plan

## Engineering release gate

1. Confirm `main` has only intended code, documentation, evidence, and user-owned visual changes.
2. Run Ruff, format, mypy, pytest/coverage, dependency audit, secret scan, docs/version checks, and
   diagram verification under Python 3.12.
3. Run live fleet verifier and production smoke with explicit regions/engine ID.
4. Confirm rollback and teardown dry runs list only exact Bastion targets.
5. Recapture count-only GCP state and check all Markdown figures/claims against it.
6. Commit new changes after `008ba20`; do not amend or squash into it.
7. Push `main` and verify GitHub Actions green.

## Submission gate

1. Re-read [DEVPOST.md](../DEVPOST.md) and fill the official form, category, links, and disclosures.
2. Publish a public English demo under four minutes.
3. Upload the architecture image/GIF and verify legibility at Devpost size.
4. Confirm the repository and services remain available through judging.
5. Submit before Aug 31, 2026, 5:00 PM PT.

Do not create or move a tag as part of the current engineering push. A release tag is a separate,
explicit decision after the final submission commit and changelog are verified.
