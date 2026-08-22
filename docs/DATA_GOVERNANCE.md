# Data governance and sovereignty inventory

Bastion uses production IAM only for read-only access review. Raw policy data is processed by
deterministic code and is neither persisted by Bastion nor sent to Gemini.

| Data | Boundary | Persistence and retention | Residency / processor |
|---|---|---|---|
| IAM member, role, resource, binding | Access Auditor deterministic tool only | Process memory; never a Bastion record | Source GCP project; read-only Auditor identity |
| Opaque finding ID, category, score, department | Policy, orchestration, routing | Firestore investigation record; exceptions expire at `approved_until` | `europe-north2` |
| Session and durable memory | Managed Agent Runtime and Memory Bank | Managed sessions/memory; deletion follows platform-owner lifecycle | `europe-west4` |
| Minimized prompt/response | Model Armor, Gemini, deterministic output screen | Bastion does not persist content; provider telemetry follows project settings | Armor `europe-west4`; Gemini `global` |
| Human-review request | Private findings API | Count, department, categories, deterministic summary, opaque finding IDs, idempotency key | Firestore `europe-north2` |
| Exception approval | Private findings API, human caller | Opaque finding ID, bounded expiry, policy version, and the **verified** reviewer principal | Firestore `europe-north2` |
| Audit event | Cloud Logging | Payload-free event metadata, 365-day log-bucket retention | `europe-west4` |
| Dead letter | Pub/Sub review subscription | Failed event envelope until operator acknowledgement/retention expiry | `europe-north2` |

## Boundary rules

- Raw members, roles, resources, and bindings stop before the model boundary.
- No principal, resource, prompt, response, tool value, or exception message enters audit logs.
- Model output is untrusted until the deterministic protected-data screen passes.
- Notification fields and categories are allowlisted; free-form destinations and binding data
  are not part of the tool contract. Opaque finding IDs are carried so a human can approve a
  specific finding; they are validated to the Auditor's exact HMAC shape and reveal nothing.
- The reviewer on an approved exception is the verified caller identity, never a request field.
  It is deliberately retained in the durable ledger for accountability and never enters model
  state, audit logs, or committed evidence.
- The HMAC key and A2A origin credential remain in Secret Manager and are never printed.
- `global` model processing is disclosed explicitly and is not described as EU residency.

## Deletion and legal ownership

Firestore investigation retention, managed Memory lifecycle, and dead-letter disposition remain
platform-owner policies; Bastion supplies deterministic identifiers and expiry semantics but does
not claim a legal retention basis. The audit bucket is configured for 365 days and remains
unlocked. Locking it would be irreversible and is outside an automated deployment.

Committed evidence is redacted and count-only. The current measured inventory is
[assets/architecture/gcp-state.json](../assets/architecture/gcp-state.json).
