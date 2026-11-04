# Evidence 23 — deployment census and installed packages

**Collected:** 28 October 2026 (census, 19:23 UTC) and 4 November 2026 (packages), evidence
chunk E1 of cohort N. Read-only: Cloud Run, Agent Runtime, Firestore, Logging and Artifact
Registry reads. The IAM census used the Auditor's own fetch and detector with a throwaway
in-memory ID key, so no production secret was read. The private bundles keep counts, digests
and public package versions only.

## Deployment

| Fact | Value |
|---|---|
| Cloud Run services | 4, all serving one image digest (`sha256:dd9853bd…`) |
| Image built | 23 August 2026, 19:59 UTC |
| Image Python | 3.12.14 |
| Installed distributions (pip layer) | 161 |
| Key packages | `google-adk` 2.7.1, `a2a-sdk` 1.1.2, `google-cloud-aiplatform` 1.165.1, `google-genai` 2.19.0, `opentelemetry-api`/`-sdk` 1.42.1 |
| Image `requirements.txt` | byte-identical to commit `f589b25`; unchanged in the repository from 22 to 24 August |
| Managed Runtime | updated 23 August 2026, 20:11 UTC; declares Python 3.12, `requirements.txt`, entrypoint `agents.orchestrator.runtime:app` |

The packages were read by streaming only the image's `pip install` layer (about 254 MB) from
Artifact Registry and listing `*.dist-info/METADATA` entries, without writing the layer to disk.
The Runtime API returns its Python specification but not its source archive, so the Runtime's
installed packages cannot be read back. It was deployed from the same requirements file the same
evening, but that is an inference, not a measurement.

## IAM census, 28 October

| Measure | Value |
|---|---|
| IAM bindings scanned | 56 (62 on 25 August, evidence 11) |
| Deterministic findings before policy | 3: `platform-infra` 1, `security-engineering` 2 |
| Human exceptions | 1, expired 18 September 2026 |
| Audit log bucket | `bastion-audit`, `europe-west4`, 365 days, unlocked |
| Scheduler jobs | 0 |

Say **the November evaluation ran against the 23 August deployment: one image with `google-adk`
2.7.1 across all four services, and a Runtime last updated that evening.**

## What this does not show

- **The Runtime's installed packages.** Only its declared Python version and requirements file
  name are readable.
- **A census on the evaluation days.** The binding count is from 28 October; the 3 November runs
  delivered the same three findings, but no new census was taken then.
