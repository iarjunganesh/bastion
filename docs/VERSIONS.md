# Versions and evidence provenance

This table separates the source target from measured deployments. Updated 6 November 2026.
`requirements.txt` supplies source dependency pins; observations supply deployment facts.

| Scope | Framework / revision | What the evidence establishes |
|---|---|---|
| Released v0.8.0, 28 October | Tag `v0.8.0` at `4d70b1ba81b0c37b5cbd55223b93f651855de0d9`; Google ADK 2.13.0, A2A SDK 1.3.0, Python 3.12 | Source release, with 321 cases at release and 100% core coverage. The tag itself did not deploy production; the 5 November descendants and overlays are recorded separately below |
| Submitted v0.7.0 tree | `google-adk` v2.8.0 source pin | Historical submission source, distinct from its deployed resolution |
| August deployment provenance | Evidence 11–13 identify code revision `c81b4af`; E23 later measures the Cloud Run image's `google-adk` 2.7.1 resolution | Dated route observations; the managed Runtime's installed packages were not read back |
| 27 October study | Same worker revisions and Runtime update metadata as August | 20 completed investigations; installed packages were not freshly inventoried |
| Cohort N, 3–4 November | Same deployment. Serving image (one digest, all four Cloud Run services, built 23 Aug) read 4 Nov: Python 3.12.14, 161 distributions, `google-adk` 2.7.1, `a2a-sdk` 1.1.2, requirements identical to commit `f589b25` | Evidence 16–21. The managed Runtime reports Python 3.12 and `requirements.txt` but not its installed resolution |
| Offline O1, 4 November | `google-adk` 2.13.0, `a2a-sdk` 1.3.0 from `requirements.lock`, Python 3.12 | Evidence 22: A2A state boundary reproduced; both upstream warnings fire |
| Upgraded deployment, 5 November | Evidence 24: four existing Cloud Run services serve one new digest; its in-build container check asserted `google-adk` 2.13.0, `a2a-sdk` 1.3.0 and SDK 2.6.0. Existing Runtime source updated separately with Python 3.12 and `requirements-runtime.txt` | Protected configuration verified. Pilot stopped on quoted-routing parsing; no positive completion closure. Runtime installed packages remain unreadable. Source is `d7d6a99` plus the explicitly hashed SDK-access overlay, not an unchanged release tag |
| Corrected F recovery, 5 November | Evidence 25: one new image, four existing image updates, same asserted ADK/A2A/SDK pins; source delta is the exact Escalation quoted-routing parser correction | Runtime resource/graph unchanged from E24; five normal cases, direct confirmation control and two replays passed. Refusal join verified via read-only addendum after collector false positive. Runtime packages still unreadable; original failed F retained separately |

ADK 2.13.0 is the latest stable release checked on 28 October against
[PyPI](https://pypi.org/project/google-adk/2.13.0/) and
[the upstream release](https://github.com/google/adk-python/releases/tag/v2.13.0).
It requires newer Google SDK components and changes the default GenAI telemetry schema.
Warnings added in `google-adk` v2.12.0 do not change per-agent A2A session semantics;
explicit message/receipt contracts remain necessary.

Historical evidence files, release notes, and incident reproductions retain their actual
versions. New validation belongs in a separate dated cohort. Never edit old bundle bytes,
replace old version labels with current pins, or infer deployment from a README badge.

The report's Section 5 contains its cohort method; Appendix A records version provenance. Release/source changes do not upgrade
the framework version of any measurement already in the report.

v0.8.0 is released as source with one accepted advisory ([dependency status](DEPENDENCY-STATUS.md)).
The release itself did not upgrade production. Evidence 24 records the separate 5 November
deployment and stopped pilot; cohort N retains its unchanged August provenance.
