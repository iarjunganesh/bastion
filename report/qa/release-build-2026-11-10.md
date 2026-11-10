# Release build record — 10 November 2026

This is the build proposed for `report-2026-11`. It follows the verified review build
(`f3b2bb95…9071`, see `final-closeout-2026-11-10.md`) and changes only release presentation.
No finding, claim, figure or evidence statement changed.

## Changes from the verified build

| Change | Source | Effect in the PDF |
|---|---|---|
| Running header reads `report-2026-11` instead of `Review draft` | `build_report.py` | Every page header |
| Appendix A.2 states that sources, build inputs and the publication manifest are released under `report-2026-11`, with links pinned to the immutable base commit | `sections/appendix-a-reproducibility.md` | p.20 |
| The generated provenance line describes the manifest's scope instead of disclaiming public release | `build_report.py` | p.20, with the new manifest hash |
| One line wrapped in `test_build_report.py` (lint only) | `test_build_report.py` | None |

Repository links remain pinned to base commit `aa398f6953de6dd3d56d84b2ae981a4a06591474`.
Every cited file is byte-identical there (no local-snapshot overlay), and since that commit only
`HANDOFF.md` and the report plan have changed in the repository. A commit hash is a more
immutable link target than a tag, so the links were not moved.

## Verification

- **Page-by-page comparison with the verified build:** the PDF text layer differs only in the
  header, the A.2 sentence and provenance line, and a reflow (one A.4 bullet moves from p.20 to
  p.21; Appendix B's E19 row from p.21 to p.22). All 62 link targets and all embedded figure
  images are identical per page. The figure PNGs are byte-identical.
- **Visual inspection:** pages 1, 20, 21 and 22 in full at the 1.5× render. Table headers repeat
  across the p.21–22 split. The other pages are unchanged from the verified build, which
  received a full 25-page inspection, apart from the header.
- **Build checks:** 17 report checks pass; automated layout findings are empty; 25 pages.
- **Integrity:** all 70 source-manifest entries match the files and the snapshot members; the
  ZIP CRC passes; no overlay. The frozen outline, Appendix C stop/amendment rows and the C.4
  dead-letter table are unchanged. The statistical illustration stays in §§5.7 and 8.
- **Privacy:** finite pattern checks over the manuscript, PDF text, metadata, links and every
  report text file to be committed returned zero hits. Details and limits are in
  `release-integrity.json`.

## Artifacts

| Artifact | SHA-256 |
|---|---|
| `bastion-technical-report-2026-11.pdf` (740,892 bytes) | `75c57e3aab8f19af1b39cec7b6a28385e6df1f92865928e0707c345e01b223d2` |
| `source-manifest.json` | `549e61a4d2fa4ceded6b00c65329da7c93f64fd3cb6ede5a9148fceb9b4772d2` |
| `source-snapshot.zip` (71 members) | `bde01b6375a856809aedb3389c4c21ad06a5c4b57cec1498a2005627e9c1d94c` |

The PDF and the snapshot ZIP embed timestamps and are not byte-reproducible; the source
manifest is the reproducibility anchor. AI assistance is disclosed in Appendix A.5; no
independent peer review is claimed. Publication requires the maintainer's approval of the
manuscript and of `../PUBLICATION-MANIFEST.md`.
