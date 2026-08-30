#!/usr/bin/env python3
"""Generate the one authorized P-18R5 anchor and its build receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from swimlane_anchor import build_anchor_model, render_html, render_svg


SOURCE_DIR = Path(__file__).resolve().parent
R5_DIR = SOURCE_DIR.parent
ANCHOR_DIR = R5_DIR / "anchor"
SVG_PATH = ANCHOR_DIR / "swimlane--neutral-light.svg"
HTML_PATH = ANCHOR_DIR / "swimlane--neutral-light.html"
RECEIPT_PATH = R5_DIR / "P-18R5-BUILD-RECEIPT.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def render_payloads() -> tuple[bytes, bytes, dict[str, object]]:
    model = build_anchor_model()
    svg = render_svg(model)
    html = render_html(model, svg)
    board = model.layout.artboard
    receipt = {
        "schema_version": "1.0",
        "contract_id": "P18R5-KERNEL-SWIMLANE-ANCHOR-1.5.0",
        "anchor_id": "P18R5-SWIMLANE-NEUTRAL-LIGHT",
        "mode": "neutral-light",
        "layout_engine": "lane-interaction",
        "serializer_count": 2,
        "specimen_count": 1,
        "artboard": {
            "width": board.width,
            "height": board.height,
            "aspect_ratio": round(board.width / board.height, 6),
            "safe_area": board.safe_area,
            "semantic_field_plus_legend_ratio": round(
                ((board.legend_top - board.lane_top) + board.legend_height) / board.height,
                6,
            ),
        },
        "typography": {
            role: {
                "preferred": resolved.requested_family,
                "resolved": resolved.resolved_family,
                "weight": resolved.role.weight,
                "size_px": resolved.role.size_px,
                "fallback_used": resolved.fallback_used,
                "fallback_reason": resolved.fallback_reason,
                "font_path": str(resolved.resolved_face.path),
                "face_index": resolved.resolved_face.index,
            }
            for role, resolved in model.typography.items()
        },
        "semantic_projection": {
            "locked_fixture_id": "P18-C02-SWIM",
            "locked_node_count": len(model.semantic_ir["nodes"]),
            "locked_edge_count": len(model.semantic_ir["edges"]),
            "display_node_count": len(model.layout.nodes),
            "display_edge_count": len(model.routes),
            "covered_node_ids": sorted(
                semantic_id
                for node in model.layout.nodes
                for semantic_id in node.content.semantic_node_ids
            ),
            "covered_edge_ids": sorted(
                semantic_id
                for route in model.routes
                for semantic_id in route.spec.semantic_edge_ids
            ),
        },
        "routing": {
            "ports_allocated_before_routing": True,
            "decorative_source_port_dots": False,
            "obstacle_clearance_px": 16,
            "minimum_label_connector_clearance_px": 8,
            "rounded_orthogonal": True,
            "bridge_detection_enabled": True,
            "bridge_owner_orientation": "horizontal",
            "bridge_geometry": "path_integrated_open_hop",
            "minimum_parallel_corridor_separation_px": 56,
            "minimum_same_segment_hop_clearance_px": 12,
            "bridge_paint_order": ["path_integrated_base_routes", "hop_underlay", "hop_repaint", "annotations"],
            "bridge_closed_shape_or_junction": False,
            "bridge_count": sum(len(route.bridges) for route in model.routes),
        },
        "node_sizing": {
            "font_metrics_before_wrap": True,
            "local_stage_width_budget": True,
            "balanced_wrap": True,
            "short_word_orphan_rejected_when_local_width_available": True,
            "hard_max_width_px": 440,
        },
        "boundaries": {
            "qa_only": True,
            "external_resources": False,
            "javascript": False,
            "runtime_modified": False,
            "package_modified": False,
            "dist_modified": False,
            "p18r6_authorized": False,
        },
    }
    return (svg + "\n").encode("utf-8"), html.encode("utf-8"), receipt


def main() -> None:
    ANCHOR_DIR.mkdir(parents=True, exist_ok=True)
    svg_bytes, html_bytes, receipt = render_payloads()
    SVG_PATH.write_bytes(svg_bytes)
    HTML_PATH.write_bytes(html_bytes)
    receipt["artifacts"] = {
        str(SVG_PATH.relative_to(R5_DIR)): {
            "sha256": sha256_bytes(svg_bytes),
            "bytes": len(svg_bytes),
        },
        str(HTML_PATH.relative_to(R5_DIR)): {
            "sha256": sha256_bytes(html_bytes),
            "bytes": len(html_bytes),
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"anchor": str(HTML_PATH), "svg": str(SVG_PATH), "receipt": str(RECEIPT_PATH)}))


if __name__ == "__main__":
    main()
