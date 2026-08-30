#!/usr/bin/env python3
"""Generate 93 P-19 specimens and link 14 unchanged approved P-18 anchors."""

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
from gantt_review03_fixture import gantt_fixture
from flywheel_review04_fixture import flywheel_fixture
from fishbone_review06_fixture import fishbone_fixture
from dp_integration_review07_fixture import dp_integration_fixture
from bar_chart_review08_fixture import bar_chart_fixture
from line_chart_review16_fixture import line_chart_fixture
from dp_security_matrix_review09_fixture import dp_security_matrix_fixture
from er_data_model_review10_fixture import er_data_model_fixture
from uml_class_review24_fixture import uml_class_fixture
from high_level_review12_fixture import high_level_fixture
from it_current_state_review13_fixture import it_current_state_fixture
from kanban_review14_fixture import kanban_fixture
from layers_review15_fixture import layers_fixture
from medallion_review17_fixture import medallion_fixture
from polar_chart_review18_fixture import polar_chart_fixture
from wardley_map_review19_fixture import wardley_map_fixture
from venn_review20_fixture import venn_fixture
from treemap_review21_fixture import treemap_fixture
from tree_review26_fixture import tree_fixture
from story_map_review29_fixture import story_map_fixture
from state_machine_review30_fixture import state_machine_fixture
from sequence_review31_fixture import sequence_fixture
from scatter_chart_review33_fixture import scatter_chart_fixture
from radar_review34_fixture import radar_fixture
from process_review37_fixture import process_fixture
from dumbbell_review42_fixture import dumbbell_fixture
from bubble_review40_fixture import bubble_fixture
from slope_graph_review41_fixture import slope_graph_fixture
from p19_scope import REUSED_TYPES, p18_references
from visual_adapters_v15 import P19A_CAPABILITIES, adapt_visual  # noqa: E402


GALLERY = ROOT / "evidence/p19/gallery"
SPECIMENS = GALLERY / "specimens"
PREVIEWS = GALLERY / "previews"
INVENTORY_PATH = GALLERY / "P-19B-INVENTORY.json"
MANIFEST_PATH = GALLERY / "P-19B-MANIFEST.json"
RENDERER_REFERENCE = ROOT / "thien-skill-creative-diagram/references/gallery-renderer-v15.json"

