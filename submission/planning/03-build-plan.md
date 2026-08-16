# Build and verification plan

The P0/P1 build is complete. This file records the final execution order so a new project or
release follows the same dependencies.

1. Install Python 3.12 dependencies and run offline quality/security gates.
2. Enable APIs; create workload identities, Firestore, topics, DLQ, Model Armor access, and
   generated secrets.
3. Deploy the findings API and two worker A2A services from one immutable image.
4. Provision Registry platform endpoints and Agent Gateway/IAP policy.
5. Update the managed Runtime source deployment with Agent Identity and Gateway binding.
6. Register the managed Runtime and worker Agent Cards; grant per-resource egress/invocation.
7. Deploy the Eventarc durable dispatcher with its Runtime target and remove legacy direct-peer
   credentials/grants.
8. Provision the audit sink/bucket, metrics, alerts, and dashboard.
9. Run fleet verifier, full production smoke, safe rollback dry run, and teardown dry run.
10. Recapture count-only state, regenerate visuals, sweep Markdown, run all gates, commit, push,
    and verify GitHub Actions.

The repeatable Windows entry point is `infrastructure/bootstrap.ps1`. Existing Memory and Runtime
engine IDs are mandatory because managed engine creation is an explicit platform-owner action.
