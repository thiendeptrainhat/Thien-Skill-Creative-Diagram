"""Deterministic P-11 quality gates for semantic diagram artifacts.

The validators are deliberately read-only and use only the Python standard
library.  They inspect trusted project output and inert normalized records;
they never execute imported content, fetch resources, update a golden, or
assemble a release package.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from diagram_core import CANONICAL_TYPES, canonical_json
from safe_import import parse_csv_text, parse_json_text, parse_pasted_table, tabular_matrix
from visual_system import Rect, Route, VisualError, load_visual_system, rects_overlap, validate_contrast, validate_geometry


QA_VERSION = "p11-qa-1"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
MATERIAL_COLLECTIONS = ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations")
FORBIDDEN_PACKAGE_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SECRET_PACKAGE_NAMES = {".env", "id_rsa", "id_ed25519"}
QA_ONLY_PARTS = {"evidence", "golden-candidates", "qa-only", "previews"}
EXTERNAL_RE = re.compile(r"(?:https?:|file:|javascript:|data:text/html)", re.I)
EVENT_RE = re.compile(r"^on[a-z]+$", re.I)
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T.*)?$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class QAFailure(Exception):
    """Stable failure raised by one P-11 hard check."""

    def __init__(self, code: str, message: str, *, location: str = "artifact") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.location = location

    def issue(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "location": self.location, "stage": "p11-qa"}


def _fail(code: str, message: str, location: str = "artifact") -> None:
    raise QAFailure(code, message, location=location)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_json_documents(paths: Iterable[Path]) -> dict[str, Any]:
    checked: list[str] = []
    for path in sorted(paths, key=lambda item: str(item)):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            _fail("schema-json-invalid", f"JSON document is invalid: {path.name}.", str(path))
        checked.append(str(path))
    return {"status": "pass", "count": len(checked), "paths": checked}


def validate_markdown_links(markdown_files: Iterable[Path], root: Path) -> dict[str, Any]:
    checked = 0
    root = root.resolve()
    for path in sorted(markdown_files, key=lambda item: str(item)):
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                _fail("reference-link-escape", f"Reference link escapes the skill root: {raw_target}.", str(path))
            if not resolved.exists():
                _fail("reference-link-missing", f"Reference link target does not exist: {raw_target}.", str(path))
            checked += 1
    return {"status": "pass", "checked_links": checked}


def validate_type_coverage(reference_dir: Path) -> dict[str, Any]:
    index = json.loads((reference_dir / "capability-map.json").read_text(encoding="utf-8"))
    type_files = {path.stem.removeprefix("type-") for path in reference_dir.glob("type-*.md") if path.name != "type-index.md"}
    expected_files = {diagram_type.replace("/", "-") for diagram_type in CANONICAL_TYPES}
    if type_files != expected_files:
        missing = sorted(expected_files - type_files)
        extra = sorted(type_files - expected_files)
        _fail("type-coverage-mismatch", f"Type references differ from the 27-type contract; missing={missing}, extra={extra}.", str(reference_dir))
    capabilities = index.get("capabilities") if set(index) == {"schema_version", "capabilities"} else index
    if not isinstance(capabilities, Mapping):
        _fail("capability-map-invalid", "Capability map needs a capability object.", str(reference_dir / "capability-map.json"))
    type_parents = {str(parent) for item in capabilities.values() if isinstance(item, Mapping) and str(item.get("class")) == "canonical-type" for parent in item.get("parents", [])}
    if type_parents != set(CANONICAL_TYPES):
        _fail("type-capability-mismatch", "Canonical capability parents do not cover exactly 27 types.", str(reference_dir / "capability-map.json"))
    return {"status": "pass", "type_count": len(type_files), "capability_count": len(capabilities)}


def validate_determinism(first: bytes | str | Mapping[str, Any], second: bytes | str | Mapping[str, Any]) -> dict[str, str]:
    def normalized(value: bytes | str | Mapping[str, Any]) -> bytes:
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode("utf-8")
        return canonical_json(value).encode("utf-8")

    first_bytes, second_bytes = normalized(first), normalized(second)
    if first_bytes != second_bytes:
        _fail("build-drift", "Equal normalized input and environment produced different bytes.", "determinism")
    return {"status": "pass", "sha256": sha256_bytes(first_bytes)}


def _parse_svg(svg: str) -> ET.Element:
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        _fail("svg-invalid", "SVG is not well-formed XML.")
        raise AssertionError from error
    if root.tag.rsplit("}", 1)[-1] != "svg":
        _fail("svg-root-invalid", "Artifact root is not SVG.")
    return root


def _viewbox(root: ET.Element) -> Rect:
    raw = root.get("viewBox", "")
    try:
        x, y, width, height = (float(value) for value in raw.replace(",", " ").split())
    except (ValueError, TypeError):
        _fail("svg-viewbox-invalid", "SVG requires a numeric four-value viewBox.")
    if width <= 0 or height <= 0:
        _fail("svg-viewbox-invalid", "SVG viewBox dimensions must be positive.")
    return Rect(x, y, width, height)


def _point_in(rect: Rect, point: tuple[float, float], tolerance: float = 0.5) -> bool:
    return rect.left - tolerance <= point[0] <= rect.right + tolerance and rect.top - tolerance <= point[1] <= rect.bottom + tolerance


def _on_boundary(rect: Rect, point: tuple[float, float], tolerance: float = 1.0) -> bool:
    x, y = point
    return (
        rect.left - tolerance <= x <= rect.right + tolerance
        and (math.isclose(y, rect.top, abs_tol=tolerance) or math.isclose(y, rect.bottom, abs_tol=tolerance))
    ) or (
        rect.top - tolerance <= y <= rect.bottom + tolerance
        and (math.isclose(x, rect.left, abs_tol=tolerance) or math.isclose(x, rect.right, abs_tol=tolerance))
    )


def _graphic_points(element: ET.Element) -> list[tuple[float, float]]:
    tag = element.tag.rsplit("}", 1)[-1]
    try:
        if tag == "rect":
            x, y = float(element.get("x", 0)), float(element.get("y", 0))
            width, height = float(element.get("width", 0)), float(element.get("height", 0))
            return [(x, y), (x + width, y + height)]
        if tag == "circle":
            cx, cy, radius = float(element.get("cx", 0)), float(element.get("cy", 0)), float(element.get("r", 0))
            return [(cx - radius, cy - radius), (cx + radius, cy + radius)]
        if tag == "line":
            return [(float(element.get("x1", 0)), float(element.get("y1", 0))), (float(element.get("x2", 0)), float(element.get("y2", 0)))]
        if tag in {"polygon", "polyline"}:
            values = [float(value) for value in re.findall(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", element.get("points", ""))]
            return list(zip(values[::2], values[1::2]))
    except ValueError:
        _fail("svg-geometry-invalid", "SVG contains a non-numeric geometry attribute.")
    return []


def _route_segments(route: Route) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    return list(zip(route.points, route.points[1:]))


def _segment_cross(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    (a1, a2), (b1, b2) = first, second
    a_vertical, b_vertical = math.isclose(a1[0], a2[0]), math.isclose(b1[0], b2[0])
    a_horizontal, b_horizontal = math.isclose(a1[1], a2[1]), math.isclose(b1[1], b2[1])
    if not ((a_vertical and b_horizontal) or (a_horizontal and b_vertical)):
        return False
    vertical, horizontal = (first, second) if a_vertical else (second, first)
    x, y = vertical[0][0], horizontal[0][1]
    within_v = min(vertical[0][1], vertical[1][1]) < y < max(vertical[0][1], vertical[1][1])
    within_h = min(horizontal[0][0], horizontal[1][0]) < x < max(horizontal[0][0], horizontal[1][0])
    return within_v and within_h


def validate_geometry_contract(
    canvas: Rect,
    nodes: Mapping[str, Rect],
    routes: Sequence[Route],
    *,
    intentional_crossings: Iterable[frozenset[str]] = (),
    semantic_junctions: Iterable[tuple[str, tuple[float, float]]] = (),
) -> dict[str, Any]:
    try:
        validate_geometry(canvas, nodes, routes, minimum_gap=8)
    except VisualError as error:
        _fail(error.code, error.message, "geometry")
    allowed_crossings = set(intentional_crossings)
    for index, first in enumerate(routes):
        for second in routes[index + 1 :]:
            if any(_segment_cross(a, b) for a in _route_segments(first) for b in _route_segments(second)):
                if frozenset({first.edge_id, second.edge_id}) not in allowed_crossings:
                    _fail("route-crossing-unmarked", f"Routes {first.edge_id} and {second.edge_id} cross without an intentional marker.", "geometry")
    junctions = {(node_id, point) for node_id, point in semantic_junctions}
    attachments: dict[tuple[str, tuple[float, float]], list[str]] = {}
    for route in routes:
        attachments.setdefault((route.source_id, route.points[0]), []).append(route.edge_id)
        attachments.setdefault((route.target_id, route.points[-1]), []).append(route.edge_id)
    for attachment, edge_ids in attachments.items():
        if len(edge_ids) > 1 and attachment not in junctions:
            _fail("shared-attach-point", f"Edges {edge_ids} share an undeclared attachment point.", "geometry")
    return {"status": "pass", "nodes": len(nodes), "routes": len(routes)}


def validate_svg_contract(svg: str, ir: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = _parse_svg(svg)
    canvas = _viewbox(root)
    ids = [value for element in root.iter() if (value := element.get("id"))]
    if len(ids) != len(set(ids)):
        _fail("duplicate-svg-id", "SVG IDs must be unique.", "svg")
    labelled = root.get("aria-labelledby", "").split()
    if root.get("role") != "img" or len(labelled) < 2 or any(value not in ids for value in labelled):
        _fail("accessible-name-missing", "SVG needs role=img and valid title/description references.", "svg")
    for element in root.iter():
        for name, value in element.attrib.items():
            if EVENT_RE.match(name) or EXTERNAL_RE.search(value):
                _fail("svg-executable-or-external", "SVG contains executable or external content.", "svg")
        for point in _graphic_points(element):
            if not _point_in(canvas, point):
                _fail("graphic-out-of-bounds", "A graphic primitive is outside the SVG viewBox.", "svg")
    if root.findall(f".//{{{SVG_NS}}}clipPath"):
        _fail("material-clipping-risk", "Material output may not rely on a clipping path.", "svg")
    serialized = ET.tostring(root, encoding="unicode")
    if "textLength=" in serialized or "lengthAdjust=" in serialized or re.search(r"scale\([^,]+,\s*(?:0|0\.\d+)", serialized):
        _fail("typography-compressed", "Material typography may not be artificially compressed.", "svg")
    rendered_text = " ".join(root.itertext())
    if "…" in rendered_text or "..." in rendered_text:
        _fail("material-ellipsis", "Material content may not be hidden by ellipsis.", "svg")
    if unicodedata.normalize("NFC", rendered_text) != rendered_text:
        _fail("unicode-not-nfc", "Rendered text must preserve NFC-normalized Vietnamese text.", "svg")
    if ir is not None:
        material: list[str] = []
        for collection in MATERIAL_COLLECTIONS:
            for item in ir.get(collection, []):
                value = item.get("label", item.get("text"))
                if value is not None:
                    material.append(str(value))
        for value in material:
            if unicodedata.normalize("NFC", value) != value:
                _fail("source-unicode-not-nfc", "Source label is not NFC-normalized.", "ir")
            if value not in rendered_text:
                _fail("material-label-missing", f"Rendered SVG is missing material text: {value}.", "svg")
        reading_order = list(ir.get("accessibility", {}).get("reading_order", []))
        material_ids = [str(item["id"]) for collection in MATERIAL_COLLECTIONS for item in ir.get(collection, [])]
        if reading_order != material_ids:
            _fail("reading-order-mismatch", "Accessible reading order must match canonical narrative order.", "ir.accessibility.reading_order")
    return {"status": "pass", "unique_ids": len(ids), "view_box": [canvas.x, canvas.y, canvas.width, canvas.height]}


def validate_contrast_contract(system: Mapping[str, Any] | None = None) -> dict[str, Any]:
    try:
        report = validate_contrast(system or load_visual_system())
    except VisualError as error:
        _fail(error.code, error.message, "visual-system")
    return {"status": "pass", "pairs": len(report), "report": report}


def validate_state_redundancy(ir: Mapping[str, Any], svg: str) -> dict[str, Any]:
    text = " ".join(_parse_svg(svg).itertext()).casefold()
    stateful = [item for item in ir.get("nodes", []) if item.get("state")]
    for item in stateful:
        state = str(item["state"]).casefold()
        if state not in text:
            _fail("color-only-state", f"State for {item['id']} lacks a textual or shape-label channel.", "svg")
    return {"status": "pass", "stateful_items": len(stateful)}


def validate_motion_html(html: str, mode: str) -> dict[str, Any]:
    lowered = html.lower()
    if 'data-static-frame="complete"' not in lowered:
        _fail("static-frame-incomplete", "HTML must declare a complete static frame.", "html")
    for token, code in (("prefers-reduced-motion", "reduced-motion-missing"), ("@media print", "print-frame-missing"), (":focus-visible", "focus-style-missing")):
        if token not in lowered:
            _fail(code, f"HTML is missing required behavior: {token}.", "html")
    if mode != "none":
        if "<script" not in lowered:
            _fail("motion-runtime-missing", "Enhanced motion mode needs its deterministic runtime.", "html")
        if "motion-replay" not in lowered or "motion-pause" not in lowered:
            _fail("motion-controls-missing", "Motion needs pause and replay controls.", "html")
    return {"status": "pass", "mode": mode}


def _canonical_cell(value: Any) -> dict[str, Any]:
    if value is None or (isinstance(value, str) and value.strip().casefold() in {"null", "none", "missing"}):
        return {"kind": "missing", "value": None}
    text = unicodedata.normalize("NFC", str(value).strip())
    if text.casefold() == "nan":
        return {"kind": "non-finite", "value": "NaN"}
    if NUMBER_RE.fullmatch(text):
        try:
            number = Decimal(text)
        except InvalidOperation:
            pass
        else:
            return {"kind": "number", "value": format(number.normalize(), "f")}
    if DATE_RE.fullmatch(text):
        return {"kind": "date", "value": text}
    return {"kind": "text", "value": text}


def normalize_quantitative_carrier(bundle: Mapping[str, Any]) -> dict[str, Any]:
    matrix = tabular_matrix(bundle)
    return {
        "headers": [unicodedata.normalize("NFC", str(value).strip()) for value in matrix["headers"]],
        "rows": [[_canonical_cell(value) for value in row] for row in matrix["rows"]],
    }


def validate_carrier_equivalence(pasted: str, csv_text: str, json_text: str) -> dict[str, Any]:
    normalized = {
        "pasted-table": normalize_quantitative_carrier(parse_pasted_table(pasted)),
        "csv": normalize_quantitative_carrier(parse_csv_text(csv_text)),
        "json": normalize_quantitative_carrier(parse_json_text(json_text)),
    }
    values = list(normalized.values())
    if any(value != values[0] for value in values[1:]):
        _fail("carrier-ir-mismatch", "Equivalent pasted-table, CSV, and JSON data did not normalize identically.", "quantitative-input")
    return {"status": "pass", "normalized_sha256": sha256_bytes(canonical_json(values[0]).encode("utf-8")), "row_count": len(values[0]["rows"])}


def _parse_datetime(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        _fail("temporal-value-invalid", "Temporal values must be ISO-8601 strings.", field)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("temporal-value-invalid", "Temporal values must be valid ISO-8601 strings.", field)
    if parsed.tzinfo is None:
        _fail("timezone-missing", "Temporal values require an explicit timezone.", field)
    return parsed


def validate_quantitative_ir(ir: Mapping[str, Any], svg: str | None = None) -> dict[str, Any]:
    diagram_type = str(ir.get("diagram", {}).get("type", ""))
    series = list(ir.get("series", []))
    for item in series:
        if not item.get("unit"):
            _fail("quantitative-unit-missing", "Every quantitative series needs an explicit unit.", "ir.series")
        for datum in item.get("data", []):
            value, missing = datum.get("value"), bool(datum.get("missing"))
            if value is None and not missing:
                _fail("missingness-implicit", "Null values must carry missing=true.", "ir.series")
            if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value))):
                _fail("numeric-value-invalid", "Quantitative values must be finite numbers or explicit missing values.", "ir.series")
    axes = list(ir.get("axes", []))
    if diagram_type == "bar-chart":
        y_axis = next((axis for axis in axes if axis.get("dimension") == "y"), None)
        exception = any(str(item.get("text", "")).startswith("baseline-exception:") for item in ir.get("annotations", []))
        contains_zero = bool(y_axis) and y_axis.get("domain_min") is not None and y_axis.get("domain_max") is not None and y_axis["domain_min"] <= 0 <= y_axis["domain_max"]
        if not contains_zero and not exception:
            _fail("bar-zero-baseline", "Bar length requires a zero baseline or a visible approved exception.", "ir.axes")
    if diagram_type == "scatter-plot":
        x_axis = next((axis for axis in axes if axis.get("dimension") == "x"), None)
        y_axis = next((axis for axis in axes if axis.get("dimension") == "y"), None)
        if not x_axis or not y_axis:
            _fail("scatter-domain-missing", "Scatter requires declared x and y domains.", "ir.axes")
        for datum in [datum for item in series for datum in item.get("data", [])]:
            if not isinstance(datum.get("domain"), (int, float)) or not isinstance(datum.get("value"), (int, float)):
                _fail("scatter-coordinate-invalid", "Scatter points require numeric x/y coordinates.", "ir.series")
            if not (x_axis["domain_min"] <= datum["domain"] <= x_axis["domain_max"] and y_axis["domain_min"] <= datum["value"] <= y_axis["domain_max"]):
                _fail("scatter-coordinate-out-of-domain", "Scatter coordinate is outside the declared domain.", "ir.series")
    if diagram_type == "radar":
        domains = {(axis.get("domain_min"), axis.get("domain_max"), axis.get("unit")) for axis in axes}
        if len(domains) != 1:
            _fail("radar-scale-incompatible", "Radar axes need one published compatible scale and unit.", "ir.axes")
    if diagram_type == "quadrant":
        x_axis = next((axis for axis in axes if axis.get("dimension") == "x"), None)
        y_axis = next((axis for axis in axes if axis.get("dimension") == "y"), None)
        for datum in [datum for item in series for datum in item.get("data", [])]:
            if not x_axis or not y_axis or not (x_axis["domain_min"] <= datum["domain"] <= x_axis["domain_max"] and y_axis["domain_min"] <= datum["value"] <= y_axis["domain_max"]):
                _fail("quadrant-coordinate-out-of-domain", "Quadrant coordinates must remain within declared axes.", "ir.series")
    if diagram_type in {"gantt", "timeline"}:
        previous: datetime | None = None
        for node in ir.get("nodes", []):
            start = _parse_datetime(node.get("start"), f"ir.nodes.{node.get('id')}.start")
            end_value = node.get("end")
            if end_value is not None:
                end = _parse_datetime(end_value, f"ir.nodes.{node.get('id')}.end")
                if end < start:
                    _fail("temporal-duration-invalid", "End must not precede start.", "ir.nodes")
            if previous is not None and start < previous:
                _fail("temporal-order-invalid", "Temporal nodes must preserve chronological order.", "ir.nodes")
            previous = start
    if svg is not None:
        root = _parse_svg(svg)
        text = " ".join(root.itertext())
        if series:
            metadata = next((item for item in root.findall(f".//{{{SVG_NS}}}metadata") if item.get("data-kind") == "exact-data"), None)
            if metadata is None or not metadata.text:
                _fail("exact-data-missing", "Quantitative SVG needs an exact-data metadata representation.", "svg")
            try:
                exact = json.loads(metadata.text)
            except json.JSONDecodeError:
                _fail("exact-data-invalid", "Exact-data metadata is not valid JSON.", "svg")
            exact_series = exact.get("series")
            if diagram_type == "pyramid-funnel" and isinstance(exact_series, list) and exact_series and series:
                source_order = [datum.get("domain") for datum in series[0].get("data", [])]
                rendered_order = [datum.get("domain") for datum in exact_series[0].get("data", [])]
                if rendered_order != source_order:
                    _fail("funnel-order-invalid", "Rendered funnel stage order differs from the declared source order.", "svg")
            if exact_series != series:
                _fail("source-render-value-mismatch", "Rendered exact data differs from source IR.", "svg")
        if diagram_type in {"gantt", "timeline"}:
            for node in ir.get("nodes", []):
                for field in ("start", "end"):
                    value = node.get(field)
                    if value is not None and str(value) not in text:
                        _fail("source-render-time-mismatch", "Rendered time differs from source IR.", "svg")
    return {"status": "pass", "diagram_type": diagram_type, "series_count": len(series)}


def validate_fidelity(ir: Mapping[str, Any]) -> dict[str, Any]:
    source_ids = {str(item.get("id")) for item in ir.get("source_items", [])}
    dispositions: list[str] = []
    for collection in ("kept", "merged", "dropped", "source_rot"):
        for item in ir.get("fidelity", {}).get(collection, []):
            dispositions.extend(str(value) for value in item.get("source_ids", []))
    if len(dispositions) != len(set(dispositions)) or set(dispositions) != source_ids:
        _fail("fidelity-equation-invalid", "Every source item needs exactly one fidelity disposition.", "ir.fidelity")
    if ir.get("fidelity", {}).get("invented_count") != 0:
        _fail("invented-content", "Imported content may not create unsupported semantic facts.", "ir.fidelity")
    return {"status": "pass", "source_count": len(source_ids)}


def validate_package_inventory(paths: Iterable[str]) -> dict[str, Any]:
    normalized: list[str] = []
    for raw in paths:
        if "\\" in raw or raw.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", raw):
            _fail("package-path-absolute", f"Package path must be portable and relative: {raw}.", "package")
        path = PurePosixPath(raw)
        if not raw or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            _fail("package-path-traversal", f"Package path is unsafe: {raw}.", "package")
        if any(part in FORBIDDEN_PACKAGE_NAMES for part in path.parts) or path.suffix in {".pyc", ".log", ".zip"}:
            _fail("package-development-file", f"Package includes a development-only file: {raw}.", "package")
        if any(part in SECRET_PACKAGE_NAMES for part in path.parts) or path.suffix in {".pem", ".key", ".p12"}:
            _fail("package-secret-file", f"Package includes a secret-bearing file type: {raw}.", "package")
        if any(part.casefold() in QA_ONLY_PARTS for part in path.parts):
            _fail("package-qa-only-file", f"QA-only material may not enter a release package: {raw}.", "package")
        normalized.append(str(path))
    if len(normalized) != len(set(normalized)):
        _fail("package-duplicate-path", "Package paths must be unique.", "package")
    return {"status": "pass", "path_count": len(normalized)}


def audit_skill_tree(skill_root: Path) -> dict[str, Any]:
    if any(path.is_symlink() for path in skill_root.rglob("*")):
        _fail("package-symlink", "Canonical skill tree may not contain symlinks.", str(skill_root))
    relative = [path.relative_to(skill_root).as_posix() for path in skill_root.rglob("*") if path.is_file()]
    package = validate_package_inventory(relative)
    json_report = validate_json_documents(skill_root.rglob("*.json"))
    json_report["paths"] = [Path(path).resolve().relative_to(skill_root.resolve()).as_posix() for path in json_report["paths"]]
    link_report = validate_markdown_links(skill_root.rglob("*.md"), skill_root)
    coverage = validate_type_coverage(skill_root / "references")
    contrast = validate_contrast_contract()
    return {"qa_version": QA_VERSION, "status": "pass", "package": package, "json": json_report, "links": link_report, "coverage": coverage, "contrast_pairs": contrast["pairs"]}


__all__ = [
    "QA_VERSION", "QAFailure", "audit_skill_tree", "normalize_quantitative_carrier",
    "sha256_bytes", "validate_carrier_equivalence", "validate_contrast_contract",
    "validate_determinism", "validate_fidelity", "validate_geometry_contract",
    "validate_json_documents", "validate_markdown_links", "validate_motion_html",
    "validate_package_inventory", "validate_quantitative_ir", "validate_state_redundancy",
    "validate_svg_contract", "validate_type_coverage",
]
