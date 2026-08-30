"""P-18R5 master visual kernel for independently authored QA anchors.

The module implements the P-18R4 pipeline without carrying the rejected P-18R3
visual foundation.  It is evidence-only source: no runtime, package, dist, or
release payload imports this file in P-18R5.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from PIL import ImageFont


class FontResolutionError(RuntimeError):
    """Raised when an explicit font request cannot be honored safely."""


@dataclass(frozen=True)
class FontFace:
    family: str
    path: Path
    index: int
    weight: int
    style: str = "normal"


@dataclass(frozen=True)
class FontRole:
    name: str
    preferred_family: str
    fallback_families: tuple[str, ...]
    size_px: int
    weight: int
    line_height_px: int
    tracking_px: float = 0.0


@dataclass(frozen=True)
class TypographyRequest:
    explicit_user_fonts: Mapping[str, str] = field(default_factory=dict)
    explicit_user_fallbacks: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedFont:
    role: FontRole
    requested_family: str
    resolved_face: FontFace
    precedence_source: str
    fallback_used: bool
    fallback_reason: str | None

    @property
    def resolved_family(self) -> str:
        return self.resolved_face.family


@dataclass(frozen=True)
class TextMetrics:
    width: float
    height: float
    ascent: int
    descent: int


@dataclass(frozen=True)
class WrappedText:
    lines: tuple[str, ...]
    width: float
    height: float
    line_height: int


class FontResolver:
    """Resolve role fonts by explicit precedence and disclose every fallback."""

    def __init__(self, catalog: Mapping[str, Sequence[FontFace]]) -> None:
        self.catalog = {family: tuple(faces) for family, faces in catalog.items()}

    def _face(self, family: str, weight: int) -> FontFace | None:
        faces = self.catalog.get(family, ())
        if not faces:
            return None
        return min(faces, key=lambda face: abs(face.weight - weight))

    def resolve(self, role: FontRole, request: TypographyRequest) -> ResolvedFont:
        explicit = request.explicit_user_fonts.get(role.name)
        if explicit:
            candidates = (explicit,) + tuple(request.explicit_user_fallbacks.get(role.name, ()))
            for candidate_index, family in enumerate(candidates):
                face = self._face(family, role.weight)
                if face:
                    return ResolvedFont(
                        role=role,
                        requested_family=explicit,
                        resolved_face=face,
                        precedence_source="explicit_user_font",
                        fallback_used=candidate_index > 0,
                        fallback_reason=(f"user-approved fallback for unavailable {explicit}" if candidate_index > 0 else None),
                    )
            raise FontResolutionError(
                f"Explicit user font '{explicit}' for role '{role.name}' is unavailable; "
                "no user-approved fallback resolved."
            )

        preferred = self._face(role.preferred_family, role.weight)
        if preferred:
            return ResolvedFont(
                role=role,
                requested_family=role.preferred_family,
                resolved_face=preferred,
                precedence_source="skill_default_profile",
                fallback_used=False,
                fallback_reason=None,
            )
        for family in role.fallback_families:
            face = self._face(family, role.weight)
            if face:
                return ResolvedFont(
                    role=role,
                    requested_family=role.preferred_family,
                    resolved_face=face,
                    precedence_source="disclosed_system_fallback",
                    fallback_used=True,
                    fallback_reason=f"preferred default {role.preferred_family} is not installed",
                )
        raise FontResolutionError(
            f"Neither preferred default '{role.preferred_family}' nor a disclosed system fallback "
            f"is available for role '{role.name}'."
        )


class FontMetricEngine:
    """Measure and wrap with the resolved local font face, never character count."""

    def __init__(self, resolved: Mapping[str, ResolvedFont]) -> None:
        self.resolved = dict(resolved)
        self._fonts: dict[str, ImageFont.FreeTypeFont] = {}
        for role_name, item in self.resolved.items():
            self._fonts[role_name] = ImageFont.truetype(
                str(item.resolved_face.path),
                item.role.size_px,
                index=item.resolved_face.index,
            )

    def font(self, role_name: str) -> ImageFont.FreeTypeFont:
        return self._fonts[role_name]

    def validate_glyphs(self, role_name: str, text: str) -> tuple[str, ...]:
        font = self.font(role_name)
        missing: list[str] = []
        for character in sorted(set(text)):
            if character.isspace() or character in {"\u200b", "\ufeff"}:
                continue
            mask = font.getmask(character)
            if mask.getbbox() is None:
                missing.append(character)
        return tuple(missing)

    def measure(self, role_name: str, text: str) -> TextMetrics:
        resolved = self.resolved[role_name]
        font = self.font(role_name)
        left, top, right, bottom = font.getbbox(text or " ")
        tracking = max(0, len(text) - 1) * resolved.role.tracking_px
        ascent, descent = font.getmetrics()
        return TextMetrics(
            width=max(0.0, float(right - left) + tracking),
            height=max(float(bottom - top), float(resolved.role.line_height_px)),
            ascent=ascent,
            descent=descent,
        )

    def wrap(self, role_name: str, text: str, max_width: float) -> WrappedText:
        role = self.resolved[role_name].role
        words = text.split()
        if not words:
            return WrappedText(("",), 0.0, float(role.line_height_px), role.line_height_px)
        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if self.measure(role_name, candidate).width <= max_width:
                current = candidate
                continue
            lines.append(current)
            current = word
        lines.append(current)

        split_lines: list[str] = []
        for line in lines:
            if self.measure(role_name, line).width <= max_width:
                split_lines.append(line)
                continue
            fragment = ""
            for character in line:
                candidate = fragment + character
                if fragment and self.measure(role_name, candidate).width > max_width:
                    split_lines.append(fragment)
                    fragment = character
                else:
                    fragment = candidate
            if fragment:
                split_lines.append(fragment)
        width = max(self.measure(role_name, line).width for line in split_lines)
        return WrappedText(
            lines=tuple(split_lines),
            width=width,
            height=float(len(split_lines) * role.line_height_px),
            line_height=role.line_height_px,
        )

    def wrap_balanced(self, role_name: str, text: str, max_width: float) -> WrappedText:
        """Prefer a single line, then a balanced two-line break without an orphan."""

        role = self.resolved[role_name].role
        full = self.measure(role_name, text)
        if full.width <= max_width:
            return WrappedText((text,), full.width, float(role.line_height_px), role.line_height_px)

        words = text.split()
        candidates: list[tuple[float, tuple[str, str]]] = []
        for split_at in range(1, len(words)):
            first = " ".join(words[:split_at])
            second = " ".join(words[split_at:])
            first_width = self.measure(role_name, first).width
            second_width = self.measure(role_name, second).width
            if max(first_width, second_width) > max_width:
                continue
            orphan_penalty = 0.0
            if len(words[split_at:]) == 1 and len(second) < max(7, int(len(text) * 0.34)):
                orphan_penalty = max_width * 4
            raggedness = abs(first_width - second_width)
            candidates.append((orphan_penalty + raggedness, (first, second)))
        if candidates:
            lines = min(candidates, key=lambda item: item[0])[1]
            width = max(self.measure(role_name, line).width for line in lines)
            return WrappedText(
                lines=lines,
                width=width,
                height=float(len(lines) * role.line_height_px),
                line_height=role.line_height_px,
            )
        return self.wrap(role_name, text, max_width)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def cx(self) -> float:
        return self.x + self.width / 2

    @property
    def cy(self) -> float:
        return self.y + self.height / 2

    def inflated(self, amount: float) -> "Box":
        return Box(self.x - amount, self.y - amount, self.width + amount * 2, self.height + amount * 2)

    def contains(self, point: Point, tolerance: float = 0.0) -> bool:
        return (
            self.left - tolerance <= point.x <= self.right + tolerance
            and self.top - tolerance <= point.y <= self.bottom + tolerance
        )

    def intersects(self, other: "Box", clearance: float = 0.0) -> bool:
        return not (
            self.right + clearance <= other.left
            or other.right + clearance <= self.left
            or self.bottom + clearance <= other.top
            or other.bottom + clearance <= self.top
        )


@dataclass(frozen=True)
class DataTag:
    code: str
    label: str
    kind: str


@dataclass(frozen=True)
class NodeContent:
    node_id: str
    lane_id: str
    stage: int
    role_badge: str
    title: str
    transition: str
    system_line: str
    tags: tuple[DataTag, ...]
    semantic_node_ids: tuple[str, ...]
    focal: bool = False


@dataclass(frozen=True)
class NodeGeometry:
    content: NodeContent
    box: Box
    title_lines: tuple[str, ...]
    tag_widths: tuple[float, ...]


class IntrinsicNodeSizer:
    MIN_WIDTH = 292.0
    HARD_MAX_WIDTH = 440.0
    PADDING_X = 20.0

    def __init__(self, metrics: FontMetricEngine) -> None:
        self.metrics = metrics

    def ideal_width(self, content: NodeContent) -> tuple[float, tuple[float, ...]]:
        padding_x = self.PADDING_X
        badge_width = self.metrics.measure("badge", content.role_badge).width + 20
        title_width = self.metrics.measure("node_title", content.title).width
        transition_width = self.metrics.measure("material", content.transition).width
        system_width = self.metrics.measure("technical", content.system_line).width
        tag_widths = tuple(self.metrics.measure("tag", tag.code).width + 18 for tag in content.tags)
        tag_total = sum(tag_widths) + max(0, len(tag_widths) - 1) * 7
        natural_width = max(
            badge_width,
            title_width,
            transition_width,
            system_width + tag_total + 18,
        ) + padding_x * 2
        return min(self.HARD_MAX_WIDTH, max(self.MIN_WIDTH, natural_width)), tag_widths

    def measure(
        self,
        content: NodeContent,
        local_width_budget: float | None = None,
    ) -> tuple[float, float, tuple[str, ...], tuple[float, ...]]:
        padding_x = self.PADDING_X
        ideal_width, tag_widths = self.ideal_width(content)
        budget = self.HARD_MAX_WIDTH if local_width_budget is None else max(self.MIN_WIDTH, local_width_budget)
        width = min(ideal_width, budget)
        title = self.metrics.wrap_balanced("node_title", content.title, width - padding_x * 2)
        height = 20 + 20 + 8 + title.height + 6 + 20 + 8 + 18 + 16
        return width, height, title.lines, tag_widths


@dataclass(frozen=True)
class LaneSpec:
    lane_id: str
    code: str
    label: str


@dataclass(frozen=True)
class StageSpec:
    index: int
    number: str
    label: str
    focal: bool = False


@dataclass(frozen=True)
class EdgeSpec:
    edge_id: str
    source: str
    target: str
    label: str
    semantic_edge_ids: tuple[str, ...]
    critical: bool = False


@dataclass(frozen=True)
class Port:
    node_id: str
    side: str
    point: Point


@dataclass(frozen=True)
class BridgeMark:
    point: Point
    orientation: str
    segment_index: int
    radius: float = 14.0


@dataclass(frozen=True)
class RoutedEdge:
    spec: EdgeSpec
    source_port: Port
    target_port: Port
    points: tuple[Point, ...]
    label_box: Box
    bridges: tuple[BridgeMark, ...] = ()


@dataclass(frozen=True)
class Artboard:
    width: float
    height: float
    safe_area: float
    rail_height: float
    lane_top: float
    lane_height: float
    legend_top: float
    legend_height: float


@dataclass(frozen=True)
class LaneLayout:
    artboard: Artboard
    lanes: tuple[LaneSpec, ...]
    stages: tuple[StageSpec, ...]
    nodes: tuple[NodeGeometry, ...]
    stage_centers: Mapping[int, float]

    @property
    def node_map(self) -> dict[str, NodeGeometry]:
        return {node.content.node_id: node for node in self.nodes}


class LaneInteractionEngine:
    """Content-fit wide lane engine with no global post-layout transform."""

    def __init__(self, node_sizer: IntrinsicNodeSizer) -> None:
        self.node_sizer = node_sizer

    def layout(
        self,
        lanes: Sequence[LaneSpec],
        stages: Sequence[StageSpec],
        contents: Sequence[NodeContent],
    ) -> LaneLayout:
        safe = 52.0
        rail_height = 138.0
        legend_height = 190.0
        stage_gap = 76.0
        left_gutter = 280.0
        measured = {content.node_id: self.node_sizer.measure(content) for content in contents}

        def solve_geometry(
            measurements: Mapping[str, tuple[float, float, tuple[str, ...], tuple[float, ...]]],
        ) -> tuple[Artboard, dict[int, float], dict[int, float]]:
            maximum_node_height = max(item[1] for item in measurements.values())
            maximum_node_width = max(item[0] for item in measurements.values())
            lane_height = maximum_node_height + 30.0
            lane_top = rail_height
            legend_top = lane_top + len(lanes) * lane_height
            natural_height = legend_top + legend_height + safe
            first_center = left_gutter + safe + maximum_node_width / 2
            stage_stride = maximum_node_width + stage_gap
            provisional = {stage.index: first_center + stage.index * stage_stride for stage in stages}
            natural_width = max(provisional.values()) + maximum_node_width / 2 + safe
            width = max(natural_width, natural_height * 2.22)
            if width / natural_height > 2.45:
                natural_height = width / 2.45
            last_center = width - safe - maximum_node_width / 2
            center_span = last_center - first_center
            denominator = max(1, len(stages) - 1)
            centers = {
                stage.index: first_center + center_span * stage.index / denominator
                for stage in stages
            }
            ordered = sorted((center, index) for index, center in centers.items())
            local_budgets: dict[int, float] = {}
            for position, (center, stage_index) in enumerate(ordered):
                adjacent = []
                if position:
                    adjacent.append(center - ordered[position - 1][0])
                if position + 1 < len(ordered):
                    adjacent.append(ordered[position + 1][0] - center)
                corridor_budget = min(adjacent) - stage_gap if adjacent else self.node_sizer.HARD_MAX_WIDTH
                local_budgets[stage_index] = min(self.node_sizer.HARD_MAX_WIDTH, corridor_budget)
            board = Artboard(
                width=round(width, 2),
                height=round(natural_height, 2),
                safe_area=safe,
                rail_height=rail_height,
                lane_top=lane_top,
                lane_height=lane_height,
                legend_top=legend_top,
                legend_height=legend_height,
            )
            return board, centers, local_budgets

        for _ in range(4):
            artboard, stage_centers, stage_budgets = solve_geometry(measured)
            next_measured = {
                content.node_id: self.node_sizer.measure(content, stage_budgets[content.stage])
                for content in contents
            }
            signature = tuple((key, value[0], value[2]) for key, value in sorted(measured.items()))
            next_signature = tuple((key, value[0], value[2]) for key, value in sorted(next_measured.items()))
            measured = next_measured
            if next_signature == signature:
                break

        artboard, stage_centers, _ = solve_geometry(measured)
        lane_index = {lane.lane_id: index for index, lane in enumerate(lanes)}
        nodes: list[NodeGeometry] = []
        for content in contents:
            width_value, height_value, title_lines, tag_widths = measured[content.node_id]
            x = stage_centers[content.stage] - width_value / 2
            y = (
                artboard.lane_top
                + lane_index[content.lane_id] * artboard.lane_height
                + (artboard.lane_height - height_value) / 2
            )
            nodes.append(
                NodeGeometry(
                    content=content,
                    box=Box(x, y, width_value, height_value),
                    title_lines=title_lines,
                    tag_widths=tag_widths,
                )
            )
        return LaneLayout(
            artboard=artboard,
            lanes=tuple(lanes),
            stages=tuple(stages),
            nodes=tuple(nodes),
            stage_centers=stage_centers,
        )


def _unique_sorted(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(sorted(set(round(value, 3) for value in values)))


def _segment_hits_box(a: Point, b: Point, box: Box, clearance: float) -> bool:
    target = box.inflated(clearance)
    if abs(a.x - b.x) < 0.001:
        low, high = sorted((a.y, b.y))
        return target.left <= a.x <= target.right and not (high <= target.top or low >= target.bottom)
    if abs(a.y - b.y) < 0.001:
        low, high = sorted((a.x, b.x))
        return target.top <= a.y <= target.bottom and not (high <= target.left or low >= target.right)
    raise ValueError("Only orthogonal segments are supported")


def route_hits_box(points: Sequence[Point], box: Box, clearance: float = 0.0) -> bool:
    return any(_segment_hits_box(a, b, box, clearance) for a, b in zip(points, points[1:]))


class PortAllocator:
    def allocate(self, layout: LaneLayout, edges: Sequence[EdgeSpec]) -> dict[tuple[str, str], Port]:
        node_map = layout.node_map
        inbound: dict[str, list[EdgeSpec]] = {}
        outbound: dict[str, list[EdgeSpec]] = {}
        for edge in edges:
            inbound.setdefault(edge.target, []).append(edge)
            outbound.setdefault(edge.source, []).append(edge)
        result: dict[tuple[str, str], Port] = {}
        for node_id, related in inbound.items():
            node = node_map[node_id]
            ordered = sorted(related, key=lambda edge: node_map[edge.source].box.cy)
            offsets = self._offsets(len(ordered))
            for edge, offset in zip(ordered, offsets):
                result[(edge.edge_id, "target")] = Port(node_id, "left", Point(node.box.left, node.box.cy + offset))
        for node_id, related in outbound.items():
            node = node_map[node_id]
            ordered = sorted(related, key=lambda edge: node_map[edge.target].box.cy)
            offsets = self._offsets(len(ordered))
            for edge, offset in zip(ordered, offsets):
                result[(edge.edge_id, "source")] = Port(node_id, "right", Point(node.box.right, node.box.cy + offset))
        return result

    @staticmethod
    def _offsets(count: int) -> tuple[float, ...]:
        if count <= 1:
            return (0.0,)
        spacing = 22.0
        start = -(count - 1) * spacing / 2
        return tuple(start + index * spacing for index in range(count))


class OrthogonalRouter:
    """Route rounded orthogonal edges through measured stage corridors."""

    def __init__(self, clearance: float = 14.0, label_clearance: float = 10.0) -> None:
        self.clearance = clearance
        self.label_clearance = label_clearance

    def route(self, layout: LaneLayout, edges: Sequence[EdgeSpec], label_widths: Mapping[str, float]) -> tuple[RoutedEdge, ...]:
        node_map = layout.node_map
        ports = PortAllocator().allocate(layout, edges)
        obstacles = {node_id: geometry.box for node_id, geometry in node_map.items()}
        routed: list[RoutedEdge] = []
        for edge in edges:
            source = ports[(edge.edge_id, "source")]
            target = ports[(edge.edge_id, "target")]
            candidates = self._corridor_candidates(layout, source.point.x, target.point.x)
            selected: tuple[Point, ...] | None = None
            for corridor_x in candidates:
                points = self._compress((
                    source.point,
                    Point(corridor_x, source.point.y),
                    Point(corridor_x, target.point.y),
                    target.point,
                ))
                if self._clear(points, edge, obstacles):
                    selected = points
                    break
            if selected is None:
                raise RuntimeError(f"No obstacle-clear corridor for edge {edge.edge_id}")
            label_width = label_widths[edge.edge_id]
            label_box = self._label_box(selected, label_width)
            routed.append(
                RoutedEdge(
                    spec=edge,
                    source_port=source,
                    target_port=target,
                    points=selected,
                    label_box=label_box,
                )
            )
        positioned = self._position_labels(tuple(routed), layout)
        return self._with_bridges(positioned)

    def _corridor_candidates(self, layout: LaneLayout, source_x: float, target_x: float) -> tuple[float, ...]:
        lower, upper = sorted((source_x, target_x))
        centers = sorted(layout.stage_centers.values())
        gaps = [(left + right) / 2 for left, right in zip(centers, centers[1:]) if lower < (left + right) / 2 < upper]
        preferred = (source_x * 0.35 + target_x * 0.65, (source_x + target_x) / 2, source_x * 0.65 + target_x * 0.35)
        values = [value for value in preferred + tuple(reversed(gaps)) + tuple(gaps) if lower + 18 < value < upper - 18]
        return _unique_sorted(values)

    def _clear(self, points: Sequence[Point], edge: EdgeSpec, obstacles: Mapping[str, Box]) -> bool:
        for node_id, box in obstacles.items():
            if node_id in {edge.source, edge.target}:
                continue
            if route_hits_box(points, box, self.clearance):
                return False
        return True

    @staticmethod
    def _compress(points: Sequence[Point]) -> tuple[Point, ...]:
        result: list[Point] = []
        for point in points:
            if result and abs(result[-1].x - point.x) < 0.001 and abs(result[-1].y - point.y) < 0.001:
                continue
            result.append(point)
        return tuple(result)

    def _label_box(self, points: Sequence[Point], width: float) -> Box:
        horizontal = [
            (a, b)
            for a, b in zip(points, points[1:])
            if abs(a.y - b.y) < 0.001 and abs(a.x - b.x) >= width + 24
        ]
        if not horizontal:
            a, b = points[0], points[-1]
        else:
            a, b = max(horizontal, key=lambda pair: abs(pair[1].x - pair[0].x))
        center_x = (a.x + b.x) / 2
        y = a.y - 30 - self.label_clearance
        return Box(center_x - width / 2 - 10, y, width + 20, 28)

    def _position_labels(self, edges: tuple[RoutedEdge, ...], layout: LaneLayout) -> tuple[RoutedEdge, ...]:
        node_boxes = [node.box for node in layout.nodes]
        placed: list[Box] = []
        positioned: list[RoutedEdge] = []
        for edge in edges:
            width = edge.label_box.width
            candidates: list[Box] = []
            for a, b in zip(edge.points, edge.points[1:]):
                if abs(a.y - b.y) < 0.001 and abs(a.x - b.x) >= width + 24:
                    low, high = sorted((a.x, b.x))
                    for fraction in (0.35, 0.5, 0.65):
                        center_x = low + (high - low) * fraction
                        candidates.append(Box(center_x - width / 2, a.y - 38 - self.label_clearance, width, 28))
                        candidates.append(Box(center_x - width / 2, a.y + 10 + self.label_clearance, width, 28))
                elif abs(a.x - b.x) < 0.001 and abs(a.y - b.y) >= 52:
                    low, high = sorted((a.y, b.y))
                    for fraction in (0.35, 0.5, 0.65):
                        center_y = low + (high - low) * fraction
                        candidates.append(Box(a.x + 18 + self.label_clearance, center_y - 14, width, 28))
                        candidates.append(Box(a.x - width - 18 - self.label_clearance, center_y - 14, width, 28))
            selected = edge.label_box
            for candidate in candidates:
                if candidate.top < layout.artboard.rail_height + 4 or candidate.bottom > layout.artboard.legend_top - 4:
                    continue
                if any(candidate.intersects(box, 8) for box in node_boxes):
                    continue
                if any(candidate.intersects(box, 8) for box in placed):
                    continue
                blocked = False
                for other in edges:
                    if other.spec.edge_id == edge.spec.edge_id:
                        continue
                    distance = min(
                        segment_distance_to_box(start, end, candidate)
                        for start, end in zip(other.points, other.points[1:])
                    )
                    if distance < 8:
                        blocked = True
                        break
                if not blocked:
                    selected = candidate
                    break
            placed.append(selected)
            positioned.append(
                RoutedEdge(
                    spec=edge.spec,
                    source_port=edge.source_port,
                    target_port=edge.target_port,
                    points=edge.points,
                    label_box=selected,
                    bridges=edge.bridges,
                )
            )
        return tuple(positioned)

    @staticmethod
    def _with_bridges(edges: tuple[RoutedEdge, ...]) -> tuple[RoutedEdge, ...]:
        bridge_map: dict[str, list[BridgeMark]] = {edge.spec.edge_id: [] for edge in edges}
        for left_index, left in enumerate(edges):
            for right in edges[left_index + 1:]:
                for a1, a2 in zip(left.points, left.points[1:]):
                    for b1, b2 in zip(right.points, right.points[1:]):
                        left_horizontal = abs(a1.y - a2.y) < 0.001
                        right_horizontal = abs(b1.y - b2.y) < 0.001
                        if left_horizontal == right_horizontal:
                            continue
                        horizontal = (a1, a2) if left_horizontal else (b1, b2)
                        vertical = (b1, b2) if left_horizontal else (a1, a2)
                        hx1, hx2 = sorted((horizontal[0].x, horizontal[1].x))
                        vy1, vy2 = sorted((vertical[0].y, vertical[1].y))
                        x = vertical[0].x
                        y = horizontal[0].y
                        radius = 14.0
                        if hx1 + radius + 2 < x < hx2 - radius - 2 and vy1 + radius + 2 < y < vy2 - radius - 2:
                            owner = left if left_horizontal else right
                            owner_segments = list(zip(owner.points, owner.points[1:]))
                            segment_index = next(
                                index
                                for index, (start, end) in enumerate(owner_segments)
                                if abs(start.y - end.y) < 0.001
                                and min(start.x, end.x) < x < max(start.x, end.x)
                                and abs(start.y - y) < 0.001
                            )
                            mark = BridgeMark(Point(x, y), "horizontal", segment_index, radius)
                            if not any(
                                existing.segment_index == mark.segment_index
                                and abs(existing.point.x - mark.point.x) < 0.001
                                and abs(existing.point.y - mark.point.y) < 0.001
                                for existing in bridge_map[owner.spec.edge_id]
                            ):
                                bridge_map[owner.spec.edge_id].append(mark)
        return tuple(
            RoutedEdge(
                spec=edge.spec,
                source_port=edge.source_port,
                target_port=edge.target_port,
                points=edge.points,
                label_box=edge.label_box,
                bridges=tuple(sorted(
                    bridge_map[edge.spec.edge_id],
                    key=lambda mark: (mark.segment_index, mark.point.x, mark.point.y),
                )),
            )
            for edge in edges
        )


def rounded_orthogonal_path(points: Sequence[Point], radius: float = 14.0) -> str:
    if len(points) < 2:
        raise ValueError("A route needs at least two points")
    commands = [f"M {points[0].x:.2f} {points[0].y:.2f}"]
    for index in range(1, len(points) - 1):
        previous, current, following = points[index - 1], points[index], points[index + 1]
        incoming = hypot(current.x - previous.x, current.y - previous.y)
        outgoing = hypot(following.x - current.x, following.y - current.y)
        corner = min(radius, incoming / 2, outgoing / 2)
        before = Point(
            current.x + (previous.x - current.x) / incoming * corner,
            current.y + (previous.y - current.y) / incoming * corner,
        )
        after = Point(
            current.x + (following.x - current.x) / outgoing * corner,
            current.y + (following.y - current.y) / outgoing * corner,
        )
        commands.append(f"L {before.x:.2f} {before.y:.2f}")
        commands.append(f"Q {current.x:.2f} {current.y:.2f} {after.x:.2f} {after.y:.2f}")
    commands.append(f"L {points[-1].x:.2f} {points[-1].y:.2f}")
    return " ".join(commands)


def segment_distance_to_box(a: Point, b: Point, box: Box) -> float:
    """Conservative distance for orthogonal segment-to-label clearance checks."""
    if _segment_hits_box(a, b, box, 0):
        return 0.0
    if abs(a.y - b.y) < 0.001:
        low, high = sorted((a.x, b.x))
        dx = max(box.left - high, low - box.right, 0)
        dy = max(box.top - a.y, a.y - box.bottom, 0)
        return hypot(dx, dy)
    low, high = sorted((a.y, b.y))
    dx = max(box.left - a.x, a.x - box.right, 0)
    dy = max(box.top - high, low - box.bottom, 0)
    return hypot(dx, dy)


def default_font_catalog() -> dict[str, tuple[FontFace, ...]]:
    avenir = Path("/System/Library/Fonts/Avenir Next.ttc")
    menlo = Path("/System/Library/Fonts/Menlo.ttc")
    georgia = Path("/System/Library/Fonts/Supplemental/Georgia.ttf")
    georgia_bold = Path("/System/Library/Fonts/Supplemental/Georgia Bold.ttf")
    catalog: dict[str, tuple[FontFace, ...]] = {}
    if avenir.exists():
        catalog["Avenir Next"] = (
            FontFace("Avenir Next", avenir, 7, 400),
            FontFace("Avenir Next", avenir, 5, 500),
            FontFace("Avenir Next", avenir, 2, 600),
            FontFace("Avenir Next", avenir, 0, 700),
        )
    if menlo.exists():
        catalog["Menlo"] = (
            FontFace("Menlo", menlo, 0, 400),
            FontFace("Menlo", menlo, 1, 700),
        )
    if georgia.exists():
        faces = [FontFace("Georgia", georgia, 0, 400)]
        if georgia_bold.exists():
            faces.append(FontFace("Georgia", georgia_bold, 0, 700))
        catalog["Georgia"] = tuple(faces)
    return catalog


def default_font_roles() -> dict[str, FontRole]:
    return {
        "display": FontRole("display", "Instrument Serif", ("Georgia",), 48, 400, 56),
        "lane": FontRole("lane", "Geist", ("Avenir Next",), 18, 600, 23, 1.4),
        "node_title": FontRole("node_title", "Geist", ("Avenir Next",), 24, 600, 30),
        "material": FontRole("material", "Geist", ("Avenir Next",), 16, 500, 20),
        "technical": FontRole("technical", "Geist Mono", ("Menlo",), 16, 400, 19),
        "badge": FontRole("badge", "Geist Mono", ("Menlo",), 14, 700, 18, 0.8),
        "tag": FontRole("tag", "Geist Mono", ("Menlo",), 14, 700, 18, 0.5),
        "legend": FontRole("legend", "Geist", ("Avenir Next",), 16, 500, 20),
    }


def resolve_default_typography(request: TypographyRequest | None = None) -> dict[str, ResolvedFont]:
    resolver = FontResolver(default_font_catalog())
    actual_request = request or TypographyRequest()
    return {name: resolver.resolve(role, actual_request) for name, role in default_font_roles().items()}


__all__ = [
    "Artboard",
    "Box",
    "BridgeMark",
    "DataTag",
    "EdgeSpec",
    "FontMetricEngine",
    "FontResolutionError",
    "FontResolver",
    "FontRole",
    "IntrinsicNodeSizer",
    "LaneInteractionEngine",
    "LaneLayout",
    "LaneSpec",
    "NodeContent",
    "NodeGeometry",
    "OrthogonalRouter",
    "Point",
    "ResolvedFont",
    "RoutedEdge",
    "StageSpec",
    "TypographyRequest",
    "default_font_catalog",
    "default_font_roles",
    "resolve_default_typography",
    "rounded_orthogonal_path",
    "route_hits_box",
    "segment_distance_to_box",
]
