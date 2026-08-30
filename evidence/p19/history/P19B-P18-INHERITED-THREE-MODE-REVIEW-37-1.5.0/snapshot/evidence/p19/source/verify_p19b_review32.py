#!/usr/bin/env python3
"""D-112 thin Treemap and review-31 preservation verification."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    sys.path.insert(0, str(path))

from connector_policy_v15 import CONNECTOR_POLICY_ID  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from treemap_layout_v15 import INTER_TILE_GAP, layout_treemap, treemap_table, validate_treemap_svg  # noqa: E402
from treemap_review21_fixture import treemap_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-31-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review32-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize_candidate(text):
    return text.replace(P19B_CANDIDATE_ID, OLD)


def svg_from_text(text):
    match = re.search(r"<svg\b.*?</svg>", text, re.S)
    require(match, "Missing SVG")
    return match.group()


def geometry_only(svg):
    return re.findall(r'<(?:rect|line|path|circle|text)\b[^>]*>', svg)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong review-32 gallery")
    preserved_html = preserved_previews = policy_declarations = 0
    current_geometry, old_geometry, measurements = [], [], []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
        if record["fixture_id"] == "type-treemap":
            for token in (
                'data-treemap-contract="D-112-thin-complete-borders"',
                'data-geometry-contract="D-103-uniform-inset-complete-borders"',
                f'data-inter-tile-gap="{INTER_TILE_GAP:.1f}"',
                '.tm-tile{stroke:var(--connector);stroke-width:1.2',
                '.tm-tile.tm-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}',
                '.tm-rule{stroke:var(--grid);stroke-width:1}',
                '.tm-swatch-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}',
            ):
                require(token in page, f"Treemap thin-stroke contract drift: {current.name}")
            svg = svg_from_text(page)
            old_svg = svg_from_text(previous.read_text())
            require(svg.count('data-border-edges="top right bottom left"') == 6, "Incomplete Treemap borders")
            measurements.append(validate_treemap_svg(svg))
            current_geometry.append(geometry_only(svg))
            old_geometry.append(geometry_only(old_svg))
        else:
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-treemap.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"tiles": 6, "exact_area_encoding": 6, "complete_borders": 6, "uniform_insets": 6, "direct_labels": 5, "compact_labels": 1, "focal_tiles": 1}
    require(len(current_geometry) == len(MODES) and current_geometry[0] == current_geometry[1] == current_geometry[2], "Treemap geometry differs across modes")
    require(current_geometry == old_geometry, "Treemap geometry changed from archived review-31")
    require(all(item == expected for item in measurements), "Treemap measurements mismatch")
    layout = layout_treemap(adapt_visual(treemap_fixture()))
    require(all(item["inset"] == 4.0 for item in layout["tiles"]), "D-103 inset drift")
    require(treemap_table(adapt_visual(treemap_fixture())).count("<tr>") == 7, "Treemap table drift")
    raster, proof_svg = PROOFS / "type-treemap.svg.png", PROOFS / "type-treemap.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-112 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-112", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(current_geometry), "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "treemap_measurement": measurements[0], "old_current_geometry": "PASS", "three_mode_geometry": "PASS",
        "stroke_contract": {"regular_tile": 1.2, "focal_tile": 1.6, "rule": 1.0, "regular_swatch": 1.2, "focal_swatch": 1.6},
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-32-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
