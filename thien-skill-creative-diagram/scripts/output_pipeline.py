"""P-08 portable output, conditional rasterization, and static-first motion.

The module has no mandatory third-party dependency. It renders validated IR
through the P-07 static renderer, creates self-contained HTML or standalone
SVG, and uses PNG only through an already available bounded adapter. It never
installs software, fetches a resource, or executes imported source content.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Mapping

from diagram_core import AUDIENCES, CANONICAL_TYPES, DETAILS, SECURITY_LIMITS, SIZES, VISUAL_MODES, build_ir, canonical_json, normalize_request
from full_renderer import RENDERER_VERSION, render_static
from motion_catalog import select_motion_capabilities
from safe_import import validate_workspace_target
from semantic_grammars import validate_semantics
from structural_profiles import (
    build_profiled_plan,
    load_profile_registry,
    profile_binding_for_ledger,
    validate_artifact_binding,
    validate_profile_binding,
    validate_profile_ledger,
)
from profile_renderer import RENDERER_VERSION as PROFILE_RENDERER_VERSION, render_profiled_svg, validate_rendered_geometry


OUTPUT_VERSION = "p08-output-1"
SVG_NS = "http://www.w3.org/2000/svg"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RASTER_TIMEOUT_SECONDS = 30
RASTER_OUTPUT_LIMIT = 64 * 1024 * 1024
PROFILED_SVG_LIMIT = 10 * 1024 * 1024
PROFILE_JOB_INPUT_LIMIT = 2 * 1024 * 1024
PROFILE_JOB_VERSION = "2.1"
ET.register_namespace("", SVG_NS)

PROFILE_JOB_COLLECTIONS = (
    "nodes",
    "edges",
    "groups",
    "lanes",
    "series",
    "axes",
    "annotations",
)
PROFILE_JOB_COUNT_FIELDS = (*PROFILE_JOB_COLLECTIONS, "directed_edges")


def _profile_job_collection_schema() -> dict[str, Any]:
    """Project the canonical semantic schema into the agent-authored job surface."""

    schema_path = Path(__file__).resolve().parent.parent / "references" / "semantic-ir.schema.json"
    raw = json.loads(schema_path.read_text(encoding="utf-8"))

    def strip_runtime_receipts(value: Any) -> Any:
        if isinstance(value, dict):
            cleaned = {key: strip_runtime_receipts(item) for key, item in value.items() if key != "source_refs"}
            if isinstance(cleaned.get("required"), list):
                cleaned["required"] = [item for item in cleaned["required"] if item != "source_refs"]
            if isinstance(cleaned.get("properties"), dict):
                cleaned["properties"].pop("source_refs", None)
            return cleaned
        if isinstance(value, list):
            return [strip_runtime_receipts(item) for item in value]
        return copy.deepcopy(value)

    return {
        "$schema": raw["$schema"],
        "type": "object",
        "additionalProperties": False,
        "required": list(PROFILE_JOB_COLLECTIONS),
        "properties": {
            name: strip_runtime_receipts(raw["properties"][name])
            for name in PROFILE_JOB_COLLECTIONS
        },
        "$defs": strip_runtime_receipts(raw["$defs"]),
        "note": "Runtime-owned source_refs are deliberately removed; type-specific semantic validators still apply.",
    }


_PROFILE_REGISTRY = load_profile_registry()
_PROFILE_JOB_COLLECTION_SCHEMA = _profile_job_collection_schema()
PROFILE_JOB_CONTRACT: dict[str, Any] = {
    "job_version": PROFILE_JOB_VERSION,
    "purpose": "Executable natural-language-to-profiled-SVG fast path; semantic content remains explicit and inert.",
    "required": [
        "job_version",
        "instruction",
        "title",
        "diagram_type",
        "structural_profile",
        "source_assertions",
        "relation_groups",
        "expected_counts",
    ],
    "optional_defaults": {
        "variant_ids": [],
        "size": "fit",
        "detail": "balanced",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": "auto",
        "nodes": [],
        "edges": [],
        "groups": [],
        "lanes": [],
        "series": [],
        "axes": [],
        "annotations": [],
        "accessibility_description": "the trusted instruction",
    },
    "relation_group": {
        "required": ["id_prefix", "sources", "targets", "kind", "directed"],
        "semantics": "Expands the Cartesian product of sources x targets into atomic edges before IR construction.",
        "optional_edge_fields": [
            "label",
            "order",
            "guard",
            "amount",
            "unit",
            "relation_kind",
            "source_member",
            "target_member",
            "source_multiplicity",
            "target_multiplicity",
        ],
    },
    "source_assertions": {
        "purpose": "Separate agent-authored pre-IR double entry. It is reconciled against the materialized job and validated IR; it does not independently prove that natural-language interpretation was complete.",
        "required": [
            "node_ids",
            "edge_assertions",
            "group_members",
            "lane_members",
            "node_member_ids",
            "series_data_ids",
            "axis_ids",
            "annotation_ids",
        ],
        "edge_assertion_required": ["source", "target", "kind", "directed", "source_quote"],
        "edge_assertion_semantics": "One record per atomic edge. source_quote is one minimal relation clause (not the whole instruction), must occur verbatim once, and must contain the source and target label or ID; repeated quotes are allowed for fan-in, fan-out, and chains.",
        "exact_shapes": {
            "node_ids": "Unique array containing every and only nodes[].id.",
            "edge_assertions": "Array containing exactly one source/target/kind/directed assertion for every atomic edge after direct edges and relation_groups are combined; edge IDs are deliberately not repeated here.",
            "group_members": "Object whose keys are exactly every groups[].id and whose values are the exact unique groups[].member_ids arrays; use {} when groups is empty.",
            "lane_members": "Object whose keys are exactly every lanes[].id and whose values are the exact unique lanes[].member_ids arrays; use {} when lanes is empty.",
            "node_member_ids": "Object whose keys are exactly nodes that explicitly contain a members field (including an explicit empty members array) and whose values are those exact unique nested member IDs; use {} when no node contains members.",
            "series_data_ids": "Object whose keys are exactly every series[].id and whose values are the exact unique IDs in that series data array; use {} when series is empty.",
            "axis_ids": "Unique array containing every and only axes[].id; use [] when axes is empty.",
            "annotation_ids": "Unique array containing every and only annotations[].id; use [] when annotations is empty.",
        },
    },
    "collection_schema": _PROFILE_JOB_COLLECTION_SCHEMA,
    "supported_diagram_types": sorted(CANONICAL_TYPES),
    "supported_profiles": [
        {
            "profile_id": profile["profile_id"],
            "profile_class": profile["profile_class"],
            "canonical_parent": profile["canonical_parent"],
            "layout_engine": profile["layout_engine"],
            "variant_ids": [profile["capability_id"]] if profile.get("capability_id") else [],
        }
        for profile in _PROFILE_REGISTRY["profiles"]
    ],
    "dial_values": {
        "size": list(SIZES),
        "detail": list(DETAILS),
        "audience": list(AUDIENCES),
        "visual_mode": list(VISUAL_MODES),
        "language": {"accepted": "auto or one BCP-47-style tag matching ^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$", "examples": ["auto", "vi", "en-US"]},
    },
    "expected_counts": {
        "required": list(PROFILE_JOB_COUNT_FIELDS),
        "additional_keys": False,
        "value_contract": "Every required value is a non-negative integer; booleans are invalid.",
        "semantics": "The object must contain exactly all eight required keys. Each value must equal both the fully materialized collection count and its independent source_assertions count; directed_edges counts atomic edges whose directed value is true.",
    },
    "minimal_valid_job": {
        "job_version": "2.1",
        "instruction": "Người dùng gọi API.",
        "title": "Luồng truy cập tối thiểu",
        "diagram_type": "architecture",
        "structural_profile": "topology-and-zones",
        "nodes": [
            {"id": "user", "role": "actor", "label": "Người dùng"},
            {"id": "api", "role": "service", "label": "API"},
        ],
        "groups": [
            {"id": "trusted-zone", "label": "Vùng tin cậy", "member_ids": ["api"]},
        ],
        "source_assertions": {
            "node_ids": ["user", "api"],
            "edge_assertions": [
                {"source": "user", "target": "api", "kind": "request", "directed": True, "source_quote": "Người dùng gọi API."},
            ],
            "group_members": {"trusted-zone": ["api"]},
            "lane_members": {},
            "node_member_ids": {},
            "series_data_ids": {},
            "axis_ids": [],
            "annotation_ids": [],
        },
        "relation_groups": [
            {"id_prefix": "user-api", "sources": ["user"], "targets": ["api"], "kind": "request", "directed": True},
        ],
        "expected_counts": {
            "nodes": 2,
            "edges": 1,
            "groups": 1,
            "lanes": 0,
            "series": 0,
            "axes": 0,
            "annotations": 0,
            "directed_edges": 1,
        },
    },
    "fixed_output": {"format": "svg", "motion": "none", "files": ["diagram.svg", "diagram.ledger.json"]},
}

OUTPUT_CAPABILITIES = {
    "CAP-O01": "format routing and transparent fallback",
    "CAP-O02": "responsive size preset",
    "CAP-O03": "validated detail preservation",
    "CAP-O04": "audience wording without fact changes",
    "CAP-O05": "diagram-only standalone SVG",
    "CAP-O06": "conditional PNG from an existing rasterizer",
    "CAP-O07": "accessible SVG name, description, and exact-data alternative",
}

SIZE_OUTPUTS: dict[str, tuple[str, str, int, int]] = {
    "doc-inline": ("960", "720", 960, 720),
    "doc-wide": ("1440", "900", 1440, 900),
    "slide-16x9": ("1600", "900", 1600, 900),
    "slide-4x3": ("1600", "1200", 1600, 1200),
    "social-og": ("1200", "630", 1200, 630),
    "social-square": ("1080", "1080", 1080, 1080),
    "print-a4-landscape": ("297mm", "210mm", 1600, 1131),
    "print-letter-landscape": ("11in", "8.5in", 1600, 1236),
    "fit": ("1600", "900", 1600, 900),
}


class OutputFailure(Exception):
    def __init__(self, code: str, message: str, *, status: str = "invalid") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status

    def issue(self) -> dict[str, str]:
        return {"code": self.code, "stage": "output", "message": self.message}


@dataclass(frozen=True)
class Artifact:
    name: str
    media_type: str
    content: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


@dataclass(frozen=True)
class RasterizerAdapter:
    name: str
    render: Callable[[str, int, int], bytes]


@dataclass(frozen=True)
class ExportBundle:
    artifacts: Mapping[str, Artifact]
    ledger: Mapping[str, Any]


@dataclass(frozen=True)
class ProfiledWriteResult:
    output_dir: str
    svg_path: str
    ledger_path: str
    selected_profile: str
    layout_engine: str
    svg_sha256: str
    ledger_sha256: str


def _run_command(command: list[str], svg: str) -> bytes:
    try:
        result = subprocess.run(
            command,
            input=svg.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=RASTER_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise OutputFailure("rasterizer-failed", "The detected rasterizer could not produce PNG.") from error
    if result.returncode != 0 or not result.stdout or len(result.stdout) > RASTER_OUTPUT_LIMIT:
        raise OutputFailure("rasterizer-failed", "The detected rasterizer returned an invalid or oversized result.")
    return result.stdout


def detect_rasterizer(*, search_path: str | None = None, allow_python_adapter: bool = True) -> RasterizerAdapter | None:
    """Detect a preinstalled renderer without importing or installing it eagerly."""

    if allow_python_adapter and importlib.util.find_spec("cairosvg") is not None:
        def render_cairosvg(svg: str, width: int, height: int) -> bytes:
            try:
                import cairosvg  # type: ignore[import-not-found]
                return cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=width, output_height=height)
            except Exception as error:
                raise OutputFailure("rasterizer-failed", "The preinstalled CairoSVG adapter failed.") from error
        return RasterizerAdapter("cairosvg-preinstalled", render_cairosvg)
    for executable in ("rsvg-convert", "magick", "convert"):
        path = shutil.which(executable, path=search_path)
        if not path:
            continue
        if executable == "rsvg-convert":
            return RasterizerAdapter(executable, lambda svg, width, height, p=path: _run_command([p, "--format", "png", "--width", str(width), "--height", str(height)], svg))
        prefix = [path] if executable == "convert" else [path]
        return RasterizerAdapter(executable, lambda svg, width, height, p=prefix: _run_command(p + ["svg:-", "-resize", f"{width}x{height}!", "png:-"], svg))
    return None


def registered_capabilities(
    diagram_type: str,
    *,
    rasterizer: RasterizerAdapter | None = None,
    auto_detect_rasterizer: bool = True,
) -> set[str]:
    if diagram_type not in CANONICAL_TYPES:
        raise OutputFailure("type-unsupported", "Output capabilities require one canonical diagram type.")
    capabilities = {
        f"grammar:{diagram_type}",
        f"layout:{diagram_type}",
        "renderer:static-svg",
        "validator:output",
        "exporter:html",
        "exporter:svg",
    }
    available = rasterizer or (detect_rasterizer() if auto_detect_rasterizer else None)
    if available:
        capabilities.update({"rasterizer:png", "exporter:png"})
    return capabilities


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "-", value)


def _exact_data(ir: Mapping[str, Any]) -> tuple[str, str]:
    vi = str(ir["diagram"]["language"]).lower().startswith("vi")
    words = ({"caption": "Dữ liệu chính xác", "domain": "Miền", "series": "Chuỗi", "value": "Giá trị", "unit": "Đơn vị", "missing": "thiếu", "role": "Vai trò", "component": "Thành phần", "state": "Trạng thái"} if vi else {"caption": "Exact diagram data", "domain": "Domain", "series": "Series", "value": "Value", "unit": "Unit", "missing": "missing", "role": "Role", "component": "Component", "state": "State"})
    if ir["series"]:
        rows = []
        plain = []
        for series in ir["series"]:
            unit = series.get("unit") or ""
            for datum in series["data"]:
                if "distribution_samples" in datum:
                    domain = datum["id"]
                    value = ", ".join(str(item) for item in datum["distribution_samples"])
                elif {"x_value", "y_value", "size_value"} <= set(datum):
                    domain = f"x={datum['x_value']}, y={datum['y_value']}"
                    value = f"size={datum['size_value']} {datum.get('size_unit') or ''}".strip()
                else:
                    domain = datum.get("domain", datum["id"])
                    value = words["missing"] if datum.get("missing") else str(datum.get("value"))
                rows.append(f"<tr><th scope=\"row\">{escape(str(domain))}</th><td>{escape(str(series['label']))}</td><td>{escape(value)}</td><td>{escape(str(unit))}</td></tr>")
                plain.append(f"{series['label']} / {domain} = {value} {unit}".strip())
        table = f'<table><caption>{words["caption"]}</caption><thead><tr><th>{words["domain"]}</th><th>{words["series"]}</th><th>{words["value"]}</th><th>{words["unit"]}</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
        return table, "; ".join(plain)
    if ir["diagram"]["type"] == "dp-security-matrix":
        rows = []
        plain = []
        for cell in ir["nodes"]:
            role, component = str(cell.get("secondary_label", "|")).split("|", 1)
            state = str(cell.get("state", "unknown"))
            rows.append(f"<tr><th scope=\"row\">{escape(role)}</th><td>{escape(component)}</td><td>{escape(state)}</td></tr>")
            plain.append(f"{role} / {component} = {state}")
        table = f'<table><caption>{words["caption"]}</caption><thead><tr><th>{words["role"]}</th><th>{words["component"]}</th><th>{words["state"]}</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
        return table, "; ".join(plain)
    return "", ""


def _semantic_snapshot(ir: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact validated semantic payload without runtime provenance handles."""

    def strip_runtime_receipts(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(key): strip_runtime_receipts(item)
                for key, item in value.items()
                if key != "source_refs"
            }
        if isinstance(value, list):
            return [strip_runtime_receipts(item) for item in value]
        return copy.deepcopy(value)

    return {
        "diagram": strip_runtime_receipts(ir["diagram"]),
        **{
            name: strip_runtime_receipts(ir[name])
            for name in PROFILE_JOB_COLLECTIONS
        },
    }


