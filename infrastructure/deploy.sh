#!/usr/bin/env bash
# Build one reviewed image context, deploy each agent privately, then connect private A2A peers.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
REGION="${GCP_REGION:?set GCP_REGION explicitly}"
MODEL_LOCATION="${GOOGLE_CLOUD_LOCATION:?set GOOGLE_CLOUD_LOCATION=global for Gemini}"
MODEL_ARMOR_TEMPLATE_ID="${MODEL_ARMOR_TEMPLATE_ID:?set MODEL_ARMOR_TEMPLATE_ID}"
MODEL_ARMOR_LOCATION="${MODEL_ARMOR_LOCATION:?set MODEL_ARMOR_LOCATION}"
FINDING_HMAC_SECRET="${BASTION_FINDING_HMAC_SECRET:?set Secret Manager secret id for keyed finding IDs}"
MAX_INSTANCES="${BASTION_MAX_INSTANCES:-3}"
MEMORY_LIMIT="${BASTION_MEMORY_LIMIT:-1Gi}"
SESSION_URI="${BASTION_SESSION_SERVICE_URI:?set a managed non-memory ADK session service URI}"
MEMORY_URI="${BASTION_MEMORY_SERVICE_URI:?set a managed non-memory ADK memory service URI}"
TOPIC="${PUBSUB_TOPIC:?set PUBSUB_TOPIC}"
IMAGE_REPOSITORY="${BASTION_IMAGE_REPOSITORY:-cloud-run-source-deploy}"
IMAGE_TAG="${BASTION_IMAGE_TAG:-$(git rev-parse --short HEAD)}"
IMAGE="${BASTION_IMAGE:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_REPOSITORY}/bastion:${IMAGE_TAG}}"

if [[ "$SESSION_URI" == "memory://" || "$MEMORY_URI" == "memory://" ]]; then
  echo "Refusing ephemeral memory:// services: cross-week context must be durable." >&2
  exit 64
fi

sa() { echo "$1@${PROJECT_ID}.iam.gserviceaccount.com"; }
# ``status.url`` can retain a legacy hashed alias after a revision update.  Cloud Run's
# canonical regional hostname is deterministic and is what peers must publish in their cards.
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
uri() { echo "https://$1-${PROJECT_NUMBER}.${REGION}.run.app"; }

# Build once, deploy the exact same immutable image to every private service.  `gcloud run
# deploy --source` wraps this sequence but has proven to hang after source upload on Windows;
# the explicit Cloud Build boundary yields a build ID, auditable logs, and no hidden wait.
if [[ -z "${BASTION_IMAGE:-}" ]]; then
  if ! gcloud artifacts repositories describe "$IMAGE_REPOSITORY" --project "$PROJECT_ID" --location "$REGION" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$IMAGE_REPOSITORY" --project "$PROJECT_ID" --location "$REGION" \
      --repository-format=docker --quiet
  fi
  gcloud builds submit . --project "$PROJECT_ID" --tag "$IMAGE" --quiet
fi

deploy_agent() {
  local service=$1 agent_dir=$2 account=$3 extras=${4:-}
  local -a secret_args=()
  if [[ "$agent_dir" == "access_auditor" ]]; then
    secret_args=(--set-secrets "BASTION_FINDING_HMAC_KEY=${FINDING_HMAC_SECRET}:latest")
  fi
  gcloud run deploy "$service" --quiet \
    --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
    --service-account "$account" --no-allow-unauthenticated --ingress internal \
    --min-instances 0 --max-instances "$MAX_INSTANCES" --memory "$MEMORY_LIMIT" \
    --set-env-vars "BASTION_AGENT_DIR=$agent_dir,BASTION_SERVICE_URL=https://placeholder.invalid,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$MODEL_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=TRUE,VERTEX_AI_MODEL=${VERTEX_AI_MODEL:-gemini-3.5-flash},MODEL_ARMOR_TEMPLATE_ID=$MODEL_ARMOR_TEMPLATE_ID,MODEL_ARMOR_LOCATION=$MODEL_ARMOR_LOCATION,BASTION_SESSION_SERVICE_URI=$SESSION_URI,BASTION_MEMORY_SERVICE_URI=$MEMORY_URI,ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false,OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT${extras}" \
    "${secret_args[@]}" \
    --labels "app=bastion,agent=$agent_dir,classification=internal"
  # Cloud Run assigns the canonical origin during the source deploy.  Publish that exact
  # origin in the card rather than a guessed hostname, then wait for the card revision.  Query
  # again after the update: Cloud Run can promote a new canonical URL with that revision.
  gcloud run services update "$service" --project "$PROJECT_ID" --region "$REGION" \
    --update-env-vars "BASTION_SERVICE_URL=$(uri "$service")" >/dev/null
  gcloud run services update "$service" --project "$PROJECT_ID" --region "$REGION" \
    --update-env-vars "BASTION_SERVICE_URL=$(uri "$service")" >/dev/null
}

