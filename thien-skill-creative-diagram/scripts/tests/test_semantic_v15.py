"""P-17 contract tests for the 39-type / four-capability semantic target."""

from __future__ import annotations

import copy
import json
import sys
import unittest
import unicodedata
from decimal import Decimal
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from diagram_core import CANONICAL_TYPES, CoreError, build_ir, normalize_request, semantic_hash, validate_common_ir  # noqa: E402
from full_renderer import render_static  # noqa: E402
from semantic_catalog import TYPE_GRAMMARS, VARIANT_MAPPINGS  # noqa: E402
from semantic_fixtures import fixtures, negative_fixture, remove_material, variant_fixtures  # noqa: E402
from semantic_grammars import derive_ridgeline_profiles, normalize_unit, numeric_tolerance, numerically_equal, validate_semantics  # noqa: E402
from visual_system import VisualError  # noqa: E402


SKILL_ROOT = SCRIPT_DIR.parent
NEW_TYPES = tuple(diagram_type for diagram_type, grammar in TYPE_GRAMMARS.items() if int(grammar["capability_id"][-2:]) >= 28)
NEW_VARIANTS = ("CAP-V17", "CAP-V18", "CAP-V19", "CAP-V20")


def explicit_request(diagram_type: str, variant_ids: list[str] | None = None) -> dict[str, object]:
    return {
        "instruction": "Tạo sơ đồ từ các dữ kiện đã cung cấp.",
        "source": {"kind": "natural-language", "content": "Dữ kiện độc lập."},
        "diagram_type": diagram_type,
        "variant_ids": variant_ids or [],
        "language": {"mode": "explicit", "tag": "vi"},
    }


