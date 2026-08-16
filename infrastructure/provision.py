"""Idempotently provision Bastion's minimum production control plane.

The script makes each external mutation explicit and queryable.  It never grants Owner/Editor,
never creates a public agent endpoint, and refuses to deploy without the pre-existing Model
Armor template required for fail-closed model screening.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from collections.abc import Sequence

from identity.policy import IDENTITIES, validate_identities

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ.get("GCP_REGION", "europe-north2")
DATABASE = os.environ.get("FIRESTORE_DATABASE", "(default)")
TOPIC = os.environ.get("PUBSUB_TOPIC", "bastion-investigations")
MODEL_ARMOR_LOCATION = os.environ.get("MODEL_ARMOR_LOCATION", "europe-west4")
MODEL_ARMOR_TEMPLATE = os.environ.get("MODEL_ARMOR_TEMPLATE_ID", "bastion-guardrail")
GCLOUD: str = shutil.which("gcloud") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for provisioning")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - repository-owned gcloud arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=check,
        text=True,
        capture_output=True,
    )


def exists(args: Sequence[str]) -> bool:
    result = run(*args, check=False)
    return result.returncode == 0


def model_armor_template_accessible() -> bool:
    """Check the regional REST endpoint, not gcloud's unreliable Model Armor command.

    The Cloud SDK command can return ``PERMISSION_DENIED`` even for a project Owner holding the
    documented Viewer and User roles. The direct regional endpoint is the same control-plane API
    used by the Python client and is the path the runtime actually relies on.
    """
    token = subprocess.run(  # noqa: S603 - fixed gcloud executable and arguments
        [GCLOUD, "auth", "print-access-token"],
        check=False,
        text=True,
        capture_output=True,
    )
    if token.returncode != 0 or not token.stdout.strip():
        return False
    uri = (
        f"https://modelarmor.{MODEL_ARMOR_LOCATION}.rep.googleapis.com/v1/projects/{PROJECT}"
        f"/locations/{MODEL_ARMOR_LOCATION}/templates/{MODEL_ARMOR_TEMPLATE}"
    )
    request = urllib.request.Request(  # noqa: S310 - fixed regional Google API endpoint
        uri, headers={"Authorization": f"Bearer {token.stdout.strip()}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30):  # noqa: S310 - fixed URI above
            return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return False


def ensure_api(service: str) -> None:
    if not exists(
        (
            "services",
            "list",
            "--enabled",
            f"--filter=config.name={service}",
            "--format=value(config.name)",
        )
    ):
        run("services", "enable", service)


def ensure_service_account(name: str) -> str:
    email = f"{name}@{PROJECT}.iam.gserviceaccount.com"
    if not exists(("iam", "service-accounts", "describe", email)):
        run("iam", "service-accounts", "create", name, f"--display-name=Bastion {name}")
    return email


def ensure_project_role(member: str, role: str) -> None:
    # Membership and role must occur in the same flattened binding. Searching the complete
    # policy for each string independently falsely reports a grant when another identity has
    # the role and this identity merely appears elsewhere in the policy.
    granted = run(
        "projects",
        "get-iam-policy",
        PROJECT,
        "--flatten=bindings[].members",
        f"--filter=bindings.role={role} AND bindings.members={member}",
        "--format=value(bindings.role)",
    ).stdout.strip()
    if granted != role:
        run("projects", "add-iam-policy-binding", PROJECT, f"--member={member}", f"--role={role}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply", action="store_true", help="perform mutations; otherwise validate prerequisites"
    )
    args = parser.parse_args()
    validate_identities()
    print(f"Bastion project={PROJECT} region={REGION} firestore={DATABASE}")
    required = (
        "aiplatform.googleapis.com",
        "asset.googleapis.com",
        "firestore.googleapis.com",
        "pubsub.googleapis.com",
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "eventarc.googleapis.com",
        "artifactregistry.googleapis.com",
        "secretmanager.googleapis.com",
        "modelarmor.googleapis.com",
        "agentregistry.googleapis.com",
        "agentidentity.googleapis.com",
        "iap.googleapis.com",
        "networkservices.googleapis.com",
        "networksecurity.googleapis.com",
    )
    if not args.apply:
        missing = [
            service
            for service in required
            if not exists(
                (
                    "services",
                    "list",
                    "--enabled",
                    f"--filter=config.name={service}",
                    "--format=value(config.name)",
                )
            )
        ]
        if missing:
            raise SystemExit(f"Required APIs are disabled: {', '.join(missing)}")
        if not model_armor_template_accessible():
            raise SystemExit(
                "Model Armor template is absent or caller lacks access; provisioner requires "
                "modelarmor.templates.get"
            )
        print(
            "Prerequisites validated. Re-run with --apply to provision durable state and "
            "identities."
        )
        return

    for service in required:
        ensure_api(service)
    if not exists(("firestore", "databases", "describe", f"--database={DATABASE}")):
        run("firestore", "databases", "create", f"--database={DATABASE}", f"--location={REGION}")
    if not exists(("pubsub", "topics", "describe", TOPIC)):
        run("pubsub", "topics", "create", TOPIC)
    if not model_armor_template_accessible():
        raise SystemExit(
            "Model Armor template must be created by an approved Model Armor administrator "
            "before deployment"
        )

    for identity in IDENTITIES:
        email = ensure_service_account(identity.name)
        for role in sorted(identity.roles):
            ensure_project_role(f"serviceAccount:{email}", role)
    print("Provisioned Firestore, Pub/Sub, and least-privilege service accounts.")


if __name__ == "__main__":
    main()
