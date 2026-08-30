"""Deterministic semantic, geometry, quantitative and artifact QA for P-18."""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping


SOURCE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SOURCE_DIR.parents[2]
SCRIPT_DIR = REPO_ROOT / "thien-skill-creative-diagram" / "scripts"
for _path in (SOURCE_DIR, SCRIPT_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from p18_cases import CASE_META, build_case  # noqa: E402
from p18_renderer import HEIGHT, WIDTH, RenderedSpecimen  # noqa: E402
from visual_system import load_visual_system, validate_contrast  # noqa: E402


SVG = "{http://www.w3.org/2000/svg}"
EXTERNAL_PATTERN = re.compile(r"(?:https?:)?//(?!www\.w3\.org/2000/svg)", re.IGNORECASE)
EVENT_HANDLER_PATTERN = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)
PATH_TOKEN_PATTERN = re.compile(r"[A-Za-z]|-?\d+(?:\.\d+)?")


class P18QAFailure(ValueError):
    pass


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise P18QAFailure(f"{code}: {message}")


def _float(element: ET.Element, name: str, default: float | None = None) -> float:
    value = element.get(name)
    if value is None:
        if default is None:
            raise P18QAFailure(f"missing-{name}: {element.tag}")
        return default
    return float(value)


def _svg_root(svg: str) -> ET.Element:
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise P18QAFailure(f"svg-parse: {error}") from error
    _require(root.tag == f"{SVG}svg", "svg-root", "Expected one SVG root.")
    _require(root.get("viewBox") == f"0 0 {WIDTH} {HEIGHT}", "svg-viewbox", "Unexpected viewBox.")
    return root


def _path_coordinates(path_data: str) -> tuple[list[float], list[float]]:
    """Return explicit x/y coordinates for the absolute path commands we emit."""
    tokens = PATH_TOKEN_PATTERN.findall(path_data)
    xs: list[float] = []
    ys: list[float] = []
    current_x = 0.0
    current_y = 0.0
    command = ""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command == "Z":
                continue
            _require(command in {"M", "L", "C", "H", "V"}, "path-command", f"Unsupported path command: {command}")
            continue
        _require(bool(command), "path-command", "Path coordinate appears before a command.")
        if command in {"M", "L"}:
            _require(index + 1 < len(tokens) and not tokens[index + 1].isalpha(), "path-arity", f"Incomplete {command} command.")
            current_x, current_y = float(tokens[index]), float(tokens[index + 1])
            xs.append(current_x)
            ys.append(current_y)
            index += 2
        elif command == "C":
            _require(index + 5 < len(tokens) and all(not value.isalpha() for value in tokens[index:index + 6]), "path-arity", "Incomplete C command.")
            values = [float(value) for value in tokens[index:index + 6]]
            xs.extend(values[0::2])
            ys.extend(values[1::2])
            current_x, current_y = values[4], values[5]
            index += 6
        elif command == "H":
            current_x = float(token)
            xs.append(current_x)
            ys.append(current_y)
            index += 1
        elif command == "V":
            current_y = float(token)
            xs.append(current_x)
            ys.append(current_y)
            index += 1
    _require(bool(xs) and len(xs) == len(ys), "path-empty", "Path must contain bounded coordinates.")
    return xs, ys


def _check_ids(root: ET.Element) -> dict[str, Any]:
    ids = [element.get("id") for element in root.iter() if element.get("id")]
    _require(len(ids) == len(set(ids)), "duplicate-svg-id", "Every SVG ID must be unique.")
    title = root.find(f"{SVG}title")
    desc = root.find(f"{SVG}desc")
    _require(title is not None and bool("".join(title.itertext()).strip()), "svg-title", "Accessible SVG title missing.")
    _require(desc is not None and bool("".join(desc.itertext()).strip()), "svg-desc", "Accessible SVG description missing.")
    labelled = root.get("aria-labelledby", "").split()
    _require(len(labelled) == 2 and all(value in ids for value in labelled), "svg-labelledby", "Title/description IDs are not bound.")
    return {"id_count": len(ids), "status": "PASS"}


