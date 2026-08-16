"""Record what is actually deployed, so the architecture documentation cannot lie.

Bastion's architecture diagram showed Firestore, Cloud Run services, Pub/Sub topics and a
Model Armor template on a day when the project contained exactly one resource: the default
Compute Engine service account Google creates for you. Every other box was an intention
drawn as a fact. In a project whose entire pitch is that its claims are checkable, that is
the worst kind of documentation rot — the picture a judge looks at first, asserting a
system that does not exist.

So the status in the docs is derived from the project rather than typed by hand. Run this,
commit the JSON, and the diagram's legend is a measurement.

    python scripts/capture_gcp_state.py            # rewrite the state file
    python scripts/capture_gcp_state.py --check     # fail if it is stale (CI has no creds)

**This never writes a principal.** It records whether things exist and how many, never who
they are. `getIamPolicy` output and service-account emails are exactly what SECURITY.md
forbids committing, and a state file is no less committed than a policy dump.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "assets" / "architecture" / "gcp-state.json"

PROJECT = "bastion-fleet-2026"
REGION = "europe-north2"
CONTROL_REGION = "europe-west4"

# ADR-003's service surface. The key is the label used in the documentation; the value is
# the API that must be enabled for that row to count as "enabled".
SERVICES = {
    "Vertex AI": "aiplatform.googleapis.com",
    "Cloud Run": "run.googleapis.com",
    "Eventarc": "eventarc.googleapis.com",
    "Firestore": "firestore.googleapis.com",
    "Pub/Sub": "pubsub.googleapis.com",
    "Cloud Scheduler": "cloudscheduler.googleapis.com",
    "IAM Recommender": "recommender.googleapis.com",
    "Cloud Asset Inventory": "cloudasset.googleapis.com",
    "Cloud IAM": "iam.googleapis.com",
    "Model Armor": "modelarmor.googleapis.com",
    "Secret Manager": "secretmanager.googleapis.com",
    "Cloud Trace": "cloudtrace.googleapis.com",
    "Cloud Logging": "logging.googleapis.com",
    "Cloud Monitoring": "monitoring.googleapis.com",
    "BigQuery": "bigquery.googleapis.com",
    "Firebase Hosting": "firebasehosting.googleapis.com",
    "Cloud Build": "cloudbuild.googleapis.com",
    "Artifact Registry": "artifactregistry.googleapis.com",
    # The three GEAP surfaces enabled 2026-08-15. They are listed here rather than in a
    # separate block because the "N of N services enabled" line in the documentation is
    # meant to cover everything the architecture names, and these are named.
    "Agent Gateway": "networkservices.googleapis.com",
    "Agent Registry": "agentregistry.googleapis.com",
    "Agent Identity": "agentidentity.googleapis.com",
}

# Each probe answers "does anything exist here yet", and returns a COUNT, never a name.
# Naming a Cloud Run service is harmless; naming a service account is not, and keeping the
# rule uniform means nobody has to decide case by case.
PROBES: dict[str, list[str]] = {
    "cloud_run_services": ["run", "services", "list"],
    "firestore_databases": ["firestore", "databases", "list"],
    "pubsub_topics": ["pubsub", "topics", "list"],
    "scheduler_jobs": ["scheduler", "jobs", "list", f"--location={REGION}"],
    "secrets": ["secrets", "list"],
    "artifact_repositories": ["artifacts", "repositories", "list"],
    "agent_gateways": [
        "network-services",
        "agent-gateways",
        "list",
        f"--location={CONTROL_REGION}",
    ],
    "agent_registry_services": [
        "agent-registry",
        "services",
        "list",
        f"--location={CONTROL_REGION}",
    ],
}

# Service accounts Google creates for you, which are not evidence that anything was built.
# Counting them was a real defect: the two default accounts made `sum(resources)` read as 2,
# which is above the threshold at which check_docs.py stops rejecting committed architecture
# images — so the measurement designed to prevent a fictional diagram was one row away from
# permitting one. A resource count answers "what has Bastion deployed", so it counts what
# Bastion deployed.
GOOGLE_DEFAULT_SA = ("-compute@developer.gserviceaccount.com", "@appspot.gserviceaccount.com")

# Model Armor is probed over REST rather than through gcloud. `gcloud model-armor templates
# list` — and `gcloud alpha model-armor …` — return `PERMISSION_DENIED: Read access to project
# 'bastion-fleet-2026' was denied` for an account holding roles/owner, while the identical REST
# GET succeeds. Trusting the CLI here would report the one resource this project has actually
# deployed as absent, which is the same class of error as reporting one it has not.
MODEL_ARMOR_LOCATION = "europe-west4"
MODEL_ARMOR_ENDPOINT = (
    f"https://modelarmor.{MODEL_ARMOR_LOCATION}.rep.googleapis.com/v1"
    f"/projects/{PROJECT}/locations/{MODEL_ARMOR_LOCATION}/templates"
)
AGENT_ENGINE_LOCATION = "europe-west4"
AGENT_ENGINE_ENDPOINT = (
    f"https://{AGENT_ENGINE_LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
    f"/locations/{AGENT_ENGINE_LOCATION}/reasoningEngines"
)


def gcloud() -> str:
    found = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if found is None:
        print("gcloud is not on PATH — cannot capture live state.", file=sys.stderr)
        raise SystemExit(2)
    return found


def run(args: list[str], field: str = "name") -> list[str]:
    """Return non-empty output lines, or [] when the command fails or returns nothing.

    `field` matters more than it looks. `gcloud services list` puts the bare API id in
    `config.name` and a fully-qualified `projects/<number>/services/<api>` in `name`, so
    reading the wrong one silently reports every service as disabled — which is exactly
    the kind of confidently-wrong output this file exists to prevent.
    """
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [gcloud(), *args, f"--project={PROJECT}", f"--format=value({field})"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return []
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def enabled_apis() -> set[str]:
    return set(run(["services", "list", "--enabled"], field="config.name"))


def own_service_accounts() -> int:
    """Service accounts this project created, excluding the ones Google created for it.

    The emails are read and immediately discarded. Only the count leaves this function,
    because the state file is committed and a service-account email is a principal.
    """
    emails = run(["iam", "service-accounts", "list"], field="email")
    return sum(1 for email in emails if not email.endswith(GOOGLE_DEFAULT_SA))


def model_armor_templates() -> int:
    """Count Model Armor templates over REST — see MODEL_ARMOR_ENDPOINT for why not gcloud."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [gcloud(), "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 0
    token = completed.stdout.strip()
    if completed.returncode != 0 or not token:
        return 0
    request = urllib.request.Request(  # noqa: S310 - fixed https endpoint, not user input
        MODEL_ARMOR_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return 0
    return len(payload.get("templates", []))


def agent_engines() -> int:
    """Count durable Agent Engine instances without writing their resource IDs to Git."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [gcloud(), "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 0
    token = completed.stdout.strip()
    if completed.returncode != 0 or not token:
        return 0
    request = urllib.request.Request(  # noqa: S310 - fixed Google API endpoint
        AGENT_ENGINE_ENDPOINT, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return 0
    return len(payload.get("reasoningEngines", []))


def capture() -> dict[str, Any]:
    apis = enabled_apis()
    return {
        "_comment": "Generated by scripts/capture_gcp_state.py. Never hand-edit.",
        "_warning": "Contains counts only. Never add principals, emails, or policy bindings.",
        "captured_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project": PROJECT,
        "region": REGION,
        "services": {
            label: {"api": api, "enabled": api in apis} for label, api in SERVICES.items()
        },
        "resources": {
            **{name: len(run(args)) for name, args in PROBES.items()},
            "model_armor_templates": model_armor_templates(),
            "agent_engines": agent_engines(),
            "service_accounts_created": own_service_accounts(),
        },
    }


def load() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    loaded: dict[str, Any] = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return loaded


def comparable(state: dict[str, Any]) -> dict[str, Any]:
    """Everything except the timestamp, which moves on every run by design."""
    return {key: value for key, value in state.items() if key != "captured_utc"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare against the committed file instead of rewriting it",
    )
    arguments = parser.parse_args()

    if arguments.check:
        committed = load()
        if not committed:
            print(f"{STATE_FILE.name} is missing — run this script without --check.")
            return 1
        if comparable(capture()) != comparable(committed):
            print(f"{STATE_FILE.name} disagrees with the live project — re-run and commit.")
            return 1
        print(f"{STATE_FILE.name} matches the live project.")
        return 0

    state = capture()
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    live = sum(state["resources"].values())
    on = sum(1 for entry in state["services"].values() if entry["enabled"])
    print(f"wrote {STATE_FILE.relative_to(ROOT).as_posix()}")
    print(f"  {on}/{len(SERVICES)} services enabled, {live} resource(s) actually deployed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
