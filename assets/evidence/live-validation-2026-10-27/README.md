# Live-validation supplement - 27 October 2026

Static, redacted data for [evidence 14](../14-live-validation.md) and the
local technical report draft (intentionally uncommitted). These files were promoted from the
verified local capture without changing the bundle or its data. They are intended
repository artifacts; promotion here does not create a release, DOI or permission
for another live run.

| File | Content |
|---|---|
| [Bundle](bastion-live-validation-2026-10-27.zip) | Original metrics, source/checkpoint history, recovery, provenance, collector/evidence code and tests, plus its internal hash manifest |
| [Summary](summary.json) | Denominators, timing definitions, results, deployment checks and explicit limitations |
| [Runs](runs.csv) | 20 investigation rows; client confirmation timing and delivered counts |
| [Stages](stages.csv) | 120 paired Runtime audit-duration rows |
| [Hashes](sha256.json) | SHA-256 of the four supplied data files |

The bundle SHA-256 is
`3f9acf4c82f390cd25091ec684c8a195af36388592363916742a6607e4a7d80c`.
The ZIP contains a separate `sha256.json` for its 15 members, including the
original stopped collector archive. Do not discard that archive or the recovery:
one collection-method repair occurred, but no investigation was rerun or excluded.

## Offline verification

These commands do not contact GCP or invoke any agent:

```powershell
Get-FileHash assets\evidence\live-validation-2026-10-27\bastion-live-validation-2026-10-27.zip -Algorithm SHA256
python -m zipfile -t assets\evidence\live-validation-2026-10-27\bastion-live-validation-2026-10-27.zip
```

The report build additionally checks the bundle hash, every internal member hash,
the public-file manifest, byte equality of the supplied summary/CSVs and the
reported denominators. No live collector is imported or executed by that build.

The collector code inside the ZIP is a historical acquisition artifact, not a
command to run against Bastion. Its completed authorization is exhausted.
Reproduction of a new live study requires explicit operator approval and an
authorized project; offline analysis of these files does not.

## Interpretation

Twenty executions are not twenty independent IAM policies. Sixty delivered
finding instances are not sixty distinct risks. Client completion confirmation
includes the 5s polling interval; Runtime audit durations measure a different
boundary. The pilot trace uses an explicit unique-name/time-window match, not an
embedded investigation-ID join. The five replay publications have bounded
unchanged-effect observations, not independent per-message delivery receipts.

Opaque event/context/invocation/trace IDs and department-level counts are retained
for correlation. Raw IAM, finding lists, principals, model text, secrets and
private origins are not supplied. Model-submission counts are not token usage or
an actual currency-cost measurement. See the evidence record for full limits.