CAPABILITY_NAMES = {
    "CAP-V17": "dumbbell",
    "CAP-V18": "slope-graph",
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
    canonical['gantt'] = gantt_fixture()
    canonical['loop-flywheel'] = flywheel_fixture()
    canonical['fishbone'] = fishbone_fixture()
    canonical['dp-integration'] = dp_integration_fixture()
    canonical['bar-chart'] = bar_chart_fixture()
    canonical['line-chart'] = line_chart_fixture()
    canonical['radar'] = radar_fixture()
    canonical['process'] = process_fixture()
    canonical['polar-chart'] = polar_chart_fixture()
    canonical['wardley-map'] = wardley_map_fixture()
    canonical['venn'] = venn_fixture()
    canonical['treemap'] = treemap_fixture()
    canonical['tree'] = tree_fixture()
    canonical['story-map'] = story_map_fixture()
    canonical['state-machine'] = state_machine_fixture()
    canonical['sequence'] = sequence_fixture()
    canonical['dp-security-matrix'] = dp_security_matrix_fixture()
    canonical['er-data-model'] = er_data_model_fixture()
    canonical['uml-class'] = uml_class_fixture()
    canonical['high-level'] = high_level_fixture()
    canonical['it-current-state'] = it_current_state_fixture()
    canonical['kanban'] = kanban_fixture()
    canonical['medallion'] = medallion_fixture()
    variants = variant_fixtures()
    variants["CAP-V17"] = dumbbell_fixture()
    values = [(f"type-{diagram_type}", diagram_type, canonical[diagram_type]) for diagram_type in CANONICAL_TYPES if diagram_type not in REUSED_TYPES]
    variants["CAP-V18"] = slope_graph_fixture()
    variants["CAP-V20"] = bubble_fixture()
    values.extend(
        (
            f"cap-{capability.lower()}-{CAPABILITY_NAMES[capability]}",
            CAPABILITY_NAMES[capability] if capability in {"CAP-V17", "CAP-V18", "CAP-V20"} else capability,
            variants[capability],
        )
        for capability in P19A_CAPABILITIES
    )
    values.append(("type-layers", "layers", layers_fixture()))
    values.append(("type-scatter-chart", "scatter-chart", scatter_chart_fixture()))
    return values


def build_index(records: list[dict]) -> str:
    approved_cards = []
    for item in p18_references():
        html_path = "../../p18/r6/" + item["html"].split("/r6/", 1)[1]
        svg_path = "../../p18/r6/" + item["svg"].split("/r6/", 1)[1]
        identity = escape(item["identity"])
        approved_cards.append(f'<article class="card" data-phase="p18"><div class="preview"><img src="{svg_path}" alt="P-18 đã duyệt · {identity}"></div><div class="meta"><span>P18</span><div><h2>{identity}</h2><p>Đã duyệt · giữ nguyên bản gốc</p></div></div><nav aria-label="Bản P-18 {identity}"><a href="{html_path}">neutral-light · P-18 gốc</a></nav></article>')
    grouped: dict[str, list[dict]] = {}
    for record in records:
        grouped.setdefault(record["identity"], []).append(record)
    cards = []
    for index, (identity, items) in enumerate(grouped.items(), 1):
        light = next(item for item in items if item["mode"] == "neutral-light")
        links = "".join(f'<a href="{escape(item["path"])}">{escape(item["mode"])}</a>' for item in items)
        preview_path = f'previews/{escape(light["fixture_id"])}.svg'
        cards.append(
            f'<article class="card" data-phase="p19"><div class="preview"><img src="{preview_path}" alt="Preview {escape(identity)} · neutral-light"></div>'
            f'<div class="meta"><span>{index:02d}</span><div><h2>{escape(identity)}</h2><p>{escape(light["layout_engine"])} · {escape(light["silhouette"])}</p></div></div><nav aria-label="Modes for {escape(identity)}">{links}</nav></article>'
        )
    return f'''<!doctype html><html lang="vi" data-candidate-id="{P19B_CANDIDATE_ID}" data-visual-parent-candidate="{P18_PARENT_CANDIDATE_ID}" data-visual-parent-manifest-sha256="{P18_PARENT_MANIFEST_SHA256}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-18 đã duyệt + P-19 bổ sung</title><style>
    :root{{--paper:#eeece7;--canvas:#f7f6f2;--surface:#ffffff;--ink:#252b3c;--muted:#687286;--line:#c7ccd2;--accent:#f26a32;--accent-soft:#f8e7dd}}*{{box-sizing:border-box}}html,body{{margin:0;background:var(--paper);color:var(--ink)}}body{{font-family:'Avenir Next',Avenir,'Segoe UI',sans-serif;padding:48px 24px 80px}}main{{width:min(100%,1680px);margin:auto}}.eyebrow{{margin:0 0 8px;color:var(--accent);font:700 13px Menlo,Monaco,monospace;letter-spacing:.16em}}h1{{margin:0;font:400 clamp(40px,6vw,70px)/1.04 Georgia,'Times New Roman',serif}}.lede{{max-width:940px;margin:14px 0 30px;color:var(--muted);font-size:17px;line-height:1.6}}.counts{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px}}.counts span{{border:1px solid var(--line);border-radius:7px;padding:7px 10px;background:#ffffff8a;font:12px Menlo,Monaco,monospace}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.card{{min-width:0;border:1px solid var(--line);border-radius:18px;background:var(--surface);overflow:hidden;box-shadow:0 16px 42px #2d344312}}.preview{{aspect-ratio:16/10;border-bottom:1px solid var(--line);background:var(--canvas);overflow:hidden}}.preview img{{display:block;width:100%;height:100%;object-fit:contain}}.meta{{display:grid;grid-template-columns:38px 1fr;gap:12px;padding:15px 16px 8px}}.meta>span{{display:grid;place-items:center;width:34px;height:34px;border-radius:7px;background:var(--accent-soft);color:#df5522;font:700 12px Menlo,Monaco,monospace}}h2{{margin:0;font-size:18px}}.meta p{{margin:4px 0 0;color:var(--muted);font:12px Menlo,Monaco,monospace;overflow-wrap:anywhere}}nav{{display:flex;flex-wrap:wrap;gap:8px;padding:8px 16px 16px}}nav a{{color:#df5522;font:700 12px Menlo,Monaco,monospace}}a:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}@media(max-width:1050px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:650px){{body{{padding:24px 12px 48px}}.grid{{grid-template-columns:1fr}}}}
    </style></head><body><main><p class="eyebrow">P‑19B · P18 REVIEW‑17 INHERITED · QA CONTACT SHEET</p><h1>Giữ P-18. Bổ sung P-19.</h1><p class="lede">14 loại đã có bản P‑18 được giữ nguyên; P‑19 gồm 25 loại, 4 capability và hai presentation variant “layers” + “scatter-chart”, mỗi identity có đủ 3 mode = 93 HTML. Không tạo lại các loại đã duyệt, không tự chuyển màu P‑18. P‑19 vẫn chờ owner review; P‑19C chưa được phép.</p><div class="counts" aria-label="Gallery counts"><span>14 P‑18 đã duyệt</span><span>25 loại P‑19</span><span>4 capability P‑19</span><span>2 presentation variant</span><span>93 HTML P‑19</span><span>107 diagram tổng hợp</span></div><h2>P-18 · Bản gốc đã duyệt</h2><p class="lede">Dùng trực tiếp 14 anchor review‑17; không còn bản P‑19 trùng lặp.</p><section class="grid">{''.join(approved_cards)}</section><h2 style="margin-top:48px">P-19 · Phần bổ sung</h2><p class="lede">Ba mode cho từng loại, capability và presentation variant còn lại.</p><section class="grid">{''.join(cards)}</section></main></body></html>'''


def main() -> None:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    sources = specimen_sources()
    if len(sources) != 31:
        raise RuntimeError("D-113 requires 25 canonical fixtures, four capability fixtures, Layers and scatter-chart presentation variants")

    records = []
    full_order = [f"type-{kind}" for kind in CANONICAL_TYPES] + [f"cap-{cap.lower()}-{CAPABILITY_NAMES[cap]}" for cap in P19A_CAPABILITIES] + ["type-layers", "type-scatter-chart"]
    for fixture_id, identity, ir in sources:
        plan = adapt_visual(ir)
        for mode_index, mode in enumerate(MODES):
            ordinal = full_order.index(fixture_id) * 3 + mode_index + 1
            filename = f"{ordinal:03d}-{fixture_id}--{mode}.html"
            path = SPECIMENS / filename
            path.write_text(render_gallery_html(ir, mode, fixture_id), encoding="utf-8")
            is_layers = fixture_id == "type-layers"
            is_scatter_chart = fixture_id == "type-scatter-chart"
            records.append({
                "ordinal": ordinal,
                "fixture_id": fixture_id,
                "identity": identity,
                "canonical_type": plan["adapter"]["canonical_type"],
                "capability_id": plan["adapter"]["capability_id"],
                "parent": "layer-stack" if is_layers else "scatter-plot" if is_scatter_chart else plan["adapter"]["canonical_type"] if plan["adapter"]["capability_id"] else None,
                "presentation_variant_id": "layers" if is_layers else "scatter-chart" if is_scatter_chart else None,
                "mode": mode,
                "layout_engine": plan["adapter"]["layout_engine"],
                "silhouette": "five-band-abstraction-stack" if is_layers else "quantitative-performance-scatter-with-trend" if is_scatter_chart else plan["adapter"]["silhouette"],
                "source_ir_sha256": plan["source_ir_sha256"],
                "path": f"specimens/{filename}",
                "sha256": sha256(path),
                "automated_check_disposition": "p19b-static-and-browser-planned",
            })

    if len(records) != 93:
        raise RuntimeError("P-19B generation did not produce exactly 93 specimens")
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
    if len(preview_files) != 31:
        raise RuntimeError("P-19B contact sheet requires exactly 31 neutral-light SVG previews")

    aggregate = hashlib.sha256(canonical_json(records).encode("utf-8")).hexdigest()
    inventory = {
        "schema_version": "1.0",
        "candidate_id": P19B_CANDIDATE_ID,
        "phase": "P-19B",
        "scope": "QA-only source/gallery; non-package",
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "canonical_type_count": 25,
        "presentation_variant_count": 2,
        "semantic_canonical_type_count": 39,
        "reused_p18_anchor_count": 14,
        "reused_p18_anchors": p18_references(),
        "reuse_authority": "D-084/D-085/D-095/D-096/D-097/D-098/D-099/D-100/D-105/D-106/D-108/D-109/D-110/D-111/D-112/D-113/D-114/D-115/D-116/D-117/D-118/D-119/D-120/D-121/D-122",
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
        "note": "D-122: renamed the CAP-V17 display identity to dumbbell while retaining CAP-V17 as the internal capability id and bar-chart as canonical parent; replaced only its three visual modes with an original twelve-category shared-scale paired comparison using the inherited P-18 template, direct endpoint/gap labels, mean ± population-standard-deviation bands and one redundantly identified focal pair; retained D-121–D-085 scope; 93 P-19 HTML, no owner approval or P-19C claim.",
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
