# Technical report

These are the canonical sources for the one definitive report, *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed Agent Fleet*. It is written from the blueprint frozen on 9 November 2026 (`OUTLINE.md`). The drafts of 6–7 November are archived privately outside the repository; they are not editions.

| File | Purpose |
|---|---|
| `sections/` | Ordered manuscript sections (§1–10), appendices A–C and references |
| `OUTLINE.md` | Frozen blueprint |
| `make_figures.py`, `figures/` | Deterministic Pillow renderings of Figures 1–3 |
| `build_report.py` | Offline assembly, source snapshot, PDF and layout validation |
| `test_build_report.py` | Integrity, citation, statistic-placement and table-layout checks |
| `PUBLICATION-MANIFEST.md` | Release artifacts, their hashes, what is published and what stays private |
| `qa/` | Review records, the claim reconciliation and machine-readable build receipts |

Generated outputs are not tracked: the PDF (`bastion-technical-report-2026-11.pdf`), `manuscript.md`, `source-manifest.json`, `source-snapshot.zip` and the rendered QA pages. The release attaches the PDF, source manifest and source snapshot. The snapshot is a
manifest-verifiable subset, not a standalone checkout: rebuilding needs the full tagged
checkout, Git history containing the pinned link-base commit, and the public live-validation
files in `assets/evidence/live-validation-2026-10-27/`.

Review history: the 9 November review and its original findings are in
[qa/final-review-2026-11-09.md](qa/final-review-2026-11-09.md); the
[10 November closeout](qa/final-closeout-2026-11-10.md) records all 16 follow-up findings as
verified. The [release build record](qa/release-build-2026-11-10.md) documents the release candidate and
the final build, which added the reserved DOI, ORCID iD and licence line. The frozen blueprint and evidence are unchanged.

Use Python 3.12 in a separate build environment. These dependencies are never shipped to the fleet.

```powershell
uv venv --python 3.12 .local/report-build-venv
uv pip install --python .local/report-build-venv/Scripts/python.exe -r report/requirements-build.txt
$env:PYTHONPATH = "$PWD;$PWD/report"
./.local/report-build-venv/Scripts/python.exe -m unittest discover -s report -p test_build_report.py
./.local/report-build-venv/Scripts/python.exe report/make_figures.py
./.local/report-build-venv/Scripts/python.exe report/build_report.py
```

The report text, figures and review records are licensed under CC BY 4.0 and the build scripts under MIT; see [LICENSE-CONTENT.md](../LICENSE-CONTENT.md).

The builder reads Windows system fonts (Times New Roman, Arial). The report was released on 10 November as [`report-2026-11`](https://github.com/iarjunganesh/bastion/releases/tag/report-2026-11) after the maintainer approved the manuscript and the publication manifest. Do not move the tag, replace its assets or rebuild the released PDF. See the [report plan](../docs/research/report-plan.md).
