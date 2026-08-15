"""P-05 semantic selectors and validators for the 27 canonical types."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime
from typing import Any, Callable, Iterable, Mapping

from diagram_core import CoreError, validate_common_ir
from semantic_catalog import TYPE_GRAMMARS


PERMISSION_STATES = {"allow", "deny", "conditional", "unknown"}
CARDINALITY_KINDS = {"one-to-one", "one-to-many", "many-to-one", "many-to-many"}
MESSAGE_KINDS = {"message", "request", "response", "async", "return"}


def _error(code: str, message: str, field: str = "ir") -> None:
    raise CoreError(code, "type-grammar", message, field=field)


def _roles(ir: Mapping[str, Any]) -> Counter[str]:
    return Counter(node["role"] for node in ir["nodes"])


def _edge_adjacency(ir: Mapping[str, Any], edge_filter: Callable[[Mapping[str, Any]], bool] | None = None) -> tuple[dict[str, list[str]], Counter[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree: Counter[str] = Counter()
    for edge in ir["edges"]:
        if edge_filter is not None and not edge_filter(edge):
            continue
        adjacency[edge["source"]].append(edge["target"])
        indegree[edge["target"]] += 1
        indegree.setdefault(edge["source"], 0)
    return adjacency, indegree


def _reachable(adjacency: Mapping[str, list[str]], starts: Iterable[str]) -> set[str]:
    queue = deque(starts)
    seen = set(starts)
    while queue:
        current = queue.popleft()
        for target in adjacency.get(current, []):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def _has_cycle(ir: Mapping[str, Any], edge_filter: Callable[[Mapping[str, Any]], bool] | None = None) -> bool:
    adjacency, _ = _edge_adjacency(ir, edge_filter)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        for target in adjacency.get(node_id, []):
            if visit(target):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node["id"]) for node in ir["nodes"])


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _axes(ir: Mapping[str, Any], dimension: str) -> list[Mapping[str, Any]]:
    return [axis for axis in ir["axes"] if axis["dimension"] == dimension]


def _require_role(ir: Mapping[str, Any], role: str, code: str | None = None) -> None:
    if _roles(ir)[role] == 0:
        _error(code or f"missing-role-{role}", f"Required semantic role is missing: {role}.", "ir.nodes")


def _minimum(ir: Mapping[str, Any], collection: str, count: int, code: str) -> None:
    if len(ir[collection]) < count:
        _error(code, f"Expected at least {count} {collection}.", f"ir.{collection}")


def _validate_minimum_two_nodes(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "nodes", 2, "minimum-two-nodes")


def _validate_minimum_three_nodes(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "nodes", 3, "minimum-three-nodes")


def _validate_minimum_one_edge(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "edges", 1, "minimum-one-edge")


def _validate_requires_boundary(ir: Mapping[str, Any]) -> None:
    if not ir["groups"]:
        _error("boundary-required", "At least one explicit boundary group is required.", "ir.groups")


def _validate_directed_edges(ir: Mapping[str, Any]) -> None:
    if any(not edge["directed"] for edge in ir["edges"]):
        _error("directed-edge-required", "Every relationship in this grammar must be directed.", "ir.edges")


def _validate_requires_group(ir: Mapping[str, Any]) -> None:
    if not ir["groups"]:
        _error("group-required", "At least one semantic group is required.", "ir.groups")


def _validate_requires_node_state(ir: Mapping[str, Any]) -> None:
    if any(not node.get("state") for node in ir["nodes"]):
        _error("node-state-required", "Every current-state system needs an explicit state.", "ir.nodes")


def _validate_requires_handoff(ir: Mapping[str, Any]) -> None:
    if not any(edge["kind"] in {"handoff", "integration", "transition"} for edge in ir["edges"]):
        _error("handoff-required", "At least one explicit handoff or integration is required.", "ir.edges")


def _validate_requires_start(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "start")


def _validate_requires_terminal(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "terminal")


def _validate_requires_decision(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "decision")


def _validate_decision_guards(ir: Mapping[str, Any]) -> None:
    decision_ids = {node["id"] for node in ir["nodes"] if node["role"] == "decision"}
    for decision_id in decision_ids:
        outgoing = [edge for edge in ir["edges"] if edge["source"] == decision_id]
        if len(outgoing) < 2 or any(not edge.get("guard") for edge in outgoing):
            _error("decision-guard-required", "Each decision needs at least two guarded outgoing branches.", "ir.edges")


def _validate_all_nodes_reachable(ir: Mapping[str, Any]) -> None:
    adjacency, indegree = _edge_adjacency(ir)
    starts = [node["id"] for node in ir["nodes"] if node["role"] in {"start", "initial"}]
    if not starts:
        starts = [node["id"] for node in ir["nodes"] if indegree[node["id"]] == 0]
    if set(node["id"] for node in ir["nodes"]) != _reachable(adjacency, starts):
        _error("unreachable-node", "Every node must be reachable from a declared start or root.", "ir.nodes")


def _validate_message_edges(ir: Mapping[str, Any]) -> None:
    if not ir["edges"] or any(edge["kind"] not in MESSAGE_KINDS for edge in ir["edges"]):
        _error("message-edge-required", "Sequence edges must use a supported message kind.", "ir.edges")


def _validate_unique_edge_order(ir: Mapping[str, Any]) -> None:
    orders = [edge.get("order") for edge in ir["edges"]]
    if any(order is None for order in orders) or len(orders) != len(set(orders)):
        _error("edge-order-invalid", "Every ordered edge needs a unique order.", "ir.edges")


def _validate_contiguous_edge_order(ir: Mapping[str, Any]) -> None:
    orders = sorted(edge.get("order") for edge in ir["edges"] if edge.get("order") is not None)
    if orders != list(range(len(orders))):
        _error("edge-order-not-contiguous", "Message order must be contiguous from zero.", "ir.edges")


def _validate_requires_initial(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "initial")


def _validate_transition_edges(ir: Mapping[str, Any]) -> None:
    if not ir["edges"] or any(edge["kind"] != "transition" for edge in ir["edges"]):
        _error("transition-edge-required", "State-machine edges must be transitions.", "ir.edges")


def _validate_entity_roles(ir: Mapping[str, Any]) -> None:
    if any(node["role"] not in {"entity", "associative-entity"} for node in ir["nodes"]):
        _error("entity-role-required", "ER nodes must be entities or associative entities.", "ir.nodes")


def _validate_cardinality_edges(ir: Mapping[str, Any]) -> None:
    if not ir["edges"] or any(edge["kind"] not in CARDINALITY_KINDS for edge in ir["edges"]):
        _error("cardinality-required", "Every ER relationship needs an explicit supported cardinality.", "ir.edges")


def _validate_requires_temporal_node(ir: Mapping[str, Any]) -> None:
    if not ir["nodes"] or any(node.get("start") is None for node in ir["nodes"]):
        _error("temporal-value-required", "Every event needs an explicit timestamp.", "ir.nodes")


def _validate_chronological_node_order(ir: Mapping[str, Any]) -> None:
    values = [_parse_time(node["start"]) for node in ir["nodes"]]
    if values != sorted(values):
        _error("chronology-out-of-order", "Timeline node order must follow supplied chronological order.", "ir.nodes")


def _validate_timezone_required(ir: Mapping[str, Any]) -> None:
    temporal_values = [
        value
        for node in ir["nodes"]
        for value in (node.get("start"), node.get("end"))
        if value is not None
    ]
    for value in temporal_values:
        parsed = _parse_time(value)
        if parsed.tzinfo is None:
            _error("timezone-required", "Temporal values need a timezone or explicit unknown-timezone marker.", "ir.nodes")


def _validate_minimum_two_lanes(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "lanes", 2, "minimum-two-lanes")


def _validate_lane_membership_exact(ir: Mapping[str, Any]) -> None:
    counts: Counter[str] = Counter(member for lane in ir["lanes"] for member in lane["member_ids"])
    node_ids = {node["id"] for node in ir["nodes"]}
    if set(counts) != node_ids or any(count != 1 for count in counts.values()):
        _error("lane-membership-not-exact", "Each node must belong to exactly one swimlane.", "ir.lanes")


def _validate_requires_cross_lane_handoff(ir: Mapping[str, Any]) -> None:
    lane_by_node = {member: lane["id"] for lane in ir["lanes"] for member in lane["member_ids"]}
    if not any(
        edge["kind"] == "handoff" and lane_by_node.get(edge["source"]) != lane_by_node.get(edge["target"])
        for edge in ir["edges"]
    ):
        _error("cross-lane-handoff-required", "At least one handoff must cross lane ownership.", "ir.edges")


def _validate_requires_x_y_axes(ir: Mapping[str, Any]) -> None:
    if len(_axes(ir, "x")) != 1 or len(_axes(ir, "y")) != 1:
        _error("x-y-axes-required", "Exactly one x and one y axis are required.", "ir.axes")


def _validate_requires_x_y_linear_axes(ir: Mapping[str, Any]) -> None:
    _validate_requires_x_y_axes(ir)
    if any(axis["scale"] != "linear" for axis in ir["axes"] if axis["dimension"] in {"x", "y"}):
        _error("linear-axes-required", "Both scatter axes must be linear.", "ir.axes")


def _validate_numeric_coordinate_series(ir: Mapping[str, Any]) -> None:
    if not ir["series"]:
        _error("coordinate-series-required", "At least one coordinate series is required.", "ir.series")
    for series in ir["series"]:
        for datum in series["data"]:
            if isinstance(datum["domain"], bool) or not isinstance(datum["domain"], (int, float)):
                _error("numeric-x-required", "Coordinate x/domain values must be numeric.", "ir.series")
            if datum["value"] is not None and not isinstance(datum["value"], (int, float)):
                _error("numeric-y-required", "Coordinate y values must be numeric or explicitly missing.", "ir.series")


def _validate_coordinates_within_domain(ir: Mapping[str, Any]) -> None:
    x_axis = _axes(ir, "x")[0]
    y_axis = _axes(ir, "y")[0]
    if any(x_axis.get(key) is None or y_axis.get(key) is None for key in ("domain_min", "domain_max")):
        _error("axis-domain-required", "Coordinate axes require explicit minimum and maximum domains.", "ir.axes")
    for series in ir["series"]:
        for datum in series["data"]:
            if not (x_axis["domain_min"] <= datum["domain"] <= x_axis["domain_max"]):
                _error("coordinate-out-of-domain", "An x coordinate is outside the declared domain.", "ir.series")
            if datum["value"] is not None and not (y_axis["domain_min"] <= datum["value"] <= y_axis["domain_max"]):
                _error("coordinate-out-of-domain", "A y coordinate is outside the declared domain.", "ir.series")


def _validate_minimum_three_axes(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "axes", 3, "minimum-three-axes")


def _validate_requires_series(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "series", 1, "series-required")


def _validate_common_axis_domain(ir: Mapping[str, Any]) -> None:
    domains = {(axis.get("domain_min"), axis.get("domain_max"), axis.get("unit")) for axis in ir["axes"]}
    if len(domains) != 1 or any(value is None for domain in domains for value in domain[:2]):
        _error("incompatible-axis-domain", "All radar criteria must share one declared domain and unit.", "ir.axes")


def _validate_values_within_domain(ir: Mapping[str, Any]) -> None:
    lower, upper, _ = next(iter({(axis.get("domain_min"), axis.get("domain_max"), axis.get("unit")) for axis in ir["axes"]}))
    for series in ir["series"]:
        if len(series["data"]) != len(ir["axes"]):
            _error("radar-dimension-mismatch", "Each radar series needs one value per criterion.", "ir.series")
        if any(datum["value"] is None or not lower <= datum["value"] <= upper for datum in series["data"]):
            _error("value-out-of-domain", "A radar value is outside the declared common domain.", "ir.series")


def _validate_requires_single_cycle(ir: Mapping[str, Any]) -> None:
    if not _has_cycle(ir):
        _error("cycle-required", "The directed station graph must close a cycle.", "ir.edges")
    adjacency, _ = _edge_adjacency(ir)
    node_ids = {node["id"] for node in ir["nodes"] if node["role"] == "station"}
    if node_ids and any(len(adjacency.get(node_id, [])) != 1 for node_id in node_ids):
        _error("single-cycle-required", "Each station must have one outgoing cycle edge.", "ir.edges")


def _validate_requires_nested_groups(ir: Mapping[str, Any]) -> None:
    if len(ir["groups"]) < 2 or not any(group.get("parent_group_id") for group in ir["groups"]):
        _error("nested-group-required", "At least one group must be nested inside another.", "ir.groups")


def _validate_requires_tree(ir: Mapping[str, Any]) -> None:
    node_ids = {node["id"] for node in ir["nodes"]}
    hierarchy_edges = [edge for edge in ir["edges"] if edge["kind"] in {"parent", "branch"}]
    if len(hierarchy_edges) != max(0, len(node_ids) - 1):
        _error("tree-edge-count", "A tree needs exactly n-1 parent-child edges.", "ir.edges")
    adjacency, indegree = _edge_adjacency(ir, lambda edge: edge in hierarchy_edges)
    roots = [node_id for node_id in node_ids if indegree[node_id] == 0]
    if len(roots) != 1 or any(indegree[node_id] != 1 for node_id in node_ids - set(roots)):
        _error("tree-parent-count", "A tree needs one root and one parent for every other node.", "ir.edges")
    if _has_cycle(ir, lambda edge: edge in hierarchy_edges) or _reachable(adjacency, roots) != node_ids:
        _error("tree-invalid", "Tree parent-child relations must be acyclic and connected.", "ir.edges")


def _validate_requires_primary_reporting(ir: Mapping[str, Any]) -> None:
    if not any(edge["kind"] == "reports-to" for edge in ir["edges"]):
        _error("primary-reporting-required", "At least one primary reporting edge is required.", "ir.edges")


def _validate_primary_reporting_acyclic(ir: Mapping[str, Any]) -> None:
    if _has_cycle(ir, lambda edge: edge["kind"] == "reports-to"):
        _error("reporting-cycle", "Primary reporting relationships cannot form a cycle.", "ir.edges")


def _validate_distinguish_nonprimary_edges(ir: Mapping[str, Any]) -> None:
    if any(edge["kind"] != "reports-to" and not edge.get("label") for edge in ir["edges"]):
        _error("nonprimary-edge-label-required", "Non-primary organizational relations need an explicit label.", "ir.edges")


def _validate_minimum_two_layers(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "lanes", 2, "minimum-two-layers")


def _validate_minimum_two_tiers(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "lanes", 2, "minimum-two-tiers")


def _validate_unique_layer_order(ir: Mapping[str, Any]) -> None:
    orders = [lane["order"] for lane in ir["lanes"]]
    if len(orders) != len(set(orders)):
        _error("layer-order-duplicate", "Layer or tier order must be unique.", "ir.lanes")


def _validate_requires_layer_members(ir: Mapping[str, Any]) -> None:
    if any(not lane["member_ids"] for lane in ir["lanes"]):
        _error("empty-layer", "Every layer needs at least one semantic member.", "ir.lanes")


def _validate_minimum_two_groups(ir: Mapping[str, Any]) -> None:
    _minimum(ir, "groups", 2, "minimum-two-groups")


def _validate_requires_single_ordered_series(ir: Mapping[str, Any]) -> None:
    if len(ir["series"]) != 1 or not ir["series"][0]["data"]:
        _error("single-series-required", "This grammar needs one non-empty ordered series.", "ir.series")


def _validate_requires_categorical_x_linear_y(ir: Mapping[str, Any]) -> None:
    if not any(axis["dimension"] == "x" and axis["scale"] == "categorical" for axis in ir["axes"]):
        _error("categorical-x-required", "Bar charts need a categorical x axis.", "ir.axes")
    if not any(axis["dimension"] == "y" and axis["scale"] == "linear" for axis in ir["axes"]):
        _error("linear-y-required", "Bar charts need a linear y axis.", "ir.axes")


def _validate_bar_zero_baseline(ir: Mapping[str, Any]) -> None:
    y_axes = _axes(ir, "y")
    has_exception = any(annotation["text"].startswith("baseline-exception:") for annotation in ir["annotations"])
    contains_zero = bool(y_axes) and y_axes[0].get("domain_min") is not None and y_axes[0].get("domain_max") is not None and y_axes[0]["domain_min"] <= 0 <= y_axes[0]["domain_max"]
    if not contains_zero and not has_exception:
        _error("bar-zero-baseline", "Bar charts require a zero baseline or an explicit approved exception.", "ir.axes")


def _validate_series_domain_consistency(ir: Mapping[str, Any]) -> None:
    domains = [[datum["domain"] for datum in series["data"]] for series in ir["series"]]
    if domains and any(domain != domains[0] for domain in domains[1:]):
        _error("series-domain-mismatch", "Series must share the same declared domain ordering.", "ir.series")


def _validate_requires_ordered_x_linear_y(ir: Mapping[str, Any]) -> None:
    x_axes = _axes(ir, "x")
    y_axes = _axes(ir, "y")
    if len(x_axes) != 1 or x_axes[0]["scale"] not in {"time", "ordinal"}:
        _error("ordered-x-required", "Line charts need one time or ordinal x axis.", "ir.axes")
    if len(y_axes) != 1 or y_axes[0]["scale"] != "linear":
        _error("linear-y-required", "Line charts need one linear y axis.", "ir.axes")


def _validate_domain_order_valid(ir: Mapping[str, Any]) -> None:
    for series in ir["series"]:
        domains = [datum["domain"] for datum in series["data"]]
        if domains != sorted(domains):
            _error("domain-order-invalid", "Series domain order must be non-decreasing.", "ir.series")


def _validate_missing_values_explicit(ir: Mapping[str, Any]) -> None:
    for series in ir["series"]:
        for datum in series["data"]:
            if datum["missing"] != (datum["value"] is None):
                _error("missingness-mismatch", "Missing status must agree with a null value.", "ir.series")


def _validate_requires_task_times(ir: Mapping[str, Any]) -> None:
    task_nodes = [node for node in ir["nodes"] if node["role"] in {"task", "milestone"}]
    if not task_nodes or any(node.get("start") is None or node.get("end") is None for node in task_nodes):
        _error("task-times-required", "Every task or milestone needs start and end timestamps.", "ir.nodes")


def _validate_end_not_before_start(ir: Mapping[str, Any]) -> None:
    for node in ir["nodes"]:
        if node.get("start") and node.get("end") and _parse_time(node["end"]) < _parse_time(node["start"]):
            _error("end-before-start", "A task or period ends before it starts.", "ir.nodes")


def _validate_dependency_acyclic(ir: Mapping[str, Any]) -> None:
    if _has_cycle(ir, lambda edge: edge["kind"] == "dependency"):
        _error("dependency-cycle", "Task dependencies cannot form a cycle.", "ir.edges")


def _validate_scatter_missingness_valid(ir: Mapping[str, Any]) -> None:
    _validate_missing_values_explicit(ir)


def _validate_requires_stage_groups(ir: Mapping[str, Any]) -> None:
    if len(ir["groups"]) < 2:
        _error("stage-groups-required", "High-Level diagrams need at least two explicit stage groups.", "ir.groups")


def _validate_requires_progression(ir: Mapping[str, Any]) -> None:
    if not any(edge["kind"] in {"progression", "dependency", "transfer"} for edge in ir["edges"]):
        _error("progression-required", "At least one stage progression is required.", "ir.edges")


def _validate_requires_cross_cutting_annotation(ir: Mapping[str, Any]) -> None:
    if not any(len(annotation["target_ids"]) >= 2 for annotation in ir["annotations"]):
        _error("cross-cutting-annotation-required", "A cross-cutting concern must target at least two stages.", "ir.annotations")


def _validate_requires_activity(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "activity")


def _validate_requires_artifact(ir: Mapping[str, Any]) -> None:
    _require_role(ir, "artifact")


def _validate_requires_process_flow(ir: Mapping[str, Any]) -> None:
    if not any(edge["kind"] in {"flow", "handoff", "parallel"} for edge in ir["edges"]):
        _error("process-flow-required", "Process diagrams need an explicit flow, handoff, or parallel edge.", "ir.edges")


def _validate_parallel_order_consistent(ir: Mapping[str, Any]) -> None:
    ordered = [edge["order"] for edge in ir["edges"] if edge.get("order") is not None and edge["kind"] != "parallel"]
    if len(ordered) != len(set(ordered)):
        _error("process-order-duplicate", "Sequential process edges need unique order values.", "ir.edges")


def _validate_requires_promotion_edge(ir: Mapping[str, Any]) -> None:
    if not any(edge["kind"] == "promotion" for edge in ir["edges"]):
        _error("promotion-edge-required", "Medallion semantics require a promotion edge.", "ir.edges")


def _validate_preserves_exception_path(ir: Mapping[str, Any]) -> None:
    exception_nodes = {node["id"] for node in ir["nodes"] if node["role"] == "exception"}
    if exception_nodes and not any(edge["target"] in exception_nodes and edge["kind"] in {"rejection", "exception"} for edge in ir["edges"]):
        _error("exception-path-missing", "Declared exceptions need an explicit path.", "ir.edges")


def _validate_requires_source_transform_sink(ir: Mapping[str, Any]) -> None:
    roles = _roles(ir)
    if roles["source"] == 0 or roles["sink"] == 0 or roles["transform"] + roles["queue"] == 0:
        _error("data-flow-role-missing", "Data flow requires source, transform or queue, and sink roles.", "ir.nodes")


def _validate_data_lineage_connected(ir: Mapping[str, Any]) -> None:
    adjacency, _ = _edge_adjacency(ir)
    sources = [node["id"] for node in ir["nodes"] if node["role"] == "source"]
    sinks = {node["id"] for node in ir["nodes"] if node["role"] == "sink"}
    if not sources or not sinks or not all(_reachable(adjacency, [source]) & sinks for source in sources):
        _error("data-lineage-disconnected", "Every data source needs a directed path to a sink.", "ir.edges")


def _validate_requires_source_platform_consumer(ir: Mapping[str, Any]) -> None:
    roles = _roles(ir)
    if roles["source"] + roles["partner"] == 0 or roles["platform-service"] == 0 or roles["consumer"] == 0:
        _error("integration-role-missing", "Integration topology requires source, platform-service, and consumer roles.", "ir.nodes")


def _matrix_cells(ir: Mapping[str, Any]) -> list[tuple[str, str, str]]:
    cells: list[tuple[str, str, str]] = []
    for node in ir["nodes"]:
        if node["role"] != "permission-cell":
            continue
        identity = node.get("secondary_label", "")
        if identity.count("|") != 1:
            _error("permission-cell-identity", "Permission cells need role|component identity.", "ir.nodes")
        role, component = identity.split("|", 1)
        cells.append((role, component, node.get("state", "")))
    return cells


def _validate_requires_rectangular_permission_matrix(ir: Mapping[str, Any]) -> None:
    cells = _matrix_cells(ir)
    roles = {cell[0] for cell in cells}
    components = {cell[1] for cell in cells}
    pairs = {(cell[0], cell[1]) for cell in cells}
    if not roles or not components or len(pairs) != len(cells) or pairs != {(role, component) for role in roles for component in components}:
        _error("permission-matrix-incomplete", "Every role-component intersection must appear exactly once.", "ir.nodes")


def _validate_permission_state_enum(ir: Mapping[str, Any]) -> None:
    if any(state not in PERMISSION_STATES for _, _, state in _matrix_cells(ir)):
        _error("permission-state-invalid", "Permission state must be allow, deny, conditional, or unknown.", "ir.nodes")


def _validate_requires_accessible_data(ir: Mapping[str, Any]) -> None:
    if not ir["accessibility"]["data_representation_required"]:
        _error("accessible-data-required", "This quantitative or matrix grammar requires an accessible data representation.", "ir.accessibility")


NO_RESTRICTION_INVARIANTS = {
    "allows-multi-group-membership",
    "group-membership-complete",
    "preserves-nonmonotonic-values",
    "preserves-outside-members",
}


INVARIANT_HANDLERS: dict[str, Callable[[Mapping[str, Any]], None]] = {
    name.removeprefix("_validate_").replace("_", "-"): value
    for name, value in list(globals().items())
    if name.startswith("_validate_") and callable(value)
}


def validate_typed_ir(ir_value: Mapping[str, Any]) -> dict[str, Any]:
    """Run common validation followed by the selected type's semantic grammar."""

    ir = validate_common_ir(ir_value)
    diagram_type = ir["diagram"]["type"]
    grammar = TYPE_GRAMMARS.get(diagram_type)
    if grammar is None:
        _error("grammar-unavailable", "No canonical semantic grammar exists for this type.", "ir.diagram.type")
    for invariant in grammar["invariants"]:
        if invariant in NO_RESTRICTION_INVARIANTS:
            continue
        handler = INVARIANT_HANDLERS.get(invariant)
        if handler is None:
            _error("grammar-handler-missing", f"Semantic invariant has no validator: {invariant}.")
        handler(ir)
    return ir


