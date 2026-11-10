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
| One line wrapped; the path-refusal test no longer names a private file | `test_build_report.py` | None |
| The live-validation check compares LF-normalised public captures with the exact-byte-verified bundle members, so an LF checkout no longer fails; one test added (PR #18 review comment) | `build_report.py`, `test_build_report.py` | None; only the manifest hash on p.20 changes |

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
- **Build checks:** 18 report checks pass; automated layout findings are empty; 25 pages.
- **Integrity:** all 70 source-manifest entries match the files and the snapshot members; the
  ZIP CRC passes; no overlay. The frozen outline, Appendix C stop/amendment rows and the C.4
  dead-letter table are unchanged. The statistical illustration stays in §§5.7 and 8.
- **Privacy:** finite pattern checks over the manuscript, PDF text, metadata, links and every
  report text file to be committed returned zero hits. Details and limits are in
  `release-integrity.json`.

## Artifacts

| Artifact | SHA-256 |
|---|---|
| `bastion-technical-report-2026-11.pdf` (740,890 bytes) | `81c2dfce5886426bde5ee81f5db461d2c83dc79a37b3c949c066f94c6220c706` |
| `source-manifest.json` | `0e399dc83af237e7df127dd5ec8dd2b95017d40810daf8136ab1d2863c46a342` |
| `source-snapshot.zip` (71 members) | `4c2e6b489028c6c64b24b25475d13c2b52b9a3aea15834979be5a90716c77732` |

The PDF and the snapshot ZIP embed timestamps and are not byte-reproducible; the source
manifest is the reproducibility anchor. AI assistance is disclosed in Appendix A.5; no
independent peer review is claimed. Publication requires the maintainer's approval of the
manuscript and of `../PUBLICATION-MANIFEST.md`.

## Final build — 10 November 2026

This build replaces the release candidate above (`81c2dfce…0706`), which the release review
verified. It follows the maintainer's decisions (CC BY 4.0 for report and evidence, MIT for
code, manual Zenodo upload, DOI in the PDF) and the review's packaging fix.

| Change | Source | Effect in the PDF |
|---|---|---|
| ORCID iD on the author line; reserved DOI and CC BY 4.0 on the date line, both linked | `sections/00-front.md` | p.1 (no added lines) |
| Appendix A.2 adds the Zenodo DOI and the licence scope | `sections/appendix-a-reproducibility.md` | p.20 |
| Provenance line names the snapshot's actual scope; the snapshot carries `LICENSE` and `LICENSE-CONTENT.md` | `build_report.py` (PR #19) | p.20, with the new manifest hash |

**Verification against the candidate:** page-by-page, the text layer differs only on p.1 and
p.20 as listed, plus reflow on pp.20–25 (one A.4 bullet, Appendix B row E18, Appendix C.1 row L,
the References heading and five reference entries move to the next page). Two links are added
on p.1; the other 62 link targets are unchanged and five move from p.24 to p.25. All embedded
figure images are byte-identical. Pages 1 and 20–25 were inspected in full: table headers repeat
across the pp.21–22 and pp.22–23 splits and p.25 ends cleanly. 19 report checks pass;
automated layout findings are empty; 25 pages, 64 links. All 72 manifest entries match the files
and the 73 snapshot members; the ZIP CRC passes; no overlay; the snapshot's `LICENSE` is
LF-normalised. The frozen outline is unchanged (`fae36638…9259015`, LF-normalised). Privacy
checks over the PDF, metadata, links, manuscript and committed report text returned zero hits.

| Final artifact | SHA-256 |
|---|---|
| `bastion-technical-report-2026-11.pdf` (25 pages, 741,684 bytes) | `ec710124910bba89dcb4fd3bbd769f714347074f3989869c00b74f31a013dcb3` |
| `source-manifest.json` (72 entries) | `b8606936efff176be3b89f2de77fa6fec59095530ff235ad66c5fb6aebbf891a` |
| `source-snapshot.zip` (73 members) | `3433623337a5069130fbfb1f545fdc1ef4cca6a4325fce588d5ad59e1515a912` |

The DOI link resolves only after the Zenodo record is published.
