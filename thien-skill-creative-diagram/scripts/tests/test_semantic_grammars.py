"""P-05 semantic grammar, inventory, selector, and pattern tests."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from diagram_core import CoreError, plan_complexity  # noqa: E402
from semantic_catalog import CAPABILITY_MAP, PATTERNS, SPECIMEN_GROUPS, TYPE_GRAMMARS, VARIANT_MAPPINGS, expected_capability_ids  # noqa: E402
from semantic_grammars import missing_invariant_handlers, select_data_lake_profile, validate_semantics  # noqa: E402
from semantic_patterns import TRANSFORMS, apply_pattern  # noqa: E402
from semantic_fixtures import COLLECTIONS, finalize, fixtures, negative_fixture, variant_fixtures  # noqa: E402


def materialize_pattern(fragment):
    collections = {name: copy.deepcopy(fragment.get(name, [])) for name in COLLECTIONS}
    return finalize(fragment["diagram_type"], **collections)


class SemanticGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = fixtures()

    def test_all_39_positive_fixtures(self):
        self.assertEqual(set(self.cases), set(TYPE_GRAMMARS))
        for diagram_type, ir in self.cases.items():
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(validate_semantics(ir)["diagram"]["type"], diagram_type)

    def test_all_39_boundary_mutations_fail(self):
        for diagram_type, ir in self.cases.items():
            with self.subTest(diagram_type=diagram_type):
                with self.assertRaises(CoreError):
                    validate_semantics(negative_fixture(diagram_type, ir))

    def test_invariant_handler_coverage_is_complete(self):
        self.assertEqual(missing_invariant_handlers(), set())

    def test_capability_inventory_is_exact_and_actionable(self):
        self.assertEqual(set(CAPABILITY_MAP), expected_capability_ids())
        self.assertEqual(len(CAPABILITY_MAP), 111)
        for capability_id, entry in CAPABILITY_MAP.items():
            with self.subTest(capability_id=capability_id):
                self.assertTrue(entry["implementation"])
                self.assertTrue(entry["selector"])
                self.assertTrue(entry["fallback"])
                self.assertTrue(entry["test_id"])
                self.assertTrue(entry["status"])

    def test_specimen_inventory_count_and_links(self):
        self.assertEqual(sum(group["count"] for group in SPECIMEN_GROUPS), 97)
        for group in SPECIMEN_GROUPS:
            self.assertTrue(set(group["capabilities"]) <= set(CAPABILITY_MAP))

    def test_variants_have_parent_phase_and_status(self):
        self.assertEqual(len(VARIANT_MAPPINGS), 20)
        for capability_id, variant in VARIANT_MAPPINGS.items():
            with self.subTest(capability_id=capability_id):
                self.assertTrue(variant["parents"])
                self.assertTrue(variant["phase"])
                self.assertTrue(variant["implementation"])
                self.assertTrue(variant["status"])

    def test_data_lake_selector_reuses_only_three_existing_types(self):
        self.assertEqual(select_data_lake_profile(["tier-promotion"])[0]["type"], "medallion")
        selected = select_data_lake_profile(iter(["sources-platform-consumers", "stage-layer-overview"]))
        self.assertEqual({item["type"] for item in selected}, {"dp-integration", "high-level"})
        self.assertTrue(all(item["materially_distinct"] for item in selected))

    def test_data_lake_selector_rejects_unknown_or_empty_signal(self):
        for signals in ([], ["pretty-lake"]):
            with self.subTest(signals=signals), self.assertRaises(CoreError):
                select_data_lake_profile(signals)

    def test_variant_parent_mismatch_fails(self):
        ir = copy.deepcopy(self.cases["bar-chart"])
        ir["diagram"]["variant_ids"] = ["CAP-V09"]
        with self.assertRaises(CoreError) as caught:
            validate_semantics(ir)
        self.assertEqual(caught.exception.code, "variant-parent-mismatch")

    def test_all_four_v15_variants_validate_under_their_locked_parents(self):
        cases = variant_fixtures()
        self.assertEqual(set(cases), {"CAP-V17", "CAP-V18", "CAP-V19", "CAP-V20"})
        for capability_id, ir in cases.items():
            with self.subTest(capability_id=capability_id):
                self.assertEqual(validate_semantics(ir)["diagram"]["variant_ids"], [capability_id])

    def test_vietnamese_long_label_is_preserved(self):
        ir = copy.deepcopy(self.cases["process"])
        long_label = "Bộ phận kiểm soát nội bộ rà soát đầy đủ chứng từ đối chiếu và lưu vết phê duyệt"
        ir["nodes"][0]["label"] = long_label
        self.assertEqual(validate_semantics(ir)["nodes"][0]["label"], long_label)

    def test_dense_graph_reports_complexity_without_semantic_loss(self):
        ir = copy.deepcopy(self.cases["architecture"])
        template = ir["nodes"][1]
        for index in range(40):
            item = copy.deepcopy(template)
            item["id"] = f"service-extra-{index}"
            item["label"] = f"Dịch vụ nghiệp vụ có nhãn dài số {index}"
            source_id = f"source-service-extra-{index}"
            item["source_refs"] = [source_id]
            ir["nodes"].append(item)
            ir["source_items"].append({"id": source_id, "source_kind": "natural-language", "locator": f"dense:{index}", "content_class": "entity"})
            ir["fidelity"]["kept"].append({"source_ids": [source_id], "ir_ids": [item["id"]], "reason": "Supplied dense node retained."})
            ir["accessibility"]["reading_order"].append(item["id"])
        validate_semantics(ir)
        plan = plan_complexity(ir, {"size": "doc-inline"})
        self.assertFalse(plan["fits"])
        self.assertIn(plan["resolution"], {"offer-larger-size", "split-or-narrow"})


class SemanticPatternTests(unittest.TestCase):
    CASES = {
        "CAP-P01": {"producers": ["Cổng A", "Cổng B"], "queue": "Hàng đợi", "sink": "Xử lý", "capacity": "100 hồ sơ", "overflow": "Vùng tràn"},
        "CAP-P02": {"stages": [{"owner": "Tiếp nhận", "activity": "Kiểm tra", "artifact": "Phiếu nhận"}, {"owner": "Phê duyệt", "activity": "Duyệt", "artifact": "Quyết định"}]},
        "CAP-P03": {"input": "Email tự do", "transform": "Chuẩn hóa", "output": "Bản ghi cấu trúc"},
        "CAP-P04": {"request": "Yêu cầu truy cập", "policy": "Đủ điều kiện?", "allow_outcome": "Cho phép", "deny_outcome": "Từ chối"},
        "CAP-P05": {"requester": "Ứng dụng", "gateway": "Cổng kiểm soát", "service": "Dịch vụ chuẩn", "denied_route": "Đường tắt bị chặn", "boundary": "Vùng tin cậy", "approved_label": "Được phê duyệt", "denied_label": "Bị từ chối"},
        "CAP-P06": {"layers": [{"layer": "Biên", "owner": "An ninh", "control": "WAF"}, {"layer": "Dữ liệu", "owner": "Dữ liệu", "control": "Phân quyền"}]},
        "CAP-P07": {"layers": ["Phòng ngừa", "Phát hiện"], "controls": ["Kiểm tra đầu vào", "Cảnh báo"], "owner": "Kiểm soát", "residual_risk": "Rủi ro còn lại được theo dõi"},
    }

    def test_all_seven_patterns_transform_to_valid_parent_semantics(self):
        self.assertEqual(set(TRANSFORMS), set(PATTERNS))
        for capability_id, facts in self.CASES.items():
            with self.subTest(capability_id=capability_id):
                fragment = apply_pattern(capability_id, facts)
                self.assertEqual(fragment["diagram_type"], PATTERNS[capability_id]["parent"])
                self.assertEqual(validate_semantics(materialize_pattern(fragment))["diagram"]["type"], fragment["diagram_type"])

    def test_patterns_do_not_invent_missing_required_labels(self):
        for capability_id in PATTERNS:
            with self.subTest(capability_id=capability_id), self.assertRaises(CoreError):
                apply_pattern(capability_id, {})

    def test_generated_maps_are_json_serializable(self):
        json.dumps(CAPABILITY_MAP, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
