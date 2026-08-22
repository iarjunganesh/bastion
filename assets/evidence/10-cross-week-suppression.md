# Evidence 10 — a prior week's approved exception suppresses a later matching finding

**Observed:** 2026-08-22 against the live `bastion-fleet-2026` project, through the deployed
managed Runtime and both Cloud Run workers. The exception was created on **2026-08-19**, so a
real three-day gap separates the human decision from the run that honoured it.

This is the track's second obligation — *"safely maintain context across weeks of asynchronous
operations"* — and it is the one claim that could not be compressed by working harder, because
its critical path is elapsed time. Until this capture the repository deliberately did not claim
it.

## What was approved, and by whom

| | |
|---|---|
| Finding | `4c546546a073060ab61a2e18` (opaque, HMAC-derived) |
| Approved until | 2026-09-18 |
| Policy version at approval | `v0.1.0` |
| Created through | `POST /v1/exceptions` on the IAM-private findings API |
| Reviewer | the verified calling identity, recorded in Firestore — never taken from the request body |

No principal, binding, role, or reviewer address appears in this file. The finding id is the
opaque identifier the system is designed to expose; it is what a human quotes to approve an
exception, and it keys nothing outside the audited project.

## The run that honoured it

One investigation, `investigation.run started` → `completed`, 32 audit records under a single
`investigation_id` spanning the Runtime and both workers:

```text
18:32:08  investigation.run  started    orchestrator       RUNTIME
18:32:15  investigation.run  started    access_auditor     access-auditor
18:32:21  tool.call          completed  audit_iam_policy   access-auditor
18:32:30  agent.run          started    policy_step        RUNTIME
18:32:31  agent.run          completed  policy_step        RUNTIME
18:32:31  agent.run          completed  policy_gate        RUNTIME
18:32:49  tool.call          completed  notify_human       escalation-agent
18:32:52  investigation.run  completed  orchestrator       RUNTIME
```

`notify_human` was called **once**. The same IAM policy produces three overly-broad findings
across two departments; one of those three carries the approved exception, and its department
received **no notification at all** — not an empty one. A team with nothing to review is not
paged, which is the behaviour `route_by_department` was written for.

| Human-review records written | Department | Findings |
|---|---|---|
| 1 | `security-engineering` | 2 |
| — | `platform-infra` | **0 — suppressed** |

The immediately preceding runs, at 16:59 the same day, wrote **two** records and delivered
`4c546546a073060ab61a2e18` to `platform-infra` while the same exception was already live and
current. The difference between those runs and this one is the fix in
[ADR-012](../../docs/adr/012-structured-findings-across-a2a.md)'s amendment: session state does
not cross an A2A boundary, so the policy decision has to travel as event content and the routing
result has to carry its own decision-filtered finding ids. The suppression was always being
computed correctly; it was being discarded one hop later.

## Proof boundary

- This proves **suppression across a real elapsed gap on the deployed path**, not that the
  exception store is immutable or that expiry has been observed firing. The 2026-09-18 expiry has
  not elapsed, so the "stops suppressing when it expires" half is covered by tests only.
- The gap is three days, not a calendar week. The claim made is "across a real elapsed gap
  spanning deployments and restarts," which is what happened; it is not a claim that a week
  passed.
- The reviewer identity is in the durable ledger and deliberately not reproduced here.
- Suppression is deterministic — `apply_policy_rules_with_memory` compares the opaque id against
  the Firestore ledger and checks the expiry. No model participates in the decision, and the
  Escalation Agent never sees the suppressed finding at all.
