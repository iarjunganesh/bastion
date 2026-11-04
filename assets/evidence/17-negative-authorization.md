# Evidence 17 — negative authorization probes

**Captured:** 3 November 2026, about 20:00 UTC, evidence chunk E2 of cohort N. 15 probes
against the unchanged August deployment. No model call, no investigation, and no exception
written. Tokens, service origins and identities stayed in memory; the private bundle records
status codes and booleans only.

## Exception approval (`POST /v1/exceptions`)

Every probe that could pass validation named a random, opaque-shaped finding ID that matches
no real finding. The exception ledger was read before and after: the synthetic ID never
appeared and the ledger count stayed at 1.

| Probe | Caller | Payload | Status | Refused by |
|---|---|---|---:|---|
| A1 | No token | Expired | 403 | Cloud Run IAM |
| A2 | Malformed bearer token | Expired | 401 | Cloud Run IAM |
| A3 | Escalation Agent identity (a permitted service caller) | Expired | 403 | Service: "not the configured exception approver" |
| A4 | Maintainer's own user identity | Expired | 401 | Cloud Run IAM |
| A5 | Approver | Expiry in the past | 400 | Validation |
| A6 | Approver | Timestamp without a timezone | 400 | Validation |
| A7 | Approver | Finding ID not in the opaque Auditor shape | 400 | Validation |
| A8 | Approver | Expiry beyond the 90-day maximum | 400 | Validation |
| A9 | Approver | `policy_version` missing | 422 | Request schema |

A3 carried an invalid payload on purpose. A 403 rather than a 400 shows that the approver
check runs before validation, and an authorization fault could not have written a record.

## Peer origin (Access Auditor A2A surface)

| Probe | Request | Status | Body |
|---|---|---:|---|
| P1 | Agent card, no peer credential | 401 | "unauthorized peer" |
| P2 | Agent card, random wrong credential | 401 | "unauthorized peer" |

## Escalation Agent IAM read

| Probe | Identity | Result |
|---|---|---|
| I1 | Maintainer impersonates the Escalation Agent identity | Succeeded |
| I2 | Escalation Agent calls `projects.getIamPolicy` | 403 `PERMISSION_DENIED` |
| I3 | Escalation Agent `testIamPermissions` for the policy read | Not held |
| I4 | Access Auditor `testIamPermissions` for the policy read (control) | Held |

I1 succeeding before I2 fails separates an impersonation failure from the policy-read denial,
the same distinction [evidence 03](03-escalation-agent-denied.md) made on 15 August. The
Auditor control used a permission test, so no policy content was read.

Say **the approval endpoint refused every caller but the configured approver, and every
malformed approval, without writing; the Escalation identity still cannot read IAM**. These
are single probes, not a fuzzing campaign. The peer-origin result covers a direct request to
the Auditor; it is not the Gateway/Registry refusal (E5).