def _prepare_svg(
    svg: str,
    ir: Mapping[str, Any],
    mode: str,
    size: str,
    *,
    annotate_motion: bool,
    include_semantic_snapshot: bool = False,
) -> tuple[str, int]:
    root = ET.fromstring(svg)
    profiled_fit = size == "fit" and root.get("data-renderer-version") == PROFILE_RENDERER_VERSION
    if profiled_fit:
        try:
            if float(root.attrib["width"]) <= 0 or float(root.attrib["height"]) <= 0:
                raise ValueError
        except (KeyError, TypeError, ValueError) as error:
            raise OutputFailure("svg-canvas-invalid", "Profiled fit output needs positive numeric intrinsic dimensions.") from error
    else:
        width, height, _, _ = SIZE_OUTPUTS[size]
        root.set("width", width)
        root.set("height", height)
    root.set("data-output-version", OUTPUT_VERSION)
    root.set("data-static-frame", "complete")
    root.set("lang", str(ir["diagram"]["language"]))
    table_html, plain_data = _exact_data(ir)
    desc = root.find(f"{{{SVG_NS}}}desc")
    if desc is None:
        raise OutputFailure("svg-accessibility-invalid", "SVG is missing its accessible description.")
    if plain_data:
        exact_label = "Dữ liệu chính xác" if str(ir["diagram"]["language"]).lower().startswith("vi") else "Exact data"
        desc.text = f"{desc.text or ''} {exact_label}: {plain_data}"
        metadata = ET.SubElement(root, f"{{{SVG_NS}}}metadata")
        metadata.set("data-kind", "exact-data")
        metadata.text = canonical_json({"series": ir["series"], "matrix": ir["nodes"] if ir["diagram"]["type"] == "dp-security-matrix" else []})
    if include_semantic_snapshot:
        metadata = ET.SubElement(root, f"{{{SVG_NS}}}metadata")
        metadata.set("data-kind", "exact-semantics")
        metadata.text = canonical_json(_semantic_snapshot(ir))
    target_count = 0
    if annotate_motion:
        root.set("data-motion-frame", "enhanceable")
        prefix = f"p07-{_safe_id(ir['diagram']['type'])}-{_safe_id(mode)}-"
        ordered_ids = list(ir["accessibility"]["reading_order"])
        ordered_ids.extend(datum["id"] for series in ir["series"] for datum in series["data"])
        by_id = {element.get("id"): element for element in root.iter() if element.get("id")}
        for item_id in ordered_ids:
            element = by_id.get(prefix + _safe_id(item_id))
            if element is None:
                continue
            element.set("data-motion-index", str(target_count))
            element.set("class", (element.get("class", "") + " motion-target").strip())
            target_count += 1
    rendered = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    _validate_svg_output(rendered, ir, require_motion_targets=annotate_motion and bool(target_count))
    return rendered, target_count


