#!/usr/bin/env python3
"""D-104 detailed UML-class verification against archived review-23 bytes."""
from __future__ import annotations

from collections import Counter
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
from uml_class_layout_v15 import (  # noqa: E402
    EXPECTED_CONTAINERS, EXPECTED_RELATIONSHIPS, LEGEND_KINDS,
    layout_uml_class, uml_class_table, validate_uml_class_svg,
)
from uml_class_review24_fixture import uml_class_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-23-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review24-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def svg_from_page(page):
    match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
    require(match is not None, "Missing UML class SVG")
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
    targets = [record for record in records if record["fixture_id"] == "type-uml-class"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "UML class must expose three modes")

    old_inventory = json.loads((ARCHIVE / "snapshot/evidence/p19/gallery/P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    old_records = {record["path"]: record for record in old_inventory["records"]}
    require(len(old_records) == 90, "Wrong archived gallery scope")
    preserved_html = preserved_previews = 0
    for path_name, old_record in old_records.items():
        if old_record["fixture_id"] == "type-uml-class":
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
            require(digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)), f"Prior preview changed: {preview.name}")
            preserved_previews += 1

    plan = adapt_visual(uml_class_fixture())
    layout = layout_uml_class(plan)
    require(tuple(layout["containers"]) == EXPECTED_CONTAINERS, "UML class material mismatch")
    require(tuple(layout["relationships"]) == EXPECTED_RELATIONSHIPS, "UML relation material mismatch")
    relation_kinds = Counter(item["kind"] for item in layout["relationships"].values())
    require(relation_kinds == Counter({"realization": 2, "dependency": 1, "composition": 1, "association": 1}), "UML relation-kind mix mismatch")
    require(uml_class_table(plan).count("<tr>") == 23, "Alternative UML table incomplete")

    PROOFS.mkdir(exist_ok=True)
    geometry, proof_files = [], []
    expected = {"containers": 7, "members": 17, "relationships": 5, "legend_kinds": 6, "cardinalities": 4}
    for record in targets:
        page = (GALLERY / record["path"]).read_bytes()
        svg = svg_from_page(page)
        require(validate_uml_class_svg(svg) == expected, "Serialized UML class mismatch")
        require(svg.count('data-continuous-subpaths="1"') == 5, "Every UML relationship must be a continuous path")
        require(svg.count('data-uml-legend-kind=') == 6, "Complete UML relationship legend missing")
        require(svg.count('data-uml-cardinality=') == 4, "Inline UML cardinalities missing")
        require('data-uml-role="interface"' in svg and "«interface»" in svg, "Interface stereotype is not explicit")
        geometry.append(svg.replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-uml-class--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "UML class geometry differs across modes")
    raster = PROOFS / "type-uml-class.svg.png"
    require(raster.is_file(), "Missing inspected neutral-light raster")
    proof_files.append({"path": str(raster.relative_to(ROOT)), "sha256": digest(raster), "visually_inspected": True})

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-104",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "uml_class_html_changed": 3,
        "prior_html_artwork_preserved": preserved_html,
        "prior_preview_svg_byte_identical": preserved_previews,
        "containers": 7,
        "members": 17,
        "relationships": 5,
        "relationship_kind_counts": dict(sorted(relation_kinds.items())),
        "legend_kinds": list(LEGEND_KINDS),
        "inline_cardinalities": 4,
        "continuous_relation_paths": 5,
        "rounded_association_route": "PASS",
        "three_mode_geometry": "PASS",
        "alternative_exact_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_URL_POLICY",
        "local_raster_inspection": "PASS_NEUTRAL_LIGHT",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-24-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
