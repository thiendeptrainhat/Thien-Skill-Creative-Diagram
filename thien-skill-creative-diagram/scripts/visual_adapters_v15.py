"""P-19A visual adapters for the 39-type / four-capability v1.5 target.

The adapters consume validated semantic IR and produce deterministic,
engine-specific layout plans.  They deliberately do not emit HTML, SVG, CSS,
or mode derivatives; those outputs belong to P-19B.  No adapter may fall back
to a generic card or unknown-diagram template.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping

from diagram_core import CANONICAL_TYPES, NEW_VARIANT_PARENTS, canonical_json
from semantic_grammars import derive_ridgeline_profiles, validate_semantics


ADAPTER_SCHEMA_VERSION = "1.0"
TARGET_VERSION = "1.5.0"
P19A_CAPABILITIES = ("CAP-V17", "CAP-V18", "CAP-V19", "CAP-V20")


class AdapterError(ValueError):
    """Fail-closed error raised before any visual emission."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AdapterSpec:
    adapter_id: str
    canonical_type: str
    capability_id: str | None
    layout_engine: str
    silhouette: str
    artboard_profile: str
    semantic_focus: str
    primary_mark: str
    connector_policy: str
    accessible_alternative: str


ENGINE_TYPES: dict[str, tuple[str, ...]] = {
    "topology-and-zones": ("architecture", "it-current-state", "high-level"),
    "integration-pipeline": ("data-flow", "dp-integration"),
    "runtime-deployment": ("deployment",),
    "dependency-dag": ("dependency-graph",),
    "directed-flow-state": ("flowchart", "process", "state-machine"),
    "lane-interaction": ("swimlane", "sequence"),
    "time-planning": ("timeline", "gantt"),
    "work-experience": ("kanban", "user-journey", "story-map"),
    "hierarchy": ("tree", "org-chart"),
    "containment-stack": ("nested", "layer-stack", "medallion", "pyramid-funnel"),
    "compartment-model": ("er-data-model", "database-schema", "uml-class"),
    "spatial-matrix": ("quadrant", "dp-security-matrix", "wardley-map", "venn"),
    "quantitative": ("bar-chart", "line-chart", "scatter-plot", "radar", "polar-chart", "treemap"),
    "special-geometry": ("loop-flywheel", "sankey", "fishbone"),
}

ENGINE_CAPABILITIES: dict[str, tuple[str, ...]] = {
    engine: (() if engine != "quantitative" else P19A_CAPABILITIES)
    for engine in ENGINE_TYPES
}

ENGINE_ARTBOARD_PROFILE = {
    "topology-and-zones": "landscape_network_data",
    "integration-pipeline": "landscape_network_data",
    "runtime-deployment": "landscape_network_data",
    "dependency-dag": "landscape_network_data",
    "directed-flow-state": "tall_directed_flow",
    "lane-interaction": "wide_rail_lane",
    "time-planning": "wide_rail_lane",
    "work-experience": "wide_rail_lane",
    "hierarchy": "balanced_matrix_hierarchy",
    "containment-stack": "balanced_matrix_hierarchy",
    "compartment-model": "landscape_network_data",
    "spatial-matrix": "balanced_matrix_hierarchy",
    "quantitative": "landscape_network_data",
    "special-geometry": "landscape_network_data",
}


def _spec(
    diagram_type: str,
    silhouette: str,
    semantic_focus: str,
    primary_mark: str,
    connector_policy: str,
    accessible_alternative: str,
) -> AdapterSpec:
    engine = next(engine for engine, types in ENGINE_TYPES.items() if diagram_type in types)
    return AdapterSpec(
        adapter_id=f"type:{diagram_type}",
        canonical_type=diagram_type,
        capability_id=None,
        layout_engine=engine,
        silhouette=silhouette,
        artboard_profile=ENGINE_ARTBOARD_PROFILE[engine],
        semantic_focus=semantic_focus,
        primary_mark=primary_mark,
        connector_policy=connector_policy,
        accessible_alternative=accessible_alternative,
    )


