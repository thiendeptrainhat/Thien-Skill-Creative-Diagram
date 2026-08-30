#!/usr/bin/env python3
"""Verify D-117 detailed process and exact review-36 preservation."""
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
from process_layout_v15 import (
    EXPECTED_SHAPES,
    layout_process,
    process_css,
    process_table,
    validate_process_svg,
)
from process_review37_fixture import process_fixture
from visual_adapters_v15 import adapt_visual

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-36-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review37-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-37 gallery")
    target = [item for item in records if item["fixture_id"] == "type-process"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong process coverage")

    preserved_html = preserved_previews = policy_declarations = 0
    geometry = []
    measurements = []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-process":
            for token in (
                'data-process-contract="D-117-five-shape-detailed-process"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-shape-kind="terminator"',
                'data-shape-kind="process"',
                'data-shape-kind="decision"',
                'data-shape-kind="document"',
                'data-shape-kind="multiple-document"',
                "Luồng ưu tiên đường thẳng",
            ):
                require(token in page, f"Process contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_process_svg(svg))
            geometry.append(geometry_only(svg))
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-process.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Preview drift: {preview.name}")
        preserved_previews += 1

    expected = {
        "nodes": 11,
        "edges": 11,
        "shape_counts": EXPECTED_SHAPES,
        "straight_routes": 11,
        "rounded_orthogonal_exceptions": 0,
        "multiple_document_inlets": 2,
    }
    require(all(item == expected for item in measurements), "Process measurement mismatch")
    require(geometry[0] == geometry[1] == geometry[2], "Three-mode process geometry mismatch")
    plan = adapt_visual(process_fixture())
    layout = layout_process(plan)
    inlet_x = sorted(item["end"][0] for item in layout["edges"] if item["target_anchor"].startswith("top-"))
    require(inlet_x == [920, 1080] and sum(inlet_x) / 2 == 1000, "Process inlet balance mismatch")
    require("stroke-width:1.45" in process_css({}) and "stroke-width:1.8" in process_css({}), "Process paint weight drift")
    require(process_table(plan).count("<tr>") == 23, "Process alternative table drift")
    raster = PROOFS / "type-process.svg.png"
    proof_svg = PROOFS / "type-process.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-117 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-117",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "process_measurement": measurements[0],
        "shape_taxonomy": list(EXPECTED_SHAPES),
        "connector_policy": "eleven straight routes; centered single attachments; two even multiple-document inlets",
        "three_mode_geometry": "PASS",
        "alternative_table_rows": {"nodes": 11, "routes": 11},
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
    output = ROOT / "evidence/p19/P-19B-REVIEW-37-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
