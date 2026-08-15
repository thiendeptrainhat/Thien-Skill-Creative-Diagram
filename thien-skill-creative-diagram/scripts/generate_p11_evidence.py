"""Generate deterministic P-11 registries and read-only QA evidence."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
TEST_DIR = SCRIPT_DIR / "tests"
SKILL_ROOT = SCRIPT_DIR.parent
REPO_ROOT = SKILL_ROOT.parent
REFERENCE_DIR = SKILL_ROOT / "references"
EVIDENCE_DIR = REPO_ROOT / "evidence" / "p11"
P06_ROOT = REPO_ROOT / "evidence" / "p06" / "golden-candidates"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from golden_review import compare
from output_pipeline import export_artifacts
from p11_coverage import P11_HARD_FAILURES
from qa_contract import (
    QA_VERSION,
    audit_skill_tree,
    validate_carrier_equivalence,
    validate_motion_html,
    validate_quantitative_ir,
    validate_svg_contract,
)
from semantic_fixtures import fixtures


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _request(diagram_type: str, *, format: str = "svg", motion: str = "none") -> dict[str, Any]:
    return {
        "instruction": "Generate deterministic P-11 QA evidence.",
        "source": {"kind": "natural-language", "content": "Independent P-11 QA fixture."},
        "diagram_type": diagram_type,
        "size": "fit",
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": {"mode": "explicit", "tag": "vi"},
        "format": format,
        "motion": motion,
    }


def _golden_manifest() -> dict[str, Any]:
    pilot = json.loads((P06_ROOT / "pilot-manifest.json").read_text(encoding="utf-8"))
    artifacts: list[dict[str, str]] = []
    for item in pilot["artifacts"]:
        for kind, media_type in (("html", "text/html"), ("svg", "image/svg+xml")):
            artifacts.append({
                "path": f"evidence/p06/golden-candidates/{item[kind]}",
                "sha256": item[f"{kind}_sha256"],
                "media_type": media_type,
                "approval_ref": "PROJECT-CONTRACT.md D-025",
            })
    return {"schema_version": "1.0", "approval": "approved-p06-direction", "immutable": True, "artifacts": artifacts}


def generate() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    coverage = {
        "schema_version": "1.0",
        "phase": "P-11",
        "qa_version": QA_VERSION,
        "hard_failure_count": len(P11_HARD_FAILURES),
        "categories": sorted({item["category"] for item in P11_HARD_FAILURES.values()}),
        "hard_failures": P11_HARD_FAILURES,
        "boundary": "P-09 and P-12 are not started; no benchmark or independent forward test is included.",
    }
    _write_json(REFERENCE_DIR / "p11-hard-failure-map.json", coverage)

    golden_manifest = _golden_manifest()
    golden_path = EVIDENCE_DIR / "approved-p06-golden-manifest.json"
    _write_json(golden_path, golden_manifest)
    golden_report = compare(golden_path, REPO_ROOT)
    _write_json(EVIDENCE_DIR / "golden-review-report.json", {**golden_report, "baseline_updated": False})

    cases = fixtures()
    svg_report: list[dict[str, Any]] = []
    for diagram_type, ir in cases.items():
        bundle = export_artifacts(ir, _request(diagram_type), auto_detect_rasterizer=False)
        svg = bundle.artifacts["svg"].content.decode("utf-8")
        validation = validate_svg_contract(svg, ir)
        svg_report.append({"diagram_type": diagram_type, "sha256": bundle.artifacts["svg"].sha256, "validation": validation["status"]})

    quantitative: list[dict[str, Any]] = []
    for diagram_type in ("bar-chart", "line-chart", "scatter-plot", "radar", "gantt", "timeline", "quadrant", "pyramid-funnel"):
        ir = cases[diagram_type]
        if diagram_type in {"scatter-plot", "quadrant"}:
            ir = json.loads(json.dumps(ir, ensure_ascii=False))
            for series in ir["series"]:
                series["unit"] = series.get("unit") or "điểm"
        svg = export_artifacts(ir, _request(diagram_type), auto_detect_rasterizer=False).artifacts["svg"].content.decode("utf-8")
        result = validate_quantitative_ir(ir, svg)
        quantitative.append({"diagram_type": diagram_type, "status": result["status"]})

    step_html = export_artifacts(cases["flowchart"], _request("flowchart", format="html", motion="step"), auto_detect_rasterizer=False).artifacts["html"].content.decode("utf-8")
    carrier = validate_carrier_equivalence(
        "Kỳ\tGiá trị\tGhi chú\nT1\t0\tnull\nT2\t-2.50\tổn định",
        "Kỳ,Giá trị,Ghi chú\nT1,0,null\nT2,-2.50,ổn định",
        '[{"Kỳ":"T1","Giá trị":0,"Ghi chú":null},{"Kỳ":"T2","Giá trị":-2.5,"Ghi chú":"ổn định"}]',
    )
    qa_report = {
        "schema_version": "1.0",
        "phase": "P-11",
        "qa_version": QA_VERSION,
        "skill_tree": audit_skill_tree(SKILL_ROOT),
        "svg_matrix": svg_report,
        "svg_matrix_count": len(svg_report),
        "quantitative": quantitative,
        "carrier_equivalence": carrier,
        "motion": validate_motion_html(step_html, "step"),
        "golden": {"compared": golden_report["compared"], "immutable": True, "baseline_updated": False},
        "browser_verification": "not-run-out-of-scope: P-11 builds static QA/golden infrastructure; executable benchmark/browser runs belong to P-12",
        "p09_p12_boundary": "not-started",
    }
    _write_json(EVIDENCE_DIR / "qa-run-report.json", qa_report)
    _write_json(EVIDENCE_DIR / "mutation-coverage-report.json", {
        "schema_version": "1.0",
        "phase": "P-11",
        "status": "pass-after-unit-suite",
        "hard_failure_count": len(P11_HARD_FAILURES),
        "detected_count": sum(item["status"] == "detected" for item in P11_HARD_FAILURES.values()),
        "test_ids": sorted(item["test_id"] for item in P11_HARD_FAILURES.values()),
        "note": "The unit-test run is recorded in P-11-EVIDENCE.md; this registry does not self-certify without that run.",
    })
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(EVIDENCE_DIR.iterdir())
        if path.is_file() and path.name not in {"artifact-hashes.json", "P-11-EVIDENCE.md"}
    }
    _write_json(EVIDENCE_DIR / "artifact-hashes.json", hashes)


if __name__ == "__main__":
    generate()

