# Submission architecture summary

The authoritative design is [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md). The video and
Devpost copy should use this compressed sequence:

```text
Pub/Sub -> Eventarc/OIDC -> private durable ingress -> Firestore lifecycle
  -> managed Runtime Orchestrator (Agent Identity)
  -> Agent Gateway + IAP + Registry
      -> read-only Access Auditor -> production IAM/Asset
      -> Escalation Agent -> IAM-private findings API
  -> payload-free Cloud Logging/Trace -> retained metrics/alerts/dashboard
```

## Lines that must stay clear

- Cloud Run `orchestrator` is a durable dispatcher, not a second production agent graph.
- The agent catalog has one managed Runtime entry and two worker Agent Cards.
- Worker origins are application-authenticated for managed cross-region Gateway traffic; the
  findings endpoint is Cloud Run IAM-private.
- Raw IAM stops inside the Auditor's deterministic tool. Gemini sees minimized risk state.
- Firestore owns delivery state; managed Memory owns longer-lived agent context.
- Cloud/state regions are EU, but Gemini uses `global`, so end-to-end EU residency is not claimed.
- The audit bucket has 365-day retention and is unlocked.

Use the generated light/dark SVGs on GitHub and the animated 16:9 GIF on Devpost/video. Every
resource count must match `assets/architecture/gcp-state.json` at publication time.
