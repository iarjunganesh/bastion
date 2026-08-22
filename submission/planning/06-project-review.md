# Final project review

## What is complete

- Three-agent ADK fleet with one managed Runtime and two protected A2A workers.
- Managed Registry, Gateway/IAP, Agent Identity, Memory, Model Armor, and Observability.
- Real read-only IAM/Asset review with deterministic findings and department routing.
- Durable Eventarc/Firestore lifecycle, leases, retry, DLQ, deduplication, and idempotent findings.
- PII/protected-data boundary, payload-free full audit lifecycle, and explicit sovereignty limits.
- Reproducible Python 3.12 Windows deployment, smoke, rollback, teardown, and CI gates.
- 211 tests with 100% statement and branch coverage.

## Residual submission work

- Record and publish the under-four-minute demo.
- Upload the architecture GIF/image and complete the Devpost form.
- Reconfirm billing budget/anomaly notification and service availability before recording.
- Optionally publish the bonus blog and social post.

## Honest limitations

- No IAM writes or automatic remediation.
- No immutable audit claim; retention bucket is unlocked.
- No regional-residency claim for global Gemini.
- No historical SLO, cost, accuracy, or wall-clock-week evidence.
- ADK Remote A2A is experimental and SequentialAgent is deprecated; risk is pinned and recorded.

These limitations strengthen rather than weaken the submission when stated next to the enforced
controls: the project makes a narrow, reproducible institutional-agent claim and proves it.
