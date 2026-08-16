#!/usr/bin/env bash
# Build one reviewed image context, deploy each agent privately, then connect private A2A peers.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
REGION="${GCP_REGION:?set GCP_REGION explicitly}"
MODEL_LOCATION="${GOOGLE_CLOUD_LOCATION:?set GOOGLE_CLOUD_LOCATION=global for Gemini}"
MODEL_ARMOR_TEMPLATE_ID="${MODEL_ARMOR_TEMPLATE_ID:?set MODEL_ARMOR_TEMPLATE_ID}"
MODEL_ARMOR_LOCATION="${MODEL_ARMOR_LOCATION:?set MODEL_ARMOR_LOCATION}"
FINDING_HMAC_SECRET="${BASTION_FINDING_HMAC_SECRET:?set Secret Manager secret id for keyed finding IDs}"
A2A_SHARED_SECRET="${BASTION_A2A_SHARED_SECRET_ID:-bastion-a2a-shared-secret}"
MAX_INSTANCES="${BASTION_MAX_INSTANCES:-3}"
MEMORY_LIMIT="${BASTION_MEMORY_LIMIT:-1Gi}"
SESSION_URI="${BASTION_SESSION_SERVICE_URI:?set a managed non-memory ADK session service URI}"
MEMORY_URI="${BASTION_MEMORY_SERVICE_URI:?set a managed non-memory ADK memory service URI}"
RUNTIME_REGION="${AGENT_RUNTIME_REGION:?set AGENT_RUNTIME_REGION}"
RUNTIME_ENGINE_ID="${BASTION_RUNTIME_AGENT_ENGINE_ID:?set BASTION_RUNTIME_AGENT_ENGINE_ID}"
TOPIC="${PUBSUB_TOPIC:?set PUBSUB_TOPIC}"
DEAD_LETTER_TOPIC="${BASTION_DEAD_LETTER_TOPIC:-bastion-investigations-dead-letter}"
DEAD_LETTER_REVIEW_SUB="${BASTION_DEAD_LETTER_REVIEW_SUB:-bastion-dead-letter-review}"
IMAGE_REPOSITORY="${BASTION_IMAGE_REPOSITORY:-cloud-run-source-deploy}"
IMAGE_TAG="${BASTION_IMAGE_TAG:-$(git rev-parse --short HEAD)}"
IMAGE="${BASTION_IMAGE:-${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_REPOSITORY}/bastion:${IMAGE_TAG}}"

if [[ "$SESSION_URI" == "memory://" || "$MEMORY_URI" == "memory://" ]]; then
  echo "Refusing ephemeral memory:// services: cross-week context must be durable." >&2
  exit 64
fi

sa() { echo "$1@${PROJECT_ID}.iam.gserviceaccount.com"; }
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
# Cloud Run validates an ID token's audience against the service's canonical status URL. A
# deterministic routing alias may reach the service but receives 401 when used as ``aud``.
uri() {
  gcloud run services describe "$1" --project "$PROJECT_ID" --region "$REGION" \
    --format='value(status.url)'
}

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
  local -a secret_cleanup_args=()
  local -a access_args=(--no-allow-unauthenticated)
  local ingress=internal
  local timeout=300
  local service_url=https://placeholder.invalid
  # Agent Gateway is a managed egress proxy in europe-west4; Cloud Run does not classify its
  # cross-region traffic as "internal" ingress. Peers therefore expose an IAM-protected
  # network endpoint, but remain non-public: no unauthenticated principal is granted and the
  # Agent Identity is authorized per destination at Gateway and Cloud Run layers.
  if [[ "$agent_dir" == "access_auditor" || "$agent_dir" == "escalation_agent" ]]; then
    ingress=all
    access_args=(--allow-unauthenticated)
  fi
  if [[ "$agent_dir" == "orchestrator" ]]; then
    # Eventarc owns retries, so the request must outlive a cold Runtime plus the full agent graph.
    # Its durable lease remains longer than this bound to prevent a concurrent reclaim.
    timeout=600
  fi
  if [[ "$agent_dir" == "access_auditor" ]]; then
    secret_args=(--set-secrets "BASTION_FINDING_HMAC_KEY=${FINDING_HMAC_SECRET}:latest,BASTION_A2A_SHARED_SECRET=${A2A_SHARED_SECRET}:latest")
  elif [[ "$agent_dir" == "escalation_agent" ]]; then
    secret_args=(--set-secrets "BASTION_A2A_SHARED_SECRET=${A2A_SHARED_SECRET}:latest")
  else
    # Reconciliation matters on an existing service: --set-secrets does not remove a secret
    # inherited from an older revision. The dispatcher must never retain peer credentials.
    secret_cleanup_args=(--remove-secrets BASTION_A2A_SHARED_SECRET)
  fi
  # Existing services keep one stable canonical origin across revisions. Reusing it in the
  # deployment avoids creating a transient placeholder revision that is unsafe to roll back to.
  if gcloud run services describe "$service" --project "$PROJECT_ID" --region "$REGION" >/dev/null 2>&1; then
    service_url="$(uri "$service")"
  fi
  gcloud run deploy "$service" --quiet \
    --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
    --service-account "$account" "${access_args[@]}" --ingress "$ingress" \
    --min-instances 0 --max-instances "$MAX_INSTANCES" --memory "$MEMORY_LIMIT" --timeout "$timeout" \
    --set-env-vars "BASTION_AGENT_DIR=$agent_dir,BASTION_SERVICE_URL=$service_url,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$MODEL_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=TRUE,VERTEX_AI_MODEL=${VERTEX_AI_MODEL:-gemini-3.5-flash},MODEL_ARMOR_TEMPLATE_ID=$MODEL_ARMOR_TEMPLATE_ID,MODEL_ARMOR_LOCATION=$MODEL_ARMOR_LOCATION,BASTION_SESSION_SERVICE_URI=$SESSION_URI,BASTION_MEMORY_SERVICE_URI=$MEMORY_URI,ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=false,OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT${extras}" \
    "${secret_args[@]}" \
    "${secret_cleanup_args[@]}" \
    --labels "app=bastion,agent=$agent_dir,classification=internal"
  # Publish the exact canonical origin as both the card URL and future ID-token audience.
  if [[ "$service_url" == "https://placeholder.invalid" ]]; then
    gcloud run services update "$service" --project "$PROJECT_ID" --region "$REGION" \
      --update-env-vars "BASTION_SERVICE_URL=$(uri "$service")" >/dev/null
  fi
}

