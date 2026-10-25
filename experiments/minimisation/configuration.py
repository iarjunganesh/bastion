"""Explicit experiment settings; never update gcloud or saved ADC configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG = Path(__file__).with_name("config.json")


def load_config(path: Path = CONFIG) -> dict[str, Any]:
    settings = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "project",
        "quota_project",
        "location",
        "model",
        "temperature",
        "max_output_tokens",
        "pilot_max_calls",
        "max_spend_sek",
        "model_generation_enabled",
    }
    if set(settings) != required:
        raise ValueError("Unknown or missing experiment setting")
    for key in ("project", "quota_project"):
        if settings[key] != "bastion-fleet-2026":
            raise ValueError(f"{key} must explicitly select bastion-fleet-2026")
    if settings["location"] != "global" or settings["model"] != "gemini-3.5-flash":
        raise ValueError("Model/location change requires method review")
    for key, upper in (("max_output_tokens", 8192), ("pilot_max_calls", 5), ("max_spend_sek", 200)):
        if type(settings[key]) is not int or not 0 < settings[key] <= upper:
            raise ValueError(f"Invalid {key}")
    if type(settings["temperature"]) not in (int, float) or not 0 <= settings["temperature"] <= 2:
        raise ValueError("Invalid temperature")
    if settings["model_generation_enabled"] is not False:
        raise ValueError("Model generation remains disabled; runner/authorization not complete")
    return settings


def explicit_credentials(auth_default: Any, settings: dict[str, Any]) -> Any:
    """For a future authorized SDK runner; inferred project is deliberately ignored."""
    credentials, _ = auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return credentials.with_quota_project(settings["quota_project"])


if __name__ == "__main__":
    print(json.dumps(load_config(), indent=2))
