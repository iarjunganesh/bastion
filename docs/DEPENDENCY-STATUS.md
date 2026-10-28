# Dependency status — 28 October 2026

v0.8.0 is released with **one accepted advisory**. Every other known vulnerability in the locked
graph is fixed, and the CI audit fails on any new one. Removal is tracked in
[issue #3](https://github.com/iarjunganesh/bastion/issues/3).

| Package | Locked | Advisory | Fixed in | Why it stays |
|---|---|---|---|---|
| `opentelemetry-api` | 1.44.0 | CVE-2026-114603 / GHSA-xcq7-p3pf-p88h | 1.45.1 | Every `google-adk` release caps OpenTelemetry below the fix: v2.8.0–v2.12.0 at ≤1.42.1 and 2.13.0 at ≤1.44 (checked on PyPI 28 October) |

## Risk acceptance

The [upstream advisory](https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-xcq7-p3pf-p88h)
describes excessive CPU use while parsing malformed inbound `tracestate` headers. For Bastion:

- **Availability only.** The flaw cannot expose data, change findings or touch IAM, which
  Bastion can only read.
- **Authenticated callers only.** The dispatcher has internal-only ingress and every Cloud Run
  service requires an identity token (fleet verifier, 28 October); the managed Runtime is reached
  only through the dispatcher. Bastion's own code configures no inbound trace propagation, but
  ADK and A2A internals were not proven never to parse the header.
- **No new exposure from this release.** v0.8.0 changes source and the public console only. The
  deployed fleet still runs its August image, whose older OpenTelemetry is also below the fix.
- A stalled worker delays an investigation; the durable lifecycle retries it rather than
  completing it without receipts.

Accepted by the maintainer on 28 October 2026. The CI audit and `make audit-dependencies` skip
exactly this ID. Remove the skip as soon as an ADK release admits `opentelemetry-api` 1.45.1,
then relock and re-audit; check again before any redeploy of the fleet.

## How the lock got here

The first CI audit of the ADK 2.13.0 upgrade found several vulnerable transitive packages. The
refreshed universal Python 3.12 lock updated them, removed unused ADK evaluation extras from the
shipped fleet and raised the media dependency to Pillow 13.0.0, leaving only the advisory above.
No requirement metadata was edited, no `--no-deps` install was used and no incompatible resolver
override was added. A locally rebuilt ADK wheel with a relaxed bound was explored and not adopted.
