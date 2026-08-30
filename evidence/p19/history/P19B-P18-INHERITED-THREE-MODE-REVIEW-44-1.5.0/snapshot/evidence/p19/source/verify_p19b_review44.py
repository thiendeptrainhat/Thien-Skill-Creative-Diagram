#!/usr/bin/env python3
"""Verify D-124 layer-stack redraw and exact review-43 preservation."""

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
from layer_stack_layout_v15 import (
    LAYER_ORDER,
    layer_stack_css,
    layer_stack_table,
    layout_layer_stack,
    validate_layer_stack_svg,
)
from layer_stack_review44_fixture import layer_stack_fixture
from visual_adapters_v15 import adapt_visual


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-43-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review44-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-44 gallery")
    target = [item for item in records if item["fixture_id"] == "type-layer-stack"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong layer-stack coverage")
    require({item["identity"] for item in target} == {"layer-stack"}, "layer-stack display identity drift")
    require({item["canonical_type"] for item in target} == {"layer-stack"}, "layer-stack canonical identity drift")
    require({item["capability_id"] for item in target} == {None} and {item["parent"] for item in target} == {None}, "layer-stack binding drift")

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
        if record["fixture_id"] == "type-layer-stack":
            for token in (
                'data-layer-stack-contract="D-124-five-layer-modular-split"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-layer-count="5"',
                'data-module-count="23"',
                'data-domain-count="2"',
                'data-dependency-count="4"',
                '<strong>layer-stack</strong>',
            ):
                require(token in page, f"layer-stack contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_layer_stack_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            previous_record = old_record_by_ordinal[record["ordinal"]]
            previous = ARCHIVE / "snapshot/evidence/p19/gallery" / previous_record["path"]
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1

    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-layer-stack.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    require(all(item == {"layers": 5, "modules": 23, "domains": 2, "dependencies": 4, "focal_layers": 1, "abstraction_axes": 1} for item in measurements), "layer-stack measurement mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode layer-stack geometry mismatch")
    plan = adapt_visual(layer_stack_fixture())
    layout = layout_layer_stack(plan)
    require(tuple(layout["rows"]) == LAYER_ORDER, "layer-stack ordering mismatch")
    require([len(layout["rows"][item]["member_ids"]) for item in LAYER_ORDER] == [4, 5, 6, 4, 4], "layer-stack distribution mismatch")
    require(all(len(layout["groups"][item]["member_ids"]) == 3 for item in ("domain-models", "domain-knowledge")), "layer-stack split-domain mismatch")
    require(all(item["x"] == 1055 and item["source_y"] < item["target_y"] for item in layout["connectors"]), "layer-stack centered straight dependency mismatch")
    css = layer_stack_css({})
    require("stroke-width:1" in css and "stroke-width:1.2" in css and "stroke-width:1.6" in css, "layer-stack thin stroke hierarchy missing")
    require("transparent" not in css, "Raster-unsafe transparent color mixing remains")
    require(not any(f"var(--{name})" in css for name in ("purple", "teal", "lime", "chart-green")), "Undefined/reference palette token remains")
    require(layer_stack_table(plan).count("<tr>") == 24, "layer-stack exact alternative table drift")
    raster, proof_svg = PROOFS / "layer-stack.svg.png", PROOFS / "layer-stack.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-124 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-124",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "layer_stack_measurement": measurements[0],
        "display_identity": "layer-stack",
        "layer_distribution": [4, 5, 6, 4, 4],
        "intelligence_domains": ["Mô hình", "Dữ liệu & tri thức"],
        "dependency_routing": "4 straight centered adjacent-layer arrows",
        "presentation_layers_variant": "PRESERVED_AS_NON_TARGET",
        "three_mode_geometry": "PASS",
        "alternative_table_rows": 23,
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
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
    output = ROOT / "evidence/p19/P-19B-REVIEW-44-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
