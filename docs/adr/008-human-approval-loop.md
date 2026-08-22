# ADR-008: The exception ledger gets a production writer, and it is a human

**Status:** Accepted 2026-08-18
**Traces to:** [hackathon brief](../../submission/DEVPOST.md)

## Decision

Approving an exception is a **human act on the IAM-private findings API**, never an agent tool.
The reviewer is taken from the verified caller identity rather than the request body, the expiry
is capped, and the opaque finding IDs needed to approve travel on the human-review record.

## Context

The track's second obligation is maintaining context across weeks of asynchronous work, and
Bastion answers it partly with expiring human-approved exceptions. The suppression *read* path
was real: [`agents/orchestrator/agent.py`](../../agents/orchestrator/agent.py) consults the
ledger for every finding, and restart-plus-suppression is integration-tested.

The *write* path did not exist. The only caller of the store's `approve()` was the test suite —
zero production callers. Worse, the human-review record carried a count and no finding
identifier, while the ledger is keyed by finding id, so a reviewer reading the surface they are
given could not name the finding they wanted to approve even with direct database access.

The capability was therefore documented, tested, and unreachable in the deployed fleet. That is
precisely the gap between *implemented* and *observed* that [ADR-006](006-pillar-coverage.md)
exists to keep visible, and it was found by trying to capture the evidence rather than by
reading the code.

## Rationale

- **A model must not be able to suppress a finding.** `SECURITY.md` already stated that the
  model cannot create an exception. Making approval an agent tool would have reversed that for
  convenience, so the write lives on the human surface behind Cloud Run IAM instead.
- **Self-asserted identity is not an audit trail.** `approve()` accepts `reviewer` as a string.
  Reached over HTTP that is an attestation the caller forges about itself. Deriving the reviewer
  from the verified ID token is what makes the ledger evidence of *who* accepted the risk.
- **Opaque IDs are the existing minimisation primitive**, already sanctioned by
  [data governance](../DATA_GOVERNANCE.md) to persist in Firestore. Carrying them to the review
  record adds no exposure: an HMAC identifier names a finding without describing it, and a
  fabricated one is inert because it can only key an exception no real finding will match.
- **An unbounded exception is a permanent silent hole.** Expiry is capped at 90 days so a
  suppression cannot outlive the reasoning behind it unnoticed.

## Consequences

- `notify_human` gains `finding_ids`. The signature is still the control — it is handed opaque
  identifiers and counts, never bindings — and `tests/security/test_tool_surface.py` asserts the
  parameter set by equality, so a future widening fails loudly.
- That same test fails if any agent ever declares an approval tool, which is the enforcement
  behind this record rather than a convention.
- A human operator needs `roles/run.invoker` on the findings API to approve. This is a
  deliberate, separate grant from the Escalation Agent's write access.
- The cross-week claim can now be demonstrated end to end through deployed surfaces instead of
  seeded by an unaudited console edit. A console-authored Firestore document would have bypassed
  the very audit trail this project argues for.
