from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from golden_review import compare, compare_manifest
from qa_contract import QAFailure, sha256_bytes


class ImmutableGoldenReviewTests(unittest.TestCase):
    def manifest(self, sha256: str, path: str = "approved.svg") -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "approval": "owner-approved",
            "immutable": True,
            "artifacts": [{"path": path, "sha256": sha256, "media_type": "image/svg+xml", "approval_ref": "D-025"}],
        }

    def test_matching_approved_bytes_pass_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "approved.svg"
            artifact.write_bytes(b"approved-bytes")
            before = artifact.stat().st_mtime_ns
            result = compare_manifest(self.manifest(sha256_bytes(artifact.read_bytes())), root)
            self.assertEqual(result["status"], "pass")
            self.assertTrue(result["immutable"])
            self.assertEqual(artifact.stat().st_mtime_ns, before)

    def test_drift_missing_approval_and_path_escape_mutations_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "approved.svg"
            artifact.write_bytes(b"current")
            with self.assertRaises(QAFailure) as drift:
                compare_manifest(self.manifest(sha256_bytes(b"previous")), root)
            self.assertEqual(drift.exception.code, "golden-drift")
            missing_approval = self.manifest(sha256_bytes(artifact.read_bytes()))
            missing_approval["approval"] = "candidate"
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(missing_approval), encoding="utf-8")
            with self.assertRaises(QAFailure) as approval:
                compare(manifest_path, root)
            self.assertEqual(approval.exception.code, "golden-approval-missing")
            with self.assertRaises(QAFailure) as escape:
                compare_manifest(self.manifest(sha256_bytes(b"x"), "../outside.svg"), root)
            self.assertEqual(escape.exception.code, "golden-path-escape")

    def test_cli_exposes_compare_only_and_rejects_update(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT_DIR / "golden_review.py"), "--manifest", "x.json", "--root", ".", "--update"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments: --update", result.stderr)


if __name__ == "__main__":
    unittest.main()