TYPE_ADAPTERS: dict[str, AdapterSpec] = {
    "architecture": _spec("architecture", "trust-zone-topology", "trust boundaries and dependencies", "bounded service node", "boundary ports with obstacle-aware orthogonal routes", "ordered component and dependency list"),
    "it-current-state": _spec("it-current-state", "health-layer-topology", "current-state health and integration", "state-coded system node", "orthogonal integration routes", "system state and dependency table"),
    "flowchart": _spec("flowchart", "start-decision-terminal-flow", "decision guards and terminal outcomes", "semantic process shape", "directed orthogonal branches with guard labels", "ordered step and branch list"),
    "sequence": _spec("sequence", "lifeline-message-sequence", "participant order and message chronology", "lifeline with message rail", "ordered horizontal message routes", "chronological message transcript"),
    "state-machine": _spec("state-machine", "initial-state-terminal-flow", "states and transitions", "state capsule", "directed transition routes", "state and transition table"),
    "er-data-model": _spec("er-data-model", "entity-cardinality-compartments", "entities and cardinalities", "entity compartment", "relationship lines with endpoint cardinality", "entity and relationship table"),
    "timeline": _spec("timeline", "proportional-event-time-rail", "chronology and event spacing", "event marker", "leader lines off a proportional rail", "chronological event list"),
    "swimlane": _spec("swimlane", "ownership-lane-handoff", "ownership, phase, and handoff", "lane-owned activity", "rounded orthogonal routes with integrated hops", "lane-by-step handoff table"),
    "quadrant": _spec("quadrant", "two-axis-quadrant-field", "relative position on two scales", "positioned point", "leaders only for direct labels", "exact point coordinate table"),
    "radar": _spec("radar", "radial-multi-axis-profile", "multivariate profile on disclosed scales", "radial polygon", "closed profile perimeter", "axis-by-series value table"),
    "loop-flywheel": _spec("loop-flywheel", "cyclic-station-ring", "closed reinforcing cycle", "cycle station", "single-direction ring routes", "ordered cycle station list"),
    "nested": _spec("nested", "nested-boundary-containment", "parent-child containment", "nested boundary", "no connector unless semantics requires one", "containment tree"),
    "tree": _spec("tree", "root-branch-leaf-tree", "parent-child hierarchy", "hierarchy node", "ranked parent-child routes", "indented hierarchy"),
    "org-chart": _spec("org-chart", "primary-reporting-tree", "primary reporting structure", "role card", "straight parent-child reporting routes", "reporting hierarchy"),
    "layer-stack": _spec("layer-stack", "ordered-control-layer-stack", "layer order and enforcement", "horizontal layer band", "cross-layer routes only", "ordered layer inventory"),
    "venn": _spec("venn", "set-overlap-field", "set membership and overlap", "set region", "no connector; enclosure carries meaning", "set membership matrix"),
    "pyramid-funnel": _spec("pyramid-funnel", "continuous-tiered-silhouette", "ordered magnitude tiers", "continuous triangular tier", "no connector; shared boundaries carry order", "stage value table"),
    "bar-chart": _spec("bar-chart", "zero-baseline-category-bars", "category magnitude on a shared baseline", "aligned bar", "no connector", "category value table"),
    "line-chart": _spec("line-chart", "ordered-series-lines", "change over an ordered domain", "series line", "ordered series path", "domain-by-series value table"),
    "gantt": _spec("gantt", "task-duration-rail", "task duration and dependency", "time bar", "dependency routes outside bars", "task schedule table"),
    "scatter-plot": _spec("scatter-plot", "xy-observation-field", "relationship and outliers", "positioned observation", "leaders only for selected labels", "exact x-y table"),
    "high-level": _spec("high-level", "bounded-stage-overview", "stage progression with cross-cutting concerns", "bounded stage", "simple left-to-right progression routes", "stage and governance summary"),
    "process": _spec("process", "activity-artifact-process", "activity-to-artifact progression", "activity or artifact shape", "ordered directed routes", "ordered process record"),
    "medallion": _spec("medallion", "tiered-promotion-stack", "data promotion through ordered tiers", "tier band", "promotion routes between tiers", "tier and promotion table"),
    "data-flow": _spec("data-flow", "source-transform-sink-pipeline", "source-transform-sink lineage", "pipeline stage", "left-to-right transfer routes", "lineage table"),
    "dp-integration": _spec("dp-integration", "source-platform-consumer-pipeline", "platform integration boundary", "platform service stage", "boundary-aware integration routes", "integration endpoint table"),
    "dp-security-matrix": _spec("dp-security-matrix", "actor-resource-permission-grid", "permission state by actor and resource", "permission cell", "no connector; row-column position carries meaning", "permission matrix"),
    "polar-chart": _spec("polar-chart", "angular-radius-cycle", "cyclical category magnitude", "radial mark", "closed only when the data contract requires it", "category radius table"),
    "treemap": _spec("treemap", "hierarchical-area-tiling", "hierarchical part-to-whole", "area tile", "no connector; enclosure and area carry meaning", "hierarchy and exact value table"),
    "sankey": _spec("sankey", "conserved-flow-ribbons", "quantitative flow conservation", "scaled ribbon", "contiguous source-target ribbon", "source-target-value flow table"),
    "fishbone": _spec("fishbone", "cause-category-spine", "grouped causes converging on one effect", "cause branch", "angled branches terminating on a shared spine", "cause category and effect list"),
    "wardley-map": _spec("wardley-map", "value-chain-evolution-field", "value-chain position and evolution", "positioned component", "dependency routes between positioned components", "component coordinate and dependency table"),
    "kanban": _spec("kanban", "wip-columns-and-cards", "work state, WIP, and blocked status", "work item card", "no connector by default", "column, WIP, and item table"),
    "user-journey": _spec("user-journey", "moments-action-thought-emotion-grid", "stage, action, touchpoint, and sentiment", "journey moment", "stage progression rail", "journey stage table"),
    "deployment": _spec("deployment", "zone-host-artifact-containment", "runtime placement and replicas", "deployed artifact", "runtime routes between exact boundaries", "zone-host-artifact table"),
    "dependency-graph": _spec("dependency-graph", "ranked-dag-with-cycle-backedge", "rank, fan-in, and explicit cycles", "dependency node", "ranked routes with cycle back-edge separation", "dependency adjacency list"),
    "uml-class": _spec("uml-class", "class-member-relationship-compartments", "classes, members, and typed relationships", "class compartment", "typed relationship routes with multiplicity", "class member and relationship table"),
    "story-map": _spec("story-map", "backbone-stories-release-cut", "backbone order and release slices", "story card", "no connector; row and cut position carry meaning", "backbone and release-slice table"),
    "database-schema": _spec("database-schema", "table-column-index-compartments", "physical tables, columns, indexes, and foreign keys", "table compartment", "column-bound foreign-key routes", "table, column, index, and key table"),
}


