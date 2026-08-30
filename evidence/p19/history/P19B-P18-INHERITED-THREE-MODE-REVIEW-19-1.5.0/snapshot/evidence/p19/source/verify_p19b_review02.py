"""Focused D-081 geometry, unchanged-artwork and immutable-corpus verification."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/comparison"):
    sys.path.insert(0, str(path))
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID, render_gallery_html, validate_target_geometry
from semantic_fixtures import fixtures
from generate_comparison import p19_preview

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-01-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
TARGETS = {"dp-integration", "swimlane"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text())
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected artifact drift: {name}")
    current_protected = {str(p.relative_to(ROOT)) for d in ("evidence/p18", "dist", ".release-staging") for p in (ROOT/d).rglob("*") if p.is_file()}
    current_protected.update(("evidence/p19/P-19A-SOURCE-MANIFEST.json", "evidence/p19/P-19A-PLAN-MANIFEST.json"))
    require(current_protected == set(receipt["protected_records"]), "Protected inventory changed")
    records = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text())["records"]
    unchanged_html = unchanged_preview = 0
    measurements, proof_files = [], []
    proof_dir = ROOT / "evidence/p19/review02-checks"
    proof_dir.mkdir(exist_ok=True)
    for record in records:
        path = GALLERY / record["path"]
        old_path = ARCHIVE / "snapshot" / path.relative_to(ROOT)
        current = path.read_text()
        old = old_path.read_text()
        if record["canonical_type"] not in TARGETS:
            require(current.replace(P19B_CANDIDATE_ID, OLD) == old, f"Non-target HTML changed: {path}")
            unchanged_html += 1
            if record["mode"] == "neutral-light":
                preview = GALLERY / "previews" / (record["fixture_id"] + ".svg")
                require(digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)), "Non-target SVG changed")
                unchanged_preview += 1
        else:
            svg = current[current.index("<svg "):current.index("</svg>") + 6]
            result = validate_target_geometry(svg, record["canonical_type"])
            measurements.append({"type": record["canonical_type"], "mode": record["mode"], "result": result})
            # Keep exact semantic metadata/table/CSS, except new candidate identity.
            tail = current[current.index("</svg>") + 6:].replace(P19B_CANDIDATE_ID, OLD)
            require(tail == old[old.index("</svg>") + 6:], "Target semantics or accessible alternative changed")
            require(current[:current.index("<svg ")].replace(P19B_CANDIDATE_ID, OLD) == old[:old.index("<svg ")], "Target shell/style changed")
            preview = proof_dir / f'{record["fixture_id"]}--{record["mode"]}.svg'
            preview.write_bytes(p19_preview(current.encode())[0])
            proof_files.append({"path": str(preview.relative_to(ROOT)), "sha256": digest(preview), "source_html_sha256": digest(path)})
    straight = []
    for mode in MODES:
        page = render_gallery_html(fixtures()["swimlane"], mode, "type-swimlane", connector_corner_style="straight")
        svg = page[page.index("<svg "):page.index("</svg>") + 6]
        straight.append({"mode": mode, "result": validate_target_geometry(svg, "swimlane")})
        preview = proof_dir / f"type-swimlane--{mode}--straight-proof.svg"
        preview.write_bytes(p19_preview(page.encode())[0])
        proof_files.append({"path": str(preview.relative_to(ROOT)), "sha256": digest(preview), "scope": "QA-only straight override proof; not a gallery specimen"})
    require(unchanged_html == 123 and unchanged_preview == 41 and len(measurements) == 6, "Unexpected change scope")
    report = {"candidate_id": P19B_CANDIDATE_ID, "authority": "D-081", "status": "PASS",
              "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
              "archived_files_verified": len(receipt["snapshot_records"]),
              "protected_files_verified": len(receipt["protected_records"]),
              "unchanged_non_target_html_after_candidate_id_normalization": unchanged_html,
              "byte_identical_non_target_preview_svg": unchanged_preview,
              "target_measurements": measurements, "straight_override_proofs": straight,
              "proof_svg_files": proof_files, "browser": "BLOCKED_NOT_EXECUTABLE",
              "limits": "Focused serialized geometry/immutability checks, not browser, full P-19C QA or owner approval."}
    (ROOT / "evidence/p19/P-19B-REVIEW-02-VERIFICATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key not in ("target_measurements", "straight_override_proofs", "proof_svg_files")}, indent=2))


if __name__ == "__main__":
    main()
