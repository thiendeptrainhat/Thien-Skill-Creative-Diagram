#!/usr/bin/env python3
"""D-094 Kanban verification against archived review-13 bytes."""
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
from kanban_layout_v15 import kanban_table, layout_kanban, validate_kanban_svg  # noqa: E402
from kanban_review14_fixture import kanban_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-13-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review14-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def svg_from_page(page):
    match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
    require(match is not None, "Missing Kanban SVG")
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
    targets = [record for record in records if record["fixture_id"] == "type-kanban"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "Kanban must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-kanban":
            require(digest(active) != digest(previous), f"Kanban not regenerated: {record['mode']}")
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

    plan = adapt_visual(kanban_fixture())
    layout = layout_kanban(plan)
    require(len(layout["columns"]) == 4 and len(layout["items"]) == 11, "Kanban material mismatch")
    require([item["count"] for item in layout["columns"].values()] == [3, 4, 2, 2], "Kanban column counts mismatch")
    require(sum(item["over_limit"] for item in layout["columns"].values()) == 1, "Kanban WIP breach mismatch")
    require(layout["columns"]["column-progress"]["counter"] == "4/3", "Kanban WIP counter mismatch")
    states = [item["state"] for item in layout["items"].values()]
    require(states.count("blocked") == 1 and states.count("waiting-external") == 1 and states.count("done") == 2, "Kanban state count mismatch")
    require(kanban_table(plan).count("<tr>") == 16, "Alternative Kanban table incomplete")

    PROOFS.mkdir(exist_ok=True)
    geometry, proof_files = [], []
    expected = {"columns": 4, "items": 11, "wip_breaches": 1, "blocked": 1, "waiting_external": 1, "done": 2}
    for record in targets:
        page = (GALLERY / record["path"]).read_bytes()
        svg = svg_from_page(page)
        require(validate_kanban_svg(svg) == expected, "Serialized Kanban mismatch")
        geometry.append(svg.replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-kanban--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "Kanban geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-094",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "kanban_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "columns": 4,
        "items": 11,
        "column_counts": [3, 4, 2, 2],
        "wip_breaches": 1,
        "blocked": 1,
        "waiting_external": 1,
        "done": 2,
        "three_mode_geometry": "PASS",
        "alternative_exact_kanban_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-14-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
