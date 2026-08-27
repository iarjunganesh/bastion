# Evidence 13 — current deployed route reasoning chain in Cloud Trace

**Observed:** 2026-08-25 on the live `bastion-fleet-2026` fleet
**Code revision:** `c81b4af`
**Investigation:** `755dec5f-2feb-4cd2-9dc3-63ff32d3404b`
**Trace:** `09369db584cc9df10f60993fa8fabe1c`

The investigation recorded in [evidence 11](11-current-route-correlation.md) also produced a
single Cloud Trace containing **22 spans** over **1m 5.401s**. The complete governed sequence is
one connected tree rather than a set of unjoined fragments: the managed Runtime's workflow span
is the root, and both A2A worker calls appear beneath it.

## Observed span tree

| Span | Duration |
|---|---|
| `invoke_workflow orchestrator` (root) | 1m 5.401s |
| `invoke_agent orchestrator` | 1m 4.684s |
| `invoke_agent access_auditor` | 40.700s |
| — `GET` → `/a2a/access_auditor/.well-known/agent-card.json` | 14.518s |
| — `a2a.client.transports.jsonrpc.JsonRpcTransport.send_message` → `POST /a2a/access_auditor` | 25.739s |
| `invoke_agent policy_step` | 1.346s |
| — `/google.firestore.v1.Firestore/BatchGetDocuments` × 3 | 672.149ms, 160.761ms, 167.220ms |
| `invoke_agent policy_gate` | 284.415ms |
| `invoke_agent escalation_agent` | 22.075s |
| — `GET` → `/a2a/escalation_agent/.well-known/agent-card.json` | 12.073s |
| — `a2a.client.transports.jsonrpc.JsonRpcTransport.send_message` → `POST /a2a/escalation_agent` | 9.693s |
| `invoke_agent escalation_gate` | 277.387ms |

Three details are worth naming because they are visible here and nowhere else in the evidence set:

- **Both A2A hops are preceded by an agent-card fetch.** The worker's
  `.well-known/agent-card.json` is retrieved before the call is made, so the catalogued-route
  claim is observable in the request chain rather than inferred from configuration.
- **The exception lookup is a nested child of `policy_step`.** Three Firestore
  `BatchGetDocuments` calls sit inside the deterministic policy span, which is what durable
  human-decision continuity looks like from the execution side.
- **All five orchestration steps appear in their fixed order**, ending with `escalation_gate`.
  Every agent span carries ADK's `GenAI` operation marker and the opaque managed Runtime
  workload id; no agent is named by a service URL.

The reviewed screenshot shows 18 rows because the two JSON-RPC transport wrappers are collapsed,
hiding their four `POST` and path children. The span total reported by the Console and by the
Cloud Trace API is 22 in both cases, and the two sources agree on every duration above.

## Data-minimisation check

The deployed Runtime sets `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`, so no
prompt or response text exists in these spans at all. That is a structural property of the
deployment, not a redaction applied afterwards.

The retained record above carries span names, durations, ordering, and the opaque trace and
workload identifiers only. Span *attributes* were deliberately not opened or captured: the
transport spans carry `http.url` and `/http/host` values naming private Cloud Run worker origins,
along with project identifiers, and those are prohibited from judge-facing artifacts. The
reviewed screenshot expands no span for that reason, and is retained as
[`screenshots/13-current-route-trace.png`](screenshots/13-current-route-trace.png); the raw source
remains ignored under `.takes/`. Gallery image 05 crops it further, stopping left of the
Service/workload column, so no partial workload id appears there.

## Proof boundary

- This proves the **current deployed route** produced one connected reasoning chain across the
  managed Runtime and both A2A workers, in the documented order, on the revision named above.
- A trace is **sampled and expires**. It is explanatory telemetry, not the retained compliance
  record — that role belongs to the payload-free audit trail in
  [evidence 11](11-current-route-correlation.md) and the 365-day bucket in
  [evidence 07](07-observability.md). The two are deliberately separate artifacts and never
  derive from one another.
- Durations are one observation of one investigation. They are not a latency SLO, a benchmark, or
  a historical attainment figure.
- The trace shows that a request reached each worker. It does not show what the Auditor read, what
  the model returned, or which findings were routed; those are established by evidence 11 and 12.
- It is not a Gateway authorization result, a Model Armor refusal, or a retry/dead-letter proof.
