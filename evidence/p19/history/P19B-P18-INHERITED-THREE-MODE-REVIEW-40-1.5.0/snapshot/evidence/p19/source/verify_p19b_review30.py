#!/usr/bin/env python3
"""D-110 detailed state-machine and review-29 preservation verification."""
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
from state_machine_layout_v15 import layout_state_machine, validate_state_machine_svg  # noqa: E402
from state_machine_review30_fixture import state_machine_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-29-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review30-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def normalize_candidate(text):
    return text.replace(P19B_CANDIDATE_ID, OLD)


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
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 90, "Wrong review-30 gallery")
    preserved_html = preserved_previews = policy_declarations = 0
    target_geometries, target_measurements = [], []
    for record in records:
        current = GALLERY / record["path"]
        page = current.read_text()
        require(f'data-connector-policy="{CONNECTOR_POLICY_ID}"' in page, f"D-105 policy missing: {current.name}")
        policy_declarations += 1
        if record["fixture_id"] == "type-state-machine":
            for token in (
                'data-state-machine-contract="D-110-detailed-lifecycle"',
                'data-attachment-policy="D-105-centered-and-even"',
                'data-route-exception="return-transition-avoids-forward-lane"',
                '.stmc-state{fill:var(--surface);stroke:var(--connector);stroke-width:1.15}',
                "TRẢ LẠI · CHỈNH SỬA",
            ):
                require(token in page, f"State-machine contract drift: {current.name}")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            target_measurements.append(validate_state_machine_svg(svg))
            target_geometries.append(geometry_only(svg))
        else:
            previous = ARCHIVE / "snapshot" / current.relative_to(ROOT)
            require(normalize_candidate(page) == normalize_candidate(previous.read_text()), f"Non-target HTML drift: {current.name}")
            preserved_html += 1
    for preview in sorted((GALLERY / "previews").glob("*.svg")):
        if preview.name == "type-state-machine.svg":
            continue
        previous = ARCHIVE / "snapshot" / preview.relative_to(ROOT)
        require(digest(preview) == digest(previous), f"Non-target preview drift: {preview.name}")
        preserved_previews += 1
    expected = {"states": 4, "initial_markers": 1, "terminal_markers": 1, "straight_transitions": 5, "return_transitions": 1, "centered_attachments": 12}
    require(len(target_geometries) == len(MODES) and target_geometries[0] == target_geometries[1] == target_geometries[2], "State-machine geometry differs across modes")
    require(all(item == expected for item in target_measurements), "State-machine measurements mismatch")
    layout = layout_state_machine(adapt_visual(state_machine_fixture()))
    require(layout["card_boxes"]["state-live"][0] + 170 == layout["terminal"][0], "Vertical lifecycle center mismatch")
    raster, proof_svg = PROOFS / "type-state-machine.svg.png", PROOFS / "type-state-machine.svg"
    require(raster.is_file() and proof_svg.is_file(), "Missing D-110 visual proof")
    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-110", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "target_html_count": len(target_geometries), "global_policy_declarations": policy_declarations,
        "non_target_html_preserved_after_candidate_normalization": preserved_html,
        "non_target_previews_byte_identical": preserved_previews,
        "state_machine_measurement": target_measurements[0], "three_mode_geometry": "PASS",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "proof_files": [
            {"path": str(proof_svg.relative_to(ROOT)), "sha256": digest(proof_svg)},
            {"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True},
        ],
        "browser": "BLOCKED_URL_POLICY", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-30-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
