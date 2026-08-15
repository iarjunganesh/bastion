# Agent Identity — Security & Governance pillar

Zero-trust: every service runs under its own GCP service account with the minimum IAM roles
it needs. There is no shared "agents" service account, and no service account holds a
predefined broad role where a narrower one will do.

This is the one pillar whose failure is directly observable. A mis-scoped call returns a
denial, and that denial is the artifact — see the verification step below.

> The three service accounts now exist and a least-privilege IAM contrast has been captured.
> The agents still execute as `sub_agents` of one `SequentialAgent` in a local process, so the
> runtime does not yet enforce those identities. The table below is the deployment target.

## Service accounts

Three, one per deployed agent. `infrastructure/deploy.sh` names exactly these; if a row is
added here it must be added there in the same change, or a service will deploy under the
wrong identity and the least-privilege claim becomes false in the artifact that proves it.

| Service | Service account | IAM roles |
|---|---|---|
| Orchestrator | `orchestrator-sa@PROJECT.iam.gserviceaccount.com` | `roles/datastore.user` scoped to `investigations`, `roles/pubsub.publisher` |
| Access Auditor | `access-auditor-sa@PROJECT.iam.gserviceaccount.com` | **`roles/iam.securityReviewer`** — read-only on the live IAM policy — plus `roles/cloudasset.viewer` and `roles/recommender.iamViewer` |
| Escalation Agent | `escalation-agent-sa@PROJECT.iam.gserviceaccount.com` | Write-only on the findings endpoint, `roles/secretmanager.secretAccessor` for that endpoint's URL. **No IAM read of any kind** |

**There were five rows here, and two of them were for services that no longer exist.** Gateway
and Registry each had a service account, because each used to be a Cloud Run service in this
repository. [ADR-003](../docs/adr/003-pillars-on-geap.md) replaced both with managed GEAP
products on 2026-08-15 and ~3,460 lines were deleted; a managed product is not a service this
project deploys, so it is not an identity this project creates. The rows outlived the code by
a day.

**There is no Policy Enforcer service account either.**
[ADR-002](../docs/adr/002-three-agents.md) merged that agent into the Orchestrator. A row for it
survived here long after the merge, and `deploy.sh` would have stood the service up — the same
failure as the Gateway and Registry rows, one decision earlier. Three occurrences of one shape
is a pattern, so: **this table is derived from what `deploy.sh` deploys, and nothing else.**

**The audit target is the live IAM policy, not a Firestore collection.** An earlier version
of this file scoped the Access Auditor to a custom role on an `entitlements` collection —
left over from the mock-data design that [ADR-001](../docs/adr/001-real-iam-not-mock-data.md)
rejected. The Auditor reads real bindings through `roles/iam.securityReviewer`, and the
policy it reads contains the three accounts above.

**The escalation surface is the dashboard's findings API, not Slack.** The agent reads
`BASTION_FINDINGS_ENDPOINT` and posts a typed body carrying a count. It held
`SLACK_WEBHOOK_URL` and a free-text `text` field until 2026-08-15, which contradicted ADR-003 —
Slack is not among the twenty services — and a free-text field is where principal identifiers
end up.

## Verification test (Week 2 milestone)

Call `projects.getIamPolicy` from the **Escalation Agent's** service account and confirm it
fails with `PERMISSION_DENIED`. That denial is the proof-point for zero-trust access control
in the demo; screenshot it. It is the shot the storyboard was missing, and it is the answer to
the rules page's *"clear, strictly enforced separation of concerns between agents"* — the one
sub-question an IAM-enforced fleet answers better than a convention-based one.

**The denial is safe to film; a success would not be.** The call returns an error, not a
policy, so nothing sensitive reaches the screen. Do not "check it works first" by running the
same call from the Auditor's account on camera.

The captured denial is recorded in
[`../assets/evidence/03-escalation-agent-denied.md`](../assets/evidence/03-escalation-agent-denied.md).
The `tests/security/` directory is still empty; deployed identity enforcement needs its own
repeatable test before the pillar is complete.

## TODO

- [ ] Split the `SequentialAgent` so each agent is its own deployable with its own
      `root_agent`. Until this lands the three share one identity and the table above cannot
      be true of anything
- [x] Create the three service accounts (`gcloud iam service-accounts create ...`)
- [ ] Grant each the roles above, and nothing else. Verify with a query that returns **roles
      and no identities** — `gcloud projects get-iam-policy "$PROJECT"
      --flatten="bindings[].members" --filter="bindings.members:<sa>"
      --format="value(bindings.role)"`. The unfiltered form returns every principal in the
      project and must not be printed; see [`../SECURITY.md`](../SECURITY.md)
- [ ] Wire Workload Identity so Cloud Run services assume these SAs natively (no key files)
- [x] Capture the Escalation Agent denial
