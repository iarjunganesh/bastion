# Publication manifest: `report-2026-11`

**Status: proposed, awaiting the maintainer's approval.** Nothing has been tagged, released,
deposited or announced. Approving this manifest together with the manuscript authorises the
release steps below; each external step still runs only on that approval.

## Work

| Field | Value |
|---|---|
| Title | *Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed Agent Fleet* |
| Author | Arjun Ganesh |
| Affiliation | Independent researcher, Stockholm |
| Date | November 2026 |
| Type | Technical report; not peer reviewed (AI assistance disclosed in Appendix A.5) |
| Release tag | `report-2026-11` |
| Repository link base | `aa398f6953de6dd3d56d84b2ae981a4a06591474` (immutable; every cited file byte-identical) |
| Deployed system described | `v0.9.0` (`be5c621`) and `v0.9.1` (`755dd07`) |

## Release artifacts

Built on 10 November 2026 from the sources in this directory. Record:
[qa/release-build-2026-11-10.md](qa/release-build-2026-11-10.md).

| Artifact | Published as | SHA-256 |
|---|---|---|
| `bastion-technical-report-2026-11.pdf` (25 pages, 740,892 bytes) | GitHub release asset; Zenodo file | `75c57e3aab8f19af1b39cec7b6a28385e6df1f92865928e0707c345e01b223d2` |
| `source-manifest.json` | GitHub release asset; Zenodo file | `549e61a4d2fa4ceded6b00c65329da7c93f64fd3cb6ede5a9148fceb9b4772d2` |
| `source-snapshot.zip` (71 members: cited public files, build inputs, manifest) | GitHub release asset; Zenodo file | `bde01b6375a856809aedb3389c4c21ad06a5c4b57cec1498a2005627e9c1d94c` |
| `figures/figure1-topology.png` | In the tagged tree | `56160fae4551924b8467d31b7a42c12f19f4c8a8f0fc74c49c0702552af4f40d` |
| `figures/figure2-chronology.png` | In the tagged tree | `66e5ae34d1b173f6aa1982561ab4ec77b64543953609b5ec2b318fbff750f8ba` |
| `figures/figure3-timeout.png` | In the tagged tree | `1d6207266b19e4ed7f768f894ea1d83bfccbf1faf521e09d201b18c2c4fba4b0` |
| `OUTLINE.md` (frozen blueprint) | In the tagged tree | `fae36638d94e567cc3888e37af0c65c177efe7f07d3a23be9d72ddee59259015` |

The PDF and ZIP embed timestamps, so a rebuild produces different bytes. The source manifest is
the reproducibility anchor: each snapshot member and cited file must hash to its entry.

## What is published

- **The tagged tree** (`report-2026-11` on the merge commit that adds this directory):
  canonical sections, build and figure scripts, report tests, figures, the frozen blueprint,
  this manifest and the review records in `qa/` (Markdown and JSON receipts only).
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
| Creator | Arjun Ganesh; affiliation "Independent researcher" |
| Description | The report abstract, followed by the Section 8 scope statement |
| Keywords | AI agents; agent security; distributed systems; execution boundaries; data minimisation; IAM; failure analysis; fault injection |
| Related identifiers | GitHub release `report-2026-11` (is supplemented by); repository `iarjunganesh/bastion` |
| Version | `report-2026-11` |
| Licence | **Maintainer decision** (see below) |

Recommended method: a **manual upload** of the three artifacts, so the record contains exactly
the hashed files. The GitHub–Zenodo integration would instead archive the whole tagged
repository and requires enabling the repository in Zenodo, an external account setting.

The DOI is not printed in the PDF. If the maintainer wants it printed, reserve the DOI in
Zenodo first; that needs one more rebuild and new hashes in this manifest.

## Decisions for the maintainer

1. Approve the manuscript (the PDF above).
2. Approve this manifest.
3. Choose the report licence. Recommended: **CC BY 4.0** for the report text and figures; the
   repository code stays MIT. Alternative: MIT for everything, as the repository licence.
4. Choose the Zenodo method (manual upload recommended) and whether the DOI is printed in the PDF.

## Release steps after approval

1. Merge the report-sources PR. Confirm that `git ls-files report` lists the sources and that
   regenerated artifacts still match the hashes above, or rebuild and update this manifest.
2. Create the annotated tag `report-2026-11` on that merge commit and push it.
3. Create the GitHub release from the tag; attach the three artifacts; verify their downloaded
   SHA-256 values against this table.
4. Deposit on Zenodo with the metadata above; record the DOI.
5. Update the site and README with the DOI and release links in a normal PR (the site deploys
   from `main`).
6. Record the tag, release URL and DOI in `HANDOFF.md` and the report plan.

No new experiment, evidence change or retrospective edit of sealed records is part of this
release.
