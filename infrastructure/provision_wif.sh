#!/usr/bin/env bash
# Federate GitHub Actions into this project with no key material, then grant it exactly enough
# to deploy code and nothing else.
#
# Why this exists at all: every deploy today runs from one workstation with one human's
# credentials. That is a single point of failure and an unauditable one — the IAM log shows a
# person, not a pipeline, and nothing reproduces the deploy if that machine is unavailable.
#
# Why it grants so little: CI deploys *code*. It does not change authority. No role below can
# create a binding, alter Eventarc or Pub/Sub, edit the Agent Registry, or touch Firestore,
# Secret Manager, or the audit bucket. Provisioning authority stays an operator action performed
# by a named human, because the ledger exists to distinguish a human decision from an automated
# one — see ADR-008 for the same argument applied to exception approval.
#
# No service-account key is ever created. Federation exchanges a short-lived GitHub OIDC token
# for a short-lived Google token; there is nothing to leak and nothing to rotate.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
REGION="${GCP_REGION:?set GCP_REGION explicitly}"
# The one value that must be exact. The attribute condition below is the entire security boundary
# of this federation: without it, *any* GitHub repository in the world could mint a token that
# this project accepts.
REPOSITORY="${BASTION_GITHUB_REPOSITORY:?set BASTION_GITHUB_REPOSITORY, e.g. owner/bastion}"
POOL="${BASTION_WIF_POOL:-github-pool}"
PROVIDER="${BASTION_WIF_PROVIDER:-github-provider}"
DEPLOYER="github-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"

if [[ "$REPOSITORY" != */* || "$REPOSITORY" == */*/* ]]; then
  echo "BASTION_GITHUB_REPOSITORY must be exactly owner/repo, got: ${REPOSITORY}" >&2
  exit 64
fi

echo "Federating ${REPOSITORY} into ${PROJECT_ID} (no keys will be created)."

# --- the federated identity -----------------------------------------------------------------
gcloud iam service-accounts describe "$DEPLOYER" --project="$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud iam service-accounts create github-deployer \
    --project="$PROJECT_ID" \
    --display-name="GitHub Actions deployer (WIF)" \
    --description="Federated CI identity. Deploys code; never changes IAM, Eventarc, Pub/Sub, or the Registry."

gcloud iam workload-identity-pools describe "$POOL" \
  --project="$PROJECT_ID" --location=global >/dev/null 2>&1 || \
  gcloud iam workload-identity-pools create "$POOL" \
    --project="$PROJECT_ID" --location=global \
    --display-name="GitHub Actions" \
    --description="Federated identity for ${REPOSITORY} CI. No keys are ever issued."

# `--attribute-condition` is not optional hardening; it is the boundary. Google will accept any
# token this issuer signs, and GitHub signs one for every repository on the platform. Pinning
# `assertion.repository` is what makes the trust specific to this repository rather than to
# GitHub as a whole.
gcloud iam workload-identity-pools providers describe "$PROVIDER" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL" >/dev/null 2>&1 || \
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
    --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL" \
    --display-name="GitHub OIDC" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository == '${REPOSITORY}'"

POOL_RESOURCE="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}"

# Only this repository may impersonate the deployer. Scoped to attribute.repository rather than
# to the pool: a pool-wide binding would re-open exactly what the attribute condition closes.
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_RESOURCE}/attribute.repository/${REPOSITORY}" \
  --condition=None >/dev/null

# --- what the deployer may do -----------------------------------------------------------------
# run.developer, not run.admin: it may deploy a revision to an existing service, and may not
# rewrite that service's IAM policy. `gcloud run deploy` re-establishes the service IAM policy,
# which is precisely why deploy.sh reapplies the approver grant — CI must not be able to.
for role in \
  roles/run.developer \
  roles/cloudbuild.builds.editor \
  roles/artifactregistry.writer \
  roles/aiplatform.user \
  roles/logging.viewer
do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOYER}" --role="$role" --condition=None >/dev/null
  echo "  granted ${role}"
done

# Deploying a Cloud Run service means acting as the identity that service runs as. Granted per
# service account rather than project-wide, so the deployer can act as the fleet's workload
# identities and as nothing else — notably not as approver-sa, which would let a pipeline
# approve the suppression of a finding.
for sa in orchestrator-sa access-auditor-sa escalation-agent-sa; do
  target="${sa}@${PROJECT_ID}.iam.gserviceaccount.com"
  if gcloud iam service-accounts describe "$target" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam service-accounts add-iam-policy-binding "$target" \
      --project="$PROJECT_ID" \
      --member="serviceAccount:${DEPLOYER}" \
      --role="roles/iam.serviceAccountUser" --condition=None >/dev/null
    echo "  may act as ${sa}"
  else
    echo "  skipped ${sa} (not present)" >&2
  fi
done

cat <<SUMMARY

Federation ready. Set these two repository variables in GitHub
(Settings -> Secrets and variables -> Actions -> Variables). Neither is a secret: a pool
resource name and a service-account email authorize nothing without a token GitHub signs for
${REPOSITORY} specifically.

  GCP_WIF_PROVIDER = ${POOL_RESOURCE}/providers/${PROVIDER}
  GCP_DEPLOY_SA    = ${DEPLOYER}

Then run the "Deploy" workflow manually. It is deliberately not triggered by push:
a deploy to a live access-governance fleet is a decision, and someone should make it.
SUMMARY