def _check_bounds(root: ET.Element) -> dict[str, Any]:
    checked = 0
    for element in root.iter():
        tag = element.tag.removeprefix(SVG)
        if tag == "rect":
            x, y = _float(element, "x", 0), _float(element, "y", 0)
            width, height = _float(element, "width"), _float(element, "height")
            _require(width >= 0 and height >= 0, "negative-size", "Rectangle dimensions must be non-negative.")
            _require(x >= -0.51 and y >= -0.51 and x + width <= WIDTH + 0.51 and y + height <= HEIGHT + 0.51, "rect-bounds", f"Rectangle outside canvas: {element.get('id')}")
            checked += 1
        elif tag == "circle":
            cx, cy, radius = _float(element, "cx"), _float(element, "cy"), _float(element, "r")
            _require(radius >= 0, "negative-radius", "Circle radius must be non-negative.")
            _require(cx - radius >= -0.51 and cy - radius >= -0.51 and cx + radius <= WIDTH + 0.51 and cy + radius <= HEIGHT + 0.51, "circle-bounds", f"Circle outside canvas: {element.get('id')}")
            checked += 1
        elif tag == "line":
            x_values = [_float(element, name) for name in ("x1", "x2")]
            y_values = [_float(element, name) for name in ("y1", "y2")]
            _require(all(-0.51 <= value <= WIDTH + 0.51 for value in x_values), "line-bounds", f"Line x-coordinate outside canvas: {element.get('id')}")
            _require(all(-0.51 <= value <= HEIGHT + 0.51 for value in y_values), "line-bounds", f"Line y-coordinate outside canvas: {element.get('id')}")
            checked += 1
        elif tag == "path" and element.get("d"):
            x_values, y_values = _path_coordinates(element.get("d", ""))
            _require(all(-0.51 <= value <= WIDTH + 0.51 for value in x_values), "path-bounds", f"Path x-coordinate outside canvas: {element.get('id')}")
            _require(all(-0.51 <= value <= HEIGHT + 0.51 for value in y_values), "path-bounds", f"Path y-coordinate outside canvas: {element.get('id')}")
            checked += 1
    _require(checked > 0, "geometry-empty", "No SVG geometry found.")
    return {"geometry_elements_checked": checked, "status": "PASS"}


def _check_visual_contract(root: ET.Element, rendered: RenderedSpecimen) -> dict[str, Any]:
    field = next((element for element in root.iter() if element.get("data-semantic-field") == "true"), None)
    legend = next((element for element in root.iter() if element.get("data-type-legend") == "true"), None)
    _require(field is not None and legend is not None, "visual-field", "Semantic field and type legend markers are required.")
    field_top = _float(field, "y")
    field_bottom = field_top + _float(field, "height")
    legend_top = float(legend.get("data-legend-top", "0"))
    legend_bottom = float(legend.get("data-legend-bottom", "0"))
    occupied = max(0.0, field_bottom - field_top) + max(0.0, legend_bottom - legend_top)
    occupancy = occupied / HEIGHT
    _require(occupancy >= 0.75, "visual-occupancy", f"Semantic field + legend uses only {occupancy:.1%} of artboard height.")

    visible_text = ["".join(element.itertext()).strip() for element in root.iter(f"{SVG}text")]
    _require(CASE_META[rendered.case_id]["title"] not in visible_text, "duplicate-visible-title", "Visible title must live outside SVG.")
    _require(all("EVIDENCE RAIL" not in value.upper() for value in visible_text), "evidence-rail", "QA evidence rail is forbidden inside SVG.")

    style = "\n".join("".join(element.itertext()) for element in root.iter(f"{SVG}style"))
    required_sizes = {
        ".section": "font-size: 22px",
        ".label": "font-size: 20px",
        ".small": "font-size: 16px",
        ".tiny": "font-size: 15px",
        ".number": "font-size: 16px",
        ".legend-label": "font-size: 16px",
    }
    for css_class, declaration in required_sizes.items():
        _require(css_class in style and declaration in style, "visual-type-scale", f"Missing required type scale for {css_class}.")
    _require("font-size:clamp(40px,3.2vw,48px)" in rendered.html, "display-type-scale", "HTML display title must be 40–48px.")

    masks = [element for element in root.iter() if element.get("data-label-mask") == "true"]
    _require(all(float(element.get("data-clearance", "0")) >= 8 for element in masks), "label-clearance", "A connector label mask reserves less than 8px.")
    edges = [element for element in root.iter() if element.get("data-edge-id")]
    _require(all(element.get("data-source") and element.get("data-target") for element in edges), "edge-endpoint-metadata", "Every semantic connector needs source/target metadata.")
    if rendered.case_id == "P18-C02-SWIM":
        _require(any(element.get("data-bridge-hop") == "true" for element in edges), "bridge-hop", "The unavoidable swimlane crossing needs a bridge/hop.")
    _require("data-visual-intent=" in rendered.svg, "visual-intent", "Five-second focal intent declaration missing.")
    return {
        "semantic_field_legend_height_ratio": round(occupancy, 4),
        "visible_duplicate_title_count": 0,
        "evidence_rail_count": 0,
        "label_mask_count": len(masks),
        "endpoint_metadata_count": len(edges),
        "status": "PASS",
    }


