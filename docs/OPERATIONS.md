# Operations objectives and release gates

The live project has four log-based metrics, five enabled alert policies, a 365-day regional
analytics log bucket, a payload-free audit sink, and the **Bastion Fleet Operations** dashboard.
These are configured controls; the objectives below are service targets, not historical SLO
attainment claims.

| Signal | Objective | Live detection / response |
|---|---|---|
| Investigation completion | 99% of admitted events finish within 10 minutes | Stuck-delivery alert; inspect Firestore status/lease and Eventarc delivery |
| Duplicate effects | Zero duplicate review records | Deterministic idempotency key and create-once receiver; replay returns `accepted=false` |
| Audit failures | Every supported run/agent/model/tool action has a terminal audit event | Audit-failure metric and alert; correlate by investigation ID across hops, invocation ID within one agent run |
| Policy refusals | Refusal rate remains explainable by bounded reason | Refusal-spike alert; never bypass policy to restore throughput |
| Model Armor | Unavailable or matched screening always fails closed | Dedicated failure/refusal metric and alert |
| Dead letters | Zero unresolved review messages | Backlog alert on `bastion-dead-letter-review`; investigate before replay |
| Cost/capacity | Cloud Run max instances stays within `BASTION_MAX_INSTANCES` | Deployment verifier plus platform budget controls; no automatic IAM widening |

## Release procedure

1. Run the Python 3.12 quality gates from the README.
2. Deploy one immutable image to the four Cloud Run services and update managed Runtime
   separately when its graph/runtime source changes; `deploy.sh` alone does not do both.
3. Verify the existing Registry, Gateway, Runtime, IAM, DLQ, audit and alert configuration;
   reprovision authority only under an approved infrastructure change.
4. Run `python -m infrastructure.verify_fleet` and `python -m infrastructure.smoke_test`. The
   smoke Runtime check passes only on the completion gate's confirmation, not on any stream.
5. Capture only redacted counts/statuses in `assets/evidence/`.

Since 7 November the Escalation worker's receipts name their finding IDs and the completion gate
compares them. A worker image or Runtime deployed without the other fails every investigation
closed, so steps 2 and 3 are one change: deploy the Cloud Run image and the Runtime together.

`infrastructure.deploy_agent_runtime` uses the SDK's public `runtimes.update`/`create`, which add
`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` when it is absent; the deploy environment now declares
it as `unspecified`. The 5 November Runtime update instead used a reviewed operator script that
removed this SDK addition to keep the existing environment byte-for-byte, so the Runtime deployed
then does not carry it. With `enable_tracing=True` the template reads `unspecified` like an unset
value; ADK additionally sends its telemetry user-agent header.

`infrastructure/rollback.py` is dry-run by default and permits only one of the two newest safe
revisions. `infrastructure/teardown.py` is also dry-run by default: it verifies the exact
project, describes every allowlisted serving resource, reconciles the regional Agent Registry
(the worker and Runtime cards plus the 14 Google API endpoint registrations), and prints a JSON
inventory. An unrecognised or non-Bastion registry entry, a disagreement between the registry
listing and the individual describes, a timeout, or any error other than that command's own
not-found for that exact resource stops it before deletion; the legacy dispatcher card is
expected absent. Failures are reported as status codes only; gcloud stderr, which can name the
authenticated principal, is never printed. `--apply` requires `--confirm-project` and a clean
fresh inventory, and stops on the first failed or timed-out delete, reporting the completed
count; a timed-out delete has an unknown outcome and needs a fresh inventory before any retry.
Firestore, secrets, managed Runtime/Memory, audit logs, images and IAM are never touched.

## Failure semantics

A handler admits an event before execution, owns a bounded lease, returns `503` for a concurrent
or failed attempt so Eventarc retains delivery, and acknowledges an already-completed replay.
Expired leases are reclaimable. The dead-letter policy targets approximately five delivery
attempts; it is not a hard cap. One rejected event was observed reaching review after five
deliveries ([E21](../assets/evidence/21-redelivery-and-dead-letter.md)). Dependency errors
are audited by class without leaking response content.
