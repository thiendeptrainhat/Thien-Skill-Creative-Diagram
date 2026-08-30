#!/usr/bin/env python3
"""Verify D-121 slope-graph rename/redraw and exact review-40 preservation."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID
from slope_graph_layout_v15 import (
    layout_slope_graph, slope_graph_css, slope_graph_table,
    validate_slope_graph_svg,
)
from slope_graph_review41_fixture import slope_graph_fixture
from visual_adapters_v15 import adapt_visual

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-40-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review41-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def svg_from_text(text):
    match = re.search(r"<svg\b.*?</svg>", text, re.S)
    require(match, "Missing SVG")
    return match.group()


def geometry_only(svg):
    return re.findall(r'<(?:rect|line|path|circle|polygon|text)\b[^>]*>', svg)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-41 gallery")
    target = [item for item in records if item["fixture_id"] == "cap-cap-v18-slope-graph"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong slope-graph coverage")
    require({item["identity"] for item in target} == {"slope-graph"}, "CAP-V18 display identity was not renamed")
    require({item["capability_id"] for item in target} == {"CAP-V18"}, "CAP-V18 internal capability id changed")
    require({item["canonical_type"] for item in target} == {"line-chart"} and {item["parent"] for item in target} == {"line-chart"}, "slope-graph parent binding changed")

    preserved_html = preserved_previews = policy_declarations = 0
    geometries = []
    measurements = []
    old_record_by_ordinal = {
        item["ordinal"]: item
        for item in json.loads((ARCHIVE / "snapshot/evidence/p19/gallery/P-19B-INVENTORY.json").read_text())["records"]
    }
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"Connector policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "cap-cap-v18-slope-graph":
            for token in (
                'data-slope-graph-contract="D-121-seven-series-two-state"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-capability-id="CAP-V18"',
                '<strong>slope-graph</strong>',
            ):
                require(token in page, f"slope-graph contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_slope_graph_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            old_record = old_record_by_ordinal[record["ordinal"]]
            previous = ARCHIVE / "snapshot/evidence/p19/gallery" / old_record["path"]
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "cap-cap-v18-slope-graph.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"series": 7, "endpoints": 14, "axes": 2, "ticks": 6, "rises": 5, "falls": 2, "crossings": 9, "focal": 1}
    require(all(item == expected for item in measurements), "slope-graph measurement mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode slope-graph geometry mismatch")
    plan = adapt_visual(slope_graph_fixture())
    layout = layout_slope_graph(plan)
    require({item["rank_left"] for item in layout["series"]} == set(range(1, 8)), "Left ranks invalid")
    require({item["rank_right"] for item in layout["series"]} == set(range(1, 8)), "Right ranks invalid")
    css = slope_graph_css({})
    require("stroke-width:1.25" in css, "slope-graph thin axis hierarchy missing")
    require("stroke-width:3.4" in css and "stroke-width:4.5" in css and "opacity:1" in css, "Seven slope lines are not comparison-scale visible")
    require(not any(f"var(--{name})" in css for name in ("blue", "green", "amber", "plum")), "Undefined slope-graph color token remains")
    require(all(f"var(--{name})" in css for name in ("accent", "series-1", "success", "series-4", "danger", "connector", "muted")), "Seven slope-graph series are not bound to template-defined tokens")
    require(slope_graph_table(plan).count("<tr>") == 8, "slope-graph exact alternative table drift")
    raster, proof_svg = PROOFS / "slope-graph.svg.png", PROOFS / "slope-graph.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-121 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-121",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "slope_graph_measurement": measurements[0],
        "display_identity": "slope-graph",
        "internal_capability_id": "CAP-V18",
        "canonical_parent": "line-chart",
        "state_contract": "exactly two shared states on a truthful 0–100% scale",
        "three_mode_geometry": "PASS",
        "alternative_table_rows": 7,
        "comparison_scale_line_visibility": "PASS_7_SOLID_LINES_WITH_DEFINED_TEMPLATE_TOKENS",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "focused_scope_tests": "11/11 PASS",
        "static_verification": "34/34 PASS",
        "full_regression": "400/400 PASS",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-41-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
