# Required GCP access

Run provisioning as an approved project deployer. Agent identities never receive deployment or
administrative roles.

## Deployer prerequisites

- Google Cloud CLI authenticated for the target project and Application Default Credentials;
- Python 3.12 and Git for Windows Bash at `C:\Program Files\Git\bin\bash.exe`;
- project permissions equivalent to Service Usage Admin, Cloud Run Admin, Eventarc Admin,
  Pub/Sub Admin, Artifact Registry Admin/Writer, Cloud Build Editor/Builder, Service Account
  Admin/User, Secret Manager Admin, Monitoring Editor, Logging Config Writer, and the permissions
  to manage Agent Runtime, Agent Registry, Agent Gateway/IAP, Firestore, and Model Armor;
- access to an existing Model Armor template. Only its administrator needs
  `roles/modelarmor.admin`; agents receive `roles/modelarmor.user` where needed.

## Required inputs

`bootstrap.ps1` requires the project ID plus existing Memory and Runtime Agent Engine IDs. It
uses explicit defaults `europe-north2` for Cloud Run/data transport, `europe-west4` for managed
agent controls, and `global` for Gemini.

The bootstrap creates missing generated 256-bit HMAC and A2A secrets without printing values.
It grants the HMAC only to the Auditor; it grants the A2A origin secret to both workers, Google
Runtime deployment identities, and the managed Runtime Agent Identity. The Cloud Run dispatcher
does not receive that secret.

The findings endpoint is deployed by Bastion. No external webhook is required: only the
Escalation service identity receives `roles/run.invoker` and the endpoint stores a count-only,
idempotent review record.

## Windows 11 command

```powershell
.\infrastructure\bootstrap.ps1 `
  -Project 'YOUR_PROJECT_ID' `
  -MemoryAgentEngineId 'YOUR_MEMORY_ENGINE_ID' `
  -RuntimeAgentEngineId 'YOUR_RUNTIME_ENGINE_ID'
```

Provisioning and verification are idempotent. Rollback and teardown are separate, dry-run-first
commands and are never invoked by bootstrap.
