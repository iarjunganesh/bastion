# Security policy

Bastion reads a live cloud project's IAM policy. That makes a handful of ordinary security
practices non-optional here, and worth stating plainly.

## Reporting a vulnerability

Open a GitHub issue for anything non-sensitive. For anything that would expose a
credential or a principal, contact the maintainer privately rather than filing publicly.

This is a hackathon submission, not production software. There is no support commitment
and no patch SLA.

## What this repository must never contain

- Service-account keys, application-default-credentials files, or any exported credential.
- A raw `get-iam-policy` dump. These carry real principal identifiers and real email
  addresses. `.gitignore` covers the usual filenames, but the obligation belongs to
  whoever commits, not to the pattern list.
- Unredacted findings. Anything published under `assets/evidence/` is redacted
  deliberately before it is committed.

**And never *print* one.** The trap is not `echo $KEY` — nobody writes that. It is a broad
read of a store that happens to contain principals: `gcloud projects get-iam-policy`,
`gcloud secrets versions access`, `gcloud run services describe` with its full environment,
`cat .env`, `printenv`. Terminal output is not ephemeral; it lands in scrollback, in session
transcripts, and in anything later pasted into an issue or a screen recording. Redirect to a
gitignored file and grep that, or ask for the one field you need —
`--format="value(bindings.role)"` returns roles and no identities. The narrow query is not
merely tidier; it *is* the control.

**Demo recordings are the highest-risk surface here**, because the whole point is showing a
real policy on screen. The redaction pass runs before a capture is kept, never after it is
uploaded.

If a credential does land in history, rotate it first and rewrite history second. The
rotation is what matters; the rewrite is cosmetic once the value is public.

## Security-property ledger

This ledger separates implemented proof from target controls.

| Property | Current state |
|---|---|
| Per-agent least privilege | Three private Cloud Run services run under separate agent service accounts; peer calls use audience-bound ID tokens. A retained deployed denial capture is still owed. |
| Gateway authorization | Local caller/target/skill/classification policy and private Cloud Run ID-token transport are implemented. Managed Gateway deployment evidence remains pending. |
| Audit refusals and failures | `AuditPlugin` is registered by the supported local runner and Cloud Run startup path. Production-log evidence remains pending. |
| Payload-free audit records | Implemented and covered in local tests; production-log verification remains pending. |
| Prompt-injection screening | Model Armor is registered as ADK's pre-model callback and fails closed. The direct block is captured; retained deployed trace evidence is next. |
| Outbound PII boundary | Opaque finding IDs, post-model structured-output screening, and schema-limited notification payloads are implemented. Production trace verification remains pending. |
| Fixed tool definitions | Implemented in agent construction and covered by populated security tests. |
| Authenticated, bounded Cloud Run | Four internal-only Cloud Run services are deployed; invoker IAM is granted only to the required peer or Eventarc service identity. |

`submission/SUBMISSION.md` is the proof ledger. A target row is not a claim of enforcement.
