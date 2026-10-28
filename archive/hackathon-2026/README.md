# All Things Agentic Hackathon 2026 — archived submission material

Bastion was built for, and submitted to, the All Things Agentic Hackathon 2026 (Fortified
Enterprise Fleet track) on 2026-08-29. Judging has closed and no award is claimed. The project now
continues as a technical report; this folder keeps the submission-only material out of the way
of that work without deleting the record.

Everything here is frozen. Files were moved, not rewritten: only their repository paths and the
links between them were updated so that they still resolve. The exact submitted tree is the
`v0.7.0` tag, which keeps every file at its original location.

## Contents

| Path | What it is |
|---|---|
| [Official brief](./submission/DEVPOST.md) | Captured official hackathon brief |
| [Devpost description](./submission/DEVPOST_README.md) | Project description as submitted |
| [Submission ledger](./submission/SUBMISSION.md) | Submission ledger: engineering proof versus publication tasks |
| [Article source](./submission/ARTICLE_DRAFT.md) | Source of the dev.to article on A2A state loss, published 2026-08-29 |
| Other files in `submission` | Demo script, capture runbook, social copy |
| [Planning documents](./submission/planning/) | Judging matrix, build/release plans, project review, reproducibility (00–07, 10) |
| [Devpost worksheet](./devpost-submission.md) | Field-by-field worksheet for the Devpost form |
| [Gallery screenshots](./assets/screenshots/README.md) | The five Devpost gallery images |
| Demo video and voiceover folders under `assets` | Captions, stills and narration of the demo video (the MP4 master is ignored) |
| Devpost thumbnail under `assets/brand` | Devpost thumbnail |
| `scripts` folder | Demo-video tooling: narration, capture hook and assembly |

The demo video is published at [youtu.be/Xpj8YmzFfpk](https://youtu.be/Xpj8YmzFfpk) and the entry at
[devpost.com/software/bastion-pfuy71](https://devpost.com/software/bastion-pfuy71).

## What deliberately stayed in place

The Devpost page and the public evidence console link to files on `main`, so these were not moved:
the architecture images under `assets/architecture/`, the evidence records under `assets/evidence/`,
[`assets/README.md`](../../assets/README.md), [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md),
the brand banners and `LICENSE`.

Three planning ledgers are still in active use by the technical report and moved to
[`docs/research/`](../../docs/research/claim-matrix.md) instead of here: the claim matrix
(formerly `planning/11`), the P0/P1 remediation ledger (`planning/08`) and the observation
backlog (`planning/09`).

## Rebuilding the demo media

The scripts here resolve paths relative to this folder, but the video also draws on the
architecture and evidence assets that stayed in place, so they are kept as a record rather than
as working tools. To rebuild the narration or the cut, check out `v0.7.0` and follow the
archived [demo script](./submission/DEMO_SCRIPT.md). The redaction gate still covers the archived
gallery and stills because they remain public in this repository.
