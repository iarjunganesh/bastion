# Bastion: Execution Boundaries, Control Evolution, and Bounded Evaluation of a Governed Agent Fleet

Arjun Ganesh

Independent researcher, Stockholm

November 2026 | Technical report

## Abstract

Bastion is a deployed, three-agent fleet that reviews Google Cloud Identity and Access Management (IAM) access. It was built so that deterministic code, rather than a language model, holds every policy decision. An Access Auditor reads IAM under a read-only identity and gives the model only opaque finding identifiers, departments, reason codes and bounded scores. Model-free steps apply human exceptions and thresholds, route findings to owning departments and require delivery receipts. A separate Escalation Agent, which cannot read IAM, creates human-review records.

This report is an evidence-grounded account of the fleet in four parts: how it was designed, where its execution boundaries failed, how its controls evolved in response, and what the final bounded evaluation did and did not demonstrate. Between August and November 2026, five dated failures exposed gaps between local execution signals and downstream work. A completed status, a worker-local state key, a state-only policy decision, an error-free remote reply or a closed response stream did not establish that the intended work had run across the boundary. Repairs made policy execution, handoffs and downstream completion explicitly checkable.

The final bounded evaluation covered G and H on v0.9.0 and I–M on v0.9.1 on 7–8 November 2026 under pre-specified protocols. One cohort recorded 98 of 98 validated serial production investigations before an instrument stop. Two earlier cohorts are retained as stopped: one on an instrument fault and one on a model-service rejection that failed closed. Targeted controls passed: a direct completion check, five completed-event replays, a prompt-injection refusal and the rejection of a forged routing envelope. A read-only telemetry census found Runtime graph spans in 5 of 142 agent traces. A timeout fault injection observed fail-closed handling, redelivery and dead-lettering. It also observed worker computation continuing after the caller had timed out. The evaluation supports bounded observations on one project and one workload. It is not a reliability rate, a service-level objective, a comparative privacy result or a general security guarantee.

**Contributions.** C1, a governed, minimisation-first architecture with deterministic policy authority, explicit agent handoffs and durable execution controls. C2, a dated failure-and-repair case study that separates observed behaviour from framework-documented semantics. C3, a bounded deployment evaluation under pre-specified protocols that retains its stopped runs, negative controls and fault injection.