CAPABILITY_ADAPTERS: dict[str, AdapterSpec] = {
    "CAP-V17": AdapterSpec("capability:CAP-V17", "bar-chart", "CAP-V17", "quantitative", "paired-values-gap-dumbbell", "landscape_network_data", "two values and signed gap per category", "paired endpoint dots", "one connector segment per category", "category, endpoint, and gap table"),
    "CAP-V18": AdapterSpec("capability:CAP-V18", "line-chart", "CAP-V18", "quantitative", "two-state-rank-slopegraph", "landscape_network_data", "direction, rank, ties, and crossing between two states", "direct-labeled slope", "one segment per series", "series endpoint, delta, and rank table"),
    "CAP-V19": AdapterSpec("capability:CAP-V19", "line-chart", "CAP-V19", "quantitative", "shared-domain-distribution-ridgeline", "landscape_network_data", "comparable distributions on one domain and amplitude contract", "offset density ridge", "no semantic connector", "series profile and exact sample table"),
    "CAP-V20": AdapterSpec("capability:CAP-V20", "scatter-plot", "CAP-V20", "quantitative", "xy-area-observation-bubble", "landscape_network_data", "x, y, and area-encoded magnitude", "area-scaled bubble", "leaders only for selected direct labels", "exact x-y-size table"),
}


