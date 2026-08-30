"""P-19B three-mode standalone HTML renderer for the v1.5 gallery.

This module consumes the validated P-19A adapter plan and emits one complete,
self-contained HTML document.  It has no network dependency, no script
runtime, and no generic/unknown fallback.  Every approved adapter id is bound
to an explicit visual recipe while the three modes share identical semantics
and geometry.
"""

from __future__ import annotations

from html import escape
import json
import math
from typing import Any, Callable, Mapping

from visual_adapters_v15 import CAPABILITY_ADAPTERS, TYPE_ADAPTERS, adapt_visual
from visual_system import contrast_report, load_visual_system


P19B_SCHEMA_VERSION = "1.0"
P19B_CANDIDATE_ID = "P19B-THREE-MODE-EXACT-129-HTML-1.5.0"
MODES = ("neutral-light", "neutral-dark", "editorial")
VIEWBOX = (0, 0, 1200, 760)


class GalleryRenderError(ValueError):
    """Fail-closed P-19B renderer error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _text(value: Any) -> str:
    return escape(str(value), quote=True)


def _labels(plan: Mapping[str, Any], collection: str, fallback: tuple[str, ...]) -> list[str]:
    values = [str(item.get("label") or item.get("id")) for item in plan["semantic_projection"].get(collection, [])]
    return values or list(fallback)


def _svg_text(x: float, y: float, value: str, css: str = "label", anchor: str = "middle") -> str:
    return f'<text class="{css}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{_text(value)}</text>'


def _card(x: float, y: float, w: float, h: float, label: str, *, css: str = "node", radius: int = 18) -> str:
    return (
        f'<g class="node-card"><rect class="{css}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}"/>'
        f'{_svg_text(x + w / 2, y + h / 2 + 6, label)}</g>'
    )


def _line(x1: float, y1: float, x2: float, y2: float, *, arrow: bool = False, css: str = "connector") -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<line class="{css}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{marker}/>'


def _poly(points: list[tuple[float, float]], *, css: str = "connector", close: bool = False) -> str:
    encoded = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    tag = "polygon" if close else "polyline"
    return f'<{tag} class="{css}" points="{encoded}"/>'


def _topology(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Input", "Core", "Output"))
    if kind == "architecture":
        return '<rect class="zone" x="170" y="155" width="860" height="390" rx="30"/>' + _svg_text(205, 192, "TRUST ZONE", "micro", "start") + _card(230, 280, 240, 110, labels[0]) + _line(470, 335, 700, 335, arrow=True) + _card(700, 280, 260, 110, labels[-1], css="node focal")
    if kind == "it-current-state":
        return _card(150, 220, 270, 130, labels[0], css="node warning") + _line(420, 285, 760, 285, arrow=True) + _card(760, 220, 290, 130, labels[-1], css="node focal") + '<circle class="status danger-fill" cx="380" cy="245" r="10"/><circle class="status success-fill" cx="1010" cy="245" r="10"/>' + _svg_text(285, 430, "LEGACY", "micro") + _svg_text(905, 430, "ACTIVE", "micro")
    return '<rect class="zone" x="105" y="170" width="990" height="360" rx="26"/>' + "".join(_card(160 + i * 330, 285, 220, 100, label, css="node focal" if i == 1 else "node") for i, label in enumerate((labels + ["Govern"] * 3)[:3])) + _line(380, 335, 490, 335, arrow=True) + _line(710, 335, 820, 335, arrow=True) + '<rect class="accent-band" x="160" y="455" width="880" height="26" rx="13"/>' + _svg_text(600, 475, "CROSS-CUTTING GOVERNANCE", "micro")


def _pipeline(plan: Mapping[str, Any]) -> str:
    labels = _labels(plan, "nodes", ("Source", "Transform", "Consumer"))
    kind = plan["adapter"]["canonical_type"]
    cards = []
    for index, label in enumerate((labels + ["Transform", "Consumer"])[:3]):
        x = 120 + index * 370
        css = "node focal" if (kind == "dp-integration" and index == 1) else "node"
        cards.append(_card(x, 275, 260, 120, label, css=css))
        if index < 2:
            cards.append(_line(x + 260, 335, x + 370, 335, arrow=True))
    boundary = '<rect class="zone dashed" x="470" y="190" width="260" height="290" rx="26"/>' if kind == "dp-integration" else ""
    return boundary + "".join(cards) + _svg_text(600, 520, "SOURCE → TRANSFORM → SINK", "micro")


def _deployment(plan: Mapping[str, Any]) -> str:
    labels = _labels(plan, "nodes", ("API", "Database"))
    return '<rect class="zone" x="105" y="150" width="440" height="420" rx="28"/>' + '<rect class="zone" x="655" y="150" width="440" height="420" rx="28"/>' + _svg_text(145, 190, "APPLICATION ZONE", "micro", "start") + _svg_text(695, 190, "DATA ZONE", "micro", "start") + _card(170, 270, 310, 140, labels[0], css="node focal") + _card(720, 270, 310, 140, labels[-1]) + _line(480, 340, 720, 340, arrow=True) + _svg_text(600, 320, "8443 → 5432", "micro")


def _dependency(plan: Mapping[str, Any]) -> str:
    labels = _labels(plan, "nodes", ("A", "B", "C"))
    a, b, c = (labels + ["B", "C"])[:3]
    return _card(130, 300, 220, 100, a) + _card(490, 175, 220, 100, b, css="node focal") + _card(850, 300, 220, 100, c) + _line(350, 350, 490, 225, arrow=True) + _line(710, 225, 850, 350, arrow=True) + '<path class="connector backedge" d="M960 400 C960 570 240 570 240 400" marker-end="url(#arrow)"/>' + _svg_text(600, 600, "EXPLICIT CYCLE BACK-EDGE", "micro")


def _directed(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Start", "Review", "Done"))
    if kind == "flowchart":
        return '<ellipse class="node" cx="220" cy="350" rx="120" ry="58"/>' + _svg_text(220, 356, labels[0]) + _line(340, 350, 500, 350, arrow=True) + '<polygon class="node focal" points="600,240 710,350 600,460 490,350"/>' + _svg_text(600, 356, labels[1]) + _line(710, 350, 875, 245, arrow=True) + _line(710, 350, 875, 455, arrow=True) + _card(875, 190, 230, 100, labels[2]) + _card(875, 405, 230, 100, labels[-1]) + _svg_text(780, 270, "YES", "micro") + _svg_text(780, 445, "NO", "micro")
    if kind == "state-machine":
        return '<circle class="ink-fill" cx="130" cy="350" r="18"/>' + _line(148, 350, 285, 350, arrow=True) + _card(285, 290, 250, 120, labels[0], radius=60) + _line(535, 350, 680, 350, arrow=True) + _card(680, 290, 250, 120, labels[1], css="node focal", radius=60) + _line(930, 350, 1040, 350, arrow=True) + '<circle class="terminal" cx="1080" cy="350" r="28"/><circle class="terminal" cx="1080" cy="350" r="19"/>'
    return _card(130, 285, 260, 130, labels[0]) + _line(390, 350, 560, 350, arrow=True) + '<path class="document" d="M560 275 H890 V405 Q808 365 725 405 Q642 445 560 405 Z"/>' + _svg_text(725, 340, labels[-1]) + _svg_text(600, 510, "ACTIVITY → ARTIFACT", "micro")


def _lane(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Sender", "Receiver"))
    if kind == "sequence":
        x1, x2 = 340, 860
        return _card(x1 - 110, 130, 220, 80, labels[0]) + _card(x2 - 110, 130, 220, 80, labels[-1]) + _line(x1, 210, x1, 590, css="lifeline") + _line(x2, 210, x2, 590, css="lifeline") + _line(x1, 310, x2, 310, arrow=True) + _line(x2, 450, x1, 450, arrow=True, css="connector dashed") + _svg_text(600, 290, "REQUEST", "micro") + _svg_text(600, 430, "RESPONSE", "micro")
    return '<rect class="lane" x="90" y="150" width="1020" height="190"/><rect class="lane alt" x="90" y="340" width="1020" height="190"/>' + _svg_text(125, 190, "REQUESTER", "micro", "start") + _svg_text(125, 380, "REVIEWER", "micro", "start") + _card(210, 220, 250, 90, labels[0]) + _card(740, 400, 250, 90, labels[-1], css="node focal") + '<path class="connector" d="M460 265 H620 Q650 265 650 295 V415 Q650 445 680 445 H740" marker-end="url(#arrow)"/>' + '<path class="bridge" d="M620 265 A30 30 0 0 1 650 295"/>'


def _time(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Discover", "Build"))
    if kind == "timeline":
        return _line(140, 370, 1060, 370, arrow=True, css="axis") + "".join(f'<circle class="point {"focal" if i == 1 else ""}" cx="{x}" cy="370" r="16"/>{_line(x, 370, x, 250 if i % 2 == 0 else 490, css="leader")}{_svg_text(x, 225 if i % 2 == 0 else 535, label)}' for i, (x, label) in enumerate(zip((280, 600, 920), (labels + ["Close"])[:3])))
    return _svg_text(125, 178, "TASK", "micro", "start") + _line(340, 190, 340, 560, css="gridline") + _line(560, 190, 560, 560, css="gridline") + _line(780, 190, 780, 560, css="gridline") + _svg_text(360, 178, "15 AUG", "micro") + _svg_text(580, 178, "17 AUG", "micro") + _svg_text(800, 178, "20 AUG", "micro") + _svg_text(120, 285, labels[0], "label", "start") + _svg_text(120, 430, labels[-1], "label", "start") + '<rect class="bar" x="340" y="240" width="220" height="64"/><rect class="bar focal" x="560" y="385" width="360" height="64"/>' + '<path class="connector" d="M560 272 H600 V385" marker-end="url(#arrow)"/>'


def _work(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Discover", "Submit"))
    if kind == "kanban":
        return "".join(f'<g><rect class="column" x="{100+i*350}" y="160" width="300" height="420" rx="20"/>{_svg_text(125+i*350, 205, title, "micro", "start")}{_card(135+i*350, 250, 230, 115, (labels+["Done"])[i], css="node warning" if i==1 else "node")}</g>' for i, title in enumerate(("READY · 1/2", "REVIEW · 1/1", "DONE · 1")))
    if kind == "user-journey":
        items = []
        for i, label in enumerate((labels + ["Complete"])[:3]):
            x = 125 + i * 350
            items.append(_card(x, 190, 250, 105, label, css="node focal" if i == 1 else "node"))
            items.append(_line(x + 125, 315, x + 125, 520, css="sentiment"))
            items.append(f'<circle class="point" cx="{x+125}" cy="{430 + (i-1)*45}" r="16"/>')
        return _line(130, 430, 1070, 430, css="axis") + "".join(items) + _svg_text(90, 345, "+", "micro") + _svg_text(90, 540, "−", "micro")
    return '<line class="cutline" x1="90" y1="410" x2="1110" y2="410"/>' + _svg_text(105, 398, "RELEASE CUT", "micro", "start") + "".join(_card(130 + i * 340, 180, 260, 110, label, css="node focal" if i == 0 else "node") + _card(130 + i * 340, 460, 260, 90, f"Slice {i+1}") for i, label in enumerate((labels + ["Export"])[:3]))


def _hierarchy(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Root", "Branch", "Leaf"))
    root, branch, leaf = (labels + ["Branch", "Leaf"])[:3]
    root_label = root if kind == "tree" else labels[-1]
    return _card(475, 130, 250, 100, root_label, css="node focal") + _line(600, 230, 600, 330) + _line(300, 330, 900, 330) + _line(300, 330, 300, 420, arrow=True) + _line(900, 330, 900, 420, arrow=True) + _card(170, 420, 260, 100, branch) + _card(770, 420, 260, 100, leaf) + _svg_text(600, 600, "PRIMARY HIERARCHY", "micro")


def _containment(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Core", "Service"))
    if kind == "nested":
        return '<rect class="zone" x="130" y="130" width="940" height="500" rx="34"/>' + _svg_text(175, 180, "PLATFORM", "micro", "start") + '<rect class="zone alt" x="280" y="235" width="640" height="300" rx="28"/>' + _svg_text(320, 280, "DOMAIN", "micro", "start") + _card(445, 335, 310, 110, labels[0], css="node focal")
    if kind in {"layer-stack", "medallion"}:
        names = (labels + ["Curated", "Serving"])[:3] if kind == "medallion" else ("EDGE", "SERVICE", "DATA")
        return "".join(f'<rect class="tier {"focal" if i==1 else ""}" x="{170+i*45}" y="{180+i*135}" width="{860-i*90}" height="105" rx="18"/>{_svg_text(600, 245+i*135, label)}' for i, label in enumerate(names))
    values = (100, 64, 35)
    names = ("AWARE", "CONSIDER", "ACT")
    points = [(180, 170), (1020, 170), (850, 590), (350, 590)]
    return _poly(points, css="funnel", close=True) + _line(250, 310, 950, 310, css="tierline") + _line(300, 450, 900, 450, css="tierline") + "".join(_svg_text(600, 250 + i * 140, f"{names[i]} · {values[i]}") for i in range(3))


def _compartment(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Customer", "Order"))
    member_labels = {"er-data-model": ("id · PK", "name · text"), "uml-class": ("− id: UUID", "+ submit(): void"), "database-schema": ("id · uuid · PK", "customer_id · uuid · FK")}[kind]
    left = _card(120, 190, 350, 330, labels[0], css="node compartment", radius=10)
    right = _card(730, 190, 350, 330, labels[-1], css="node compartment", radius=10)
    dividers = _line(120, 275, 470, 275, css="divider") + _line(730, 275, 1080, 275, css="divider")
    members = _svg_text(150, 335, member_labels[0], "body", "start") + _svg_text(150, 385, member_labels[1], "body", "start") + _svg_text(760, 335, member_labels[0], "body", "start") + _svg_text(760, 385, member_labels[1], "body", "start")
    relation = _line(470, 355, 730, 355) + _svg_text(600, 335, "1  ·  N", "micro")
    return left + right + dividers + members + relation + _svg_text(600, 590, kind.replace("-", " ").upper(), "micro")


def _spatial(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "venn":
        return '<circle class="set series-one" cx="475" cy="365" r="215"/><circle class="set series-two" cx="725" cy="365" r="215"/>' + _svg_text(350, 370, "SET A") + _svg_text(850, 370, "SET B") + _svg_text(600, 370, "SHARED", "label focal-text")
    if kind == "dp-security-matrix":
        cells = []
        states = ("allow", "conditional", "allow", "deny")
        for i, state in enumerate(states):
            x = 400 + (i % 2) * 260; y = 240 + (i // 2) * 150
            cells.append(f'<rect class="matrix-cell {state}" x="{x}" y="{y}" width="240" height="130" rx="12"/>{_svg_text(x+120,y+72,state.upper(),"micro")}' )
        return _svg_text(250, 310, "READER", "micro") + _svg_text(250, 460, "ADMIN", "micro") + _svg_text(520, 195, "STORE", "micro") + _svg_text(780, 195, "API", "micro") + "".join(cells)
    axis = _line(170, 570, 1060, 570, arrow=True, css="axis") + _line(170, 570, 170, 135, arrow=True, css="axis")
    if kind == "quadrant":
        return axis + _line(615, 135, 615, 570, css="gridline") + _line(170, 350, 1060, 350, css="gridline") + '<circle class="point focal" cx="850" cy="230" r="18"/><circle class="point" cx="370" cy="460" r="18"/>' + _svg_text(1030, 610, "IMPACT", "micro") + _svg_text(130, 150, "LIKELIHOOD", "micro", "end")
    return axis + _line(170, 245, 1060, 245, css="gridline") + _line(170, 405, 1060, 405, css="gridline") + '<circle class="point focal" cx="360" cy="215" r="22"/><circle class="point" cx="750" cy="390" r="22"/>' + _line(360, 215, 750, 390) + _svg_text(350, 175, "NEED", "micro") + _svg_text(760, 435, "SERVICE", "micro") + _svg_text(1040, 610, "EVOLUTION", "micro")


def _quantitative(plan: Mapping[str, Any]) -> str:
    adapter_id = plan["adapter"]["adapter_id"]
    kind = plan["adapter"]["canonical_type"]
    axis = _line(150, 590, 1060, 590, arrow=True, css="axis") + _line(150, 590, 150, 140, arrow=True, css="axis")
    if adapter_id == "capability:CAP-V17":
        return axis + _line(300, 300, 790, 300, css="series-line") + _line(420, 460, 900, 460, css="series-line") + '<circle class="point series-one-fill" cx="300" cy="300" r="18"/><circle class="point series-two-fill" cx="790" cy="300" r="18"/><circle class="point series-one-fill" cx="420" cy="460" r="18"/><circle class="point series-two-fill" cx="900" cy="460" r="18"/>' + _svg_text(260, 306, "A", "micro", "end") + _svg_text(380, 466, "B", "micro", "end")
    if adapter_id == "capability:CAP-V18":
        return axis + _line(330, 455, 870, 235, css="series-line") + _line(330, 260, 870, 390, css="series-line second") + _svg_text(330, 630, "BEFORE", "micro") + _svg_text(870, 630, "AFTER", "micro") + _svg_text(300, 455, "Alpha 2", "micro", "end") + _svg_text(900, 235, "8 Alpha", "micro", "start") + _svg_text(300, 260, "Beta 7", "micro", "end") + _svg_text(900, 390, "4 Beta", "micro", "start")
    if adapter_id == "capability:CAP-V19":
        ridges=[]
        for i, y in enumerate((300, 470)):
            pts=[(220+x*95, y-math.sin(x/5*math.pi)*95) for x in range(6)]
            ridges.append(_poly(pts, css="ridge")+_svg_text(190,y+5,("NORTH","SOUTH")[i],"micro","end"))
        return axis+"".join(ridges)
    if adapter_id == "capability:CAP-V20":
        return axis + '<circle class="bubble series-one" cx="420" cy="350" r="10"/><circle class="bubble series-two" cx="810" cy="420" r="74"/>' + _svg_text(420, 320, "0", "micro") + _svg_text(810, 425, "25", "label") + _svg_text(1045, 630, "X", "micro") + _svg_text(120, 155, "Y", "micro")
    if kind == "bar-chart":
        return axis + '<rect class="bar" x="300" y="360" width="180" height="230"/><rect class="bar focal" x="650" y="245" width="180" height="345"/>' + _svg_text(390, 630, "JAN · 12", "micro") + _svg_text(740, 630, "FEB · 18", "micro")
    if kind == "line-chart":
        return axis + _poly([(230,470),(470,395),(710,300),(950,220)],css="series-line") + ''.join(f'<circle class="point focal" cx="{x}" cy="{y}" r="12"/>' for x,y in [(230,470),(470,395),(710,300),(950,220)])
    if kind == "scatter-plot":
        return axis + ''.join(f'<circle class="point {"focal" if i==2 else ""}" cx="{x}" cy="{y}" r="16"/>' for i,(x,y) in enumerate([(300,450),(520,300),(790,210),(900,430)])) + _svg_text(810, 190, "OUTLIER", "micro")
    if kind == "radar":
        center=(600,370); radii=(85,170,255); parts=[]
        for r in radii:
            parts.append(_poly([(center[0]+math.cos(-math.pi/2+i*2*math.pi/5)*r,center[1]+math.sin(-math.pi/2+i*2*math.pi/5)*r) for i in range(5)],css="gridshape",close=True))
        values=(.8,.55,.9,.68,.45)
        parts.append(_poly([(center[0]+math.cos(-math.pi/2+i*2*math.pi/5)*255*values[i],center[1]+math.sin(-math.pi/2+i*2*math.pi/5)*255*values[i]) for i in range(5)],css="radarshape",close=True))
        return ''.join(parts)
    if kind == "polar-chart":
        center=(600,380); parts=[]
        for i,r in enumerate((210,130,55,175)):
            a1=-90+i*90; a2=a1+72
            x1=center[0]+math.cos(math.radians(a1))*r; y1=center[1]+math.sin(math.radians(a1))*r
            x2=center[0]+math.cos(math.radians(a2))*r; y2=center[1]+math.sin(math.radians(a2))*r
            parts.append(f'<path class="polar {"focal" if i==0 else ""}" d="M600 380 L{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f} Z"/>')
        return ''.join(parts)
    # treemap is the only remaining canonical quantitative recipe.
    return '<rect class="zone" x="120" y="150" width="960" height="450" rx="18"/><rect class="tile focal" x="140" y="180" width="560" height="390"/><rect class="tile" x="720" y="180" width="340" height="185"/><rect class="tile alt" x="720" y="385" width="340" height="185"/>' + _svg_text(420, 390, "A · 60") + _svg_text(890, 280, "B · 25") + _svg_text(890, 485, "C · 15")


def _special(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Learn", "Build", "Measure"))
    if kind == "loop-flywheel":
        centers=((600,175),(850,470),(350,470)); parts=[]
        for i,(x,y) in enumerate(centers): parts.append(_card(x-105,y-50,210,100,(labels+["Measure"])[i],css="node focal" if i==0 else "node",radius=50))
        parts.extend((_line(680,230,800,410,arrow=True),_line(760,505,440,505,arrow=True),_line(400,410,520,230,arrow=True)))
        return ''.join(parts)
    if kind == "fishbone":
        return _line(190, 380, 980, 380, arrow=True, css="spine") + _line(320, 380, 430, 235, css="bone") + _line(500, 380, 610, 525, css="bone") + _line(680, 380, 790, 235, css="bone") + _card(900, 315, 240, 130, labels[-1], css="node focal") + _svg_text(420, 210, labels[0], "body") + _svg_text(610, 565, labels[1], "body") + _svg_text(790, 210, "Technology", "body")
    # Sankey: bar heights and ribbon widths share one disclosed linear scale.
    return '<rect class="flowbar" x="120" y="245" width="48" height="250"/><rect class="flowbar focal" x="575" y="245" width="48" height="250"/><rect class="flowbar" x="1030" y="245" width="48" height="250"/>' + '<path class="ribbon series-one" d="M168 245 C330 245 413 245 575 245 L575 495 C413 495 330 495 168 495 Z"/><path class="ribbon series-two" d="M623 245 C785 245 868 245 1030 245 L1030 495 C868 495 785 495 623 495 Z"/>' + _svg_text(144, 220, labels[0]) + _svg_text(599, 220, labels[1]) + _svg_text(1054, 220, labels[-1]) + _svg_text(372, 380, "25", "label") + _svg_text(826, 380, "25", "label")


ENGINE_RENDERERS: dict[str, Callable[[Mapping[str, Any]], str]] = {
    "topology-and-zones": _topology,
    "integration-pipeline": _pipeline,
    "runtime-deployment": _deployment,
    "dependency-dag": _dependency,
    "directed-flow-state": _directed,
    "lane-interaction": _lane,
    "time-planning": _time,
    "work-experience": _work,
    "hierarchy": _hierarchy,
    "containment-stack": _containment,
    "compartment-model": _compartment,
    "spatial-matrix": _spatial,
    "quantitative": _quantitative,
    "special-geometry": _special,
}


def _data_rows(plan: Mapping[str, Any]) -> str:
    inventory = plan["material_inventory"]["by_collection"]
    rows = []
    for collection in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations"):
        ids = inventory.get(collection, [])
        if ids:
            rows.append(f"<tr><th scope=\"row\">{_text(collection)}</th><td>{_text(', '.join(ids))}</td><td>{len(ids)}</td></tr>")
    if not rows:
        rows.append('<tr><th scope="row">material</th><td>Validated semantic projection</td><td>1</td></tr>')
    return "".join(rows)


def _css(tokens: Mapping[str, str], mode: str) -> str:
    editorial = "Georgia, 'Times New Roman', serif" if mode == "editorial" else "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    return f"""
    :root{{--canvas:{tokens['canvas']};--surface:{tokens['surface']};--surface-alt:{tokens['surface_alt']};--text:{tokens['text']};--muted:{tokens['muted']};--border:{tokens['border']};--accent:{tokens['accent']};--on-accent:{tokens['on_accent']};--connector:{tokens['connector']};--series-1:{tokens['series_1']};--series-2:{tokens['series_2']};--grid:{tokens['grid']};--success:{tokens['success']};--danger:{tokens['danger']}}}
    *{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:var(--canvas);color:var(--text)}}body{{font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;padding:24px}}main{{width:min(100%,1320px);margin:auto}}header{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;margin:4px 0 22px}}.eyebrow{{margin:0 0 8px;font:700 13px ui-monospace,monospace;letter-spacing:.14em;color:var(--accent)}}h1{{margin:0;font-family:{editorial};font-size:clamp(30px,5vw,54px);line-height:1.03;font-weight:{'500' if mode=='editorial' else '750'}}}.takeaway{{max-width:760px;margin:10px 0 0;color:var(--muted);font-size:16px;line-height:1.55}}.badge{{align-self:start;border:1px solid var(--border);border-radius:999px;padding:9px 13px;font:700 12px ui-monospace,monospace;color:var(--muted)}}.artifact-frame{{border:1px solid var(--border);border-radius:{'2px' if mode=='editorial' else '22px'};background:var(--surface);overflow:hidden;box-shadow:0 18px 55px color-mix(in srgb,var(--text) 10%,transparent)}}svg{{display:block;width:100%;height:auto;background:var(--surface)}}.label{{font:650 18px ui-sans-serif,system-ui,sans-serif;fill:var(--text)}}.label.focal-text{{fill:var(--accent)}}.body{{font:500 16px ui-sans-serif,system-ui,sans-serif;fill:var(--text)}}.micro{{font:750 12px ui-monospace,monospace;letter-spacing:.08em;fill:var(--muted)}}.node,.zone,.lane,.column,.tier,.tile,.matrix-cell{{fill:var(--surface);stroke:var(--border);stroke-width:2}}.zone{{fill:var(--surface-alt)}}.zone.alt,.lane.alt,.tile.alt{{fill:var(--canvas)}}.zone.dashed{{stroke-dasharray:8 7}}.node.focal,.tier.focal,.tile.focal{{fill:color-mix(in srgb,var(--accent) 14%,var(--surface));stroke:var(--accent);stroke-width:3}}.node.warning{{fill:color-mix(in srgb,var(--danger) 11%,var(--surface));stroke:var(--danger)}}.connector,.axis,.leader,.lifeline,.divider,.gridline,.tierline,.bone,.spine{{fill:none;stroke:var(--connector);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}.axis{{stroke-width:2}}.gridline,.divider,.tierline{{stroke:var(--grid);stroke-width:2}}.leader,.lifeline{{stroke-dasharray:7 7}}.bridge{{fill:none;stroke:var(--surface);stroke-width:8}}.backedge{{stroke-dasharray:10 8}}.status,.point,.terminal,.bubble{{fill:var(--surface);stroke:var(--connector);stroke-width:3}}.point.focal{{fill:var(--accent);stroke:var(--on-accent)}}.success-fill{{fill:var(--success);stroke:none}}.danger-fill{{fill:var(--danger);stroke:none}}.ink-fill{{fill:var(--text)}}.terminal{{fill:none}}.accent-band{{fill:color-mix(in srgb,var(--accent) 18%,var(--surface))}}.bar,.flowbar{{fill:var(--series-1)}}.bar.focal,.flowbar.focal{{fill:var(--series-2)}}.cutline{{stroke:var(--danger);stroke-width:3;stroke-dasharray:12 8}}.sentiment{{stroke:var(--grid);stroke-width:8}}.compartment{{fill:var(--surface)}}.set{{fill:color-mix(in srgb,var(--series-1) 26%,transparent);stroke:var(--series-1);stroke-width:3}}.set.series-two{{fill:color-mix(in srgb,var(--series-2) 26%,transparent);stroke:var(--series-2)}}.allow{{fill:color-mix(in srgb,var(--success) 22%,var(--surface));stroke:var(--success)}}.conditional{{fill:color-mix(in srgb,var(--accent) 20%,var(--surface));stroke:var(--accent)}}.deny{{fill:color-mix(in srgb,var(--danger) 18%,var(--surface));stroke:var(--danger)}}.series-line,.ridge,.gridshape,.radarshape{{fill:none;stroke:var(--series-1);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.series-line.second{{stroke:var(--series-2)}}.series-one-fill{{fill:var(--series-1)}}.series-two-fill{{fill:var(--series-2)}}.ridge{{stroke-width:7}}.gridshape{{stroke:var(--grid);stroke-width:2}}.radarshape{{fill:color-mix(in srgb,var(--series-1) 20%,transparent)}}.polar{{fill:color-mix(in srgb,var(--series-1) 25%,var(--surface));stroke:var(--series-1);stroke-width:3}}.polar.focal{{fill:color-mix(in srgb,var(--series-2) 42%,var(--surface));stroke:var(--series-2)}}.bubble.series-one{{fill:var(--series-1)}}.bubble.series-two{{fill:color-mix(in srgb,var(--series-2) 52%,var(--surface));stroke:var(--series-2)}}.funnel{{fill:color-mix(in srgb,var(--accent) 13%,var(--surface));stroke:var(--accent);stroke-width:3}}.ribbon{{stroke:none;opacity:.58}}.ribbon.series-one{{fill:var(--series-1)}}.ribbon.series-two{{fill:var(--series-2)}}.document{{fill:var(--surface-alt);stroke:var(--accent);stroke-width:3}}.facts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;margin-top:14px;border:1px solid var(--border);background:var(--border)}}.fact{{padding:14px;background:var(--surface)}}.fact span{{display:block;color:var(--muted);font:700 11px ui-monospace,monospace;letter-spacing:.08em}}.fact strong{{display:block;margin-top:5px;font-size:14px;overflow-wrap:anywhere}}details{{margin-top:14px;border:1px solid var(--border);border-radius:14px;background:var(--surface)}}summary{{cursor:pointer;padding:14px 16px;font-weight:750}}summary:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:10px 16px;border-top:1px solid var(--border);text-align:left;vertical-align:top}}th{{width:18%;color:var(--muted)}}td:last-child{{width:8%;font-variant-numeric:tabular-nums}}@media(max-width:720px){{body{{padding:12px}}header{{grid-template-columns:1fr}}.facts{{grid-template-columns:1fr}}.artifact-frame{{overflow:auto}}svg{{min-width:760px}}}}@media print{{body{{padding:0}}.artifact-frame{{box-shadow:none}}details{{display:block}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;animation:none!important;transition:none!important}}}}
    """


def render_gallery_html(ir_value: Mapping[str, Any], mode: str, fixture_id: str) -> str:
    """Render one deterministic self-contained P-19B specimen HTML."""

    if mode not in MODES:
        raise GalleryRenderError("mode-invalid", f"Unsupported mode: {mode!r}")
    if not fixture_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in fixture_id):
        raise GalleryRenderError("fixture-id-invalid", "Fixture id must be a safe non-empty token.")
    plan = adapt_visual(ir_value)
    adapter = plan["adapter"]
    engine = adapter["layout_engine"]
    if engine not in ENGINE_RENDERERS:
        raise GalleryRenderError("engine-unbound", f"No renderer is bound for {engine!r}")
    tokens = load_visual_system()["modes"][mode]
    failures = [item for item in contrast_report(load_visual_system()) if item["mode"] == mode and item["status"] != "pass"]
    if failures:
        raise GalleryRenderError("mode-contrast-failure", f"Visual token mode {mode!r} failed the inherited contrast contract.")
    identity = adapter["capability_id"] or adapter["canonical_type"]
    parent = adapter["canonical_type"] if adapter["capability_id"] else "none"
    title = str(ir_value["diagram"]["title"])
    description = str(plan["accessibility_contract"]["description"])
    svg_id = f"diagram-{fixture_id}-{mode}"
    artwork = ENGINE_RENDERERS[engine](plan)
    svg = f'''<svg id="{svg_id}" role="img" aria-labelledby="{svg_id}-title {svg_id}-desc" viewBox="0 0 1200 760" data-layout-engine="{_text(engine)}" data-silhouette="{_text(adapter['silhouette'])}" data-geometry-contract="content-fit-no-global-transform"><title id="{svg_id}-title">{_text(title)}</title><desc id="{svg_id}-desc">{_text(description)} {_text(adapter['semantic_focus'])}.</desc><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="context-stroke"/></marker></defs><rect width="1200" height="760" fill="var(--surface)"/>{artwork}</svg>'''
    metadata = {
        "candidate_id": P19B_CANDIDATE_ID,
        "schema_version": P19B_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "identity": identity,
        "canonical_type": adapter["canonical_type"],
        "capability_id": adapter["capability_id"],
        "parent": parent,
        "mode": mode,
        "layout_engine": engine,
        "silhouette": adapter["silhouette"],
        "source_ir_sha256": plan["source_ir_sha256"],
        "automated_check_disposition": "p19b-static-and-browser-planned",
    }
    return f'''<!doctype html><html lang="vi" data-candidate-id="{P19B_CANDIDATE_ID}" data-fixture-id="{_text(fixture_id)}" data-diagram-type="{_text(adapter['canonical_type'])}" data-capability-id="{_text(adapter['capability_id'] or 'none')}" data-parent-type="{_text(parent)}" data-mode="{_text(mode)}" data-layout-engine="{_text(engine)}" data-silhouette="{_text(adapter['silhouette'])}" data-check-disposition="p19b-static-and-browser-planned"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="{'dark' if mode == 'neutral-dark' else 'light'}"><title>{_text(identity)} · {_text(mode)} · P-19B</title><style>{_css(tokens, mode)}</style></head><body><main><header><div><p class="eyebrow">P‑19B · {_text(engine.upper())}</p><h1>{_text(title)}</h1><p class="takeaway">{_text(adapter['semantic_focus'].capitalize())}. {_text(adapter['accessible_alternative'].capitalize())}.</p></div><span class="badge">{_text(identity)} · {_text(mode)}</span></header><figure class="artifact-frame">{svg}</figure><section class="facts" aria-label="Thông tin specimen"><div class="fact"><span>TYPE / CAPABILITY</span><strong>{_text(identity)}</strong></div><div class="fact"><span>LAYOUT ENGINE</span><strong>{_text(engine)}</strong></div><div class="fact"><span>SILHOUETTE</span><strong>{_text(adapter['silhouette'])}</strong></div></section><details><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Collection</th><th scope="col">Semantic IDs</th><th scope="col">Count</th></tr></thead><tbody>{_data_rows(plan)}</tbody></table></details><pre hidden id="p19b-metadata">{escape(json.dumps(metadata, ensure_ascii=False, sort_keys=True), quote=False)}</pre></main></body></html>'''


def renderer_inventory() -> dict[str, Any]:
    """Return the explicit adapter-to-recipe binding used by P-19B."""

    adapters = list(TYPE_ADAPTERS.values()) + list(CAPABILITY_ADAPTERS.values())
    return {
        "schema_version": P19B_SCHEMA_VERSION,
        "candidate_id": P19B_CANDIDATE_ID,
        "modes": list(MODES),
        "viewbox": list(VIEWBOX),
        "adapter_count": len(adapters),
        "engine_renderer_count": len(ENGINE_RENDERERS),
        "bindings": [
            {
                "adapter_id": item.adapter_id,
                "layout_engine": item.layout_engine,
                "silhouette": item.silhouette,
                "renderer": ENGINE_RENDERERS[item.layout_engine].__name__,
            }
            for item in adapters
        ],
        "boundary": {
            "standalone_html": True,
            "external_resources": False,
            "package_asset": False,
            "p19c_full_qa_freeze_owner_review": False,
        },
    }


__all__ = [
    "GalleryRenderError",
    "MODES",
    "P19B_CANDIDATE_ID",
    "P19B_SCHEMA_VERSION",
    "render_gallery_html",
    "renderer_inventory",
]
