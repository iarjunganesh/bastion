## 1. Introduction

An access-review agent must answer questions that a fluent explanation cannot settle. Which production evidence was read? Which code decided that a review was needed? Did a human exception change the result? Did the next service receive the decision, and was the review record actually created? Each question has a cheap and misleading answer: an explanation that sounds right, a state key that is populated, a remote call that returned without an error, or an investigation marked completed.

Bastion is a deployed fleet built to make those answers checkable. On one live Google Cloud project, an Access Auditor reads IAM under a read-only identity. Deterministic code flags Owner and Editor grants, assigns department ownership and gives the model a minimised finding: an opaque identifier, a department, a reason code and a bounded score. Gemini writes a short rationale per finding. Model-free steps then preserve the finding set, apply human exceptions and thresholds, route delivery to departments and confirm completion. The Escalation Agent cannot read IAM or change a binding, and its output is a human-review record, not an access decision. [S1–S3, S6–S8]

Building, operating and measuring the fleet repeatedly exposed one failure pattern. A component produced the signal that ordinarily means "done", and nothing checked that the work behind that signal had happened:

- a policy step was refused before its tools ran, and the investigation still reported completion;
- a correctly computed decision disappeared at an agent-to-agent (A2A) boundary, so the next service acted on older content;
- a failed remote task arrived as an empty, error-free event;
- a managed Runtime stream closed with no investigation run, and the durable record read completed.

Later work found smaller instances of the same mismatch. Each was caught before a false success was recorded: a framework upgrade changed how relayed content was wrapped, and a model service rejected a request with HTTP 429.

This report asks one question. **What does it take for application-level correctness claims about a distributed agent fleet to rest on evidence, and what did that require in one deployed system?** Its unifying lesson is that such claims require evidence at execution boundaries. Unit tests, coverage, status fields and the absence of exceptions are local signals. They do not show that a separate service received a value, that a remote step ran, or that a side effect was confirmed.

The report makes three contributions:

- **C1, a governed architecture (Sections 3–4).** A deployed IAM-review fleet that keeps raw policy away from the model, holds policy authority in deterministic code, crosses agent boundaries only through explicit, validated content, and makes completion depend on confirmations produced by the step that did the work.
- **C2, a failure-and-repair case study (Section 6).** Dated execution-boundary failures from August to November 2026, the controls that answered them, and what each repair did and did not verify. Behaviour that the framework documents is kept separate from Bastion's own violations of its contracts.
- **C3, a bounded deployment evaluation (Sections 5 and 7).** Pre-specified protocols on v0.9.0 (G and H) and v0.9.1 (I–M), covering successful serial runs, two stopped cohorts, a model-retry recovery, negative security controls, replay checks, a telemetry census and a timeout fault injection. Section 8 states what the evaluation does not demonstrate.

The contribution is an implementation-grounded case study, not a general framework, a benchmark or a comparative result. A planned comparison of minimised and raw model inputs (C4) is deferred and reports no results. A cross-framework study of execution contracts across remote agent boundaries is proposed as future research in Section 9; it has not been performed. Bastion began as personal work for the All Things Agentic Hackathon 2026. No award or placement is claimed.
