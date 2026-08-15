"""P-08 portable output, conditional rasterization, and static-first motion.

The module has no mandatory third-party dependency. It renders validated IR
through the P-07 static renderer, creates self-contained HTML or standalone
SVG, and uses PNG only through an already available bounded adapter. It never
installs software, fetches a resource, or executes imported source content.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Mapping

from diagram_core import CANONICAL_TYPES, canonical_json, normalize_request
from full_renderer import RENDERER_VERSION, render_static
from motion_catalog import select_motion_capabilities
from safe_import import validate_workspace_target
from semantic_grammars import validate_semantics


OUTPUT_VERSION = "p08-output-1"
SVG_NS = "http://www.w3.org/2000/svg"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RASTER_TIMEOUT_SECONDS = 30
RASTER_OUTPUT_LIMIT = 64 * 1024 * 1024
ET.register_namespace("", SVG_NS)

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
                value = words["missing"] if datum.get("missing") else str(datum.get("value"))
                rows.append(f"<tr><th scope=\"row\">{escape(str(datum['domain']))}</th><td>{escape(str(series['label']))}</td><td>{escape(value)}</td><td>{escape(str(unit))}</td></tr>")
                plain.append(f"{series['label']} / {datum['domain']} = {value} {unit}".strip())
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


def _prepare_svg(svg: str, ir: Mapping[str, Any], mode: str, size: str, *, annotate_motion: bool) -> tuple[str, int]:
    root = ET.fromstring(svg)
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


def export_artifacts(
    ir_value: Mapping[str, Any],
    raw_request: Mapping[str, Any],
    *,
    rasterizer: RasterizerAdapter | None = None,
    auto_detect_rasterizer: bool = True,
    motion_runtime: bool = True,
    font_substitution: str | None = None,
) -> ExportBundle:
    ir = validate_semantics(ir_value)
    request = normalize_request(raw_request)
    if request["diagram_type"] != "auto" and request["diagram_type"] != ir["diagram"]["type"]:
        raise OutputFailure("output-type-mismatch", "The validated IR type does not match the explicitly requested diagram type.")
    static = render_static(ir, request["visual_mode"], coverage_badge=False)
    standalone_svg, _ = _prepare_svg(static.svg, ir, request["visual_mode"], request["size"], annotate_motion=False)
    motion_svg, target_count = _prepare_svg(static.svg, ir, request["visual_mode"], request["size"], annotate_motion=request["motion"] != "none" and motion_runtime)
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
        "schema_version": "1.0",
        "output_version": OUTPUT_VERSION,
        "renderer_version": RENDERER_VERSION,
        "requested_format": requested_format,
        "delivered_artifacts": delivered,
        "artifacts": {key: {"name": value.name, "media_type": value.media_type, "sha256": value.sha256, "bytes": len(value.content)} for key, value in artifacts.items()},
        "language": ir["diagram"]["language"],
        "diagram_type": ir["diagram"]["type"],
        "dials": {key: request[key] for key in ("size", "detail", "audience", "visual_mode", "format", "motion")},
        "ir_hash": hashlib.sha256(canonical_json(ir).encode("utf-8")).hexdigest(),
        "base_static_svg_hash": static.sha256,
        "standalone_svg_hash": hashlib.sha256(standalone_svg.encode("utf-8")).hexdigest(),
        "rasterizer": active_rasterizer.name if active_rasterizer else None,
        "font_policy": {"network_fetch": False, "stack": "Inter, Noto Sans, Arial, Helvetica Neue, system-ui, sans-serif", "substitution": font_substitution},
        "motion_capabilities": motion_capabilities,
        "output_capabilities": list(OUTPUT_CAPABILITIES),
        "static_fallback_complete": True,
        "warnings": warnings,
        "validation": {"semantic": "pass", "svg": "pass", "html": "pass" if "html" in artifacts else "not-requested", "png": "pass" if "png" in artifacts else "unavailable-or-not-requested"},
    }
    return ExportBundle(artifacts, ledger)


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


__all__ = [
    "Artifact", "ExportBundle", "OUTPUT_CAPABILITIES", "OUTPUT_VERSION",
    "OutputFailure", "RasterizerAdapter", "detect_rasterizer", "export_artifacts",
    "registered_capabilities", "write_bundle",
]
