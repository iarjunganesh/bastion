# Why Bastion is distinctive

Bastion does not demo a fictional enterprise. It reads its own live GCP IAM policy under a
read-only identity, finds over-permission deterministically, and then proves the agent that writes
a review record cannot read that policy.

The technical story is one composed control chain:

- managed catalog and department metadata make agents reusable rather than hard-coded;
- Firestore plus Eventarc makes asynchronous work resumable and deduplicated;
- Memory Bank plus expiring human exceptions prevents repeatedly reopening accepted risk;
- Agent Identity, Gateway/IAP, worker origin authentication, and per-workload IAM prevent bypass;
- deterministic minimisation and Model Armor contain production data before global model use;
- a count-only idempotent receiver gives the fleet one bounded human-review side effect;
- payload-free audit records, retained metrics, alerts, and dashboard make failures visible.

The strongest demo beat is the contrast: Auditor succeeds on a live read, Escalation is denied the
same capability, yet the governed fleet still completes a useful human-review workflow.
