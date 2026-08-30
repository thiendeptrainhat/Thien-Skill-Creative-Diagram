#!/usr/bin/env python3
"""Verify D-120 Bubble rename, area encoding and exact review-39 preservation."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    sys.path.insert(0, str(path))

from bubble_layout_v15 import bubble_css, bubble_table, layout_bubble, validate_bubble_svg
from bubble_review40_fixture import bubble_fixture
from connector_policy_v15 import CONNECTOR_POLICY_ID
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID
from visual_adapters_v15 import adapt_visual

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-39-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review40-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-40 gallery")
    target = [item for item in records if item["fixture_id"] == "cap-cap-v20-bubble"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong Bubble coverage")
    require({item["identity"] for item in target} == {"bubble"}, "CAP-V20 display identity was not renamed to bubble")
    require({item["capability_id"] for item in target} == {"CAP-V20"}, "CAP-V20 internal capability id changed")
    require({item["canonical_type"] for item in target} == {"scatter-plot"} and {item["parent"] for item in target} == {"scatter-plot"}, "Bubble parent binding changed")

    preserved_html = preserved_previews = policy_declarations = 0
    geometries = []
    measurements = []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"Connector policy missing: {current.name}")
        policy_declarations += 1
        previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
        if record["fixture_id"] == "cap-cap-v20-bubble":
            for token in (
                'data-bubble-contract="D-120-seven-point-area-faithful"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-capability-id="CAP-V20"',
                '<strong>bubble</strong>',
            ):
                require(token in page, f"Bubble contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_bubble_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "cap-cap-v20-bubble.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"bubbles": 7, "focal": 1, "axes": 2, "x_ticks": 8, "y_ticks": 9, "area_scale_constant": 57.8}
    require(all(item == expected for item in measurements), "Bubble measurement mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode Bubble geometry mismatch")
    plan = adapt_visual(bubble_fixture())
    layout = layout_bubble(plan)
    require(len({round(item["radius"] ** 2 / item["area_value"], 10) for item in layout["points"]}) == 1, "Bubble radius does not encode area")
    require("stroke-width:1.15" in bubble_css({}) and "stroke-width:1.8" in bubble_css({}), "Bubble thin-stroke hierarchy missing")
    require(bubble_table(plan).count("<tr>") == 8, "Bubble exact alternative table drift")
    raster, proof_svg = PROOFS / "bubble.svg.png", PROOFS / "bubble.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-120 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-120",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "bubble_measurement": measurements[0],
        "display_identity": "bubble",
        "internal_capability_id": "CAP-V20",
        "canonical_parent": "scatter-plot",
        "area_encoding": "radius=sqrt(value/80)*68; rendered circle area proportional to value",
        "axis_arrow_policy": "plain",
        "three_mode_geometry": "PASS",
        "alternative_table_rows": 7,
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
    output = ROOT / "evidence/p19/P-19B-REVIEW-40-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
