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
