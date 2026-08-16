"""Agent Gateway configuration is declarative and fail-closed."""

from __future__ import annotations

from infrastructure import provision_gateway


def test_gateway_is_regional_managed_egress_bound_to_registry():
    config = provision_gateway.desired_config()
    assert config["googleManaged"] == {"governedAccessPath": "AGENT_TO_ANYWHERE"}
    assert config["protocols"] == ["MCP"]
    # The module captures GCP_PROJECT_ID at import, and conftest sets it with `setdefault`
    # so an operator shell or CI's own value legitimately wins. Pinning the project literal
    # here would assert the ambient environment rather than the URI this module builds — so
    # the project floats and the shape does not: host, segment order, and no trailing slash.
    assert config["registries"] == [
        f"//agentregistry.googleapis.com/projects/{provision_gateway.PROJECT}"
        "/locations/europe-west4"
    ]


def test_gateway_verifier_rejects_absence_and_wrong_binding():
    assert provision_gateway.validate(None) == ["Agent Gateway is absent"]
    errors = provision_gateway.validate(
        {
            "googleManaged": {"governedAccessPath": "CLIENT_TO_AGENT"},
            "protocols": [],
            "registries": [],
            "labels": {},
        },
        {
            "service": "iap.googleapis.com",
            "failOpen": True,
            "metadata": {"iamEnforcementMode": "DRY_RUN"},
        },
        {"target": {"resources": []}},
    )
    assert "Gateway is not Agent-to-Anywhere" in errors
    assert "Gateway is not bound to Bastion's regional Agent Registry" in errors
    assert "Gateway authorization extension is fail-open" in errors
    assert "Gateway IAP enforcement remains in dry-run mode" in errors


def test_iap_extension_is_enforced_and_fail_closed():
    extension = provision_gateway.desired_auth_extension()
    assert extension["failOpen"] is False
    assert "iamEnforcementMode" not in extension["metadata"]
    policy = provision_gateway.desired_auth_policy()
    assert policy["action"] == "CUSTOM"
    assert policy["target"]["resources"] == [
        f"projects/{provision_gateway.PROJECT}/locations/europe-west4/agentGateways/bastion-egress"
    ]
