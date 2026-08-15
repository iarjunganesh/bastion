# Evidence 03 — the Escalation Agent is denied the IAM policy, by IAM

**Captured:** 2026-08-15
**Project:** `bastion-fleet-2026`
**Call:** `projects.getIamPolicy`, made twice — once as each agent's own service account

This is the Agent Identity pillar's proof, and the one
[`identity/identity_config.md`](../../identity/identity_config.md) has described as owed since
the file was written. Separation of concerns here is **enforced in IAM, not by convention**:
the Escalation Agent cannot read the policy it escalates findings about, even with a fully
compromised prompt, because its service account holds no permission to.

## The two calls

```text
$ gcloud projects get-iam-policy bastion-fleet-2026 \
    --impersonate-service-account=escalation-agent-sa@…

ERROR: (gcloud.projects.get-iam-policy) [<SERVICE-ACCOUNT>] does not have permission
to access projects instance [bastion-fleet-2026:getIamPolicy] (or it may not exist):
The caller does not have permission.

  exit status 1
```

```text
$ gcloud projects get-iam-policy bastion-fleet-2026 \
    --impersonate-service-account=access-auditor-sa@… \
    --flatten="bindings[].members" --format="value(bindings.role)"

  exit status 0
  role bindings visible to the Auditor: 15
  distinct roles:                       15
  identities printed:                   0
```

Same call, same project, same moment. The only variable is which service account made it.

## Why this denial is the real one

**A first attempt produced the wrong 403 and was discarded rather than captured.** It read
`Failed to impersonate … Permission 'iam.serviceAccounts.getAccessToken' denied`, which is a
denial of *impersonation*, not of the policy read — the `serviceAccountTokenCreator` grant had
not propagated yet, and it took about 75 seconds. Publishing that as the pillar's proof would
have been a screenshot of an unrelated failure captioned as a security control.

So the two are separated explicitly. The capture above was taken only after
`gcloud auth print-access-token --impersonate-service-account` **succeeded** for the same
account. Impersonation working and the policy read failing is the only combination that proves
anything.

## The bindings behind it

| Service account | Roles | Why |
|---|---|---|
| `access-auditor-sa` | `roles/iam.securityReviewer`, `roles/cloudasset.viewer`, `roles/recommender.iamViewer` | Read-only on the policy it audits, and nothing else |
| `orchestrator-sa` | `roles/pubsub.publisher`, `roles/datastore.user` | State and async. **No policy read** |
| `escalation-agent-sa` | **none** | The absence *is* the control |

`escalation-agent-sa` holds no project-level role at all. That is not an oversight to tidy up
later — it is the configuration under test.

## Redaction

The denial returns an **error, not a policy**, which is what makes it safe to publish and to
film; a success would not be. The Auditor's side is reported as counts only, produced by
`--format="value(bindings.role)"`, which returns role names and no identities. Service-account
emails are masked above. No principal from the audited project appears in this file.

## What this closes

- **Agent Identity** — the pillar's one observable proof
  ([ADR-006](../../docs/adr/006-pillar-coverage.md)).
- The rules page's *"clear, strictly enforced separation of concerns between agents"* — answered
  in IAM rather than in prose.
- The least-privilege half of the track's third demand. The read is real *and* now restrained
  by something other than the code's own good manners.

## What it does not close

- **Historical capture condition.** These service accounts were created before the private Cloud
  Run fleet existed. Current deployment state is measured in
  [`../architecture/gcp-state.json`](../architecture/gcp-state.json); this record remains the
  safe, redacted denial baseline. The denial was produced by workstation impersonation, not by
  a deployed agent being refused mid-investigation. A retained service-originated denial is the
  stronger remaining evidence.
- The security suite now exercises the Cloud Run audience, identity-policy shape, and private
  peer transport. A retained deployed denial is the remaining evidence artifact.
