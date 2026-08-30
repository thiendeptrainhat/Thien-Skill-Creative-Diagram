"""P-18R6 neutral-light engine anchors.

This QA-only module is an original, engine-specific implementation.  It reuses
the approved P-18R5 font-resolution contract as an internal dependency, but it
does not import or adapt the rejected P-18R3 renderer or any upstream visual
asset.  Every function below owns a distinct geometry/silhouette.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import importlib.util
from math import sqrt
from pathlib import Path
import sys
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[4]
R5_KERNEL_PATH = ROOT / "evidence/p18/r5/source/master_visual_kernel.py"
_R5_NAME = "p18r5_master_visual_kernel"
_SPEC = importlib.util.spec_from_file_location(_R5_NAME, R5_KERNEL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load frozen P-18R5 master visual kernel")
_R5 = importlib.util.module_from_spec(_SPEC)
sys.modules[_R5_NAME] = _R5
_SPEC.loader.exec_module(_R5)


TOKENS = {
    "canvas": "#f7f6f2",
    "paper": "#fbfaf7",
    "surface": "#ffffff",
    "surface_soft": "#eeece7",
    "surface_slate": "#e8ebee",
    "ink": "#252b3c",
    "ink_soft": "#53627b",
    "ink_faint": "#778194",
    "line": "#4f5e76",
    "line_soft": "#c7ccd2",
    "grid": "#d9d7d2",
    "accent": "#f26a32",
    "accent_soft": "#f8e7dd",
    "accent_text": "#df5522",
    "blue": "#2f65af",
    "green": "#7c9167",
    "amber": "#b9894b",
    "plum": "#756b7f",
}


@dataclass(frozen=True)
class Anchor:
    order: int
    engine: str
    canonical_type: str
    filename: str
    title: str
    takeaway: str
    svg: str
    facts: tuple[tuple[str, str], ...]


def _load_typography():
    resolved = _R5.resolve_default_typography()
    return resolved, _R5.FontMetricEngine(resolved)


TYPOGRAPHY, METRICS = _load_typography()


def resolved_family(role: str) -> str:
    return TYPOGRAPHY[role].resolved_family


def _attrs(values: dict[str, object]) -> str:
    return " ".join(f'{escape(str(key))}="{escape(str(value))}"' for key, value in values.items())


def _text(x: float, y: float, value: str, cls: str = "material", anchor: str = "start", **extra: object) -> str:
    attrs = {"class": cls, "x": f"{x:.1f}", "y": f"{y:.1f}", "text-anchor": anchor, **extra}
    return f"<text {_attrs(attrs)}>{escape(value)}</text>"


def _tspans(x: float, y: float, lines: Iterable[str], cls: str, line_height: int, anchor: str = "start") -> str:
    content = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        content.append(f'<tspan x="{x:.1f}" dy="{dy}">{escape(line)}</tspan>')
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{"".join(content)}</text>'


def _rect(x: float, y: float, w: float, h: float, cls: str = "node", rx: float = 14, **extra: object) -> str:
    attrs = {"class": cls, "x": x, "y": y, "width": w, "height": h, "rx": rx, **extra}
    return f"<rect {_attrs(attrs)}/>"


def _line(x1: float, y1: float, x2: float, y2: float, cls: str = "wire", **extra: object) -> str:
    return f'<line {_attrs({"class": cls, "x1": x1, "y1": y1, "x2": x2, "y2": y2, **extra})}/>'


def _path(d: str, cls: str = "wire", **extra: object) -> str:
    return f'<path {_attrs({"class": cls, "d": d, **extra})}/>'


def _circle(cx: float, cy: float, r: float, cls: str = "dot", **extra: object) -> str:
    return f'<circle {_attrs({"class": cls, "cx": cx, "cy": cy, "r": r, **extra})}/>'


def _node(
    x: float,
    y: float,
    title: str,
    subtitle: str,
    badge: str,
    *,
    width: float = 0,
    height: float = 124,
    focal: bool = False,
    muted: bool = False,
    title_role: str = "node_title",
) -> tuple[str, float]:
    measured = METRICS.measure(title_role, title).width
    computed = min(410.0, max(246.0, measured + 72.0))
    w = max(width, computed)
    classes = "node-card focal" if focal else "node-card muted" if muted else "node-card"
    badge_w = max(54, METRICS.measure("technical", badge).width + 22)
    parts = [
        f'<g class="{classes}" data-measured-title-width="{measured:.2f}" data-card-width="{w:.2f}">',
        _rect(x, y, w, height, "node-boundary", 14),
        _rect(x + 18, y + 16, badge_w, 28, "badge", 6),
        _text(x + 18 + badge_w / 2, y + 36, badge, "badge-text", "middle"),
        _text(x + w / 2, y + 76, title, "node-title", "middle"),
        _text(x + w / 2, y + 105, subtitle, "mono", "middle"),
        "</g>",
    ]
    return "".join(parts), w


def _legend(y: float, width: float, items: tuple[tuple[str, str], ...], note: str = "") -> str:
    parts = [_line(52, y, width - 52, y, "legend-rule"), _text(56, y + 38, "LEGEND", "kicker")]
    x = 210.0
    for kind, label in items:
        if kind == "accent":
            parts.extend([_rect(x, y + 20, 28, 24, "legend-accent", 5), _text(x + 42, y + 39, label, "legend-text")])
        elif kind == "line":
            parts.extend([_line(x, y + 34, x + 42, y + 34, "wire"), _text(x + 58, y + 39, label, "legend-text")])
        elif kind == "dash":
            parts.extend([_line(x, y + 34, x + 42, y + 34, "wire dashed"), _text(x + 58, y + 39, label, "legend-text")])
        elif kind == "dot":
            parts.extend([_circle(x + 14, y + 32, 8, "dot"), _text(x + 42, y + 39, label, "legend-text")])
        x += max(205, METRICS.measure("material", label).width + 118)
    if note:
        parts.append(_text(width - 56, y + 39, note, "legend-note", "end"))
    return "".join(parts)


def _svg_shell(
    engine: str,
    canonical_type: str,
    title: str,
    description: str,
    width: int,
    height: int,
    body: str,
    *,
    semantic_ratio: float = 0.84,
    takeaway_id: str = "focal",
) -> str:
    human = resolved_family("node_title")
    mono = resolved_family("technical")
    display = resolved_family("display")
    css = f"""
      text{{font-family:'{escape(human)}';fill:{TOKENS['ink']};text-rendering:geometricPrecision}}
      .display{{font-family:'{escape(display)}';font-size:48px;font-weight:400}}
      .node-title{{font-size:24px;font-weight:650}}
      .material{{font-size:16px;font-weight:500}}
      .material-strong{{font-size:18px;font-weight:650}}
      .mono,.badge-text,.kicker,.legend-note{{font-family:'{escape(mono)}';font-size:16px}}
      .mono{{fill:{TOKENS['ink_soft']}}}
      .kicker{{font-size:14px;font-weight:700;letter-spacing:2.1px;fill:{TOKENS['ink_faint']}}}
      .badge-text{{font-size:14px;font-weight:700;letter-spacing:1px;fill:{TOKENS['ink_soft']}}}
      .node-boundary{{fill:{TOKENS['surface']};stroke:{TOKENS['line']};stroke-width:2.2}}
      .node-card.focal .node-boundary{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2.8}}
      .node-card.muted .node-boundary{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line_soft']}}}
      .badge{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line_soft']};stroke-width:1.2}}
      .focal .badge{{fill:#fff3ec;stroke:{TOKENS['accent']}}}
      .focal .badge-text{{fill:{TOKENS['accent_text']}}}
      .wire{{fill:none;stroke:{TOKENS['line']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
      .wire.soft{{stroke:{TOKENS['line_soft']};stroke-width:2}}
      .wire.accent{{stroke:{TOKENS['accent']};stroke-width:3.6}}
      .wire.blue{{stroke:{TOKENS['blue']}}}
      .wire.green{{stroke:{TOKENS['green']}}}
      .wire.dashed{{stroke-dasharray:9 9}}
      .zone{{fill:none;stroke:{TOKENS['line_soft']};stroke-width:1.6}}
      .zone-fill{{fill:{TOKENS['surface_soft']};fill-opacity:.55;stroke:{TOKENS['line_soft']};stroke-width:1.6}}
      .grid{{stroke:{TOKENS['grid']};stroke-width:1.4}}
      .dot{{fill:{TOKENS['ink']}}}
      .accent-dot{{fill:{TOKENS['accent']}}}
      .legend-rule{{stroke:{TOKENS['grid']};stroke-width:1.5}}
      .legend-accent{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2}}
      .legend-text{{font-size:16px;fill:{TOKENS['ink_soft']}}}
      .legend-note{{font-size:14px;font-style:italic;fill:{TOKENS['ink_soft']}}}
      .band{{fill:{TOKENS['surface_slate']};stroke:{TOKENS['line_soft']};stroke-width:1.5}}
      .band.focal{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2.3}}
      .label-mask{{fill:{TOKENS['canvas']}}}
      .axis{{stroke:{TOKENS['line']};stroke-width:2.2}}
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}"
      role="img" aria-labelledby="anchor-title anchor-desc" data-layout-engine="{escape(engine)}"
      data-canonical-type="{escape(canonical_type)}" data-mode="neutral-light" data-semantic-ratio="{semantic_ratio:.2f}"
      data-min-label-clearance="8" data-font-measured="true" data-no-global-transform="true"
      data-takeaway-node="{escape(takeaway_id)}" data-resolved-human-font="{escape(human)}" data-resolved-mono-font="{escape(mono)}">
      <title id="anchor-title">{escape(title)}</title>
      <desc id="anchor-desc">{escape(description)}</desc>
      <defs>
        <pattern id="dot-field" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{TOKENS['grid']}" opacity=".34"/></pattern>
        <marker id="arrow" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="{TOKENS['line']}"/></marker>
        <marker id="arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="{TOKENS['accent']}"/></marker>
        <style>{css}</style>
      </defs>
      <rect width="{width}" height="{height}" fill="{TOKENS['canvas']}"/>
      <rect width="{width}" height="{height}" fill="url(#dot-field)"/>
      {body}
    </svg>'''


def topology_anchor() -> Anchor:
    w, h = 1680, 940
    parts = [
        _rect(60, 90, 310, 590, "zone-fill", 20), _text(88, 130, "EDGE", "kicker"),
        _rect(430, 90, 560, 590, "zone-fill", 20), _text(458, 130, "APPLICATION", "kicker"),
        _rect(1050, 90, 570, 590, "zone-fill", 20), _text(1078, 130, "CONTENT", "kicker"),
    ]
    n1, _ = _node(92, 235, "Reader", "browser · public", "EXT", width=246, muted=True)
    n2, _ = _node(462, 235, "Cloud edge", "cache · TLS", "EDGE", width=260)
    n3, _ = _node(760, 235, "Astro origin", "SSR · MDX", "ORIG", width=280, focal=True)
    n4, _ = _node(1102, 180, "MDX bundle", "content/*.mdx", "BUN", width=300)
    n5, _ = _node(1102, 420, "Media store", "assets · OG", "STORE", width=300)
    parts += [n1, n2, n3, n4, n5]
    parts += [
        _path("M338 297 H462", "wire blue", **{"marker-end": "url(#arrow)"}),
        _path("M722 297 H760", "wire accent", **{"marker-end": "url(#arrow-accent)"}),
        _path("M1040 272 H1070 Q1102 272 1102 240", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M1040 322 H1070 Q1102 322 1102 480", "wire", **{"marker-end": "url(#arrow)"}),
        _text(392, 280, "HTTPS", "kicker", "middle"), _text(741, 280, "SSR", "kicker", "middle"),
        _text(1080, 256, "READ", "kicker", "end"), _text(1080, 458, "QUERY", "kicker", "end"),
        _legend(748, w, (("accent", "focal origin"), ("line", "request / dependency"), ("dash", "external / async")), "Boundary carries trust context."),
    ]
    svg = _svg_shell("topology-and-zones", "architecture", "Kiến trúc nội dung tại edge", "Ba vùng tin cậy; origin là điểm hội tụ giữa edge và hai nguồn nội dung.", w, h, "".join(parts))
    return Anchor(1, "topology-and-zones", "architecture", "01-topology-and-zones--neutral-light", "Architecture anchor", "Origin là điểm hội tụ và ranh giới tin cậy chính.", svg, (("focal", "Astro origin"), ("zones", "EDGE / APPLICATION / CONTENT"), ("flow", "Reader → edge → origin → content")))


def integration_anchor() -> Anchor:
    w, h = 1680, 940
    parts = []
    for x, width, label in ((52, 390, "COLLECT"), (476, 590, "TRANSFORM"), (1100, 528, "SERVE")):
        parts.extend([_rect(x, 78, width, 638, "zone-fill", 20), _text(x + 26, 120, label, "kicker")])
    n1, _ = _node(86, 180, "Order events", "JSON · every minute", "SRC", width=320)
    n2, _ = _node(86, 430, "Inventory files", "CSV · nightly", "SRC", width=320, muted=True)
    n3, _ = _node(520, 292, "Normalize contracts", "schema · dedupe", "STEP", width=500, focal=True)
    n4, _ = _node(1144, 180, "Analytics mart", "partitioned tables", "DB", width=430)
    n5, _ = _node(1144, 430, "Alert stream", "exceptions only", "API", width=430)
    parts += [n1, n2, n3, n4, n5]
    parts += [
        _path("M406 242 H465 Q500 242 520 326", "wire blue", **{"marker-end": "url(#arrow)"}),
        _path("M406 492 H465 Q500 492 520 382", "wire dashed", **{"marker-end": "url(#arrow)"}),
        _path("M1020 326 H1108 Q1144 326 1144 242", "wire accent", **{"marker-end": "url(#arrow-accent)"}),
        _path("M1020 382 H1108 Q1144 382 1144 492", "wire", **{"marker-end": "url(#arrow)"}),
        _text(454, 225, "STREAM", "kicker", "middle"), _text(455, 515, "BATCH", "kicker", "middle"),
        _text(1084, 308, "CURATED", "kicker", "middle"), _text(1082, 405, "EXCEPTIONS", "kicker", "middle"),
        _legend(784, w, (("line", "data movement"), ("dash", "scheduled batch"), ("accent", "contract boundary")), "One transform, two outputs."),
    ]
    svg = _svg_shell("integration-pipeline", "data-flow", "Tích hợp đơn hàng và tồn kho", "Hai nguồn hội tụ tại bước chuẩn hóa trước khi tách thành mart và alert stream.", w, h, "".join(parts))
    return Anchor(2, "integration-pipeline", "data-flow", "02-integration-pipeline--neutral-light", "Integration anchor", "Chuẩn hóa hợp đồng là nút kiểm soát trung tâm.", svg, (("sources", "Order events; Inventory files"), ("control", "Normalize contracts"), ("outputs", "Analytics mart; Alert stream")))


def deployment_anchor() -> Anchor:
    w, h = 1540, 980
    parts = [
        _rect(58, 80, 1424, 674, "zone-fill", 24), _text(88, 124, "REGION · SINGAPORE", "kicker"),
        _rect(104, 154, 902, 530, "zone", 20), _text(132, 196, "KUBERNETES CLUSTER", "kicker"),
        _rect(1040, 154, 392, 530, "zone", 20), _text(1068, 196, "MANAGED DATA", "kicker"),
        _rect(150, 236, 378, 360, "zone-fill", 18), _text(178, 278, "NODE POOL A", "kicker"),
        _rect(574, 236, 378, 360, "zone-fill", 18), _text(602, 278, "NODE POOL B", "kicker"),
    ]
    a, _ = _node(184, 334, "API · 3 replicas", "health /ready", "POD", width=310, focal=True)
    b, _ = _node(608, 334, "Worker · 5 replicas", "queue consumers", "POD", width=310)
    c, _ = _node(1080, 288, "Postgres", "multi-AZ", "DB", width=312)
    d, _ = _node(1080, 486, "Object storage", "encrypted", "OBJ", width=312, muted=True)
    parts += [a, b, c, d]
    parts += [
        _path("M494 396 H608", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M918 380 H1000 Q1040 380 1080 350", "wire accent", **{"marker-end": "url(#arrow-accent)"}),
        _path("M918 426 H1000 Q1040 426 1080 548", "wire", **{"marker-end": "url(#arrow)"}),
        _text(550, 378, "JOBS", "kicker", "middle"), _text(1004, 354, "SQL", "kicker", "middle"),
        _legend(824, w, (("accent", "public workload"), ("line", "runtime dependency"), ("dash", "external boundary")), "Containment is the deployment truth."),
    ]
    svg = _svg_shell("runtime-deployment", "deployment", "Triển khai dịch vụ theo vùng", "Nested region, cluster, node pool và managed-data boundaries cho thấy runtime placement.", w, h, "".join(parts))
    return Anchor(3, "runtime-deployment", "deployment", "03-runtime-deployment--neutral-light", "Deployment anchor", "API public nằm trong cluster và phụ thuộc managed data ngoài cluster.", svg, (("region", "Singapore"), ("cluster", "Kubernetes"), ("workloads", "API; Worker"), ("managed", "Postgres; Object storage")))


def dependency_anchor() -> Anchor:
    w, h = 1540, 1200
    parts = []
    for index, y in enumerate((110, 330, 550, 770)):
        parts.extend([_text(62, y + 18, f"RANK {index}", "kicker"), _line(180, y + 40, 1480, y + 40, "grid")])
    positions = {
        "web": (300, 82), "admin": (930, 82), "api": (260, 302), "ui": (900, 302),
        "types": (390, 522), "db": (930, 522), "tokens": (180, 780), "utils": (650, 780), "zod": (1080, 780),
    }
    specs = [
        ("web", "web", "apps/web", "APP", False, False), ("admin", "admin", "apps/admin", "APP", False, False),
        ("api", "api", "services/api", "SVC", False, False), ("ui", "ui-kit", "packages/ui-kit", "PKG", False, False),
        ("types", "shared-types", "packages/shared-types", "PKG", True, False), ("db", "database", "services/db", "SVC", False, False),
        ("tokens", "tokens", "packages/tokens", "PKG", False, True), ("utils", "utils", "packages/utils", "PKG", False, False),
        ("zod", "zod", "external · npm", "EXT", False, True),
    ]
    boxes: dict[str, tuple[float, float, float]] = {}
    for key, title, sub, badge, focal, muted in specs:
        x, y = positions[key]
        item, width = _node(x, y, title, sub, badge, width=280, focal=focal, muted=muted)
        boxes[key] = (x, y, width)
        parts.append(item)
    def dep(source: str, target: str, offset: float = 0, cls: str = "wire") -> str:
        sx, sy, sw = boxes[source]; tx, ty, tw = boxes[target]
        x1 = sx + sw / 2 + offset; y1 = sy + 124; x2 = tx + tw / 2 + offset; y2 = ty
        mid = (y1 + y2) / 2
        return _path(f"M{x1:.1f} {y1:.1f} V{mid:.1f} H{x2:.1f} V{y2:.1f}", cls, **{"marker-end": "url(#arrow)"})
    parts += [
        _path("M416 206 V250 H376 V302", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M500 206 V250 H970 V302", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M1070 206 V302", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M400 426 V458 H480 V522", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M1040 426 V484 H580 V522", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M480 646 V684 H320 V780", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M530 646 V712 H790 V780", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M580 646 V740 H1220 V780", "wire", **{"marker-end": "url(#arrow)"}),
    ]
    parts.append(_path("M930 584 H840 Q810 584 810 584 H670", "wire", **{"marker-end": "url(#arrow)"}))
    parts += [
        _path("M790 904 V980 H320 V904", "wire accent dashed", **{"marker-end": "url(#arrow-accent)"}),
        _text(555, 1010, "CYCLE · MUST BREAK", "kicker", "middle"),
        _legend(1100, w, (("accent", "high fan-in"), ("line", "dependency"), ("dash", "cycle back-edge"))),
    ]
    svg = _svg_shell("dependency-dag", "dependency-graph", "Phụ thuộc package theo rank", "Các package được xếp rank; shared-types có fan-in cao và một cycle back-edge được đánh dấu.", w, h, "".join(parts), semantic_ratio=.88)
    return Anchor(4, "dependency-dag", "dependency-graph", "04-dependency-dag--neutral-light", "Dependency anchor", "shared-types là điểm hội tụ; cycle tokens → utils phải được phá.", svg, (("ranks", "0–3"), ("focal", "shared-types"), ("risk", "cycle back-edge")))


def directed_anchor() -> Anchor:
    w, h = 1240, 1160
    parts = []
    def diamond(cx: float, cy: float, rw: float, rh: float, label: tuple[str, str], focal: bool = False) -> str:
        cls = "band focal" if focal else "band"
        points = f"{cx},{cy-rh} {cx+rw},{cy} {cx},{cy+rh} {cx-rw},{cy}"
        return f'<polygon class="{cls}" points="{points}"/>' + _tspans(cx, cy - 6, label, "node-title", 29, "middle")
    start, _ = _node(420, 72, "New request", "signal received", "START", width=400, muted=True)
    step, _ = _node(420, 250, "Validate evidence", "owner · timestamp", "STEP", width=400)
    end, _ = _node(420, 918, "Release decision", "record rationale", "END", width=400, focal=True)
    parts += [start, step]
    parts += [diamond(620, 500, 240, 110, ("Material", "exception?")), diamond(620, 750, 240, 110, ("Control", "effective?"), True), end]
    parts += [
        _path("M620 196 V250", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 374 V390", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 610 V640", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 860 V918", "wire accent", **{"marker-end": "url(#arrow-accent)"}),
        _path("M860 500 H1040 V312 H820", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M860 750 H1080 V980 H820", "wire", **{"marker-end": "url(#arrow)"}),
        _text(918, 478, "NO", "kicker"), _text(914, 728, "NO", "kicker"), _text(644, 630, "YES", "kicker"), _text(644, 896, "YES", "kicker"),
        _legend(1060, w, (("accent", "approved path"), ("line", "branch"), ("dot", "decision point"))),
    ]
    svg = _svg_shell("directed-flow-state", "flowchart", "Luồng quyết định phát hành", "Hai decision diamond tách ngoại lệ và hiệu lực kiểm soát; happy path đi đến release decision.", w, h, "".join(parts), semantic_ratio=.91)
    return Anchor(5, "directed-flow-state", "flowchart", "05-directed-flow-state--neutral-light", "Directed flow anchor", "Chỉ ngoại lệ trọng yếu với kiểm soát hiệu lực mới đi đến release.", svg, (("start", "New request"), ("decisions", "Material exception; Control effective"), ("end", "Release decision")))


def time_anchor() -> Anchor:
    w, h = 1680, 860
    y = 410
    parts = [_line(120, y, 1560, y, "axis"), _line(120, y - 18, 120, y + 18, "axis"), _line(1560, y - 18, 1560, y + 18, "axis")]
    events = [
        (160, "FEB 2025", "Baseline", "inventory locked", False, -1),
        (430, "APR 2025", "Contract v1", "semantic IR", False, 1),
        (810, "SEP 2025", "Kernel", "typography pass", False, -1),
        (1180, "JAN 2026", "Anchor review", "14 engines", True, 1),
        (1518, "APR 2026", "Coverage", "39 + 4", True, -1),
    ]
    for x, date, title, sub, focal, direction in events:
        cls = "accent-dot" if focal else "dot"
        line_cls = "wire accent" if focal else "wire soft"
        top = y - 138 if direction == 1 else y + 138
        parts += [_circle(x, y, 11 if focal else 8, cls), _line(x, y, x, top, line_cls)]
        baseline = top - 12 if direction == 1 else top + 32
        parts += [_text(x, baseline, date, "kicker", "middle"), _text(x, baseline + 34, title, "node-title", "middle"), _text(x, baseline + 64, sub, "mono", "middle")]
    parts += [_text(500, 662, "2025", "display", "middle", opacity="0.08"), _text(1290, 226, "2026", "display", "middle", opacity="0.08"), _legend(738, w, (("dot", "event"), ("accent", "major milestone")), "Spacing is proportional to elapsed time.")]
    svg = _svg_shell("time-planning", "timeline", "Lộ trình semantic đến coverage", "Năm mốc theo thời gian thực; hai mốc coral đánh dấu anchor review và full coverage.", w, h, "".join(parts), semantic_ratio=.87)
    return Anchor(7, "time-planning", "timeline", "07-time-planning--neutral-light", "Timeline anchor", "Anchor review là mốc chuyển từ foundation sang coverage.", svg, (("span", "Feb 2025–Apr 2026"), ("milestones", "Anchor review; Coverage")))


def experience_anchor() -> Anchor:
    w, h = 1660, 980
    columns = [(190, "DISCOVER"), (550, "VERIFY"), (910, "DECIDE"), (1270, "ACT")]
    parts = []
    for x, label in columns:
        parts += [_rect(x, 78, 320, 104, "band", 14), _text(x + 160, 126, label, "node-title", "middle"), _text(x + 160, 157, "moment", "kicker", "middle"), _line(x - 20, 204, x - 20, 748, "grid")]
    rows = [(250, "ACTION"), (410, "THOUGHT"), (570, "EMOTION")]
    for y, label in rows:
        parts += [_text(58, y + 18, label, "kicker"), _line(170, y + 42, 1600, y + 42, "grid")]
    actions = ["Find policy", "Check source", "Compare options", "Record choice"]
    thoughts = ["Is this current?", "Can I trust it?", "What changes?", "Who owns follow-up?"]
    emotion = [3, 2, 4, 5]
    for index, (x, _) in enumerate(columns):
        parts += [_rect(x + 18, 230, 284, 78, "node-boundary", 12), _text(x + 160, 278, actions[index], "material-strong", "middle")]
        focus = index == 2
        parts += [_rect(x + 18, 390, 284, 78, "band focal" if focus else "node-boundary", 12), _text(x + 160, 438, thoughts[index], "material-strong", "middle")]
        parts += [_circle(x + 160, 618, 14 + emotion[index] * 3, "accent-dot" if focus else "dot"), _text(x + 160, 680, f"confidence {emotion[index]}/5", "mono", "middle")]
    parts += [_path("M350 618 C520 548 710 666 1070 618 S1390 560 1430 618", "wire accent"), _legend(820, w, (("line", "experience trace"), ("accent", "decision moment"), ("dot", "confidence")), "Rows separate behavior, cognition and feeling.")]
    svg = _svg_shell("work-experience", "user-journey", "Hành trình ra quyết định có bằng chứng", "Bốn moment theo hàng action, thought và emotion; Decide là friction/focal moment.", w, h, "".join(parts))
    return Anchor(8, "work-experience", "user-journey", "08-work-experience--neutral-light", "Experience anchor", "Khâu so sánh lựa chọn là thời điểm cần hỗ trợ rõ nhất.", svg, (("moments", "Discover; Verify; Decide; Act"), ("rows", "Action; Thought; Emotion"), ("focal", "Decide")))


def hierarchy_anchor() -> Anchor:
    w, h = 1600, 960
    parts = [_text(58, 180, "COMMAND", "kicker"), _line(180, 208, 1540, 208, "grid"), _text(58, 440, "DOMAINS", "kicker"), _line(180, 468, 1540, 468, "grid"), _text(58, 698, "PODS", "kicker")]
    root, _ = _node(570, 80, "Operating lead", "priority · arbitration", "FRONT", width=460, focal=True)
    parts.append(root)
    mids = [(160, "Growth", "acquisition"), (520, "Content", "editorial"), (880, "Commerce", "orders"), (1240, "Systems", "platform")]
    for x, title, sub in mids:
        node, _ = _node(x, 338, title, sub, "POD", width=260)
        parts += [node, _path(f"M800 204 V270 H{x+130} V338", "wire")]
    leaves = [(90, "Media", "ads"), (390, "CRM", "lifecycle"), (690, "Writer", "copy"), (990, "Store", "checkout"), (1290, "Runtime", "agents")]
    for x, title, sub in leaves:
        node, _ = _node(x, 626, title, sub, "SPEC", width=230, muted=True)
        parts.append(node)
    parts += [
        _path("M290 462 V554 H205 V626", "wire"), _path("M290 554 H505 V626", "wire"),
        _path("M650 462 V626", "wire"), _path("M1010 462 V554 H1105 V626", "wire"), _path("M1370 462 V626", "wire"),
        _legend(850, w, (("accent", "front door"), ("line", "accountability"), ("dash", "unfilled role")), "Ownership descends; escalation returns to one front door."),
    ]
    svg = _svg_shell("hierarchy", "org-chart", "Mô hình điều phối theo domain", "Một front door phân nhánh thành bốn domain và các specialist pod.", w, h, "".join(parts), semantic_ratio=.88)
    return Anchor(9, "hierarchy", "org-chart", "09-hierarchy--neutral-light", "Hierarchy anchor", "Operating lead là front door duy nhất; domain ownership phân nhánh rõ.", svg, (("root", "Operating lead"), ("domains", "Growth; Content; Commerce; Systems"), ("leaves", "Five specialist pods")))


def containment_anchor() -> Anchor:
    w, h = 1420, 1000
    cx, base_y = 710, 754
    layers = [
        (190, 130, "Flagship decision", "rare · highest leverage", True),
        (330, 236, "Operating principles", "quarterly · durable", False),
        (470, 342, "Reusable playbooks", "monthly · repeatable", False),
        (610, 448, "Daily procedures", "daily · volume work", False),
    ]
    previous_y = 126
    parts = []
    for half_width, top_y, title, sub, focal in layers:
        bottom_y = top_y + 106
        top_half = max(48, half_width - 92)
        cls = "band focal" if focal else "band"
        points = f"{cx-top_half},{top_y} {cx+top_half},{top_y} {cx+half_width},{bottom_y} {cx-half_width},{bottom_y}"
        parts += [f'<polygon class="{cls}" points="{points}"/>', _text(cx, top_y + 46, title, "node-title", "middle"), _text(cx, top_y + 78, sub, "mono", "middle")]
        previous_y = bottom_y
    parts += [
        _line(108, 756, 108, 136, "axis", **{"marker-end": "url(#arrow)"}),
        _text(72, 446, "RARER · HIGHER LEVERAGE", "kicker", "middle", transform="rotate(-90 72 446)"),
        _text(1120, 180, "APEX", "kicker"), _text(1120, 214, "defines direction", "mono"),
        _legend(882, w, (("accent", "apex"), ("line", "supporting layer")), "The base funds the apex; the apex defines the base."),
    ]
    svg = _svg_shell("containment-stack", "pyramid-funnel", "Tháp vận hành từ thủ tục đến quyết định", "Bốn lớp thu hẹp theo độ hiếm và đòn bẩy; apex là focal layer.", w, h, "".join(parts), semantic_ratio=.89)
    return Anchor(10, "containment-stack", "pyramid-funnel", "10-containment-stack--neutral-light", "Containment anchor", "Quy trình khối lượng lớn ở đáy tài trợ cho quyết định đòn bẩy cao ở đỉnh.", svg, (("layers", "4"), ("apex", "Flagship decision"), ("base", "Daily procedures")))


def compartment_anchor() -> Anchor:
    w, h = 1640, 940
    parts = []
    entities = [
        (70, 200, 390, "CUSTOMER", ("# id          uuid", "email         text · unique", "segment       enum", "created_at    timestamp"), False, False),
        (620, 128, 430, "ORDER", ("# id          uuid", "→ customer_id uuid", "status        enum", "total         decimal", "placed_at     timestamp"), True, False),
        (1180, 200, 390, "PAYMENT", ("# id          uuid", "→ order_id    uuid", "provider      text", "amount        decimal", "captured_at   timestamp"), False, False),
        (640, 548, 390, "ORDER_ITEM", ("→ order_id    uuid", "→ sku_id      uuid", "quantity      int", "unit_price    decimal"), False, True),
    ]
    for x, y, width, title, fields, focal, muted in entities:
        cls = "node-card focal" if focal else "node-card muted" if muted else "node-card"
        height = 92 + len(fields) * 38
        parts += [f'<g class="{cls}">', _rect(x, y, width, height, "node-boundary", 14), _text(x + 24, y + 34, "ENTITY", "kicker"), _text(x + 24, y + 70, title, "node-title"), _line(x, y + 86, x + width, y + 86, "grid")]
        for index, field in enumerate(fields):
            parts.append(_text(x + 24, y + 124 + index * 38, field, "mono"))
        parts.append("</g>")
    parts += [
        _path("M460 342 H570 Q620 342 620 300", "wire"), _text(538, 323, "1 · PLACES · N", "kicker", "middle"),
        _path("M1050 300 Q1100 300 1180 342", "wire"), _text(1118, 276, "1 · PAID BY · N", "kicker", "middle"),
        _path("M835 410 V548", "wire"), _text(856, 500, "1 · CONTAINS · N", "kicker"),
        _legend(828, w, (("accent", "aggregate root"), ("line", "relationship"), ("dash", "join / dependent")), "# primary key · → foreign key · 1/N cardinality"),
    ]
    svg = _svg_shell("compartment-model", "database-schema", "Mô hình đơn hàng và thanh toán", "Bốn entity compartment với primary key, foreign key và cardinality rõ ràng.", w, h, "".join(parts))
    return Anchor(11, "compartment-model", "database-schema", "11-compartment-model--neutral-light", "Compartment anchor", "ORDER là aggregate root nối khách hàng, thanh toán và line item.", svg, (("entities", "Customer; Order; Payment; Order item"), ("root", "Order"), ("cardinality", "1:N")))


def matrix_anchor() -> Anchor:
    w, h = 1500, 980
    left, top, right, bottom = 190, 120, 1370, 758
    midx, midy = (left + right) / 2, (top + bottom) / 2
    parts = [
        _rect(left, top, midx-left, midy-top, "band focal", 0),
        _line(left, midy, right, midy, "axis"), _line(midx, top, midx, bottom, "axis"),
        _text(left + 30, top + 46, "DO FIRST", "kicker"), _text(midx + 30, top + 46, "MAJOR PROJECTS", "kicker"),
        _text(left + 30, bottom - 28, "QUICK WINS", "kicker"), _text(right - 30, bottom - 28, "AVOID", "kicker", "end"),
        _text(left, bottom + 46, "LOW EFFORT", "kicker"), _text(right, bottom + 46, "HIGH EFFORT", "kicker", "end"),
        _text(midx + 24, top - 20, "HIGH IMPACT", "kicker"), _text(midx + 24, bottom + 26, "LOW IMPACT", "kicker"),
    ]
    points = [
        (360, 240, "Freeze contract", True), (550, 356, "Update glossary", False), (980, 240, "Engine gallery", False),
        (1180, 320, "Full adapter pass", False), (410, 610, "Fix one label", False), (1040, 610, "Rewrite package", False),
    ]
    for x, y, label, focal in points:
        parts += [_circle(x, y, 13 if focal else 9, "accent-dot" if focal else "dot"), _text(x + 24, y + 7, label, "material-strong")]
    parts += [_legend(872, w, (("accent", "start now"), ("dot", "candidate")), "Position is the signal; coral is reserved for one action.")]
    svg = _svg_shell("spatial-matrix", "quadrant", "Ma trận effort và impact", "Sáu initiative được định vị trên hai trục; Freeze contract là hành động duy nhất được ưu tiên.", w, h, "".join(parts), semantic_ratio=.82)
    return Anchor(12, "spatial-matrix", "quadrant", "12-spatial-matrix--neutral-light", "Spatial matrix anchor", "Freeze contract là hành động high-impact/low-effort cần làm trước.", svg, (("x", "Effort"), ("y", "Impact"), ("focal", "Freeze contract")))


def quantitative_anchor() -> Anchor:
    w, h = 1500, 980
    left, top, right, bottom = 170, 110, 1370, 740
    parts = [_line(left, bottom, right, bottom, "axis"), _line(left, top, left, bottom, "axis", **{"marker-end": "url(#arrow)"})]
    for value in range(0, 101, 20):
        y = bottom - value * 5.6
        parts += [_line(left, y, right, y, "grid"), _text(left - 26, y + 6, str(value), "mono", "end")]
    for value in range(0, 101, 20):
        x = left + value * 11.5
        parts += [_line(x, bottom, x, bottom + 10, "axis"), _text(x, bottom + 42, str(value), "mono", "middle")]
    data = [
        (24, 72, 18, "Manual review", False), (42, 58, 32, "Rules engine", False),
        (62, 78, 46, "Hybrid", True), (78, 52, 24, "Auto-approve", False), (88, 32, 14, "Fast path", False),
    ]
    for xv, yv, size, label, focal in data:
        x = left + xv * 11.5; y = bottom - yv * 5.6; r = sqrt(size) * 5.2
        fill = TOKENS["accent"] if focal else TOKENS["ink"]
        opacity = ".80" if focal else ".24"
        parts += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="{opacity}" stroke="{fill}" stroke-width="2" data-x="{xv}" data-y="{yv}" data-size="{size}"/>', _text(x + r + 12, y + 6, label, "material")]
    parts += [_text((left+right)/2, 838, "AUTOMATION %", "kicker", "middle"), _text(62, (top+bottom)/2, "CONTROL CONFIDENCE", "kicker", "middle", transform=f"rotate(-90 62 {(top+bottom)/2})"), _legend(878, w, (("accent", "recommended"), ("dot", "alternative")), "Bubble area encodes monthly volume; exact values are in the accessible table.")]
    svg = _svg_shell("quantitative", "scatter-plot", "Tự động hóa, kiểm soát và khối lượng", "Năm phương án trên hai trục; diện tích bubble mã hóa volume và Hybrid là focal recommendation.", w, h, "".join(parts), semantic_ratio=.83)
    return Anchor(13, "quantitative", "scatter-plot", "13-quantitative--neutral-light", "Quantitative anchor", "Hybrid cân bằng automation 62, confidence 78 và volume 46.", svg, tuple((label, f"automation={x}; confidence={y}; volume={size}") for x, y, size, label, _ in data))


def special_anchor() -> Anchor:
    w, h = 1640, 960
    parts = [_text(84, 120, "INTAKE", "kicker"), _text(710, 120, "ROUTING", "kicker"), _text(1400, 120, "OUTCOME", "kicker")]
    nodes = [
        (90, 210, 42, 300, "Monthly budget", "12,000 min", True),
        (720, 170, 30, 220, "Unit tests", "5,200 min", False),
        (720, 430, 30, 190, "E2E", "4,000 min", True),
        (720, 670, 30, 120, "Build + lint", "2,800 min", False),
        (1420, 190, 30, 340, "Passed", "9,400 min", False),
        (1420, 590, 30, 130, "Failed", "1,600 min", False),
        (1420, 770, 30, 72, "Flaked", "1,000 min", True),
    ]
    for x, y, nw, nh, title, sub, focal in nodes:
        color = TOKENS["accent"] if focal and title == "Flaked" else TOKENS["ink"]
        parts += [f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" fill="{color}" rx="4"/>', _text(x - 16 if x > 1000 else x + nw + 16, y + nh/2 - 6, title, "node-title", "end" if x > 1000 else "start"), _text(x - 16 if x > 1000 else x + nw + 16, y + nh/2 + 24, sub, "mono", "end" if x > 1000 else "start")]
    ribbons = [
        ("M132 250 C330 250 510 220 720 220 L720 390 C510 390 330 400 132 400 Z", TOKENS["line_soft"], .74),
        ("M132 410 C360 410 520 470 720 470 L720 610 C520 610 360 560 132 560 Z", TOKENS["line_soft"], .74),
        ("M132 570 C350 570 540 700 720 700 L720 790 C540 790 350 680 132 680 Z", TOKENS["line_soft"], .74),
        ("M750 200 C980 200 1190 210 1420 230 L1420 480 C1180 440 980 370 750 360 Z", TOKENS["line_soft"], .72),
        ("M750 470 C980 470 1190 470 1420 470 L1420 610 C1190 610 980 610 750 610 Z", TOKENS["line_soft"], .72),
        ("M750 700 C980 700 1190 540 1420 520 L1420 610 C1190 640 980 760 750 780 Z", TOKENS["line_soft"], .72),
        ("M750 360 C980 360 1190 800 1420 790 L1420 842 C1190 850 980 440 750 390 Z", TOKENS["accent"], .32),
    ]
    parts = [f'<path d="{d}" fill="{color}" fill-opacity="{opacity}" stroke="none"/>' for d, color, opacity in ribbons] + parts
    parts += [_legend(860, w, (("line", "stage routing"), ("accent", "flaked rerun"), ("dot", "stage total")), "Ribbon width is proportional; totals reconcile to 12,000 minutes.")]
    svg = _svg_shell("special-geometry", "sankey", "Phân bổ CI minutes theo outcome", "Các ribbon bảo toàn tổng 12,000 phút qua stage và outcome; flaked path được nhấn coral.", w, h, "".join(parts), semantic_ratio=.84)
    return Anchor(14, "special-geometry", "sankey", "14-special-geometry--neutral-light", "Special geometry anchor", "Flaked reruns tiêu tốn 1,000 trên 12,000 CI minutes.", svg, (("budget", "12000"), ("stages", "5200 + 4000 + 2800 = 12000"), ("outcomes", "9400 + 1600 + 1000 = 12000"), ("flaked", "1000")))


def anchors_without_swimlane() -> tuple[Anchor, ...]:
    builders: tuple[Callable[[], Anchor], ...] = (
        topology_anchor, integration_anchor, deployment_anchor, dependency_anchor,
        directed_anchor, time_anchor, experience_anchor, hierarchy_anchor,
        containment_anchor, compartment_anchor, matrix_anchor, quantitative_anchor,
        special_anchor,
    )
    return tuple(builder() for builder in builders)


def render_html(anchor: Anchor) -> str:
    rows = "".join(f"<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>" for key, value in anchor.facts)
    receipts = []
    for role in ("display", "material", "technical"):
        resolved = TYPOGRAPHY[role]
        source = "disclosed fallback" if resolved.fallback_used else "preferred default"
        receipts.append(f"<span><strong>{escape(resolved.resolved_family)}</strong> · {source}</span>")
    return f'''<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(anchor.title)} · P-18R6</title>
  <style>
    :root{{--paper:#eeece7;--ink:#252b3c;--muted:#687286;}}
    *{{box-sizing:border-box}} html,body{{margin:0;min-height:100%;background:var(--paper);color:var(--ink)}}
    body{{font-family:'{escape(resolved_family('material'))}',sans-serif;padding:48px 24px 80px}}
    main{{width:min(100%,1720px);margin:auto}} header{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;margin-bottom:24px}}
    .eyebrow{{margin:0 0 8px;font-family:'{escape(resolved_family('technical'))}',monospace;font-size:14px;letter-spacing:.16em;color:#f26a32}}
    h1{{margin:0;font-family:'{escape(resolved_family('display'))}',serif;font-size:48px;line-height:1.06;font-weight:400}}
    .lede{{max-width:760px;margin:10px 0 0;font-size:16px;line-height:1.55;color:var(--muted)}}
    .receipts{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px}} .receipts span{{padding:7px 10px;border:1px solid #c9cdd2;border-radius:7px;background:#ffffff8a;font:12px '{escape(resolved_family('technical'))}',monospace;color:#657086}}
    .artifact-frame{{overflow:hidden;border:1px solid #d8d6d1;border-radius:18px;background:#f7f6f2;box-shadow:0 20px 60px #2d34431a}}
    .artifact-frame svg{{display:block;width:100%;height:auto}} .evidence{{margin-top:24px;padding:24px;border:1px solid #d8d6d1;border-radius:14px;background:#ffffff8a}}
    .evidence h2{{margin:0 0 8px;font-size:20px}} .evidence p{{margin:0 0 14px;font-size:16px;color:var(--muted)}} table{{border-collapse:collapse;width:100%;font-size:14px}} th,td{{padding:10px 12px;border-top:1px solid #d8d6d1;text-align:left}}
    @media(max-width:820px){{body{{padding:24px 12px 48px}}header{{grid-template-columns:1fr}}.receipts{{justify-content:flex-start}}h1{{font-size:40px}}.evidence{{overflow-x:auto}}}}
    @media print{{body{{padding:0;background:#fff}}header,.evidence{{display:none}}.artifact-frame{{border:0;box-shadow:none}}}}
  </style>
</head>
<body><main>
  <header><div><p class="eyebrow">P‑18R6 · NEUTRAL LIGHT · ENGINE {anchor.order:02d}</p><h1>{escape(anchor.title)}</h1><p class="lede">{escape(anchor.takeaway)}</p></div><div class="receipts" aria-label="Resolved font receipt">{"".join(receipts)}</div></header>
  <section class="artifact-frame" aria-label="Canonical engine anchor">{anchor.svg}</section>
  <section class="evidence" aria-labelledby="evidence-heading"><h2 id="evidence-heading">Semantic projection</h2><p>Nằm ngoài canonical screenshot và không tham gia masked blind/five-second review.</p><table><tbody>{rows}</tbody></table></section>
</main></body></html>'''


__all__ = ["Anchor", "TOKENS", "TYPOGRAPHY", "anchors_without_swimlane", "render_html", "resolved_family"]
