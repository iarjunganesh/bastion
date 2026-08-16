"""Cloud Run ingress is a service-level, not revision-level, security control."""

from __future__ import annotations

import os

os.environ.setdefault("GCP_PROJECT_ID", "bastion-test-project")
os.environ.setdefault("GCP_REGION", "europe-north2")

from infrastructure import verify_fleet


def test_verifier_reads_ingress_from_service_metadata(monkeypatch):
    def describe(service):
        peer = service in verify_fleet.PEERS
        environment = (
            [{"name": "BASTION_A2A_SHARED_SECRET", "valueFrom": {"secretKeyRef": {"name": "x"}}}]
            if peer
            else (
                [{"name": "BASTION_RUNTIME_AGENT_ENGINE_ID", "value": "runtime-1"}]
                if service == "bastion-orchestrator"
                else []
            )
        )
        return {
            "metadata": {
                "annotations": {"run.googleapis.com/ingress": verify_fleet.SERVICES[service]},
                "labels": {"classification": "internal"},
            },
            "spec": {
                "template": {
                    "spec": {
                        "serviceAccountName": "fleet@example.iam.gserviceaccount.com",
                        "containers": [{"env": environment}],
                    }
                }
            },
        }

    def run(command, **kwargs):
        joined = " ".join(command)
        if "eventarc triggers describe" in joined:
            stdout = "/apps/orchestrator/trigger/eventarc\n"
        elif "pubsub subscriptions list" in joined:
            stdout = '[{"ackDeadlineSeconds":600,"deadLetterPolicy":{"maxDeliveryAttempts":5}}]'
        else:
            stdout = "\n".join(sorted(verify_fleet.REQUIRED_REGISTRY_SERVICES))
        return type("R", (), {"returncode": 0, "stdout": stdout})()

    monkeypatch.setattr(verify_fleet, "describe", describe)
    monkeypatch.setattr(verify_fleet.subprocess, "run", run)
    monkeypatch.setattr(verify_fleet.provision_gateway, "describe", lambda: {})
    monkeypatch.setattr(verify_fleet.provision_gateway, "describe_auth_extension", lambda: {})
    monkeypatch.setattr(verify_fleet.provision_gateway, "describe_auth_policy", lambda: {})
    monkeypatch.setattr(verify_fleet.provision_gateway, "validate", lambda *args: [])
    verify_fleet.main()
