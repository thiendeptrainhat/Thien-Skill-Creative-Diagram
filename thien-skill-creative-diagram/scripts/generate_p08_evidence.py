"""Generate deterministic P-08 coverage maps and QA-only evidence artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
TEST_DIR = SCRIPT_DIR / "tests"
REPO_ROOT = SCRIPT_DIR.parents[1]
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
EVIDENCE_DIR = REPO_ROOT / "evidence" / "p08"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from motion_catalog import MOTION_CAPABILITIES
from output_pipeline import OUTPUT_VERSION, detect_rasterizer, export_artifacts
from p08_coverage import P08_COVERAGE
from semantic_fixtures import legacy_fixtures


def _request(diagram_type: str, *, format: str = "html", motion: str = "none", size: str = "fit") -> dict[str, Any]:
    return {
        "instruction": "Generate a validated portable artifact.",
        "source": {"kind": "natural-language", "content": "Original P-08 QA fixture."},
        "diagram_type": diagram_type,
        "size": size,
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": {"mode": "explicit", "tag": "vi"},
        "format": format,
        "motion": motion,
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(REFERENCE_DIR / "p08-coverage-map.json", {
        "schema_version": "1.0",
        "phase": "P-08",
        "coverage_count": len(P08_COVERAGE),
        "capabilities": P08_COVERAGE,
        "p09_p11_boundary": "P-09 brand assets and P-11 automated QA/golden infrastructure remain not started.",
    })
    cases = legacy_fixtures()
    matrix: list[dict[str, str]] = []
    for diagram_type, ir in cases.items():
        svg = export_artifacts(ir, _request(diagram_type, format="svg"), auto_detect_rasterizer=False)
        matrix.append({"diagram_type": diagram_type, "format": "svg", "motion": "none", "sha256": svg.artifacts["svg"].sha256})
        for motion in ("none", "reveal", "step", "loop"):
            html = export_artifacts(ir, _request(diagram_type, motion=motion), auto_detect_rasterizer=False)
            matrix.append({"diagram_type": diagram_type, "format": "html", "motion": motion, "sha256": html.artifacts["html"].sha256})

    representatives = {
        "representative-static.html": export_artifacts(cases["architecture"], _request("architecture"), auto_detect_rasterizer=False),
        "representative-reveal.html": export_artifacts(cases["architecture"], _request("architecture", motion="reveal"), auto_detect_rasterizer=False),
        "representative-step.html": export_artifacts(cases["flowchart"], _request("flowchart", motion="step"), auto_detect_rasterizer=False),
        "representative-loop.html": export_artifacts(cases["loop-flywheel"], _request("loop-flywheel", motion="loop"), auto_detect_rasterizer=False),
        "representative.svg": export_artifacts(cases["bar-chart"], _request("bar-chart", format="svg"), auto_detect_rasterizer=False),
    }
    representative_ledgers: dict[str, Any] = {}
    for filename, bundle in representatives.items():
        artifact = next(iter(bundle.artifacts.values()))
        (EVIDENCE_DIR / filename).write_bytes(artifact.content)
        representative_ledgers[filename] = bundle.ledger

    absent_png = export_artifacts(cases["architecture"], _request("architecture", format="png"), auto_detect_rasterizer=False)
    size_runs = []
    for size in ("doc-inline", "doc-wide", "slide-16x9", "slide-4x3", "social-og", "social-square", "print-a4-landscape", "print-letter-landscape", "fit"):
        bundle = export_artifacts(cases["architecture"], _request("architecture", format="svg", size=size), auto_detect_rasterizer=False)
        size_runs.append({"size": size, "sha256": bundle.artifacts["svg"].sha256})
    environment_rasterizer = detect_rasterizer()
    manifest = {
        "schema_version": "1.0",
        "phase": "P-08",
        "output_version": OUTPUT_VERSION,
        "matrix": matrix,
        "matrix_count": len(matrix),
        "expected_matrix_count": 27 * 5,
        "type_count": len(cases),
        "public_motion_modes": ["none", "reveal", "step", "loop"],
        "motion_capability_count": len(MOTION_CAPABILITIES),
        "p08_capability_count": len(P08_COVERAGE),
        "size_runs": size_runs,
        "png_environment": {"detected": environment_rasterizer.name if environment_rasterizer else None, "real_png_generated": False, "fallback_delivered": sorted(absent_png.artifacts), "warnings": absent_png.ledger["warnings"]},
        "representative_ledgers": representative_ledgers,
        "browser_verification": "blocked-not-executable: local file URL rejected by browser URL policy; no workaround used",
        "p09_p11_boundary": "not-started",
    }
    _write_json(EVIDENCE_DIR / "output-motion-manifest.json", manifest)
    hashes = {str(path.relative_to(EVIDENCE_DIR)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(EVIDENCE_DIR.iterdir()) if path.is_file() and path.name not in {"artifact-hashes.json", "P-08-EVIDENCE.md"}}
    _write_json(EVIDENCE_DIR / "artifact-hashes.json", hashes)


if __name__ == "__main__":
    generate()
