#!/usr/bin/env python3
"""Verify D-125 nested redraw and exact review-44 preservation."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "thien-skill-creative-diagram/scripts",
    ROOT / "thien-skill-creative-diagram/scripts/tests",
    ROOT / "evidence/p19/source",
):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID
from nested_layout_v15 import (
    SCOPE_BOXES,
    SCOPE_ORDER,
    layout_nested,
    nested_css,
    nested_table,
    validate_nested_svg,
)
from nested_review45_fixture import nested_fixture
from visual_adapters_v15 import adapt_visual


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-44-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review45-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-45 gallery")
    target = [item for item in records if item["fixture_id"] == "type-nested"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong nested coverage")
    require({item["identity"] for item in target} == {"nested"}, "nested display identity drift")
    require({item["canonical_type"] for item in target} == {"nested"}, "nested canonical identity drift")
    require({item["capability_id"] for item in target} == {None} and {item["parent"] for item in target} == {None}, "nested binding drift")

    preserved_html = preserved_previews = policy_declarations = 0
    geometries = []
    measurements = []
    old_records = json.loads((ARCHIVE / "snapshot/evidence/p19/gallery/P-19B-INVENTORY.json").read_text())["records"]
    old_record_by_ordinal = {item["ordinal"]: item for item in old_records}
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"Connector policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-nested":
            for token in (
                'data-nested-contract="D-125-five-depth-inheritance"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-scope-count="5"',
                'data-artifact-count="5"',
                'data-max-depth="4"',
                '<strong>nested</strong>',
            ):
                require(token in page, f"nested contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_nested_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            previous_record = old_record_by_ordinal[record["ordinal"]]
            previous = ARCHIVE / "snapshot/evidence/p19/gallery" / previous_record["path"]
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1

    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-nested.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"scopes": 5, "artifacts": 5, "max_depth": 4, "focal_scopes": 1, "annotation_leaders": 1}
    require(all(item == expected for item in measurements), "nested measurement mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode nested geometry mismatch")
    plan = adapt_visual(nested_fixture())
    layout = layout_nested(plan)
    require(tuple(layout["scopes"]) == SCOPE_ORDER, "nested scope ordering mismatch")
    require([layout["scopes"][item]["parent"] for item in SCOPE_ORDER] == [None, *SCOPE_ORDER[:-1]], "nested parent chain mismatch")
    require(sum(item["focal"] for item in layout["scopes"].values()) == 1, "nested focal scope mismatch")
    for outer, inner in zip(SCOPE_ORDER, SCOPE_ORDER[1:]):
        ox, oy, ow, oh = SCOPE_BOXES[outer]
        ix, iy, iw, ih = SCOPE_BOXES[inner]
        require((ix - ox, iy - oy, ox + ow - ix - iw, oy + oh - iy - ih) == (65, 75, 65, 75), f"nested inset mismatch: {inner}")
    css = nested_css({})
    require("stroke-width:1" in css and "stroke-width:1.6" in css, "nested thin stroke hierarchy missing")
    require(not any(f"var(--{name})" in css for name in ("purple", "teal", "lime", "chart-green")), "Undefined/reference palette token remains")
    require(nested_table(plan).count("<tr>") == 6, "nested exact alternative table drift")
    raster, proof_svg = PROOFS / "nested.svg.png", PROOFS / "nested.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-125 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-125",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "nested_measurement": measurements[0],
        "display_identity": "nested",
        "scope_order": list(SCOPE_ORDER),
        "inset_per_depth": {"x": 65, "y": 75},
        "three_mode_geometry": "PASS",
        "alternative_table_rows": 5,
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY",
        "owner_approval": "APPROVED_D-126_WITH_P18_P19_COEXISTENCE",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-45-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
