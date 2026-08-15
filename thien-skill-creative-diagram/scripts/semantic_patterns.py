"""Original P-05 semantic transformations for the seven locked patterns.

The transformations accept already trusted, structured facts. They create no
layout, styling, renderer instructions, or inferred business facts.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from diagram_core import CoreError
from semantic_catalog import PATTERNS


def _fail(field: str, message: str) -> None:
    raise CoreError("pattern-input-invalid", "semantic-pattern", message, field=field)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(field, "A supplied non-empty label is required; the transformation will not invent one.")
    return value


def _strings(value: Any, field: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _fail(field, "A list of supplied labels is required.")
    values = [_text(item, f"{field}[{index}]") for index, item in enumerate(value)]
    if len(values) < minimum:
        _fail(field, f"At least {minimum} supplied values are required.")
    return values


def _slug(index: int, role: str) -> str:
    return f"{role}-{index + 1}"


def _node(node_id: str, role: str, label: str, **extra: Any) -> dict[str, Any]:
    return {"id": node_id, "role": role, "label": label, **extra}


def _edge(edge_id: str, source: str, target: str, kind: str, **extra: Any) -> dict[str, Any]:
    return {"id": edge_id, "source": source, "target": target, "kind": kind, "directed": True, **extra}


def _result(capability_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], *, groups: list[dict[str, Any]] | None = None, lanes: list[dict[str, Any]] | None = None, annotations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "capability_id": capability_id,
        "diagram_type": PATTERNS[capability_id]["parent"],
        "nodes": nodes,
        "edges": edges,
        "groups": groups or [],
        "lanes": lanes or [],
        "series": [],
        "axes": [],
        "annotations": annotations or [],
    }


def transform_fan_in_queue(facts: Mapping[str, Any]) -> dict[str, Any]:
    producers = _strings(facts.get("producers"), "producers", 2)
    queue_label = _text(facts.get("queue"), "queue")
    sink_label = _text(facts.get("sink"), "sink")
    capacity = _text(facts.get("capacity"), "capacity")
    overflow = _text(facts.get("overflow"), "overflow")
    nodes = [_node(_slug(i, "source"), "source", label) for i, label in enumerate(producers)]
    nodes += [_node("queue-main", "queue", queue_label, secondary_label=capacity), _node("sink-main", "sink", sink_label), _node("sink-overflow", "sink", overflow)]
    edges = [_edge(_slug(i, "transfer"), node["id"], "queue-main", "transfer") for i, node in enumerate(nodes[: len(producers)])]
    edges += [_edge("transfer-delivery", "queue-main", "sink-main", "transfer"), _edge("transfer-overflow", "queue-main", "sink-overflow", "transfer")]
    return _result("CAP-P01", nodes, edges)


def transform_repeated_stages(facts: Mapping[str, Any]) -> dict[str, Any]:
    stages = facts.get("stages")
    if not isinstance(stages, Sequence) or isinstance(stages, (str, bytes)) or len(stages) < 2:
        _fail("stages", "At least two supplied stage records are required.")
    nodes: list[dict[str, Any]] = []
    lanes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    previous_artifact: str | None = None
    for index, raw in enumerate(stages):
        if not isinstance(raw, Mapping):
            _fail(f"stages[{index}]", "Each stage must be an object.")
        activity_id = _slug(index, "activity")
        artifact_id = _slug(index, "artifact")
        nodes += [_node(activity_id, "activity", _text(raw.get("activity"), f"stages[{index}].activity")), _node(artifact_id, "artifact", _text(raw.get("artifact"), f"stages[{index}].artifact"))]
        lanes.append({"id": _slug(index, "lane"), "label": _text(raw.get("owner"), f"stages[{index}].owner"), "owner": _text(raw.get("owner"), f"stages[{index}].owner"), "member_ids": [activity_id, artifact_id], "order": index})
        if previous_artifact is not None:
            edges.append(_edge(_slug(index - 1, "handoff"), previous_artifact, activity_id, "handoff", order=index - 1))
        edges.append(_edge(_slug(index, "flow"), activity_id, artifact_id, "flow", order=len(stages) + index))
        previous_artifact = artifact_id
    return _result("CAP-P02", nodes, edges, lanes=lanes)


def transform_unstructured_artifact(facts: Mapping[str, Any]) -> dict[str, Any]:
    nodes = [
        _node("source-unstructured", "source", _text(facts.get("input"), "input")),
        _node("transform-structure", "transform", _text(facts.get("transform"), "transform")),
        _node("sink-structured", "sink", _text(facts.get("output"), "output")),
    ]
    edges = [_edge("transfer-input", "source-unstructured", "transform-structure", "transfer"), _edge("transfer-output", "transform-structure", "sink-structured", "transfer")]
    return _result("CAP-P03", nodes, edges)


def transform_policy_traces(facts: Mapping[str, Any]) -> dict[str, Any]:
    policy = _text(facts.get("policy"), "policy")
    allow = _text(facts.get("allow_outcome"), "allow_outcome")
    deny = _text(facts.get("deny_outcome"), "deny_outcome")
    nodes = [_node("start-request", "start", _text(facts.get("request"), "request")), _node("decision-policy", "decision", policy), _node("terminal-allow", "terminal", allow), _node("terminal-deny", "terminal", deny)]
    edges = [_edge("flow-evaluate", "start-request", "decision-policy", "flow"), _edge("flow-allow", "decision-policy", "terminal-allow", "flow", guard=allow), _edge("flow-deny", "decision-policy", "terminal-deny", "flow", guard=deny)]
    return _result("CAP-P04", nodes, edges)


def transform_secure_route(facts: Mapping[str, Any]) -> dict[str, Any]:
    approved_label = _text(facts.get("approved_label"), "approved_label")
    denied_label = _text(facts.get("denied_label"), "denied_label")
    nodes = [_node("actor-requester", "actor", _text(facts.get("requester"), "requester")), _node("service-gateway", "service", _text(facts.get("gateway"), "gateway")), _node("service-approved", "service", _text(facts.get("service"), "service")), _node("service-denied", "service", _text(facts.get("denied_route"), "denied_route"))]
    edges = [_edge("dependency-entry", "actor-requester", "service-gateway", "dependency"), _edge("dependency-approved", "service-gateway", "service-approved", "dependency", label=approved_label), _edge("dependency-denied", "actor-requester", "service-denied", "dependency", label=denied_label)]
    groups = [{"id": "boundary-trusted", "label": _text(facts.get("boundary"), "boundary"), "member_ids": ["service-gateway", "service-approved"]}]
    return _result("CAP-P05", nodes, edges, groups=groups)


def transform_control_catalog(facts: Mapping[str, Any]) -> dict[str, Any]:
    layers = facts.get("layers")
    if not isinstance(layers, Sequence) or isinstance(layers, (str, bytes)) or len(layers) < 2:
        _fail("layers", "At least two supplied layer records are required.")
    nodes: list[dict[str, Any]] = []
    lanes: list[dict[str, Any]] = []
    for index, raw in enumerate(layers):
        if not isinstance(raw, Mapping):
            _fail(f"layers[{index}]", "Each layer must be an object.")
        node_id = _slug(index, "control")
        nodes.append(_node(node_id, "control", _text(raw.get("control"), f"layers[{index}].control")))
        lanes.append({"id": _slug(index, "layer"), "label": _text(raw.get("layer"), f"layers[{index}].layer"), "owner": _text(raw.get("owner"), f"layers[{index}].owner"), "member_ids": [node_id], "order": index})
    edges = [_edge(_slug(i, "enforcement"), nodes[i]["id"], nodes[i + 1]["id"], "enforcement") for i in range(len(nodes) - 1)]
    return _result("CAP-P06", nodes, edges, lanes=lanes)


def transform_compensating_layers(facts: Mapping[str, Any]) -> dict[str, Any]:
    layers = _strings(facts.get("layers"), "layers", 2)
    controls = _strings(facts.get("controls"), "controls", len(layers))
    if len(controls) != len(layers):
        _fail("controls", "Each supplied layer needs exactly one supplied compensating control.")
    nodes = [_node(_slug(i, "control"), "control", controls[i]) for i in range(len(layers))]
    lanes = [{"id": _slug(i, "layer"), "label": layers[i], "owner": _text(facts.get("owner"), "owner"), "member_ids": [nodes[i]["id"]], "order": i} for i in range(len(layers))]
    edges = [_edge(_slug(i, "compensation"), nodes[i]["id"], nodes[i + 1]["id"], "compensation") for i in range(len(nodes) - 1)]
    annotations = [{"id": "annotation-residual-risk", "text": _text(facts.get("residual_risk"), "residual_risk"), "target_ids": [nodes[-1]["id"]]}]
    return _result("CAP-P07", nodes, edges, lanes=lanes, annotations=annotations)


TRANSFORMS = {
    "CAP-P01": transform_fan_in_queue,
    "CAP-P02": transform_repeated_stages,
    "CAP-P03": transform_unstructured_artifact,
    "CAP-P04": transform_policy_traces,
    "CAP-P05": transform_secure_route,
    "CAP-P06": transform_control_catalog,
    "CAP-P07": transform_compensating_layers,
}


def apply_pattern(capability_id: str, facts: Mapping[str, Any]) -> dict[str, Any]:
    transform = TRANSFORMS.get(capability_id)
    if transform is None:
        _fail("capability_id", "The semantic pattern is outside the locked inventory.")
    return transform(facts)


__all__ = ["TRANSFORMS", "apply_pattern"] + [pattern["transform"] for pattern in PATTERNS.values()]
