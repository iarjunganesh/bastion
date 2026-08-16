"""Provision Bastion's retained audit route, metrics, alerts, and operations dashboard."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

PROJECT = os.environ["GCP_PROJECT_ID"]
LOCATION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
RETENTION_DAYS = int(os.environ.get("BASTION_AUDIT_RETENTION_DAYS", "365"))
BUCKET = "bastion-audit"
SINK = "bastion-audit"
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
ROOT = Path(__file__).resolve().parents[1]
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for observability provisioning")

METRICS = {
    "bastion_audit_failures": (
        'jsonPayload.event:* AND jsonPayload.outcome="failed"',
        "Failed correlated Bastion audit actions",
    ),
    "bastion_policy_refusals": (
        'jsonPayload.event:* AND jsonPayload.outcome="refused"',
        "Fail-closed Bastion policy refusals",
    ),
    "bastion_audit_records": (
        "jsonPayload.event:* AND jsonPayload.invocation_id:*",
        "Correlated payload-free Bastion audit records",
    ),
    "bastion_model_armor_refusals": (
        'jsonPayload.event:("model_armor.input" OR "model_armor.output") '
        'AND jsonPayload.outcome="refused"',
        "Model Armor and protected-data refusals",
    ),
}


def call(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(  # noqa: S603 - reviewed gcloud-only arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def ensure_audit_bucket() -> None:
    exists = call(
        "logging",
        "buckets",
        "describe",
        BUCKET,
        f"--location={LOCATION}",
        "--format=json",
        check=False,
    )
    if exists.returncode:
        call(
            "logging",
            "buckets",
            "create",
            BUCKET,
            f"--location={LOCATION}",
            f"--retention-days={RETENTION_DAYS}",
            "--enable-analytics",
            "--description=Bastion payload-free compliance audit records",
        )
    else:
        bucket = json.loads(exists.stdout)
        if int(bucket.get("retentionDays", 0)) != RETENTION_DAYS:
            call(
                "logging",
                "buckets",
                "update",
                BUCKET,
                f"--location={LOCATION}",
                f"--retention-days={RETENTION_DAYS}",
            )
        if not bucket.get("analyticsEnabled", False):
            # The API refuses an analytics upgrade combined with other field updates.
            call(
                "logging",
                "buckets",
                "update",
                BUCKET,
                f"--location={LOCATION}",
                "--enable-analytics",
            )
    destination = f"logging.googleapis.com/projects/{PROJECT}/locations/{LOCATION}/buckets/{BUCKET}"
    exists = call("logging", "sinks", "describe", SINK, check=False)
    operation = "update" if exists.returncode == 0 else "create"
    call(
        "logging",
        "sinks",
        operation,
        SINK,
        destination,
        "--log-filter=jsonPayload.event:* AND jsonPayload.invocation_id:*",
        "--description=Route correlated Bastion audit events to the regional retained bucket",
    )


def ensure_metrics() -> None:
    for name, (filter_expression, description) in METRICS.items():
        exists = call("logging", "metrics", "describe", name, check=False)
        operation = "update" if exists.returncode == 0 else "create"
        call(
            "logging",
            "metrics",
            operation,
            name,
            f"--log-filter={filter_expression}",
            f"--description={description}",
        )


def ensure_dashboard() -> None:
    dashboards = call("monitoring", "dashboards", "list", "--format=json").stdout
    records: list[dict[str, Any]] = json.loads(dashboards or "[]")
    if any(record.get("displayName") == "Bastion Fleet Operations" for record in records):
        return
    source = ROOT / "infrastructure" / "monitoring-dashboard.json"
    call("monitoring", "dashboards", "create", f"--config-from-file={source}")


def ensure_alerts() -> None:
    source_subscription = call(
        "pubsub",
        "subscriptions",
        "list",
        "--filter=topic:bastion-investigations",
        "--format=value(name.basename())",
        "--limit=1",
    ).stdout.strip()
    if not source_subscription:
        raise RuntimeError("Eventarc transport subscription is absent")
    specs = (
        (
            "Bastion audit action failures",
            "Any failed audited Cloud Run action",
            'metric.type="logging.googleapis.com/user/bastion_audit_failures" '
            'AND resource.type="cloud_run_revision"',
            "> 0",
            "0s",
            "A correlated action failed. Inspect the retained audit bucket by invocation_id.",
        ),
        (
            "Bastion refusal spike",
            "More than ten policy refusals",
            'metric.type="logging.googleapis.com/user/bastion_policy_refusals" '
            'AND resource.type="cloud_run_revision"',
            "> 10",
            "0s",
            "Investigate caller and reason trends; do not widen access automatically.",
        ),
        (
            "Bastion Model Armor failure or refusal",
            "Any Model Armor refusal",
            'metric.type="logging.googleapis.com/user/bastion_model_armor_refusals" '
            'AND resource.type="cloud_run_revision"',
            "> 0",
            "0s",
            "Bastion failed closed. Restore screening; never bypass Model Armor.",
        ),
        (
            "Bastion stuck investigation delivery",
            "Oldest Eventarc message exceeds ten minutes",
            'metric.type="pubsub.googleapis.com/subscription/oldest_unacked_message_age" '
            'AND resource.type="pubsub_subscription" '
            f'AND resource.label.subscription_id="{source_subscription}"',
            "> 600",
            "120s",
            "Inspect Eventarc delivery and the durable Firestore lease.",
        ),
        (
            "Bastion dead-letter backlog",
            "Any unresolved dead letter",
            'metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages" '
            'AND resource.type="pubsub_subscription" '
            'AND resource.label.subscription_id="bastion-dead-letter-review"',
            "> 0",
            "0s",
            "Review the failure before replaying its bounded dead letter.",
        ),
    )
    records = json.loads(call("monitoring", "policies", "list", "--format=json").stdout or "[]")
    existing = {record.get("displayName") for record in records}
    for (
        display_name,
        condition_name,
        filter_expression,
        comparison,
        duration,
        documentation,
    ) in specs:
        if display_name in existing:
            continue
        call(
            "monitoring",
            "policies",
            "create",
            f"--display-name={display_name}",
            f"--condition-display-name={condition_name}",
            f"--condition-filter={filter_expression}",
            f"--if={comparison}",
            f"--duration={duration}",
            "--trigger-count=1",
            "--combiner=OR",
            f"--documentation={documentation}",
            "--documentation-format=text/markdown",
        )


def main() -> None:
    if RETENTION_DAYS < 30:
        raise SystemExit("BASTION_AUDIT_RETENTION_DAYS must be at least 30")
    ensure_audit_bucket()
    ensure_metrics()
    ensure_alerts()
    ensure_dashboard()
    print(
        f"Verified regional audit bucket ({RETENTION_DAYS} days), four metrics, five alerts, "
        "and Bastion Fleet Operations dashboard."
    )


if __name__ == "__main__":
    main()
