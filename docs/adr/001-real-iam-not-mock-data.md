# ADR-001: Audit a real GCP IAM policy, not mock entitlement rows

**Status:** Accepted
**Date:** 2026-08-13
**Traces to:** [`submission/DEVPOST.md`](../../submission/DEVPOST.md)

## Decision

The Access Auditor's primary data source is the live IAM policy of the GCP project Bastion
is deployed into, read through the IAM and Cloud Asset Inventory APIs. A hand-authored
entitlement dataset is not the source of truth, and may exist only as a small seeded
overlay to guarantee that one specific finding appears on camera.

## Context

The track's own sentence names this as one of three obligations: agents must
*"interact with production data without violating enterprise compliance, data sovereignty,
or security policies."* Production data, not a fixture. The other two obligations are
[ADR-003](003-pillars-on-geap.md).

Innovation & Operational Utility is 40% of the score, worded as how much real-world
friction the agent removes on its own, and **ties break on that criterion first**. The
organizers' own success tips lead with *"solve a real, specific problem you actually
have."*

The original plan audited 30–50 hand-authored rows representing entitlements across
fictional SaaS tools. A governance fleet reasoning over invented rows demonstrates
architecture — the 30% criterion — while quietly failing the largest one. Enterprise
framing makes invented data more conspicuous rather than less, because there is no
enterprise behind it.

## Rationale

- A real IAM policy is one API call away, so this is *less* work than authoring fake rows.
- The findings are genuine. The project's default Compute Engine service account holds
  `roles/editor` — an unseeded, real over-permission of exactly
  the class the product exists to catch.
- Judges recognise an IAM policy on sight; a fixture invites the question of what else was
  staged.
- The policy contains the service accounts Bastion's own agents run under, so the system
  audits its own permissions. This is the *"Twist"* named once in the rules page's 40%
  criterion and never defined — Bastion's reading of it, offered as such rather than
  assumed.

## Consequences

**Detection is deterministic, and that is deliberate.** A model deciding which bindings are
over-broad would make the central finding unreproducible. Where Gemini does and does not sit
in this loop is [ADR-001](001-real-iam-not-mock-data.md), and the distinction it draws matters:
"no model in the detection path" is this record's intent, and it must not be allowed to
collapse into "no model call anywhere", which fails a pass/fail requirement.

The demo depends on a real project having interesting structure, which becomes more true as
the scoped service accounts are deployed, not less.

Real data carries real principals and real email addresses. Raw policy output is never
printed, never committed, and never recorded; anything published under `assets/evidence/`
is redacted deliberately. Ask for the one field needed —
`--format="value(bindings.role)"` returns roles, `--format=json` returns identities. A
leaked identifier from an access-governance project would discredit the submission more
than a missing feature would.

Findings are not guaranteed to be dramatic on any given day. The seeded overlay exists for
exactly that risk, and any use of it must be disclosed on camera and in `submission/`.

## Absorbed record: where Gemini sits in the loop (was ADR-008)

Folded in on 2026-08-15, because it is a consequence of auditing real data rather than an
independent decision.

**Detection is deterministic and runs before any model call.** `find_anomalies` is plain
Python over the policy Cloud Asset Inventory returns; Gemini is asked to write the rationale
for a finding, never to produce one. Three properties follow, and all three matter more when
the data is real:

- **The audit trail is defensible.** A compliance product cannot answer *"why was this
  flagged?"* with *"the model thought so."* A finding is a fact before it is a sentence.
- **The same policy yields the same findings on two runs.** A model-scored review that drifts
  between runs is one nobody can act on.
- **The model never receives the raw policy document.** That is what keeps the residency
  exposure small, given the `global` model endpoint
  ([ADR-004](004-flash-only-global-endpoint.md)) — it is a design property, not a promise.

Findings are corroborated against the IAM Recommender, Google's own signal that a role is
broader than its usage warrants, so the deterministic pass is grounded in first-party data
rather than in a threshold this project invented.
