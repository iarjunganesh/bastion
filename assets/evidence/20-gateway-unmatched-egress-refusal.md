# Evidence 20 — Agent Gateway refuses egress it does not match to a registered endpoint

**Collected:** 4 November 2026, evidence chunk E5 of cohort N. Read-only: configuration reads and
retained logs (IAP data-access audit, Runtime stdout and stderr, Firestore status counts) from
5 October onward. No request was sent, no identity created and nothing changed. The private
bundle records counts, timestamps and public Google API hostnames only.

## What the Gateway governs

Agent Gateway `bastion-egress` is `AGENT_TO_ANYWHERE`: it governs the managed Runtime's
outbound calls. Callers reaching the A2A workers are checked by the workers' peer credential
instead ([evidence 17](17-negative-authorization.md), P1 and P2), so this page is about egress.

| Configuration, read 4 Nov | Value |
|---|---|
| Registry bound to the Gateway | 1 (regional, 17 services) |
| IAP authorization extension | `iap.googleapis.com`, `failOpen` unset (fail-closed), policy version V1 |
| Gateway authorization policy | `CUSTOM`, `REQUEST_AUTHZ`, one target |
| `roles/iap.egressor` | held by one Agent Identity, unconditional |
| Admin-activity audit entries since 1 Sep | 0 (the same query returns 62 for 23 Aug, 20:00–20:15) |

The Gateway and its policy show update times of 4 and 26 October. With no admin-activity entry
since 1 September, these were platform-side updates, not configuration changes by the project.

## Observed refusals

| Measure | Value |
|---|---|
| IAP `AuthorizeUser` decisions, 5 Oct – 4 Nov | 176, all denied (code 7) |
| Permission checked | `iap.webServiceVersions.egressViaIAP` |
| Resource the request resolved to | `unregisteredEndpoint` (all 176) |
| Request | `cloudresourcemanager.mtls.googleapis.com/google.cloud.resourcemanager.v3.Projects/GetProject` (all 176) |
| Authenticated principal on the decision record | none (all 176) |
| Days | 27 Oct: 52; 3 Nov: 124 |
| Runtime instance starts in the window | 13; every one followed by exactly 12 refusals within 90 s (156) |
| Other refusals | 20, in pairs during runs |
| Runtime log lines for the failed project lookup | 88 (two IAP decisions per failed lookup) |
| Investigations completed on those days | 27 Oct: 20; 3 Nov: 31 |

Every refusal is the agent SDK's start-up project lookup. The Runtime logged it as
`PERMISSION_DENIED: Egress request is not authorized. The endpoint is either incorrect or
unregistered in the Agent Registry`, fell back, and the investigations completed. No granted
decision appears in this log, so it shows refusals but not the matched allows.

Say **the managed Gateway, with fail-closed IAP enforcement, refused every observed egress
request it did not match to a registered endpoint: 176 decisions across 13 Runtime instance
starts, while investigations continued.**

## What this does not show

- **A destination we chose.** The refused request is incidental, made by the SDK, not a probe
  aimed at a known-unregistered host. A deliberate probe would need new code in the Runtime.
- **That the host is unregistered.** The Registry has a gRPC entry for
  `https://cloudresourcemanager.mtls.googleapis.com`, created 18 August, yet IAP resolved the
  request to `unregisteredEndpoint`. A missing grant is ruled out, because the Agent Identity
  holds `roles/iap.egressor`. Why the Gateway did not match this entry is not visible from
  outside the platform. Report it as an unexplained mismatch between the Registry catalog and
  the Gateway's classification.
- **Matched allows.** Approved egress (Model Armor, Vertex AI, Firestore, the two workers)
  succeeded in every investigation that actually ran (E7's false completion ran nothing), but
  no granted IAP decision was logged to confirm the allow side directly.
