"""Malformed output and wrong-project controls."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import configuration
import responses
import study


class ResponseTests(unittest.TestCase):
    def test_rejects_bad_json_and_unexpected_fields(self) -> None:
        for text in (
            '{"count":0,"count":0,"findings":[]}',
            '{"count":NaN,"findings":[]}',
            '```json\n{"count":0,"findings":[]}\n```',
            '{"count":true,"findings":[]}',
            '{"count":0,"findings":[],"extra":"x"}',
            "[]",
        ):
            with self.subTest(text=text), self.assertRaises(responses.InvalidResponse):
                responses.parse_response(text, "explain")

    def test_valid_empty_is_distinct_from_missing_refused_or_invalid(self) -> None:
        case = study.generate(count=1)[0]
        trial = study.requests(case, 0)[2]
        identity = {k: trial[k] for k in ("case_id", "condition", "replicate")}
        valid = responses.evaluate(
            case, trial, dict(identity, status="success", text='{"count":0,"findings":[]}')
        )
        self.assertTrue(valid["structural_fidelity"])
        for status in ("error", "refusal", "success"):
            result = responses.evaluate(case, trial, dict(identity, status=status, text=""))
            self.assertFalse(result["valid_response"])
        with self.assertRaises(responses.InvalidResponse):
            responses.evaluate(case, trial, dict(identity, case_id="wrong", status="success"))

    def test_rejects_invalid_scores_ids_and_duplicates(self) -> None:
        case = study.generate(count=2)[1]
        base = study.template(case["findings"])
        self.assertEqual(responses.parse_response(json.dumps(base), "explain"), base)
        for key, value in (
            ("risk_score", True),
            ("risk_score", float("inf")),
            ("finding_id", "bad"),
            ("rationale", "x" * 281),
        ):
            changed = copy.deepcopy(base)
            changed["findings"][0][key] = value
            with self.assertRaises(responses.InvalidResponse):
                responses.parse_response(json.dumps(changed), "explain")
        base["findings"].append(base["findings"][0])
        base["count"] += 1
        with self.assertRaises(responses.InvalidResponse):
            responses.parse_response(json.dumps(base), "explain")

    def test_project_override_does_not_use_inferred_project(self) -> None:
        settings = configuration.load_config()
        credentials = Mock()
        loader = Mock(return_value=(credentials, "jnanasagara"))
        returned = configuration.explicit_credentials(loader, settings)
        credentials.with_quota_project.assert_called_once_with("bastion-fleet-2026")
        self.assertIs(returned, credentials.with_quota_project.return_value)
        for key, value in (
            ("project", "jnanasagara"),
            ("quota_project", "jnanasagara"),
            ("model_generation_enabled", True),
            ("max_spend_sek", 201),
        ):
            changed = dict(settings, **{key: value})
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    configuration.load_config(path)
