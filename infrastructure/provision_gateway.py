"""Provision and verify Bastion's Google-managed Agent Gateway.

Agent Gateway's current resource schema requires ``MCP`` in ``protocols`` even though the
managed proxy passes through all HTTP traffic, including A2A. Only MCP bodies receive
attribute-level parsing; A2A remains an authenticated HTTP pass-through governed by endpoint
registration and IAM. This distinction is intentionally encoded here rather than hidden in a
console-only deployment.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, cast

PROJECT = os.environ["GCP_PROJECT_ID"]
REGION = os.environ.get("AGENT_RUNTIME_REGION", "europe-west4")
GATEWAY = os.environ.get("BASTION_AGENT_GATEWAY", "bastion-egress")
AUTH_EXTENSION = os.environ.get("BASTION_IAP_AUTH_EXTENSION", "bastion-iap-enforcement")
AUTH_POLICY = os.environ.get("BASTION_GATEWAY_AUTH_POLICY", "bastion-gateway-iap")
GCLOUD = shutil.which("gcloud") or shutil.which("gcloud.cmd") or ""
if not GCLOUD:
    raise RuntimeError("gcloud must be installed for Agent Gateway provisioning")

REQUIRED_APIS = (
    "agentregistry.googleapis.com",
    "iap.googleapis.com",
    "networksecurity.googleapis.com",
    "networkservices.googleapis.com",
)


def registry_uri() -> str:
    # The API validator rejects a trailing slash even though an older generated schema
    # description displayed one. Keep the canonical resource prefix exact.
    return f"//agentregistry.googleapis.com/projects/{PROJECT}/locations/{REGION}"


def desired_config() -> dict[str, Any]:
    return {
        "description": "Bastion governed egress for registered institutional agents.",
        "googleManaged": {"governedAccessPath": "AGENT_TO_ANYWHERE"},
        "labels": {
            "app": "bastion",
            "classification": "internal",
            "policy": "bastion-v1",
        },
        # Required by the current API schema. The proxy still passes A2A HTTP traffic;
        # only MCP receives request-body attribute extraction.
        "protocols": ["MCP"],
        "registries": [registry_uri()],
    }


def desired_auth_extension() -> dict[str, Any]:
    """IAP enforcement configuration: no dry-run marker and never fail open."""
    return {
        "name": AUTH_EXTENSION,
        "service": "iap.googleapis.com",
        "failOpen": False,
        "timeout": "1s",
        "metadata": {"iapPolicyVersion": "V1"},
    }


def desired_auth_policy() -> dict[str, Any]:
    return {
        "name": AUTH_POLICY,
        "target": {"resources": [f"projects/{PROJECT}/locations/{REGION}/agentGateways/{GATEWAY}"]},
        "policyProfile": "REQUEST_AUTHZ",
        "action": "CUSTOM",
        "customProvider": {
            "authzExtension": {
                "resources": [
                    f"projects/{PROJECT}/locations/{REGION}/authzExtensions/{AUTH_EXTENSION}"
                ]
            }
        },
    }


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - repository-owned gcloud arguments
        [GCLOUD, *args, "--project", PROJECT, "--quiet"],
        check=check,
        text=True,
        capture_output=True,
    )


def ensure_required_apis() -> None:
    for service in REQUIRED_APIS:
        result = run(
            "services",
            "list",
            "--enabled",
            f"--filter=config.name={service}",
            "--format=value(config.name)",
            check=False,
        )
        if result.returncode or result.stdout.strip() != service:
            run("services", "enable", service)


def describe() -> dict[str, Any] | None:
    result = run(
        "network-services",
        "agent-gateways",
        "describe",
        GATEWAY,
        f"--location={REGION}",
        "--format=json",
        check=False,
    )
    if result.returncode:
        return None
    return cast(dict[str, Any], json.loads(result.stdout))


def describe_auth_extension() -> dict[str, Any] | None:
    result = run(
        "beta",
        "service-extensions",
        "authz-extensions",
        "describe",
        AUTH_EXTENSION,
        f"--location={REGION}",
        "--format=json",
        check=False,
    )
    return None if result.returncode else cast(dict[str, Any], json.loads(result.stdout))


def describe_auth_policy() -> dict[str, Any] | None:
    result = run(
        "network-security",
        "authz-policies",
        "describe",
        AUTH_POLICY,
        f"--location={REGION}",
        "--format=json",
        check=False,
    )
    return None if result.returncode else cast(dict[str, Any], json.loads(result.stdout))


def validate(
    record: dict[str, Any] | None,
    extension: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> list[str]:
    if record is None:
        return ["Agent Gateway is absent"]
    errors: list[str] = []
    desired = desired_config()
    if record.get("googleManaged", {}).get("governedAccessPath") != "AGENT_TO_ANYWHERE":
        errors.append("Gateway is not Agent-to-Anywhere")
    if "MCP" not in record.get("protocols", []):
        errors.append("Gateway lacks the required MCP protocol declaration")
    if registry_uri() not in record.get("registries", []):
        errors.append("Gateway is not bound to Bastion's regional Agent Registry")
    for key, value in desired["labels"].items():
        if record.get("labels", {}).get(key) != value:
            errors.append(f"Gateway label {key} is missing or incorrect")
    if extension is None:
        errors.append("Gateway IAP authorization extension is absent")
    else:
        metadata = extension.get("metadata", {})
        if extension.get("service") != "iap.googleapis.com":
            errors.append("Gateway authorization extension does not delegate to IAP")
        # Protobuf JSON omits a false boolean, so absence is the enforced fail-closed default.
        if extension.get("failOpen", False) is not False:
            errors.append("Gateway authorization extension is fail-open")
        if metadata.get("iamEnforcementMode") == "DRY_RUN":
            errors.append("Gateway IAP enforcement remains in dry-run mode")
    if policy is None:
        errors.append("Gateway request authorization policy is absent")
    else:
        targets = policy.get("target", {}).get("resources", [])
        expected_suffix = f"/locations/{REGION}/agentGateways/{GATEWAY}"
        # Network Security canonicalizes the project ID to its numeric project number.
        if not any(str(target).endswith(expected_suffix) for target in targets):
            errors.append("Gateway authorization policy targets the wrong resource")
    return errors


def apply() -> None:
    ensure_required_apis()
    with tempfile.TemporaryDirectory(prefix="bastion-gateway-") as directory:
        source = Path(directory) / "gateway.json"
        source.write_text(json.dumps(desired_config(), indent=2), encoding="utf-8")
        result = run(
            "network-services",
            "agent-gateways",
            "import",
            GATEWAY,
            f"--location={REGION}",
            f"--source={source}",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())

        extension_source = Path(directory) / "iap-extension.json"
        extension_source.write_text(
            json.dumps(desired_auth_extension(), indent=2), encoding="utf-8"
        )
        result = run(
            "beta",
            "service-extensions",
            "authz-extensions",
            "import",
            AUTH_EXTENSION,
            f"--location={REGION}",
            f"--source={extension_source}",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())

        policy_source = Path(directory) / "iap-policy.json"
        policy_source.write_text(json.dumps(desired_auth_policy(), indent=2), encoding="utf-8")
        result = run(
            "network-security",
            "authz-policies",
            "import",
            AUTH_POLICY,
            f"--location={REGION}",
            f"--source={policy_source}",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="create or update the gateway")
    args = parser.parse_args()
    if args.apply:
        apply()
    errors = validate(describe(), describe_auth_extension(), describe_auth_policy())
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Verified Agent Gateway {GATEWAY} in {REGION}.")


if __name__ == "__main__":
    main()