def _validate_svg_output(svg: str, ir: Mapping[str, Any], *, require_motion_targets: bool = False) -> None:
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise OutputFailure("svg-invalid", "Standalone SVG is not valid XML.") from error
    if root.tag != f"{{{SVG_NS}}}svg":
        raise OutputFailure("svg-root-invalid", "Standalone output must have an SVG root.")
    ids = [element.get("id") for element in root.iter() if element.get("id")]
    if len(ids) != len(set(ids)):
        raise OutputFailure("svg-id-duplicate", "Standalone SVG contains duplicate IDs.")
    lowered = svg.lower().replace(f'xmlns="{SVG_NS}"', "")
    if any(token in lowered for token in ("<script", "http://", "https://", "file://", "javascript:", "onload=", "onclick=", "@import")):
        raise OutputFailure("svg-external-or-executable", "Standalone SVG contains executable or external content.")
    if root.get("role") != "img" or not root.get("aria-labelledby"):
        raise OutputFailure("svg-accessibility-invalid", "Standalone SVG needs an accessible role and labelled-by relation.")
    if require_motion_targets and not any(element.get("data-motion-index") is not None for element in root.iter()):
        raise OutputFailure("motion-target-missing", "Motion was requested but no deterministic target exists.")
    material = [str(item.get("label", item.get("text", ""))) for collection in ("nodes", "groups", "lanes", "series", "axes", "annotations") for item in ir[collection]]
    text = " ".join(root.itertext())
    if any(value and value not in text for value in material):
        raise OutputFailure("svg-material-loss", "Standalone SVG is missing material source-backed text.")


class _HTMLAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.svg_count = 0
        self.external: list[str] = []
        self.ids: list[str] = []
        self.buttons = 0
        self.tables = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "svg": self.svg_count += 1
        if tag == "button": self.buttons += 1
        if tag == "table": self.tables += 1
        if values.get("id"): self.ids.append(str(values["id"]))
        for name in ("src", "href", "action", "poster"):
            value = values.get(name) or ""
            if re.match(r"(?:https?:|file:|//)", value, re.I): self.external.append(value)
        if any(name.lower().startswith("on") for name, _ in attrs): self.external.append("event-handler")


def _labels(language: str) -> dict[str, str]:
    if language == "vi":
        return {"previous": "Bước trước", "next": "Bước tiếp", "replay": "Phát lại", "pause": "Tạm dừng", "resume": "Tiếp tục", "controls": "Điều khiển chuyển động", "complete": "Sơ đồ tĩnh đầy đủ", "data": "Dữ liệu chính xác", "noscript": "JavaScript không hoạt động; toàn bộ nội dung tĩnh vẫn hiển thị."}
    return {"previous": "Previous step", "next": "Next step", "replay": "Replay", "pause": "Pause", "resume": "Resume", "controls": "Motion controls", "complete": "Complete static diagram", "data": "Exact data", "noscript": "JavaScript is unavailable; the complete static content remains visible."}


def _motion_css() -> str:
    return """
.motion-target{transition:opacity .22s ease,filter .22s ease,transform .22s ease;transform-box:fill-box;transform-origin:center}
html.motion-enabled[data-motion-mode=step] .motion-target[data-motion-state=future]{opacity:.2;filter:saturate(.25)}
html.motion-enabled[data-motion-mode=step] .motion-target[data-motion-state=past]{opacity:.58}
html.motion-enabled[data-motion-mode=step] .motion-target[data-motion-state=current]{opacity:1;filter:drop-shadow(0 0 7px currentColor);transform:scale(1.025)}
html.motion-enabled[data-motion-mode=reveal] .motion-target{animation:p08-reveal .48s both;animation-delay:calc(var(--motion-index) * 90ms)}
html.motion-enabled[data-motion-mode=loop] figure::after{content:"";position:absolute;inset:10% auto auto 4%;width:12px;height:12px;border-radius:50%;background:#2f6fed;box-shadow:0 0 0 5px rgba(47,111,237,.18);animation:p08-loop 3.2s linear infinite;pointer-events:none}
html.motion-paused *{animation-play-state:paused!important}
@keyframes p08-reveal{from{opacity:.22;transform:translateY(7px)}to{opacity:1;transform:none}}
@keyframes p08-loop{0%{transform:translate(0,0)}25%{transform:translate(78vw,0)}50%{transform:translate(78vw,60vh)}75%{transform:translate(0,60vh)}100%{transform:translate(0,0)}}
@media(prefers-reduced-motion:reduce){.motion-target,figure::after{animation:none!important;transition:none!important;opacity:1!important;filter:none!important;transform:none!important}}
@media print{.motion-controls,.motion-status,noscript{display:none!important}.motion-target{animation:none!important;transition:none!important;opacity:1!important;filter:none!important;transform:none!important}figure{overflow:visible!important;box-shadow:none!important;border:0!important}svg{min-width:0!important;width:100%!important;height:auto!important}}
"""


def _motion_script(mode: str, count: int, labels: Mapping[str, str]) -> str:
    # Only trusted constants are serialized into this project-authored script.
    config = json.dumps({"mode": mode, "count": count, "pause": labels["pause"], "resume": labels["resume"]}, ensure_ascii=True, separators=(",", ":"))
    return f"""(()=>{{'use strict';const c={config};const root=document.documentElement;const items=[...document.querySelectorAll('[data-motion-index]')];const status=document.getElementById('motion-status');const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;if(c.mode==='none'||reduced||!items.length){{if(status)status.textContent='{escape(labels['complete'])}';return;}}root.classList.add('motion-enabled');items.forEach((el,i)=>el.style.setProperty('--motion-index',String(i)));let step=0,paused=false;const apply=()=>{{if(c.mode!=='step')return;items.forEach((el,i)=>el.dataset.motionState=i<step?'past':i===step?'current':'future');if(status)status.textContent=`${{step+1}} / ${{items.length}}`;}};const replay=()=>{{step=0;root.classList.remove('motion-enabled');void root.offsetWidth;root.classList.add('motion-enabled');apply();}};document.getElementById('motion-prev')?.addEventListener('click',()=>{{step=Math.max(0,step-1);apply();}});document.getElementById('motion-next')?.addEventListener('click',()=>{{step=Math.min(items.length-1,step+1);apply();}});document.getElementById('motion-replay')?.addEventListener('click',replay);document.getElementById('motion-pause')?.addEventListener('click',e=>{{paused=!paused;root.classList.toggle('motion-paused',paused);e.currentTarget.textContent=paused?c.resume:c.pause;}});document.addEventListener('keydown',e=>{{if(c.mode!=='step'||/input|textarea|select/i.test(e.target.tagName))return;if(e.key==='ArrowRight'){{step=Math.min(items.length-1,step+1);apply();}}if(e.key==='ArrowLeft'){{step=Math.max(0,step-1);apply();}}if(e.key==='Home'){{step=0;apply();}}if(e.key==='End'){{step=items.length-1;apply();}}}});apply();}})();"""


def _build_html(svg: str, ir: Mapping[str, Any], request: Mapping[str, Any], target_count: int, *, motion_runtime: bool) -> tuple[str, list[str]]:
    language = str(ir["diagram"]["language"])
    labels = _labels(language)
    mode = request["motion"] if motion_runtime else "none"
    warnings: list[str] = []
    if request["motion"] != "none" and not motion_runtime:
        warnings.append("Motion runtime is unavailable; delivered complete static HTML.")
    data_table, _ = _exact_data(ir)
    controls = ""
    if mode != "none":
        step_controls = f'<button id="motion-prev" type="button">{escape(labels["previous"])}</button><button id="motion-next" type="button">{escape(labels["next"])}</button>' if mode == "step" else ""
        controls = f'<nav class="motion-controls" aria-label="{escape(labels["controls"], quote=True)}">{step_controls}<button id="motion-replay" type="button">{escape(labels["replay"])}</button><button id="motion-pause" type="button">{escape(labels["pause"])}</button></nav><p id="motion-status" class="motion-status" aria-live="polite"></p>'
    min_width = {"doc-inline": 640, "social-square": 640, "social-og": 760, "fit": 640}.get(request["size"], 900)
    page_rule = {"print-a4-landscape": "@page{size:A4 landscape;margin:10mm}", "print-letter-landscape": "@page{size:Letter landscape;margin:10mm}"}.get(request["size"], "")
    script = f'<script>{_motion_script(mode, target_count, labels)}</script>' if mode != "none" else ""
    html = f'''<!doctype html><html lang="{escape(language)}" data-motion-mode="{mode}" data-static-frame="complete"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; media-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"><title>{escape(str(ir["diagram"]["title"]))}</title><style>{page_rule}:root{{color-scheme:light dark;--paper:#f4f6fa;--ink:#17223b;--line:#c7d1e2;--focus:#0b65d8}}*{{box-sizing:border-box}}body{{margin:0;padding:clamp(12px,3vw,36px);background:var(--paper);color:var(--ink);font-family:Inter,"Noto Sans",Arial,"Helvetica Neue",system-ui,sans-serif;line-height:1.45}}main{{max-width:1800px;margin:auto}}figure{{position:relative;margin:0;overflow:auto;background:white;border:1px solid var(--line);border-radius:18px;box-shadow:0 18px 50px rgba(23,34,59,.12)}}svg{{display:block;width:100%;height:auto;min-width:{min_width}px}}.motion-controls{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}}button{{min-height:44px;padding:8px 14px;border:2px solid var(--line);border-radius:10px;background:white;color:#17223b;font:600 15px inherit}}button:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}.motion-status{{min-height:1.5em;font-variant-numeric:tabular-nums}}.data-alternative{{margin-top:20px;overflow:auto}}table{{border-collapse:collapse;width:100%;background:white}}caption{{font-weight:700;text-align:left;padding:8px 0}}th,td{{border:1px solid var(--line);padding:8px;text-align:left}}.sr-only{{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}}{_motion_css()}</style></head><body><main><h1 class="sr-only">{escape(str(ir["diagram"]["title"]))}</h1>{controls}<figure aria-label="{escape(str(ir["accessibility"]["name"]), quote=True)}">{svg}</figure>{f'<section class="data-alternative" aria-label="{escape(labels["data"], quote=True)}">{data_table}</section>' if data_table else ''}<noscript>{escape(labels["noscript"])}</noscript></main>{script}</body></html>'''
    _validate_html_output(html, mode=mode, needs_table=bool(ir["accessibility"]["data_representation_required"]))
    return html, warnings


