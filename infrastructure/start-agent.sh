#!/usr/bin/env sh
set -eu

: "${BASTION_AGENT_DIR:?BASTION_AGENT_DIR must name a folder under /app/agents}"
: "${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT is required}"
: "${GOOGLE_CLOUD_LOCATION:?GOOGLE_CLOUD_LOCATION is required}"
: "${BASTION_SESSION_SERVICE_URI:?a durable ADK session service is required}"
: "${BASTION_MEMORY_SERVICE_URI:?a durable ADK memory service is required}"

case "$BASTION_AGENT_DIR" in
  orchestrator|access_auditor|escalation_agent) ;;
  *) echo "Invalid BASTION_AGENT_DIR: $BASTION_AGENT_DIR" >&2; exit 64 ;;
esac

exec adk api_server \
  --host=0.0.0.0 \
  --port="$PORT" \
  --a2a \
  --trace_to_cloud \
  --otel_to_cloud \
  --extra_plugins=observability.audit.AuditPlugin \
  --session_service_uri="$BASTION_SESSION_SERVICE_URI" \
  --memory_service_uri="$BASTION_MEMORY_SERVICE_URI" \
  "/app/agents/$BASTION_AGENT_DIR"
