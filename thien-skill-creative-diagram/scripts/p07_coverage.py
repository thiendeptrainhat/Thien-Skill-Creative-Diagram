"""Canonical P-07 visual/import coverage dispositions.

This supplements the locked P-05 inventory and does not claim P-08 export or
motion implementation.
"""

from __future__ import annotations

from typing import Any

from semantic_catalog import CAPABILITY_MAP, SPECIMEN_GROUPS, expected_capability_ids


def _disposition(capability_id: str, item: dict[str, Any]) -> tuple[str, str, str]:
    prefix = capability_id[4]
    if prefix == "T":
        return "implemented-static-visual-3-mode", "T-P07-27X3-VISUAL", "P-07 static SVG coverage"
    if prefix == "V":
        if capability_id == "CAP-V15":
            return "text-equivalent-fallback", "T-P07-16-VARIANTS", "symbol asset remains deferred to P-09"
        return "implemented-static-variant-smoke", "T-P07-16-VARIANTS", "P-07 presentation or semantic variant coverage"
    if prefix == "P":
        return "implemented-parent-pattern-smoke", "T-P07-7-PATTERNS", "rendered under the existing canonical parent"
    if prefix == "I":
        if capability_id == "CAP-I12":
            return "integrated-fidelity-reconciliation", "T-P07-FIDELITY", "P-04 invariant integrated into P-07 imports"
        return "implemented-safe-import", f"T-P07-{capability_id}-IMPORT", "bounded inert P-07 parser/redraw path"
    if prefix == "O":
        return "static-coverage-smoke", "T-P07-P08-BOUNDARY", "production export remains deferred to P-08"
    if prefix == "M":
        return "complete-static-fallback-smoke", "T-P07-P08-BOUNDARY", "motion remains deferred to P-08"
    if prefix == "F":
        if capability_id in {f"CAP-F{i:02d}" for i in range(1, 7)}:
            return "implemented-safe-failure", f"T-P07-{capability_id}-FAIL", "P-07 named non-destructive failure"
        if capability_id in {"CAP-F13", "CAP-F14"}:
            return "integrated-existing-failure-contract", "T-P07-REGRESSION", "existing P-04/P-05 behavior retained"
        return "static-fallback-evidenced", "T-P07-P08-BOUNDARY", "production exporter or motion failure remains deferred to P-08"
    raise AssertionError(f"Unknown capability class: {item}")


def build_p07_coverage() -> dict[str, dict[str, Any]]:
    if set(CAPABILITY_MAP) != expected_capability_ids():
        raise AssertionError("P-05 capability inventory drifted")
    coverage: dict[str, dict[str, Any]] = {}
    for capability_id, item in CAPABILITY_MAP.items():
        disposition, test_id, boundary = _disposition(capability_id, item)
        coverage[capability_id] = {
            "class": item["class"],
            "parents": item["parents"],
            "phase_owner": item["phase_owner"],
            "p07_disposition": disposition,
            "visual_or_import_evidence": test_id,
            "boundary": boundary,
        }
    return coverage


P07_COVERAGE = build_p07_coverage()
SPECIMEN_TOTAL = sum(group["count"] for group in SPECIMEN_GROUPS)


__all__ = ["P07_COVERAGE", "SPECIMEN_TOTAL", "build_p07_coverage"]
