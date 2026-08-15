"""Generate deterministic P-07 reference maps and QA-only smoke evidence."""

from __future__ import annotations

import copy
import hashlib
import html
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
TEST_DIR = SCRIPT_DIR / "tests"
REPO_ROOT = SCRIPT_DIR.parents[1]
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
EVIDENCE_DIR = REPO_ROOT / "evidence" / "p07"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from full_renderer import RENDERER_VERSION, render_static
from p07_coverage import P07_COVERAGE, SPECIMEN_TOTAL
from semantic_catalog import PATTERNS, SPECIMEN_GROUPS, TYPE_GRAMMARS, VARIANT_MAPPINGS
from semantic_fixtures import finalize, fixtures
from semantic_patterns import apply_pattern


MODES = ("neutral-light", "neutral-dark", "editorial")
MODE_VARIANTS = {"CAP-V01": "neutral-light", "CAP-V02": "neutral-dark", "CAP-V03": "editorial"}
PATTERN_FACTS: dict[str, dict[str, Any]] = {
    "CAP-P01": {"producers": ["A", "B"], "queue": "Hàng đợi", "sink": "Kho", "capacity": "100", "overflow": "Tràn"},
    "CAP-P02": {"stages": [{"activity": "Nhận", "artifact": "Phiếu", "owner": "Đơn vị A"}, {"activity": "Duyệt", "artifact": "Biên bản", "owner": "Đơn vị B"}]},
    "CAP-P03": {"input": "Ghi chú", "transform": "Chuẩn hóa", "output": "Hồ sơ"},
    "CAP-P04": {"request": "Yêu cầu", "policy": "Chính sách", "allow_outcome": "Cho phép", "deny_outcome": "Từ chối"},
    "CAP-P05": {"requester": "Nhóm", "gateway": "Cổng", "service": "Dịch vụ", "denied_route": "Đường tắt", "approved_label": "Được duyệt", "denied_label": "Bị chặn", "boundary": "Vùng tin cậy"},
    "CAP-P06": {"layers": [{"layer": "Biên", "owner": "An toàn", "control": "Tường lửa"}, {"layer": "Dữ liệu", "owner": "An toàn", "control": "Mã hóa"}]},
    "CAP-P07": {"layers": ["Biên", "Dữ liệu"], "controls": ["Tường lửa", "Mã hóa"], "owner": "An toàn", "residual_risk": "Rủi ro còn lại"},
}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(REFERENCE_DIR / "visual-coverage-map.json", {
        "schema_version": "1.0",
        "phase": "P-07",
        "capability_count": len(P07_COVERAGE),
        "specimen_count": SPECIMEN_TOTAL,
        "p08_boundary": "Production export and motion remain deferred; this map records static coverage/fallback only.",
        "capabilities": P07_COVERAGE,
    })

    cases = fixtures()
    type_runs: list[dict[str, str]] = []
    light_svgs: list[tuple[str, str]] = []
    for diagram_type in TYPE_GRAMMARS:
        for mode in MODES:
            result = render_static(cases[diagram_type], mode)
            type_runs.append({"diagram_type": diagram_type, "mode": mode, "sha256": result.sha256, "status": result.validation["status"]})
            if mode == "neutral-light":
                light_svgs.append((diagram_type, result.svg))

    qa_svg_dir = EVIDENCE_DIR / "qa-svg"
    qa_svg_dir.mkdir(exist_ok=True)
    for diagram_type in ("architecture", "sequence", "swimlane", "bar-chart", "radar", "dp-security-matrix"):
        (qa_svg_dir / f"{diagram_type}.svg").write_text(render_static(cases[diagram_type]).svg, encoding="utf-8")

    variant_runs: list[dict[str, str]] = []
    for capability_id, variant in VARIANT_MAPPINGS.items():
        parent = "architecture" if "all" in variant["parents"] else variant["parents"][0]
        ir = copy.deepcopy(cases[parent])
        ir["diagram"]["variant_ids"] = [capability_id]
        mode = MODE_VARIANTS.get(capability_id, "neutral-light")
        result = render_static(ir, mode)
        variant_runs.append({"capability_id": capability_id, "parent": parent, "mode": mode, "sha256": result.sha256, "status": result.validation["status"], "boundary": P07_COVERAGE[capability_id]["boundary"]})

    pattern_runs: list[dict[str, str]] = []
    for capability_id, pattern in PATTERNS.items():
        transformed = apply_pattern(capability_id, PATTERN_FACTS[capability_id])
        ir = finalize(pattern["parent"], **{key: transformed[key] for key in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations")})
        result = render_static(ir)
        pattern_runs.append({"capability_id": capability_id, "parent": pattern["parent"], "sha256": result.sha256, "status": result.validation["status"]})

    smoke = {
        "schema_version": "1.0",
        "phase": "P-07",
        "renderer_version": RENDERER_VERSION,
        "type_mode_runs": type_runs,
        "type_mode_count": len(type_runs),
        "variant_runs": variant_runs,
        "variant_count": len(variant_runs),
        "pattern_runs": pattern_runs,
        "pattern_count": len(pattern_runs),
        "specimen_groups": list(SPECIMEN_GROUPS),
        "specimen_count": SPECIMEN_TOTAL,
        "capability_count": len(P07_COVERAGE),
        "p08_boundary": "No production exporter, rasterizer, animation, or motion behavior is implemented by P-07.",
    }
    _write_json(EVIDENCE_DIR / "visual-smoke-manifest.json", smoke)
    _write_json(EVIDENCE_DIR / "import-test-manifest.json", {
        "schema_version": "1.0",
        "phase": "P-07",
        "carriers": ["natural-language", "pasted-table", "csv", "json", "drawio-xml", "drawio-png-embedded-model", "drawio-svg-embedded-model", "mermaid-text", "markdown-mermaid-fence"],
        "mermaid_subsets": ["flowchart/graph", "sequenceDiagram", "stateDiagram-v2/stateDiagram", "erDiagram"],
        "safety_properties": ["data-only", "bounded", "no-fetch", "no-execute", "no-formula-evaluation", "no-external-resource", "no-write", "explicit-source-backed-semantic-mapping", "fidelity-reconciliation"],
        "test_module": "scripts/tests/test_safe_import.py",
    })

    cards = "\n".join(f'<article><h2>{html.escape(name)}</h2>{svg}</article>' for name, svg in light_svgs)
    contact = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>P-07 QA-only visual coverage</title><style>body{{margin:0;padding:32px;background:#e8edf5;color:#17223b;font-family:system-ui,sans-serif}}header{{max-width:1200px;margin:auto auto 24px}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px}}article{{background:white;border:1px solid #c8d2e3;border-radius:16px;padding:16px;overflow:hidden}}h2{{font-size:18px;margin:0 0 10px}}svg{{width:100%;height:auto;display:block}}</style></head><body><header><h1>P-07 · 27-type static visual coverage</h1><p>QA-only; neutral-light representative renders. Not a P-08 production export artifact.</p></header><main>{cards}</main></body></html>'''
    (EVIDENCE_DIR / "contact-sheet.html").write_text(contact, encoding="utf-8")

    hashes = {str(path.relative_to(EVIDENCE_DIR)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(EVIDENCE_DIR.rglob("*")) if path.is_file() and path.name not in {"artifact-hashes.json", "P-07-EVIDENCE.md"}}
    _write_json(EVIDENCE_DIR / "artifact-hashes.json", hashes)


if __name__ == "__main__":
    generate()
