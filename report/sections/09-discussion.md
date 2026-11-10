## 9. Discussion and research agenda

### 9.1 What generalises, and what does not

The historical failures motivate a common design principle: make execution and downstream completion explicitly checkable at each boundary. The individual repairs differed, including explicit message content, receipt checks, parser compatibility and bounded model retry. Applying this principle requires knowing where the boundaries are. D6, D8 and D9 escaped a test suite with 100% configured statement and branch coverage, because the tests exercised an in-process topology in which state is shared. The E24 parser and an SDK client attribute that a test double supplied (Appendix A.1) passed the suite for the same reason. A test double encodes its author's belief about a boundary, not the boundary itself. Coverage measures which local branches ran. It cannot show that a separate service received a value, that a remote step ran at all, or that a side effect was confirmed. [S10, S14]

The case study motivates boundary tests for each real transport:

- remote output with no shared session;
- a state-only event before a remote call;
- an absent or malformed reply;
- a failed remote task;
- an empty or truncated stream;
- a caller-visible timeout whose callee keeps running.

It does not show that these instances are exhaustive, or that every agent framework fails the same way. Some failures were Bastion's own violations of its contracts (D1, E19). Others were Bastion's wrong assumptions about documented framework semantics (D6, D8). The distinction matters, because only the second kind is a portable lesson about the framework.

The final evaluation also shows the value of retaining stopped runs. G's instrument stop, H's model 429 and L's invalid field mask each ended a protocol execution. G5 and L1 completed in the cloud; the stopped records were retained, and later work is reported separately. H28 then motivated the bounded model retry that I57 exercised. Had these stopped records been replaced or pooled, the record would show a cleaner result and less evidence.

### 9.2 Primary direction: across the agent boundary

The primary follow-on question is: **do agent frameworks preserve execution contracts when sub-agents become remote?** The proposed study would compose equivalent workflows twice within each framework, once in-process and once with sub-agents behind A2A, using both naive and idiomatic ports. It would measure, against an independent observation ledger:

- propagation of errors and refusals across the boundary;
- visibility of state and of policy decisions;
- fidelity of A2A task state;
- propagation of context and correlation identifiers;
- outcome uncertainty after a partial failure, including cancellation after a caller-visible timeout;
- persisted side effects.

Documented framework behaviour would be kept separate from application violations, as in Section 6. D6, D8 and D9 and the M-Cancellation observation motivate the study. **It has not been performed, and no comparative result is claimed.**

### 9.3 Other directions

- **C4, minimised against raw inputs.** The deterministic findings would be held fixed while comparing three conditions: a model explaining synthetic raw IAM policy together with those findings, a model explaining the same findings alone, and deterministic templates. The study would measure protected-string disclosure, drift from the rule set, explanation support, reviewer usefulness and tokens. All policies must be synthetic, because the raw condition exposes exactly the data the product withholds. The harness exists; the protocol must be fixed before any model call.
- **Telemetry on managed platforms.** Investigate why Runtime graph spans were exported for only some investigations, and when exported spans can be trusted as evidence.
- **Cancellation propagation.** Measure, per transport, whether a caller-visible timeout reaches remote computation, and design idempotent, cancellable remote steps.
- **Platform questions.** Ask Google Cloud why IAP resolves registered non-standard hostnames to `unregisteredEndpoint`. File the contentless failed-task behaviour upstream.
