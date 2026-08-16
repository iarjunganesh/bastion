# Security policy

Bastion reads production IAM, so minimisation and least privilege are release controls rather
than conventions. This is a hackathon project, not supported production software; there is no
support or patch SLA.

## Reporting a vulnerability

Open a GitHub issue only for non-sensitive reports. Send any credential, principal, endpoint,
or policy exposure privately to the maintainer.

## Never commit or print

- service-account keys, ADC files, access tokens, secret values, or `.env` contents;
- raw `get-iam-policy` or Cloud Asset output;
- unredacted findings, principal identifiers, private endpoint inventories, or full runtime
  environment dumps.

Use a narrow projection such as `--format="value(bindings.role)"`. Terminal scrollback, CI logs,
issues, and recordings are disclosure surfaces. If a credential is exposed, rotate it before
rewriting history.

## Enforced production boundaries

| Boundary | Deployed control and proof |
|---|---|
| Agent separation | The managed Orchestrator has an Agent Identity. Auditor, Escalation, durable ingress, and findings API use distinct service accounts. The Escalation identity has no IAM read role. |
| Governed egress | Runtime egress is bound to `bastion-egress`; IAP is default-deny and grants that Agent Identity per Registry destination. The Cloud Run dispatcher has no peer credential or worker invoker binding. |
| Worker origin | Worker origins are network-reachable for cross-region Gateway traffic, but every non-health A2A request requires the Secret Manager origin credential. Missing or wrong credentials return `401`. |
| Findings write | The findings API is IAM-private. Only the Escalation service identity has `run.invoker`; anonymous requests return `403`. Schema validation, an allowlist, and a deterministic key collapse replays. |
| Model boundary | Deterministic rules minimise IAM data before Gemini. Model Armor is a fail-closed pre-model callback; deterministic output screening blocks protected shapes. |
| Model authority | Missing/invalid risk fails closed. The model cannot create an exception, modify IAM, choose an endpoint, expand a tool schema, or clear an investigation. |
| Audit trail | `AuditPlugin` covers run, agent, model, tool, refusal, and error seams. Records include correlation metadata, argument names, and exception classes, never values, prompts, responses, or exception messages. |
| Durability | Firestore owns admission, leases, attempts, terminal state, exceptions, and notification idempotency. Eventarc has a five-attempt dead-letter policy and review subscription. |
| Retention | Payload-free audit logs route to a `europe-west4` analytics bucket with 365-day retention. The bucket is intentionally not locked because locking is irreversible. |

The two worker services carry an `allUsers` Cloud Run invoker binding only because Cloud Run IAM
cannot receive the managed Runtime's Agent Identity through Agent Gateway as an ordinary service
account token. This is not anonymous application access: the required origin secret is validated
before A2A processing, and Gateway IAP independently constrains the Runtime's destination. The
private findings API uses ordinary Cloud Run IAM and has no `allUsers` binding.

## Residual risks

- Gemini 3.5 Flash uses Vertex AI `global`; Bastion therefore makes no regional-residency claim
  for model processing. Data minimisation is the boundary control.
- ADK 2.7 `RemoteA2aAgent` is experimental, and `SequentialAgent` is deprecated while `Workflow`
  cannot yet serve as an `LlmAgent` sub-agent. Versions are pinned and covered by local and live
  gates; [ADR-005](docs/adr/005-adk-as-the-agent-framework.md) records acceptance.
- Audit retention is configured but not WORM/immutable. Locking the bucket requires a separate,
  explicit platform-owner decision.

The grounded deployment and evidence ledger is [submission/SUBMISSION.md](submission/SUBMISSION.md).