deploy_findings_api() {
  gcloud run deploy bastion-findings-api --quiet \
    --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
    --service-account "$(sa findings-api-sa)" --no-allow-unauthenticated --ingress internal \
    --min-instances 0 --max-instances "$MAX_INSTANCES" \
    --command python --args=-m,infrastructure.findings_api \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --labels "app=bastion,component=findings-inbox,classification=internal"
}

# The notification surface is Bastion-owned and private. It stores a count-only human-review
# record; an arbitrary public webhook is not a deployment option.
deploy_findings_api
FINDINGS_ENDPOINT="$(uri bastion-findings-api)/v1/escalations"
gcloud run services add-iam-policy-binding bastion-findings-api --project "$PROJECT_ID" --region "$REGION" \
  --member="serviceAccount:$(sa escalation-agent-sa)" --role=roles/run.invoker

# Peers first: their URIs are inputs to the Orchestrator, never manually copied into .env.
deploy_agent bastion-access-auditor access_auditor "$(sa access-auditor-sa)"
deploy_agent bastion-escalation-agent escalation_agent "$(sa escalation-agent-sa)" \
  ",BASTION_FINDINGS_ENDPOINT=$FINDINGS_ENDPOINT"

AUDITOR_URI="$(uri bastion-access-auditor)"
ESCALATION_URI="$(uri bastion-escalation-agent)"

# Only the orchestrator's workload identity may invoke either peer.
for service in bastion-access-auditor bastion-escalation-agent; do
  gcloud run services add-iam-policy-binding "$service" --project "$PROJECT_ID" --region "$REGION" \
    --member="serviceAccount:$(sa orchestrator-sa)" --role=roles/run.invoker
done

deploy_agent bastion-orchestrator orchestrator "$(sa orchestrator-sa)" \
  ",BASTION_AUDITOR_CARD_URL=$AUDITOR_URI/a2a/access_auditor/.well-known/agent-card.json,BASTION_ESCALATION_CARD_URL=$ESCALATION_URI/a2a/escalation_agent/.well-known/agent-card.json"

# Eventarc delivers Pub/Sub CloudEvents only to the Orchestrator's ADK trigger path. Its
# dedicated delivery identity receives `run.invoker` on this one service — never on a peer.
EVENTARC_SA="$(sa eventarc-invoker-sa)"
PUBSUB_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"
EVENTARC_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-eventarc.iam.gserviceaccount.com"
gcloud run services add-iam-policy-binding bastion-orchestrator --project "$PROJECT_ID" --region "$REGION" \
  --member="serviceAccount:${EVENTARC_SA}" --role=roles/run.invoker
# Older deployments granted the Eventarc service agent directly. Delivery now uses the dedicated
# identity below, so remove that broader leftover binding when it is present.
gcloud run services remove-iam-policy-binding bastion-orchestrator --project "$PROJECT_ID" --region "$REGION" \
  --member="serviceAccount:${EVENTARC_SERVICE_AGENT}" --role=roles/run.invoker >/dev/null 2>&1 || true
# The Pub/Sub service agent mints the OIDC delivery token. Scope this permission to the one
# delivery identity rather than granting it project-wide.
gcloud iam service-accounts add-iam-policy-binding "$EVENTARC_SA" --project "$PROJECT_ID" \
  --member="serviceAccount:${PUBSUB_SERVICE_AGENT}" --role=roles/iam.serviceAccountTokenCreator
if ! gcloud eventarc triggers describe bastion-investigations-to-orchestrator \
  --project "$PROJECT_ID" --location "$REGION" >/dev/null 2>&1; then
  gcloud eventarc triggers create bastion-investigations-to-orchestrator \
    --project "$PROJECT_ID" --location "$REGION" \
    --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
    --transport-topic="projects/${PROJECT_ID}/topics/${TOPIC}" \
    --service-account="$EVENTARC_SA" \
    --destination-run-service=bastion-orchestrator --destination-run-region="$REGION" \
    --destination-run-path=/apps/orchestrator/trigger/eventarc
else
  gcloud eventarc triggers update bastion-investigations-to-orchestrator \
    --project "$PROJECT_ID" --location "$REGION" --service-account="$EVENTARC_SA"
fi

printf 'Deployed private fleet:\n  orchestrator: %s\n  auditor: %s\n  escalation: %s\n' \
  "$(uri bastion-orchestrator)" "$AUDITOR_URI" "$ESCALATION_URI"

python -m infrastructure.register_agents
python -m infrastructure.verify_fleet