def _validate_html_output(html: str, *, mode: str, needs_table: bool) -> None:
    audit = _HTMLAudit()
    audit.feed(html)
    if audit.svg_count != 1 or audit.external or len(audit.ids) != len(set(audit.ids)):
        raise OutputFailure("html-portability-invalid", "HTML must contain one inline SVG, unique IDs, and no external or event-handler resource.")
    if needs_table and audit.tables != 1:
        raise OutputFailure("html-data-alternative-missing", "Quantitative or matrix HTML needs one exact-data table.")
    if mode == "step" and audit.buttons < 4:
        raise OutputFailure("motion-controls-incomplete", "Step mode needs previous, next, replay, and pause controls.")
    if "@media print" not in html or "prefers-reduced-motion" not in html:
        raise OutputFailure("static-fallback-incomplete", "HTML needs print and reduced-motion complete-state rules.")


def _png_dimensions(content: bytes) -> tuple[int, int]:
    if len(content) < 24 or not content.startswith(PNG_SIGNATURE) or content[12:16] != b"IHDR":
        raise OutputFailure("png-invalid", "Rasterizer output is not a valid PNG header.")
    return struct.unpack(">II", content[16:24])


def _validate_png(content: bytes, width: int, height: int) -> None:
    if len(content) > RASTER_OUTPUT_LIMIT:
        raise OutputFailure("png-over-limit", "PNG exceeds the approved output ceiling.")
    if _png_dimensions(content) != (width, height):
        raise OutputFailure("png-dimension-mismatch", "PNG dimensions do not match the validated static SVG canvas.")
    offset = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    while offset < len(content):
        if offset + 12 > len(content):
            raise OutputFailure("png-invalid", "PNG contains a truncated chunk.")
        length = struct.unpack(">I", content[offset:offset + 4])[0]
        kind = content[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(content):
            raise OutputFailure("png-invalid", "PNG chunk length exceeds the artifact boundary.")
        payload = content[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", content[offset + 8 + length:end])[0]
        import binascii
        if binascii.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise OutputFailure("png-invalid", "PNG chunk checksum is invalid.")
        chunks.append(kind)
        offset = end
        if kind == b"IEND":
            break
    if not chunks or chunks[0] != b"IHDR" or b"IDAT" not in chunks or chunks[-1] != b"IEND" or offset != len(content):
        raise OutputFailure("png-invalid", "PNG is missing required chunks or has trailing data.")


def _export_from_svg(
    ir: Mapping[str, Any],
    request: Mapping[str, Any],
    base_svg: str,
    base_static_svg_hash: str,
    *,
    rasterizer: RasterizerAdapter | None,
    auto_detect_rasterizer: bool,
    motion_runtime: bool,
    font_substitution: str | None,
    structural_profile: Mapping[str, Any] | None = None,
) -> ExportBundle:
    profiled = structural_profile is not None
    standalone_svg, _ = _prepare_svg(
        base_svg,
        ir,
        request["visual_mode"],
        request["size"],
        annotate_motion=False,
        include_semantic_snapshot=profiled,
    )
    motion_svg, target_count = _prepare_svg(
        base_svg,
        ir,
        request["visual_mode"],
        request["size"],
        annotate_motion=request["motion"] != "none" and motion_runtime,
        include_semantic_snapshot=profiled,
    )
    artifacts: dict[str, Artifact] = {}
    warnings: list[str] = []
    if font_substitution:
        warnings.append(f"Preferred font is unavailable; using declared local fallback {font_substitution}. Revalidate wrapping in the target renderer.")
    requested_format = request["format"]
    if request["motion"] != "none" and requested_format in {"svg", "png"}:
        warnings.append(f"Motion mode {request['motion']} is unavailable for {requested_format.upper()}; delivered a complete static frame.")
    if requested_format in {"html", "html+png"}:
        html, html_warnings = _build_html(motion_svg, ir, request, target_count, motion_runtime=motion_runtime)
        warnings.extend(html_warnings)
        artifacts["html"] = Artifact("diagram.html", "text/html; charset=utf-8", html.encode("utf-8"))
    if requested_format == "svg":
        artifacts["svg"] = Artifact("diagram.svg", "image/svg+xml", standalone_svg.encode("utf-8"))
    active_rasterizer = rasterizer or (detect_rasterizer() if auto_detect_rasterizer else None)
    if requested_format in {"png", "html+png"}:
        if active_rasterizer is None:
            warnings.append("PNG is unavailable because no approved preinstalled rasterizer was detected; no installation was attempted.")
            if requested_format == "png":
                artifacts["svg"] = Artifact("diagram.svg", "image/svg+xml", standalone_svg.encode("utf-8"))
        else:
            try:
                if profiled and request["size"] == "fit":
                    prepared_root = ET.fromstring(standalone_svg)
                    raster_width = int(float(prepared_root.attrib["width"]))
                    raster_height = int(float(prepared_root.attrib["height"]))
                else:
                    _, _, raster_width, raster_height = SIZE_OUTPUTS[request["size"]]
                png = active_rasterizer.render(standalone_svg, raster_width, raster_height)
                _validate_png(png, raster_width, raster_height)
                artifacts["png"] = Artifact("diagram.png", "image/png", png)
            except Exception as error:
                message = error.message if isinstance(error, OutputFailure) else "The adapter raised an unexpected bounded failure."
                warnings.append(f"PNG renderer {active_rasterizer.name} failed: {message}")
                if requested_format == "png":
                    artifacts["svg"] = Artifact("diagram.svg", "image/svg+xml", standalone_svg.encode("utf-8"))
    delivered = sorted(artifacts)
    effective_motion = request["motion"] if motion_runtime and requested_format in {"html", "html+png"} else "none"
    motion_capabilities = select_motion_capabilities(ir, effective_motion)
    ledger = {
        "schema_version": "2.1" if structural_profile is not None else "1.0",
        "output_version": OUTPUT_VERSION,
        "renderer_version": "caller-supplied-profiled-svg" if structural_profile is not None else RENDERER_VERSION,
        "requested_format": requested_format,
        "delivered_artifacts": delivered,
        "artifacts": {key: {"name": value.name, "media_type": value.media_type, "sha256": value.sha256, "bytes": len(value.content)} for key, value in artifacts.items()},
        "language": ir["diagram"]["language"],
        "diagram_type": ir["diagram"]["type"],
        "dials": {key: request[key] for key in ("size", "detail", "audience", "visual_mode", "format", "motion")},
        "ir_hash": hashlib.sha256(canonical_json(ir).encode("utf-8")).hexdigest(),
        "base_static_svg_hash": base_static_svg_hash,
        "standalone_svg_hash": hashlib.sha256(standalone_svg.encode("utf-8")).hexdigest(),
        "rasterizer": active_rasterizer.name if active_rasterizer else None,
        "font_policy": {"network_fetch": False, "stack": "Inter, Noto Sans, Arial, Helvetica Neue, system-ui, sans-serif", "substitution": font_substitution},
        "motion_capabilities": motion_capabilities,
        "output_capabilities": list(OUTPUT_CAPABILITIES),
        "static_fallback_complete": True,
        "warnings": warnings,
        "validation": {"semantic": "pass", "svg": "pass", "html": "pass" if "html" in artifacts else "not-requested", "png": "pass" if "png" in artifacts else "unavailable-or-not-requested"},
    }
    if structural_profile is not None:
        binding = profile_binding_for_ledger(structural_profile)
        semantic_snapshot = _semantic_snapshot(ir)
        ledger.update({
            "selected_profile": binding["selected_profile"],
            "canonical_parent": binding["canonical_parent"],
            "layout_engine": binding["layout_engine"],
            "mode": binding["mode"],
            "structural_override": binding["structural_override"],
            "profile_fallback": binding["fallback"],
            "profile_registry_sha256": binding["registry_sha256"],
            "profile_record_sha256": binding["profile_record_sha256"],
            "binding_stage": binding["binding_stage"],
            "structural_profile": binding,
            "profile_binding": "pass",
            "structural_conformance": "not-evaluated",
            "semantic_snapshot": semantic_snapshot,
            "semantic_snapshot_sha256": hashlib.sha256(canonical_json(semantic_snapshot).encode("utf-8")).hexdigest(),
        })
        ledger["validation"] = {**ledger["validation"], "profile_binding": "pass", "structural_conformance": "not-evaluated"}
        validate_profile_ledger(ledger, binding)
    return ExportBundle(artifacts, ledger)


def export_artifacts(
    ir_value: Mapping[str, Any],
    raw_request: Mapping[str, Any],
    *,
    rasterizer: RasterizerAdapter | None = None,
    auto_detect_rasterizer: bool = True,
    motion_runtime: bool = True,
    font_substitution: str | None = None,
) -> ExportBundle:
    """Historical P-08 export path using the historical P-07 renderer."""

    ir = validate_semantics(ir_value)
    request = normalize_request(raw_request)
    if request["diagram_type"] != "auto" and request["diagram_type"] != ir["diagram"]["type"]:
        raise OutputFailure("output-type-mismatch", "The validated IR type does not match the explicitly requested diagram type.")
    static = render_static(ir, request["visual_mode"], coverage_badge=False)
    return _export_from_svg(
        ir,
        request,
        static.svg,
        static.sha256,
        rasterizer=rasterizer,
        auto_detect_rasterizer=auto_detect_rasterizer,
        motion_runtime=motion_runtime,
        font_substitution=font_substitution,
    )


def export_profiled_artifacts(
    ir_value: Mapping[str, Any],
    raw_request: Mapping[str, Any],
    profiled_svg: str,
    pre_render_binding: Mapping[str, Any],
    *,
    rasterizer: RasterizerAdapter | None = None,
    auto_detect_rasterizer: bool = True,
    motion_runtime: bool = True,
    font_substitution: str | None = None,
) -> ExportBundle:
    """Export an SVG produced from a validated v2.1 pre-render profile plan.

    This path never calls the historical renderer.  It validates identity and
    provenance, but leaves structural geometry conformance unevaluated for an
    independent validator or judge.
    """

    ir = validate_semantics(ir_value)
    request = normalize_request(raw_request)
    if request["diagram_type"] != "auto" and request["diagram_type"] != ir["diagram"]["type"]:
        raise OutputFailure("output-type-mismatch", "The validated IR type does not match the explicitly requested diagram type.")
    if not isinstance(profiled_svg, str) or not profiled_svg.strip() or len(profiled_svg.encode("utf-8")) > PROFILED_SVG_LIMIT:
        raise OutputFailure("profiled-svg-invalid", "Profile-aware export needs one bounded non-empty SVG string.")
    try:
        validate_profile_binding(pre_render_binding)
        if pre_render_binding["canonical_parent"] != ir["diagram"]["type"]:
            raise OutputFailure("profile-parent-mismatch", "Profile binding does not match the validated semantic IR.")
        if pre_render_binding["requested_selector"] != request["structural_profile"]:
            raise OutputFailure("profile-selector-mismatch", "Profile binding does not match the normalized request selector.")
        if pre_render_binding["mode"] != request["visual_mode"]:
            raise OutputFailure("profile-mode-mismatch", "Profile binding does not match the normalized visual mode.")
        override = request["structural_override"]
        if pre_render_binding["structural_override"] != override["status"] or pre_render_binding.get("override_reason") != override.get("reason"):
            raise OutputFailure("profile-override-mismatch", "Profile binding does not match the normalized structural override.")
        validate_artifact_binding(profiled_svg, pre_render_binding)
    except OutputFailure:
        raise
    except Exception as error:
        code = getattr(error, "code", "profile-binding-invalid")
        raise OutputFailure(str(code), "Profile-aware export rejected an invalid pre-render binding or SVG receipt.") from error
    return _export_from_svg(
        ir,
        request,
        profiled_svg,
        hashlib.sha256(profiled_svg.encode("utf-8")).hexdigest(),
        rasterizer=rasterizer,
        auto_detect_rasterizer=auto_detect_rasterizer,
        motion_runtime=motion_runtime,
        font_substitution=font_substitution,
        structural_profile=pre_render_binding,
    )


def write_bundle(
    bundle: ExportBundle,
    targets: Mapping[str, str | Path],
    workspace_root: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, str]:
    if set(targets) != set(bundle.artifacts):
        raise OutputFailure("output-target-ambiguous", "Provide exactly one explicit relative target for every delivered artifact.", status="needs-clarification")
    written: dict[str, str] = {}
    for key, artifact in bundle.artifacts.items():
        target = validate_workspace_target(targets[key], workspace_root)
        expected_suffix = {"html": ".html", "svg": ".svg", "png": ".png"}[key]
        if target.suffix.lower() != expected_suffix:
            raise OutputFailure("output-extension-mismatch", f"Target for {key} must end with {expected_suffix}.")
        if target.exists() and not overwrite:
            raise OutputFailure("output-exists", "Output already exists; explicit overwrite permission is required.", status="needs-clarification")
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False) as temporary:
            temporary.write(artifact.content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, target)
        written[key] = str(target)
    return written


_PROFILE_JOB_FIELDS = frozenset(
    {
        "job_version",
        "instruction",
        "title",
        "diagram_type",
        "structural_profile",
        "variant_ids",
        "size",
        "detail",
        "audience",
        "visual_mode",
        "language",
        "source_assertions",
        "relation_groups",
        "expected_counts",
        "accessibility_description",
        *PROFILE_JOB_COLLECTIONS,
    }
)
_RELATION_GROUP_FIELDS = frozenset(
    {
        "id_prefix",
        "sources",
        "targets",
        "kind",
        "directed",
        "label",
        "order",
        "guard",
        "amount",
        "unit",
        "relation_kind",
        "source_member",
        "target_member",
        "source_multiplicity",
        "target_multiplicity",
    }
)
_SOURCE_ASSERTION_FIELDS = frozenset(
    {
        "node_ids",
        "edge_assertions",
        "group_members",
        "lane_members",
        "node_member_ids",
        "series_data_ids",
        "axis_ids",
        "annotation_ids",
    }
)
_EDGE_ASSERTION_FIELDS = frozenset({"source", "target", "kind", "directed", "source_quote"})
_CONTENT_CLASS = {
    "nodes": "entity",
    "edges": "relation",
    "groups": "group",
    "lanes": "lane",
    "series": "value",
    "axes": "label",
    "annotations": "annotation",
}


def _profile_job_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise OutputFailure("profile-job-invalid", f"{field} must be an object.")
    return dict(value)


def _profile_job_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise OutputFailure("profile-job-invalid", f"{field} must be an array.")
    return value


def _profile_job_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise OutputFailure("profile-job-invalid", f"{field} must be a non-empty string.")
    return value


def _expand_relation_groups(raw_groups: Any, *, edge_budget: int) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for index, raw_group in enumerate(_profile_job_list(raw_groups, "relation_groups")):
        field = f"relation_groups[{index}]"
        group = _profile_job_mapping(raw_group, field)
        extras = sorted(set(group) - _RELATION_GROUP_FIELDS)
        if extras:
            raise OutputFailure("profile-job-unknown-field", f"Unknown {field} field: {extras[0]}.")
        missing = sorted({"id_prefix", "sources", "targets", "kind", "directed"} - set(group))
        if missing:
            raise OutputFailure("profile-job-missing-field", f"Missing {field}.{missing[0]}.")
        prefix = _profile_job_string(group["id_prefix"], f"{field}.id_prefix")
        sources = _profile_job_list(group["sources"], f"{field}.sources")
        targets = _profile_job_list(group["targets"], f"{field}.targets")
        if not sources or not targets:
            raise OutputFailure("profile-job-relation-empty", f"{field} needs at least one source and one target.")
        if any(not isinstance(item, str) or not item for item in [*sources, *targets]):
            raise OutputFailure("profile-job-relation-invalid", f"{field} sources and targets must be unique non-empty IDs.")
        if len(sources) != len(set(sources)) or len(targets) != len(set(targets)):
            raise OutputFailure("profile-job-relation-invalid", f"{field} sources and targets must be unique non-empty IDs.")
        if not isinstance(group["directed"], bool):
            raise OutputFailure("profile-job-relation-invalid", f"{field}.directed must be a boolean.")
        kind = _profile_job_string(group["kind"], f"{field}.kind")
        pair_count = len(sources) * len(targets)
        if pair_count > edge_budget - len(expanded):
            raise OutputFailure(
                "profile-job-complexity-limit",
                f"Expanded relation groups exceed the hard limit of {edge_budget} edges.",
            )
        extras_for_edge = {key: copy.deepcopy(value) for key, value in group.items() if key not in {"id_prefix", "sources", "targets"}}
        extras_for_edge["kind"] = kind
        for raw_source in sources:
            for raw_target in targets:
                source, target = str(raw_source), str(raw_target)
                edge_id = prefix if pair_count == 1 else f"{prefix}-{source}-{target}"
                expanded.append({"id": edge_id, "source": source, "target": target, **copy.deepcopy(extras_for_edge)})
    return expanded


def _profile_job_counts(collections: Mapping[str, list[dict[str, Any]]]) -> dict[str, int]:
    counts = {name: len(collections[name]) for name in PROFILE_JOB_COLLECTIONS}
    counts["directed_edges"] = sum(1 for edge in collections["edges"] if edge.get("directed") is True)
    return counts


def _profile_job_id_list(value: Any, field: str) -> list[str]:
    values = _profile_job_list(value, field)
    if any(not isinstance(item, str) or not item for item in values) or len(values) != len(set(values)):
        raise OutputFailure("source-assertion-invalid", f"{field} must contain unique non-empty IDs.")
    return list(values)


def _profile_job_members_map(value: Any, field: str) -> dict[str, list[str]]:
    raw_mapping = _profile_job_mapping(value, field)
    normalized: dict[str, list[str]] = {}
    for raw_id, raw_members in raw_mapping.items():
        item_id = _profile_job_string(raw_id, f"{field}.id")
        normalized[item_id] = sorted(_profile_job_id_list(raw_members, f"{field}.{item_id}"))
    return dict(sorted(normalized.items()))


def _source_assertion_counts(assertions: Mapping[str, Any]) -> dict[str, int]:
    edges = _profile_job_list(assertions["edge_assertions"], "source_assertions.edge_assertions")
    return {
        "nodes": len(_profile_job_list(assertions["node_ids"], "source_assertions.node_ids")),
        "edges": len(edges),
        "groups": len(_profile_job_mapping(assertions["group_members"], "source_assertions.group_members")),
        "lanes": len(_profile_job_mapping(assertions["lane_members"], "source_assertions.lane_members")),
        "series": len(_profile_job_mapping(assertions["series_data_ids"], "source_assertions.series_data_ids")),
        "axes": len(_profile_job_list(assertions["axis_ids"], "source_assertions.axis_ids")),
        "annotations": len(_profile_job_list(assertions["annotation_ids"], "source_assertions.annotation_ids")),
        "directed_edges": sum(1 for edge in edges if isinstance(edge, Mapping) and edge.get("directed") is True),
    }


def _validate_expected_counts(raw_counts: Any, actual: Mapping[str, int], asserted: Mapping[str, int]) -> None:
    expected = _profile_job_mapping(raw_counts, "expected_counts")
    if set(expected) != set(PROFILE_JOB_COUNT_FIELDS):
        raise OutputFailure(
            "profile-job-count-contract",
            "expected_counts must contain exactly nodes, edges, groups, lanes, series, axes, annotations, and directed_edges.",
        )
    for field in PROFILE_JOB_COUNT_FIELDS:
        value = expected[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise OutputFailure("profile-job-count-contract", f"expected_counts.{field} must be a non-negative integer.")
        if value != actual[field]:
            raise OutputFailure(
                "semantic-coverage-mismatch",
                f"Expected {value} {field}, but the materialized semantic receipt contains {actual[field]}.",
            )
        if value != asserted[field]:
            raise OutputFailure(
                "semantic-coverage-mismatch",
                f"Expected {value} {field}, but independent source assertions contain {asserted[field]}.",
            )


def _validate_source_assertions(
    raw_assertions: Any,
    instruction: str,
    collections: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    assertions = _profile_job_mapping(raw_assertions, "source_assertions")
    if set(assertions) != _SOURCE_ASSERTION_FIELDS:
        raise OutputFailure(
            "source-assertion-contract",
            "source_assertions must contain exactly node_ids, edge_assertions, group_members, lane_members, node_member_ids, series_data_ids, axis_ids, and annotation_ids.",
        )

    node_ids = sorted(_profile_job_id_list(assertions["node_ids"], "source_assertions.node_ids"))
    material_node_ids = sorted(_profile_job_string(item.get("id"), f"nodes[{index}].id") for index, item in enumerate(collections["nodes"]))
    if node_ids != material_node_ids:
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted node IDs do not exactly match the materialized job.")
    node_labels = {
        _profile_job_string(item.get("id"), f"nodes[{index}].id"): _profile_job_string(item.get("label"), f"nodes[{index}].label")
        for index, item in enumerate(collections["nodes"])
    }

    raw_edges = _profile_job_list(assertions["edge_assertions"], "source_assertions.edge_assertions")
    asserted_edges: list[dict[str, Any]] = []
    asserted_edge_tuples: list[tuple[str, str, str, bool]] = []
    for index, raw_edge in enumerate(raw_edges):
        field = f"source_assertions.edge_assertions[{index}]"
        edge = _profile_job_mapping(raw_edge, field)
        if set(edge) != _EDGE_ASSERTION_FIELDS or not isinstance(edge.get("directed"), bool):
            raise OutputFailure("source-assertion-invalid", f"{field} needs exact source/target/kind/directed/source_quote fields.")
        source = _profile_job_string(edge["source"], f"{field}.source")
        target = _profile_job_string(edge["target"], f"{field}.target")
        kind = _profile_job_string(edge["kind"], f"{field}.kind")
        quote = _profile_job_string(edge["source_quote"], f"{field}.source_quote")
        if source not in node_labels or target not in node_labels:
            raise OutputFailure("source-assertion-invalid", f"{field} references an unknown node ID.")
        if len(quote) > 320 or ";" in quote or "\n" in quote or "\r" in quote:
            raise OutputFailure("source-assertion-unbound", f"{field}.source_quote must be one bounded minimal relation clause, not a paragraph.")
        if instruction.count(quote) != 1:
            raise OutputFailure("source-assertion-unbound", f"{field}.source_quote must occur exactly once in the trusted instruction.")
        folded_quote = quote.casefold()
        for endpoint in (source, target):
            if node_labels[endpoint].casefold() not in folded_quote and endpoint.casefold() not in folded_quote:
                raise OutputFailure(
                    "source-assertion-unbound",
                    f"{field}.source_quote does not name endpoint {endpoint} by exact label or ID.",
                )
        asserted_edges.append({"source": source, "target": target, "kind": kind, "directed": edge["directed"], "source_quote": quote})
        asserted_edge_tuples.append((source, target, kind, edge["directed"]))

    material_edge_tuples: list[tuple[str, str, str, bool]] = []
    for index, edge in enumerate(collections["edges"]):
        if not isinstance(edge.get("directed"), bool):
            raise OutputFailure("profile-job-invalid", f"edges[{index}].directed must be a boolean.")
        material_edge_tuples.append(
            (
                _profile_job_string(edge.get("source"), f"edges[{index}].source"),
                _profile_job_string(edge.get("target"), f"edges[{index}].target"),
                _profile_job_string(edge.get("kind"), f"edges[{index}].kind"),
                edge["directed"],
            )
        )
    if sorted(asserted_edge_tuples) != sorted(material_edge_tuples):
        raise OutputFailure("semantic-coverage-mismatch", "Atomic source-asserted edges do not exactly match materialized edges.")

    group_members = _profile_job_members_map(assertions["group_members"], "source_assertions.group_members")
    material_groups = {
        _profile_job_string(group.get("id"), f"groups[{index}].id"): sorted(
            _profile_job_id_list(group.get("member_ids"), f"groups[{index}].member_ids")
        )
        for index, group in enumerate(collections["groups"])
    }
    if group_members != dict(sorted(material_groups.items())):
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted group IDs or members do not exactly match the materialized job.")

    lane_members = _profile_job_members_map(assertions["lane_members"], "source_assertions.lane_members")
    material_lanes = {
        _profile_job_string(lane.get("id"), f"lanes[{index}].id"): sorted(
            _profile_job_id_list(lane.get("member_ids"), f"lanes[{index}].member_ids")
        )
        for index, lane in enumerate(collections["lanes"])
    }
    if lane_members != dict(sorted(material_lanes.items())):
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted lane IDs or members do not exactly match the materialized job.")

    node_member_ids = _profile_job_members_map(assertions["node_member_ids"], "source_assertions.node_member_ids")
    material_node_members = {
        _profile_job_string(node.get("id"), f"nodes[{index}].id"): sorted(
            _profile_job_string(member.get("id"), f"nodes[{index}].members[{member_index}].id")
            for member_index, member in enumerate(_profile_job_list(node.get("members"), f"nodes[{index}].members"))
        )
        for index, node in enumerate(collections["nodes"])
        if "members" in node
    }
    if node_member_ids != dict(sorted(material_node_members.items())):
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted node-member IDs do not exactly match the materialized job.")

    series_data_ids = _profile_job_members_map(assertions["series_data_ids"], "source_assertions.series_data_ids")
    material_series_data = {
        _profile_job_string(series.get("id"), f"series[{index}].id"): sorted(
            _profile_job_string(datum.get("id"), f"series[{index}].data[{datum_index}].id")
            for datum_index, datum in enumerate(_profile_job_list(series.get("data"), f"series[{index}].data"))
        )
        for index, series in enumerate(collections["series"])
    }
    if series_data_ids != dict(sorted(material_series_data.items())):
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted series or datum IDs do not exactly match the materialized job.")

    axis_ids = sorted(_profile_job_id_list(assertions["axis_ids"], "source_assertions.axis_ids"))
    material_axis_ids = sorted(_profile_job_string(axis.get("id"), f"axes[{index}].id") for index, axis in enumerate(collections["axes"]))
    if axis_ids != material_axis_ids:
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted axis IDs do not exactly match the materialized job.")
    annotation_ids = sorted(_profile_job_id_list(assertions["annotation_ids"], "source_assertions.annotation_ids"))
    material_annotation_ids = sorted(
        _profile_job_string(annotation.get("id"), f"annotations[{index}].id") for index, annotation in enumerate(collections["annotations"])
    )
    if annotation_ids != material_annotation_ids:
        raise OutputFailure("semantic-coverage-mismatch", "Source-asserted annotation IDs do not exactly match the materialized job.")

    normalized = {
        "node_ids": node_ids,
        "edge_assertions": sorted(asserted_edges, key=lambda item: (item["source"], item["target"], item["kind"], item["directed"], item["source_quote"])),
        "group_members": group_members,
        "lane_members": lane_members,
        "node_member_ids": node_member_ids,
        "series_data_ids": series_data_ids,
        "axis_ids": axis_ids,
        "annotation_ids": annotation_ids,
    }
    return normalized


def _semantic_receipt(
    instruction: str,
    collections: Mapping[str, list[dict[str, Any]]],
    source_assertions: Mapping[str, Any],
) -> dict[str, Any]:
    node_ids = [_profile_job_string(item.get("id"), f"nodes[{index}].id") for index, item in enumerate(collections["nodes"])]
    edge_records: list[dict[str, Any]] = []
    for index, item in enumerate(collections["edges"]):
        if not isinstance(item.get("directed"), bool):
            raise OutputFailure("profile-job-invalid", f"edges[{index}].directed must be a boolean.")
        edge_records.append(
            {
                "id": _profile_job_string(item.get("id"), f"edges[{index}].id"),
                "source": _profile_job_string(item.get("source"), f"edges[{index}].source"),
                "target": _profile_job_string(item.get("target"), f"edges[{index}].target"),
                "kind": _profile_job_string(item.get("kind"), f"edges[{index}].kind"),
                "directed": item["directed"],
            }
        )
    group_members: dict[str, list[str]] = {}
    for index, item in enumerate(collections["groups"]):
        group_id = _profile_job_string(item.get("id"), f"groups[{index}].id")
        members = _profile_job_list(item.get("member_ids"), f"groups[{index}].member_ids")
        if any(not isinstance(member, str) or not member for member in members):
            raise OutputFailure("profile-job-invalid", f"groups[{index}].member_ids must contain non-empty IDs.")
        if len(members) != len(set(members)):
            raise OutputFailure("profile-job-invalid", f"groups[{index}].member_ids must be unique.")
        if group_id in group_members:
            raise OutputFailure("profile-job-invalid", "Profiled-job group IDs must be unique.")
        group_members[group_id] = sorted(members)
    return {
        "schema_version": "1.2",
        "source_instruction_sha256": hashlib.sha256(instruction.encode("utf-8")).hexdigest(),
        "source_assertions_sha256": hashlib.sha256(canonical_json(source_assertions).encode("utf-8")).hexdigest(),
        "source_assertions": copy.deepcopy(source_assertions),
        "node_ids": sorted(node_ids),
        "edges": sorted(edge_records, key=lambda item: item["id"]),
        "group_members": dict(sorted(group_members.items())),
    }


def _reconcile_semantic_receipt(
    receipt_value: Mapping[str, Any],
    request: Mapping[str, Any],
    ir: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = _profile_job_mapping(receipt_value, "semantic_receipt")
    if set(receipt) != {
        "schema_version",
        "source_instruction_sha256",
        "source_assertions_sha256",
        "source_assertions",
        "node_ids",
        "edges",
        "group_members",
    }:
        raise OutputFailure("semantic-receipt-invalid", "Semantic receipt fields are incomplete or unknown.")
    if receipt["schema_version"] != "1.2":
        raise OutputFailure("semantic-receipt-invalid", "Semantic receipt version is unsupported.")
    instruction_hash = hashlib.sha256(str(request["instruction"]).encode("utf-8")).hexdigest()
    if receipt["source_instruction_sha256"] != instruction_hash:
        raise OutputFailure("semantic-coverage-mismatch", "Semantic receipt is not bound to the trusted instruction.")
    if not isinstance(receipt["source_assertions_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", receipt["source_assertions_sha256"]):
        raise OutputFailure("semantic-receipt-invalid", "Semantic receipt source assertion hash is invalid.")
    ir_collections = {name: [copy.deepcopy(item) for item in ir[name]] for name in PROFILE_JOB_COLLECTIONS}
    normalized_assertions = _validate_source_assertions(receipt["source_assertions"], str(request["instruction"]), ir_collections)
    assertion_hash = hashlib.sha256(canonical_json(normalized_assertions).encode("utf-8")).hexdigest()
    if receipt["source_assertions_sha256"] != assertion_hash:
        raise OutputFailure("semantic-coverage-mismatch", "Semantic receipt source assertions do not match their bound hash.")

    node_ids = _profile_job_list(receipt["node_ids"], "semantic_receipt.node_ids")
    if any(not isinstance(item, str) or not item for item in node_ids):
        raise OutputFailure("semantic-receipt-invalid", "Semantic receipt node IDs must be unique non-empty strings.")
    if len(node_ids) != len(set(node_ids)):
        raise OutputFailure("semantic-receipt-invalid", "Semantic receipt node IDs must be unique non-empty strings.")
    expected_nodes = {str(item["id"]) for item in ir["nodes"]}
    if set(node_ids) != expected_nodes:
        raise OutputFailure("semantic-coverage-mismatch", "Semantic receipt node IDs do not exactly match validated IR.")

    edge_records = _profile_job_list(receipt["edges"], "semantic_receipt.edges")
    receipt_edges: dict[str, tuple[str, str, str, bool]] = {}
    for index, raw_edge in enumerate(edge_records):
        edge = _profile_job_mapping(raw_edge, f"semantic_receipt.edges[{index}]")
        if set(edge) != {"id", "source", "target", "kind", "directed"} or not isinstance(edge.get("directed"), bool):
            raise OutputFailure("semantic-receipt-invalid", "Every semantic receipt edge needs exact id/source/target/kind/directed fields.")
        edge_id = _profile_job_string(edge["id"], f"semantic_receipt.edges[{index}].id")
        if edge_id in receipt_edges:
            raise OutputFailure("semantic-receipt-invalid", "Semantic receipt edge IDs must be unique.")
        receipt_edges[edge_id] = (
            _profile_job_string(edge["source"], f"semantic_receipt.edges[{index}].source"),
            _profile_job_string(edge["target"], f"semantic_receipt.edges[{index}].target"),
            _profile_job_string(edge["kind"], f"semantic_receipt.edges[{index}].kind"),
            edge["directed"],
        )
    ir_edges = {
        str(edge["id"]): (str(edge["source"]), str(edge["target"]), str(edge["kind"]), edge.get("directed") is True)
        for edge in ir["edges"]
    }
    if receipt_edges != ir_edges:
        raise OutputFailure("semantic-coverage-mismatch", "Semantic receipt edges do not exactly match validated IR.")

    raw_group_members = _profile_job_mapping(receipt["group_members"], "semantic_receipt.group_members")
    receipt_groups: dict[str, set[str]] = {}
    for group_id, raw_members in raw_group_members.items():
        members = _profile_job_list(raw_members, f"semantic_receipt.group_members.{group_id}")
        if any(not isinstance(item, str) or not item for item in members):
            raise OutputFailure("semantic-receipt-invalid", "Semantic receipt group members must be unique non-empty IDs.")
        if len(members) != len(set(members)):
            raise OutputFailure("semantic-receipt-invalid", "Semantic receipt group members must be unique non-empty IDs.")
        receipt_groups[str(group_id)] = set(members)
    ir_groups = {str(group["id"]): {str(member) for member in group["member_ids"]} for group in ir["groups"]}
    if receipt_groups != ir_groups:
        raise OutputFailure("semantic-coverage-mismatch", "Semantic receipt group IDs or members do not exactly match validated IR.")
    return copy.deepcopy(receipt)


def _materialize_profile_job(job_value: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    job = _profile_job_mapping(job_value, "job")
    extras = sorted(set(job) - _PROFILE_JOB_FIELDS)
    if extras:
        raise OutputFailure("profile-job-unknown-field", f"Unknown job field: {extras[0]}.")
    missing = sorted(set(PROFILE_JOB_CONTRACT["required"]) - set(job))
    if missing:
        raise OutputFailure("profile-job-missing-field", f"Missing job field: {missing[0]}.")
    if job["job_version"] != PROFILE_JOB_VERSION:
        raise OutputFailure("profile-job-version", f"job_version must be {PROFILE_JOB_VERSION}.")
    instruction = _profile_job_string(job["instruction"], "instruction")
    title = _profile_job_string(job["title"], "title")

    collections: dict[str, list[dict[str, Any]]] = {}
    for name in PROFILE_JOB_COLLECTIONS:
        raw_values = _profile_job_list(job.get(name, []), name)
        values: list[dict[str, Any]] = []
        for index, raw_value in enumerate(raw_values):
            value = _profile_job_mapping(raw_value, f"{name}[{index}]")
            if "source_refs" in value:
                raise OutputFailure("profile-job-source-receipt-owned", f"{name}[{index}].source_refs is owned by the runtime.")
            values.append(copy.deepcopy(value))
        collections[name] = values
    if len(collections["edges"]) > SECURITY_LIMITS["edges"]:
        raise OutputFailure("profile-job-complexity-limit", f"Direct edges exceed the hard limit of {SECURITY_LIMITS['edges']}.")
    collections["edges"].extend(
        _expand_relation_groups(
            job["relation_groups"],
            edge_budget=SECURITY_LIMITS["edges"] - len(collections["edges"]),
        )
    )
    source_assertions = _validate_source_assertions(job["source_assertions"], instruction, collections)
    _validate_expected_counts(
        job["expected_counts"],
        _profile_job_counts(collections),
        _source_assertion_counts(source_assertions),
    )
    receipt = _semantic_receipt(instruction, collections, source_assertions)

    source_items: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    reading_order: list[str] = []
    source_counter = 0

    def attach_receipt(item: dict[str, Any], content_class: str, locator: str, *, include_reading_order: bool = True) -> None:
        nonlocal source_counter
        if "source_refs" in item:
            raise OutputFailure("profile-job-source-receipt-owned", f"{locator}.source_refs is owned by the runtime.")
        item_id = _profile_job_string(item.get("id"), f"{locator}.id")
        source_counter += 1
        source_id = f"source-{source_counter:04d}"
        item["source_refs"] = [source_id]
        source_items.append(
            {
                "id": source_id,
                "source_kind": "natural-language",
                "locator": f"profile-job:{locator}",
                "content_class": content_class,
            }
        )
        kept.append({"source_ids": [source_id], "ir_ids": [item_id], "reason": "Explicit profiled-job semantic item retained."})
        if include_reading_order:
            reading_order.append(item_id)

    for collection_name in PROFILE_JOB_COLLECTIONS:
        for index, item in enumerate(collections[collection_name]):
            attach_receipt(item, _CONTENT_CLASS[collection_name], f"{collection_name}[{index}]")
            if collection_name == "nodes" and "members" in item:
                for member_index, raw_member in enumerate(_profile_job_list(item["members"], f"nodes[{index}].members")):
                    member = _profile_job_mapping(raw_member, f"nodes[{index}].members[{member_index}]")
                    item["members"][member_index] = member
                    attach_receipt(member, "entity", f"nodes[{index}].members[{member_index}]")
            if collection_name == "series":
                for datum_index, raw_datum in enumerate(_profile_job_list(item.get("data"), f"series[{index}].data")):
                    datum = _profile_job_mapping(raw_datum, f"series[{index}].data[{datum_index}]")
                    item["data"][datum_index] = datum
                    attach_receipt(datum, "value", f"series[{index}].data[{datum_index}]", include_reading_order=False)

    language_value = job.get("language", "auto")
    if language_value == "auto":
        language = {"mode": "auto"}
    else:
        language = {"mode": "explicit", "tag": _profile_job_string(language_value, "language")}
    raw_request = {
        "instruction": instruction,
        "source": {"kind": "natural-language", "content": instruction},
        "diagram_type": _profile_job_string(job["diagram_type"], "diagram_type"),
        "variant_ids": copy.deepcopy(job.get("variant_ids", [])),
        "structural_profile": _profile_job_string(job["structural_profile"], "structural_profile"),
        "structural_override": {"status": "none"},
        "size": job.get("size", "fit"),
        "detail": job.get("detail", "balanced"),
        "audience": job.get("audience", "mixed"),
        "visual_mode": job.get("visual_mode", "neutral-light"),
        "language": language,
        "format": "svg",
        "motion": "none",
    }
    normalized_request = normalize_request(raw_request)
    parsed_model = {
        "title": title,
        "route_candidates": [
            {
                "type": normalized_request["diagram_type"],
                "confidence": "high",
                "evidence": ["request:explicit profiled-job diagram_type"],
                "compatible": True,
                "viable": True,
                "materially_distinct": False,
            }
        ],
        "variant_ids": copy.deepcopy(normalized_request["variant_ids"]),
        **collections,
        "source_items": source_items,
        "fidelity": {"kept": kept, "merged": [], "dropped": [], "source_rot": [], "invented_count": 0},
        "accessibility": {
            "name": title,
            "description": job.get("accessibility_description", instruction),
            "reading_order": reading_order,
            "data_representation_required": bool(
                collections["series"]
                or normalized_request["diagram_type"] in {"dp-security-matrix", "treemap", "sankey"}
            ),
        },
    }
    ir = build_ir(normalized_request, parsed_model)
    return normalized_request, ir, receipt


def create_profiled_diagram(
    raw_request: Mapping[str, Any],
    semantic_model: Mapping[str, Any],
    output_dir: str | Path,
    *,
    semantic_receipt: Mapping[str, Any] | None = None,
) -> ProfiledWriteResult:
    """Resolve, render, validate, and atomically publish exactly SVG + ledger.

    ``semantic_model`` is validated common IR, not SVG or free-form drawing
    instructions.  ``output_dir`` must not already exist so the completed pair
    can be made visible with one directory rename and no partial artifact set.
    """

    ir = validate_semantics(semantic_model)
    request = normalize_request(raw_request)
    reconciled_receipt = _reconcile_semantic_receipt(semantic_receipt, request, ir) if semantic_receipt is not None else None
    if request["format"] != "svg" or request["motion"] != "none":
        raise OutputFailure("profiled-output-contract", "The one-call profile renderer publishes one static SVG plus one ledger; request format=svg and motion=none.")
    target = Path(output_dir).expanduser()
    if target.exists():
        raise OutputFailure("output-exists", "Atomic profile output requires a new, non-existing output directory.", status="needs-clarification")
    requested_parent = target.parent
    if requested_parent.is_symlink() or not requested_parent.is_dir():
        raise OutputFailure("output-parent-invalid", "Output parent must be an existing non-symlink directory.")
    parent = requested_parent.resolve()
    resolved_target = parent / target.name
    if not target.name or target.name in {".", ".."}:
        raise OutputFailure("output-target-invalid", "Output directory needs one explicit safe final name.")

    plan = build_profiled_plan(ir, request)
    binding = plan["profile_binding"]
    svg = render_profiled_svg(ir, request, plan)
    geometry = validate_rendered_geometry(svg, ir, binding)
    bundle = export_profiled_artifacts(ir, request, svg, binding, auto_detect_rasterizer=False, motion_runtime=False)
    if set(bundle.artifacts) != {"svg"}:
        raise OutputFailure("profiled-output-ambiguous", "The one-call renderer must produce exactly one SVG before ledger publication.")
    ledger = dict(bundle.ledger)
    ledger["renderer_version"] = PROFILE_RENDERER_VERSION
    ledger["structural_conformance"] = "pass"
    ledger["geometry_validation"] = geometry
    ledger["validation"] = {**dict(ledger["validation"]), "structural_conformance": "pass", "geometry": "pass"}
    if reconciled_receipt is not None:
        ledger["semantic_receipt_sha256"] = hashlib.sha256(canonical_json(reconciled_receipt).encode("utf-8")).hexdigest()
        ledger["source_assertions_sha256"] = reconciled_receipt["source_assertions_sha256"]
        ledger["semantic_coverage"] = "pass"
        ledger["semantic_coverage_scope"] = "declared-source-assertions-to-validated-ir"
        ledger["source_interpretation_attestation"] = "agent-authored-not-independently-proven"
        ledger["validation"] = {**dict(ledger["validation"]), "semantic_coverage": "pass"}
    validate_profile_ledger(ledger, binding)
    svg_bytes = bundle.artifacts["svg"].content
    ledger_bytes = (json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

    stage = Path(tempfile.mkdtemp(prefix=f".{target.name}.", dir=parent))
    try:
        (stage / "diagram.svg").write_bytes(svg_bytes)
        (stage / "diagram.ledger.json").write_bytes(ledger_bytes)
        if {item.name for item in stage.iterdir()} != {"diagram.svg", "diagram.ledger.json"}:
            raise OutputFailure("profiled-output-ambiguous", "Atomic stage contains an unexpected file.")
        os.replace(stage, resolved_target)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return ProfiledWriteResult(
        output_dir=str(resolved_target),
        svg_path=str(resolved_target / "diagram.svg"),
        ledger_path=str(resolved_target / "diagram.ledger.json"),
        selected_profile=str(binding["selected_profile"]),
        layout_engine=str(binding["layout_engine"]),
        svg_sha256=hashlib.sha256(svg_bytes).hexdigest(),
        ledger_sha256=hashlib.sha256(ledger_bytes).hexdigest(),
    )


def create_profiled_diagram_from_job(job: Mapping[str, Any], output_dir: str | Path) -> ProfiledWriteResult:
    """Materialize a bounded semantic job, reconcile its receipt, and call the canonical one-call renderer."""

    request, ir, receipt = _materialize_profile_job(job)
    return create_profiled_diagram(request, ir, output_dir, semantic_receipt=receipt)


def _load_profile_job(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    descriptor: int | None = None
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
        )
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size == 0 or metadata.st_size > PROFILE_JOB_INPUT_LIMIT:
            raise OutputFailure("profile-job-input-invalid", "Job path must be a non-empty regular non-symlink file no larger than 2 MiB.")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            content = stream.read(PROFILE_JOB_INPUT_LIMIT + 1)
    except OutputFailure:
        raise
    except OSError as error:
        raise OutputFailure("profile-job-input-invalid", "Job path must be an existing readable regular non-symlink file.") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if not content or len(content) > PROFILE_JOB_INPUT_LIMIT:
        raise OutputFailure("profile-job-input-invalid", "Job file is empty or exceeds the 2 MiB limit.")
    try:
        value = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OutputFailure("profile-job-json-invalid", "Job file must contain one valid UTF-8 JSON object.") from error
    return _profile_job_mapping(value, "job")


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create one validated profiled SVG + ledger pair from a bounded JSON job without a custom Python driver.",
    )
    parser.add_argument("--job", help="Path to one UTF-8 JSON profiled job. Use --print-job-contract to inspect fields.")
    parser.add_argument("--output-dir", help="New, non-existing directory that will atomically receive diagram.svg and diagram.ledger.json.")
    parser.add_argument("--print-job-contract", action="store_true", help="Print the machine-readable profiled-job contract and exit.")
    args = parser.parse_args(argv)
    if args.print_job_contract:
        if args.job or args.output_dir:
            parser.error("--print-job-contract cannot be combined with --job or --output-dir")
        print(json.dumps(PROFILE_JOB_CONTRACT, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if not args.job or not args.output_dir:
        parser.error("--job and --output-dir are required for creation")
    try:
        result = create_profiled_diagram_from_job(_load_profile_job(args.job), args.output_dir)
    except Exception as error:
        issue_method = getattr(error, "issue", None)
        issue = issue_method() if callable(issue_method) else {
            "code": str(getattr(error, "code", "profile-job-failed")),
            "stage": str(getattr(error, "stage", "profile-job")),
            "message": str(getattr(error, "message", "Profiled job failed closed.")),
        }
        print(json.dumps({"status": "FAIL", "issue": issue}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "PASS",
                "output_dir": result.output_dir,
                "files": {
                    "diagram.svg": {"path": result.svg_path, "sha256": result.svg_sha256},
                    "diagram.ledger.json": {"path": result.ledger_path, "sha256": result.ledger_sha256},
                },
                "selected_profile": result.selected_profile,
                "layout_engine": result.layout_engine,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


__all__ = [
    "Artifact", "ExportBundle", "ProfiledWriteResult", "OUTPUT_CAPABILITIES", "OUTPUT_VERSION",
    "OutputFailure", "RasterizerAdapter", "detect_rasterizer", "export_artifacts", "export_profiled_artifacts",
    "PROFILE_JOB_CONTRACT", "create_profiled_diagram", "create_profiled_diagram_from_job", "registered_capabilities", "write_bundle",
]


if __name__ == "__main__":
    raise SystemExit(_main())