def parsed_from_ir(ir: dict[str, object]) -> dict[str, object]:
    diagram = ir["diagram"]
    return {
        "title": diagram["title"],
        "route_candidates": [{
            "type": diagram["type"],
            "confidence": "high",
            "evidence": [f"request:p17 fixture {diagram['type']}"],
            "compatible": True,
            "viable": True,
            "materially_distinct": False,
        }],
        "variant_ids": list(diagram.get("variant_ids", [])),
        **{key: copy.deepcopy(ir[key]) for key in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations", "source_items", "fidelity", "accessibility")},
    }


def expect_core_code(test: unittest.TestCase, code: str, callback) -> None:
    with test.assertRaises(CoreError) as raised:
        callback()
    test.assertEqual(raised.exception.code, code)


class P17SchemaRouterTests(unittest.TestCase):
    def test_request_and_ir_schemas_lock_exact_39_type_enum(self) -> None:
        request_schema = json.loads((SKILL_ROOT / "references" / "request.schema.json").read_text(encoding="utf-8"))
        ir_schema = json.loads((SKILL_ROOT / "references" / "semantic-ir.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(request_schema["properties"]["schema_version"]["const"], "1.5")
        self.assertEqual(ir_schema["properties"]["schema_version"]["const"], "1.5")
        self.assertEqual(tuple(request_schema["properties"]["diagram_type"]["enum"][1:]), CANONICAL_TYPES)
        self.assertEqual(tuple(ir_schema["$defs"]["type"]["enum"]), CANONICAL_TYPES)
        self.assertEqual(len(CANONICAL_TYPES), 39)

    def test_ir_schema_exposes_all_locked_structured_fields(self) -> None:
        schema = json.loads((SKILL_ROOT / "references" / "semantic-ir.schema.json").read_text(encoding="utf-8"))
        node_fields = set(schema["$defs"]["node"]["properties"])
        edge_fields = set(schema["$defs"]["edge"]["properties"])
        group_fields = set(schema["$defs"]["group"]["properties"])
        member_fields = set(schema["$defs"]["member"]["properties"])
        datum_fields = set(schema["$defs"]["datum"]["properties"])
        self.assertTrue({"parent_group_id", "members", "placement", "work", "journey", "strategy", "story"} <= node_fields)
        self.assertTrue({"amount", "unit", "relation_kind", "source_member", "target_member"} <= edge_fields)
        self.assertTrue({"declared_total", "unit", "wip_limit", "release_slice", "cause_category"} <= group_fields)
        self.assertTrue({"indexed_member_ids", "index_unique"} <= member_fields)
        self.assertTrue({"x_value", "y_value", "size_value", "size_unit", "distribution_samples"} <= datum_fields)

    def test_request_variant_parent_contract_is_enforced(self) -> None:
        for capability_id, parent in {"CAP-V17": "bar-chart", "CAP-V18": "line-chart", "CAP-V19": "line-chart", "CAP-V20": "scatter-plot"}.items():
            with self.subTest(capability_id=capability_id):
                self.assertEqual(normalize_request(explicit_request(parent, [capability_id]))["variant_ids"], [capability_id])
                expect_core_code(self, "variant-parent-mismatch", lambda: normalize_request(explicit_request("architecture", [capability_id])))

    def test_explicit_request_variant_reaches_ir_without_parser_invention(self) -> None:
        ir = variant_fixtures()["CAP-V17"]
        parsed = parsed_from_ir(ir)
        parsed["variant_ids"] = []
        built = build_ir(explicit_request("bar-chart", ["CAP-V17"]), parsed)
        self.assertEqual(built["diagram"]["variant_ids"], ["CAP-V17"])
        parsed["variant_ids"] = ["CAP-V18"]
        expect_core_code(self, "variant-selection-conflict", lambda: build_ir(explicit_request("bar-chart", ["CAP-V17"]), parsed))

    def test_p17_coverage_registry_has_stable_ids_and_render_deferral(self) -> None:
        registry = json.loads((SKILL_ROOT / "references" / "semantic-v15-coverage-map.json").read_text(encoding="utf-8"))
        self.assertEqual(set(registry["capabilities"]), {f"CAP-T{i:02d}" for i in range(28, 40)} | set(NEW_VARIANTS))
        for capability_id, entry in registry["capabilities"].items():
            with self.subTest(capability_id=capability_id):
                self.assertEqual(entry["semantic_status"], "implemented-p17")
                self.assertEqual(entry["render_status"], "deferred-to-p18-or-p19")
                suffixes = {test_id.rsplit("-", 2)[-2] for test_id in entry["test_ids"]}
                self.assertTrue({"POS", "BOUND", "HARD", "RENDER", "A11Y"} <= suffixes)
                render_id = next(test_id for test_id in entry["test_ids"] if "-RENDER-" in test_id)
                self.assertEqual(entry["test_status"][render_id], "deferred-to-p18-or-p19")


class P17CanonicalSemanticTests(unittest.TestCase):
    def test_all_12_positive_boundary_and_hard_families_are_executable(self) -> None:
        cases = fixtures()
        self.assertEqual(len(NEW_TYPES), 12)
        for diagram_type in NEW_TYPES:
            with self.subTest(test_id=f"T-TYPE-{int(TYPE_GRAMMARS[diagram_type]['capability_id'][-2:]):02d}-POS-01"):
                self.assertEqual(validate_semantics(cases[diagram_type])["diagram"]["type"], diagram_type)
            with self.subTest(test_id=f"T-TYPE-{int(TYPE_GRAMMARS[diagram_type]['capability_id'][-2:]):02d}-BOUND-01"):
                with self.assertRaises(CoreError):
                    validate_semantics(negative_fixture(diagram_type, cases[diagram_type]))

    def test_all_12_fixtures_have_complete_accessible_reading_order(self) -> None:
        for diagram_type in NEW_TYPES:
            with self.subTest(diagram_type=diagram_type):
                ir = validate_common_ir(copy.deepcopy(fixtures()[diagram_type]))
                material = {item["id"] for name in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations") for item in ir[name]}
                material.update(member["id"] for node in ir["nodes"] for member in node.get("members", []))
                self.assertEqual(set(ir["accessibility"]["reading_order"]), material)

    def test_polar_zero_and_missing_are_preserved_but_negative_fails(self) -> None:
        ir = copy.deepcopy(fixtures()["polar-chart"])
        validated = validate_semantics(ir)
        values = [datum["value"] for datum in validated["series"][0]["data"]]
        self.assertIn(0, values)
        self.assertIn(None, values)
        ir["series"][0]["data"][0]["value"] = -0.01
        expect_core_code(self, "polar-value-out-of-domain", lambda: validate_semantics(ir))

    def test_treemap_zero_leaf_reconciles_and_missing_or_unit_mismatch_fails(self) -> None:
        ir = copy.deepcopy(fixtures()["treemap"])
        ir["nodes"][0]["value"] = 0
        for group in ir["groups"]:
            group["declared_total"] = 40
        self.assertEqual(validate_semantics(ir)["nodes"][0]["value"], 0)
        missing = copy.deepcopy(ir)
        missing["nodes"][0]["value"] = None
        expect_core_code(self, "treemap-value-invalid", lambda: validate_semantics(missing))
        mismatched = copy.deepcopy(ir)
        mismatched["nodes"][0]["unit"] = "Triệu đồng"
        expect_core_code(self, "unit-mismatch", lambda: validate_semantics(mismatched))

    def test_sankey_zero_flow_epsilon_and_unit_policy(self) -> None:
        zero = copy.deepcopy(fixtures()["sankey"])
        for edge in zero["edges"]:
            edge["amount"] = 0
        self.assertEqual(validate_semantics(zero)["edges"][0]["amount"], 0)
        within = copy.deepcopy(fixtures()["sankey"])
        within["edges"][1]["amount"] = 25 + 1e-9
        self.assertEqual(validate_semantics(within)["diagram"]["type"], "sankey")
        outside = copy.deepcopy(fixtures()["sankey"])
        outside["edges"][1]["amount"] = 25.000001
        expect_core_code(self, "sankey-conservation-failure", lambda: validate_semantics(outside))
        trimmed = copy.deepcopy(fixtures()["sankey"])
        trimmed["edges"][1]["unit"] = "  hồ sơ  "
        validate_semantics(trimmed)
        case_sensitive = copy.deepcopy(fixtures()["sankey"])
        case_sensitive["edges"][1]["unit"] = "Hồ sơ"
        expect_core_code(self, "unit-mismatch", lambda: validate_semantics(case_sensitive))

    def test_structural_boundaries_cover_story_pairing_and_physical_index_scope(self) -> None:
        story = copy.deepcopy(fixtures()["story-map"])
        story["nodes"][1]["story"].update({"release_slice": "R2", "cut_status": "unassigned"})
        expect_core_code(self, "story-unassigned-pairing", lambda: validate_semantics(story))
        schema = copy.deepcopy(fixtures()["database-schema"])
        before_hash = semantic_hash(schema)
        schema["nodes"][1]["members"][2]["indexed_member_ids"].reverse()
        validated = validate_semantics(schema)
        self.assertEqual(validated["nodes"][1]["members"][2]["indexed_member_ids"], ["column-order-id", "column-order-customer"])
        self.assertNotEqual(semantic_hash(schema), before_hash)
        foreign = copy.deepcopy(fixtures()["database-schema"])
        foreign["nodes"][0]["members"][1]["indexed_member_ids"] = ["column-order-id"]
        expect_core_code(self, "index-member-invalid", lambda: validate_semantics(foreign))

    def test_nested_unknown_fields_fail_closed(self) -> None:
        deployment = copy.deepcopy(fixtures()["deployment"])
        deployment["nodes"][0]["placement"]["run_script"] = True
        expect_core_code(self, "unknown-field", lambda: validate_semantics(deployment))


class P17VariantQuantitativeTests(unittest.TestCase):
    def test_numeric_equality_formula_and_nfc_unit_normalization_are_exact(self) -> None:
        self.assertEqual(numeric_tolerance(0), Decimal("1E-9"))
        self.assertEqual(numeric_tolerance(1_000_000), Decimal("0.001000000"))
        self.assertTrue(numerically_equal(1, 1 + 1e-9))
        self.assertFalse(numerically_equal(1, 1 + 2e-9))
        decomposed = unicodedata.normalize("NFD", "điểm")
        self.assertEqual(normalize_unit(f"  {decomposed}  "), "điểm")
        self.assertNotEqual(normalize_unit("Điểm"), normalize_unit("điểm"))

    def test_dumbbell_shared_domain_cardinality_gap_and_missing_policy(self) -> None:
        ir = copy.deepcopy(variant_fixtures()["CAP-V17"])
        validated = validate_semantics(ir)
        gaps = [second["value"] - first["value"] for first, second in zip(validated["series"][0]["data"], validated["series"][1]["data"])]
        self.assertEqual(gaps, [6, 6])
        missing = copy.deepcopy(ir)
        missing["series"][1]["data"][0].update({"value": None, "missing": True})
        expect_core_code(self, "dumbbell-endpoint-invalid", lambda: validate_semantics(missing))
        cardinality = copy.deepcopy(ir)
        remove_material(cardinality, "series", "series-after")
        expect_core_code(self, "dumbbell-cardinality", lambda: validate_semantics(cardinality))

    def test_slopegraph_preserves_direction_rank_and_crossing(self) -> None:
        ir = validate_semantics(copy.deepcopy(variant_fixtures()["CAP-V18"]))
        directions = [series["data"][1]["value"] - series["data"][0]["value"] for series in ir["series"]]
        self.assertEqual(directions, [6, -3])
        rank_before = sorted(ir["series"], key=lambda series: series["data"][0]["value"], reverse=True)
        rank_after = sorted(ir["series"], key=lambda series: series["data"][1]["value"], reverse=True)
        self.assertNotEqual([series["id"] for series in rank_before], [series["id"] for series in rank_after])
        mismatched = copy.deepcopy(ir)
        mismatched["series"][1]["unit"] = "Điểm"
        expect_core_code(self, "unit-mismatch", lambda: validate_semantics(mismatched))

    def test_ridgeline_histogram_and_explicit_bandwidth_kde_use_global_max(self) -> None:
        histogram = validate_semantics(copy.deepcopy(variant_fixtures()["CAP-V19"]))
        profiles = derive_ridgeline_profiles(histogram)
        self.assertAlmostEqual(profiles["global_max"], 0.4)
        self.assertTrue(all(0 <= value <= 1 for values in profiles["amplitudes"].values() for value in values))
        self.assertTrue(any(value == 1 for values in profiles["amplitudes"].values() for value in values))
        kde = copy.deepcopy(histogram)
        for series in kde["series"]:
            series["distribution"].update({"method": "kde-gaussian", "bandwidth": 0.5})
        self.assertGreater(derive_ridgeline_profiles(validate_semantics(kde))["global_max"], 0)
        automatic = copy.deepcopy(kde)
        automatic["series"][0]["distribution"]["bandwidth"] = None
        expect_core_code(self, "invalid-number", lambda: validate_semantics(automatic))

    def test_bubble_zero_size_is_preserved_and_negative_or_missing_fails(self) -> None:
        ir = validate_semantics(copy.deepcopy(variant_fixtures()["CAP-V20"]))
        self.assertEqual(ir["series"][0]["data"][0]["size_value"], 0)
        negative = copy.deepcopy(ir)
        negative["series"][0]["data"][0]["size_value"] = -1
        expect_core_code(self, "bubble-size-negative", lambda: validate_semantics(negative))
        missing = copy.deepcopy(ir)
        missing["series"][0]["data"][0]["size_value"] = None
        expect_core_code(self, "bubble-value-missing", lambda: validate_semantics(missing))

    def test_all_new_variant_parent_mismatches_are_hard_failures(self) -> None:
        for capability_id in NEW_VARIANTS:
            ir = copy.deepcopy(fixtures()["architecture"])
            ir["diagram"]["variant_ids"] = [capability_id]
            with self.subTest(test_id=f"T-VAR-{capability_id}-HARD-PARENT-01"):
                expect_core_code(self, "variant-parent-mismatch", lambda ir=ir: validate_semantics(ir))


class P17VisualBoundaryTests(unittest.TestCase):
    def test_12_new_types_have_no_generic_render_substitution(self) -> None:
        for diagram_type in NEW_TYPES:
            with self.subTest(diagram_type=diagram_type):
                with self.assertRaises(VisualError) as raised:
                    render_static(fixtures()[diagram_type])
                self.assertEqual(raised.exception.code, "type-visual-not-implemented")

    def test_four_new_variants_have_no_parent_render_substitution(self) -> None:
        for capability_id, ir in variant_fixtures().items():
            with self.subTest(capability_id=capability_id):
                with self.assertRaises(VisualError) as raised:
                    render_static(ir)
                self.assertEqual(raised.exception.code, "variant-visual-not-implemented")


if __name__ == "__main__":
    unittest.main()
