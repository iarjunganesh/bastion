# Required GCP access

The deployment is designed to fail closed. The account running the provisioning command needs
access to the existing Model Armor template, plus ordinary project deployment permissions.

An approved project administrator should grant the deployment principal one of the following
least-privilege options before running `python -m infrastructure.provision --apply`:

- `roles/modelarmor.user` to use an existing template; and
- `modelarmor.templates.get` on `bastion-guardrail` (or the organisation's equivalent custom
  role).

Only a designated Model Armor administrator needs `roles/modelarmor.admin`, and only if the
template itself must be created or changed. Do not grant that role to agent service accounts.

The Cloud Run deployer also needs the normal build/deploy permissions: Cloud Run Admin, Service
Account User for each Bastion workload identity, Artifact Registry Writer, and Cloud Build
Builder. Those deployment roles belong to the human or CI deployer, never to an agent runtime.

Before deployment, an approved secret administrator must ensure a random ≥32-character value in
Secret Manager and set `BASTION_FINDING_HMAC_SECRET` to that secret's ID. The Bastion project has
an EU-replicated `bastion-finding-hmac` secret ready for this purpose. Only the Access Auditor
needs `Secret Manager Secret Accessor` on it; the deployment injects it as
`BASTION_FINDING_HMAC_KEY` and never commits or logs the value.

The organisation must also supply `BASTION_FINDINGS_ENDPOINT`: the authenticated internal
findings-review API that accepts Bastion's count-only, idempotent escalation payload. This is a
business-owned integration point; it must not be replaced with an invented public URL or a Slack
webhook. The deployment fails closed until it is set.