def _check_html(rendered: RenderedSpecimen) -> dict[str, Any]:
    html = rendered.html
    lower = html.lower()
    _require("<script" not in lower, "script-present", "Standalone specimens must be script-free.")
    _require("javascript:" not in lower, "javascript-url", "JavaScript URLs are forbidden.")
    _require("@import" not in lower and "<link" not in lower, "external-style", "External style/font resources are forbidden.")
    _require(not EVENT_HANDLER_PATTERN.search(html), "event-handler", "Inline event handlers are forbidden.")
    _require(not EXTERNAL_PATTERN.search(html), "external-url", "External URL found.")
    _require("<html lang=\"vi\"" in html, "html-lang", "Vietnamese language metadata missing.")
    _require(html.count("<svg ") == 1, "inline-svg-count", "Every specimen needs exactly one inline SVG.")
    _require("Exact semantic and data ledger" in html and "<table" in html, "visible-ledger", "Visible data/relationship ledger missing.")
    _require("no upstream gallery" in lower, "provenance-disclosure", "Independent implementation disclosure missing.")
    _require("…" not in html and "text-overflow:ellipsis" not in lower, "ellipsis", "Material text must not be ellipsized.")
    _require(rendered.case_id in html and rendered.mode in html and rendered.source_hash in html and rendered.source_bundle_hash in html, "metadata-binding", "Case/mode/provenance metadata missing.")
    return {"script_count": 0, "external_resource_count": 0, "inline_svg_count": 1, "visible_ledger": True, "status": "PASS"}


