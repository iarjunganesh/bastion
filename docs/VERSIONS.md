# Versions and evidence provenance

This table separates the source target from measured deployments. Updated 4 November 2026.
`requirements.txt` supplies source dependency pins; observations supply deployment facts.

| Scope | Framework / revision | What the evidence establishes |
|---|---|---|
| Release v0.8.0 (current source) | Google ADK 2.13.0; A2A SDK 1.3.0; Python 3.12 | Locked offline suite (321 cases at release), 100% core coverage; production upgrade not established |
| Submitted v0.7.0 tree | `google-adk` v2.8.0 source pin | Historical submission source, distinct from its deployed resolution |
| August fleet observations | Recorded `google-adk` v2.7.1 resolution deployed by v0.4.0 | Dated observations; evidence 11–13 identify code revision `c81b4af` |
| 27 October study | Same worker revisions and Runtime update metadata as August | 20 completed investigations; installed packages were not freshly inventoried |
| Cohort N, 3–4 November | Same deployment. Serving image (one digest, all four Cloud Run services, built 23 Aug) read 4 Nov: Python 3.12.14, 161 distributions, `google-adk` 2.7.1, `a2a-sdk` 1.1.2, requirements identical to commit `f589b25` | Evidence 16–21. The managed Runtime reports Python 3.12 and `requirements.txt` but not its installed resolution |
| Offline O1, 4 November | `google-adk` 2.13.0, `a2a-sdk` 1.3.0 from `requirements.lock`, Python 3.12 | Evidence 22: A2A state boundary reproduced; both upstream warnings fire |
| Upgraded deployment | Pending: cohort F, 8–10 November | Must verify all four Cloud Run services and managed Runtime, then record exact revisions/resolution |

ADK 2.13.0 is the latest stable release checked on 28 October against
[PyPI](https://pypi.org/project/google-adk/2.13.0/) and
[the upstream release](https://github.com/google/adk-python/releases/tag/v2.13.0).
It requires newer Google SDK components and changes the default GenAI telemetry schema.
Warnings added in `google-adk` v2.12.0 do not change per-agent A2A session semantics;
explicit message/receipt contracts remain necessary.

Historical evidence files, release notes, and incident reproductions retain their actual
versions. New validation belongs in a separate dated cohort. Never edit old bundle bytes,
replace old version labels with current pins, or infer deployment from a README badge.

The report's Section 4.1 contains its cohort table. Release/source changes do not upgrade
the framework version of any measurement already in the report.

v0.8.0 is released as source with one accepted advisory ([dependency status](DEPENDENCY-STATUS.md)).
It does not upgrade production: the fleet still runs its August deployment (verified 28 October).
