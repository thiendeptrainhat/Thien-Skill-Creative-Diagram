"""P-19A adapter coverage and boundary tests."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from diagram_core import CANONICAL_TYPES, CoreError, canonical_json  # noqa: E402
from semantic_fixtures import fixtures, negative_fixture, variant_fixtures  # noqa: E402
from visual_adapters_v15 import (  # noqa: E402
    CAPABILITY_ADAPTERS,
    ENGINE_CAPABILITIES,
    ENGINE_TYPES,
    P19A_CAPABILITIES,
    TYPE_ADAPTERS,
    adapt_visual,
    adapter_inventory,
)


ROOT = SCRIPT_DIR.parents[1]
FOUNDATION = ROOT / "evidence/p18/P-18R4-VISUAL-FOUNDATION.json"
R6_MANIFEST = ROOT / "evidence/p18/r6/P-18R6-MANIFEST.json"
REFERENCE = SCRIPT_DIR.parent / "references/visual-adapters-v15.json"


class P19ARegistryTests(unittest.TestCase):
    def test_exact_39_plus_4_registry_and_fourteen_engines(self) -> None:
        inventory = adapter_inventory()
        self.assertEqual(inventory["canonical_type_count"], 39)
        self.assertEqual(inventory["capability_count"], 4)
        self.assertEqual(inventory["layout_engine_count"], 14)
        self.assertEqual(set(TYPE_ADAPTERS), set(CANONICAL_TYPES))
        self.assertEqual(tuple(CAPABILITY_ADAPTERS), P19A_CAPABILITIES)
        self.assertEqual(sum(len(values) for values in ENGINE_TYPES.values()), 39)
        self.assertEqual(sum(len(values) for values in ENGINE_CAPABILITIES.values()), 4)

    def test_engine_mapping_is_exactly_the_locked_p18r4_mapping(self) -> None:
        foundation = json.loads(FOUNDATION.read_text(encoding="utf-8"))
        expected = [
            {
                "id": item["id"],
                "canonical_types": item["canonical_types"],
                "capabilities": [
                    {"dumbbell": "CAP-V17", "slopegraph": "CAP-V18", "ridgeline": "CAP-V19", "bubble": "CAP-V20"}[value]
                    for value in item["capabilities"]
                ],
            }
            for item in foundation["layout_engines"]
        ]
        self.assertEqual(adapter_inventory()["layout_engines"], expected)

    def test_every_adapter_has_a_distinct_non_generic_silhouette(self) -> None:
        specs = list(TYPE_ADAPTERS.values()) + list(CAPABILITY_ADAPTERS.values())
        silhouettes = [item.silhouette for item in specs]
        self.assertEqual(len(silhouettes), 43)
        self.assertEqual(len(set(silhouettes)), 43)
        self.assertFalse(any("generic" in item or "unknown" in item or "card-template" in item for item in silhouettes))

    def test_reference_is_generated_from_the_canonical_registry(self) -> None:
        reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
        self.assertEqual(reference, adapter_inventory())

    def test_owner_approved_review17_manifest_remains_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(R6_MANIFEST.read_bytes()).hexdigest(),
            "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a",
        )


class P19APlanTests(unittest.TestCase):
    def test_all_39_type_fixtures_produce_deterministic_engine_specific_plans(self) -> None:
        cases = fixtures()
        self.assertEqual(set(cases), set(CANONICAL_TYPES))
        expected_contract = {
            "topology-and-zones": "topology_contract",
            "integration-pipeline": "pipeline_contract",
            "runtime-deployment": "placements",
            "dependency-dag": "dependency_contract",
            "directed-flow-state": "directed_contract",
            "lane-interaction": "lane_contract",
            "time-planning": "time_contract",
            "work-experience": "work_contract",
            "hierarchy": "hierarchy_contract",
            "containment-stack": "containment_contract",
            "compartment-model": "compartment_contract",
            "spatial-matrix": "spatial_contract",
            "quantitative": "quantitative_contract",
            "special-geometry": "special_contract",
        }
        for diagram_type, ir in cases.items():
            with self.subTest(diagram_type=diagram_type):
                first = adapt_visual(copy.deepcopy(ir))
                second = adapt_visual(copy.deepcopy(ir))
                self.assertEqual(canonical_json(first), canonical_json(second))
                self.assertEqual(first["adapter"]["canonical_type"], diagram_type)
                self.assertEqual(first["adapter"]["layout_engine"], TYPE_ADAPTERS[diagram_type].layout_engine)
                self.assertIn(expected_contract[first["adapter"]["layout_engine"]], first["semantic_projection"])
                self.assertEqual(first["phase_boundary"]["html_svg_emission"], "deferred-to-p19b")
                serialized = canonical_json(first).lower()
                self.assertNotIn("<svg", serialized)
                self.assertNotIn("<html", serialized)
                self.assertNotIn("<style", serialized)

    def test_material_inventory_retains_every_semantic_object_and_nested_value(self) -> None:
        for diagram_type, ir in fixtures().items():
            with self.subTest(diagram_type=diagram_type):
                plan = adapt_visual(ir)
                inventory = plan["material_inventory"]
                expected_top = sum(len(ir[name]) for name in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations"))
                expected_members = sum(len(node.get("members", [])) for node in ir["nodes"])
                expected_data = sum(len(series.get("data", [])) for series in ir["series"])
                self.assertEqual(inventory["material_count"], expected_top + expected_members + expected_data)
                self.assertEqual(plan["accessibility_contract"]["reading_order"], ir["accessibility"]["reading_order"])

    def test_invalid_semantics_fail_before_adapter_planning(self) -> None:
        for diagram_type, ir in fixtures().items():
            with self.subTest(diagram_type=diagram_type):
                with self.assertRaises(CoreError):
                    adapt_visual(negative_fixture(diagram_type, ir))

    def test_phase_boundary_never_claims_p19b_or_p19c_work(self) -> None:
        for ir in list(fixtures().values()) + list(variant_fixtures().values()):
            boundary = adapt_visual(ir)["phase_boundary"]
            self.assertEqual(set(boundary.values()), {"deferred-to-p19b", "deferred-to-p19c"})
        self.assertEqual(
            adapter_inventory()["boundary"],
            {
                "emits_html_or_svg": False,
                "derives_visual_modes": False,
                "creates_gallery": False,
                "next_authority_required": "P-19B",
            },
        )


class P19ACapabilityTests(unittest.TestCase):
    def test_dumbbell_projects_exact_endpoint_pairs_and_signed_gap(self) -> None:
        plan = adapt_visual(variant_fixtures()["CAP-V17"])
        self.assertEqual(plan["adapter"]["silhouette"], "paired-values-gap-dumbbell")
        self.assertEqual([item["signed_gap"] for item in plan["semantic_projection"]["quantitative_contract"]["dumbbell_pairs"]], [6, 6])

    def test_slopegraph_projects_two_states_direction_and_delta(self) -> None:
        plan = adapt_visual(variant_fixtures()["CAP-V18"])
        slopes = plan["semantic_projection"]["quantitative_contract"]["slope_series"]
        self.assertEqual([item["delta"] for item in slopes], [6, -3])
        self.assertEqual({item["from_state"] for item in slopes}, {"Trước"})
        self.assertEqual({item["to_state"] for item in slopes}, {"Sau"})

    def test_ridgeline_projects_shared_normalized_profiles(self) -> None:
        plan = adapt_visual(variant_fixtures()["CAP-V19"])
        profiles = plan["semantic_projection"]["quantitative_contract"]["ridgeline_profiles"]
        self.assertGreater(profiles["global_max"], 0)
        self.assertTrue(all(0 <= value <= 1 for values in profiles["amplitudes"].values() for value in values))

    def test_bubble_projects_area_not_radius_as_the_data_value(self) -> None:
        plan = adapt_visual(variant_fixtures()["CAP-V20"])
        points = plan["semantic_projection"]["quantitative_contract"]["bubble_points"]
        self.assertEqual([item["area_value"] for item in points], [0, 25])
        self.assertTrue(all("radius" not in item for item in points))

    def test_capability_parent_and_engine_bindings_are_exact(self) -> None:
        expected = {
            "CAP-V17": "bar-chart",
            "CAP-V18": "line-chart",
            "CAP-V19": "line-chart",
            "CAP-V20": "scatter-plot",
        }
        for capability_id, ir in variant_fixtures().items():
            with self.subTest(capability_id=capability_id):
                plan = adapt_visual(ir)
                self.assertEqual(plan["adapter"]["capability_id"], capability_id)
                self.assertEqual(plan["adapter"]["canonical_type"], expected[capability_id])
                self.assertEqual(plan["adapter"]["layout_engine"], "quantitative")


if __name__ == "__main__":
    unittest.main()
