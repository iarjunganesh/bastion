## 8. What the evaluation does not demonstrate

Each limitation is stated once here, and other sections refer to it.

**No general or field reliability rate, and no service-level objective.** Cohort I's 98 of 98 is a count of validated serial investigations on one deployment over three hours. The conditional Clopper–Pearson bound of about 3.01% (Section 5.7) holds only under an i.i.d. Bernoulli model that these observations do not establish. G and H stopped, and the earlier false completion (1 in 28) is reported with its denominator, not as a percentage. No figure in this report is a reliability estimate.

**No representativeness.** There was one Google Cloud project. The 7–8 November G–M preflights recorded a bounded workload of 62 bindings, 3 findings and 2 departments; the earlier 56-binding census belongs to 28 October and does not establish a binding count for cohort N's 3–4 November investigations. The detector flags only Owner and Editor grants, with a fixed score that is not a calibrated probability. It drops conditions, does not detect stale identities and stops at 500 results. Its recall against real IAM risk is not measured. [S2]

**No concurrency, scale, multi-tenancy or scheduled operation.** Every cohort was serial. The fleet is triggered by an approved event source; there is no Scheduler job, and recurring or continuous operation is not claimed. [E15]

**No tracing of every investigation.** Trace export after the upgrade was observed to be incomplete (Section 7.4). Traces join investigations only by time window, because audit records carry no trace ID. [E28]

**No unregistered-caller Gateway refusal.** The Gateway is egress-only, so a refusal of an unregistered caller cannot occur there and is not claimed. The E20 refusals were an incidental SDK lookup to a registered host. They show fail-closed handling of unmatched traffic, not discrimination between registered and unregistered destinations. [E20]

**No C4 result.** No study measures whether minimisation costs the model useful context, or whether the rationale helps a reviewer. Minimisation is pseudonymisation: opaque IDs are linkable, and departments, categories, counts and timing still reveal information. Zero raw fields in the finding schema is not a measured zero probability of leakage.

**No exact cost.** Execution stayed within credits under per-chunk caps, and the daily billing checks of 6 and 8 November showed reported usage fully offset. Exact per-chunk cost was not measured, and late postings were not ruled out.

**No reading of the Runtime's installed packages.** Image builds asserted their package versions (Appendix A.1). The managed Runtime's installed resolution was never read independently.

**No guarantee that in-flight remote computation is cancelled after a caller-visible timeout.** M observed the opposite in the tested configuration (Section 7.5).

**Further boundaries.**

- *Single probes.* Each authorisation and screening probe ran once, against one fixture or one token shape. This is not fuzzing. The screening probes model a compromised authorised caller, not an anonymous one. [E17, E18, E27]
- *Event-specific retry and dead-letter observations.* E21 observed one permanent ingress rejection, the F pilot observed a parser failure with five failed deliveries (joined to its dead-letter message post hoc in Appendix C.4), and M observed one injected worker timeout. H28 separately observed redelivery after a model 429. These cases do not establish a general delivery-attempt bound; Google documents the configured dead-letter count as approximate, and delivery of a paging notification was not verified. [R11, E21, E24, E26, E29]
- *Replays.* The bounded replay observations do not establish exactly-once delivery.
- *Routing provenance.* The test shows that Auditor-attributed routing is rejected. It does not show that unauthorised routing is impossible (Section 6.2).
- *Pre-specification.* The protocols are pre-specified, not pre-registered. M's original protocol hash is reconstructed (Section 5.5).
- *Governance.* The audit bucket is not locked. The exception ledger retains the verified approver identity. Global inference rules out a claim of end-to-end EU residency. No legal compliance is claimed. [S3, E07]
- *Fleet end state.* The fleet was retired on 9 November 2026, so none of these observations can be repeated on the same deployment (Appendix A.4).
