"""Cloud Run ingress is a service-level, not revision-level, security control."""

from __future__ import annotations

import os

os.environ.setdefault("GCP_PROJECT_ID", "bastion-test-project")
os.environ.setdefault("GCP_REGION", "europe-north2")

from infrastructure import verify_fleet


def test_verifier_reads_ingress_from_service_metadata(monkeypatch):
    record = {
        "metadata": {
            "annotations": {"run.googleapis.com/ingress": "internal"},
            "labels": {"classification": "internal"},
        },
        "spec": {
            "template": {"spec": {"serviceAccountName": "fleet@example.iam.gserviceaccount.com"}}
        },
    }
    monkeypatch.setattr(verify_fleet, "describe", lambda service: record)
    monkeypatch.setattr(
        verify_fleet.subprocess,
        "run",
        lambda *args, **kwargs: type(
            "R", (), {"returncode": 0, "stdout": "/apps/orchestrator/trigger/eventarc\n"}
        )(),
    )
    verify_fleet.main()
