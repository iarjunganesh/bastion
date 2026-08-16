# Evidence 06 — durable delivery and idempotent human review

**Observed:** 2026-08-16 UTC against the deployed Cloud Run/Eventarc/Firestore path.

- A versioned Pub/Sub event reached the Eventarc Cloud Run ingress and a Firestore investigation
  reached `completed` with one attempt in an observed successful run.
- A separate Vertex quota outage emitted a payload-free `model.request=failed` record and left the
  investigation failed/reclaimable rather than silently clearing it.
- An unauthenticated findings request returned `403`.
- A request made with the real Escalation service identity returned `202` and `accepted=true`.
- Repeating the same valid body and deterministic idempotency key returned `202` and
  `accepted=false`, without creating a second review record.
- The Eventarc subscription has five delivery attempts and a dedicated dead-letter review
  subscription.

No event ID, principal, service URL, payload, token, or stored finding is published here. This
evidence demonstrates one successful completion and one dependency-failure behavior; it does not
claim an availability percentage.
