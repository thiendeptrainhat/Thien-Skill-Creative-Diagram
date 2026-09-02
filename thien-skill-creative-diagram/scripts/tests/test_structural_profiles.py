from __future__ import annotations

import copy
import hashlib
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from diagram_core import CANONICAL_TYPES, CoreError, normalize_request
from full_renderer import render_static
from output_pipeline import export_profiled_artifacts
from semantic_fixtures import fixtures, variant_fixtures
from structural_profiles import (
    ARTIFACT_ATTRIBUTE_MAP,
    REGISTRY_PATH,
    StructuralProfileError,
    artifact_binding_attributes,
    build_profiled_plan,
    load_profile_registry,
    resolve_structural_profile,
    validate_artifact_binding,
    validate_profile_binding,
    validate_profile_ledger,
    validate_profile_registry,
)


REPO_ROOT = SCRIPT_DIR.parents[1]
ASSET_DIR = REPO_ROOT / "assets/diagrams"
SCREENSHOT_DIR = REPO_ROOT / "screenshots/diagrams"


def request(diagram_type: str, *, profile: str = "auto", variant_ids: list[str] | None = None, override: dict[str, str] | None = None) -> dict[str, object]:
    return {
        "instruction": "Create a source-faithful diagram.",
        "source": {"kind": "natural-language", "content": "Validated fixture data."},
        "diagram_type": diagram_type,
        "variant_ids": list(variant_ids or []),
        "structural_profile": profile,
        "structural_override": override or {"status": "none"},
        "size": "fit",
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": {"mode": "explicit", "tag": "vi"},
        "format": "svg",
        "motion": "none",
    }


def bound_svg(ir: dict[str, object], binding: dict[str, object]) -> str:
    root = ET.fromstring(render_static(ir, "neutral-light", coverage_badge=False).svg)
    root.attrib.update(artifact_binding_attributes(binding))
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


class RegistryContractTests(unittest.TestCase):
    def test_exact_taxonomy_and_frozen_engine_alignment(self) -> None:
        registry = load_profile_registry()
        result = validate_profile_registry(registry)
        self.assertEqual(result["profiles"], 45)
        self.assertEqual(result["engines"], 14)
        self.assertEqual(result["classes"], {"canonical-anchor": 14, "canonical-type": 25, "capability": 4, "presentation": 2})
        canonical = [item for item in registry["profiles"] if item["profile_class"].startswith("canonical-")]
        self.assertEqual({item["canonical_parent"] for item in canonical}, set(CANONICAL_TYPES))

    def test_every_record_binds_one_approved_neutral_light_asset_pair(self) -> None:
        registry = load_profile_registry()
        identities = [item["approved_reference_identity"] for item in registry["profiles"]]
        self.assertEqual(len(identities), len(set(identities)))
        for identity in identities:
            with self.subTest(identity=identity):
                self.assertTrue((ASSET_DIR / f"{identity}--neutral-light.html").is_file())
                self.assertTrue((SCREENSHOT_DIR / f"{identity}--neutral-light.png").is_file())

    def test_registry_and_materialized_record_hashes_are_deterministic(self) -> None:
        first = resolve_structural_profile("architecture")
        second = resolve_structural_profile("architecture")
        self.assertEqual(first, second)
        self.assertEqual(first["binding"]["registry_sha256"], hashlib.sha256(REGISTRY_PATH.read_bytes()).hexdigest())
        dark = resolve_structural_profile("architecture", mode="neutral-dark")
        self.assertEqual(first["binding"]["profile_record_sha256"], dark["binding"]["profile_record_sha256"])
        self.assertEqual(first["materialized_record"], dark["materialized_record"])


