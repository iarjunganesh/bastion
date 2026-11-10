## References

External sources R1–R11 and upstream records U1–U4 were checked in November 2026. Repository references (S, E) link to the public base revision named in the cited-source manifest where their bytes are unchanged, and are otherwise supplied in the source snapshot (Appendix A.2).

- **R1.** Edoardo Debenedetti, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas Carlini, Daniel Fabian, Christoph Kern, Chongyang Shi, Andreas Terzis, and Florian Tramèr. *Defeating Prompt Injections by Design*. arXiv:2503.18813v2, 2025. [Paper](https://arxiv.org/abs/2503.18813v2).
- **R2.** Luca Beurer-Kellner, Beat Buesser, Ana-Maria Creţu, Edoardo Debenedetti, Daniel Dobos, Daniel Fabian, Marc Fischer, David Froelicher, Kathrin Grosse, Daniel Naeff, Ezinwanne Ozoani, Andrew Paverd, Florian Tramèr, and Václav Volhejn. *Design Patterns for Securing LLM Agents against Prompt Injections*. arXiv:2506.08837v3, 2025. [Paper](https://arxiv.org/abs/2506.08837v3).
- **R3.** Miles Turpin, Julian Michael, Ethan Perez, and Samuel R. Bowman. *Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting*. NeurIPS 2023; arXiv:2305.04388v2. [Paper](https://arxiv.org/abs/2305.04388v2).
- **R4.** European Parliament and Council. Regulation (EU) 2016/679, Article 5(1)(c), 2016. [Official text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng).
- **R5.** Google Cloud. *Overview of role recommendations*. Documentation. [Documentation](https://docs.cloud.google.com/policy-intelligence/docs/role-recommendations-overview).
- **R6.** Jerome H. Saltzer, David P. Reed, and David D. Clark. *End-to-End Arguments in System Design*. ACM Transactions on Computer Systems 2(4):277–288, 1984. [DOI](https://doi.org/10.1145/357401.357402).
- **R7.** Peng Huang, Chuanxiong Guo, Lidong Zhou, Jacob R. Lorch, Yingnong Dang, Murali Chintalapati, and Randolph Yao. *Gray Failure: The Achilles' Heel of Cloud-Scale Systems*. HotOS 2017, 150–155. [DOI](https://doi.org/10.1145/3102980.3103005).
- **R8.** Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. *Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems*. OSDI 2014, 249–265. [Paper](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan).
- **R9.** C. J. Clopper and E. S. Pearson. *The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial*. Biometrika 26(4):404–413, 1934. [DOI](https://doi.org/10.1093/biomet/26.4.404).
- **R10.** Agent2Agent (A2A) Project. *Agent2Agent (A2A) Protocol Specification*. [Specification](https://a2a-protocol.org/latest/specification/).
- **R11.** Google Cloud. *Dead-letter topics* (Pub/Sub). Documentation. [Documentation](https://docs.cloud.google.com/pubsub/docs/dead-letter-topics).

- **S1.** [Architecture](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/ARCHITECTURE.md).
- **S2.** [Auditor implementation](https://github.com/iarjunganesh/bastion/blob/REVISION/agents/access_auditor/agent.py).
- **S3.** [Data governance](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/DATA_GOVERNANCE.md).
- **S4.** [Fixed tool boundary, ADR-007](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/adr/007-tool-poisoning.md).
- **S5.** [Claim matrix](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/research/claim-matrix.md); [Observation backlog, including defect D2](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/research/observation-backlog.md).
- **S6.** [Structured findings across A2A, ADR-012](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/adr/012-structured-findings-across-a2a.md).
- **S7.** [Policy enforcement gate, ADR-010](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/adr/010-policy-enforcement-gate.md); [Orchestrator implementation](https://github.com/iarjunganesh/bastion/blob/REVISION/agents/orchestrator/agent.py).
- **S8.** [Escalation implementation](https://github.com/iarjunganesh/bastion/blob/REVISION/agents/escalation_agent/agent.py).
- **S9.** [Tool-result screening, ADR-011](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/adr/011-inbound-screening-covers-tool-results.md); [Screening implementation](https://github.com/iarjunganesh/bastion/blob/REVISION/model_armor/guardrails.py).
- **S10.** [Repository guidance](https://github.com/iarjunganesh/bastion/blob/REVISION/AGENTS.md); [Coverage configuration](https://github.com/iarjunganesh/bastion/blob/REVISION/pyproject.toml).
- **S11.** [Earlier article source](https://github.com/iarjunganesh/bastion/blob/REVISION/archive/hackathon-2026/submission/ARTICLE_DRAFT.md).
- **S12.** [Durable ingress completion check](https://github.com/iarjunganesh/bastion/blob/REVISION/infrastructure/agent_server.py); [Its tests](https://github.com/iarjunganesh/bastion/blob/REVISION/tests/unit/test_agent_server.py).
- **S13.** [Retained-evidence numerical and collection audit](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/research/evidence-audit-2026-11-04.md).
- **S14.** [Release and deployment version provenance](https://github.com/iarjunganesh/bastion/blob/REVISION/docs/VERSIONS.md).
- **S15.** [Bounded model retry](https://github.com/iarjunganesh/bastion/blob/REVISION/agents/model_retry.py); [Its tests](https://github.com/iarjunganesh/bastion/blob/REVISION/tests/unit/test_model_retry.py).

- **E03.** [The Escalation Agent is denied the IAM policy, by IAM](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/03-escalation-agent-denied.md).
- **E05.** [Managed Runtime and governed egress](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/05-runtime-gateway.md).
- **E06.** [Durable delivery and idempotent human review](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/06-durable-findings.md).
- **E07.** [Retained operations controls](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/07-observability.md).
- **E09.** [Cross-department routing](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/09-cross-department-routing.md).
- **E10.** [An approved exception survives deployments and suppresses a later finding](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/10-cross-week-suppression.md).
- **E11.** [Current deployed route correlation](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/11-current-route-correlation.md).
- **E12.** [Deployed agent callback refuses prompt injection](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/12-agent-mediated-model-armor-refusal.md).
- **E13.** [Current deployed route reasoning chain in Cloud Trace](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/13-current-route-trace.md).
- **E14.** [Bounded live validation, 27 October 2026](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/14-live-validation.md).
- **E15.** [Count-only fleet inventory](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/15-fleet-inventory.md).
- **E16.** [Human exception approval, suppression and expiry](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/16-exception-lifecycle.md).
- **E17.** [Negative authorization probes](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/17-negative-authorization.md).
- **E18.** [Agent-mediated Model Armor refusal, re-probed](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/18-model-armor-refusal-reprobe.md).
- **E19.** [Repeatability batch and a false completion](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/19-repeatability-and-false-completion.md).
- **E20.** [Agent Gateway refuses egress it does not match to a registered endpoint](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/20-gateway-unmatched-egress-refusal.md).
- **E21.** [A rejected event is redelivered and dead-lettered on the production subscription](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/21-redelivery-and-dead-letter.md).
- **E22.** [The A2A state boundary, reproduced on the locked stack](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/22-a2a-state-boundary-reproduction.md).
- **E23.** [Deployment census and installed packages](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/23-deployment-census.md).
- **E24.** [Upgraded deployment and stopped pilot](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/24-upgraded-deployment-and-stopped-pilot.md).
- **E25.** [Corrected cohort F verification](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/25-corrected-cohort-F-verification.md).
- **E26.** [Cohorts G, H and I on the v0.9.0 and v0.9.1 deployments](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/26-cohorts-g-h-i.md).
- **E27.** [Targeted controls J on the v0.9.1 fleet](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/27-targeted-controls-j.md).
- **E28.** [Runtime trace export: isolation run K and a read-only census](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/28-telemetry-census-k.md).
- **E29.** [Worker timeout fault injection: runs L and M](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/29-timeout-fault-injection-l-m.md).

- **U1.** [ADK issue 6854](https://github.com/google/adk-python/issues/6854). Closed as completed 12 October 2026.
- **U2.** [ADK PR 6859](https://github.com/google/adk-python/pull/6859). Community PR by Sylvester Kaczmarek, including the author's legacy-path warning (`3e74d00`) and end-to-end test (`86343bf`). Imported into ADK `main` as `d2cb22e` on 12 October 2026; the GitHub PR was closed after import.
- **U3.** [ADK PR 6862](https://github.com/google/adk-python/pull/6862). Closed unmerged 24 August 2026.
- **U4.** [ADK commit d2cb22e](https://github.com/google/adk-python/commit/d2cb22e), "fix: warn when session state is dropped", 12 October 2026; first released in [v2.12.0](https://github.com/google/adk-python/releases/tag/v2.12.0), 13 October 2026.
