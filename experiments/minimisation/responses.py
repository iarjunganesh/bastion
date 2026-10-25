"""Strict offline response parsing. No repairs, calls, or fabricated model responses."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from study import score, score_detection


class InvalidResponse(ValueError):
    """A bounded reason for rejecting untrusted output."""


def reject_constant(value: str) -> None:
    del value
    raise InvalidResponse("non_finite_json")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidResponse("duplicate_json_key")
        result[key] = value
    return result


def parse_response(text: str, task: str) -> dict[str, Any]:
    if not isinstance(text, str) or len(text.encode("utf-8")) > 262144:
        raise InvalidResponse("response_size_or_type")
    try:
        response = json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_object)
    except (json.JSONDecodeError, RecursionError) as error:
        raise InvalidResponse("invalid_json") from error
    if not isinstance(response, dict) or set(response) != {"count", "findings"}:
        raise InvalidResponse("report_fields")
    findings = response["findings"]
    if not isinstance(findings, list) or len(findings) > 400:
        raise InvalidResponse("findings_shape")
    if type(response["count"]) is not int or response["count"] != len(findings):
        raise InvalidResponse("count_mismatch")
    if task not in ("detect", "explain"):
        raise InvalidResponse("unknown_task")
    fields = {"reason", "risk_score", "rationale"} | (
        {"member", "role"} if task == "detect" else {"finding_id", "department"}
    )
    seen = set()
    for finding in findings:
        if not isinstance(finding, dict) or set(finding) != fields:
            raise InvalidResponse("finding_fields")
        for key in fields - {"risk_score"}:
            if not isinstance(finding[key], str) or not finding[key]:
                raise InvalidResponse("finding_string")
        risk = finding["risk_score"]
        if type(risk) not in (float, int) or not math.isfinite(risk) or not 0 <= risk <= 1:
            raise InvalidResponse("risk_score")
        if not 1 <= len(finding["rationale"]) <= 280:
            raise InvalidResponse("rationale_length")
        if finding["reason"] not in ("overly_broad_role", "missing_condition", "stale_identity"):
            raise InvalidResponse("reason_code")
        if task == "explain":
            if not re.fullmatch("[0-9a-f]{24}", finding["finding_id"]):
                raise InvalidResponse("finding_id")
            if len(finding["department"]) > 64:
                raise InvalidResponse("department_length")
            identity = finding["finding_id"]
        else:
            identity = (finding["member"], finding["role"])
        if identity in seen:
            raise InvalidResponse("duplicate_finding")
        seen.add(identity)
    return response


def evaluate(case: dict[str, Any], trial: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Preserve failed/refused/invalid trials; caller joins every planned trial separately."""
    identity = {key: trial[key] for key in ("case_id", "condition", "replicate")}
    if any(record.get(key) != value for key, value in identity.items()):
        raise InvalidResponse("trial_identity_mismatch")
    status = record.get("status")
    if status in ("error", "refusal"):
        return {**identity, "status": status, "valid_response": False}
    if status != "success":
        raise InvalidResponse("unknown_status")
    try:
        response = parse_response(record.get("text"), trial["task"])
    except InvalidResponse as error:
        return {**identity, "status": "invalid", "valid_response": False, "reason": str(error)}
    metrics = (
        score_detection(case, response) if trial["task"] == "detect" else score(case, response)
    )
    if trial["task"] == "detect":
        metrics["altered_rule_fields"] = sum(
            f["reason"] != "overly_broad_role" or f["risk_score"] != 0.8
            for f in response["findings"]
        )
    return {**identity, "status": "success", **metrics}