DATA_LAKE_SIGNAL_MAP = {
    "tier-promotion": "medallion",
    "sources-platform-consumers": "dp-integration",
    "stage-layer-overview": "high-level",
}


def select_data_lake_profile(signals: Iterable[str]) -> list[dict[str, Any]]:
    """Map abstract data-lake signals to existing types without creating type 28."""

    signal_list = list(signals)
    distinct_signal_count = len(set(signal_list))
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for signal in signal_list:
        if signal not in DATA_LAKE_SIGNAL_MAP:
            _error("unknown-profile-signal", f"Unknown data-lake semantic signal: {signal}.", "signals")
        diagram_type = DATA_LAKE_SIGNAL_MAP[signal]
        if diagram_type in seen:
            continue
        seen.add(diagram_type)
        selected.append(
            {
                "type": diagram_type,
                "confidence": "high" if distinct_signal_count == 1 else "medium",
                "evidence": [f"request:data-lake signal={signal}"],
                "compatible": True,
                "viable": True,
                "materially_distinct": distinct_signal_count > 1,
                "rejection_reason": "Another supplied data-lake story is dominant.",
            }
        )
    if not selected:
        _error("profile-evidence-missing", "No data-lake semantic signal was supplied.", "signals")
    return selected


def validate_variant_ids(ir: Mapping[str, Any]) -> None:
    """Enforce P-05 semantic parent mappings for implemented variants."""

    from semantic_catalog import VARIANT_MAPPINGS

    diagram_type = ir["diagram"]["type"]
    for capability_id in ir["diagram"].get("variant_ids", []):
        variant = VARIANT_MAPPINGS.get(capability_id)
        if variant is None:
            _error("variant-unmapped", f"Variant is outside the locked inventory: {capability_id}.", "ir.diagram.variant_ids")
        if "all" not in variant["parents"] and diagram_type not in variant["parents"]:
            _error("variant-parent-mismatch", f"Variant {capability_id} is incompatible with {diagram_type}.", "ir.diagram.variant_ids")


def validate_semantics(ir_value: Mapping[str, Any]) -> dict[str, Any]:
    ir = validate_typed_ir(ir_value)
    validate_variant_ids(ir)
    return ir


def missing_invariant_handlers() -> set[str]:
    invariants = {item for grammar in TYPE_GRAMMARS.values() for item in grammar["invariants"]}
    return invariants - set(INVARIANT_HANDLERS) - NO_RESTRICTION_INVARIANTS


__all__ = [
    "DATA_LAKE_SIGNAL_MAP",
    "missing_invariant_handlers",
    "select_data_lake_profile",
    "validate_semantics",
    "validate_typed_ir",
    "validate_variant_ids",
]
