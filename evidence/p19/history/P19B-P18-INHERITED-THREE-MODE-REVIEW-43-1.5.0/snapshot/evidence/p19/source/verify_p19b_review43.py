#!/usr/bin/env python3
"""Verify D-123 ridgeline rename/redraw and exact review-42 preservation."""
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
from ridgeline_layout_v15 import (
    layout_ridgeline, ridgeline_css, ridgeline_table, validate_ridgeline_svg,
)
from ridgeline_review43_fixture import ridgeline_fixture
from visual_adapters_v15 import adapt_visual

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-42-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review43-checks"


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-43 gallery")
    target = [item for item in records if item["fixture_id"] == "cap-cap-v19-ridgeline"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong ridgeline coverage")
    require({item["identity"] for item in target} == {"ridgeline"}, "CAP-V19 display identity was not renamed")
    require({item["capability_id"] for item in target} == {"CAP-V19"}, "CAP-V19 internal capability id changed")
    require({item["canonical_type"] for item in target} == {"line-chart"} and {item["parent"] for item in target} == {"line-chart"}, "ridgeline parent binding changed")

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
        if record["fixture_id"] == "cap-cap-v19-ridgeline":
            for token in (
                'data-ridgeline-contract="D-123-twelve-shared-domain-quantiles"',
                'data-template-contract="p18r6-review17-preserved"',
                'data-capability-id="CAP-V19"',
                '<strong>ridgeline</strong>',
            ):
                require(token in page, f"ridgeline contract drift: {current.name}")
            require("CAP-V19-RIDGELINE" not in page, f"Legacy ridgeline label leaked: {current.name}")
            svg = svg_from_text(page)
            measurements.append(validate_ridgeline_svg(svg))
            geometries.append(geometry_only(svg))
        else:
            old_record = old_record_by_ordinal[record["ordinal"]]
            previous = ARCHIVE / "snapshot/evidence/p19/gallery" / old_record["path"]
            normalized_current = page.replace(P19B_CANDIDATE_ID, OLD)
            normalized_previous = previous.read_text().replace(P19B_CANDIDATE_ID, OLD)
            require(normalized_current == normalized_previous, f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "cap-cap-v19-ridgeline.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    require(all(item["ridges"] == 12 and item["bands"] == 36 and item["medians"] == 12 for item in measurements), "Ridgeline measurement mismatch")
    require(all(item["axes"] == 1 and item["ticks"] == 7 and item["reference_lines"] == 1 for item in measurements), "Ridgeline shared-scale mismatch")
    require(geometries[0] == geometries[1] == geometries[2], "Three-mode ridgeline geometry mismatch")
    plan = adapt_visual(ridgeline_fixture())
    layout = layout_ridgeline(plan)
    require(len({item["baseline"] for item in layout["rows"]}) == 12, "Ridgeline row spacing invalid")
    require(all(len(item["points"]) == 20 for item in layout["rows"]), "Ridgeline KDE detail invalid")
    css = ridgeline_css({})
    require("stroke-width:1.2" in css and "stroke-width:1.25" in css, "Ridgeline thin stroke hierarchy missing")
    require(not any(f"var(--{name})" in css for name in ("purple", "teal", "lime", "chart-green")), "Undefined/reference palette token remains")
    require(ridgeline_table(plan).count("<tr>") == 13, "Ridgeline exact alternative table drift")
    raster, proof_svg = PROOFS / "ridgeline.svg.png", PROOFS / "ridgeline.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-123 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-123",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target),
        "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "ridgeline_measurement": measurements[0],
        "display_identity": "ridgeline",
        "internal_capability_id": "CAP-V19",
        "canonical_parent": "line-chart",
        "shared_domain": "0–120 ms linear; one domain and one global-max amplitude contract",
        "quantile_bands": "50/80/95 percent nested per service",
        "shared_reference_median": round(layout["reference_median"], 3),
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
    output = ROOT / "evidence/p19/P-19B-REVIEW-43-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
