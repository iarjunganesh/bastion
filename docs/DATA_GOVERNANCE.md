# Data governance and sovereignty inventory

Bastion reviews a project IAM policy for the authorised purpose of detecting over-broad access.
It is not a general identity directory, and no raw policy dump is retained or sent to a model.

| Field | Source | Processing boundary | Persistence | Retention / deletion | Residency and access |
|---|---|---|---|---|---|
| Raw IAM member and role | Cloud Asset Inventory | Deterministic Auditor only | Never persisted by Bastion | Process memory only | Read by `access-auditor-sa` through read-only IAM/Asset roles in the audited project |
| Opaque finding ID | HMAC/fingerprint of raw binding | Policy, routing, model, and notification | Firestore investigation/exception record | Exception expires at `approved_until`; investigation retention policy must be configured before deployment | Firestore database is `europe-north2`; agent runtime identity has `datastore.user` only |
| Department and risk category | Deterministic department catalog / rules | Policy, model, notification | Firestore and payload-free audit event | Same investigation policy | EU workload boundary; no principal or resource identifier present |
| Model prompt / response | Minimized category, department, opaque ID | Model Armor before input; deterministic protected-data callback after output | Not retained by Bastion | Cloud-provider telemetry subject to configured retention | Gemini uses `GOOGLE_CLOUD_LOCATION=global`; this is **not** an EU data-residency claim. Model Armor is in `europe-west4`. Minimisation is the control before either boundary. |
| Human notification | Count, department, allowlisted categories, deterministic summary | Private, IAM-authenticated findings endpoint | Firestore-backed idempotent review record | Retention policy must be configured by the platform owner | The endpoint validates source, department, categories, deterministic summary, and idempotency key; Bastion sends no binding values |
| Audit record | Event type, actor, invocation ID, argument names, error class | Structured stdout / Cloud Logging | Cloud Logging after deployment | Logging retention must be set by the approved platform owner | No argument values, principal values, or exception messages are emitted |

## Operating rules

- Do not use production IAM dumps as test fixtures or evidence.
- Do not put endpoint URLs, credentials, raw principal identifiers, or Model Armor template output
  in Git, screen recordings, or prompt text.
- The Cloud Run deployment rejects ephemeral memory and unauthenticated ingress.
- A deployment owner must configure the Firestore/Cloud Logging retention policy and document the
  approved duration before taking the service beyond the demonstration environment.

This inventory is deliberately a release gate, not a blanket statement of compliance. The
post-deployment evidence must prove the configured retention and access policies.