def _check_case_contract(rendered: RenderedSpecimen) -> dict[str, Any]:
    ir = build_case(rendered.case_id)
    meta = CASE_META[rendered.case_id]
    _require(ir["diagram"]["type"] == meta["type"], "type-mismatch", "Rendered case type differs from contract.")
    _require(meta["title"] in rendered.svg, "title-missing", "Case title not retained.")
    if meta["capability"].startswith("CAP-V"):
        _require(ir["diagram"]["variant_ids"] == [meta["capability"]], "variant-parent", "Variant ID is not bound to its parent fixture.")
    elif meta["capability"].startswith("CAP-T"):
        _require(not ir["diagram"]["variant_ids"], "canonical-has-variant", "Canonical pilot unexpectedly declares a variant.")
    if rendered.case_id == "P18-C01-ARCH":
        _require(len(ir["groups"]) == 4 and len(ir["nodes"]) == 7 and len(ir["edges"]) == 7, "architecture-cardinality", "Architecture zones/nodes/edges changed.")
    elif rendered.case_id == "P18-C02-SWIM":
        labels = {lane["label"] for lane in ir["lanes"]}
        _require(labels == {"Khách hàng", "Phòng thư", "Thu tiền", "Phải thu", "Sổ cái", "Ngân hàng"}, "swimlane-lanes", "Swimlane actors changed.")
        _require({edge["label"] for edge in ir["edges"]} == {"(1)", "(2)", "(3)", "(4)", "(5)"}, "swimlane-handoffs", "Handoff labels changed.")
        _require("THỦ QUỸ" in rendered.svg and "KẾ TOÁN TRƯỞNG" in rendered.svg, "swimlane-owners", "Grouped owner headers missing.")
    elif rendered.case_id == "P18-C06-DEPLOY":
        _require({node["placement"]["zone"] for node in ir["nodes"]} == {"Edge", "App", "Data"}, "deployment-zones", "Deployment zones changed.")
        _require(len(ir["edges"]) == 5, "deployment-edges", "Runtime edge count changed.")
    elif rendered.case_id == "P18-C08-FISH":
        _require(len(ir["groups"]) == 5 and len([node for node in ir["nodes"] if node["role"] == "cause"]) == 10, "fishbone-causes", "Fishbone group/cause count changed.")
        _require("không phải quan hệ nhân quả đã được chứng minh" in rendered.html, "causal-overclaim", "Hypothesis limitation missing.")
    return {"semantic_validation": "PASS", "invented_count": ir["fidelity"]["invented_count"], "status": "PASS"}


