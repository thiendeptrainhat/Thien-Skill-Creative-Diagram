#!/usr/bin/env python3
"""Generate the exact P-18R6 14-engine neutral-light gallery."""

from __future__ import annotations

import hashlib
from html import escape
import json
from pathlib import Path
import shutil

from gallery_kernel import Anchor, TYPOGRAPHY, anchors_without_swimlane, orthogonal_route_d, render_html


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
ANCHORS = R6 / "anchors"
REVIEW = R6 / "review"
R5 = ROOT / "evidence/p18/r5"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def r6_lane_phase_extension(parent_svg: str) -> str:
    """Add complete R6 phase coverage without mutating the frozen R5 source."""

    root_needle = 'data-layout-engine="lane-interaction" data-mode="neutral-light"'
    root_replacement = (
        'data-layout-engine="lane-interaction" data-mode="neutral-light" '
        'data-r6-local-extension="D-066" data-major-phase-count="6" '
        'data-workflow-step-count="6" data-phase-coverage="complete"'
    )
    if parent_svg.count(root_needle) != 1:
        raise RuntimeError("Unexpected R5 Swimlane root contract")
    svg = parent_svg.replace(root_needle, root_replacement, 1)

    rail_start = '<line class="rail-line" x1="994.63" y1="66.00" x2="2966.17" y2="66.00"/>'
    rail_end = '<text class="rail-label" x="2966.17" y="109.00" text-anchor="middle">ĐĂNG SỔ</text>'
    start = svg.find(rail_start)
    end = svg.find(rail_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Unexpected R5 Swimlane major-phase rail")
    end += len(rail_end)
    phases = (
        (0, 501.75, "CHUẨN BỊ", "card-customer", False),
        (1, 994.63, "NHẬN BỘ", "card-mail", False),
        (2, 1487.52, "PHÂN LOẠI", "card-cash", False),
        (3, 1980.40, "GỬI NGÂN HÀNG", "card-bank", False),
        (4, 2473.29, "CẬP NHẬT NỢ", "card-ar", True),
        (5, 2966.17, "ĐĂNG SỔ", "card-ledger-post,card-ledger-close", False),
    )
    rail_parts = [
        '<g data-major-phase-rail="true" data-phase-count="6" '
        'data-phase-order="CHUẨN BỊ|NHẬN BỘ|PHÂN LOẠI|GỬI NGÂN HÀNG|CẬP NHẬT NỢ|ĐĂNG SỔ" '
        'data-step-coverage="one-or-more-node-per-phase">',
        '<line class="rail-line" x1="501.75" y1="66.00" x2="2966.17" y2="66.00"/>',
    ]
    for index, x, label, mapped_nodes, focal in phases:
        focal_class = " focal" if focal else ""
        rail_parts.extend(
            (
                f'<g data-major-phase-index="{index}" data-workflow-step-id="step-{index}" '
                f'data-major-phase-label="{label}" data-mapped-node-ids="{mapped_nodes}" '
                f'data-phase-center-x="{x:.2f}">',
                f'<circle class="rail-dot{focal_class}" cx="{x:.2f}" cy="66.00" r="19"/>',
                f'<text class="rail-number{focal_class}" x="{x:.2f}" y="71.00" text-anchor="middle">{index}</text>',
                f'<text class="rail-label{focal_class}" x="{x:.2f}" y="109.00" text-anchor="middle">{label}</text>',
                '</g>',
            )
        )
    rail_parts.append('</g>')
    svg = svg[:start] + "".join(rail_parts) + svg[end:]

    legend_start = '<circle cx="280.00" cy="1234.00" r="16" fill="#F1F0EC" stroke="#C9CDD2" stroke-width="1.5"/>'
    legend_end = '<text class="legend-label" x="1308.00" y="1240.00">Đăng Sổ</text>'
    start = svg.find(legend_start)
    end = svg.find(legend_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Unexpected R5 Swimlane phase legend")
    end += len(legend_end)
    legend_positions = (280.0, 500.0, 720.0, 940.0, 1160.0, 1380.0)
    legend_parts = ['<g data-major-phase-legend="true" data-phase-count="6">']
    for (index, _, label, _, focal), x in zip(phases, legend_positions, strict=True):
        fill = "#FAD8C9" if focal else "#F1F0EC"
        stroke = "#F26A32" if focal else "#C9CDD2"
        number_fill = "#B84A1B" if focal else "#242B3D"
        display_label = label.title()
        legend_parts.extend(
            (
                f'<g data-major-phase-legend-index="{index}" data-workflow-step-id="step-{index}" data-major-phase-label="{label}">',
                f'<circle cx="{x:.2f}" cy="1234.00" r="16" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
                f'<text class="rail-number" x="{x:.2f}" y="1239.00" text-anchor="middle" fill="{number_fill}">{index}</text>',
                f'<text class="legend-label" x="{x + 28:.2f}" y="1240.00">{display_label}</text>',
                '</g>',
            )
        )
    legend_parts.append('</g>')
    return svg[:start] + "".join(legend_parts) + svg[end:]


def lane_anchor() -> Anchor:
    source = R5 / "anchor/swimlane--neutral-light.svg"
    svg = r6_lane_phase_extension(source.read_text(encoding="utf-8"))
    return Anchor(
        order=6,
        engine="lane-interaction",
        canonical_type="swimlane",
        filename="06-lane-interaction--neutral-light",
        title="Lane interaction anchor",
        takeaway="Sáu major phase phủ đủ workflow từ Chuẩn bị đến Đăng sổ; nhánh cập nhật công nợ vẫn là focal handoff.",
        svg=svg,
        facts=(
            ("lineage", "R6-local phase-coverage extension over exact frozen P-18R5 review-04 source"),
            ("source_sha256", sha256(source)),
            ("manifest_sha256", sha256(R5 / "P-18R5-MANIFEST.json")),
            ("local_extension", "D-066 · six major phases"),
            ("engine", "lane-interaction"),
        ),
    )


def all_anchors() -> tuple[Anchor, ...]:
    return tuple(sorted((*anchors_without_swimlane(), lane_anchor()), key=lambda item: item.order))


def shell_css() -> str:
    return """
    :root{--paper:#eeece7;--canvas:#f7f6f2;--ink:#252b3c;--muted:#687286;--line:#d6d4ce;--accent:#f26a32}
    *{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--paper);color:var(--ink)}
    body{font-family:system-ui,sans-serif;padding:44px 24px 72px}main{width:min(100%,1840px);margin:auto}
    .eyebrow{margin:0 0 8px;font:700 14px ui-monospace,monospace;letter-spacing:.16em;color:var(--accent)}
    h1{margin:0;font-family:Georgia,serif;font-size:48px;line-height:1.06;font-weight:400}.lede{max-width:880px;margin:12px 0 32px;font-size:16px;line-height:1.6;color:var(--muted)}
    .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.card{display:flex;flex-direction:column;min-width:0;border:1px solid var(--line);border-radius:18px;background:#ffffff8f;overflow:hidden;box-shadow:0 16px 44px #2d344314}
    .preview{display:flex;align-items:center;justify-content:center;aspect-ratio:16/9;padding:10px;background:var(--canvas);border-bottom:1px solid var(--line)}.preview img{display:block;width:100%;height:100%;object-fit:contain}
    .meta{display:grid;grid-template-columns:auto 1fr auto;gap:12px;align-items:center;padding:16px 18px}.num{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:#e4e2dd;font:700 14px ui-monospace,monospace}.meta h2{margin:0;font-size:20px}.meta p{margin:4px 0 0;color:var(--muted);font:14px ui-monospace,monospace}.open{color:var(--accent);text-decoration:none;font-weight:700}.open:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
    @media(max-width:980px){.grid{grid-template-columns:1fr}}@media(max-width:650px){body{padding:24px 12px 48px}h1{font-size:40px}.meta{grid-template-columns:auto 1fr}.open{grid-column:2}}
    """


def build_index(anchors: tuple[Anchor, ...]) -> str:
    cards = []
    for item in anchors:
        cards.append(f'''<article class="card"><div class="preview"><img src="anchors/{escape(item.filename)}.svg" alt="{escape(item.title)}"></div><div class="meta"><span class="num">{item.order:02d}</span><div><h2>{escape(item.engine)}</h2><p>{escape(item.canonical_type)} · neutral-light</p></div><a class="open" href="anchors/{escape(item.filename)}.html">Open anchor →</a></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-18R6 · 14-engine anchor gallery</title><style>{shell_css()}</style></head><body><main><p class="eyebrow">P‑18R6 · OWNER REVIEW CONTACT SHEET</p><h1>Fourteen engines. Fourteen distinct silhouettes.</h1><p class="lede">QA-only neutral-light anchors derived from the locked semantic contract. This labeled sheet is for owner inspection; use the masked sheet for blind recognition.</p><section class="grid">{"".join(cards)}</section></main></body></html>'''


def build_blind(anchors: tuple[Anchor, ...]) -> str:
    # Fixed deterministic shuffle prevents the numeric order from revealing the engine map.
    order = (11, 3, 8, 1, 13, 5, 10, 2, 14, 7, 4, 12, 6, 9)
    lookup = {item.order: item for item in anchors}
    cards = []
    for blind_number, source_order in enumerate(order, 1):
        item = lookup[source_order]
        cards.append(f'''<article class="card"><div class="preview"><img src="anchors/{escape(item.filename)}.svg" alt="Masked candidate {blind_number:02d}"></div><div class="meta"><span class="num">{blind_number:02d}</span><div><h2>Masked candidate</h2><p>Identify the layout family from silhouette only.</p></div></div></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-18R6 · masked blind sheet</title><style>{shell_css()}</style></head><body><main><p class="eyebrow">P‑18R6 · MASKED REVIEW</p><h1>Silhouette recognition</h1><p class="lede">Review the numbered cards before opening the labeled contact sheet. Record one family guess per card.</p><section class="grid">{"".join(cards)}</section></main></body></html>'''


def main() -> None:
    ANCHORS.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    anchors = all_anchors()
    if len(anchors) != 14 or len({item.engine for item in anchors}) != 14:
        raise RuntimeError("P-18R6 must produce exactly fourteen unique engines")

    for item in anchors:
        (ANCHORS / f"{item.filename}.svg").write_text(item.svg, encoding="utf-8")
        (ANCHORS / f"{item.filename}.html").write_text(render_html(item), encoding="utf-8")

    (R6 / "index.html").write_text(build_index(anchors), encoding="utf-8")
    (R6 / "blind-review.html").write_text(build_blind(anchors), encoding="utf-8")
    shutil.copy2(R5 / "P-18R5-MANIFEST.json", REVIEW / "P-18R5-parent-manifest.json")

    inventory = {
        "schema_version": "1.0",
        "candidate_id": "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-14-1.5.0",
        "authority": ["D-051", "D-052", "D-058", "D-059", "D-060", "D-061", "D-062", "D-063", "D-064", "D-065", "D-066", "D-067", "D-068", "D-069", "D-070", "D-071", "D-072"],
        "mode": "neutral-light",
        "engine_count": len(anchors),
        "engines": [
            {
                "order": item.order,
                "engine": item.engine,
                "canonical_type": item.canonical_type,
                "html": f"anchors/{item.filename}.html",
                "svg": f"anchors/{item.filename}.svg",
                "takeaway": item.takeaway,
            }
            for item in anchors
        ],
        "typography": {
            role: {
                "preferred": resolved.requested_family,
                "resolved": resolved.resolved_family,
                "precedence": resolved.precedence_source,
                "fallback_used": resolved.fallback_used,
                "fallback_reason": resolved.fallback_reason,
            }
            for role, resolved in TYPOGRAPHY.items()
        },
        "connector_corner_style": {
            "scope": "whole-chart",
            "engines": ["topology-and-zones", "integration-pipeline", "runtime-deployment", "dependency-dag"],
            "default": "rounded",
            "allowed": ["rounded", "straight"],
            "explicit_user_choice_precedence": True,
            "rounded_example": orthogonal_route_d(((0, 0), (0, 40), (40, 40)), "rounded"),
            "straight_example": orthogonal_route_d(((0, 0), (0, 40), (40, 40)), "straight"),
        },
        "diagram_10_annotation_gap": {
            "metric": "bbox-left-at-vertical-center-to-outer-triangle-right-edge",
            "target_px": 72.0,
            "maximum_tolerance_px": 0.01,
            "note_count": 4,
            "x_source": "outer-triangle geometry plus one shared target",
        },
        "diagram_06_phase_coverage": {
            "authority": "D-066",
            "phase_count": 6,
            "phase_order": ["CHUẨN BỊ", "NHẬN BỘ", "PHÂN LOẠI", "GỬI NGÂN HÀNG", "CẬP NHẬT NỢ", "ĐĂNG SỔ"],
            "r5_source_preserved_exactly": True,
            "r6_local_extension": True,
        },
        "diagram_11_schema_geometry": {
            "authority": ["D-066", "D-069", "D-070"],
            "top_row_center_alignment": True,
            "order_item_centered_under_order": True,
            "minimum_bottom_padding_px": 24,
            "minimum_relationship_label_node_clearance_px": 8,
            "relationship_names": ["PLACES", "PAID BY", "CONTAINS"],
            "relationship_name_placement": {"horizontal": "above", "vertical": "right"},
            "cardinality_labels_separate_from_relationship_names": True,
            "cardinality_per_relationship": {"source": "1", "target": "N"},
            "cardinality_placement": "inline-on-connector-axis",
            "cardinality_knockout": {
                "fill_role": "canvas",
                "stroke": "none",
                "along_line_padding_px": 8,
                "perpendicular_padding_px": 4,
                "minimum_node_clearance_px": 8,
                "paint_order": "connector then knockout then label",
            },
            "maximum_axis_alignment_error_px": 0.06,
        },
        "diagram_12_axis_annotations": {
            "authority": "D-067",
            "note_count": 4,
            "notes": ["↑ HIGH IMPACT", "← LOW EFFORT", "↓ LOW IMPACT", "HIGH EFFORT →"],
            "vertical_note_offset_x_px": 24,
            "horizontal_note_offset_y_px": 42,
            "minimum_axis_clearance_px": 16,
            "measured_bbox_required": True,
            "review_08_semantic_field_preserved": True,
        },
        "diagram_12_focal_region": {
            "authority": "D-068",
            "fill_role": "accent-soft",
            "stroke": "none",
            "transparent_or_zero_opacity_stroke_allowed": False,
            "geometry_preserved_from_review_09": True,
            "d067_axis_annotations_preserved": True,
        },
        "diagram_14_sankey_geometry": {
            "authority": "D-072",
            "inherited_authority": "D-071",
            "total_minutes": 12000,
            "scale_px_per_minute": 0.025,
            "node_interface_occupancy": "100%",
            "ribbon_interval_policy": "gapless and non-overlapping on every applicable node interface",
            "node_label_placement": "above",
            "node_label_alignment": "centered on node bar",
            "node_corner_style": "square",
            "rounded_bar_allowed": False,
            "top_row_alignment": "top",
            "top_row_y_px": 210.0,
            "top_row_node_ids": ["budget", "unit", "passed"],
            "top_row_max_spread_px": 0.01,
            "conservation": {
                "stages": "5200 + 4000 + 2800 = 12000",
                "outcomes": "9400 + 1600 + 1000 = 12000",
            },
        },
        "r5_parent": {
            "manifest": "review/P-18R5-parent-manifest.json",
            "manifest_sha256": sha256(R5 / "P-18R5-MANIFEST.json"),
            "swimlane_svg_sha256": sha256(R5 / "anchor/swimlane--neutral-light.svg"),
            "source_preserved_exactly": True,
            "r6_lane_svg_byte_identical_to_r5": False,
            "r6_local_extension_authority": "D-066",
        },
        "lineage": {
            "review": "review-14",
            "supersedes_for_owner_review": "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-13-1.5.0",
            "review_01_manifest_sha256": "fcdec11e49a00d89d82a3fafaba7cae2ac8e7c58908fa76cc2fa6eba383aad37",
            "review_01_archive": "history/review-01",
            "review_02_manifest_sha256": "2f9c7aad3a2dd9d43d575ddfb864effa915df909134d5401dbb075ed6ea2cf7b",
            "review_02_archive": "history/review-02",
            "review_03_manifest_sha256": "572de899399755268d63fa5cb49c598a6ee6c5d509418ed8d07484a750c62e54",
            "review_03_archive": "history/review-03",
            "review_04_manifest_sha256": "6be1aa8894cf62d252c9cd890f14b4e825497b811046df57ccb301e84054f185",
            "review_04_archive": "history/review-04",
            "review_05_manifest_sha256": "20b8f257b44d7f6c9fc0cbf7eed9b710778bdcebb142978b8f47aad61eab393b",
            "review_05_archive": "history/review-05",
            "review_06_manifest_sha256": "b1f934b5542079a93763b5ac0237dbdc2871dc6f97e8e4ea14adeb05536f844d",
            "review_06_archive": "history/review-06",
            "review_07_manifest_sha256": "da2d8840b8bf009c54c10b72ccc7e9fbd2aedf6422acd2c822548f63a29b5290",
            "review_07_archive": "history/review-07",
            "review_08_manifest_sha256": "a5e58ccb47ea63b6904e84859aace63fb3f09b2cb3147e4a3a96ce41617eb7ec",
            "review_08_archive": "history/review-08",
            "review_09_manifest_sha256": "d7f7e9653d02b0b156c2aa144643047edb09fb970a5ae07e58f7b1cecbc44703",
            "review_09_archive": "history/review-09",
            "review_10_manifest_sha256": "9a1fe7282db733c8239a0daf4abddff984c2372bfb6bb82f759de94980adaf84",
            "review_10_archive": "history/review-10",
            "review_11_manifest_sha256": "69b93b45fc852b9e9c1405b66fbb40dd10d964fa55f589b65a51984d5b3dccfc",
            "review_11_archive": "history/review-11",
            "review_12_manifest_sha256": "90de78337c49f1ee42aae8730bbf072eb8bf679388038041b793f943ddfcafb6",
            "review_12_archive": "history/review-12",
            "review_13_manifest_sha256": "520c4ad74b944a218a576bdec7f100eb84054e712a066965417961fe97b91324",
            "review_13_archive": "history/review-13",
        },
        "review": {"owner_status": "PENDING", "g03_1_5_0": "NOT-EVALUATED", "p19_authorized": False},
    }
    (R6 / "P-18R6-INVENTORY.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
