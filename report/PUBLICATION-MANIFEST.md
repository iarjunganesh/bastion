# Publication manifest: `report-2026-11`

**Status: final build pending; awaiting the maintainer's approval.** Nothing has been tagged,
released, deposited or announced. PR #18 merged the report sources on 10 November at
`41f292f54493925526d043def10c493768080bf0`; that merge did not approve the manuscript or any
publication step. Approving this manifest together with the manuscript authorises the release
steps below for the exact artifact hashes listed; any change to those bytes needs renewed
approval (step 1).

## Work

| Field | Value |
|---|---|
| Title | *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed Agent Fleet* |
| Author | Arjun Ganesh |
| Affiliation | Independent researcher, Stockholm |
| Date | November 2026 |
| Type | Technical report; not peer reviewed (AI assistance disclosed in Appendix A.5) |
| Licence | CC BY 4.0 for report text, figures and evidence records; MIT for code (`../LICENSE-CONTENT.md`) |
| Release tag | `report-2026-11` |
| Repository link base | `aa398f6953de6dd3d56d84b2ae981a4a06591474` (immutable; every cited file byte-identical) |
| Deployed system described | `v0.9.0` (`be5c621`) and `v0.9.1` (`755dd07`) |

## Release artifacts

**Pending the final build.** The final build adds the reserved DOI and the licence line to the
title page, and the source snapshot gains the two licence notices. It therefore replaces the
release candidate below, which the 10 November release review verified
([qa/release-build-2026-11-10.md](qa/release-build-2026-11-10.md)). Its hashes describe that
candidate only and are kept for the record; the final hashes will replace this table.

| Artifact (release candidate, superseded) | Published as | SHA-256 |
|---|---|---|
| `bastion-technical-report-2026-11.pdf` (25 pages, 740,890 bytes) | GitHub release asset; Zenodo file | `81c2dfce5886426bde5ee81f5db461d2c83dc79a37b3c949c066f94c6220c706` |
| `source-manifest.json` | GitHub release asset; Zenodo file | `0e399dc83af237e7df127dd5ec8dd2b95017d40810daf8136ab1d2863c46a342` |
| `source-snapshot.zip` (71 members) | GitHub release asset; Zenodo file | `4c2e6b489028c6c64b24b25475d13c2b52b9a3aea15834979be5a90716c77732` |
| `figures/figure1-topology.png` | In the tagged tree | `56160fae4551924b8467d31b7a42c12f19f4c8a8f0fc74c49c0702552af4f40d` |
| `figures/figure2-chronology.png` | In the tagged tree | `66e5ae34d1b173f6aa1982561ab4ec77b64543953609b5ec2b318fbff750f8ba` |
| `figures/figure3-timeout.png` | In the tagged tree | `1d6207266b19e4ed7f768f894ea1d83bfccbf1faf521e09d201b18c2c4fba4b0` |
| `OUTLINE.md` (frozen blueprint) | In the tagged tree | `fae36638d94e567cc3888e37af0c65c177efe7f07d3a23be9d72ddee59259015` |

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
| Upload type | Publication → Technical report |
| Creator | Arjun Ganesh; affiliation "Independent researcher, Stockholm" |
| Description | The report abstract, the Section 8 scope statement and the licence scopes above |
| Keywords | AI agents; agent security; distributed systems; execution boundaries; data minimisation; IAM; failure analysis; fault injection |
| Related identifiers | GitHub release `report-2026-11` (is supplemented by); repository `iarjunganesh/bastion` |
| Version | `report-2026-11` |
| Licences | CC BY 4.0 (report and evidence records) and MIT (bundled code) |

Method: a **manual upload** of the three artifacts, so the record contains exactly the hashed
files. The GitHub–Zenodo integration would instead archive the whole tagged repository and
requires enabling the repository in Zenodo, an external account setting.

The DOI is printed in the PDF. This was chosen before final artifact approval: the maintainer
reserves the DOI in Zenodo without publishing; the final build includes it; its replacement-build
verification is completed; and the maintainer approves its new artifact hashes before the tag
is created or either record is published.

## Decisions for the maintainer

1. Approve the manuscript (the final PDF, by hash).
2. Approve this manifest with the final hashes.
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
