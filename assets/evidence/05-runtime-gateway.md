# Evidence 05 — managed Runtime and governed egress

**Observed:** 2026-08-16 UTC with the deployed Python 3.12 Agent Runtime in `europe-west4`.

- A managed session was created successfully.
- A read-only investigation query returned streamed events.
- Runtime configuration references the managed `bastion-egress` Agent Gateway.
- Gateway validation confirmed its authorization extension and fail-closed auth policy.
- Agent Registry contained the managed Orchestrator, two worker cards, and ten approved platform
  destinations.
- The Cloud Run durable dispatcher held a Runtime target but no A2A origin secret; its direct
  worker invoker grants were absent.

No Runtime ID, Agent Identity principal, URL, token, prompt, response, or finding was retained.
This is route/configuration proof, not a latency or availability SLO measurement.

Reproduce with the environment contract in the README:

```powershell
python -m infrastructure.verify_fleet
python -m infrastructure.smoke_test --skip-async-event
```
