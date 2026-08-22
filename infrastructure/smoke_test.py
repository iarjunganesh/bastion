"""Production smoke test for governed Runtime, async delivery, and the private findings inbox."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import time
from hashlib import sha256
from uuid import uuid4

import google.cloud.pubsub_v1 as pubsub_v1
import httpx
from agentplatform import Client
from google.cloud import firestore

from infrastructure.verify_fleet import main as verify_fleet
from observability.audit import INVESTIGATION_METADATA_KEY
from runtime.events import new_investigation_payload

PROJECT = os.environ["GCP_PROJECT_ID"]
PROJECT_NUMBER = os.environ["GCP_PROJECT_NUMBER"]
RUN_REGION = os.environ.get("GCP_REGION", "europe-north2")
RUNTIME_REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
RUNTIME_ID = os.environ["BASTION_RUNTIME_AGENT_ENGINE_ID"]
TOPIC = os.environ.get("PUBSUB_TOPIC", "bastion-investigations")
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for the production smoke test")


def gcloud(*args: str) -> str:
    result = subprocess.run(  # noqa: S603 - reviewed gcloud-only arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def origin(service: str) -> str:
    value = gcloud(
        "run",
        "services",
        "describe",
        service,
        f"--region={RUN_REGION}",
        "--format=value(status.url)",
    )
    if not value.startswith("https://"):
        raise RuntimeError(f"Cloud Run returned no origin for {service}")
    return value


def verify_findings_boundary() -> None:
    target = f"{origin('bastion-findings-api')}/v1/escalations"
    denied = httpx.post(target, json={}, timeout=30)
    if denied.status_code not in {401, 403}:
        raise RuntimeError(f"unauthenticated findings request returned {denied.status_code}")
    service_account = f"escalation-agent-sa@{PROJECT}.iam.gserviceaccount.com"
    token = gcloud(
        "auth",
        "print-identity-token",
        f"--impersonate-service-account={service_account}",
        f"--audiences={target.rsplit('/v1/', 1)[0]}",
    )
    investigation_id = str(uuid4())
    key = sha256(f"{investigation_id}:security-engineering".encode()).hexdigest()
    payload = {
        "source": "bastion",
        "investigation_id": investigation_id,
        "department": "security-engineering",
        "finding_count": 1,
        # A smoke-shaped opaque id: the exact 24-hex shape the Auditor emits, so the receiver's
        # validation is exercised without deriving a real finding from the live policy.
        "finding_ids": [sha256(investigation_id.encode()).hexdigest()[:24]],
        "risk_categories": ["overly_broad_role"],
        "summary": "Access-review findings require attention: overly_broad_role",
    }
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": key}
    first = httpx.post(target, headers=headers, json=payload, timeout=30)
    second = httpx.post(target, headers=headers, json=payload, timeout=30)
    if first.status_code != 202 or first.json().get("accepted") is not True:
        raise RuntimeError("approved findings identity could not create a review record")
    if second.status_code != 202 or second.json().get("accepted") is not False:
        raise RuntimeError("findings endpoint did not collapse an idempotent duplicate")


def verify_async_event(timeout_seconds: int) -> None:
    payload = new_investigation_payload()
    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(PROJECT, TOPIC)
    publisher.publish(topic, json.dumps(payload, sort_keys=True).encode()).result(timeout=30)
    document = (
        firestore.Client(project=PROJECT)
        .collection("bastion_investigations")
        .document(str(payload["event_id"]))
    )
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        snapshot = document.get()
        status = snapshot.get("status") if snapshot.exists else None
        if status == "completed":
            return
        time.sleep(10)
    raise RuntimeError("asynchronous investigation did not complete before the smoke deadline")


async def verify_runtime() -> None:
    """Exercise the Runtime exactly as production dispatch does.

    This sent an imperative sentence — "Perform a read-only governed IAM review..." — which is
    the shape the dispatcher stopped sending, because Model Armor scores an instruction addressed
    to an agent at the same confidence as a real injection and screening fails closed
    ([ADR-009](../docs/adr/009-model-armor-threshold.md)). A smoke test that sends what production
    is forbidden to send is not smoking production; it exercises a path no deployment uses, and
    its failure says nothing about whether the fleet works.

    The correlation id is a fresh UUID rather than a durable event id because no Firestore record
    backs this probe. It travels as run-config metadata for the same reason it does in dispatch:
    the audit trail must be able to name this run without a model reading the id.
    """
    name = f"projects/{PROJECT_NUMBER}/locations/{RUNTIME_REGION}/reasoningEngines/{RUNTIME_ID}"
    # The client must outlive the engine handle. `Client(...).agent_engines.get(...)` leaves the
    # client unreferenced, so it can be collected mid-stream; its aiohttp session closes with it
    # and the next request trips `assert self._connector is not None` deep inside aiohttp — an
    # error that names nothing about ownership and reads like a fleet fault. `agent_server` learned
    # this already, which is what `test_managed_runtime_keeps_client_for_async_session_and_stream`
    # pins; the smoke path simply never had the lesson applied to it.
    client = Client(project=PROJECT, location=RUNTIME_REGION)
    engine = client.agent_engines.get(name=name)
    user = f"bastion-smoke-{uuid4()}"
    investigation_id = str(uuid4())
    session = await engine.async_create_session(user_id=user)
    count = 0
    async for _event in engine.async_stream_query(
        user_id=user,
        session_id=session["id"],
        message=json.dumps(
            {"task": "scheduled_iam_access_review", "investigation_id": investigation_id},
            sort_keys=True,
        ),
        run_config={"custom_metadata": {INVESTIGATION_METADATA_KEY: investigation_id}},
    ):
        count += 1
    if count == 0:
        raise RuntimeError("managed Agent Runtime returned no streamed events")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-timeout", type=int, default=900)
    parser.add_argument("--skip-async-event", action="store_true")
    args = parser.parse_args()
    verify_fleet()
    verify_findings_boundary()
    if not args.skip_async_event:
        verify_async_event(args.event_timeout)
    asyncio.run(verify_runtime())
    print("Production smoke passed: fleet, findings IAM/idempotency, async state, and Runtime.")


if __name__ == "__main__":
    main()
