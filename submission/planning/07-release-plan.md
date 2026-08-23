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

`v0.3.0` is the next candidate because changes after `v0.2.1` add a public evidence surface,
keyless deployment, release-log redaction, a measured request-path visual, and new documentation
and CI enforcement. A tag cannot contain uncommitted files. The release order is therefore:

1. commit the evidence-console source, safety gate, and documentation corrections;
2. complete and observe the hosted evidence gate above;
3. add the verified production URL, change the changelog heading from `Unreleased` to `0.3.0`,
   and bump `pyproject.toml` to `0.3.0`;
4. run every offline, live, version-upstream, rollback, teardown, and snapshot gate;
5. commit and push the release metadata, then verify `main` CI green;
6. create an annotated `v0.3.0` tag at that exact commit and push the tag separately.
