#!/usr/bin/env python3
"""D-086 Fishbone-only verification against archived review-05 bytes."""
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
):
    sys.path.insert(0, str(path))

from fishbone_layout_v15 import fishbone_table, layout_fishbone  # noqa: E402
from fishbone_review06_fixture import fishbone_fixture  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-05-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def verify() -> dict:
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID, "Wrong active candidate")
    require(len(records) == 87, "Gallery count changed")
    fishbone = [record for record in records if record["fixture_id"] == "type-fishbone"]
    require(len(fishbone) == 3 and {item["mode"] for item in fishbone} == set(MODES), "Fishbone must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-fishbone":
            require(digest(active) != digest(previous), f"Fishbone was not regenerated: {record['mode']}")
            continue
        require(active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD) == previous.read_text(encoding="utf-8"),
                f"Non-target artwork changed: {active.name}")
        non_target_html += 1
        if record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f"{record['fixture_id']}.svg"
            old_preview = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
            require(digest(preview) == digest(old_preview), f"Non-target preview changed: {preview.name}")
            non_target_previews += 1

    fixture = fishbone_fixture()
    plan = adapt_visual(fixture)
    layout = layout_fishbone(plan)
    categories = layout["categories"]
    causes = [member for category in categories for member in category["members"]]
    require(len(categories) == 5, "D-086 needs five cause categories")
    require(len(causes) == 10, "D-086 needs ten detailed causes")
    require([item["side"] for item in categories] == ["top", "bottom", "top", "bottom", "top"], "Categories do not alternate")
    require(layout["effect"]["label"] == "Hồ sơ xử lý trễ", "Wrong observed effect")
    for category in categories:
        sx, sy = category["start"]
        ex, ey = category["attach"]
        require(ey == layout["spine"][0][1], f"Bone misses spine: {category['id']}")
        for cause in category["members"]:
            (_, ty), (ux, uy) = cause["tick"]
            cross = (ux - sx) * (ey - sy) - (uy - sy) * (ex - sx)
            require(abs(cross) < 1e-6 and ty == uy, f"Cause tick misses bone: {cause['id']}")

    table = fishbone_table(plan)
    for item in fixture["nodes"] + fixture["groups"]:
        require(item["id"] in table, f"Alternative table omits {item['id']}")

    geometry = []
    for record in fishbone:
        page = (GALLERY / record["path"]).read_text(encoding="utf-8")
        require(page.count('data-fishbone-category=') == 5, "Serialized category count mismatch")
        require(page.count('data-fishbone-cause=') == 10, "Serialized cause count mismatch")
        require(page.count('data-fishbone-effect=') == 1, "Serialized effect count mismatch")
        svg = re.search(r"<svg\b.*?</svg>", page, re.S)
        require(svg is not None, "Missing Fishbone SVG")
        require('data-fishbone-spine="effect"' in svg.group() and 'class="bridge"' not in svg.group(), "Fishbone continuity contract failed")
        geometry.append(svg.group().replace(record["mode"], "MODE"))
    require(len(set(geometry)) == 1, "Fishbone geometry changed across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-086",
        "status": "PASS",
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "fishbone_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "fishbone_category_count": len(categories),
        "fishbone_cause_count": len(causes),
        "fishbone_effect_count": 1,
        "three_mode_geometry": "PASS",
        "bone_tick_spine_continuity": "PASS",
        "alternative_semantic_table": "PASS",
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    path = ROOT / "evidence/p19/P-19B-REVIEW-06-VERIFICATION.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
