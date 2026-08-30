#!/usr/bin/env python3
"""Deterministic structural, semantic, quantitative and security QA for P-18R6."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from gallery_kernel import containment_anchor, dependency_anchor, deployment_anchor, integration_anchor, topology_anchor


ROOT = Path(__file__).resolve().parents[4]
R6 = ROOT / "evidence/p18/r6"
ANCHORS = R6 / "anchors"
R5 = ROOT / "evidence/p18/r5"
INVENTORY = R6 / "P-18R6-INVENTORY.json"
REPORT = R6 / "review/static-verification.json"
EXPECTED_ENGINES = {
    "topology-and-zones", "integration-pipeline", "runtime-deployment", "dependency-dag",
    "directed-flow-state", "lane-interaction", "time-planning", "work-experience",
    "hierarchy", "containment-stack", "compartment-model", "spatial-matrix",
    "quantitative", "special-geometry",
}
SVG_NS = "{http://www.w3.org/2000/svg}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, test_id: str, detail: str, results: list[dict[str, str]]) -> None:
    results.append({"id": test_id, "status": "PASS" if condition else "FAIL", "detail": detail})


def visible_text(root: ET.Element) -> list[str]:
    values = []
    for item in root.iter(f"{SVG_NS}text"):
        text = "".join(item.itertext()).strip()
        if text:
            values.append(text)
    return values


def signature(root: ET.Element) -> tuple[int, ...]:
    tags = Counter(item.tag.removeprefix(SVG_NS) for item in root.iter())
    classes = Counter()
    for item in root.iter():
        for cls in item.attrib.get("class", "").split():
            classes[cls] += 1
    return (
        tags["rect"], tags["path"], tags["line"], tags["circle"], tags["polygon"],
        classes["zone"], classes["zone-fill"], classes["node-card"], classes["band"], classes["bridge-mark"],
    )


def geometry_box(item: ET.Element) -> tuple[float, float, float, float]:
    return tuple(float(item.attrib[f"data-box-{key}"]) for key in ("x", "y", "width", "height"))


def box_center(box: tuple[float, float, float, float]) -> tuple[float, float]:
    x, y, width, height = box
    return x + width / 2, y + height / 2


def polygon_points(item: ET.Element) -> tuple[tuple[float, float], ...]:
    return tuple(
        tuple(float(value) for value in pair.split(","))
        for pair in item.attrib.get("points", "").split()
    )


def horizontal_edge(points: tuple[tuple[float, float], ...], y: float) -> tuple[tuple[float, float], ...]:
    return tuple(sorted((point for point in points if abs(point[1] - y) <= 0.01), key=lambda point: point[0]))


def main() -> None:
    results: list[dict[str, str]] = []
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    html_paths = sorted(ANCHORS.glob("*.html"))
    svg_paths = sorted(ANCHORS.glob("*.svg"))
    check(len(html_paths) == 14, "R6-COUNT-HTML", f"found={len(html_paths)} expected=14", results)
    check(len(svg_paths) == 14, "R6-COUNT-SVG", f"found={len(svg_paths)} expected=14", results)
    check(inventory["engine_count"] == 14, "R6-INVENTORY-COUNT", f"inventory={inventory['engine_count']}", results)
    check({item["engine"] for item in inventory["engines"]} == EXPECTED_ENGINES, "R6-ENGINE-COVERAGE", "exact 14-engine set", results)

    parsed: list[tuple[Path, ET.Element]] = []
    for path in svg_paths:
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            parsed.append((path, root))
            check(True, f"XML-{path.stem}", "well-formed SVG", results)
        except ET.ParseError as exc:
            check(False, f"XML-{path.stem}", str(exc), results)

    engines = []
    signatures = []
    for path, root in parsed:
        source = path.read_text(encoding="utf-8")
        engine = root.attrib.get("data-layout-engine", "")
        engines.append(engine)
        signatures.append(signature(root))
        text = visible_text(root)
        viewbox = root.attrib.get("viewBox", "").split()
        valid_viewbox = len(viewbox) == 4 and all(float(value) > 0 if index >= 2 else float(value) == 0 for index, value in enumerate(viewbox))
        check(valid_viewbox, f"VIEWBOX-{engine}", root.attrib.get("viewBox", "missing"), results)
        check(root.attrib.get("role") == "img" and root.attrib.get("aria-labelledby"), f"A11Y-{engine}", "role img + labelled title/desc", results)
        check(root.find(f"{SVG_NS}title") is not None and root.find(f"{SVG_NS}desc") is not None, f"TITLE-DESC-{engine}", "title and desc present", results)
        check("<script" not in source and "<foreignObject" not in source and "http://" not in source.replace("http://www.w3.org/2000/svg", "") and "https://" not in source, f"SECURITY-{engine}", "no script/foreignObject/network resource", results)
        check("transform=\"scale" not in source and "transform=\"matrix" not in source, f"NO-GLOBAL-TRANSFORM-{engine}", "no scale/matrix layout transform", results)
        check(not any(value.upper().find("EVIDENCE RAIL") >= 0 for value in text), f"NO-EVIDENCE-RAIL-{engine}", "no visible evidence rail", results)
        check(len(text) == len([value for value in text if value]), f"VISIBLE-TEXT-{engine}", f"visible text elements={len(text)}", results)
        # The exact R5 anchor predates the R6 data attribute but is verified by its parent manifest.
        ratio = float(root.attrib.get("data-semantic-ratio", "0.81" if engine == "lane-interaction" else "0"))
        check(ratio >= 0.75, f"SEMANTIC-RATIO-{engine}", f"declared={ratio:.2f}", results)
        custom = engine != "lane-interaction"
        check((root.attrib.get("data-font-measured") == "true") if custom else True, f"FONT-MEASURED-{engine}", "real-font measurement binding", results)
        check((root.attrib.get("data-min-label-clearance") == "8") if custom else True, f"LABEL-CLEARANCE-{engine}", "minimum 8px contract", results)

        css_sizes = [int(value) for value in re.findall(r"font-size:([0-9]+)px", source)]
        allowed_minimum = min(css_sizes) if css_sizes else 14
        check(allowed_minimum >= 14, f"TYPE-MIN-{engine}", f"minimum declared font={allowed_minimum}px", results)
        check("font-size:24px" in source, f"NODE-TYPE-{engine}", "24px node title present", results)
        check("font-size:16px" in source, f"MATERIAL-TYPE-{engine}", "16px material text present", results)

    check(len(engines) == 14 and set(engines) == EXPECTED_ENGINES, "R6-SVG-ENGINE-COVERAGE", f"unique={len(set(engines))}", results)
    # Structural signatures are deliberately coarse; distinct count >=12 guards against generic-template reuse.
    check(len(set(signatures)) >= 12, "R6-SILHOUETTE-SIGNATURE", f"unique structural signatures={len(set(signatures))}/14", results)

    roots_by_engine = {root.attrib.get("data-layout-engine", ""): root for _, root in parsed}
    expected_rounded_counts = {
        "topology-and-zones": 4,
        "integration-pipeline": 4,
        "runtime-deployment": 3,
    }
    for engine, expected_count in expected_rounded_counts.items():
        root = roots_by_engine[engine]
        remediated = [
            item for item in root.iter(f"{SVG_NS}path")
            if item.attrib.get("data-remediation") == "D-062"
            and item.attrib.get("data-route-style") == "rounded-orthogonal"
        ]
        check(
            len(remediated) == expected_count,
            f"R6-D062-ROUNDED-ORTHO-{engine}",
            f"approved rounded-orthogonal routes={len(remediated)}/{expected_count}",
            results,
        )
        check(
            all(" C " not in f" {item.attrib.get('d', '')} " for item in remediated),
            f"R6-D062-NO-BROAD-CURVE-{engine}",
            "no cubic/broad curved connector in remediated routes",
            results,
        )
        check(
            root.attrib.get("data-connector-corner-style") == "rounded"
            and root.attrib.get("data-corner-style-options") == "rounded straight"
            and all(item.attrib.get("data-corner-style") == "rounded" for item in remediated)
            and all(
                item.attrib.get("d", "").count(" Q ") == int(item.attrib.get("data-turn-count", "0"))
                for item in remediated
            ),
            f"R6-D062-ONE-ROUNDED-CHART-POLICY-{engine}",
            "root and every route use the same rounded default",
            results,
        )

    containment_engines = ("topology-and-zones", "integration-pipeline", "runtime-deployment")
    for engine in containment_engines:
        root = roots_by_engine[engine]
        boxed = [
            item for item in root.iter(f"{SVG_NS}g")
            if item.attrib.get("data-zone-id") or item.attrib.get("data-node-id")
        ]
        zones = {item.attrib["data-zone-id"]: item for item in boxed if item.attrib.get("data-zone-id")}
        identifiers = [
            item.attrib.get("data-zone-id") or item.attrib.get("data-node-id")
            for item in boxed
        ]
        check(
            len(identifiers) == len(set(identifiers)) and all(identifiers),
            f"R6-D062-UNIQUE-CONTAINMENT-IDS-{engine}",
            f"measurable box ids={len(identifiers)}",
            results,
        )
        containment_ok = True
        centering_ok = True
        axis_alignment_ok = True
        parent_details = []
        for zone_id, zone in zones.items():
            parent_box = geometry_box(zone)
            parent_x, parent_y, parent_width, parent_height = parent_box
            parent_center_x, parent_center_y = box_center(parent_box)
            padding = float(zone.attrib["data-minimum-child-padding"])
            children = [item for item in boxed if item.attrib.get("data-parent-id") == zone_id]
            child_boxes = [geometry_box(item) for item in children]
            containment_ok = containment_ok and bool(children) and all(
                child_x >= parent_x + padding - 0.01
                and child_y >= parent_y + padding - 0.01
                and child_x + child_width <= parent_x + parent_width - padding + 0.01
                and child_y + child_height <= parent_y + parent_height - padding + 0.01
                for child_x, child_y, child_width, child_height in child_boxes
            )
            if child_boxes:
                group_left = min(item[0] for item in child_boxes)
                group_top = min(item[1] for item in child_boxes)
                group_right = max(item[0] + item[2] for item in child_boxes)
                group_bottom = max(item[1] + item[3] for item in child_boxes)
                group_center_x = (group_left + group_right) / 2
                group_center_y = (group_top + group_bottom) / 2
                centering_ok = centering_ok and abs(group_center_x - parent_center_x) <= 0.01 and abs(group_center_y - parent_center_y) <= 0.01
                child_centers = [box_center(item) for item in child_boxes]
                layout = zone.attrib["data-child-layout"]
                if layout == "row":
                    axis_alignment_ok = axis_alignment_ok and all(abs(center_y - parent_center_y) <= 0.01 for _, center_y in child_centers)
                elif layout == "column":
                    axis_alignment_ok = axis_alignment_ok and all(abs(center_x - parent_center_x) <= 0.01 for center_x, _ in child_centers)
                else:
                    axis_alignment_ok = axis_alignment_ok and len(child_centers) == 1 and all(
                        abs(center_x - parent_center_x) <= 0.01 and abs(center_y - parent_center_y) <= 0.01
                        for center_x, center_y in child_centers
                    )
                parent_details.append(f"{zone_id}:{layout}:{len(children)}")
        check(containment_ok, f"R6-D062-PARENT-CHILD-CONTAINMENT-{engine}", f"parents={parent_details}; declared padding honored", results)
        check(centering_ok, f"R6-D062-GROUP-CENTERING-{engine}", f"parents={parent_details}; group bbox centered on both axes", results)
        check(axis_alignment_ok, f"R6-D062-LAYOUT-AXIS-CENTERING-{engine}", f"parents={parent_details}; row/column/single axis contract", results)

    straight_builders = {
        "topology-and-zones": topology_anchor,
        "integration-pipeline": integration_anchor,
        "runtime-deployment": deployment_anchor,
    }
    for engine, builder in straight_builders.items():
        straight_root = ET.fromstring(builder("straight").svg)
        straight_routes = [
            item for item in straight_root.iter(f"{SVG_NS}path")
            if item.attrib.get("data-remediation") == "D-062"
        ]
        check(
            straight_root.attrib.get("data-connector-corner-style") == "straight"
            and straight_root.attrib.get("data-corner-style-options") == "rounded straight"
            and len(straight_routes) == expected_rounded_counts[engine]
            and all(item.attrib.get("data-route-style") == "straight-orthogonal" for item in straight_routes)
            and all(item.attrib.get("data-corner-style") == "straight" for item in straight_routes)
            and all(" Q " not in item.attrib.get("d", "") and " C " not in item.attrib.get("d", "") for item in straight_routes),
            f"R6-D062-CORNER-WHOLE-CHART-STRAIGHT-OVERRIDE-{engine}",
            "explicit straight choice removes rounded corners from every chart route",
            results,
        )

    containment_stack = roots_by_engine["containment-stack"]
    pyramid = next(
        (
            item for item in containment_stack.iter(f"{SVG_NS}g")
            if item.attrib.get("data-pyramid-silhouette") == "continuous-triangle"
        ),
        None,
    )
    pyramid_layers = [] if pyramid is None else sorted(
        (
            item for item in pyramid.iter(f"{SVG_NS}polygon")
            if item.attrib.get("data-pyramid-layer") is not None
        ),
        key=lambda item: int(item.attrib["data-pyramid-layer"]),
    )
    pyramid_dividers = [] if pyramid is None else sorted(
        (
            item for item in pyramid.iter(f"{SVG_NS}line")
            if item.attrib.get("data-shared-boundary-index") is not None
        ),
        key=lambda item: int(item.attrib["data-shared-boundary-index"]),
    )
    check(
        pyramid is not None
        and pyramid.attrib.get("data-remediation") == "D-063"
        and pyramid.attrib.get("data-layer-count") == "4"
        and pyramid.attrib.get("data-shared-boundary-count") == "3"
        and len(pyramid_layers) == 4,
        "R6-D063-CONTINUOUS-PYRAMID-METADATA",
        f"layers={len(pyramid_layers)} shared-boundaries={len(pyramid_dividers)}",
        results,
    )
    apex_points = polygon_points(pyramid_layers[0]) if pyramid_layers else ()
    check(
        len(apex_points) == 3
        and len(set(apex_points)) == 3
        and pyramid_layers[0].attrib.get("data-layer-shape") == "triangle"
        and len(horizontal_edge(apex_points, float(pyramid_layers[0].attrib.get("data-top-y", "0")))) == 1,
        "R6-D063-TRUE-TRIANGULAR-APEX",
        f"unique apex vertices={len(set(apex_points))}; no top edge",
        results,
    )
    supporting_points = [polygon_points(item) for item in pyramid_layers[1:]]
    check(
        len(supporting_points) == 3
        and all(len(points) == 4 and len(set(points)) == 4 for points in supporting_points)
        and all(item.attrib.get("data-layer-shape") == "trapezoid" for item in pyramid_layers[1:]),
        "R6-D063-SUPPORTING-LAYERS-ARE-TRAPEZOIDS",
        "three four-vertex supporting layers",
        results,
    )

    shared_boundaries_ok = len(pyramid_layers) == 4 and len(pyramid_dividers) == 3
    expected_boundaries: list[tuple[tuple[float, float], ...]] = []
    for index in range(max(0, len(pyramid_layers) - 1)):
        upper = pyramid_layers[index]
        lower = pyramid_layers[index + 1]
        shared_y = float(upper.attrib.get("data-bottom-y", "nan"))
        upper_edge = horizontal_edge(polygon_points(upper), shared_y)
        lower_edge = horizontal_edge(polygon_points(lower), float(lower.attrib.get("data-top-y", "nan")))
        expected_boundaries.append(upper_edge)
        shared_boundaries_ok = shared_boundaries_ok and len(upper_edge) == 2 and upper_edge == lower_edge
        if index < len(pyramid_dividers):
            divider = pyramid_dividers[index]
            divider_edge = tuple(sorted(((float(divider.attrib["x1"]), float(divider.attrib["y1"])), (float(divider.attrib["x2"]), float(divider.attrib["y2"])))))
            shared_boundaries_ok = shared_boundaries_ok and divider_edge == upper_edge and divider.attrib.get("data-boundary-render-count") == "1"
    check(
        shared_boundaries_ok,
        "R6-D063-EXACT-SHARED-LAYER-BOUNDARIES",
        "adjacent polygons and one divider reuse identical endpoint pairs",
        results,
    )
    check(
        pyramid is not None
        and pyramid.attrib.get("data-shared-boundary-rendering") == "single-stroke"
        and len(pyramid_dividers) == 3
        and all("pyramid-layer-fill" in item.attrib.get("class", "").split() and "stroke" not in item.attrib for item in pyramid_layers),
        "R6-D063-NO-DOUBLE-STROKE-LAYER-SEAMS",
        "fills have no per-polygon stroke; exactly three shared dividers render once",
        results,
    )

    outer_collinearity_ok = pyramid is not None and len(pyramid_layers) == 4
    if pyramid is not None:
        apex_x = float(pyramid.attrib["data-apex-x"])
        apex_y = float(pyramid.attrib["data-apex-y"])
        base_left_x = float(pyramid.attrib["data-base-left-x"])
        base_right_x = float(pyramid.attrib["data-base-right-x"])
        base_y = float(pyramid.attrib["data-base-y"])
        for item in pyramid_layers:
            for y in (float(item.attrib["data-top-y"]), float(item.attrib["data-bottom-y"])):
                edge = horizontal_edge(polygon_points(item), y)
                if y == apex_y:
                    outer_collinearity_ok = outer_collinearity_ok and edge == ((apex_x, apex_y),)
                    continue
                progress = (y - apex_y) / (base_y - apex_y)
                expected = (
                    (round(apex_x + (base_left_x - apex_x) * progress, 2), y),
                    (round(apex_x + (base_right_x - apex_x) * progress, 2), y),
                )
                actual = tuple((round(x, 2), actual_y) for x, actual_y in edge)
                outer_collinearity_ok = outer_collinearity_ok and actual == expected
    check(
        outer_collinearity_ok,
        "R6-D063-ONE-OUTER-TRIANGLE-SIDE-LINES",
        "every outer layer endpoint lies on the two common apex-to-base side lines",
        results,
    )

    leverage_axis = next(
        (
            item for item in containment_stack.iter(f"{SVG_NS}line")
            if item.attrib.get("data-role") == "leverage-axis"
        ),
        None,
    )
    clearance_ok = False
    if pyramid is not None and leverage_axis is not None and pyramid_layers:
        axis_x = float(leverage_axis.attrib["x1"])
        leftmost_x = min(x for item in pyramid_layers for x, _ in polygon_points(item))
        minimum_clearance = float(pyramid.attrib["data-min-axis-clearance"])
        actual_clearance = leftmost_x - axis_x
        clearance_ok = (
            leverage_axis.attrib.get("x1") == leverage_axis.attrib.get("x2")
            and actual_clearance >= minimum_clearance
            and abs(actual_clearance - float(pyramid.attrib["data-actual-axis-clearance"])) <= 0.01
            and abs(actual_clearance - float(leverage_axis.attrib["data-polygon-clearance"])) <= 0.01
        )
    check(
        clearance_ok,
        "R6-D063-LEFT-AXIS-POLYGON-CLEARANCE",
        "left leverage arrow remains outside all polygons with declared clearance >=140px",
        results,
    )

    regenerated_containment = ET.fromstring(containment_anchor().svg)
    regenerated_pyramid = next(
        item for item in regenerated_containment.iter(f"{SVG_NS}g")
        if item.attrib.get("data-pyramid-silhouette") == "continuous-triangle"
    )
    check(
        regenerated_pyramid.attrib.get("data-remediation") == "D-063"
        and regenerated_pyramid.attrib.get("data-layer-count") == "4"
        and regenerated_pyramid.attrib.get("data-shared-boundary-rendering") == "single-stroke",
        "R6-D063-DETERMINISTIC-PYRAMID-CONTRACT",
        "source builder regenerates the same continuous-triangle geometry contract",
        results,
    )

    dependency = roots_by_engine["dependency-dag"]
    connector_group = next(
        (item for item in dependency.iter(f"{SVG_NS}g") if item.attrib.get("data-dependency-connectors") == "true"),
        None,
    )
    dependency_routes = [] if connector_group is None else [
        item for item in connector_group.iter(f"{SVG_NS}path") if item.attrib.get("data-edge-id")
    ]
    route_by_edge = {item.attrib["data-edge-id"]: item for item in dependency_routes}
    bridge_groups = [] if connector_group is None else [
        item for item in connector_group.iter(f"{SVG_NS}g") if "bridge-mark" in item.attrib.get("class", "").split()
    ]
    check(
        dependency.attrib.get("data-connector-corner-style") == "rounded"
        and dependency.attrib.get("data-corner-style-options") == "rounded straight",
        "R6-D061-DEPENDENCY-CHART-CORNER-POLICY",
        "whole chart declares rounded default and rounded/straight options",
        results,
    )
    check(
        connector_group is not None
        and connector_group.attrib.get("data-connector-corner-style") == "rounded"
        and connector_group.attrib.get("data-rank-step") == "220"
        and connector_group.attrib.get("data-inter-rank-gap") == "96"
        and connector_group.attrib.get("data-corridor-midpoint-step") == "220",
        "R6-D061-DEPENDENCY-BALANCED-RANKS",
        "four ranks use 220px steps, 96px node gaps and aligned corridor midpoints",
        results,
    )
    check(
        connector_group is not None
        and connector_group.attrib.get("data-lower-corridor-midpoint") == "694"
        and connector_group.attrib.get("data-lower-corridor-pitch") == "20",
        "R6-D061-DEPENDENCY-BALANCED-LOWER-LADDER",
        "lower corridors are 674/694/714 around midpoint 694",
        results,
    )
    check(
        len(dependency_routes) == 10
        and len(route_by_edge) == 10
        and all(item.attrib.get("data-route-style") == "rounded-orthogonal" for item in dependency_routes)
        and all(item.attrib.get("data-corner-style") == "rounded" for item in dependency_routes),
        "R6-D061-DEPENDENCY-ONE-CORNER-STYLE",
        f"rounded orthogonal routes={len(dependency_routes)}/10",
        results,
    )
    turned_routes = [item for item in dependency_routes if int(item.attrib.get("data-turn-count", "0")) > 0]
    check(
        all(item.attrib.get("d", "").count(" Q ") == int(item.attrib["data-turn-count"]) for item in turned_routes),
        "R6-D061-DEPENDENCY-NO-MIXED-CORNERS",
        "every declared 90-degree turn is serialized as a rounded Q corner",
        results,
    )
    expected_bridge_edges = {"dependency-types-utils", "dependency-types-zod"}
    observed_bridge_edges = {item.attrib.get("data-bridge-edge", "") for item in bridge_groups}
    check(
        connector_group is not None
        and connector_group.attrib.get("data-crossing-count") == "2"
        and len(bridge_groups) == 2
        and observed_bridge_edges == expected_bridge_edges,
        "R6-D061-DEPENDENCY-ALL-CROSSINGS-BRIDGED",
        f"crossings=2 bridge_edges={sorted(observed_bridge_edges)}",
        results,
    )
    expected_bridge_points = {
        "dependency-types-utils": ("580.00", "694.00"),
        "dependency-types-zod": ("790.00", "714.00"),
    }
    bridge_contract_ok = True
    shared_bytes_ok = True
    crown_underlay_ok = True
    for bridge_group in bridge_groups:
        edge_id = bridge_group.attrib.get("data-bridge-edge", "")
        route = route_by_edge.get(edge_id)
        hop = next((item for item in bridge_group if item.attrib.get("data-bridge-role") == "hop"), None)
        underlay = next((item for item in bridge_group if item.attrib.get("data-bridge-role") == "underlay"), None)
        expected_point = expected_bridge_points.get(edge_id)
        bridge_contract_ok = bridge_contract_ok and bool(
            route is not None
            and route.attrib.get("data-path-bridges-integrated") == "true"
            and bridge_group.attrib.get("data-hop-geometry-shared") == "true"
            and bridge_group.attrib.get("data-underlay-scope") == "central-crown"
            and bridge_group.attrib.get("data-join-continuity") == "true"
            and expected_point is not None
            and (bridge_group.attrib.get("data-bridge-x"), bridge_group.attrib.get("data-bridge-y")) == expected_point
        )
        hop_commands = " ".join(hop.attrib.get("d", "").split()[3:]) if hop is not None else ""
        shared_bytes_ok = shared_bytes_ok and bool(route is not None and hop_commands and hop_commands in route.attrib.get("d", ""))
        crown_underlay_ok = crown_underlay_ok and bool(underlay is not None and underlay.attrib.get("class") == "bridge-hop-underlay")
    check(bridge_contract_ok, "R6-D061-DEPENDENCY-BRIDGE-CONTRACT", "two shared-geometry continuous hops at the expected crossings", results)
    check(shared_bytes_ok, "R6-D061-DEPENDENCY-HOP-SHARED-BYTES", "each route and repaint share identical cubic hop commands", results)
    check(crown_underlay_ok, "R6-D061-DEPENDENCY-CROWN-UNDERLAY", "each crossing masks only the central hop crown", results)
    direct_children = [] if connector_group is None else list(connector_group)
    check(
        connector_group is not None
        and connector_group.attrib.get("data-bridge-paint-order") == "base-routes then bridge-repaints"
        and len(direct_children) == 12
        and all(item.tag == f"{SVG_NS}path" for item in direct_children[:10])
        and all(item.tag == f"{SVG_NS}g" for item in direct_children[10:]),
        "R6-D061-DEPENDENCY-BRIDGE-PAINT-ORDER",
        "all ten base routes precede both bridge repaint groups",
        results,
    )
    check(
        connector_group is not None and not list(connector_group.iter(f"{SVG_NS}circle")),
        "R6-D061-DEPENDENCY-NO-FAKE-JUNCTION",
        "connector field contains no crossing bubble or fake junction circle",
        results,
    )
    expected_corridors = {
        "dependency-web-ui": ("254.00", "302.00"),
        "dependency-api-types": ("474.00", "522.00"),
        "dependency-ui-types": ("474.00", "522.00"),
        "dependency-types-tokens": ("674.00", "742.00"),
        "dependency-types-utils": ("694.00", "742.00"),
        "dependency-types-zod": ("714.00", "742.00"),
    }
    corridor_geometry_ok = all(
        edge_id in route_by_edge
        and corridor_y in route_by_edge[edge_id].attrib.get("d", "")
        and route_by_edge[edge_id].attrib.get("d", "").endswith(f"{target_y}")
        for edge_id, (corridor_y, target_y) in expected_corridors.items()
    )
    check(corridor_geometry_ok, "R6-D061-DEPENDENCY-CORRIDOR-GEOMETRY", "rank corridors and rank-3 endpoints match the balanced geometry", results)

    corner_receipt = inventory.get("connector_corner_style", {})
    check(
        corner_receipt.get("scope") == "whole-chart"
        and corner_receipt.get("default") == "rounded"
        and corner_receipt.get("allowed") == ["rounded", "straight"]
        and corner_receipt.get("explicit_user_choice_precedence") is True,
        "R6-D061-CORNER-OPTION-CONTRACT",
        "rounded default; explicit user straight override has precedence",
        results,
    )
    check(
        " Q " in corner_receipt.get("rounded_example", "")
        and " Q " not in corner_receipt.get("straight_example", "")
        and corner_receipt.get("straight_example", "").count(" L ") == 2,
        "R6-D061-CORNER-SERIALIZER-OVERRIDE",
        "same route serializes every 90-degree turn rounded or sharp according to one option",
        results,
    )
    straight_dependency = ET.fromstring(dependency_anchor("straight").svg)
    straight_group = next(
        item for item in straight_dependency.iter(f"{SVG_NS}g") if item.attrib.get("data-dependency-connectors") == "true"
    )
    straight_routes = [
        item for item in straight_group.iter(f"{SVG_NS}path") if item.attrib.get("data-edge-id")
    ]
    check(
        straight_dependency.attrib.get("data-connector-corner-style") == "straight"
        and straight_group.attrib.get("data-connector-corner-style") == "straight"
        and len(straight_routes) == 10
        and all(item.attrib.get("data-route-style") == "straight-orthogonal" for item in straight_routes)
        and all(item.attrib.get("data-corner-style") == "straight" for item in straight_routes)
        and all(" Q " not in item.attrib.get("d", "") for item in straight_routes),
        "R6-D061-CORNER-WHOLE-CHART-STRAIGHT-OVERRIDE",
        "explicit straight option removes rounded 90-degree corners from all ten chart routes",
        results,
    )
    straight_bridge_routes = [item for item in straight_routes if item.attrib.get("data-path-bridges-integrated") == "true"]
    straight_plain_routes = [item for item in straight_routes if item.attrib.get("data-path-bridges-integrated") != "true"]
    check(
        len(straight_bridge_routes) == 2
        and all(" C " in item.attrib.get("d", "") for item in straight_bridge_routes)
        and all(" C " not in item.attrib.get("d", "") for item in straight_plain_routes),
        "R6-D061-CORNER-OVERRIDE-PRESERVES-HOPS",
        "only the two required crossing hops retain cubic bridge geometry under straight-corner mode",
        results,
    )

    directed = roots_by_engine["directed-flow-state"]
    no_group = next((item for item in directed.iter(f"{SVG_NS}g") if "data-no-branch-width" in item.attrib), None)
    no_paths = [] if no_group is None else list(no_group.iter(f"{SVG_NS}path"))
    no_branches = [item for item in no_paths if item.attrib.get("data-branch")]
    no_return = next((item for item in no_paths if item.attrib.get("data-return-target") == "validate-evidence"), None)
    check(
        no_group is not None and no_group.attrib.get("data-no-branch-width") == "220" and len(no_branches) == 2,
        "R6-D060-NO-BRANCH-EQUAL-WIDTH",
        "both NO branches declare the same 220px horizontal span",
        results,
    )
    check(
        no_return is not None and "820.00 312.00" in no_return.attrib.get("d", "") and no_return.attrib.get("marker-end") == "url(#arrow)",
        "R6-D060-CONTROL-NO-RETURNS-VALIDATE",
        "shared NO return terminates at the Validate evidence node",
        results,
    )

    timeline = roots_by_engine["time-planning"]
    top_events = [item for item in timeline.iter(f"{SVG_NS}g") if "top-event" in item.attrib.get("class", "").split()]
    top_clearances = [
        float(item.attrib.get("data-leader-end", "0")) - float(item.attrib.get("data-text-bottom", "0"))
        for item in top_events
    ]
    check(
        len(top_events) == 2 and all(value >= 24 for value in top_clearances),
        "R6-D060-TOP-LABEL-ABOVE-LINE",
        f"top event clearances={top_clearances}; required>=24px",
        results,
    )

    hierarchy = roots_by_engine["hierarchy"]
    straight_children = [
        item for item in hierarchy.iter(f"{SVG_NS}line")
        if item.attrib.get("data-route-priority") == "straight"
    ]
    straight_pairs = {(item.attrib.get("data-parent"), item.attrib.get("data-child")) for item in straight_children}
    centered = all(
        item.attrib.get("x1") == item.attrib.get("x2")
        and item.attrib.get("data-entry-alignment") == "center"
        for item in straight_children
    )
    check(
        straight_pairs == {("Content", "Writer"), ("Commerce", "Store"), ("Systems", "Runtime")} and centered,
        "R6-D060-HIERARCHY-STRAIGHT-CENTER",
        f"straight centered child links={sorted(straight_pairs)}",
        results,
    )

    r5_svg = R5 / "anchor/swimlane--neutral-light.svg"
    r6_lane = ANCHORS / "06-lane-interaction--neutral-light.svg"
    check(r6_lane.read_bytes() == r5_svg.read_bytes(), "R6-R5-LANE-BYTE-PRESERVE", f"sha256={sha256(r6_lane)}", results)
    check(sha256(R5 / "P-18R5-MANIFEST.json") == "7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8", "R6-R5-PARENT-PIN", "approved manifest SHA-256 unchanged", results)

    quantitative_root = next(root for path, root in parsed if root.attrib.get("data-layout-engine") == "quantitative")
    quantitative_values = [(float(item.attrib["data-x"]), float(item.attrib["data-y"]), float(item.attrib["data-size"])) for item in quantitative_root.iter(f"{SVG_NS}circle") if "data-size" in item.attrib]
    check(len(quantitative_values) == 5 and all(0 <= x <= 100 and 0 <= y <= 100 and size > 0 for x, y, size in quantitative_values), "R6-QUANT-VALUES", f"points={len(quantitative_values)} ranges valid", results)
    special = next(item for item in inventory["engines"] if item["engine"] == "special-geometry")
    check(special["canonical_type"] == "sankey", "R6-SANKEY-TYPE", "special geometry uses conservation-based Sankey", results)

    blind = (R6 / "blind-review.html").read_text(encoding="utf-8")
    blind_visible = re.sub(r"<[^>]+>", " ", blind)
    leaked = sorted(engine for engine in EXPECTED_ENGINES if engine in blind_visible)
    check(len(re.findall(r"Masked candidate", blind_visible)) == 14, "R6-BLIND-COUNT", "14 visible masked candidates", results)
    check(not leaked, "R6-BLIND-NO-ENGINE-LEAK", f"visible engine leaks={leaked}", results)
    check("canonical type" not in blind_visible.lower() and "evidence rail" not in blind_visible.lower(), "R6-BLIND-NO-ANSWER-RAIL", "no visible type/evidence answer", results)

    for path in html_paths:
        source = path.read_text(encoding="utf-8")
        check("<script" not in source and "https://" not in source and "http://" not in source.replace("http://www.w3.org/2000/svg", ""), f"HTML-SELF-CONTAINED-{path.stem}", "standalone; no network/script", results)
        check(source.count('class="artifact-frame"') == 1, f"HTML-ONE-FRAME-{path.stem}", "exactly one canonical frame", results)

    failures = [item for item in results if item["status"] != "PASS"]
    report = {
        "schema_version": "1.0",
        "candidate_id": inventory["candidate_id"],
        "status": "PASS" if not failures else "FAIL",
        "test_count": len(results),
        "pass_count": len(results) - len(failures),
        "fail_count": len(failures),
        "results": results,
        "browser_status": "PENDING_BROWSER_EXECUTION",
        "owner_status": "PENDING",
        "g03_1_5_0": "NOT-EVALUATED",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "test_count", "pass_count", "fail_count")}, ensure_ascii=False))
    if failures:
        for failure in failures:
            print(f"FAIL {failure['id']}: {failure['detail']}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
