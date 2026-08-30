#!/usr/bin/env python3
"""Focused P-18R5 technical QA for the new kernel and single anchor."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from generate_p18r5 import HTML_PATH, RECEIPT_PATH, R5_DIR, SVG_PATH, render_payloads
from master_visual_kernel import (
    Box,
    BridgeMark,
    EdgeSpec,
    FontResolutionError,
    OrthogonalRouter,
    Point,
    Port,
    RoutedEdge,
    TypographyRequest,
    resolve_default_typography,
    route_hits_box,
    segment_distance_to_box,
)
from swimlane_anchor import TOKENS, build_anchor_model


REPORT_PATH = R5_DIR / "P-18R5-VERIFICATION.json"
BROWSER_REPORT_PATH = R5_DIR / "review" / "browser-verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, condition: bool, detail: object) -> dict[str, object]:
    return {"id": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    left, right = luminance(foreground), luminance(background)
    return (max(left, right) + 0.05) / (min(left, right) + 0.05)


def synthetic_bridge_check() -> dict[str, object]:
    first_spec = EdgeSpec("synthetic-horizontal", "a", "b", "", ())
    second_spec = EdgeSpec("synthetic-vertical", "c", "d", "", ())
    horizontal = RoutedEdge(
        first_spec,
        Port("a", "right", Point(0, 50)),
        Port("b", "left", Point(100, 50)),
        (Point(0, 50), Point(100, 50)),
        Box(0, 0, 0, 0),
    )
    vertical = RoutedEdge(
        second_spec,
        Port("c", "right", Point(50, 0)),
        Port("d", "left", Point(50, 100)),
        (Point(50, 0), Point(50, 100)),
        Box(0, 0, 0, 0),
    )
    bridged = OrthogonalRouter._with_bridges((horizontal, vertical))
    marks = [asdict(mark) for route in bridged for mark in route.bridges]
    valid = (
        len(marks) == 1
        and marks[0]["orientation"] == "horizontal"
        and marks[0]["segment_index"] == 0
        and marks[0]["radius"] >= 12
    )
    return check("P18R5-QA-BRIDGE", valid, marks)


def main() -> None:
    model = build_anchor_model()
    svg_text = SVG_PATH.read_text(encoding="utf-8")
    html_text = HTML_PATH.read_text(encoding="utf-8")
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    results: list[dict[str, object]] = []

    expected_nodes = {item["id"] for item in model.semantic_ir["nodes"]}
    projected_nodes = [semantic_id for node in model.layout.nodes for semantic_id in node.content.semantic_node_ids]
    expected_edges = {item["id"] for item in model.semantic_ir["edges"]}
    projected_edges = [semantic_id for route in model.routes for semantic_id in route.spec.semantic_edge_ids]
    results.append(check(
        "P18R5-QA-SEMANTIC-PROJECTION",
        set(projected_nodes) == expected_nodes
        and len(projected_nodes) == len(set(projected_nodes))
        and set(projected_edges) == expected_edges
        and len(projected_edges) == len(set(projected_edges)),
        {"nodes": len(projected_nodes), "edges": len(projected_edges)},
    ))

    default_typography = resolve_default_typography()
    explicit = resolve_default_typography(
        TypographyRequest(
            explicit_user_fonts={"node_title": "Avenir Next"},
        )
    )
    missing_user_font_rejected = False
    try:
        resolve_default_typography(
            TypographyRequest(explicit_user_fonts={"node_title": "Font Không Tồn Tại"})
        )
    except FontResolutionError:
        missing_user_font_rejected = True
    results.append(check(
        "P18R5-QA-FONT-PRECEDENCE",
        explicit["node_title"].precedence_source == "explicit_user_font"
        and explicit["node_title"].resolved_family == "Avenir Next"
        and default_typography["node_title"].fallback_used
        and missing_user_font_rejected,
        {
            "default_preferred": default_typography["node_title"].requested_family,
            "default_resolved": default_typography["node_title"].resolved_family,
            "explicit_resolved": explicit["node_title"].resolved_family,
            "missing_explicit_rejected": missing_user_font_rejected,
        },
    ))

    stress = "Đối chiếu séc, giấy báo chuyển tiền và tệp phải thu — Đặng Thị Mỹ Hạnh"
    glyph_failures = {
        role: model.metrics.validate_glyphs(role, stress)
        for role in model.typography
        if model.metrics.validate_glyphs(role, stress)
    }
    results.append(check("P18R5-QA-GLYPHS", not glyph_failures, glyph_failures or "all active roles cover stress string"))

    contrast_pairs = {
        "ink-on-surface": contrast_ratio(TOKENS["ink"], TOKENS["surface"]),
        "soft-ink-on-surface": contrast_ratio(TOKENS["ink_soft"], TOKENS["surface"]),
        "faint-ink-on-canvas": contrast_ratio(TOKENS["ink_faint"], TOKENS["canvas"]),
        "accent-text-on-canvas": contrast_ratio(TOKENS["accent_text"], TOKENS["canvas"]),
        "tag-check": contrast_ratio("#FFFFFF", TOKENS["tag_check"]),
        "tag-notice": contrast_ratio("#FFFFFF", TOKENS["tag_notice"]),
        "tag-listing": contrast_ratio("#FFFFFF", TOKENS["tag_listing"]),
        "tag-ar": contrast_ratio("#FFFFFF", TOKENS["tag_ar"]),
        "tag-ledger": contrast_ratio("#FFFFFF", TOKENS["tag_ledger"]),
    }
    results.append(check(
        "P18R5-QA-CONTRAST",
        all(value >= 4.5 for value in contrast_pairs.values()),
        {name: round(value, 3) for name, value in contrast_pairs.items()},
    ))

    node_overlaps: list[tuple[str, str]] = []
    for index, left in enumerate(model.layout.nodes):
        for right in model.layout.nodes[index + 1:]:
            if left.box.intersects(right.box, 4):
                node_overlaps.append((left.content.node_id, right.content.node_id))
    results.append(check("P18R5-QA-NODE-OVERLAP", not node_overlaps, node_overlaps))

    containment_failures: list[str] = []
    for node in model.layout.nodes:
        content_width = node.box.width - 40
        if any(model.metrics.measure("node_title", line).width > content_width for line in node.title_lines):
            containment_failures.append(f"{node.content.node_id}:title")
        if model.metrics.measure("material", node.content.transition).width > content_width:
            containment_failures.append(f"{node.content.node_id}:transition")
        tag_total = sum(node.tag_widths) + max(0, len(node.tag_widths) - 1) * 7
        available_bottom = node.box.width - 40
        combined = model.metrics.measure("technical", node.content.system_line).width + tag_total + 18
        if combined > available_bottom + 0.5:
            containment_failures.append(f"{node.content.node_id}:bottom-row")
    results.append(check("P18R5-QA-INTRINSIC-CONTAINMENT", not containment_failures, containment_failures))

    adaptive_targets = {"card-cash", "card-ledger-post"}
    adaptive_failures: list[str] = []
    adaptive_detail: dict[str, object] = {}
    for node in model.layout.nodes:
        measured_title = model.metrics.measure("node_title", node.content.title).width
        orphan = (
            len(node.title_lines) > 1
            and len(node.title_lines[-1].split()) == 1
            and len(node.title_lines[-1]) < 7
        )
        if orphan:
            adaptive_failures.append(f"{node.content.node_id}:orphan:{node.title_lines[-1]}")
        if node.content.node_id in adaptive_targets:
            if len(node.title_lines) != 1:
                adaptive_failures.append(f"{node.content.node_id}:unexpected-wrap")
            if node.box.width + 0.5 < measured_title + 40:
                adaptive_failures.append(f"{node.content.node_id}:insufficient-width")
            adaptive_detail[node.content.node_id] = {
                "width": round(node.box.width, 2),
                "measured_title_width": round(measured_title, 2),
                "title_lines": node.title_lines,
            }
    results.append(check(
        "P18R5-QA-ADAPTIVE-NODE-WIDTH",
        not adaptive_failures and set(adaptive_detail) == adaptive_targets,
        {"targets": adaptive_detail, "failures": adaptive_failures},
    ))

    route_failures: list[str] = []
    node_map = model.layout.node_map
    for route in model.routes:
        if not node_map[route.spec.source].box.contains(route.points[0], 0.5):
            route_failures.append(f"{route.spec.edge_id}:source")
        if not node_map[route.spec.target].box.contains(route.points[-1], 0.5):
            route_failures.append(f"{route.spec.edge_id}:target")
        for node_id, node in node_map.items():
            if node_id in {route.spec.source, route.spec.target}:
                continue
            if route_hits_box(route.points, node.box, 0.5):
                route_failures.append(f"{route.spec.edge_id}:through:{node_id}")
    results.append(check("P18R5-QA-ROUTING", not route_failures, route_failures))

    label_clearance_failures: list[str] = []
    for label_route in model.routes:
        if not label_route.spec.label:
            continue
        for other_route in model.routes:
            if label_route.spec.edge_id == other_route.spec.edge_id:
                continue
            distance = min(
                segment_distance_to_box(a, b, label_route.label_box)
                for a, b in zip(other_route.points, other_route.points[1:])
            )
            if distance < 8:
                label_clearance_failures.append(
                    f"{label_route.spec.edge_id}:{other_route.spec.edge_id}:{distance:.2f}"
                )
    results.append(check("P18R5-QA-LABEL-CLEARANCE", not label_clearance_failures, label_clearance_failures))
    results.append(synthetic_bridge_check())

    actual_bridges = [
        (route, bridge)
        for route in model.routes
        for bridge in route.bridges
    ]
    bridge_geometry_failures: list[str] = []
    for route, bridge in actual_bridges:
        if bridge.orientation != "horizontal":
            bridge_geometry_failures.append(f"{route.spec.edge_id}:orientation")
            continue
        if not 0 <= bridge.segment_index < len(route.points) - 1:
            bridge_geometry_failures.append(f"{route.spec.edge_id}:segment-index")
            continue
        start = route.points[bridge.segment_index]
        end = route.points[bridge.segment_index + 1]
        if abs(start.y - end.y) > 0.001 or abs(start.y - bridge.point.y) > 0.001:
            bridge_geometry_failures.append(f"{route.spec.edge_id}:not-on-horizontal-segment")
        if not min(start.x, end.x) + bridge.radius < bridge.point.x < max(start.x, end.x) - bridge.radius:
            bridge_geometry_failures.append(f"{route.spec.edge_id}:endpoint-clearance")
    bridge_markup = {
        "model_marks": len(actual_bridges),
        "groups": svg_text.count('class="bridge-mark'),
        "gaps": svg_text.count('data-bridge-role="gap"'),
        "underlays": svg_text.count('data-bridge-role="underlay"'),
        "hops": svg_text.count('data-bridge-role="hop"'),
        "port_dots": svg_text.count("port-dot"),
    }
    bridge_renderer_ok = (
        len(actual_bridges) > 0
        and bridge_markup["groups"] == len(actual_bridges)
        and bridge_markup["gaps"] == len(actual_bridges)
        and bridge_markup["underlays"] == len(actual_bridges)
        and bridge_markup["hops"] == len(actual_bridges)
        and bridge_markup["port_dots"] == 0
        and ".bridge-hop{fill:none" in svg_text
        and ".bridge-hop-underlay{fill:none" in svg_text
        and not bridge_geometry_failures
    )
    results.append(check(
        "P18R5-QA-BRIDGE-RENDERING",
        bridge_renderer_ok,
        {"markup": bridge_markup, "geometry_failures": bridge_geometry_failures},
    ))

    board = model.layout.artboard
    occupancy = ((board.legend_top - board.lane_top) + board.legend_height) / board.height
    results.append(check(
        "P18R5-QA-ARTBOARD",
        2.20 <= board.width / board.height <= 2.45 and occupancy >= 0.75 and board.safe_area >= 48,
        {"width": board.width, "height": board.height, "aspect": board.width / board.height, "occupancy": occupancy},
    ))

    anchor_html_files = sorted((R5_DIR / "anchor").glob("*.html"))
    anchor_svg_files = sorted((R5_DIR / "anchor").glob("*.svg"))
    external = [
        value
        for value in re.findall(r"(?:https?:|//)[^\s\"']+", html_text + svg_text)
        if value != "http://www.w3.org/2000/svg"
    ]
    unsafe = re.findall(r"<script\b|\bon[a-z]+\s*=|javascript:|<foreignObject\b", html_text + svg_text, re.I)
    global_transform = re.findall(r"<svg[^>]*\btransform=|<g[^>]*\btransform=\"(?:matrix|scale)\(", svg_text, re.I)
    results.append(check(
        "P18R5-QA-STANDALONE-SECURITY",
        len(anchor_html_files) == 1
        and len(anchor_svg_files) == 1
        and not external
        and not unsafe
        and not global_transform
        and html_text.count("<svg") == 1
        and svg_text.count("<svg") == 1,
        {
            "html_count": len(anchor_html_files),
            "svg_count": len(anchor_svg_files),
            "external": external,
            "unsafe": unsafe,
            "global_transform": global_transform,
        },
    ))

    visible_title_duplicate = ">Luồng chứng từ thu tiền<" in svg_text
    results.append(check(
        "P18R5-QA-INTERFACE-CONTENT",
        not visible_title_duplicate
        and "EVIDENCE RAIL" not in svg_text.upper()
        and 'font-size:24px' in svg_text
        and 'font-size:16px' in svg_text
        and 'font-size:14px' in svg_text,
        {
            "duplicate_visible_title": visible_title_duplicate,
            "evidence_rail": "EVIDENCE RAIL" in svg_text.upper(),
        },
    ))

    svg_bytes, html_bytes, regenerated_receipt = render_payloads()
    deterministic = svg_bytes == SVG_PATH.read_bytes() and html_bytes == HTML_PATH.read_bytes()
    receipt_artifacts = receipt["artifacts"]
    hashes_match = (
        receipt_artifacts["anchor/swimlane--neutral-light.svg"]["sha256"] == sha256(SVG_PATH)
        and receipt_artifacts["anchor/swimlane--neutral-light.html"]["sha256"] == sha256(HTML_PATH)
        and regenerated_receipt["anchor_id"] == receipt["anchor_id"]
    )
    results.append(check("P18R5-QA-DETERMINISM", deterministic and hashes_match, {"deterministic": deterministic, "hashes_match": hashes_match}))

    browser = {"status": "DEFERRED", "reason": "browser report not found"}
    if BROWSER_REPORT_PATH.exists():
        browser = json.loads(BROWSER_REPORT_PATH.read_text(encoding="utf-8"))
        browser_ok = (
            browser.get("status") == "PASS"
            and browser.get("fail_count") == 0
            and browser.get("artifact_sha256") == sha256(HTML_PATH)
        )
        results.append(check(
            "P18R5-QA-BROWSER",
            browser_ok,
            {
                "runs": browser.get("run_count"),
                "failures": browser.get("fail_count"),
                "artifact_hash_match": browser.get("artifact_sha256") == sha256(HTML_PATH),
            },
        ))
    else:
        results.append({"id": "P18R5-QA-BROWSER", "status": "DEFERRED", "detail": browser["reason"]})

    fail_count = sum(item["status"] == "FAIL" for item in results)
    deferred_count = sum(item["status"] == "DEFERRED" for item in results)
    report = {
        "schema_version": "1.0",
        "phase": "P-18R5",
        "contract_id": "P18R5-KERNEL-SWIMLANE-ANCHOR-1.5.0",
        "result": "PASS" if fail_count == 0 and deferred_count == 0 else ("FAIL" if fail_count else "DEFERRED"),
        "check_count": len(results),
        "pass_count": sum(item["status"] == "PASS" for item in results),
        "fail_count": fail_count,
        "deferred_count": deferred_count,
        "checks": results,
        "artifact_hashes": {
            str(SVG_PATH.relative_to(REPO_ROOT)): sha256(SVG_PATH),
            str(HTML_PATH.relative_to(REPO_ROOT)): sha256(HTML_PATH),
            str(RECEIPT_PATH.relative_to(REPO_ROOT)): sha256(RECEIPT_PATH),
        },
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": report["result"], "pass": report["pass_count"], "fail": fail_count, "deferred": deferred_count, "report": str(REPORT_PATH)}))
    if fail_count:
        raise SystemExit(1)


REPO_ROOT = Path(__file__).resolve().parents[4]


if __name__ == "__main__":
    main()