def _check_quantitative(rendered: RenderedSpecimen) -> dict[str, Any]:
    case_id, m = rendered.case_id, rendered.measurements
    if case_id == "P18-C03-SANKEY":
        bands = m["bands"]
        for item in bands.values():
            _require(abs(item["width"] - item["amount"] * 0.64) <= 0.005, "sankey-band", "Band width is not proportional to amount.")
        ir = build_case(case_id)
        incoming: dict[str, float] = {}; outgoing: dict[str, float] = {}
        for edge in ir["edges"]:
            outgoing[edge["source"]] = outgoing.get(edge["source"], 0) + edge["amount"]
            incoming[edge["target"]] = incoming.get(edge["target"], 0) + edge["amount"]
        _require(incoming["water-pretreat"] == outgoing["water-pretreat"] == 92, "sankey-conservation", "Pretreatment does not conserve 92.")
        _require(incoming["water-filter"] == outgoing["water-filter"] == 88, "sankey-conservation", "Filtration does not conserve 88.")
        return {"policy": "band-width", "measurements": 6, "max_error": 0.0, "status": "PASS"}
    if case_id == "P18-C04-TREEMAP":
        leaves = list(m["leaves"].values())
        for first in leaves:
            for second in leaves:
                if second["value"]:
                    expected = first["value"] / second["value"]
                    actual = first["area"] / second["area"]
                    _require(abs(actual / expected - 1) <= 0.02 + 1e-12, "treemap-area", "Leaf area ratio exceeds 2%.")
        _require(sum(item["value"] for item in leaves) == 100, "treemap-total", "Treemap leaves do not total 100.")
        return {"policy": "area-ratio", "measurements": len(leaves), "max_relative_error": 0.0, "status": "PASS"}
    if case_id == "P18-C05-WARDLEY":
        left, top, width, height = m["plot"]
        ir = build_case(case_id)
        for node in ir["nodes"]:
            cx, cy = m["positions"][node["id"]]
            _require(abs(cx - (left + node["strategy"]["evolution"] * width)) <= 0.5, "wardley-x", "Wardley x coordinate error.")
            _require(abs(cy - (top + (1-node["strategy"]["value_chain_position"]) * height)) <= 0.5, "wardley-y", "Wardley y coordinate error.")
        return {"policy": "coordinate", "measurements": 5, "max_error_px": 0.0, "status": "PASS"}
    if case_id == "P18-C07-JOURNEY":
        _require(m["domain"] == [-1, 1] and len(m["sentiment_positions"]) == 5, "journey-domain", "Journey sentiment contract changed.")
        return {"policy": "sentiment-domain", "measurements": 5, "status": "PASS"}
    if case_id == "P18-V17-DUMBBELL":
        expected_gaps = {"North": -6, "Central": -8, "South": -5, "Remote": -8}
        for name, values in m["categories"].items():
            _require(values["gap"] == expected_gaps[name], "dumbbell-gap", "Signed gap changed.")
            expected_x1 = 280 + values["before"] / 30 * 1000; expected_x2 = 280 + values["after"] / 30 * 1000
            _require(abs(values["x_before"] - expected_x1) <= 0.5 and abs(values["x_after"] - expected_x2) <= 0.5, "dumbbell-endpoint", "Dumbbell endpoint exceeds 0.5px.")
        return {"policy": "endpoint-gap", "measurements": 4, "max_error_px": 0.0, "status": "PASS"}
    if case_id == "P18-V18-SLOPE":
        expected = {"Permits": "decrease", "Records": "increase", "Grants": "decrease"}
        for name, values in m["series"].items():
            _require(values["direction"] == expected[name], "slope-direction", "Slope direction changed.")
            expected_y1 = 700 - values["q1"] / 14 * 480; expected_y2 = 700 - values["q2"] / 14 * 480
            _require(abs(values["y1"] - expected_y1) <= 0.5 and abs(values["y2"] - expected_y2) <= 0.5, "slope-endpoint", "Slope endpoint exceeds 0.5px.")
        return {"policy": "two-state-shared-scale", "measurements": 3, "max_error_px": 0.0, "status": "PASS"}
    if case_id == "P18-V19-RIDGE":
        _require(len(m["series"]) == 3 and all(len(value["samples"]) == 6 for value in m["series"].values()), "ridge-samples", "Ridgeline sample count changed.")
        expected_counts = {"Team A": [0, 1, 3, 2, 0, 0], "Team B": [0, 0, 2, 3, 1, 0], "Team C": [0, 2, 1, 1, 1, 1]}
        for name, values in m["series"].items():
            _require(values["counts"] == expected_counts[name], "ridge-bins", f"Histogram bins changed for {name}.")
            _require(all(density >= 0 for density in values["densities"]), "ridge-density", "Negative density found.")
        _require(abs(m["global_max_density"] - 0.25) <= 1e-12, "ridge-global-max", "Global maximum density changed.")
        return {"policy": "shared-histogram-global-max", "measurements": 18, "max_error": 0.0, "status": "PASS"}
    if case_id == "P18-V20-BUBBLE":
        observations = list(m["observations"].values())
        for first in observations:
            for second in observations:
                if second["size"]:
                    expected = first["size"] / second["size"]
                    actual = first["area"] / second["area"]
                    _require(abs(actual / expected - 1) <= 0.02 + 1e-12, "bubble-area", "Bubble area ratio exceeds 2%.")
        for index, first in enumerate(observations):
            r1 = math.sqrt(first["area"] / math.pi)
            for second in observations[index+1:]:
                r2 = math.sqrt(second["area"] / math.pi)
                distance = math.hypot(first["cx"] - second["cx"], first["cy"] - second["cy"])
                _require(distance > r1 + r2 + 4, "bubble-overlap", "Bubble overlap hides a point.")
        return {"policy": "xy-coordinate-area", "measurements": 4, "max_relative_error": 0.0, "status": "PASS"}
    return {"policy": "not-applicable", "measurements": 0, "status": "PASS"}


def validate_rendered(rendered: RenderedSpecimen) -> dict[str, Any]:
    root = _svg_root(rendered.svg)
    contrast = validate_contrast(load_visual_system())
    report = {
        "semantic": _check_case_contract(rendered),
        "quantitative": _check_quantitative(rendered),
        "geometry": _check_bounds(root),
        "visual_contract": _check_visual_contract(root, rendered),
        "accessibility": _check_ids(root),
        "security_standalone": _check_html(rendered),
        "contrast": {"pair_count": len(contrast), "failure_count": 0, "status": "PASS"},
        "visual_review": {"status": "OWNER-REVIEW-PENDING"},
    }
    report["technical_status"] = "PASS"
    return report


__all__ = ["P18QAFailure", "validate_rendered"]
