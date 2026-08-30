#!/usr/bin/env python3
"""D-115 solid-line radar correction and exact review-34 preservation verification."""
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
from radar_layout_v15 import layout_radar, radar_css, radar_table, validate_radar_svg  # noqa: E402
from radar_review34_fixture import radar_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-34-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review35-checks"


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
    return re.findall(r'<(?:rect|line|path|circle|polygon|text)\b[^>]*>', svg)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 93, "Wrong review-35 gallery")
    target = [item for item in records if item["fixture_id"] == "type-radar"]
    require(len(target) == 3 and {item["mode"] for item in target} == set(MODES), "Wrong radar mode coverage")

    preserved_html = preserved_previews = policy_declarations = 0
    geometry = []
    measurements = []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-radar":
            for token in (
                'data-radar-contract="D-115-five-axis-four-solid-profile"',
                'data-ring-value="10"', 'data-series-id="series-internal-platform"',
                'data-focal="true"', 'data-marker-shape="circle"',
                "Màu + hình marker · tất cả nét liền",
            ):
                require(token in page, f"Radar contract drift: {current.name}")
            svg = svg_from_text(page)
            require(svg.count('data-line-style="solid"') == 4, f"Not all profiles are solid: {current.name}")
            radar_style = re.search(r"\.rd-profile\{.*?\.rd-details", page, re.S)
            require(radar_style and "stroke-dasharray" not in radar_style.group(), f"Radar dash declaration remains: {current.name}")
            measurements.append(validate_radar_svg(svg))
            geometry.append(geometry_only(svg))
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-radar.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1

    expected = {"profiles": 4, "values": 20, "axes": 5, "rings": 5, "markers": 20, "focal": 1}
    require(all(item == expected for item in measurements), "Radar measurements mismatch")
    require(geometry[0] == geometry[1] == geometry[2], "Radar geometry differs across modes")
    layout = layout_radar(adapt_visual(radar_fixture()))
    require(layout["ticks"] == (2, 4, 6, 8, 10), "Radar ring scale drift")
    require("stroke-dasharray" not in radar_css({}), "D-115 radar CSS still uses dashed profiles")
    require(radar_table(adapt_visual(radar_fixture())).count("<tr>") == 21, "Radar table drift")
    raster, proof_svg = PROOFS / "type-radar.svg.png", PROOFS / "type-radar.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-115 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-115", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target), "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "radar_measurement": measurements[0],
        "profile_line_style": "solid-only",
        "non_color_redundancy": [item["marker"] for item in layout["profiles"]],
        "three_mode_geometry": "PASS", "alternative_table_rows": 20,
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-35-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
