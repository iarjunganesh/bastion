## Appendix A. Reproducibility and version provenance

### A.1 Source and deployment

| Fleet | Source | Deployed | Used by |
|---|---|---|---|
| August–October | Revision `c81b4af` route; Cloud Run image built 23 Aug (Python 3.12.14, `google-adk` 2.7.1, `a2a-sdk` 1.1.2, 161 distributions) | Aug 2026 | E10–E14, cohort N (E16–E23) |
| 5 Nov upgrade | Base `d7d6a99` plus a hashed SDK-access overlay; recovery adds the exact quoted-routing parser correction; `google-adk` 2.13.0 asserted in build | 5 Nov | F (E24), recovery (E25) |
| v0.9.0 | Tag `v0.9.0` (`be5c621`), 52-file clean export; image `sha256:bf3a89dc…`; `google-adk` 2.14.0, `a2a-sdk` 1.3.0, SDK 2.6.0 asserted in build | 7 Nov (Runtime ready 19:30:14Z) | G, H (E26) |
| v0.9.1 | Tag `v0.9.1` (`755dd07`), 53-file clean export; image `sha256:435604e0…`; same in-build assertion | 7 Nov (Runtime ready 22:53:07Z) | I–M (E26–E29) |

- L and M created Auditor revisions 00036–00039 on the same image digest. After each restore, the configuration was verified identical to the original.
- The Runtime's installed packages were never read independently. The Runtime declares Python 3.12 and its requirements file, not its installed resolution.
- The v0.8.0 release tag (`4d70b1b`) was not deployable as tagged. Its Runtime client calls are absent from its own pinned SDK, and a hand-written test double hid the gap. The 5 November deployments used later source. [S14]

### A.2 Build and source manifest

This report was built offline from canonical sections. Repository links point at the public base revision named in the cited-source manifest. That link base, `aa398f6`, is a later documentation and teardown revision than the deployed `v0.9.1` (`755dd07`). Their production code differs only by a docstring correction in `infrastructure/agent_server.py` (S12), which removes an unsupported cause, and by the teardown script, which this report does not cite. Files whose bytes differ from that revision are not linked under it; they are identified as local snapshot sources. The builder records full hashes of the cited repository files and retains those files in a source snapshot. The report's canonical sources, build inputs and publication manifest are released under the tag `report-2026-11`. Repository links stay pinned to the immutable base commit, whose cited bytes the manifest verifies. The report is archived on Zenodo (DOI 10.5281/zenodo.24120596). Its text and figures are licensed under CC BY 4.0; the bundled code keeps its MIT licence.

### A.3 Offline checks

```text
ruff check . && ruff format --check .
mypy agents gateway identity registry runtime model_armor observability infrastructure
pytest tests --cov --cov-fail-under=100        # 398 core cases
python scripts/check_docs.py
python scripts/check_versions.py
python scripts/check_site.py
```

The O1 reproduction of the A2A state boundary needs no credentials. Build a Python 3.12 environment from `requirements.lock` and run the script from E22.

### A.4 Fleet end state (D4, 9 November 2026)

After the evaluation, the fleet was retired under separate approvals. Before any deletion, the following were preserved and verified:

- the sealed G–M records;
- the non-acknowledging dead-letter inspection (Appendix C.4);
- both deployed images, exported by digest and read back layer by layer;
- the cohort build sources, matched byte for byte against their source manifests.

An encrypted off-laptop backup was verified independently.

- **Teardown.** An inventory-first, allowlisted teardown deleted 25 of its 26 serving targets: the Eventarc trigger, the dead-letter review subscription, two topics, four Cloud Run services and seventeen Agent Registry entries. The Agent Gateway is retained: its deletion was refused (`FAILED_PRECONDITION`) and the run was not retried. Read-only checks then found that a retained Runtime engine references it and that an authorisation policy targets it; the cause of the refusal is not established.
- **Storage.** The image repository and both build buckets were deleted.
- **Billing.** D4 disconnected billing from the Bastion project only; it made no change to the billing account itself or to any other project. Charges incurred earlier may still post.
- **Retained.** The Gateway with its authorisation policy and extension, two Runtime engines with their sessions and memory, Firestore, two secrets, the audit log bucket, service accounts and IAM. With billing disconnected, these may become inaccessible.

### A.5 Provenance and assistance

This report supersedes the author's earlier account of the A2A failure (S11, 29 August 2026) and the local drafts of 6–7 November, which were never published as editions. Generative AI tools assisted with drafting, organisation, citation lookup, collection and verification code, and document preparation. The author is responsible for the content. No AI tool is listed as an author, and no independent peer review is claimed.
