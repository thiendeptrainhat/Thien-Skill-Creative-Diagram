"""Canonical P-08 output, motion, and failure coverage dispositions."""

from __future__ import annotations

from motion_catalog import MOTION_CAPABILITIES
from output_pipeline import OUTPUT_CAPABILITIES


FAILURE_CAPABILITIES = {
    "CAP-F07": {"name": "missing rasterizer", "test_id": "T-OUT-RASTER-FALLBACK", "implementation": "SVG/HTML fallback; no install"},
    "CAP-F08": {"name": "ambiguous export target", "test_id": "T-OUT-TARGET-EXACT", "implementation": "exact relative target set required"},
    "CAP-F09": {"name": "editorial export boundary", "test_id": "T-OUT-SVG-DIAGRAM-ONLY", "implementation": "standalone SVG without HTML/editorial shell"},
    "CAP-F10": {"name": "font unavailable", "test_id": "T-OUT-FONT-FALLBACK", "implementation": "local system fallback and warning"},
    "CAP-F11": {"name": "motion failure", "test_id": "T-MOT-STATIC-FALLBACK", "implementation": "script-free complete static HTML"},
    "CAP-F12": {"name": "reduced motion or print", "test_id": "T-MOT-REDUCED-PRINT", "implementation": "complete static frame via media rules"},
}


def build_p08_coverage() -> dict[str, dict[str, str]]:
    coverage: dict[str, dict[str, str]] = {}
    for capability_id, implementation in OUTPUT_CAPABILITIES.items():
        coverage[capability_id] = {"class": "output", "status": "implemented-p08", "implementation": implementation, "test_id": f"T-OUT-{capability_id}-P08"}
    for capability_id, capability in MOTION_CAPABILITIES.items():
        coverage[capability_id] = {"class": "motion", "status": "implemented-static-first-p08", "implementation": capability["name"], "test_id": capability["test_id"]}
    for capability_id, capability in FAILURE_CAPABILITIES.items():
        coverage[capability_id] = {"class": "failure", "status": "implemented-safe-failure-p08", "implementation": capability["implementation"], "test_id": capability["test_id"]}
    return dict(sorted(coverage.items()))


P08_COVERAGE = build_p08_coverage()


__all__ = ["FAILURE_CAPABILITIES", "P08_COVERAGE", "build_p08_coverage"]
