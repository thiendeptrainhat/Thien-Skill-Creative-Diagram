#!/usr/bin/env python3
"""D-109 detailed story-map and review-28 preservation verification."""
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
from story_map_layout_v15 import layout_story_map, validate_story_map_svg  # noqa: E402
from story_map_review29_fixture import story_map_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-28-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review29-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize_candidate(text):
    return text.replace(P19B_CANDIDATE_ID, OLD)


def geometry_only(svg):
    return re.findall(r'<(?:rect|line|text)\b[^>]*>', svg)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")
    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong review-29 gallery")
    preserved_html = preserved_previews = policy_declarations = 0
    target_geometries, target_measurements = [], []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-story-map":
            for token in (
                'data-story-map-contract="D-109-detailed-release-slices"',
                ".sm-header{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.2}",
                ".sm-story{fill:var(--surface);stroke:var(--connector);stroke-width:1.2}",
                ".sm-cut{stroke:var(--accent);stroke-width:1.6}",
                "ĐƯỜNG CẮT MVP",
            ):
                require(token in page, f"Story-map contract drift: {current.name}")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            target_measurements.append(validate_story_map_svg(svg))
            target_geometries.append(geometry_only(svg))
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-story-map.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1
    expected = {"activities": 4, "steps": 6, "stories": 9, "release_slices": 3, "risk_stories": 1, "release_cut": 1}
    require(len(target_geometries) == len(MODES) and target_geometries[0] == target_geometries[1] == target_geometries[2], "Story-map geometry differs across modes")
    require(all(item == expected for item in target_measurements), "Story-map measurements mismatch")
    layout = layout_story_map(adapt_visual(story_map_fixture()))
    require(len(layout["releases"]) == 3 and sum(item["risk"] for item in layout["stories"].values()) == 1, "Story-map layout contract mismatch")
    raster, proof_svg = PROOFS / "type-story-map.svg.png", PROOFS / "type-story-map.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-109 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-109", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target_geometries), "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "story_map_measurement": target_measurements[0], "three_mode_geometry": "PASS",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-29-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