def _items(ir: Mapping[str, Any], collection: str, fields: tuple[str, ...]) -> list[dict[str, Any]]:
    return [
        {field: copy.deepcopy(item[field]) for field in fields if field in item}
        for item in ir[collection]
    ]


def _base_projection(ir: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "nodes": _items(ir, "nodes", ("id", "role", "label", "state")),
        "edges": _items(ir, "edges", ("id", "source", "target", "kind", "directed", "label", "guard", "order")),
        "groups": _items(ir, "groups", ("id", "label", "member_ids", "parent_group_id")),
        "lanes": _items(ir, "lanes", ("id", "label", "owner", "member_ids", "order")),
        "annotations": _items(ir, "annotations", ("id", "text", "target_ids")),
    }


def _project_topology(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["topology_contract"] = {
        "boundary_ids": [item["id"] for item in ir["groups"]],
        "state_by_node": {item["id"]: item.get("state") for item in ir["nodes"] if "state" in item},
        "cross_cutting_annotation_ids": [item["id"] for item in ir["annotations"]],
    }
    return projection


def _project_pipeline(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["pipeline_contract"] = {
        "stage_ids_by_role": {
            role: [item["id"] for item in ir["nodes"] if item["role"] == role]
            for role in sorted({item["role"] for item in ir["nodes"]})
        },
        "transfer_ids": [item["id"] for item in ir["edges"]],
        "platform_boundary_ids": [item["id"] for item in ir["groups"]],
    }
    return projection


def _project_deployment(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["placements"] = [
        {"node_id": item["id"], **copy.deepcopy(item["placement"])}
        for item in ir["nodes"]
    ]
    projection["runtime_relation_ids"] = [item["id"] for item in ir["edges"]]
    return projection


def _has_directed_cycle(ir: Mapping[str, Any]) -> bool:
    adjacency: dict[str, list[str]] = {item["id"]: [] for item in ir["nodes"]}
    for edge in ir["edges"]:
        adjacency.setdefault(edge["source"], []).append(edge["target"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        if any(visit(target) for target in adjacency.get(node_id, [])):
            return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(visit(node_id) for node_id in adjacency)


def _project_dependency(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["dependency_contract"] = {
        "cycle_present": _has_directed_cycle(ir),
        "fan_in": {
            node["id"]: sum(1 for edge in ir["edges"] if edge["target"] == node["id"])
            for node in ir["nodes"]
        },
        "edge_ids": [item["id"] for item in ir["edges"]],
    }
    return projection


def _project_directed(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["directed_contract"] = {
        "start_ids": [item["id"] for item in ir["nodes"] if item["role"] in {"start", "initial"}],
        "decision_ids": [item["id"] for item in ir["nodes"] if item["role"] == "decision"],
        "terminal_ids": [item["id"] for item in ir["nodes"] if item["role"] == "terminal"],
        "guard_by_edge": {item["id"]: item["guard"] for item in ir["edges"] if "guard" in item},
        "ordered_edge_ids": [item["id"] for item in sorted(ir["edges"], key=lambda value: (value.get("order", 10**9), value["id"]))],
    }
    return projection


def _project_lane(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    if ir["diagram"]["type"] == "sequence":
        projection["lane_contract"] = {
            "participant_ids": [item["id"] for item in ir["nodes"]],
            "ordered_message_ids": [item["id"] for item in sorted(ir["edges"], key=lambda value: value["order"])],
            "mode": "lifelines",
        }
    else:
        projection["lane_contract"] = {
            "ordered_lane_ids": [item["id"] for item in sorted(ir["lanes"], key=lambda value: value["order"])],
            "handoff_ids": [item["id"] for item in ir["edges"] if item["kind"] == "handoff"],
            "mode": "ownership-lanes",
        }
    return projection


def _project_time(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["time_contract"] = {
        "items": [
            {field: copy.deepcopy(item[field]) for field in ("id", "label", "role", "start", "end") if field in item}
            for item in ir["nodes"]
        ],
        "dependency_ids": [item["id"] for item in ir["edges"]],
        "timezone_required": True,
    }
    return projection


def _project_work(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    diagram_type = ir["diagram"]["type"]
    if diagram_type == "kanban":
        projection["work_contract"] = {
            "mode": "kanban",
            "columns": _items(ir, "groups", ("id", "label", "member_ids", "wip_limit")),
            "items": [{"id": item["id"], "label": item["label"], **copy.deepcopy(item["work"])} for item in ir["nodes"]],
        }
    elif diagram_type == "user-journey":
        projection["work_contract"] = {
            "mode": "journey",
            "moments": [{"id": item["id"], "label": item["label"], **copy.deepcopy(item["journey"])} for item in ir["nodes"]],
        }
    else:
        projection["work_contract"] = {
            "mode": "story-map",
            "stories": [{"id": item["id"], "label": item["label"], **copy.deepcopy(item["story"])} for item in ir["nodes"]],
            "release_slices": _items(ir, "groups", ("id", "label", "member_ids", "release_slice")),
        }
    return projection


def _project_hierarchy(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    node_ids = {item["id"] for item in ir["nodes"]}
    if ir["diagram"]["type"] == "org-chart":
        subordinate_ids = {item["source"] for item in ir["edges"]}
        root_ids = sorted(node_ids - subordinate_ids)
        direction = "subordinate-to-manager"
    else:
        child_ids = {item["target"] for item in ir["edges"]}
        root_ids = sorted(node_ids - child_ids)
        direction = "parent-to-child"
    projection["hierarchy_contract"] = {
        "root_ids": root_ids,
        "edge_direction": direction,
        "relation_ids": [item["id"] for item in ir["edges"]],
    }
    return projection


def _project_containment(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["containment_contract"] = {
        "nested_groups": _items(ir, "groups", ("id", "label", "member_ids", "parent_group_id")),
        "ordered_layers": _items(ir, "lanes", ("id", "label", "member_ids", "order")),
        "tier_series": _items(ir, "series", ("id", "label", "unit", "data")),
        "shared_boundary_required": ir["diagram"]["type"] == "pyramid-funnel",
    }
    return projection


def _project_compartment(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["compartment_contract"] = {
        "containers": [
            {
                "id": item["id"],
                "label": item["label"],
                "role": item["role"],
                "members": copy.deepcopy(item.get("members", [])),
            }
            for item in ir["nodes"]
        ],
        "relationships": _items(
            ir,
            "edges",
            ("id", "source", "target", "kind", "relation_kind", "source_member", "target_member", "source_multiplicity", "target_multiplicity"),
        ),
        "endpoint_labels_independent": True,
    }
    return projection


def _project_spatial(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["spatial_contract"] = {
        "axes": _items(ir, "axes", ("id", "dimension", "scale", "label", "domain_min", "domain_max", "unit")),
        "series": _items(ir, "series", ("id", "label", "unit", "data")),
        "permission_cells": _items(ir, "nodes", ("id", "label", "secondary_label", "state")),
        "wardley_components": [
            {"id": item["id"], "label": item["label"], **copy.deepcopy(item["strategy"])}
            for item in ir["nodes"] if "strategy" in item
        ],
        "sets": _items(ir, "groups", ("id", "label", "member_ids")),
    }
    return projection


def _project_quantitative(ir: Mapping[str, Any], capability_id: str | None) -> dict[str, Any]:
    projection = _base_projection(ir)
    projection["quantitative_contract"] = {
        "axes": _items(ir, "axes", ("id", "dimension", "scale", "label", "domain_min", "domain_max", "unit")),
        "series": _items(ir, "series", ("id", "label", "unit", "data", "distribution")),
        "treemap_groups": _items(ir, "groups", ("id", "label", "member_ids", "parent_group_id", "declared_total", "unit")),
        "treemap_leaves": _items(ir, "nodes", ("id", "label", "value", "unit", "parent_group_id")),
        "missing_values_explicit": True,
    }
    if capability_id == "CAP-V17":
        first, second = ir["series"]
        projection["quantitative_contract"]["dumbbell_pairs"] = [
            {
                "category": left["domain"],
                "first": left["value"],
                "second": right["value"],
                "signed_gap": right["value"] - left["value"],
            }
            for left, right in zip(first["data"], second["data"])
        ]
    elif capability_id == "CAP-V18":
        projection["quantitative_contract"]["slope_series"] = [
            {
                "series_id": item["id"],
                "from_state": item["data"][0]["domain"],
                "to_state": item["data"][1]["domain"],
                "from_value": item["data"][0]["value"],
                "to_value": item["data"][1]["value"],
                "delta": item["data"][1]["value"] - item["data"][0]["value"],
            }
            for item in ir["series"]
        ]
    elif capability_id == "CAP-V19":
        projection["quantitative_contract"]["ridgeline_profiles"] = derive_ridgeline_profiles(ir)
    elif capability_id == "CAP-V20":
        projection["quantitative_contract"]["bubble_points"] = [
            {
                "id": datum["id"],
                "x": datum["x_value"],
                "y": datum["y_value"],
                "area_value": datum["size_value"],
                "area_unit": datum["size_unit"],
            }
            for item in ir["series"] for datum in item["data"]
        ]
    return projection


def _project_special(ir: Mapping[str, Any]) -> dict[str, Any]:
    projection = _base_projection(ir)
    diagram_type = ir["diagram"]["type"]
    if diagram_type == "sankey":
        projection["special_contract"] = {
            "mode": "sankey",
            "flows": _items(ir, "edges", ("id", "source", "target", "amount", "unit")),
            "conservation_required": True,
            "interface_occupancy_required": True,
        }
    elif diagram_type == "fishbone":
        projection["special_contract"] = {
            "mode": "fishbone",
            "effect_ids": [item["id"] for item in ir["nodes"] if item["role"] == "effect"],
            "cause_ids": [item["id"] for item in ir["nodes"] if item["role"] == "cause"],
            "categories": _items(ir, "groups", ("id", "label", "member_ids", "cause_category")),
        }
    else:
        projection["special_contract"] = {
            "mode": "loop",
            "ordered_station_ids": [item["id"] for item in ir["nodes"]],
            "cycle_edge_ids": [item["id"] for item in ir["edges"]],
            "closed_cycle_required": True,
        }
    return projection


PROJECTORS: dict[str, Callable[..., dict[str, Any]]] = {
    "topology-and-zones": _project_topology,
    "integration-pipeline": _project_pipeline,
    "runtime-deployment": _project_deployment,
    "dependency-dag": _project_dependency,
    "directed-flow-state": _project_directed,
    "lane-interaction": _project_lane,
    "time-planning": _project_time,
    "work-experience": _project_work,
    "hierarchy": _project_hierarchy,
    "containment-stack": _project_containment,
    "compartment-model": _project_compartment,
    "spatial-matrix": _project_spatial,
    "special-geometry": _project_special,
}


def _material_inventory(ir: Mapping[str, Any]) -> dict[str, Any]:
    collections = ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations")
    by_collection = {name: [item["id"] for item in ir[name]] for name in collections}
    member_ids = [member["id"] for node in ir["nodes"] for member in node.get("members", [])]
    datum_ids = [datum["id"] for series in ir["series"] for datum in series.get("data", [])]
    return {
        "by_collection": by_collection,
        "member_ids": member_ids,
        "datum_ids": datum_ids,
        "material_count": sum(len(values) for values in by_collection.values()) + len(member_ids) + len(datum_ids),
    }


def adapt_visual(ir_value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate semantic IR and create a deterministic P-19A adapter plan."""

    ir = validate_semantics(ir_value)
    diagram_type = ir["diagram"]["type"]
    selected = [item for item in ir["diagram"].get("variant_ids", []) if item in P19A_CAPABILITIES]
    if len(selected) > 1:
        raise AdapterError("visual-capability-conflict", "Only one P-19 quantitative visual capability may own a single rendered silhouette.")
    capability_id = selected[0] if selected else None
    spec = CAPABILITY_ADAPTERS[capability_id] if capability_id else TYPE_ADAPTERS[diagram_type]
    if capability_id and NEW_VARIANT_PARENTS[capability_id] != diagram_type:
        raise AdapterError("visual-capability-parent-mismatch", "The selected capability does not belong to the canonical type.")

    if spec.layout_engine == "quantitative":
        projection = _project_quantitative(ir, capability_id)
    else:
        projection = PROJECTORS[spec.layout_engine](ir)

    return {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "target_version": TARGET_VERSION,
        "adapter": asdict(spec),
        "semantic_projection": projection,
        "material_inventory": _material_inventory(ir),
        "accessibility_contract": {
            "name": ir["accessibility"]["name"],
            "description": ir["accessibility"]["description"],
            "reading_order": list(ir["accessibility"]["reading_order"]),
            "data_representation_required": bool(ir["accessibility"]["data_representation_required"]),
            "alternative": spec.accessible_alternative,
        },
        "typography_contract": {
            "resolve_before_layout": True,
            "measure_real_metrics": True,
            "explicit_user_font_precedence": True,
            "material_min_px": 16,
            "shrink_to_fit_allowed": False,
        },
        "geometry_contract": {
            "content_fit_artboard": True,
            "ports_before_routing": True,
            "obstacle_aware_routing": True,
            "minimum_label_connector_clearance_px": 8,
            "global_post_layout_transform_allowed": False,
        },
        "phase_boundary": {
            "layout_geometry": "deferred-to-p19b",
            "mode_derivation": "deferred-to-p19b",
            "html_svg_emission": "deferred-to-p19b",
            "full_gallery_qa_and_owner_review": "deferred-to-p19c",
        },
        "source_ir_sha256": hashlib.sha256(canonical_json(ir).encode("utf-8")).hexdigest(),
    }


def adapter_inventory() -> dict[str, Any]:
    """Return the complete machine-readable P-19A adapter registry."""

    adapters = [asdict(TYPE_ADAPTERS[item]) for item in CANONICAL_TYPES]
    capabilities = [asdict(CAPABILITY_ADAPTERS[item]) for item in P19A_CAPABILITIES]
    return {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "target_version": TARGET_VERSION,
        "phase": "P-19A",
        "canonical_type_count": len(adapters),
        "capability_count": len(capabilities),
        "layout_engine_count": len(ENGINE_TYPES),
        "layout_engines": [
            {"id": engine, "canonical_types": list(ENGINE_TYPES[engine]), "capabilities": list(ENGINE_CAPABILITIES[engine])}
            for engine in ENGINE_TYPES
        ],
        "adapters": adapters,
        "capability_adapters": capabilities,
        "boundary": {
            "emits_html_or_svg": False,
            "derives_visual_modes": False,
            "creates_gallery": False,
            "next_authority_required": "P-19B",
        },
    }


def _validate_registry() -> None:
    flattened = tuple(item for values in ENGINE_TYPES.values() for item in values)
    if len(flattened) != len(CANONICAL_TYPES) or set(flattened) != set(CANONICAL_TYPES):
        raise RuntimeError("P-19A engine mapping must cover every canonical type exactly once.")
    if set(TYPE_ADAPTERS) != set(CANONICAL_TYPES):
        raise RuntimeError("P-19A requires one adapter for every canonical type.")
    if set(CAPABILITY_ADAPTERS) != set(P19A_CAPABILITIES):
        raise RuntimeError("P-19A requires the exact four approved capability adapters.")
    silhouettes = [item.silhouette for item in TYPE_ADAPTERS.values()] + [item.silhouette for item in CAPABILITY_ADAPTERS.values()]
    if len(silhouettes) != len(set(silhouettes)):
        raise RuntimeError("Every P-19A adapter needs a distinct silhouette declaration.")
    if any("generic" in item or "unknown" in item for item in silhouettes):
        raise RuntimeError("Generic/unknown silhouettes are forbidden.")


_validate_registry()


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "AdapterError",
    "AdapterSpec",
    "CAPABILITY_ADAPTERS",
    "ENGINE_CAPABILITIES",
    "ENGINE_TYPES",
    "P19A_CAPABILITIES",
    "TARGET_VERSION",
    "TYPE_ADAPTERS",
    "adapt_visual",
    "adapter_inventory",
]
