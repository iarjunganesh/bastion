# Publication manifest: `report-2026-11`

**Status: published.** Zenodo record [https://zenodo.org/records/24120596](https://zenodo.org/records/24120596), DOI
[10.5281/zenodo.24120596](https://doi.org/10.5281/zenodo.24120596), published 10 November. The maintainer approved the
manuscript and this manifest with the three final hashes on 10 November. The annotated tag
`report-2026-11` points to the PR #20 merge commit `e9e86b0f46e2cc1ba50897de7dff4f3104117b95`.
The [GitHub release](https://github.com/iarjunganesh/bastion/releases/tag/report-2026-11) carries the three artifacts; their downloaded SHA-256 values match
the table below. The three files downloaded from the Zenodo record match the same hashes
(and the MD5 values Zenodo lists), and the DOI resolves to the record. PR #18 merged the report sources on 10 November at
`41f292f54493925526d043def10c493768080bf0`. Any change to the artifact bytes would need renewed
approval (step 1).

## Work

| Field | Value |
|---|---|
| Title | *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed Agent Fleet* |
| Author | Arjun Ganesh (ORCID [0009-0004-4720-7057](https://orcid.org/0009-0004-4720-7057)) |
| Affiliation | Independent researcher, Stockholm |
| Date | November 2026 |
| Type | Technical report; not peer reviewed (AI assistance disclosed in Appendix A.5) |
| Licence | CC BY 4.0 for report text, figures and evidence records; MIT for code (`../LICENSE-CONTENT.md`) |
| Release tag | `report-2026-11` |
| DOI | [10.5281/zenodo.24120596](https://doi.org/10.5281/zenodo.24120596) (reserved; printed in the PDF; resolves after publication) |
| Repository link base | `aa398f6953de6dd3d56d84b2ae981a4a06591474` (immutable; every cited file byte-identical) |
| Deployed system described | `v0.9.0` (`be5c621`) and `v0.9.1` (`755dd07`) |

## Release artifacts

Final build, 10 November 2026; record:
[qa/release-build-2026-11-10.md](qa/release-build-2026-11-10.md) (section "Final build"). It
replaces the release candidate `81c2dfce…0706`, which the release review verified.

| Artifact | Published as | SHA-256 |
|---|---|---|
| `bastion-technical-report-2026-11.pdf` (25 pages, 741,684 bytes) | GitHub release asset; Zenodo file | `ec710124910bba89dcb4fd3bbd769f714347074f3989869c00b74f31a013dcb3` |
| `source-manifest.json` (72 entries) | GitHub release asset; Zenodo file | `b8606936efff176be3b89f2de77fa6fec59095530ff235ad66c5fb6aebbf891a` |
| `source-snapshot.zip` (73 members, including `LICENSE` and `LICENSE-CONTENT.md`) | GitHub release asset; Zenodo file | `3433623337a5069130fbfb1f545fdc1ef4cca6a4325fce588d5ad59e1515a912` |
| `figures/figure1-topology.png` | In the tagged tree | `56160fae4551924b8467d31b7a42c12f19f4c8a8f0fc74c49c0702552af4f40d` |
| `figures/figure2-chronology.png` | In the tagged tree | `66e5ae34d1b173f6aa1982561ab4ec77b64543953609b5ec2b318fbff750f8ba` |
| `figures/figure3-timeout.png` | In the tagged tree | `1d6207266b19e4ed7f768f894ea1d83bfccbf1faf521e09d201b18c2c4fba4b0` |
| `OUTLINE.md` (frozen blueprint; LF bytes as committed) | In the tagged tree | `fae36638d94e567cc3888e37af0c65c177efe7f07d3a23be9d72ddee59259015` |

The PDF and ZIP embed timestamps, so a rebuild produces different bytes. The source manifest is
the reproducibility anchor: each snapshot member and cited file must hash to its entry.

`source-snapshot.zip` is a manifest-verifiable subset, not a standalone checkout. Rebuilding or
running the report checks requires a complete checkout of the final report tag, Git history
containing the pinned link-base commit, and the five public files in
`assets/evidence/live-validation-2026-10-27/`. The builder independently pins that supplement's
ZIP at SHA-256 `3f9acf4c82f390cd25091ec684c8a195af36388592363916742a6607e4a7d80c`.

## Licence scope

The source snapshot includes the repository's MIT copyright and permission notice (`LICENSE`)
and the content-licence notice (`LICENSE-CONTENT.md`). CC BY 4.0 applies to the report text and
figures and to the evidence records; bundled repository code, including the report scripts,
keeps its MIT notice. The Zenodo record lists both CC BY 4.0 and MIT, with these scopes stated
in its description.

## What is published

- **The tagged tree** (`report-2026-11`): canonical sections, build and figure scripts, report
  tests, figures, the frozen blueprint, this manifest, the licence notices and the review
  records in `qa/` (Markdown and JSON receipts only).
- **The GitHub release:** the three artifacts above, with release notes summarising the abstract
  and the scope boundary from Section 8.
- **The Zenodo record:** the same three files and the metadata below.

## What stays private

These are never published, attached or summarised beyond what the report already states:
measurement collectors and raw captures (`.local/measurements/`), the seal files (their hashes
are public in E26–E29), the dead-letter inspection's raw pull responses, D4 teardown records and
exported images, billing records and credit values, local drafts and archives, review notes and
any private correspondence. The source snapshot contains no `.local` path; the builder refuses one.

## Zenodo deposit

| Field | Value |
|---|---|
| Resource type | Publication → Report |
| DOI | `10.5281/zenodo.24120596` (reserved in the draft) |
| Creator | Arjun Ganesh (ORCID 0009-0004-4720-7057); affiliation "Independent researcher, Stockholm" |
| Description | The report abstract, the Section 8 scope statement and the licence scopes above |
| Keywords | AI agents; agent security; distributed systems; execution boundaries; data minimisation; IAM; failure analysis; fault injection |
| Related identifiers | GitHub release `report-2026-11` (is supplemented by); repository `iarjunganesh/bastion` |
| Version | `report-2026-11` |
| Licences | CC BY 4.0 (report and evidence records) and MIT (bundled code) |

Method: a **manual upload** of the three artifacts, so the record contains exactly the hashed
files. The GitHub–Zenodo integration would instead archive the whole tagged repository and
requires enabling the repository in Zenodo, an external account setting.

The DOI is printed in the PDF. This was chosen before final artifact approval: the maintainer
reserved `10.5281/zenodo.24120596` in a Zenodo draft without publishing, and the final build
includes it. The maintainer approved the final artifact hashes above before the tag was
created. The Zenodo GitHub integration must stay off for
`iarjunganesh/bastion` until the release is complete, so the GitHub release does not create a
second Zenodo record.

## Decisions for the maintainer

1. Approved 10 November: the manuscript (the final PDF, by hash).
2. Approved 10 November: this manifest with the final hashes.
3. Decided 10 November: **CC BY 4.0** for the report and evidence records, MIT for code.
4. Decided 10 November: **manual Zenodo upload**, with the **DOI printed in the PDF**.

## Release steps after approval

1. Confirm the final reviewed release commit, passing CI, tracked report inputs and the SHA-256
   values of the preserved release artifacts. Do not rebuild as a routine release check. If any
   artifact bytes change, stop: update this manifest and the release receipts, verify the
   permitted text/link/image differences and changed-page layout, rerun the applicable
   integrity/privacy checks, and obtain the maintainer's approval of the new hashes before
   tagging or uploading.
2. Create and push the annotated `report-2026-11` tag on that exact reviewed merge commit,
   including any approved release fixes. Record its full commit ID in the approval record and
   the GitHub release notes.
3. Create the GitHub release from the tag; attach the three artifacts; download them and verify
   their SHA-256 values against this manifest.
4. Complete the reserved Zenodo technical-report draft with exactly the same three approved
   artifacts. Confirm completed uploads, filenames, sizes, metadata, licence scope and the DOI
   before publishing. Publish under the maintainer's approval, record the record URL and DOI,
   then download all three files and compare their SHA-256 values with this manifest. If any
   differ, report the mismatch and stop the announcement and site steps.
5. Update the site and README with the DOI and release links in a normal PR (the site deploys
   from `main`).
6. Record the tag, release URL and DOI in `HANDOFF.md` and the report plan.

No new experiment, evidence change or retrospective edit of sealed records is part of this
release.