class ResolutionTests(unittest.TestCase):
    def test_semantic_alias_normalizes_to_public_catalog_profile(self) -> None:
        result = resolve_structural_profile("architecture", requested_selector="architecture")
        self.assertEqual(result["binding"]["requested_selector"], "architecture")
        self.assertEqual(result["binding"]["selected_profile"], "topology-and-zones")
        self.assertEqual(result["binding"]["canonical_parent"], "architecture")
        self.assertEqual(result["binding"]["layout_engine"], "topology-and-zones")

    def test_auto_selects_one_default_but_never_infers_presentation_variant(self) -> None:
        self.assertEqual(resolve_structural_profile("layer-stack")["binding"]["selected_profile"], "type-layer-stack")
        self.assertEqual(resolve_structural_profile("scatter-plot")["binding"]["selected_profile"], "quantitative")
        self.assertEqual(resolve_structural_profile("layer-stack", requested_selector="layers")["binding"]["selected_profile"], "layers")
        self.assertEqual(resolve_structural_profile("scatter-plot", requested_selector="scatter-chart")["binding"]["selected_profile"], "scatter-chart")

    def test_capability_requires_exact_semantic_capability(self) -> None:
        result = resolve_structural_profile("bar-chart", requested_selector="CAP-V17", capability_ids=("CAP-V17",))
        self.assertEqual(result["binding"]["selected_profile"], "dumbbell")
        with self.assertRaisesRegex(StructuralProfileError, "exact semantic capability"):
            resolve_structural_profile("bar-chart", requested_selector="dumbbell")
        with self.assertRaises(StructuralProfileError):
            resolve_structural_profile("bar-chart", requested_selector="type-bar-chart", capability_ids=("CAP-V17",))

    def test_unsupported_parent_mismatch_and_silent_fallback_fail_closed(self) -> None:
        with self.assertRaises(StructuralProfileError):
            resolve_structural_profile("architecture", requested_selector="not-a-profile")
        with self.assertRaises(StructuralProfileError):
            resolve_structural_profile("architecture", requested_selector="type-sequence")
        result = resolve_structural_profile("architecture")
        self.assertIsNone(result["binding"]["fallback"])

    def test_custom_structure_needs_reason_and_is_outside_catalog_scope(self) -> None:
        with self.assertRaises(StructuralProfileError):
            resolve_structural_profile("architecture", structural_override="custom-structure")
        result = resolve_structural_profile("architecture", structural_override="custom-structure", override_reason="User explicitly requests a radial topology.")
        self.assertEqual(result["binding"]["conformance_scope"], "outside-45-profile")
        self.assertEqual(result["binding"]["structural_override"], "custom-structure")

    def test_request_extension_defaults_and_validation(self) -> None:
        normalized = normalize_request({"instruction": "Create.", "source": {"kind": "natural-language", "content": "A to B."}})
        self.assertEqual(normalized["structural_profile"], "auto")
        self.assertEqual(normalized["structural_override"], {"status": "none"})
        explicit = normalize_request({**request("architecture", profile="architecture"), "structural_override": {"status": "custom-structure", "reason": "Use a radial topology."}})
        self.assertEqual(explicit["structural_profile"], "architecture")
        with self.assertRaises(CoreError):
            normalize_request({**request("architecture"), "structural_override": {"status": "none", "reason": "conflict"}})

    def test_profiled_plan_wraps_frozen_adapter_before_render(self) -> None:
        ir = fixtures()["architecture"]
        plan = build_profiled_plan(ir, request("architecture", profile="architecture"))
        self.assertEqual(plan["profile_binding"]["binding_stage"], "pre-render")
        self.assertEqual(plan["profile_binding"]["selected_profile"], "topology-and-zones")
        self.assertEqual(plan["semantic_adapter_plan"]["adapter"]["canonical_type"], "architecture")
        capability_ir = variant_fixtures()["CAP-V17"]
        cap_plan = build_profiled_plan(capability_ir, request("bar-chart", profile="dumbbell", variant_ids=["CAP-V17"]))
        self.assertEqual(cap_plan["profile_binding"]["selected_profile"], "dumbbell")


class ReceiptAndExportTests(unittest.TestCase):
    def test_svg_binding_and_ledger_match_without_self_awarded_conformance(self) -> None:
        ir = fixtures()["architecture"]
        binding = resolve_structural_profile("architecture")["binding"]
        svg = bound_svg(ir, binding)
        self.assertEqual(set(ARTIFACT_ATTRIBUTE_MAP.values()), set(artifact_binding_attributes(binding)))
        self.assertEqual(validate_profile_binding(binding)["profile_binding"], "pass")
        self.assertEqual(validate_artifact_binding(svg, binding), {"profile_binding": "pass", "structural_conformance": "not-evaluated"})
        with patch("output_pipeline.render_static", side_effect=AssertionError("historical renderer must not run")):
            bundle = export_profiled_artifacts(ir, request("architecture"), svg, binding, auto_detect_rasterizer=False)
        self.assertEqual(bundle.ledger["schema_version"], "2.1")
        self.assertEqual(bundle.ledger["renderer_version"], "caller-supplied-profiled-svg")
        self.assertEqual(bundle.ledger["selected_profile"], "topology-and-zones")
        self.assertEqual(bundle.ledger["canonical_parent"], "architecture")
        self.assertEqual(bundle.ledger["layout_engine"], "topology-and-zones")
        self.assertEqual(bundle.ledger["mode"], "neutral-light")
        self.assertEqual(bundle.ledger["structural_override"], "none")
        self.assertIsNone(bundle.ledger["profile_fallback"])
        self.assertEqual(bundle.ledger["profile_binding"], "pass")
        self.assertEqual(bundle.ledger["structural_conformance"], "not-evaluated")
        self.assertEqual(validate_profile_ledger(bundle.ledger, binding)["profile_binding"], "pass")

    def test_forged_or_self_awarded_artifact_receipt_is_rejected(self) -> None:
        ir = fixtures()["architecture"]
        binding = resolve_structural_profile("architecture")["binding"]
        root = ET.fromstring(bound_svg(ir, binding))
        root.set("data-selected-profile", "directed-flow-state")
        with self.assertRaises(StructuralProfileError):
            validate_artifact_binding(ET.tostring(root, encoding="unicode"), binding)
        root = ET.fromstring(bound_svg(ir, binding))
        root.set("data-structural-conformance", "pass")
        with self.assertRaises(StructuralProfileError):
            validate_artifact_binding(ET.tostring(root, encoding="unicode"), binding)

    def test_forged_binding_hash_is_rejected(self) -> None:
        binding = resolve_structural_profile("architecture")["binding"]
        forged = copy.deepcopy(binding)
        forged["profile_record_sha256"] = "0" * 64
        with self.assertRaises(StructuralProfileError):
            validate_profile_binding(forged)


if __name__ == "__main__":
    unittest.main()
