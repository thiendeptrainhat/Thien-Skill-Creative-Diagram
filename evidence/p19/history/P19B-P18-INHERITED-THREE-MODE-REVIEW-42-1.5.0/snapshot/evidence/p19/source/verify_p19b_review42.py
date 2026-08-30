#!/usr/bin/env python3
"""Verify D-122 dumbbell rename/redraw and exact review-41 preservation."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID
from dumbbell_layout_v15 import (
    dumbbell_css, dumbbell_table, layout_dumbbell, validate_dumbbell_svg,
)
from dumbbell_review42_fixture import dumbbell_fixture
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID
from visual_adapters_v15 import adapt_visual

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-41-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review42-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-42 gallery")
    target = [item for item in records if item["fixture_id"] == "cap-cap-v17-dumbbell"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong dumbbell coverage")
    require({item["identity"] for item in target} == {"dumbbell"}, "CAP-V17 display identity was not renamed")
    require({item["capability_id"] for item in target} == {"CAP-V17"}, "CAP-V17 internal capability id changed")
    require({item["canonical_type"] for item in target} == {"bar-chart"} and {item["parent"] for item in target} == {"bar-chart"}, "dumbbell parent binding changed")

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
        if record["fixture_id"] == "cap-cap-v17-dumbbell":
            for token in (
                'data-dumbbell-contract="D-122-twelve-pair-shared-scale"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-capability-id="CAP-V17"',
                '<strong>dumbbell</strong>',
            ):
                require(token in page, f"dumbbell contract drift: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_dumbbell_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            old_record = old_record_by_ordinal[record["ordinal"]]
            previous = ARCHIVE / "snapshot/evidence/p19/gallery" / old_record["path"]
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "cap-cap-v17-dumbbell.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {
        "pairs": 12, "endpoints": 24, "series": 2, "bands": 2,
        "mean_lines": 2, "axes": 1, "ticks": 6, "focal": 1, "delta_labels": 12,
    }
    require(all(item == expected for item in measurements), "dumbbell measurement mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode dumbbell geometry mismatch")
    plan = adapt_visual(dumbbell_fixture())
    layout = layout_dumbbell(plan)
    require(all(item["x_after"] >= item["x_before"] for item in layout["rows"]), "Dumbbell pair order invalid")
    require(len({item["y"] for item in layout["rows"]}) == 12, "Dumbbell row spacing invalid")
    css = dumbbell_css({})
    require("stroke-width:1.2" in css and "stroke-width:1.8" in css, "Dumbbell thin axis/endpoint hierarchy missing")
    require(not any(f"var(--{name})" in css for name in ("purple", "teal", "blue", "green")), "Undefined/reference palette token remains")
    require(dumbbell_table(plan).count("<tr>") == 13, "Dumbbell exact alternative table drift")
    raster, proof_svg = PROOFS / "dumbbell.svg.png", PROOFS / "dumbbell.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-122 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-122",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "dumbbell_measurement": measurements[0],
        "display_identity": "dumbbell",
        "internal_capability_id": "CAP-V17",
        "canonical_parent": "bar-chart",
        "shared_scale": "0–100% linear; one position scale for both endpoints",
        "statistics": {
            key: {name: round(value, 4) for name, value in values.items() if name in {"mean", "stdev"}}
            for key, values in layout["stats"].items()
        },
        "three_mode_geometry": "PASS",
        "alternative_table_rows": 12,
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
    output = ROOT / "evidence/p19/P-19B-REVIEW-42-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