deploy_findings_api() {
  # Cloud Run-to-Cloud Run traffic sent to the canonical HTTPS origin is not classified as
  # internal unless both services use a VPC path. Keep the endpoint network-reachable but
  # IAM-private: no allUsers binding, and only escalation-agent-sa receives run.invoker.
  gcloud run deploy bastion-findings-api --quiet \
    --image "$IMAGE" --project "$PROJECT_ID" --region "$REGION" \
    --service-account "$(sa findings-api-sa)" --no-allow-unauthenticated --ingress all \
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

deploy_agent bastion-orchestrator orchestrator "$(sa orchestrator-sa)" \
  ",GCP_PROJECT_NUMBER=$PROJECT_NUMBER,AGENT_RUNTIME_REGION=$RUNTIME_REGION,BASTION_RUNTIME_AGENT_ENGINE_ID=$RUNTIME_ENGINE_ID,BASTION_DURABLE_STORE_BACKEND=firestore,BASTION_INVESTIGATION_LEASE_SECONDS=660"

# Reconcile permissions left by the former direct-peer Cloud Run topology. The dispatcher can
# invoke only Agent Runtime; it has neither the peer origin secret nor direct worker invocation.
for peer in bastion-access-auditor bastion-escalation-agent; do
  gcloud run services remove-iam-policy-binding "$peer" --project "$PROJECT_ID" --region "$REGION" \
    --member="serviceAccount:$(sa orchestrator-sa)" --role=roles/run.invoker >/dev/null 2>&1 || true
done
gcloud secrets remove-iam-policy-binding "$A2A_SHARED_SECRET" --project "$PROJECT_ID" \
  --member="serviceAccount:$(sa orchestrator-sa)" --role=roles/secretmanager.secretAccessor \
  >/dev/null 2>&1 || true
for obsolete_role in roles/modelarmor.user roles/pubsub.publisher; do
  gcloud projects remove-iam-policy-binding "$PROJECT_ID" --project "$PROJECT_ID" \
    --member="serviceAccount:$(sa orchestrator-sa)" --role="$obsolete_role" \
    --condition=None >/dev/null 2>&1 || true
done

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

# Eventarc owns the transport subscription but does not attach a dead-letter policy. Discover
# that one labelled subscription, bound delivery to five attempts, and retain failures on a
# separate review subscription. This is idempotent and never consumes the dead letters.
if ! gcloud pubsub topics describe "$DEAD_LETTER_TOPIC" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud pubsub topics create "$DEAD_LETTER_TOPIC" --project "$PROJECT_ID" --quiet
fi
if ! gcloud pubsub subscriptions describe "$DEAD_LETTER_REVIEW_SUB" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud pubsub subscriptions create "$DEAD_LETTER_REVIEW_SUB" --project "$PROJECT_ID" \
    --topic "$DEAD_LETTER_TOPIC" --message-retention-duration=7d --expiration-period=never --quiet
fi
EVENTARC_SUB="$(gcloud pubsub subscriptions list --project "$PROJECT_ID" \
  --filter="topic:${TOPIC}" --format='value(name.basename())' --limit=1)"
if [[ -z "$EVENTARC_SUB" ]]; then
  echo "Eventarc transport subscription for ${TOPIC} was not created" >&2
  exit 65
fi
gcloud pubsub topics add-iam-policy-binding "$DEAD_LETTER_TOPIC" --project "$PROJECT_ID" \
  --member="serviceAccount:${PUBSUB_SERVICE_AGENT}" --role=roles/pubsub.publisher --quiet >/dev/null
gcloud pubsub subscriptions add-iam-policy-binding "$EVENTARC_SUB" --project "$PROJECT_ID" \
  --member="serviceAccount:${PUBSUB_SERVICE_AGENT}" --role=roles/pubsub.subscriber --quiet >/dev/null
gcloud pubsub subscriptions update "$EVENTARC_SUB" --project "$PROJECT_ID" \
  --ack-deadline=600 --dead-letter-topic "$DEAD_LETTER_TOPIC" \
  --max-delivery-attempts=5 --quiet >/dev/null

printf 'Deployed private fleet:\n  orchestrator: %s\n  auditor: %s\n  escalation: %s\n' \
  "$(uri bastion-orchestrator)" "$AUDITOR_URI" "$ESCALATION_URI"

python -m infrastructure.register_agents
python -m infrastructure.verify_fleet
