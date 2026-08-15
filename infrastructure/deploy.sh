#!/usr/bin/env bash
# Build one reviewed image context, deploy each agent privately, then connect private A2A peers.
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID}"
REGION="${GCP_REGION:?set GCP_REGION explicitly}"
MODEL_LOCATION="${GOOGLE_CLOUD_LOCATION:?set GOOGLE_CLOUD_LOCATION=global for Gemini}"
MODEL_ARMOR_TEMPLATE_ID="${MODEL_ARMOR_TEMPLATE_ID:?set MODEL_ARMOR_TEMPLATE_ID}"
MODEL_ARMOR_LOCATION="${MODEL_ARMOR_LOCATION:?set MODEL_ARMOR_LOCATION}"
MAX_INSTANCES="${BASTION_MAX_INSTANCES:-3}"
SESSION_URI="${BASTION_SESSION_SERVICE_URI:?set a managed non-memory ADK session service URI}"
MEMORY_URI="${BASTION_MEMORY_SERVICE_URI:?set a managed non-memory ADK memory service URI}"

if [[ "$SESSION_URI" == "memory://" || "$MEMORY_URI" == "memory://" ]]; then
  echo "Refusing ephemeral memory:// services: cross-week context must be durable." >&2
  exit 64
fi

sa() { echo "$1@${PROJECT_ID}.iam.gserviceaccount.com"; }
uri() { gcloud run services describe "$1" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)'; }

deploy_agent() {
  local service=$1 agent_dir=$2 account=$3 extras=${4:-}
  gcloud run deploy "$service" \
    --source . --project "$PROJECT_ID" --region "$REGION" \
    --service-account "$account" --no-allow-unauthenticated --ingress internal \
    --min-instances 0 --max-instances "$MAX_INSTANCES" \
    --set-env-vars "BASTION_AGENT_DIR=$agent_dir,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$MODEL_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=TRUE,VERTEX_AI_MODEL=${VERTEX_AI_MODEL:-gemini-3.5-flash},MODEL_ARMOR_TEMPLATE_ID=$MODEL_ARMOR_TEMPLATE_ID,MODEL_ARMOR_LOCATION=$MODEL_ARMOR_LOCATION,BASTION_SESSION_SERVICE_URI=$SESSION_URI,BASTION_MEMORY_SERVICE_URI=$MEMORY_URI${extras}" \
    --labels "app=bastion,agent=$agent_dir,classification=internal"
}

# Peers first: their URIs are inputs to the Orchestrator, never manually copied into .env.
deploy_agent bastion-access-auditor access_auditor "$(sa access-auditor-sa)"
deploy_agent bastion-escalation-agent escalation_agent "$(sa escalation-agent-sa)"

AUDITOR_URI="$(uri bastion-access-auditor)"
ESCALATION_URI="$(uri bastion-escalation-agent)"

# Only the orchestrator's workload identity may invoke either peer.
for service in bastion-access-auditor bastion-escalation-agent; do
  gcloud run services add-iam-policy-binding "$service" --project "$PROJECT_ID" --region "$REGION" \
    --member="serviceAccount:$(sa orchestrator-sa)" --role=roles/run.invoker
done

deploy_agent bastion-orchestrator orchestrator "$(sa orchestrator-sa)" \
  ",BASTION_AUDITOR_CARD_URL=$AUDITOR_URI,BASTION_ESCALATION_CARD_URL=$ESCALATION_URI"

printf 'Deployed private fleet:\n  orchestrator: %s\n  auditor: %s\n  escalation: %s\n' \
  "$(uri bastion-orchestrator)" "$AUDITOR_URI" "$ESCALATION_URI"

python -m infrastructure.register_agents
python -m infrastructure.verify_fleet
