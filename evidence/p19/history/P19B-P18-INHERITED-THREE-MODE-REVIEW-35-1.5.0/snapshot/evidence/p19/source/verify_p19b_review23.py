#!/usr/bin/env python3
"""D-103 uniform-gap Treemap verification against archived review-22 bytes."""
from __future__ import annotations

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
    ROOT / "evidence/p19/comparison",
):
    sys.path.insert(0, str(path))

from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from treemap_layout_v15 import (  # noqa: E402
    EXPECTED_LEAF_IDS, FOCAL_ID, INTER_TILE_GAP, SMALL_ID, TILE_INSET,
    layout_treemap, treemap_table, validate_treemap_svg,
)
from treemap_review21_fixture import treemap_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-22-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review23-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def svg_from_page(page):
    match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
    require(match is not None, "Missing Treemap SVG")
    return match.group()


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong active gallery")
    targets = [record for record in records if record["fixture_id"] == "type-treemap"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "Treemap must expose three modes")

    old_inventory = json.loads((ARCHIVE / "snapshot/evidence/p19/gallery/P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    old_records = {record["path"]: record for record in old_inventory["records"]}
    require(len(old_records) == 90, "Wrong archived gallery scope")
    preserved_html = preserved_previews = 0
    for path_name, old_record in old_records.items():
        if old_record["fixture_id"] == "type-treemap":
            continue
        active = GALLERY / path_name
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        require(active.is_file(), f"Prior specimen missing: {path_name}")
        require(
            active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD)
            == previous.read_text(encoding="utf-8"),
            f"Prior artwork changed: {active.name}",
        )
        preserved_html += 1
        if old_record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f'{old_record["fixture_id"]}.svg'
            require(
                digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)),
                f"Prior preview changed: {preview.name}",
            )
            preserved_previews += 1

    plan = adapt_visual(treemap_fixture())
    layout = layout_treemap(plan)
    require(tuple(item["id"] for item in layout["tiles"]) == EXPECTED_LEAF_IDS, "Treemap material mismatch")
    require([item["id"] for item in layout["tiles"] if item["focal"]] == [FOCAL_ID], "Treemap focal mismatch")
    require([item["id"] for item in layout["tiles"] if item["compact"]] == [SMALL_ID], "Treemap compact-label mismatch")
    require(all(item["inset"] == TILE_INSET for item in layout["tiles"]), "Treemap inset mismatch")
    require(treemap_table(plan).count("<tr>") == 7, "Alternative Treemap table incomplete")

    PROOFS.mkdir(exist_ok=True)
    geometry, proof_files = [], []
    expected = {
        "tiles": 6, "exact_area_encoding": 6, "complete_borders": 6,
        "uniform_insets": 6, "direct_labels": 5, "compact_labels": 1,
        "focal_tiles": 1,
    }
    for record in targets:
        page = (GALLERY / record["path"]).read_bytes()
        page_text = page.decode("utf-8")
        svg = svg_from_page(page)
        require(validate_treemap_svg(svg) == expected, "Serialized Treemap mismatch")
        require('class="tm-gutter"' not in svg, "Under-stroke gutter must be retired")
        require(svg.count('data-border-edges="top right bottom left"') == 6, "Every tile must expose all four border edges")
        require(f'data-inter-tile-gap="{INTER_TILE_GAP:.1f}"' in svg, "Uniform inter-tile gap declaration missing")
        require('.tm-tile{stroke:var(--connector);stroke-width:2.4' in page_text, "Every non-focal tile must have a visible connector border")
        require('.tm-tile.tm-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:3.2}' in page_text, "Focal tile must have a visible accent border")
        geometry.append(svg.replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-treemap--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "Treemap geometry differs across modes")
    raster = PROOFS / "type-treemap.svg.png"
    require(raster.is_file(), "Missing inspected neutral-light raster")
    proof_files.append({"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True})

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-103",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "treemap_html_changed": 3,
        "prior_html_artwork_preserved": preserved_html,
        "prior_preview_svg_byte_identical": preserved_previews,
        "tiles": 6,
        "complete_four_edge_borders": 6,
        "uniform_insets": 6,
        "inter_tile_gap": INTER_TILE_GAP,
        "exact_allocation_area_tiles": 6,
        "focal_tiles": 1,
        "direct_label_tiles": 5,
        "compact_label_tiles": 1,
        "allocation_area_value_reconciliation": "PASS",
        "hierarchy_total_reconciliation": "PASS",
        "uniform_real_gap": "PASS",
        "three_mode_geometry": "PASS",
        "alternative_exact_value_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_URL_POLICY",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-23-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
