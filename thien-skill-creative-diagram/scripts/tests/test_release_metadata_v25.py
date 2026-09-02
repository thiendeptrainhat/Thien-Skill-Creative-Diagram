"""Step4A release-metadata contract for product version 2.5.0."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "thien-skill-creative-diagram"
DISPLAY_NAME = "Thiện’s Skill — Creative Diagram"


class ReleaseMetadataV25Tests(unittest.TestCase):
    def test_source_manifest_rebaselines_release_identity_only(self) -> None:
        manifest = json.loads((SKILL / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["project"]["version"], "2.5.0")
        self.assertEqual(manifest["release_lineage"]["target_version"], "2.5.0")
        self.assertIn("D-200", manifest["release_lineage"]["authorization"])
        gate_state = manifest["release_lineage"]["gate_state"]
        self.assertIn("G-00@2.5.0 PASS", gate_state)
        self.assertIn("G-01@2.5.0 PASS", gate_state)
        self.assertIn("G-02@2.5.0 PASS", gate_state)
        self.assertIn("G-03@2.5.0 PASS-CARRIED-FORWARD", gate_state)
        self.assertIn("G-04@2.5.0 PASS", gate_state)
        reference = next(item for item in manifest["sources"] if item["source_id"] == "SRC-THIEN-UI-UX-ULTRA")
        self.assertEqual(reference["snapshot"]["tag"], "v2.0.0")

    def test_asset_manifest_is_v25_candidate_and_not_release_eligible(self) -> None:
        manifest = json.loads((SKILL / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["project"]["version"], "2.5.0")
        self.assertEqual(manifest["schema_version"], "2.0-candidate")
        self.assertEqual(manifest["record_id"], "D197-ASSET-MANIFEST-CANDIDATE-1")
        self.assertEqual(manifest["status"], "candidate-awaiting-g06-owner-disposition")
        self.assertTrue(manifest["rights_boundary"]["counsel_approval_or_explicit_owner_waiver_required"])
        self.assertTrue(all(item["release_eligible"] is False for item in manifest["approved_candidates"]))
        selected = {
            item["asset_id"]: set(item["package_targets"])
            for item in manifest["approved_candidates"]
            if item["package_targets"]
        }
        self.assertEqual(
            selected,
            {
                "AST-TDTN-LIGHT-64": {"openai-plugin", "universal-raw-skill"},
                "AST-TDTN-LIGHT-400": {"openai-plugin", "universal-raw-skill"},
            },
        )

    def test_legal_candidate_binds_v25_without_changing_license_version(self) -> None:
        application = (SKILL / "LICENSE-APPLICATION.md").read_text(encoding="utf-8")
        notice = (SKILL / "NOTICE").read_text(encoding="utf-8")
        self.assertIn("TCD-LA-2.5.0-RC1", application)
        self.assertIn("phiên bản: `2.5.0`", application)
        self.assertIn("version: `2.5.0`", application)
        self.assertEqual(application.count(f"`{DISPLAY_NAME}`"), 2)
        self.assertIn("Version: 2.5.0", notice)
        self.assertIn("License 2.0", application)
        self.assertEqual((ROOT / "LICENSE.md").read_bytes(), (SKILL / "LICENSE.md").read_bytes())

    def test_readme_and_release_notes_do_not_claim_unbuilt_v25_archives(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        notes = (ROOT / "evidence/p21/RELEASE-NOTES-v2.5.0.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith(f"# {DISPLAY_NAME}\n"))
        self.assertIn(f"`{DISPLAY_NAME}` là skill", readme)
        self.assertTrue(notes.startswith(f"# {DISPLAY_NAME} v2.5.0\n"))
        self.assertIn("Bản phát hành hiện hành là `2.0.0`; candidate kế tiếp là `2.5.0`", readme)
        self.assertIn("Chưa có ZIP hoặc checksum `2.5.0` được công bố", readme)
        self.assertIn("Exact archive digests are intentionally absent until G-05", notes)
        self.assertIn("must not be used as a GitHub Release body before G-07", notes)

    def test_ui_metadata_and_versioned_dist_contract(self) -> None:
        openai = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn(f'display_name: "{DISPLAY_NAME}"', openai)
        self.assertIn('short_description: "Design professional, semantic diagrams"', openai)
        self.assertIn("Use $thien-skill-creative-diagram", openai)

        register = json.loads(
            (ROOT / "evidence/p22/D-157-FULL-POPULATION-REGISTER.json").read_text(encoding="utf-8")
        )
        package_contract = register["d199_step4a_successor_readiness_freeze"]["successor_readiness_contract"][
            "versioned_dist_and_package_contract"
        ]
        self.assertEqual(package_contract["final_root"], "dist/2.5.0")
        self.assertEqual(
            package_contract["final_inventory_order"],
            [
                "SHA256SUMS",
                "packaging-report.json",
                "Thien-Skill-Creative-Diagram-v2.5.0-Claude.zip",
                "Thien-Skill-Creative-Diagram-v2.5.0-ChatGPT.zip",
                "Thien-Skill-Creative-Diagram-v2.5.0-Universal.zip",
            ],
        )
        self.assertFalse((ROOT / "dist/2.5.0").exists())
        self.assertEqual(
            sorted(path.name for path in (ROOT / "dist").iterdir() if path.is_file()),
            [
                "SHA256SUMS-2.0.0.txt",
                "SHA256SUMS.txt",
                "thien-skill-creative-diagram-1.0.0-claude-plugin.zip",
                "thien-skill-creative-diagram-1.0.0-openai-plugin.zip",
                "thien-skill-creative-diagram-1.0.0-universal-raw-skill.zip",
                "thien-skill-creative-diagram-2.0.0-claude-plugin.zip",
                "thien-skill-creative-diagram-2.0.0-openai-plugin.zip",
                "thien-skill-creative-diagram-2.0.0-universal-raw-skill.zip",
            ],
        )

    def test_internal_protocol_versions_remain_independent(self) -> None:
        profiles = json.loads((SKILL / "references/structural-profiles.json").read_text(encoding="utf-8"))
        renderer = (SKILL / "scripts/profile_renderer.py").read_text(encoding="utf-8")
        pipeline = (SKILL / "scripts/output_pipeline.py").read_text(encoding="utf-8")
        self.assertEqual(profiles["schema_version"], "2.1")
        self.assertEqual(profiles["target_version"], "2.1.0")
        self.assertEqual(profiles["profile_count"], 45)
        self.assertIn('RENDERER_VERSION = "profile-renderer-2.1.0"', renderer)
        self.assertIn('"job_version": "2.1"', pipeline)


if __name__ == "__main__":
    unittest.main()
