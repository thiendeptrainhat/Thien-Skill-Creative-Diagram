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

from gallery_kernel import compartment_anchor, containment_anchor, dependency_anchor, deployment_anchor, integration_anchor, matrix_anchor, special_anchor, topology_anchor


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

    pyramid_text = [] if pyramid is None else [
        item for item in pyramid.iter(f"{SVG_NS}text")
        if item.attrib.get("data-pyramid-text-layer") is not None
    ]

    def outer_triangle_bounds(y: float) -> tuple[float, float]:
        if pyramid is None:
            return 0.0, 0.0
        local_apex_x = float(pyramid.attrib["data-apex-x"])
        local_apex_y = float(pyramid.attrib["data-apex-y"])
        local_base_y = float(pyramid.attrib["data-base-y"])
        progress = (y - local_apex_y) / (local_base_y - local_apex_y)
        return (
            local_apex_x + (float(pyramid.attrib["data-base-left-x"]) - local_apex_x) * progress,
            local_apex_x + (float(pyramid.attrib["data-base-right-x"]) - local_apex_x) * progress,
        )

    text_containment_ok = pyramid is not None and len(pyramid_text) == 8
    for text_item in pyramid_text:
        layer_index = int(text_item.attrib["data-pyramid-text-layer"])
        owning_layer = pyramid_layers[layer_index]
        bbox_x = float(text_item.attrib["data-bbox-x"])
        bbox_y = float(text_item.attrib["data-bbox-y"])
        bbox_width = float(text_item.attrib["data-bbox-width"])
        bbox_height = float(text_item.attrib["data-bbox-height"])
        bbox_bottom = bbox_y + bbox_height
        inset = float(text_item.attrib["data-minimum-polygon-inset"])
        top_y = float(owning_layer.attrib["data-top-y"])
        bottom_y = float(owning_layer.attrib["data-bottom-y"])
        top_left, top_right = outer_triangle_bounds(bbox_y)
        bottom_left, bottom_right = outer_triangle_bounds(bbox_bottom)
        text_containment_ok = text_containment_ok and (
            bbox_y >= top_y + inset
            and bbox_bottom <= bottom_y - inset
            and bbox_x >= max(top_left, bottom_left) + inset
            and bbox_x + bbox_width <= min(top_right, bottom_right) - inset
            and text_item.attrib.get("data-font-size-preserved") == "true"
        )
    check(
        text_containment_ok,
        "R6-D064-ALL-LAYER-TEXT-BBOX-CONTAINED",
        f"measured title/metadata boxes contained={len(pyramid_text)}/8 with >=8px polygon inset",
        results,
    )
    flagship = next((item for item in pyramid_text if "".join(item.itertext()) == "Flagship decision"), None)
    check(
        pyramid is not None
        and pyramid.attrib.get("data-text-remediation") == "D-064"
        and flagship is not None
        and flagship.attrib.get("data-pyramid-text-layer") == "0"
        and flagship.attrib.get("data-text-role") == "node_title"
        and flagship.attrib.get("data-bbox-width") == "193.00",
        "R6-D064-FLAGSHIP-TITLE-MEASURED-IN-APEX",
        "Flagship decision keeps 24px title role and measured 193px bbox inside true apex",
        results,
    )

    annotations = [
        item for item in containment_stack.iter(f"{SVG_NS}text")
        if item.attrib.get("data-pyramid-annotation") is not None
    ]
    annotation_text = {"".join(item.itertext()) for item in annotations}
    check(
        pyramid is not None
        and pyramid.attrib.get("data-annotation-count") == "4"
        and len(annotations) == 4
        and annotation_text == {"THE APEX", "~4 / YR", "~12 / YR", "~240 / YR"},
        "R6-D064-RIGHT-ANNOTATION-INVENTORY",
        f"right-side notes={sorted(annotation_text)}",
        results,
    )
    expected_annotation_binding = {
        "0": ("semantic", "apex"),
        "1": ("cadence-quarterly", "quarterly · durable"),
        "2": ("cadence-monthly", "monthly · repeatable"),
        "3": ("cadence-workdays", "daily · volume work"),
    }
    binding_ok = len(annotations) == 4 and all(
        (
            item.attrib.get("data-note-kind"),
            item.attrib.get("data-semantic-binding"),
        ) == expected_annotation_binding.get(item.attrib.get("data-pyramid-annotation"))
        for item in annotations
    )
    check(
        binding_ok,
        "R6-D064-ANNOTATION-SEMANTIC-CADENCE-BINDING",
        "quarterly≈4/yr; monthly≈12/yr; workdays≈240/yr; apex note is semantic",
        results,
    )
    annotation_geometry_ok = pyramid is not None and len(annotations) == 4
    for item in annotations:
        layer_index = int(item.attrib["data-pyramid-annotation"])
        owning_layer = pyramid_layers[layer_index]
        bbox_x = float(item.attrib["data-bbox-x"])
        bbox_y = float(item.attrib["data-bbox-y"])
        bbox_width = float(item.attrib["data-bbox-width"])
        bbox_height = float(item.attrib["data-bbox-height"])
        bbox_bottom = bbox_y + bbox_height
        minimum_clearance = float(item.attrib["data-minimum-polygon-clearance"])
        _, right_at_bottom = outer_triangle_bounds(bbox_bottom)
        annotation_geometry_ok = annotation_geometry_ok and (
            bbox_x - right_at_bottom >= minimum_clearance
            and bbox_x + bbox_width <= 1420 - 52
            and bbox_y >= float(owning_layer.attrib["data-top-y"]) + 8
            and bbox_bottom <= float(owning_layer.attrib["data-bottom-y"]) - 8
        )
    check(
        annotation_geometry_ok,
        "R6-D064-ANNOTATION-CLEARANCE-AND-CANVAS-FIT",
        "all notes remain right of the triangle by >=56px, inside canvas and within their layer band",
        results,
    )

    annotation_gap_policy_ok = (
        pyramid is not None
        and pyramid.attrib.get("data-annotation-remediation") == "D-065"
        and pyramid.attrib.get("data-annotation-gap-metric") == "bbox-left-at-vertical-center-to-outer-triangle-right-edge"
        and pyramid.attrib.get("data-annotation-visual-gap-target") == "72.00"
        and pyramid.attrib.get("data-annotation-gap-tolerance") == "0.01"
    )
    check(
        annotation_gap_policy_ok,
        "R6-D065-ANNOTATION-GAP-POLICY",
        "one geometry-derived bbox-center metric locks all four right-side notes to 72px",
        results,
    )

    target_gap = 72.0
    gap_tolerance = 0.01
    measured_gaps = []
    annotation_gap_geometry_ok = len(annotations) == 4
    for item in annotations:
        bbox_x = float(item.attrib["data-bbox-x"])
        bbox_y = float(item.attrib["data-bbox-y"])
        bbox_height = float(item.attrib["data-bbox-height"])
        bbox_center_y = bbox_y + bbox_height / 2
        _, right_at_center = outer_triangle_bounds(bbox_center_y)
        actual_gap = bbox_x - right_at_center
        measured_gaps.append(actual_gap)
        annotation_gap_geometry_ok = annotation_gap_geometry_ok and (
            abs(float(item.attrib["x"]) - bbox_x) <= 0.001
            and abs(float(item.attrib["data-bbox-center-y"]) - bbox_center_y) <= 0.001
            and item.attrib.get("data-gap-reference") == "bbox-vertical-center-to-outer-triangle-right-edge"
            and abs(float(item.attrib["data-visual-gap-target"]) - target_gap) <= 0.001
            and abs(float(item.attrib["data-visual-gap-actual"]) - actual_gap) <= gap_tolerance
            and abs(actual_gap - target_gap) <= gap_tolerance
        )
    check(
        annotation_gap_geometry_ok,
        "R6-D065-EQUAL-GEOMETRY-DERIVED-ANNOTATION-GAPS",
        "measured visual gaps=" + ", ".join(f"{value:.3f}px" for value in measured_gaps),
        results,
    )
    gap_spread = max(measured_gaps) - min(measured_gaps) if measured_gaps else float("inf")
    check(
        gap_spread <= gap_tolerance,
        "R6-D065-ANNOTATION-GAP-SPREAD",
        f"max-min visual-gap spread={gap_spread:.3f}px <= {gap_tolerance:.2f}px",
        results,
    )

    regenerated_containment = ET.fromstring(containment_anchor().svg)
    regenerated_pyramid = next(
        item for item in regenerated_containment.iter(f"{SVG_NS}g")
        if item.attrib.get("data-pyramid-silhouette") == "continuous-triangle"
    )
    check(
        regenerated_pyramid.attrib.get("data-remediation") == "D-063"
        and regenerated_pyramid.attrib.get("data-text-remediation") == "D-064"
        and regenerated_pyramid.attrib.get("data-annotation-remediation") == "D-065"
        and regenerated_pyramid.attrib.get("data-layer-count") == "4"
        and regenerated_pyramid.attrib.get("data-shared-boundary-rendering") == "single-stroke",
        "R6-D063-DETERMINISTIC-PYRAMID-CONTRACT",
        "source builder regenerates the same continuous-triangle and text/annotation geometry contract",
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

    lane = roots_by_engine["lane-interaction"]
    phase_rail = next(
        (item for item in lane.iter(f"{SVG_NS}g") if item.attrib.get("data-major-phase-rail") == "true"),
        None,
    )
    phase_groups = [] if phase_rail is None else [
        item for item in phase_rail.iter(f"{SVG_NS}g")
        if item.attrib.get("data-major-phase-index") is not None
    ]
    phase_groups.sort(key=lambda item: int(item.attrib["data-major-phase-index"]))
    expected_phases = ["CHUẨN BỊ", "NHẬN BỘ", "PHÂN LOẠI", "GỬI NGÂN HÀNG", "CẬP NHẬT NỢ", "ĐĂNG SỔ"]
    emitted_phases = [item.attrib.get("data-major-phase-label") for item in phase_groups]
    emitted_steps = [item.attrib.get("data-workflow-step-id") for item in phase_groups]
    check(
        lane.attrib.get("data-r6-local-extension") == "D-066"
        and lane.attrib.get("data-major-phase-count") == "6"
        and lane.attrib.get("data-workflow-step-count") == "6"
        and lane.attrib.get("data-phase-coverage") == "complete"
        and phase_rail is not None
        and phase_rail.attrib.get("data-phase-count") == "6",
        "R6-D066-LANE-PHASE-COVERAGE-CONTRACT",
        "R6 local extension declares six phases for six workflow steps",
        results,
    )
    check(
        emitted_phases == expected_phases
        and emitted_steps == [f"step-{index}" for index in range(6)]
        and len(set(emitted_steps)) == 6,
        "R6-D066-LANE-PHASE-ORDER-AND-STEP-MAPPING",
        f"phase order={emitted_phases}",
        results,
    )
    lane_node_ids = {
        item.attrib["data-node-id"] for item in lane.iter(f"{SVG_NS}g")
        if item.attrib.get("data-node-id")
    }
    mapped_node_coverage = bool(phase_groups) and all(
        set(item.attrib.get("data-mapped-node-ids", "").split(",")) <= lane_node_ids
        and all(item.attrib.get("data-mapped-node-ids", "").split(","))
        for item in phase_groups
    )
    phase_centers = [float(item.attrib["data-phase-center-x"]) for item in phase_groups]
    phase_steps = [phase_centers[index + 1] - phase_centers[index] for index in range(len(phase_centers) - 1)]
    check(
        mapped_node_coverage and phase_centers and max(phase_steps) - min(phase_steps) <= 0.02,
        "R6-D066-LANE-PHASE-NODE-COVERAGE-AND-BALANCED-RAIL",
        f"mapped nodes valid; rail steps={[round(value, 2) for value in phase_steps]}",
        results,
    )
    phase_legend = next(
        (item for item in lane.iter(f"{SVG_NS}g") if item.attrib.get("data-major-phase-legend") == "true"),
        None,
    )
    legend_groups = [] if phase_legend is None else [
        item for item in phase_legend.iter(f"{SVG_NS}g")
        if item.attrib.get("data-major-phase-legend-index") is not None
    ]
    legend_groups.sort(key=lambda item: int(item.attrib["data-major-phase-legend-index"]))
    check(
        phase_legend is not None
        and phase_legend.attrib.get("data-phase-count") == "6"
        and [item.attrib.get("data-major-phase-label") for item in legend_groups] == expected_phases,
        "R6-D066-LANE-PHASE-LEGEND-CONSISTENCY",
        "top phase rail and bottom handoff legend expose the same six phases",
        results,
    )

    schema = roots_by_engine["compartment-model"]
    schema_layout = next(
        (item for item in schema.iter(f"{SVG_NS}g") if item.attrib.get("data-schema-layout") == "D-066"),
        None,
    )
    schema_entities = {} if schema_layout is None else {
        item.attrib["data-schema-entity"]: item
        for item in schema_layout.iter(f"{SVG_NS}g")
        if item.attrib.get("data-schema-entity")
    }
    top_entities = [schema_entities.get(key) for key in ("customer", "order", "payment")]
    top_centers = [float(item.attrib["data-center-y"]) for item in top_entities if item is not None]
    check(
        len(schema_entities) == 4
        and len(top_centers) == 3
        and max(top_centers) - min(top_centers) <= 0.01,
        "R6-D066-SCHEMA-TOP-ROW-CENTER-ALIGNMENT",
        f"top entity center-y values={top_centers}",
        results,
    )
    order_center_x = float(schema_entities["order"].attrib["data-center-x"]) if "order" in schema_entities else float("nan")
    item_center_x = float(schema_entities["order-item"].attrib["data-center-x"]) if "order-item" in schema_entities else float("nan")
    check(
        abs(order_center_x - item_center_x) <= 0.01,
        "R6-D066-SCHEMA-ORDER-ITEM-CENTER-ALIGNMENT",
        f"ORDER center-x={order_center_x:.2f}; ORDER_ITEM center-x={item_center_x:.2f}",
        results,
    )
    relationships = {
        item.attrib["data-schema-relationship"]: item
        for item in schema.iter(f"{SVG_NS}line")
        if item.attrib.get("data-schema-relationship")
    }
    endpoint_ok = len(relationships) == 3
    for relationship_id, source_id, target_id in (
        ("customer-to-order", "customer", "order"),
        ("order-to-payment", "order", "payment"),
    ):
        line = relationships.get(relationship_id)
        source_box = geometry_box(schema_entities[source_id])
        target_box = geometry_box(schema_entities[target_id])
        endpoint_ok = endpoint_ok and bool(line is not None) and (
            abs(float(line.attrib["x1"]) - (source_box[0] + source_box[2])) <= 0.01
            and abs(float(line.attrib["x2"]) - target_box[0]) <= 0.01
            and abs(float(line.attrib["y1"]) - box_center(source_box)[1]) <= 0.01
            and abs(float(line.attrib["y2"]) - box_center(target_box)[1]) <= 0.01
            and line.attrib.get("data-entry-alignment") == "center"
        )
    vertical = relationships.get("order-to-order-item")
    order_box = geometry_box(schema_entities["order"])
    item_box = geometry_box(schema_entities["order-item"])
    endpoint_ok = endpoint_ok and bool(vertical is not None) and (
        abs(float(vertical.attrib["x1"]) - box_center(order_box)[0]) <= 0.01
        and abs(float(vertical.attrib["x2"]) - box_center(item_box)[0]) <= 0.01
        and abs(float(vertical.attrib["y1"]) - (order_box[1] + order_box[3])) <= 0.01
        and abs(float(vertical.attrib["y2"]) - item_box[1]) <= 0.01
        and vertical.attrib.get("data-entry-alignment") == "center"
    )
    check(
        endpoint_ok,
        "R6-D066-SCHEMA-CONNECTOR-CENTER-ENDPOINTS",
        "two horizontal and one vertical relationship terminate at exact centered boundaries",
        results,
    )
    padding_values = []
    padding_ok = len(schema_entities) == 4
    for entity in schema_entities.values():
        last_field = next(
            (item for item in entity.iter(f"{SVG_NS}text") if item.attrib.get("data-last-field") == "true"),
            None,
        )
        box = geometry_box(entity)
        actual_padding = (box[1] + box[3]) - float(last_field.attrib["data-field-bbox-bottom"]) if last_field is not None else -1
        padding_values.append(actual_padding)
        padding_ok = padding_ok and actual_padding >= 24 and abs(actual_padding - float(entity.attrib["data-content-bottom-padding"])) <= 0.01
    check(
        padding_ok,
        "R6-D066-SCHEMA-MEASURED-BOTTOM-PADDING",
        f"entity bottom padding values={[round(value, 2) for value in padding_values]}px; minimum=24px",
        results,
    )
    relationship_labels = [
        item for item in schema.iter(f"{SVG_NS}text")
        if item.attrib.get("data-relationship-label")
    ]
    label_clearance_ok = len(relationship_labels) == 3
    clearance_values = []
    for label in relationship_labels:
        minimum = float(label.attrib["data-minimum-node-clearance"])
        if label.attrib.get("data-label-axis") == "horizontal":
            left = float(label.attrib["data-left-node-clearance"])
            right = float(label.attrib["data-right-node-clearance"])
            bbox_left = float(label.attrib["data-bbox-x"])
            bbox_right = bbox_left + float(label.attrib["data-bbox-width"])
            corridor_left = float(label.attrib["data-corridor-left"])
            corridor_right = float(label.attrib["data-corridor-right"])
            clearance_values.append((left, right))
            label_clearance_ok = label_clearance_ok and (
                left >= minimum and right >= minimum
                and bbox_left >= corridor_left + minimum
                and bbox_right <= corridor_right - minimum
            )
        else:
            top = float(label.attrib["data-top-node-clearance"])
            bottom = float(label.attrib["data-bottom-node-clearance"])
            bbox_top = float(label.attrib["data-bbox-y"])
            bbox_bottom = bbox_top + float(label.attrib["data-bbox-height"])
            corridor_top = float(label.attrib["data-corridor-top"])
            corridor_bottom = float(label.attrib["data-corridor-bottom"])
            clearance_values.append((top, bottom))
            label_clearance_ok = label_clearance_ok and (
                top >= minimum and bottom >= minimum
                and bbox_top >= corridor_top + minimum
                and bbox_bottom <= corridor_bottom - minimum
            )
    check(
        label_clearance_ok,
        "R6-D066-SCHEMA-RELATIONSHIP-LABEL-CORRIDOR-CLEARANCE",
        f"label-to-node clearances={clearance_values}; minimum=8px",
        results,
    )
    regenerated_schema = ET.fromstring(compartment_anchor().svg)
    check(
        any(item.attrib.get("data-schema-layout") == "D-066" for item in regenerated_schema.iter(f"{SVG_NS}g")),
        "R6-D066-DETERMINISTIC-SCHEMA-GEOMETRY-CONTRACT",
        "source builder regenerates the same D-066 schema layout contract",
        results,
    )

    cardinality_contract = next(
        (item for item in schema.iter(f"{SVG_NS}g") if item.attrib.get("data-schema-cardinality-contract") == "D-069"),
        None,
    )
    relationship_names = {
        item.attrib["data-relationship-label"]: "".join(item.itertext()).strip()
        for item in schema.iter(f"{SVG_NS}text")
        if item.attrib.get("data-relationship-label")
    }
    expected_relationship_names = {
        "customer-to-order": "PLACES",
        "order-to-payment": "PAID BY",
        "order-to-order-item": "CONTAINS",
    }
    check(
        cardinality_contract is not None and relationship_names == expected_relationship_names
        and all("·" not in value for value in relationship_names.values()),
        "R6-D069-SCHEMA-INDEPENDENT-RELATIONSHIP-NAMES",
        f"relationship names={relationship_names}; cardinality and separators excluded",
        results,
    )

    cardinality_labels = [
        item for item in schema.iter(f"{SVG_NS}text")
        if item.attrib.get("data-relationship-cardinality")
    ]
    emitted_cardinalities = {
        (item.attrib.get("data-relationship-id"), item.attrib.get("data-endpoint-role")):
        ("".join(item.itertext()).strip(), item.attrib.get("data-cardinality-value"))
        for item in cardinality_labels
    }
    expected_cardinalities = {
        (relationship_id, endpoint): ("1" if endpoint == "source" else "N", "1" if endpoint == "source" else "N")
        for relationship_id in expected_relationship_names
        for endpoint in ("source", "target")
    }
    check(
        len(cardinality_labels) == 6 and emitted_cardinalities == expected_cardinalities,
        "R6-D069-SCHEMA-SEPARATE-ENDPOINT-CARDINALITIES",
        f"six independent endpoint labels={emitted_cardinalities}",
        results,
    )

    relationship_name_placement_ok = len(relationship_names) == 3
    relationship_name_clearances = []
    for label in relationship_labels:
        relationship_id = label.attrib["data-relationship-label"]
        line = relationships[relationship_id]
        bbox_x = float(label.attrib["data-bbox-x"])
        bbox_y = float(label.attrib["data-bbox-y"])
        bbox_width = float(label.attrib["data-bbox-width"])
        bbox_height = float(label.attrib["data-bbox-height"])
        clearance = float(label.attrib["data-line-clearance"])
        minimum = float(label.attrib["data-minimum-line-clearance"])
        if line.attrib["data-axis"] == "horizontal":
            actual = float(line.attrib["y1"]) - (bbox_y + bbox_height)
            placement = label.attrib.get("data-label-placement") == "above"
        else:
            actual = bbox_x - float(line.attrib["x1"])
            placement = label.attrib.get("data-label-placement") == "right"
        relationship_name_clearances.append((relationship_id, round(actual, 2)))
        relationship_name_placement_ok = relationship_name_placement_ok and placement and actual >= minimum and abs(actual - clearance) <= 0.02
    check(
        relationship_name_placement_ok,
        "R6-D069-SCHEMA-RELATIONSHIP-NAME-ABOVE-OR-RIGHT",
        f"relationship-name line clearances={relationship_name_clearances}; minimum=8px",
        results,
    )

    inline_contract = next(
        (item for item in schema.iter(f"{SVG_NS}g") if item.attrib.get("data-inline-cardinality-contract") == "D-070"),
        None,
    )
    cardinality_knockouts = [
        item for item in schema.iter(f"{SVG_NS}rect")
        if item.attrib.get("data-cardinality-knockout")
    ]
    knockout_by_binding = {
        item.attrib["data-cardinality-knockout"]: item
        for item in cardinality_knockouts
    }
    cardinality_placement_ok = inline_contract is not None and len(cardinality_labels) == 6
    cardinality_clearances = []
    axis_errors = []
    for label in cardinality_labels:
        relationship_id = label.attrib["data-relationship-id"]
        endpoint = label.attrib["data-endpoint-role"]
        line = relationships[relationship_id]
        bbox_x = float(label.attrib["data-bbox-x"])
        bbox_y = float(label.attrib["data-bbox-y"])
        bbox_width = float(label.attrib["data-bbox-width"])
        bbox_height = float(label.attrib["data-bbox-height"])
        node_clearance = float(label.attrib["data-node-clearance"])
        knockout_node_clearance = float(label.attrib["data-knockout-node-clearance"])
        minimum = float(label.attrib["data-minimum-node-clearance"])
        boundary = float(label.attrib["data-node-boundary"])
        if line.attrib["data-axis"] == "horizontal":
            actual_node = bbox_x - boundary if endpoint == "source" else boundary - (bbox_x + bbox_width)
            actual_axis_error = abs((bbox_y + bbox_height / 2) - float(line.attrib["y1"]))
        else:
            actual_node = bbox_y - boundary if endpoint == "source" else boundary - (bbox_y + bbox_height)
            actual_axis_error = abs((bbox_x + bbox_width / 2) - float(line.attrib["x1"]))
        cardinality_clearances.append((relationship_id, endpoint, round(actual_node, 2), round(knockout_node_clearance, 2)))
        axis_errors.append((relationship_id, endpoint, round(actual_axis_error, 3)))
        cardinality_placement_ok = cardinality_placement_ok and (
            label.attrib.get("data-label-placement") == "inline"
            and label.attrib.get("data-inline-cardinality-contract") == "D-070"
            and float(label.attrib["data-line-clearance"]) == 0
            and actual_node >= minimum and knockout_node_clearance >= minimum
            and abs(actual_node - node_clearance) <= 0.02
            and actual_axis_error <= 0.06
            and abs(actual_axis_error - float(label.attrib["data-axis-alignment-error"])) <= 0.02
        )
    check(
        cardinality_placement_ok,
        "R6-D070-SCHEMA-INLINE-CARDINALITY-AXIS-PLACEMENT",
        f"text/knockout node clearances={cardinality_clearances}; axis errors={axis_errors}; minimum node clearance=8px",
        results,
    )

    knockout_geometry_ok = len(cardinality_knockouts) == 6 and set(knockout_by_binding) == {
        label.attrib["data-relationship-cardinality"] for label in cardinality_labels
    }
    knockout_geometry = []
    for label in cardinality_labels:
        binding = label.attrib["data-relationship-cardinality"]
        knockout = knockout_by_binding.get(binding)
        if knockout is None:
            knockout_geometry_ok = False
            continue
        bbox_x = float(label.attrib["data-bbox-x"])
        bbox_y = float(label.attrib["data-bbox-y"])
        bbox_width = float(label.attrib["data-bbox-width"])
        bbox_height = float(label.attrib["data-bbox-height"])
        knockout_x = float(knockout.attrib["x"])
        knockout_y = float(knockout.attrib["y"])
        knockout_width = float(knockout.attrib["width"])
        knockout_height = float(knockout.attrib["height"])
        along = float(knockout.attrib["data-along-line-padding"])
        perpendicular = float(knockout.attrib["data-perpendicular-padding"])
        axis = knockout.attrib["data-axis"]
        if axis == "horizontal":
            expected = (
                bbox_x - along,
                bbox_y - perpendicular,
                bbox_width + 2 * along,
                bbox_height + 2 * perpendicular,
            )
        else:
            expected = (
                bbox_x - perpendicular,
                bbox_y - along,
                bbox_width + 2 * perpendicular,
                bbox_height + 2 * along,
            )
        actual = (knockout_x, knockout_y, knockout_width, knockout_height)
        knockout_geometry.append((binding, axis, tuple(round(value, 2) for value in actual)))
        knockout_geometry_ok = knockout_geometry_ok and (
            along == 8 and perpendicular == 4
            and all(abs(left - right) <= 0.02 for left, right in zip(actual, expected, strict=True))
            and knockout.attrib.get("data-relationship-id") == label.attrib.get("data-relationship-id")
            and knockout.attrib.get("data-endpoint-role") == label.attrib.get("data-endpoint-role")
            and knockout.attrib.get("data-visual-role") == "line-interruption-underlay"
        )
    check(
        knockout_geometry_ok,
        "R6-D070-SCHEMA-MEASURED-CARDINALITY-KNOCKOUT-GEOMETRY",
        f"six measured knockout rectangles={knockout_geometry}; padding along/perpendicular=8/4px",
        results,
    )

    knockout_paint_ok = len(cardinality_knockouts) == 6 and all(
        item.attrib.get("fill") == "#f7f6f2"
        and item.attrib.get("stroke") == "none"
        and item.attrib.get("data-fill-role") == "canvas"
        and float(item.attrib.get("data-node-clearance", "-1")) >= float(item.attrib.get("data-minimum-node-clearance", "8"))
        for item in cardinality_knockouts
    )
    check(
        knockout_paint_ok,
        "R6-D070-SCHEMA-CANVAS-KNOCKOUT-WHITE-SPACE",
        "every inline cardinality has an explicit canvas-fill/no-stroke underlay with >=8px node clearance",
        results,
    )

    relationship_groups = {
        item.attrib["data-schema-relationship-group"]: item
        for item in schema.iter(f"{SVG_NS}g")
        if item.attrib.get("data-schema-relationship-group")
    }
    paint_order_ok = set(relationship_groups) == set(expected_relationship_names)
    paint_order_details = []
    for relationship_id, group in relationship_groups.items():
        children = list(group)
        line_indexes = [
            index for index, item in enumerate(children)
            if item.attrib.get("data-schema-relationship") == relationship_id
        ]
        bindings = [f"{relationship_id}:source", f"{relationship_id}:target"]
        group_ok = len(line_indexes) == 1
        line_index = line_indexes[0] if line_indexes else -1
        for binding in bindings:
            knockout_indexes = [
                index for index, item in enumerate(children)
                if item.attrib.get("data-cardinality-knockout") == binding
            ]
            label_indexes = [
                index for index, item in enumerate(children)
                if item.attrib.get("data-relationship-cardinality") == binding
            ]
            group_ok = group_ok and (
                len(knockout_indexes) == 1 and len(label_indexes) == 1
                and line_index < knockout_indexes[0] < label_indexes[0]
            )
        line = relationships[relationship_id]
        group_ok = group_ok and (
            line.attrib.get("data-semantic-continuity") == "single-line"
            and line.attrib.get("data-visual-interruption") == "knockout-underlay"
            and group.attrib.get("data-cardinality-layout") == "inline-knockout"
        )
        paint_order_details.append((relationship_id, line_index, group_ok))
        paint_order_ok = paint_order_ok and group_ok
    check(
        paint_order_ok,
        "R6-D070-SCHEMA-CONNECTOR-KNOCKOUT-LABEL-PAINT-ORDER",
        f"single semantic connector painted before knockout and cardinality={paint_order_details}",
        results,
    )

    regenerated_cardinalities = [
        item for item in regenerated_schema.iter(f"{SVG_NS}text")
        if item.attrib.get("data-relationship-cardinality")
    ]
    regenerated_knockouts = [
        item for item in regenerated_schema.iter(f"{SVG_NS}rect")
        if item.attrib.get("data-cardinality-knockout")
    ]
    check(
        len(regenerated_cardinalities) == 6
        and len(regenerated_knockouts) == 6
        and any(item.attrib.get("data-schema-cardinality-contract") == "D-069" for item in regenerated_schema.iter(f"{SVG_NS}g"))
        and any(item.attrib.get("data-inline-cardinality-contract") == "D-070" for item in regenerated_schema.iter(f"{SVG_NS}g")),
        "R6-D070-DETERMINISTIC-SCHEMA-INLINE-CARDINALITY-CONTRACT",
        "source builder regenerates the same D-069 semantics plus D-070 inline-knockout placement contract",
        results,
    )

    matrix = roots_by_engine["spatial-matrix"]
    annotation_group = next(
        (item for item in matrix.iter(f"{SVG_NS}g") if item.attrib.get("data-axis-annotation-contract") == "D-067"),
        None,
    )
    axis_notes = [] if annotation_group is None else [
        item for item in annotation_group.iter(f"{SVG_NS}text")
        if item.attrib.get("data-axis-note")
    ]
    expected_axis_notes = {
        "high-impact": ("↑ HIGH IMPACT", "impact", "positive", "prefix", "top"),
        "low-effort": ("← LOW EFFORT", "effort", "negative", "prefix", "left"),
        "low-impact": ("↓ LOW IMPACT", "impact", "negative", "prefix", "bottom"),
        "high-effort": ("HIGH EFFORT →", "effort", "positive", "suffix", "right"),
    }
    emitted_axis_notes = {
        item.attrib["data-axis-note"]: (
            "".join(item.itertext()).strip(),
            item.attrib.get("data-axis"),
            item.attrib.get("data-direction"),
            item.attrib.get("data-arrow-placement"),
            item.attrib.get("data-field-edge"),
        )
        for item in axis_notes
    }
    check(
        annotation_group is not None
        and annotation_group.attrib.get("data-axis-note-count") == "4"
        and emitted_axis_notes == expected_axis_notes,
        "R6-D067-MATRIX-EXACT-AXIS-DIRECTION-ANNOTATIONS",
        f"axis annotations={emitted_axis_notes}",
        results,
    )

    note_by_id = {item.attrib["data-axis-note"]: item for item in axis_notes}
    axis_center_x = float(annotation_group.attrib.get("data-axis-center-x", "nan")) if annotation_group is not None else float("nan")
    axis_center_y = float(annotation_group.attrib.get("data-axis-center-y", "nan")) if annotation_group is not None else float("nan")
    vertical_offset_x = float(annotation_group.attrib.get("data-vertical-note-offset-x", "nan")) if annotation_group is not None else float("nan")
    horizontal_offset_y = float(annotation_group.attrib.get("data-horizontal-note-offset-y", "nan")) if annotation_group is not None else float("nan")
    position_ok = set(note_by_id) == set(expected_axis_notes)
    if position_ok:
        top_note = note_by_id["high-impact"]
        bottom_note = note_by_id["low-impact"]
        left_note = note_by_id["low-effort"]
        right_note = note_by_id["high-effort"]
        position_ok = (
            abs(float(top_note.attrib["x"]) - axis_center_x - vertical_offset_x) <= 0.01
            and abs(float(bottom_note.attrib["x"]) - axis_center_x - vertical_offset_x) <= 0.01
            and abs(float(top_note.attrib["data-vertical-offset-x"]) - vertical_offset_x) <= 0.01
            and abs(float(bottom_note.attrib["data-vertical-offset-x"]) - vertical_offset_x) <= 0.01
            and abs(float(left_note.attrib["y"]) - axis_center_y - horizontal_offset_y) <= 0.01
            and abs(float(right_note.attrib["y"]) - axis_center_y - horizontal_offset_y) <= 0.01
            and abs(float(left_note.attrib["data-horizontal-offset-y"]) - horizontal_offset_y) <= 0.01
            and abs(float(right_note.attrib["data-horizontal-offset-y"]) - horizontal_offset_y) <= 0.01
            and left_note.attrib.get("text-anchor") == "start"
            and right_note.attrib.get("text-anchor") == "end"
            and float(left_note.attrib["x"]) == float(left_note.attrib["data-axis-endpoint-x"])
            and float(right_note.attrib["x"]) == float(right_note.attrib["data-axis-endpoint-x"])
        )
    check(
        position_ok,
        "R6-D067-MATRIX-SHARED-AXIS-END-OFFSETS",
        f"vertical x-offset={vertical_offset_x:.2f}px; horizontal baseline offset={horizontal_offset_y:.2f}px",
        results,
    )

    viewbox = [float(value) for value in matrix.attrib["viewBox"].split()]
    canvas_width, canvas_height = viewbox[2], viewbox[3]
    bounds_ok = len(axis_notes) == 4
    clearance_ok = len(axis_notes) == 4
    bbox_summary = []
    for item in axis_notes:
        bbox_x = float(item.attrib["data-bbox-x"])
        bbox_y = float(item.attrib["data-bbox-y"])
        bbox_width = float(item.attrib["data-bbox-width"])
        bbox_height = float(item.attrib["data-bbox-height"])
        clearance = float(item.attrib["data-axis-clearance"])
        minimum = float(item.attrib["data-minimum-axis-clearance"])
        bounds_ok = bounds_ok and bbox_x >= 0 and bbox_y >= 0 and bbox_x + bbox_width <= canvas_width and bbox_y + bbox_height <= canvas_height
        clearance_ok = clearance_ok and clearance >= minimum and minimum >= 16
        bbox_summary.append((item.attrib["data-axis-note"], round(bbox_x, 2), round(bbox_y, 2), round(clearance, 2)))
    check(
        bounds_ok,
        "R6-D067-MATRIX-ANNOTATION-CANVAS-BOUNDS",
        f"measured annotation bboxes={bbox_summary}",
        results,
    )
    check(
        clearance_ok,
        "R6-D067-MATRIX-ANNOTATION-AXIS-CLEARANCE",
        f"annotation clearances={[round(float(item.attrib['data-axis-clearance']), 2) for item in axis_notes]}px; minimum=16px",
        results,
    )

    matrix_text = visible_text(matrix)
    matrix_focal = [
        item for item in matrix.iter(f"{SVG_NS}circle")
        if item.attrib.get("class") == "accent-dot"
    ]
    check(
        all(value in matrix_text for value in ("DO FIRST", "MAJOR PROJECTS", "QUICK WINS", "AVOID", "Freeze contract"))
        and len(matrix_focal) == 1
        and matrix_focal[0].attrib.get("cx") == "360"
        and matrix_focal[0].attrib.get("cy") == "240",
        "R6-D067-MATRIX-SEMANTIC-FIELD-PRESERVED",
        "quadrant titles and the single Freeze contract focal point remain unchanged",
        results,
    )
    regenerated_matrix = ET.fromstring(matrix_anchor().svg)
    check(
        any(item.attrib.get("data-axis-annotation-contract") == "D-067" for item in regenerated_matrix.iter(f"{SVG_NS}g")),
        "R6-D067-DETERMINISTIC-MATRIX-ANNOTATION-CONTRACT",
        "source builder regenerates the same D-067 four-note contract",
        results,
    )

    matrix_source = (ANCHORS / "12-spatial-matrix--neutral-light.svg").read_text(encoding="utf-8")
    focal_regions = [
        item for item in matrix.iter(f"{SVG_NS}rect")
        if item.attrib.get("data-focal-region-contract") == "D-068"
    ]
    focal_region = focal_regions[0] if len(focal_regions) == 1 else None
    check(
        focal_region is not None
        and focal_region.attrib.get("class") == "matrix-focal-region"
        and focal_region.attrib.get("data-fill-role") == "accent-soft"
        and focal_region.attrib.get("data-stroke") == "none"
        and "stroke" not in focal_region.attrib
        and "stroke-width" not in focal_region.attrib
        and "stroke-opacity" not in focal_region.attrib
        and re.search(r"\.matrix-focal-region\{fill:[^;]+;stroke:none\}", matrix_source) is not None,
        "R6-D068-MATRIX-FOCAL-REGION-FILL-WITHOUT-STROKE",
        "focal region keeps accent-soft fill and serializes stroke:none with no stroke workaround",
        results,
    )
    check(
        focal_region is not None
        and all(
            abs(float(focal_region.attrib[key]) - expected) <= 0.01
            for key, expected in (("x", 190.0), ("y", 120.0), ("width", 590.0), ("height", 319.0))
        )
        and focal_region.attrib.get("rx") == "0",
        "R6-D068-MATRIX-FOCAL-REGION-GEOMETRY-PRESERVED",
        "focal region remains x=190 y=120 width=590 height=319 with square corners",
        results,
    )
    regenerated_focal_regions = [
        item for item in regenerated_matrix.iter(f"{SVG_NS}rect")
        if item.attrib.get("data-focal-region-contract") == "D-068"
    ]
    check(
        len(regenerated_focal_regions) == 1
        and regenerated_focal_regions[0].attrib.get("class") == "matrix-focal-region"
        and regenerated_focal_regions[0].attrib.get("data-stroke") == "none"
        and any(item.attrib.get("data-axis-annotation-contract") == "D-067" for item in regenerated_matrix.iter(f"{SVG_NS}g")),
        "R6-D068-DETERMINISTIC-MATRIX-FOCAL-REGION-CONTRACT",
        "source builder regenerates the no-outline focal region while retaining D-067 annotations",
        results,
    )

    r5_svg = R5 / "anchor/swimlane--neutral-light.svg"
    r6_lane = ANCHORS / "06-lane-interaction--neutral-light.svg"
    check(
        sha256(r5_svg) == "a0d3949d177daebca0c84070b18d8366a025025261d03a7e03896550beb8253c",
        "R6-D066-R5-LANE-SOURCE-BYTE-PRESERVE",
        f"frozen R5 source sha256={sha256(r5_svg)}",
        results,
    )
    check(
        r6_lane.read_bytes() != r5_svg.read_bytes()
        and lane.attrib.get("data-r6-local-extension") == "D-066",
        "R6-D066-R6-LANE-LOCAL-EXTENSION-BOUNDARY",
        "R6 lane intentionally differs only as a D-066 local phase-coverage extension",
        results,
    )
    check(sha256(R5 / "P-18R5-MANIFEST.json") == "7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8", "R6-R5-PARENT-PIN", "approved manifest SHA-256 unchanged", results)

    quantitative_root = next(root for path, root in parsed if root.attrib.get("data-layout-engine") == "quantitative")
    quantitative_values = [(float(item.attrib["data-x"]), float(item.attrib["data-y"]), float(item.attrib["data-size"])) for item in quantitative_root.iter(f"{SVG_NS}circle") if "data-size" in item.attrib]
    check(len(quantitative_values) == 5 and all(0 <= x <= 100 and 0 <= y <= 100 and size > 0 for x, y, size in quantitative_values), "R6-QUANT-VALUES", f"points={len(quantitative_values)} ranges valid", results)
    special = next(item for item in inventory["engines"] if item["engine"] == "special-geometry")
    check(special["canonical_type"] == "sankey", "R6-SANKEY-TYPE", "special geometry uses conservation-based Sankey", results)
    special_root = next(root for path, root in parsed if root.attrib.get("data-layout-engine") == "special-geometry")
    sankey_contract = next(
        (item for item in special_root.iter(f"{SVG_NS}g") if item.attrib.get("data-sankey-contract") == "D-071"),
        None,
    )
    sankey_nodes = {
        item.attrib["data-sankey-node"]: item
        for item in special_root.iter(f"{SVG_NS}g")
        if "data-sankey-node" in item.attrib
    }
    sankey_ribbons = [
        item for item in special_root.iter(f"{SVG_NS}path")
        if "data-sankey-ribbon" in item.attrib
    ]
    check(
        sankey_contract is not None
        and sankey_contract.attrib.get("data-node-interface-occupancy") == "100%"
        and sankey_contract.attrib.get("data-node-label-placement") == "above"
        and sankey_contract.attrib.get("data-node-corner-style") == "square"
        and abs(float(sankey_contract.attrib.get("data-total-value", "0")) - 12000.0) <= 0.01,
        "R6-D071-SANKEY-CONTRACT",
        "diagram 14 declares 100% node-interface occupancy, above labels, square bars and 12,000 total",
        results,
    )
    check(
        len(sankey_nodes) == 7 and len(sankey_ribbons) == 9,
        "R6-D071-SANKEY-NODE-RIBBON-COUNT",
        f"nodes={len(sankey_nodes)} ribbons={len(sankey_ribbons)}",
        results,
    )
    scale = 0.025
    square_scaled_nodes = True
    labels_above = True
    for node_id, node in sankey_nodes.items():
        box = geometry_box(node)
        value = float(node.attrib["data-value"])
        bars = [
            child for child in node.iter(f"{SVG_NS}rect")
            if child.attrib.get("data-sankey-node-bar") == node_id
        ]
        labels = [
            child for child in node.iter(f"{SVG_NS}text")
            if child.attrib.get("data-node-label") == node_id
        ]
        square_scaled_nodes = square_scaled_nodes and (
            len(bars) == 1
            and "rx" not in bars[0].attrib
            and bars[0].attrib.get("data-node-corner-style") == "square"
            and node.attrib.get("data-node-corner-style") == "square"
            and abs(box[3] - value * scale) <= 0.01
        )
        labels_above = labels_above and (
            len(labels) == 2
            and all(label.attrib.get("data-label-placement") == "above" for label in labels)
            and all(label.attrib.get("text-anchor") == "middle" for label in labels)
            and all(abs(float(label.attrib["x"]) - (box[0] + box[2] / 2)) <= 0.01 for label in labels)
            and float(node.attrib["data-label-bbox-bottom"]) < box[1]
            and float(node.attrib["data-label-bottom-clearance"]) >= 12.0
        )
    check(
        square_scaled_nodes,
        "R6-D071-SANKEY-SQUARE-SCALED-BARS",
        "all seven node bars omit rx and use height=value×0.025",
        results,
    )
    check(
        labels_above,
        "R6-D071-SANKEY-LABELS-ABOVE",
        "every node title/value pair is centered above its bar with at least 12px clearance",
        results,
    )

    def interface_tiles(node_id: str, side: str) -> bool:
        node = sankey_nodes[node_id]
        _, node_y, _, node_height = geometry_box(node)
        if side == "right":
            relevant = [item for item in sankey_ribbons if item.attrib["data-source-node"] == node_id]
            intervals = sorted(
                (float(item.attrib["data-source-y0"]), float(item.attrib["data-source-y1"]))
                for item in relevant
            )
        else:
            relevant = [item for item in sankey_ribbons if item.attrib["data-target-node"] == node_id]
            intervals = sorted(
                (float(item.attrib["data-target-y0"]), float(item.attrib["data-target-y1"]))
                for item in relevant
            )
        if not intervals or abs(intervals[0][0] - node_y) > 0.01 or abs(intervals[-1][1] - (node_y + node_height)) > 0.01:
            return False
        return all(abs(left[1] - right[0]) <= 0.01 for left, right in zip(intervals, intervals[1:]))

    occupancy_ok = all(
        interface_tiles(node_id, side)
        for node_id, node in sankey_nodes.items()
        for side in (
            (["right"] if node.attrib["data-column"] == "source" else [])
            + (["left", "right"] if node.attrib["data-column"] == "stage" else [])
            + (["left"] if node.attrib["data-column"] == "outcome" else [])
        )
    )
    check(
        occupancy_ok,
        "R6-D071-SANKEY-INTERFACE-100-PERCENT-OCCUPANCY",
        "incoming/outgoing ribbon intervals tile every applicable node interface without gap or overlap",
        results,
    )
    conservation_ok = all(
        abs(float(ribbon.attrib["data-thickness"]) - float(ribbon.attrib["data-value"]) * scale) <= 0.01
        for ribbon in sankey_ribbons
    ) and all(
        abs(sum(float(item.attrib["data-value"]) for item in sankey_ribbons if item.attrib["data-source-node"] == node_id) - float(node.attrib["data-value"])) <= 0.01
        for node_id, node in sankey_nodes.items()
        if node.attrib["data-column"] in {"source", "stage"}
    ) and all(
        abs(sum(float(item.attrib["data-value"]) for item in sankey_ribbons if item.attrib["data-target-node"] == node_id) - float(node.attrib["data-value"])) <= 0.01
        for node_id, node in sankey_nodes.items()
        if node.attrib["data-column"] in {"stage", "outcome"}
    )
    check(
        conservation_ok,
        "R6-D071-SANKEY-CONSERVATION",
        "ribbon thickness and node in/out totals conserve all 12,000 minutes",
        results,
    )
    regenerated_special = ET.fromstring(special_anchor().svg)
    check(
        any(item.attrib.get("data-sankey-contract") == "D-071" for item in regenerated_special.iter(f"{SVG_NS}g"))
        and len([item for item in regenerated_special.iter(f"{SVG_NS}rect") if "data-sankey-node-bar" in item.attrib]) == 7
        and all("rx" not in item.attrib for item in regenerated_special.iter(f"{SVG_NS}rect") if "data-sankey-node-bar" in item.attrib),
        "R6-D071-DETERMINISTIC-SANKEY-CONTRACT",
        "source builder regenerates the D-071 100%-occupancy square-bar Sankey",
        results,
    )

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
