"""Original P-08 static-first motion capability catalog and selector."""

from __future__ import annotations

from typing import Any, Mapping


MOTION_CAPABILITIES: dict[str, dict[str, Any]] = {
    "CAP-M01": {"name": "complete static", "mode": "none", "primary": "static", "test_id": "T-MOT-CAP-M01-STATIC"},
    "CAP-M02": {"name": "ordered reveal", "mode": "reveal", "primary": "narrative", "test_id": "T-MOT-CAP-M02-REVEAL"},
    "CAP-M03": {"name": "controlled steps", "mode": "step", "primary": "orientation", "test_id": "T-MOT-CAP-M03-STEP"},
    "CAP-M04": {"name": "decorative loop", "mode": "loop", "primary": "ambient", "test_id": "T-MOT-CAP-M04-LOOP"},
    "CAP-M05": {"name": "path emphasis", "mode": "reveal", "primary": "orientation", "requires": "edges", "test_id": "T-MOT-CAP-M05-PATH"},
    "CAP-M06": {"name": "item emphasis", "mode": "reveal", "primary": "narrative", "requires": "nodes", "test_id": "T-MOT-CAP-M06-ITEM"},
    "CAP-M07": {"name": "queue progression", "mode": "step", "primary": "data", "parents": ["data-flow"], "test_id": "T-MOT-CAP-M07-QUEUE"},
    "CAP-M08": {"name": "field progression", "mode": "step", "primary": "data", "parents": ["data-flow", "er-data-model"], "test_id": "T-MOT-CAP-M08-FIELD"},
    "CAP-M09": {"name": "policy evaluation", "mode": "step", "primary": "feedback", "parents": ["flowchart", "dp-security-matrix"], "test_id": "T-MOT-CAP-M09-POLICY"},
    "CAP-M10": {"name": "decorative flow token", "mode": "loop", "primary": "ambient", "requires": "edges", "test_id": "T-MOT-CAP-M10-TOKEN"},
    "CAP-M11": {"name": "containment emphasis", "mode": "reveal", "primary": "orientation", "requires": "groups", "test_id": "T-MOT-CAP-M11-CONTAINMENT"},
    "CAP-M12": {"name": "chronological progression", "mode": "step", "primary": "narrative", "parents": ["timeline", "sequence"], "test_id": "T-MOT-CAP-M12-AUDIT"},
}


def select_motion_capabilities(ir: Mapping[str, Any], mode: str) -> list[str]:
    """Select only capabilities whose static fallback and semantic trigger exist."""

    if mode not in {"none", "reveal", "step", "loop"}:
        raise ValueError("Unsupported motion mode")
    selected = ["CAP-M01"]
    if mode == "none":
        return selected
    selected.append({"reveal": "CAP-M02", "step": "CAP-M03", "loop": "CAP-M04"}[mode])
    diagram_type = ir["diagram"]["type"]
    for capability_id, capability in MOTION_CAPABILITIES.items():
        if capability["mode"] != mode or capability_id in selected:
            continue
        if capability.get("requires") and not ir.get(capability["requires"], []):
            continue
        if capability.get("parents") and diagram_type not in capability["parents"]:
            continue
        selected.append(capability_id)
    return selected


__all__ = ["MOTION_CAPABILITIES", "select_motion_capabilities"]
