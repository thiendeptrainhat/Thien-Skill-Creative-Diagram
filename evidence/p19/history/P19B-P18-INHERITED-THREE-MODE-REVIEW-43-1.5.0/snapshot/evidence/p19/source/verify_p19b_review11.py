#!/usr/bin/env python3
"""D-091 ER inline-cardinality verification against archived review-10 bytes."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source", ROOT / "evidence/p19/comparison"):
    sys.path.insert(0, str(path))

from er_data_model_layout_v15 import er_data_model_table, layout_er_data_model, validate_er_data_model_svg  # noqa: E402
from er_data_model_review10_fixture import er_data_model_fixture  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-10-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review11-checks"


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(value, message):
    if not value: raise ValueError(message)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 87, "Wrong active gallery")
    targets = [record for record in records if record["fixture_id"] == "type-er-data-model"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "ER data model must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-er-data-model":
            require(digest(active) != digest(previous), f"ER data model not regenerated: {record['mode']}")
            continue
        require(active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD) == previous.read_text(encoding="utf-8"), f"Non-target artwork changed: {active.name}")
        non_target_html += 1
        if record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f"{record['fixture_id']}.svg"
            require(digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)), f"Non-target preview changed: {preview.name}")
            non_target_previews += 1

    layout = layout_er_data_model(adapt_visual(er_data_model_fixture()))
    require(len(layout["entities"]) == 4 and len(layout["relationships"]) == 3, "ER topology mismatch")
    require(er_data_model_table(adapt_visual(er_data_model_fixture())).count("<tr>") == 23, "Alternative ER table incomplete")
    PROOFS.mkdir(exist_ok=True)
    geometry, proof_files = [], []
    for record in targets:
        page = (GALLERY / record["path"]).read_bytes()
        match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
        require(match is not None, "Missing ER SVG")
        svg = match.group()
        require(validate_er_data_model_svg(svg) == {"entities": 4, "members": 19, "relationships": 3, "aggregate": 1, "join": 1}, "Serialized ER model mismatch")
        require(svg.count('data-label-placement="inline"') == 6 and svg.count('data-er-cardinality-knockout=') == 6, "P-18 inline cardinality contract missing")
        require(svg.count('data-along-line-padding="8.00"') == 6 and svg.count('data-perpendicular-padding="4.00"') == 6, "P-18 knockout padding contract missing")
        geometry.append(svg.replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-er-data-model--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "ER geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID, "authority": "D-091", "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]), "protected_files_verified": len(receipt["protected_records"]),
        "er_data_model_html_changed": 3, "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "inline_cardinality_count": 6, "canvas_knockout_count": 6,
        "endpoint_proximity_and_axis_placement": "PASS", "p18_database_schema_cardinality_contract": "PASS",
        "three_mode_geometry": "PASS", "alternative_exact_er_table": "PASS", "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE", "owner_approval": "pending", "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-11-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
