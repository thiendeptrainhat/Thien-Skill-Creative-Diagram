#!/usr/bin/env python3
"""Generate the P-19B exact 129-specimen three-mode QA gallery."""

from __future__ import annotations

from html import escape
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
TEST_DIR = SCRIPT_DIR / "tests"
for path in (SCRIPT_DIR, TEST_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from diagram_core import CANONICAL_TYPES, canonical_json  # noqa: E402
from gallery_renderer_v15 import (  # noqa: E402
    MODES,
    P18_PARENT_CANDIDATE_ID,
    P18_PARENT_MANIFEST_SHA256,
    P19B_CANDIDATE_ID,
    render_gallery_html,
    renderer_inventory,
)
from semantic_fixtures import fixtures, variant_fixtures  # noqa: E402
from visual_adapters_v15 import P19A_CAPABILITIES, adapt_visual  # noqa: E402


GALLERY = ROOT / "evidence/p19/gallery"
SPECIMENS = GALLERY / "specimens"
PREVIEWS = GALLERY / "previews"
INVENTORY_PATH = GALLERY / "P-19B-INVENTORY.json"
MANIFEST_PATH = GALLERY / "P-19B-MANIFEST.json"
RENDERER_REFERENCE = ROOT / "thien-skill-creative-diagram/references/gallery-renderer-v15.json"

CAPABILITY_NAMES = {
    "CAP-V17": "dumbbell",
    "CAP-V18": "slopegraph",
    "CAP-V19": "ridgeline",
    "CAP-V20": "bubble",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def specimen_sources() -> list[tuple[str, str, dict]]:
    canonical = fixtures()
    variants = variant_fixtures()
    values = [(f"type-{diagram_type}", diagram_type, canonical[diagram_type]) for diagram_type in CANONICAL_TYPES]
    values.extend((f"cap-{capability.lower()}-{CAPABILITY_NAMES[capability]}", capability, variants[capability]) for capability in P19A_CAPABILITIES)
    return values


def build_index(records: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for record in records:
        grouped.setdefault(record["identity"], []).append(record)
    cards = []
    for index, (identity, items) in enumerate(grouped.items(), 1):
        light = next(item for item in items if item["mode"] == "neutral-light")
        links = "".join(f'<a href="{escape(item["path"])}">{escape(item["mode"])}</a>' for item in items)
        preview_path = f'previews/{escape(light["fixture_id"])}.svg'
        cards.append(
            f'<article class="card"><div class="preview"><img src="{preview_path}" alt="Preview {escape(identity)} · neutral-light"></div>'
            f'<div class="meta"><span>{index:02d}</span><div><h2>{escape(identity)}</h2><p>{escape(light["layout_engine"])} · {escape(light["silhouette"])}</p></div></div><nav aria-label="Modes for {escape(identity)}">{links}</nav></article>'
        )
    return f'''<!doctype html><html lang="vi" data-candidate-id="{P19B_CANDIDATE_ID}" data-visual-parent-candidate="{P18_PARENT_CANDIDATE_ID}" data-visual-parent-manifest-sha256="{P18_PARENT_MANIFEST_SHA256}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-19B · P-18 inherited exact 129 HTML gallery</title><style>
    :root{{--paper:#eeece7;--canvas:#f7f6f2;--surface:#ffffff;--ink:#252b3c;--muted:#687286;--line:#c7ccd2;--accent:#f26a32;--accent-soft:#f8e7dd}}*{{box-sizing:border-box}}html,body{{margin:0;background:var(--paper);color:var(--ink)}}body{{font-family:'Avenir Next',Avenir,'Segoe UI',sans-serif;padding:48px 24px 80px}}main{{width:min(100%,1680px);margin:auto}}.eyebrow{{margin:0 0 8px;color:var(--accent);font:700 13px Menlo,Monaco,monospace;letter-spacing:.16em}}h1{{margin:0;font:400 clamp(40px,6vw,70px)/1.04 Georgia,'Times New Roman',serif}}.lede{{max-width:940px;margin:14px 0 30px;color:var(--muted);font-size:17px;line-height:1.6}}.counts{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px}}.counts span{{border:1px solid var(--line);border-radius:7px;padding:7px 10px;background:#ffffff8a;font:12px Menlo,Monaco,monospace}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.card{{min-width:0;border:1px solid var(--line);border-radius:18px;background:var(--surface);overflow:hidden;box-shadow:0 16px 42px #2d344312}}.preview{{aspect-ratio:16/10;border-bottom:1px solid var(--line);background:var(--canvas);overflow:hidden}}.preview img{{display:block;width:100%;height:100%;object-fit:contain}}.meta{{display:grid;grid-template-columns:38px 1fr;gap:12px;padding:15px 16px 8px}}.meta>span{{display:grid;place-items:center;width:34px;height:34px;border-radius:7px;background:var(--accent-soft);color:#df5522;font:700 12px Menlo,Monaco,monospace}}h2{{margin:0;font-size:18px}}.meta p{{margin:4px 0 0;color:var(--muted);font:12px Menlo,Monaco,monospace;overflow-wrap:anywhere}}nav{{display:flex;flex-wrap:wrap;gap:8px;padding:8px 16px 16px}}nav a{{color:#df5522;font:700 12px Menlo,Monaco,monospace}}a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}@media(max-width:1050px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:650px){{body{{padding:24px 12px 48px}}.grid{{grid-template-columns:1fr}}}}
    </style></head><body><main><p class="eyebrow">P‑19B · P18 REVIEW‑17 INHERITED · QA CONTACT SHEET</p><h1>43 silhouettes × 3 modes.</h1><p class="lede">Exact 129 standalone HTML specimens derived from validated semantic fixtures and the owner-approved P‑18 review‑17 visual grammar. This navigation/contact sheet is not counted as a specimen. P‑19C full QA/freeze remains outside this candidate; owner visual approval of this remediation is pending.</p><div class="counts" aria-label="Gallery counts"><span>39 canonical</span><span>4 capabilities</span><span>3 modes</span><span>129 specimens</span><span>14 engines</span><span>P‑18 review‑17 lineage</span></div><section class="grid">{''.join(cards)}</section></main></body></html>'''


def main() -> None:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    sources = specimen_sources()
    if len(sources) != 43:
        raise RuntimeError("P-19B requires exactly 39 canonical fixtures plus four capability fixtures")

    records = []
    ordinal = 0
    for fixture_id, identity, ir in sources:
        plan = adapt_visual(ir)
        for mode in MODES:
            ordinal += 1
            filename = f"{ordinal:03d}-{fixture_id}--{mode}.html"
            path = SPECIMENS / filename
            path.write_text(render_gallery_html(ir, mode, fixture_id), encoding="utf-8")
            records.append({
                "ordinal": ordinal,
                "fixture_id": fixture_id,
                "identity": identity,
                "canonical_type": plan["adapter"]["canonical_type"],
                "capability_id": plan["adapter"]["capability_id"],
                "parent": plan["adapter"]["canonical_type"] if plan["adapter"]["capability_id"] else None,
                "mode": mode,
                "layout_engine": plan["adapter"]["layout_engine"],
                "silhouette": plan["adapter"]["silhouette"],
                "source_ir_sha256": plan["source_ir_sha256"],
                "path": f"specimens/{filename}",
                "sha256": sha256(path),
                "automated_check_disposition": "p19b-static-and-browser-planned",
            })

    if ordinal != 129:
        raise RuntimeError("P-19B generation did not produce exactly 129 specimens")
    existing = sorted(path.name for path in SPECIMENS.glob("*.html"))
    expected = sorted(Path(record["path"]).name for record in records)
    if existing != expected:
        raise RuntimeError("P-19B specimen directory contains stale or missing HTML files")

    for record in records:
        if record["mode"] != "neutral-light":
            continue
        source = (GALLERY / record["path"]).read_text(encoding="utf-8")
        css = source[source.index("<style>") + 7:source.index("</style>")]
        svg = source[source.index("<svg "):source.index("</svg>") + 6]
        svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        svg = svg.replace("><title", f"><style>{css}</style><title", 1)
        (PREVIEWS / f'{record["fixture_id"]}.svg').write_text(svg, encoding="utf-8")
    preview_files = sorted(PREVIEWS.glob("*.svg"))
    if len(preview_files) != 43:
        raise RuntimeError("P-19B contact sheet requires exactly 43 neutral-light SVG previews")

    aggregate = hashlib.sha256(canonical_json(records).encode("utf-8")).hexdigest()
    inventory = {
        "schema_version": "1.0",
        "candidate_id": P19B_CANDIDATE_ID,
        "phase": "P-19B",
        "scope": "QA-only source/gallery; non-package",
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "canonical_type_count": 39,
        "capability_count": 4,
        "mode_count": 3,
        "specimen_html_count": len(records),
        "index_html_count": 1,
        "layout_engine_count": len({record["layout_engine"] for record in records}),
        "aggregate_records_sha256": aggregate,
        "records": records,
        "boundary": {
            "p19c_full_qa_freeze_owner_review": "not-performed",
            "g04_1_5_0": "NOT-EVALUATED",
            "package_build": False,
            "dist_mutation": False,
            "publication_mutation": False,
            "git_release_mutation": False,
        },
    }
    write_json(INVENTORY_PATH, inventory)
    write_json(RENDERER_REFERENCE, renderer_inventory())
    (GALLERY / "index.html").write_text(build_index(records), encoding="utf-8")

    manifest_records = []
    for path in sorted((*SPECIMENS.glob("*.html"), *PREVIEWS.glob("*.svg"), GALLERY / "index.html", INVENTORY_PATH, RENDERER_REFERENCE)):
        manifest_records.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json(MANIFEST_PATH, {
        "schema_version": "1.0",
        "candidate_id": P19B_CANDIDATE_ID,
        "record_count": len(manifest_records),
        "records": manifest_records,
        "note": "P-19B D-081 containment/continuous-connector remediation inheriting P-18R6 review-17; owner visual approval and P-19C are not performed.",
    })

    print(json.dumps({
        "candidate_id": P19B_CANDIDATE_ID,
        "specimen_html_count": len(records),
        "gallery_html_count_including_index": len(records) + 1,
        "inventory_sha256": sha256(INVENTORY_PATH),
        "manifest_sha256": sha256(MANIFEST_PATH),
        "aggregate_records_sha256": aggregate,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
