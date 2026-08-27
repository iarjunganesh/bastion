# Devpost gallery assets

This directory holds only the five final, redacted, judge-facing PNGs. Raw console captures and
discarded takes stay under ignored `.takes/` and must never be committed.

The required order, captions, sources, redaction rules, and acceptance checks are defined in
[`submission/CAPTURE_RUNBOOK.md`](../../submission/CAPTURE_RUNBOOK.md).

Expected files:

1. `01-enterprise-fleet-architecture.png`
2. `02-governed-agent-catalog.png`
3. `03-production-iam-routing.png`
4. `04-enforced-security-boundary.png`
5. `05-durable-context-and-audit.png`

All five are present as of 2026-08-27. Every one is dark, so the sequence reads as one project.

Do not add a file until it has passed sensitive-data inspection at 200% zoom.

## Promotion and redaction

1. Keep the original capture unchanged under ignored `.takes/<date>/`.
2. Crop or compose a separate final copy into this directory.
3. Inspect the final copy at 200% zoom. Record it in `REDACTIONS` in
   [`scripts/redact_evidence.py`](../../scripts/redact_evidence.py), using an empty tuple only when
   it genuinely needs no mask.
4. Run `python scripts/redact_evidence.py` to apply declared masks, then run it again with
   `--check`.

PNG masks are applied losslessly with Pillow. MP4 masks are burned into every frame with local
FFmpeg and verified using samples at the start, middle, and end. The CI gate rejects undeclared or
unmasked judge-facing media, in this directory and in `../evidence/screenshots/`.

Redact account/project resource IDs, private origins, signed-in avatars, identities, tokens, and
other nonessential private data. Never mask a metric, count, status, timestamp, query, trace or
investigation ID, or any other value cited as evidence.
