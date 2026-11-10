## 3. System and threat model

**Assets.** The protected assets are:

- raw IAM policy (members, roles, resources and bindings);
- the department catalog;
- human-exception decisions and their approver identity;
- the review records sent to departments;
- the integrity of the investigation lifecycle, meaning that "completed" means the work ran.

**Trust boundaries.** The deployed path crosses six trust boundaries (Figure 1):

| Boundary | Crossing | Control at the boundary |
|---|---|---|
| T1 | Pub/Sub and Eventarc → private dispatcher | Durable admission, leases and attempt counting; completion only on confirmation |
| T2 | Dispatcher → managed Agent Runtime | Identity-bearing session; investigation ID carried as run metadata, not model-visible content |
| T3 | Runtime → A2A workers | Protected Cloud Run services that accept only a peer-origin credential; validated message content |
| T4 | Runtime egress → Agent Gateway | Managed egress gateway (`AGENT_TO_ANYWHERE`) with a fail-closed Identity-Aware Proxy (IAP) authorization extension and a regional Agent Registry |
| T5 | Worker → model | Model Armor screening of inputs, including tool results, and of outputs, failing closed |
| T6 | Worker → IAM | A zero-argument minimising tool under the Auditor's read-only identity |

The Gateway is egress-only. It decides which destinations the Runtime may reach; it never authorises callers. Caller authorisation happens at the workers (T3) and at the findings API. [S1, E05, E17]

**Trusted.** The deployed deterministic code, its configuration and secrets, the department catalog, the Google Cloud IAM authorisation plane, and the managed services the workflow depends on. The Auditor workload necessarily handles raw policy. A compromise of that workload or of its read credential is outside the minimisation guarantee.

**Untrusted.** Model output; caller-supplied content, including content from an authenticated but compromised caller; and anything a remote agent returns.

**Failures in scope.**

- A model alters a finding, invents one or omits a required action.
- An authorised caller supplies a prompt injection.
- A caller without the right identity attempts an approval or a privileged read.
- A decision is lost or replaced at a service boundary.
- A component reports success without having done the work.
- A dependency is slow or unavailable, and the investigation must fail visibly rather than silently.

**Out of scope.** Anonymous injection that has already passed the worker-origin credential gate; denial of service; legal compliance; IAM remediation (the fleet never changes a binding); and any general information-flow guarantee.

**Design goals.**

- G1: raw policy never becomes model input.
- G2: the model cannot change authoritative finding fields.
- G3: deterministic code decides policy, routing and delivery.
- G4: every completion is confirmed by evidence produced by the step that did the work.
- G5: the audit trail correlates the distributed flow without carrying payloads or principals.

G4 is the goal that the failures in Section 6 repeatedly violated. Most of the control evolution in this report serves it.
