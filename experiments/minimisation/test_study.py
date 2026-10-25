"""Offline controls verify boundary/scoring errors without fabricating model results."""

import copy
import importlib
import os
import socket
import sys
import unittest
from unittest.mock import patch

import study


class OfflineStudyTests(unittest.TestCase):
    def test_reproducible_scoped_labels_without_network(self) -> None:
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            cases = study.generate()
            self.assertEqual(cases, study.generate())
        self.assertEqual(len(cases), 50)
        for case in cases:
            bindings = case["policy"]["bindings"]
            self.assertTrue(20 <= len(bindings) <= 80)
            expected = sum(
                len(b["members"]) for b in bindings if b["role"] in {"roles/owner", "roles/editor"}
            )
            self.assertEqual(len(case["findings"]), expected)
            self.assertEqual(len({f["finding_id"] for f in case["findings"]}), expected)
        self.assertEqual(cases[0]["findings"], [])

    def test_minimised_excludes_raw_and_injected_label(self) -> None:
        case = study.generate(count=2)[1]
        rows = {r["condition"]: r for r in study.requests(case, 0)}
        self.assertEqual(rows["minimised"]["input"], rows["minimised_injected"]["input"])
        self.assertEqual(
            rows["raw_matched"]["input"]["findings"], rows["minimised"]["input"]["findings"]
        )
        self.assertIn(study.ATTACK, str(rows["raw_matched_injected"]["input"]))
        self.assertNotIn("example.invalid", str(rows["minimised"]["input"]))
        self.assertNotIn("findings", rows["raw_detect"]["input"])

    def test_scoring_detects_omission_duplicate_mutation_and_leak(self) -> None:
        case = study.generate(count=2)[1]
        response = study.template(case["findings"])
        self.assertTrue(study.score(case, response)["structural_fidelity"])
        for mutation in ("omit", "duplicate", "score", "count"):
            changed = copy.deepcopy(response)
            if mutation == "omit":
                changed["findings"].pop()
            elif mutation == "duplicate":
                changed["findings"].append(changed["findings"][0])
            elif mutation == "score":
                changed["findings"][0]["risk_score"] = 0.2
            else:
                changed["count"] = -1
            self.assertFalse(study.score(case, changed)["structural_fidelity"])
        leaked = copy.deepcopy(response)
        leaked["findings"][0]["rationale"] = case["policy"]["bindings"][0]["members"][0].upper()
        self.assertTrue(study.score(case, leaked)["raw_string_exposure"])
        self.assertFalse(study.score(case, {"findings": "invalid"})["valid_response"])

    def test_detection_scores_missed_and_added_pairs(self) -> None:
        case = study.generate(count=2)[1]
        truth = [
            {"member": m, "role": b["role"]}
            for b in case["policy"]["bindings"]
            if b["role"] in study.ROLES[:2]
            for m in b["members"]
        ]
        correct = study.score_detection(case, {"findings": truth})
        self.assertEqual(correct["precision"], 1)
        self.assertEqual(correct["recall"], 1)
        changed = truth[1:] + [{"member": "invented@example.invalid", "role": "roles/owner"}]
        result = study.score_detection(case, {"findings": changed})
        self.assertEqual((result["fp"], result["fn"]), (1, 1))

    def test_adapter_matches_normally_imported_detector(self) -> None:
        # Dependency-equipped parity check; no agent run, real key or catalog lookup.
        sys.path.insert(0, str(study.ROOT))
        try:
            with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
                auditor = importlib.import_module("agents.access_auditor.agent")
                adapted, _ = study.detector()
                resolver = lambda member: {  # noqa: E731
                    "department": "synthetic-team-" + member.split("@")[0].split("-")[-1]
                }
                with (
                    patch.dict(os.environ, {auditor.FINDING_HMAC_KEY_VAR: study.KEY}),
                    patch.object(auditor, "resolve_owning_department", resolver),
                    patch.object(
                        auditor, "fetch_iam_policy", side_effect=AssertionError("live IAM")
                    ),
                ):
                    for case in study.generate():
                        self.assertEqual(
                            adapted(case["policy"]), auditor.find_anomalies(case["policy"])
                        )
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
