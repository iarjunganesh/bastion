"""Offline source/provenance checks; these tests never rebuild the technical report."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_report

from scripts import check_versions


class ReportIntegrityTests(unittest.TestCase):
    def copy_data(self, target: Path) -> None:
        for name in (
            build_report.LIVE_BUNDLE,
            "summary.json",
            "runs.csv",
            "stages.csv",
            "sha256.json",
        ):
            shutil.copyfile(build_report.LIVE_DATA / name, target / name)

    def test_verified_pilot_has_the_recorded_sample(self) -> None:
        summary = build_report.load_live_validation()
        self.assertEqual(summary["counts"]["completed_with_required_evidence"], 20)
        self.assertEqual(summary["validated_run_audit_events"], 560)

    def test_corrupted_pilot_bundle_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bastion-report-") as directory:
            target = Path(directory)
            self.copy_data(target)
            bundle = target / build_report.LIVE_BUNDLE
            data = bytearray(bundle.read_bytes())
            data[-1] ^= 1
            bundle.write_bytes(data)
            with (
                patch.object(build_report, "LIVE_DATA", target),
                self.assertRaisesRegex(ValueError, "reviewed capture"),
            ):
                build_report.load_live_validation()

    def test_changed_public_csv_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bastion-report-") as directory:
            target = Path(directory)
            self.copy_data(target)
            source = target / "runs.csv"
            source.write_bytes(source.read_bytes() + b"\n")
            with (
                patch.object(build_report, "LIVE_DATA", target),
                self.assertRaisesRegex(ValueError, "public-file hash mismatch"),
            ):
                build_report.load_live_validation()

    def test_version_gate_includes_canonical_section_sources(self) -> None:
        self.assertTrue(set(build_report.source_sections()) <= set(check_versions.doc_files()))

    def test_missing_canonical_section_is_refused(self) -> None:
        with (
            tempfile.TemporaryDirectory(prefix="bastion-report-") as directory,
            patch.object(build_report, "HERE", Path(directory)),
            self.assertRaisesRegex(ValueError, "Missing canonical section"),
        ):
            build_report.source_sections()

    def test_unpublished_evidence_is_not_given_a_false_commit_link(self) -> None:
        text = "[New evidence](https://github.com/iarjunganesh/bastion/blob/REVISION/assets/evidence/25-corrected-cohort-F-verification.md)"
        with patch.object(build_report, "is_base_file", return_value=False):
            resolved = build_report.resolve_repository_links(text)
        self.assertIn("local source snapshot", resolved)
        self.assertNotIn("/blob/", resolved)

    def test_cited_snapshot_rejects_private_and_parent_paths(self) -> None:
        # Joined so the repository's prose-path check does not read a deliberately absent path.
        for relative in (
            ".local/private-record.json",
            "../private.md",
            "/".join(("docs", "..", ".local", "private-record.json")),
            "docs/../report/sections/07-evaluation.md",
        ):
            text = f"[Forbidden](https://github.com/iarjunganesh/bastion/blob/REVISION/{relative})"
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                build_report.repository_sources(text)

    def test_citation_range_checks_interior_keys(self) -> None:
        text = (
            f"# Report\nIndependent researcher, Stockholm\n{build_report.REPORT_DATE}\n"
            "[S1-S3]\n## References\n- **S1.** First\n- **S3.** Third\n"
        )
        with self.assertRaisesRegex(ValueError, "S2"):
            build_report.validate_manuscript(text)

    @staticmethod
    def minimal(body: str) -> str:
        return (
            f"# Report\nIndependent researcher, Stockholm\n{build_report.REPORT_DATE}\n"
            f"{body}\n## References\n- **E03.** Third\n"
        )

    def test_single_digit_evidence_citation_is_refused(self) -> None:
        """`E3` once normalised to `E03`, so a chunk name could pass as an evidence citation."""
        with self.assertRaisesRegex(ValueError, "two digits"):
            build_report.validate_manuscript(self.minimal("[E3]"))

    def test_chunk_style_name_in_prose_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "chunk"):
            build_report.validate_manuscript(self.minimal("E6 used one event. [E03]"))

    def test_hyphenated_word_split_across_source_lines_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "split"):
            build_report.validate_manuscript(self.minimal("a general information-\nflow [E03]"))

    def test_text_sources_hash_identically_across_line_endings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bastion-report-") as directory:
            root = Path(directory)
            (root / "lf.md").write_bytes(b"a\nb\n")
            (root / "crlf.md").write_bytes(b"a\r\nb\r\n")
            (root / "figure.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            self.assertEqual(
                build_report.canonical_bytes(root / "lf.md"),
                build_report.canonical_bytes(root / "crlf.md"),
            )
            self.assertEqual(
                build_report.canonical_bytes(root / "figure.png"), b"\x89PNG\r\n\x1a\n"
            )

    def test_unresolved_placeholder_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "placeholder"):
            build_report.validate_manuscript("[[F: pending]]")

    def test_canonical_manuscript_is_complete_without_creating_a_pdf(self) -> None:
        manuscript = build_report.assemble()
        for expected in (
            "98 of 98",
            "3.01%",
            "5 of 142",
            "Six of ten model completions",
            "pre-specified",
            "RuntimeIncompleteError",
            "E29.",
            "Appendix C",
        ):
            self.assertIn(expected, manuscript)
        self.assertNotIn("pre-registered criteria", manuscript)
        self.assertNotIn("[[", manuscript)
        self.assertNotIn("/blob/REVISION/", manuscript)

    def test_statistical_bound_stays_out_of_abstract_and_conclusion(self) -> None:
        manuscript = build_report.assemble()
        abstract = manuscript.split("## Abstract", 1)[1].split("## 1.", 1)[0]
        conclusion = manuscript.split("## 10. Conclusion", 1)[1].split("## Appendix A", 1)[0]
        for part in (abstract, conclusion):
            self.assertNotIn("3.01", part)
            self.assertNotIn("Clopper", part)

    def test_each_table_shape_fits_the_available_width(self) -> None:
        for columns in (2, 3, 4, 5):
            with self.subTest(columns=columns):
                widths = build_report.table_widths(columns, 499.0)
                self.assertEqual(len(widths), columns)
                self.assertAlmostEqual(sum(widths), 499.0)
                self.assertTrue(all(value > 0 for value in widths))
        with self.assertRaises(ValueError):
            build_report.table_widths(6, 499.0)

    def test_header_presets_give_prose_columns_the_space(self) -> None:
        ledger = build_report.table_widths(4, 499, ("Run", "Fleet", "Classification", "Evidence"))
        bounds = build_report.table_widths(
            3, 499, ("Boundary", "Crossing", "Control at the boundary")
        )
        self.assertGreater(ledger[2], ledger[0] + ledger[1] + ledger[3])
        self.assertGreater(bounds[2], bounds[0])
        for widths in (ledger, bounds):
            self.assertAlmostEqual(sum(widths), 499)


if __name__ == "__main__":
    unittest.main()
