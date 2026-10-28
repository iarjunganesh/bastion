# Versions and evidence provenance

This table separates the source target from measured deployments. Updated 28 October 2026.
`requirements.txt` supplies source dependency pins; observations supply deployment facts.

| Scope | Framework / revision | What the evidence establishes |
|---|---|---|
| Current source / v0.8.0 target | Google ADK 2.13.0; A2A SDK 1.3.0; Python 3.12 | Locked offline suite: 321 passed, 100% core coverage; production upgrade not established |
| Submitted v0.7.0 tree | `google-adk` v2.8.0 source pin | Historical submission source, distinct from its deployed resolution |
| August fleet observations | Recorded `google-adk` v2.7.1 resolution deployed by v0.4.0 | Dated observations; evidence 11–13 identify code revision `c81b4af` |
| 27 October study | Same worker revisions and Runtime update metadata as August | 20 completed investigations; installed packages were not freshly inventoried |
| Upgraded deployment | Pending | Must verify all four Cloud Run services and managed Runtime, then record exact revisions/resolution |

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

The Python v0.8.0 release is currently blocked by the [dependency audit](DEPENDENCY-STATUS.md).
The static console can publish corrected dated evidence independently, and labels the source
version as release pending. No production upgrade or released tag is implied.
