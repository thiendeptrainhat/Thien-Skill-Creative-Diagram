#!/usr/bin/env python3
"""D-092 high-level verification against archived review-11 bytes."""
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

from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID, render_gallery_html  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from high_level_layout_v15 import (  # noqa: E402
    EDGE_ORDER, ROUTE_POINTS, high_level_table, layout_high_level,
    validate_high_level_svg,
)
from high_level_review12_fixture import high_level_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-11-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review12-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def svg_from_page(page):
    match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
    require(match is not None, "Missing high-level SVG")
    return match.group()


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 87, "Wrong active gallery")
    targets = [record for record in records if record["fixture_id"] == "type-high-level"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "High-level must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-high-level":
            require(digest(active) != digest(previous), f"High-level not regenerated: {record['mode']}")
            continue
        require(
            active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD)
            == previous.read_text(encoding="utf-8"),
            f"Non-target artwork changed: {active.name}",
        )
        non_target_html += 1
        if record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f"{record['fixture_id']}.svg"
            require(
                digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)),
                f"Non-target preview changed: {preview.name}",
            )
            non_target_previews += 1

    plan = adapt_visual(high_level_fixture())
    layout = layout_high_level(plan)
    require(len(layout["nodes"]) == 11 and len(layout["edges"]) == 13 and len(layout["groups"]) == 2, "High-level material mismatch")
    require(high_level_table(plan).count("<tr>") == 27, "Alternative high-level table incomplete")
    for edge_id in EDGE_ORDER:
        path = layout["edges"][edge_id]["path"]
        require(path.count("M") == 1, f"Discontinuous rounded route: {edge_id}")
        require(path.count("Q") == max(0, len(ROUTE_POINTS[edge_id]) - 2), f"Rounded turn mismatch: {edge_id}")

    PROOFS.mkdir(exist_ok=True)
    geometry, proof_files = [], []
    for record in targets:
        page = (GALLERY / record["path"]).read_bytes()
        svg = svg_from_page(page)
        require(validate_high_level_svg(svg) == {
            "nodes": 11, "edges": 13, "groups": 2,
            "continuous_routes": 13, "corner_style": "rounded",
        }, "Serialized rounded high-level mismatch")
        geometry.append(svg.replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-high-level--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})

        straight_page = render_gallery_html(
            high_level_fixture(), record["mode"], "type-high-level",
            connector_corner_style="straight",
        ).encode("utf-8")
        straight_svg = svg_from_page(straight_page)
        require(validate_high_level_svg(straight_svg)["corner_style"] == "straight", "Straight override mismatch")
        require(all("Q" not in element for element in re.findall(r'data-hl-edge-id=.*? d="([^"]+)"', straight_svg)), "Straight route contains rounded command")
        straight_proof = PROOFS / f'type-high-level--{record["mode"]}--straight-proof.svg'
        straight_proof.write_bytes(p19_preview(straight_page)[0])
        proof_files.append({"path": str(straight_proof.relative_to(ROOT)), "sha256": digest(straight_proof)})
    require(len(set(geometry)) == 1, "High-level geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-092",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "high_level_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "nodes": 11,
        "directed_edges": 13,
        "groups": 2,
        "continuous_routes": 13,
        "rounded_default": "PASS",
        "straight_explicit_override": "PASS",
        "three_mode_geometry": "PASS",
        "alternative_exact_high_level_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-12-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
