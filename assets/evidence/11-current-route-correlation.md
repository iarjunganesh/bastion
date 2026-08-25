# Evidence 11 — current deployed route correlation

**Observed:** 2026-08-25 on the live `bastion-fleet-2026` fleet
**Code revision:** `c81b4af`
**Investigation:** `755dec5f-2feb-4cd2-9dc3-63ff32d3404b`

A fresh Pub/Sub trigger completed one investigation through managed Runtime, the deployed Access
Auditor, deterministic policy gates, the deployed Escalation Agent, and back to Runtime. The
reviewed Cloud Logging export contains **28 unique structured events**, **3 invocation ids**, and
no `textPayload` records.

## Correlated milestones

| Time (CEST) | Resource | Actor | Observed event |
|---|---|---|---|
| 18:31:56 | Reasoning Engine | `orchestrator` | Investigation started |
| 18:32:18 | Cloud Run | `access_auditor` | Investigation started |
| 18:32:23 | Cloud Run | `access_auditor` | Request submitted to `gemini-3.5-flash` |
| 18:32:27 | Cloud Run | `audit_iam_policy` | Tool call completed |
| 18:32:39 | Reasoning Engine | `policy_gate` | Policy gate completed |
| 18:33:00 | Cloud Run | `escalation_agent` | Investigation completed |
| 18:33:01 | Reasoning Engine | `escalation_gate` | Escalation gate completed |
| 18:33:01 | Reasoning Engine | `orchestrator` | Investigation completed |

The worker records came from Access Auditor revision `bastion-access-auditor-00031-sbr` and
Escalation Agent revision `bastion-escalation-agent-00027-nkv`. Runtime and Cloud Run each
contributed 14 events to the same investigation id.

## Count-only companion measurement

Immediately after reviewing the route, the Auditor's current Cloud Asset Inventory read and
deterministic ownership resolver were run again without printing or persisting the policy. The
durable review inbox was queried by this investigation id and reduced to counts before output.

| Measurement | Observed value |
|---|---|
| IAM bindings scanned | 62 |
| Deterministic findings before policy | 3 |
| Canonical owning departments | `platform-infra` (1), `security-engineering` (2) |
| Completed durable investigation | 1 |
| Delivered review records | 1 |
| Findings delivered after policy | 2 |
| Routed departments after policy | `security-engineering` (2) |
| Raw IAM fields in the model-boundary finding schema | 0 |

The difference between three canonical findings and two delivered findings is intentional policy
behavior: the durable exception path can suppress an approved finding before department delivery.
This table records only the counts observed here; the separate cross-week evidence establishes
the approved-exception behavior and its time boundary.

## Data-minimisation check

The promoted record retains only timestamps, resource class, actor, event, outcome, model name,
revision, correlation ids, and aggregate event counts. The reviewed export contained no prompt,
response, email address, service-account identifier, IAM member, IAM binding, role value,
principal field, credential field, or private URL. The raw console screenshots and JSON export
remain ignored under `.takes/` and are not publication assets.

## Proof boundary

- This proves one **current deployed route completed** and that Runtime and both worker revisions
  emitted payload-free events under one investigation id.
- It proves that the deployed Auditor completed `audit_iam_policy` and submitted a request to
  Gemini 3.5 Flash. It does not expose or reconstruct the policy.
- The binding/finding/ownership measurement is a count-only companion probe taken immediately
  after the route. The route's own retained audit proves the deployed worker called the IAM tool;
  it does not embed raw policy values or these aggregate counts in telemetry.
- The P0.9 raw screenshot passed sensitive-data and readability review. It remains an ignored
  source take until the final production-routing gallery image is composed and reviewed.
- It is not an agent-mediated Model Armor refusal, a Cloud Trace span chain, a retention/WORM
  claim, or historical SLO attainment.
