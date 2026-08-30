"""Provider-neutral request, routing, and common semantic-IR core.

This module intentionally stops before carrier parsing, type grammars, layout,
rendering, and export. It uses only the Python standard library and performs no
network access, dependency installation, attachment dereference, or file write.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.5"

CANONICAL_TYPES = (
    "architecture",
    "it-current-state",
    "flowchart",
    "sequence",
    "state-machine",
    "er-data-model",
    "timeline",
    "swimlane",
    "quadrant",
    "radar",
    "polar-chart",
    "loop-flywheel",
    "nested",
    "tree",
    "org-chart",
    "layer-stack",
    "venn",
    "pyramid-funnel",
    "bar-chart",
    "treemap",
    "line-chart",
    "gantt",
    "scatter-plot",
    "high-level",
    "process",
    "medallion",
    "data-flow",
    "dp-integration",
    "dp-security-matrix",
    "sankey",
    "fishbone",
    "wardley-map",
    "kanban",
    "user-journey",
    "deployment",
    "dependency-graph",
    "uml-class",
    "story-map",
    "database-schema",
)

LEGACY_CANONICAL_TYPES = tuple(
    diagram_type
    for diagram_type in CANONICAL_TYPES
    if diagram_type
    not in {
        "polar-chart",
        "treemap",
        "sankey",
        "fishbone",
        "wardley-map",
        "kanban",
        "user-journey",
        "deployment",
        "dependency-graph",
        "uml-class",
        "story-map",
        "database-schema",
    }
)

NEW_VARIANT_PARENTS = {
    "CAP-V17": "bar-chart",
    "CAP-V18": "line-chart",
    "CAP-V19": "line-chart",
    "CAP-V20": "scatter-plot",
}

SOURCE_KINDS = (
    "natural-language",
    "pasted-table",
    "csv",
    "json",
    "drawio",
    "mermaid",
)
SIZES = (
    "doc-inline",
    "doc-wide",
    "slide-16x9",
    "slide-4x3",
    "social-og",
    "social-square",
    "print-a4-landscape",
    "print-letter-landscape",
    "fit",
)
DETAILS = ("faithful", "balanced", "simplified")
AUDIENCES = ("engineer", "mixed", "executive")
VISUAL_MODES = ("neutral-light", "neutral-dark", "editorial")
FORMATS = ("html", "svg", "png", "html+png")
MOTIONS = ("none", "reveal", "step", "loop")
CONFIDENCE = ("high", "medium", "low")
CONTENT_CLASSES = (
    "entity",
    "relation",
    "group",
    "lane",
    "value",
    "date",
    "label",
    "annotation",
    "source-rot",
)

REQUEST_DEFAULTS = {
    "schema_version": SCHEMA_VERSION,
    "diagram_type": "auto",
    "variant_ids": [],
    "size": "fit",
    "detail": "balanced",
    "audience": "mixed",
    "visual_mode": "neutral-light",
    "language": {"mode": "auto"},
    "format": "html",
    "motion": "none",
}

REQUEST_FIELDS = frozenset(
    {
        "schema_version",
        "instruction",
        "source",
        "diagram_type",
        "variant_ids",
        "size",
        "detail",
        "audience",
        "visual_mode",
        "language",
        "format",
        "motion",
    }
)

IR_FIELDS = (
    "schema_version",
    "request_id",
    "diagram",
    "selection",
    "nodes",
    "edges",
    "groups",
    "lanes",
    "series",
    "axes",
    "annotations",
    "source_items",
    "fidelity",
    "accessibility",
)

PARSED_FIELDS = frozenset(
    {
        "title",
        "route_candidates",
        "variant_ids",
        "nodes",
        "edges",
        "groups",
        "lanes",
        "series",
        "axes",
        "annotations",
        "source_items",
        "fidelity",
        "accessibility",
    }
)

ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CAP_RE = re.compile(r"^CAP-[A-Z][A-Z0-9-]+$")
LANG_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")
DIGEST_RE = re.compile(r"^[a-f0-9]{64}$")

SECURITY_LIMITS = {
    "semantic_items": 5_000,
    "nodes": 1_000,
    "edges": 2_000,
    "label_scalars": 4_096,
    "normalized_text_scalars": 2_000_000,
}

COMPLEXITY_BUDGETS = {
    "compact": {"items": 18, "relations": 24, "groups_lanes": 4, "chart_marks": 24},
    "standard": {"items": 36, "relations": 60, "groups_lanes": 8, "chart_marks": 60},
    "wide": {"items": 64, "relations": 110, "groups_lanes": 12, "chart_marks": 120},
}

SIZE_BUDGET = {
    "doc-inline": "compact",
    "social-square": "compact",
    "doc-wide": "standard",
    "slide-16x9": "standard",
    "slide-4x3": "standard",
    "social-og": "standard",
    "print-a4-landscape": "wide",
    "print-letter-landscape": "wide",
}

VIETNAMESE_MARKED_RE = re.compile(
    "[ăâđêôơưĂÂĐÊÔƠƯ]|"
    "[àáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]",
    re.IGNORECASE,
)
ENGLISH_SIGNAL_RE = re.compile(
    r"\b(?:create|diagram|show|from|with|and|the|of|to|for|process|system)\b",
    re.IGNORECASE,
)


class CoreError(Exception):
    """A stable, user-safe core failure."""

    def __init__(
        self,
        code: str,
        stage: str,
        message: str,
        *,
        field: str | None = None,
        status: str = "invalid",
        question: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage
        self.message = message
        self.field = field
        self.status = status
        self.question = question

    def issue(self) -> dict[str, Any]:
        issue: dict[str, Any] = {
            "code": self.code,
            "stage": self.stage,
            "message": self.message,
        }
        if self.field is not None:
            issue["field"] = self.field
        if self.question is not None:
            issue["question"] = self.question
        return issue


def canonical_json(value: Any) -> str:
    """Return deterministic JSON without changing semantic array order."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def semantic_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _fail(
    code: str,
    stage: str,
    message: str,
    *,
    field: str | None = None,
    status: str = "invalid",
    question: str | None = None,
) -> None:
    raise CoreError(
        code,
        stage,
        message,
        field=field,
        status=status,
        question=question,
    )


def _require_mapping(value: Any, field: str, stage: str = "request") -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail("invalid-object", stage, "Expected an object.", field=field)
    return value


def _require_list(value: Any, field: str, stage: str = "ir") -> list[Any]:
    if not isinstance(value, list):
        _fail("invalid-array", stage, "Expected an array.", field=field)
    return value


def _require_string(
    value: Any,
    field: str,
    *,
    stage: str = "request",
    minimum: int = 1,
    maximum: int | None = None,
) -> str:
    if not isinstance(value, str) or len(value) < minimum:
        _fail("invalid-string", stage, "Expected a non-empty string.", field=field)
    if maximum is not None and len(value) > maximum:
        _fail("value-over-limit", stage, "String exceeds the approved limit.", field=field)
    return value


def _require_enum(value: Any, allowed: Sequence[str], field: str, stage: str = "request") -> str:
    if value not in allowed:
        _fail(
            "invalid-enum",
            stage,
            "Value is outside the approved contract.",
            field=field,
        )
    return str(value)


def _reject_unknown(mapping: Mapping[str, Any], allowed: Iterable[str], field: str, stage: str) -> None:
    extras = sorted(set(mapping) - set(allowed))
    if extras:
        _fail(
            "unknown-field",
            stage,
            f"Unknown field: {extras[0]}.",
            field=f"{field}.{extras[0]}" if field else extras[0],
        )


def normalize_request(raw_request: Mapping[str, Any]) -> dict[str, Any]:
    """Apply approved defaults and strictly validate the trusted request envelope."""

    request = dict(_require_mapping(raw_request, "request"))
    _reject_unknown(request, REQUEST_FIELDS, "", "request")

    if "instruction" not in request:
        _fail("missing-field", "request", "Missing required field.", field="instruction")
    if "source" not in request:
        _fail("missing-field", "request", "Missing required field.", field="source")

    normalized = copy.deepcopy(REQUEST_DEFAULTS)
    normalized.update(copy.deepcopy(request))

    _require_enum(normalized["schema_version"], (SCHEMA_VERSION,), "schema_version")
    _require_string(normalized["instruction"], "instruction", maximum=20_000)
    _require_enum(
        normalized["diagram_type"],
        ("auto",) + CANONICAL_TYPES,
        "diagram_type",
    )
    variant_ids = _require_list(normalized["variant_ids"], "variant_ids", "request")
    if (
        len(variant_ids) > 1
        or len(variant_ids) != len(set(variant_ids))
        or any(item not in NEW_VARIANT_PARENTS for item in variant_ids)
    ):
        _fail(
            "invalid-variant-id",
            "request",
            "Request variant_ids accepts at most one approved 1.5 capability.",
            field="variant_ids",
        )
    if variant_ids and normalized["diagram_type"] not in {"auto", NEW_VARIANT_PARENTS[variant_ids[0]]}:
        _fail(
            "variant-parent-mismatch",
            "request",
            "The requested capability is incompatible with the requested canonical type.",
            field="variant_ids",
        )
    normalized["variant_ids"] = list(variant_ids)
    _require_enum(normalized["size"], SIZES, "size")
    _require_enum(normalized["detail"], DETAILS, "detail")
    _require_enum(normalized["audience"], AUDIENCES, "audience")
    _require_enum(normalized["visual_mode"], VISUAL_MODES, "visual_mode")
    _require_enum(normalized["format"], FORMATS, "format")
    _require_enum(normalized["motion"], MOTIONS, "motion")

    language = _require_mapping(normalized["language"], "language")
    _reject_unknown(language, ("mode", "tag"), "language", "request")
    mode = _require_enum(language.get("mode"), ("auto", "explicit"), "language.mode")
    if mode == "explicit":
        tag = _require_string(language.get("tag"), "language.tag")
        if not LANG_RE.fullmatch(tag):
            _fail("invalid-language-tag", "request", "Invalid BCP 47 language tag.", field="language.tag")
    elif "tag" in language:
        _fail(
            "conflicting-field",
            "request",
            "Automatic language mode cannot include a tag.",
            field="language.tag",
        )

    source = _require_mapping(normalized["source"], "source")
    source_allowed = (
        "kind",
        "content",
        "attachment_ref",
        "media_type",
        "page_selection",
        "block_selection",
    )
    _reject_unknown(source, source_allowed, "source", "request")
    kind = _require_enum(source.get("kind"), SOURCE_KINDS, "source.kind")
    has_content = "content" in source
    has_attachment = "attachment_ref" in source
    if has_content == has_attachment:
        _fail(
            "conflicting-source-selector",
            "request",
            "Provide exactly one of source.content or source.attachment_ref.",
            field="source",
        )
    if has_content:
        content = _require_string(source["content"], "source.content", minimum=0, maximum=5_000_000)
        byte_limit = 20 * 1024 * 1024 if kind == "drawio" else 5 * 1024 * 1024
        if len(content.encode("utf-8")) > byte_limit:
            _fail("source-over-limit", "request", "Source exceeds the approved byte limit.", field="source.content")
    else:
        _require_string(source["attachment_ref"], "source.attachment_ref")

    for selection_name in ("page_selection", "block_selection"):
        if selection_name not in source:
            continue
        selection = source[selection_name]
        if selection == "all":
            continue
        values = _require_list(selection, f"source.{selection_name}", "request")
        if not values or len(values) != len(set(values)):
            _fail("invalid-selection", "request", "Selection must contain unique positive integers.", field=f"source.{selection_name}")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in values):
            _fail("invalid-selection", "request", "Selection must contain unique positive integers.", field=f"source.{selection_name}")

    normalized["language"] = dict(language)
    normalized["source"] = dict(source)
    return normalized


def detect_language(normalized_request: Mapping[str, Any]) -> str:
    """Resolve language from the trusted instruction without consulting source data."""

    language = normalized_request["language"]
    if language["mode"] == "explicit":
        return str(language["tag"])

    instruction = unicodedata.normalize("NFC", str(normalized_request["instruction"]))
    if VIETNAMESE_MARKED_RE.search(instruction):
        return "vi"
    if instruction.isascii() and ENGLISH_SIGNAL_RE.search(instruction):
        return "en"
    _fail(
        "language-ambiguous",
        "language",
        "The trusted instruction does not provide deterministic language evidence.",
        field="language",
        status="needs-clarification",
        question="Which output language should the diagram use?",
    )


def _validate_route_candidates(parsed: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = _require_list(parsed.get("route_candidates"), "route_candidates", "route")
    if not candidates:
        _fail(
            "route-evidence-missing",
            "route",
            "No semantic type candidate was supplied.",
            field="route_candidates",
            status="needs-clarification",
            question="Which relationship should the diagram primarily communicate?",
        )

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    allowed = {
        "type",
        "confidence",
        "evidence",
        "compatible",
        "viable",
        "materially_distinct",
        "rejection_reason",
    }
    for index, raw in enumerate(candidates):
        candidate = dict(_require_mapping(raw, f"route_candidates[{index}]", "route"))
        _reject_unknown(candidate, allowed, f"route_candidates[{index}]", "route")
        diagram_type = _require_enum(candidate.get("type"), CANONICAL_TYPES, f"route_candidates[{index}].type", "route")
        if diagram_type in seen:
            _fail("duplicate-route-candidate", "route", "Route candidate types must be unique.", field=f"route_candidates[{index}].type")
        seen.add(diagram_type)
        confidence = _require_enum(candidate.get("confidence"), CONFIDENCE, f"route_candidates[{index}].confidence", "route")
        evidence = _require_list(candidate.get("evidence"), f"route_candidates[{index}].evidence", "route")
        if not evidence or any(not isinstance(item, str) or not item for item in evidence):
            _fail("route-evidence-missing", "route", "Each candidate needs semantic evidence.", field=f"route_candidates[{index}].evidence")
        for boolean_field, default in (
            ("compatible", True),
            ("viable", True),
            ("materially_distinct", False),
        ):
            value = candidate.get(boolean_field, default)
            if not isinstance(value, bool):
                _fail("invalid-boolean", "route", "Expected a boolean.", field=f"route_candidates[{index}].{boolean_field}")
            candidate[boolean_field] = value
        if index > 0:
            _require_string(candidate.get("rejection_reason"), f"route_candidates[{index}].rejection_reason", stage="route")
        candidate["type"] = diagram_type
        candidate["confidence"] = confidence
        candidate["evidence"] = list(evidence)
        normalized.append(candidate)
    return normalized


def select_type(normalized_request: Mapping[str, Any], parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Select one canonical type using supplied semantic evidence only."""

    candidates = _validate_route_candidates(parsed)
    requested = normalized_request["diagram_type"]

    if requested != "auto":
        winner = next((candidate for candidate in candidates if candidate["type"] == requested), None)
        if winner is None or not winner["compatible"]:
            _fail(
                "manual-type-mismatch",
                "route",
                "The requested type is not compatible with the supplied semantic model.",
                field="diagram_type",
                status="needs-clarification",
                question="Should the diagram type or the intended source relationship be changed?",
            )
        evidence = [f"request:manual diagram_type={requested}"] + winner["evidence"]
        alternatives = []
        for candidate in candidates:
            if candidate is winner:
                continue
            if "rejection_reason" not in candidate:
                _fail(
                    "route-rejection-missing",
                    "route",
                    "Every rejected manual-route alternative needs a supplied reason.",
                    field="route_candidates",
                )
            alternatives.append(
                {"type": candidate["type"], "rejection_reason": candidate["rejection_reason"]}
            )
        return {
            "type": requested,
            "mode": "manual",
            "confidence": winner["confidence"],
            "evidence": evidence,
            "alternatives": alternatives,
            "assumption": None,
        }

    winner = candidates[0]
    if winner["confidence"] == "low":
        _fail(
            "route-confidence-low",
            "route",
            "Type evidence is too weak to select without changing meaning.",
            status="needs-clarification",
            question="Which relationship should the diagram primarily communicate?",
        )

    material_alternative = next(
        (
            candidate
            for candidate in candidates[1:]
            if candidate["viable"] and candidate["materially_distinct"]
        ),
        None,
    )
    if material_alternative is not None:
        _fail(
            "route-material-ambiguity",
            "route",
            "Two viable canonical types encode materially different relationships.",
            status="needs-clarification",
            question=f"Should the primary story use {winner['type']} or {material_alternative['type']} semantics?",
        )

    alternatives = [
        {"type": candidate["type"], "rejection_reason": candidate["rejection_reason"]}
        for candidate in candidates[1:]
    ]
    assumption = None
    if winner["confidence"] == "medium":
        assumption = "Selected the leading candidate because remaining viable alternatives preserve the declared relations."
    return {
        "type": winner["type"],
        "mode": "auto",
        "confidence": winner["confidence"],
        "evidence": winner["evidence"],
        "alternatives": alternatives,
        "assumption": assumption,
    }


def _validate_parsed_shape(parsed_model: Mapping[str, Any]) -> dict[str, Any]:
    parsed = dict(_require_mapping(parsed_model, "parsed_model", "normalizer"))
    _reject_unknown(parsed, PARSED_FIELDS, "parsed_model", "normalizer")
    required = PARSED_FIELDS - {"variant_ids"}
    missing = sorted(required - set(parsed))
    if missing:
        _fail("missing-field", "normalizer", "Parsed semantic model is incomplete.", field=f"parsed_model.{missing[0]}")
    _require_string(parsed["title"], "parsed_model.title", stage="normalizer")
    for collection in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations", "source_items"):
        _require_list(parsed[collection], f"parsed_model.{collection}", "normalizer")
    _require_mapping(parsed["fidelity"], "parsed_model.fidelity", "normalizer")
    _require_mapping(parsed["accessibility"], "parsed_model.accessibility", "normalizer")
    variants = parsed.get("variant_ids", [])
    _require_list(variants, "parsed_model.variant_ids", "normalizer")
    if len(variants) != len(set(variants)) or any(not isinstance(item, str) or not CAP_RE.fullmatch(item) for item in variants):
        _fail("invalid-variant-id", "normalizer", "Variant IDs must be unique approved CAP identifiers.", field="parsed_model.variant_ids")
    parsed["variant_ids"] = list(variants)
    return parsed


def build_ir(normalized_request: Mapping[str, Any], parsed_model: Mapping[str, Any]) -> dict[str, Any]:
    """Build a schema-shaped common IR and enforce common semantic invariants."""

    request = normalize_request(normalized_request)
    parsed = _validate_parsed_shape(parsed_model)
    language = detect_language(request)
    decision = select_type(request, parsed)

    request_variants = request["variant_ids"]
    parsed_variants = parsed["variant_ids"]
    if request_variants and parsed_variants and request_variants != parsed_variants:
        _fail(
            "variant-selection-conflict",
            "normalizer",
            "Parsed variants conflict with the explicit request capability.",
            field="parsed_model.variant_ids",
        )
    selected_variants = request_variants or parsed_variants

    ir = {
        "schema_version": SCHEMA_VERSION,
        "request_id": f"req-{semantic_hash(request)[:20]}",
        "diagram": {
            "type": decision["type"],
            "variant_ids": copy.deepcopy(selected_variants),
            "language": language,
            "title": parsed["title"],
            "detail": request["detail"],
            "audience": request["audience"],
        },
        "selection": {
            "mode": decision["mode"],
            "confidence": decision["confidence"],
            "evidence": copy.deepcopy(decision["evidence"]),
            "alternatives": copy.deepcopy(decision["alternatives"]),
            "assumption": decision["assumption"],
        },
        "nodes": copy.deepcopy(parsed["nodes"]),
        "edges": copy.deepcopy(parsed["edges"]),
        "groups": copy.deepcopy(parsed["groups"]),
        "lanes": copy.deepcopy(parsed["lanes"]),
        "series": copy.deepcopy(parsed["series"]),
        "axes": copy.deepcopy(parsed["axes"]),
        "annotations": copy.deepcopy(parsed["annotations"]),
        "source_items": copy.deepcopy(parsed["source_items"]),
        "fidelity": copy.deepcopy(parsed["fidelity"]),
        "accessibility": copy.deepcopy(parsed["accessibility"]),
    }
    validate_common_ir(ir)
    return ir


COLLECTION_SPECS: dict[str, tuple[set[str], set[str]]] = {
    "nodes": (
        {"id", "role", "label", "source_refs"},
        {
            "id", "role", "label", "secondary_label", "state", "value", "unit",
            "parent_group_id", "start", "end", "members", "placement", "work",
            "journey", "strategy", "story", "source_refs",
        },
    ),
    "edges": (
        {"id", "source", "target", "kind", "directed", "source_refs"},
        {
            "id", "source", "target", "kind", "directed", "label", "order", "guard",
            "amount", "unit", "relation_kind", "source_member", "target_member",
            "source_multiplicity", "target_multiplicity", "source_refs",
        },
    ),
    "groups": (
        {"id", "label", "member_ids", "source_refs"},
        {
            "id", "label", "member_ids", "parent_group_id", "declared_total", "unit",
            "wip_limit", "release_slice", "cause_category", "source_refs",
        },
    ),
    "lanes": (
        {"id", "label", "owner", "member_ids", "order", "source_refs"},
        {"id", "label", "owner", "member_ids", "order", "parent_lane_id", "source_refs"},
    ),
    "series": (
        {"id", "label", "unit", "data", "source_refs"},
        {"id", "label", "unit", "distribution", "data", "source_refs"},
    ),
    "axes": (
        {"id", "dimension", "scale", "label", "source_refs"},
        {"id", "dimension", "scale", "label", "unit", "domain_min", "domain_max", "source_refs"},
    ),
    "annotations": (
        {"id", "text", "target_ids", "source_refs"},
        {"id", "text", "target_ids", "source_refs"},
    ),
}


def _validate_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        _fail("invalid-id", "ir", "ID must use lowercase letters, digits, and single hyphens.", field=field)
    return value


def _validate_string_list(value: Any, field: str, *, minimum: int = 0) -> list[str]:
    values = _require_list(value, field)
    if len(values) < minimum or len(values) != len(set(values)):
        _fail("invalid-id-list", "ir", "Expected unique IDs.", field=field)
    for index, item in enumerate(values):
        _validate_id(item, f"{field}[{index}]")
    return values


def _validate_datetime(value: Any, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        _fail("invalid-date-time", "ir", "Expected an ISO 8601 date-time string or null.", field=field)
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("invalid-date-time", "ir", "Expected an ISO 8601 date-time string or null.", field=field)


def _validate_finite(value: Any, field: str, *, allow_string: bool = False, allow_null: bool = True) -> None:
    if value is None and allow_null:
        return
    if isinstance(value, bool):
        _fail("invalid-number", "ir", "Boolean is not a quantitative value.", field=field)
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            _fail("non-finite-number", "ir", "Non-finite numbers must be represented as missing data.", field=field)
        return
    if allow_string and isinstance(value, str):
        return
    _fail("invalid-number", "ir", "Expected a finite number.", field=field)


def _validate_nullable_string(value: Any, field: str) -> None:
    if value is not None:
        _require_string(value, field, stage="ir")


def _validate_non_negative_int(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail("invalid-order", "ir", "Expected a non-negative integer.", field=field)


def _validate_positive_int(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail("invalid-positive-integer", "ir", "Expected a positive integer.", field=field)


def _check_cycle(items: Sequence[Mapping[str, Any]], parent_field: str, label: str) -> None:
    parents = {item["id"]: item.get(parent_field) for item in items}
    for start in parents:
        seen: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in seen:
                _fail("membership-cycle", "ir", f"{label} parent relationship is cyclic.", field=parent_field)
            seen.add(current)
            parent = parents.get(current)
            if parent is not None and parent not in parents:
                _fail("dangling-reference", "ir", f"{label} parent does not exist.", field=parent_field)
            current = parent


def validate_common_ir(ir_value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the approved common IR shape and P-04 semantic invariants."""

    ir = dict(_require_mapping(ir_value, "ir", "ir"))
    _reject_unknown(ir, IR_FIELDS, "ir", "ir")
    missing = [field for field in IR_FIELDS if field not in ir]
    if missing:
        _fail("missing-field", "ir", "IR is incomplete.", field=f"ir.{missing[0]}")
    _require_enum(ir["schema_version"], (SCHEMA_VERSION,), "ir.schema_version", "ir")
    _validate_id(ir["request_id"], "ir.request_id")

    diagram = dict(_require_mapping(ir["diagram"], "ir.diagram", "ir"))
    diagram_required = {"type", "language", "title", "detail", "audience"}
    diagram_allowed = diagram_required | {"variant_ids"}
    _reject_unknown(diagram, diagram_allowed, "ir.diagram", "ir")
    if not diagram_required <= set(diagram):
        _fail("missing-field", "ir", "Diagram metadata is incomplete.", field="ir.diagram")
    _require_enum(diagram["type"], CANONICAL_TYPES, "ir.diagram.type", "ir")
    _require_string(diagram["language"], "ir.diagram.language", stage="ir", minimum=2)
    _require_string(diagram["title"], "ir.diagram.title", stage="ir")
    _require_enum(diagram["detail"], DETAILS, "ir.diagram.detail", "ir")
    _require_enum(diagram["audience"], AUDIENCES, "ir.diagram.audience", "ir")
    variant_ids = _require_list(diagram.get("variant_ids", []), "ir.diagram.variant_ids")
    if len(variant_ids) != len(set(variant_ids)) or any(not isinstance(item, str) or not CAP_RE.fullmatch(item) for item in variant_ids):
        _fail("invalid-variant-id", "ir", "Variant IDs must be unique approved CAP identifiers.", field="ir.diagram.variant_ids")

    selection = dict(_require_mapping(ir["selection"], "ir.selection", "ir"))
    selection_required = {"mode", "confidence", "evidence", "alternatives"}
    selection_allowed = selection_required | {"assumption"}
    _reject_unknown(selection, selection_allowed, "ir.selection", "ir")
    if not selection_required <= set(selection):
        _fail("missing-field", "ir", "Selection record is incomplete.", field="ir.selection")
    _require_enum(selection["mode"], ("auto", "manual"), "ir.selection.mode", "ir")
    _require_enum(selection["confidence"], CONFIDENCE, "ir.selection.confidence", "ir")
    evidence = _require_list(selection["evidence"], "ir.selection.evidence")
    if not evidence or any(not isinstance(item, str) or not item for item in evidence):
        _fail("route-evidence-missing", "ir", "Selection evidence cannot be empty.", field="ir.selection.evidence")
    alternatives = _require_list(selection["alternatives"], "ir.selection.alternatives")
    for index, alternative_value in enumerate(alternatives):
        alternative = dict(_require_mapping(alternative_value, f"ir.selection.alternatives[{index}]", "ir"))
        _reject_unknown(alternative, ("type", "rejection_reason"), f"ir.selection.alternatives[{index}]", "ir")
        if set(alternative) != {"type", "rejection_reason"}:
            _fail("missing-field", "ir", "Alternative record is incomplete.", field=f"ir.selection.alternatives[{index}]")
        _require_enum(alternative["type"], CANONICAL_TYPES, f"ir.selection.alternatives[{index}].type", "ir")
        _require_string(alternative["rejection_reason"], f"ir.selection.alternatives[{index}].rejection_reason", stage="ir")

    all_ids: dict[str, str] = {ir["request_id"]: "request_id"}
    collection_by_id: dict[str, str] = {}
    source_refs_to_check: list[tuple[str, list[str]]] = []
    entities: dict[str, list[dict[str, Any]]] = {}
    member_owner: dict[str, str] = {}
    member_kind: dict[str, str] = {}
    index_members: list[tuple[str, dict[str, Any]]] = []

    datum_count = 0
    distribution_sample_count = 0
    for collection, (required, allowed) in COLLECTION_SPECS.items():
        values = _require_list(ir[collection], f"ir.{collection}")
        normalized_items: list[dict[str, Any]] = []
        for index, raw_item in enumerate(values):
            item = dict(_require_mapping(raw_item, f"ir.{collection}[{index}]", "ir"))
            _reject_unknown(item, allowed, f"ir.{collection}[{index}]", "ir")
            if not required <= set(item):
                _fail("missing-field", "ir", "IR item is incomplete.", field=f"ir.{collection}[{index}]")
            item_id = _validate_id(item["id"], f"ir.{collection}[{index}].id")
            if item_id in all_ids:
                _fail("duplicate-id", "ir", "All IR and source IDs must be globally unique.", field=f"ir.{collection}[{index}].id")
            all_ids[item_id] = collection
            collection_by_id[item_id] = collection
            refs = _validate_string_list(item["source_refs"], f"ir.{collection}[{index}].source_refs", minimum=1)
            source_refs_to_check.append((f"ir.{collection}[{index}].source_refs", refs))
            normalized_items.append(item)
        entities[collection] = normalized_items

    for index, node in enumerate(entities["nodes"]):
        _require_string(node["role"], f"ir.nodes[{index}].role", stage="ir")
        _require_string(node["label"], f"ir.nodes[{index}].label", stage="ir")
        if "value" in node:
            _validate_finite(node["value"], f"ir.nodes[{index}].value", allow_string=True)
        if "unit" in node:
            _validate_nullable_string(node["unit"], f"ir.nodes[{index}].unit")
        if node.get("parent_group_id") is not None:
            _validate_id(node["parent_group_id"], f"ir.nodes[{index}].parent_group_id")
        _validate_datetime(node.get("start"), f"ir.nodes[{index}].start")
        _validate_datetime(node.get("end"), f"ir.nodes[{index}].end")
        if "members" in node:
            members = _require_list(node["members"], f"ir.nodes[{index}].members")
            for member_index, raw_member in enumerate(members):
                field = f"ir.nodes[{index}].members[{member_index}]"
                member = dict(_require_mapping(raw_member, field, "ir"))
                required = {"id", "kind", "name", "source_refs"}
                allowed = required | {
                    "data_type", "visibility", "signature", "constraints",
                    "indexed_member_ids", "index_unique",
                }
                _reject_unknown(member, allowed, field, "ir")
                if not required <= set(member):
                    _fail("missing-field", "ir", "Member is incomplete.", field=field)
                member_id = _validate_id(member["id"], f"{field}.id")
                if member_id in all_ids:
                    _fail("duplicate-id", "ir", "All IR, member, and source IDs must be globally unique.", field=f"{field}.id")
                all_ids[member_id] = "members"
                collection_by_id[member_id] = "members"
                member_owner[member_id] = node["id"]
                _require_enum(member["kind"], ("attribute", "operation", "column", "index"), f"{field}.kind", "ir")
                member_kind[member_id] = member["kind"]
                _require_string(member["name"], f"{field}.name", stage="ir")
                for string_field in ("data_type", "signature"):
                    if string_field in member:
                        _validate_nullable_string(member[string_field], f"{field}.{string_field}")
                if "visibility" in member:
                    _require_enum(member["visibility"], ("public", "protected", "private", "package", "unspecified"), f"{field}.visibility", "ir")
                if "constraints" in member:
                    constraints = _require_list(member["constraints"], f"{field}.constraints")
                    if len(constraints) != len(set(constraints)) or any(not isinstance(value, str) or not value for value in constraints):
                        _fail("invalid-constraints", "ir", "Constraints must be unique non-empty strings.", field=f"{field}.constraints")
                has_index_fields = "indexed_member_ids" in member or "index_unique" in member
                if member["kind"] == "index":
                    if not {"indexed_member_ids", "index_unique"} <= set(member):
                        _fail("index-structure-missing", "ir", "Index members require ordered column IDs and uniqueness.", field=field)
                    _validate_string_list(member["indexed_member_ids"], f"{field}.indexed_member_ids", minimum=1)
                    if not isinstance(member["index_unique"], bool):
                        _fail("invalid-boolean", "ir", "Expected a boolean.", field=f"{field}.index_unique")
                    index_members.append((node["id"], member))
                elif has_index_fields:
                    _fail("index-fields-on-non-index", "ir", "Only index members may declare index fields.", field=field)
                member_refs = _validate_string_list(member["source_refs"], f"{field}.source_refs", minimum=1)
                source_refs_to_check.append((f"{field}.source_refs", member_refs))
        if "placement" in node:
            field = f"ir.nodes[{index}].placement"
            placement = dict(_require_mapping(node["placement"], field, "ir"))
            allowed = {"zone", "host", "artifact", "replicas", "ports"}
            _reject_unknown(placement, allowed, field, "ir")
            if not placement:
                _fail("placement-empty", "ir", "Placement needs at least one supplied field.", field=field)
            for string_field in ("zone", "host", "artifact"):
                if string_field in placement:
                    _require_string(placement[string_field], f"{field}.{string_field}", stage="ir")
            if "replicas" in placement:
                _validate_positive_int(placement["replicas"], f"{field}.replicas")
            if "ports" in placement:
                ports = _require_list(placement["ports"], f"{field}.ports")
                if len(ports) != len(set(ports)) or any(not isinstance(value, str) or not value for value in ports):
                    _fail("invalid-ports", "ir", "Ports must be unique non-empty strings.", field=f"{field}.ports")
        if "work" in node:
            field = f"ir.nodes[{index}].work"
            work = dict(_require_mapping(node["work"], field, "ir"))
            required = {"column_order", "item_order", "blocked"}
            _reject_unknown(work, required | {"wip_limit"}, field, "ir")
            if not required <= set(work):
                _fail("missing-field", "ir", "Work metadata is incomplete.", field=field)
            _validate_non_negative_int(work["column_order"], f"{field}.column_order")
            _validate_non_negative_int(work["item_order"], f"{field}.item_order")
            if not isinstance(work["blocked"], bool):
                _fail("invalid-boolean", "ir", "Expected a boolean.", field=f"{field}.blocked")
            if work.get("wip_limit") is not None:
                _validate_positive_int(work["wip_limit"], f"{field}.wip_limit")
        if "journey" in node:
            field = f"ir.nodes[{index}].journey"
            journey = dict(_require_mapping(node["journey"], field, "ir"))
            required = {"stage_order", "action", "touchpoint"}
            _reject_unknown(journey, required | {"sentiment"}, field, "ir")
            if not required <= set(journey):
                _fail("missing-field", "ir", "Journey metadata is incomplete.", field=field)
            _validate_non_negative_int(journey["stage_order"], f"{field}.stage_order")
            _require_string(journey["action"], f"{field}.action", stage="ir")
            _require_string(journey["touchpoint"], f"{field}.touchpoint", stage="ir")
            if journey.get("sentiment") is not None:
                _validate_finite(journey["sentiment"], f"{field}.sentiment", allow_null=False)
                if not -1 <= journey["sentiment"] <= 1:
                    _fail("sentiment-out-of-domain", "ir", "Sentiment must be within -1..1.", field=f"{field}.sentiment")
        if "strategy" in node:
            field = f"ir.nodes[{index}].strategy"
            strategy = dict(_require_mapping(node["strategy"], field, "ir"))
            required = {"evolution", "value_chain_position"}
            _reject_unknown(strategy, required, field, "ir")
            if set(strategy) != required:
                _fail("missing-field", "ir", "Strategy coordinates are incomplete.", field=field)
            for coordinate in required:
                _validate_finite(strategy[coordinate], f"{field}.{coordinate}", allow_null=False)
                if not 0 <= strategy[coordinate] <= 1:
                    _fail("strategy-coordinate-out-of-domain", "ir", "Strategy coordinates must be within 0..1.", field=f"{field}.{coordinate}")
        if "story" in node:
            field = f"ir.nodes[{index}].story"
            story = dict(_require_mapping(node["story"], field, "ir"))
            required = {"backbone_order", "story_order", "release_slice", "cut_status"}
            _reject_unknown(story, required, field, "ir")
            if set(story) != required:
                _fail("missing-field", "ir", "Story metadata is incomplete.", field=field)
            _validate_non_negative_int(story["backbone_order"], f"{field}.backbone_order")
            _validate_non_negative_int(story["story_order"], f"{field}.story_order")
            _validate_nullable_string(story["release_slice"], f"{field}.release_slice")
            _require_enum(story["cut_status"], ("above", "below", "at", "unassigned"), f"{field}.cut_status", "ir")
            if (story["release_slice"] is None) != (story["cut_status"] == "unassigned"):
                _fail("story-unassigned-pairing", "ir", "Unassigned cut status and null release slice must occur together.", field=field)

    for index, edge in enumerate(entities["edges"]):
        _validate_id(edge["source"], f"ir.edges[{index}].source")
        _validate_id(edge["target"], f"ir.edges[{index}].target")
        _require_string(edge["kind"], f"ir.edges[{index}].kind", stage="ir")
        if not isinstance(edge["directed"], bool):
            _fail("invalid-boolean", "ir", "Expected a boolean.", field=f"ir.edges[{index}].directed")
        if "order" in edge and (isinstance(edge["order"], bool) or not isinstance(edge["order"], int) or edge["order"] < 0):
            _fail("invalid-order", "ir", "Order must be a non-negative integer.", field=f"ir.edges[{index}].order")
        if "amount" in edge:
            _validate_finite(edge["amount"], f"ir.edges[{index}].amount")
        if "unit" in edge:
            _validate_nullable_string(edge["unit"], f"ir.edges[{index}].unit")
        if "relation_kind" in edge:
            _require_enum(
                edge["relation_kind"],
                ("association", "aggregation", "composition", "inheritance", "realization", "dependency", "foreign-key", "runtime", "flow", "other"),
                f"ir.edges[{index}].relation_kind",
                "ir",
            )
        for member_field in ("source_member", "target_member"):
            if edge.get(member_field) is not None:
                _validate_id(edge[member_field], f"ir.edges[{index}].{member_field}")
        for multiplicity_field in ("source_multiplicity", "target_multiplicity"):
            if multiplicity_field in edge:
                _validate_nullable_string(edge[multiplicity_field], f"ir.edges[{index}].{multiplicity_field}")

    for index, group in enumerate(entities["groups"]):
        _require_string(group["label"], f"ir.groups[{index}].label", stage="ir")
        _validate_string_list(group["member_ids"], f"ir.groups[{index}].member_ids", minimum=1)
        if group.get("parent_group_id") is not None:
            _validate_id(group["parent_group_id"], f"ir.groups[{index}].parent_group_id")
        if "declared_total" in group:
            _validate_finite(group["declared_total"], f"ir.groups[{index}].declared_total")
        if "unit" in group:
            _validate_nullable_string(group["unit"], f"ir.groups[{index}].unit")
        if group.get("wip_limit") is not None:
            _validate_positive_int(group["wip_limit"], f"ir.groups[{index}].wip_limit")
        for string_field in ("release_slice", "cause_category"):
            if string_field in group:
                _validate_nullable_string(group[string_field], f"ir.groups[{index}].{string_field}")

    for index, lane in enumerate(entities["lanes"]):
        _require_string(lane["label"], f"ir.lanes[{index}].label", stage="ir")
        _require_string(lane["owner"], f"ir.lanes[{index}].owner", stage="ir")
        _validate_string_list(lane["member_ids"], f"ir.lanes[{index}].member_ids")
        if isinstance(lane["order"], bool) or not isinstance(lane["order"], int) or lane["order"] < 0:
            _fail("invalid-order", "ir", "Order must be a non-negative integer.", field=f"ir.lanes[{index}].order")
        if lane.get("parent_lane_id") is not None:
            _validate_id(lane["parent_lane_id"], f"ir.lanes[{index}].parent_lane_id")

    for index, series in enumerate(entities["series"]):
        _require_string(series["label"], f"ir.series[{index}].label", stage="ir")
        _validate_nullable_string(series["unit"], f"ir.series[{index}].unit")
        if "distribution" in series:
            field = f"ir.series[{index}].distribution"
            distribution = dict(_require_mapping(series["distribution"], field, "ir"))
            required = {
                "method", "domain_min", "domain_max", "bin_count", "bin_edges",
                "bandwidth", "amplitude_normalization", "shared_domain", "shared_bins",
            }
            _reject_unknown(distribution, required, field, "ir")
            if set(distribution) != required:
                _fail("missing-field", "ir", "Distribution metadata is incomplete.", field=field)
            _require_enum(distribution["method"], ("histogram", "kde-gaussian"), f"{field}.method", "ir")
            _validate_finite(distribution["domain_min"], f"{field}.domain_min", allow_null=False)
            _validate_finite(distribution["domain_max"], f"{field}.domain_max", allow_null=False)
            _validate_positive_int(distribution["bin_count"], f"{field}.bin_count")
            if distribution["bin_count"] < 2:
                _fail("distribution-bin-count", "ir", "A distribution needs at least two bins.", field=f"{field}.bin_count")
            edges = _require_list(distribution["bin_edges"], f"{field}.bin_edges")
            if len(edges) < 3 or len(edges) != len(set(edges)):
                _fail("distribution-bin-edges", "ir", "Distribution bin edges must contain at least three unique values.", field=f"{field}.bin_edges")
            for edge_index, value in enumerate(edges):
                _validate_finite(value, f"{field}.bin_edges[{edge_index}]", allow_null=False)
            if distribution["method"] == "histogram":
                if distribution["bandwidth"] is not None:
                    _fail("distribution-bandwidth", "ir", "Histogram bandwidth must be null.", field=f"{field}.bandwidth")
            else:
                _validate_finite(distribution["bandwidth"], f"{field}.bandwidth", allow_null=False)
                if distribution["bandwidth"] <= 0:
                    _fail("distribution-bandwidth", "ir", "KDE bandwidth must be positive.", field=f"{field}.bandwidth")
            if distribution["amplitude_normalization"] != "global-max":
                _fail("distribution-normalization", "ir", "Ridgeline amplitude normalization must be global-max.", field=f"{field}.amplitude_normalization")
            if distribution["shared_domain"] is not True or distribution["shared_bins"] is not True:
                _fail("distribution-sharing", "ir", "Distribution domain and bins must be explicitly shared.", field=field)
        data = _require_list(series["data"], f"ir.series[{index}].data")
        for datum_index, raw_datum in enumerate(data):
            datum_count += 1
            datum = dict(_require_mapping(raw_datum, f"ir.series[{index}].data[{datum_index}]", "ir"))
            datum_required = {"id", "missing", "source_refs"}
            datum_allowed = datum_required | {
                "domain", "value", "x_value", "y_value", "size_value", "size_unit",
                "distribution_samples", "label",
            }
            _reject_unknown(datum, datum_allowed, f"ir.series[{index}].data[{datum_index}]", "ir")
            if not datum_required <= set(datum):
                _fail("missing-field", "ir", "Datum is incomplete.", field=f"ir.series[{index}].data[{datum_index}]")
            has_domain_value = {"domain", "value"} <= set(datum)
            has_xy = {"x_value", "y_value"} <= set(datum)
            has_distribution = "distribution_samples" in datum
            if not any((has_domain_value, has_xy, has_distribution)):
                _fail("datum-shape-invalid", "ir", "Datum needs domain/value, x/y, or distribution samples.", field=f"ir.series[{index}].data[{datum_index}]")
            datum_id = _validate_id(datum["id"], f"ir.series[{index}].data[{datum_index}].id")
            if datum_id in all_ids:
                _fail("duplicate-id", "ir", "All IR and source IDs must be globally unique.", field=f"ir.series[{index}].data[{datum_index}].id")
            all_ids[datum_id] = "data"
            collection_by_id[datum_id] = "data"
            if not isinstance(datum["missing"], bool):
                _fail("invalid-boolean", "ir", "Expected a boolean.", field=f"ir.series[{index}].data[{datum_index}].missing")
            missing_from_shape = False
            if has_domain_value:
                if not isinstance(datum["domain"], (str, int, float)) or isinstance(datum["domain"], bool):
                    _fail("invalid-domain", "ir", "Datum domain must be text or a finite number.", field=f"ir.series[{index}].data[{datum_index}].domain")
                if isinstance(datum["domain"], (int, float)):
                    _validate_finite(datum["domain"], f"ir.series[{index}].data[{datum_index}].domain", allow_null=False)
                _validate_finite(datum["value"], f"ir.series[{index}].data[{datum_index}].value")
                missing_from_shape = datum["value"] is None
            if has_xy:
                _validate_finite(datum["x_value"], f"ir.series[{index}].data[{datum_index}].x_value")
                _validate_finite(datum["y_value"], f"ir.series[{index}].data[{datum_index}].y_value")
                missing_from_shape = missing_from_shape or datum["x_value"] is None or datum["y_value"] is None
            if "size_value" in datum:
                _validate_finite(datum["size_value"], f"ir.series[{index}].data[{datum_index}].size_value")
            if "size_unit" in datum:
                _validate_nullable_string(datum["size_unit"], f"ir.series[{index}].data[{datum_index}].size_unit")
            if has_distribution:
                samples = _require_list(datum["distribution_samples"], f"ir.series[{index}].data[{datum_index}].distribution_samples")
                if not samples:
                    _fail("distribution-samples-empty", "ir", "Distribution samples cannot be empty.", field=f"ir.series[{index}].data[{datum_index}].distribution_samples")
                for sample_index, sample in enumerate(samples):
                    _validate_finite(sample, f"ir.series[{index}].data[{datum_index}].distribution_samples[{sample_index}]", allow_null=False)
                distribution_sample_count += len(samples)
            if datum["missing"] != missing_from_shape:
                _fail("missingness-mismatch", "ir", "Missing status must agree with null quantitative fields.", field=f"ir.series[{index}].data[{datum_index}]")
            datum_refs = _validate_string_list(datum["source_refs"], f"ir.series[{index}].data[{datum_index}].source_refs", minimum=1)
            source_refs_to_check.append((f"ir.series[{index}].data[{datum_index}].source_refs", datum_refs))

    for index, axis in enumerate(entities["axes"]):
        _require_enum(axis["dimension"], ("x", "y", "radial", "angular", "size"), f"ir.axes[{index}].dimension", "ir")
        _require_enum(axis["scale"], ("categorical", "linear", "time", "ordinal"), f"ir.axes[{index}].scale", "ir")
        if not isinstance(axis["label"], str):
            _fail("invalid-string", "ir", "Expected a string.", field=f"ir.axes[{index}].label")

    for index, annotation in enumerate(entities["annotations"]):
        _require_string(annotation["text"], f"ir.annotations[{index}].text", stage="ir")
        _validate_string_list(annotation["target_ids"], f"ir.annotations[{index}].target_ids", minimum=1)

    source_values = _require_list(ir["source_items"], "ir.source_items")
    source_ids: set[str] = set()
    for index, raw_source in enumerate(source_values):
        source = dict(_require_mapping(raw_source, f"ir.source_items[{index}]", "ir"))
        required = {"id", "source_kind", "locator", "content_class"}
        allowed = required | {"digest"}
        _reject_unknown(source, allowed, f"ir.source_items[{index}]", "ir")
        if not required <= set(source):
            _fail("missing-field", "ir", "Source item is incomplete.", field=f"ir.source_items[{index}]")
        source_id = _validate_id(source["id"], f"ir.source_items[{index}].id")
        if source_id in all_ids:
            _fail("duplicate-id", "ir", "All IR and source IDs must be globally unique.", field=f"ir.source_items[{index}].id")
        all_ids[source_id] = "source_items"
        source_ids.add(source_id)
        _require_enum(source["source_kind"], ("instruction",) + SOURCE_KINDS, f"ir.source_items[{index}].source_kind", "ir")
        _require_string(source["locator"], f"ir.source_items[{index}].locator", stage="ir")
        _require_enum(source["content_class"], CONTENT_CLASSES, f"ir.source_items[{index}].content_class", "ir")
        if "digest" in source and (not isinstance(source["digest"], str) or not DIGEST_RE.fullmatch(source["digest"])):
            _fail("invalid-digest", "ir", "Digest must be lowercase SHA-256 hex.", field=f"ir.source_items[{index}].digest")

    for field, refs in source_refs_to_check:
        if any(ref not in source_ids for ref in refs):
            _fail("dangling-source-reference", "ir", "A source reference does not exist.", field=field)

    endpoint_ids = {item_id for item_id, collection in collection_by_id.items() if collection in {"nodes", "groups", "lanes"}}
    for index, edge in enumerate(entities["edges"]):
        if edge["source"] not in endpoint_ids or edge["target"] not in endpoint_ids:
            _fail("dangling-endpoint", "ir", "Edge endpoint does not reference a node, group, or lane.", field=f"ir.edges[{index}]")
        for member_field in ("source_member", "target_member"):
            if edge.get(member_field) is not None and edge[member_field] not in member_owner:
                _fail("dangling-member-reference", "ir", "Edge member endpoint does not exist.", field=f"ir.edges[{index}].{member_field}")

    node_group_ids = {item_id for item_id, collection in collection_by_id.items() if collection in {"nodes", "groups"}}
    node_ids = {item_id for item_id, collection in collection_by_id.items() if collection == "nodes"}
    group_ids = {item_id for item_id, collection in collection_by_id.items() if collection == "groups"}
    for index, node in enumerate(entities["nodes"]):
        if node.get("parent_group_id") is not None and node["parent_group_id"] not in group_ids:
            _fail("dangling-reference", "ir", "Node parent group does not exist.", field=f"ir.nodes[{index}].parent_group_id")
    for index, group in enumerate(entities["groups"]):
        if any(member not in node_group_ids for member in group["member_ids"]):
            _fail("dangling-membership", "ir", "Group membership references an unsupported or missing item.", field=f"ir.groups[{index}].member_ids")
    for index, lane in enumerate(entities["lanes"]):
        if any(member not in node_ids for member in lane["member_ids"]):
            _fail("dangling-membership", "ir", "Lane membership must reference existing nodes.", field=f"ir.lanes[{index}].member_ids")
    for index, annotation in enumerate(entities["annotations"]):
        if any(target not in collection_by_id for target in annotation["target_ids"]):
            _fail("dangling-reference", "ir", "Annotation target does not exist.", field=f"ir.annotations[{index}].target_ids")

    for owner_id, index_member in index_members:
        for indexed_id in index_member["indexed_member_ids"]:
            if indexed_id not in member_owner:
                _fail("index-member-missing", "ir", "Index references a missing member.", field="ir.nodes.members.indexed_member_ids")
            if member_owner[indexed_id] != owner_id or member_kind[indexed_id] != "column":
                _fail("index-member-invalid", "ir", "Index references must be columns of the same node.", field="ir.nodes.members.indexed_member_ids")

    _check_cycle(entities["groups"], "parent_group_id", "Group")
    _check_cycle(entities["lanes"], "parent_lane_id", "Lane")

    for evidence_item in evidence:
        if evidence_item.startswith("request:"):
            continue
        match = re.match(r"^source:([a-z][a-z0-9]*(?:-[a-z0-9]+)*):", evidence_item)
        if match is None or match.group(1) not in source_ids:
            _fail("invalid-route-evidence", "ir", "Route evidence must identify request semantics or an existing source item.", field="ir.selection.evidence")

    fidelity = dict(_require_mapping(ir["fidelity"], "ir.fidelity", "ir"))
    fidelity_fields = {"kept", "merged", "dropped", "source_rot", "invented_count"}
    _reject_unknown(fidelity, fidelity_fields, "ir.fidelity", "ir")
    if set(fidelity) != fidelity_fields:
        _fail("missing-field", "ir", "Fidelity ledger is incomplete.", field="ir.fidelity")
    if fidelity["invented_count"] != 0 or isinstance(fidelity["invented_count"], bool):
        _fail("invented-content", "ir", "Invented content is a hard failure.", field="ir.fidelity.invented_count")

    disposition_by_source: dict[str, str] = {}
    semantic_ids = set(collection_by_id)
    for disposition in ("kept", "merged", "dropped", "source_rot"):
        entries = _require_list(fidelity[disposition], f"ir.fidelity.{disposition}")
        for index, raw_entry in enumerate(entries):
            entry = dict(_require_mapping(raw_entry, f"ir.fidelity.{disposition}[{index}]", "ir"))
            allowed = {"source_ids", "ir_ids", "reason"}
            required = {"source_ids", "reason"}
            _reject_unknown(entry, allowed, f"ir.fidelity.{disposition}[{index}]", "ir")
            if not required <= set(entry):
                _fail("missing-field", "ir", "Fidelity entry is incomplete.", field=f"ir.fidelity.{disposition}[{index}]")
            entry_source_ids = _validate_string_list(entry["source_ids"], f"ir.fidelity.{disposition}[{index}].source_ids", minimum=1)
            _require_string(entry["reason"], f"ir.fidelity.{disposition}[{index}].reason", stage="ir")
            for source_id in entry_source_ids:
                if source_id not in source_ids:
                    _fail("dangling-fidelity-source", "ir", "Fidelity source does not exist.", field=f"ir.fidelity.{disposition}[{index}].source_ids")
                if source_id in disposition_by_source:
                    _fail("duplicate-fidelity-disposition", "ir", "A source item has more than one fidelity disposition.", field=f"ir.fidelity.{disposition}[{index}].source_ids")
                disposition_by_source[source_id] = disposition
            if "ir_ids" in entry:
                entry_ir_ids = _validate_string_list(entry["ir_ids"], f"ir.fidelity.{disposition}[{index}].ir_ids")
                if any(ir_id not in semantic_ids for ir_id in entry_ir_ids):
                    _fail("dangling-fidelity-target", "ir", "Fidelity target does not exist.", field=f"ir.fidelity.{disposition}[{index}].ir_ids")
    if set(disposition_by_source) != source_ids:
        _fail("fidelity-reconciliation", "ir", "Every source item must have exactly one fidelity disposition.", field="ir.fidelity")

    accessibility = dict(_require_mapping(ir["accessibility"], "ir.accessibility", "ir"))
    accessibility_fields = {"name", "description", "reading_order", "data_representation_required"}
    _reject_unknown(accessibility, accessibility_fields, "ir.accessibility", "ir")
    if set(accessibility) != accessibility_fields:
        _fail("missing-field", "ir", "Accessibility record is incomplete.", field="ir.accessibility")
    _require_string(accessibility["name"], "ir.accessibility.name", stage="ir")
    _require_string(accessibility["description"], "ir.accessibility.description", stage="ir")
    reading_order = _validate_string_list(accessibility["reading_order"], "ir.accessibility.reading_order")
    if not isinstance(accessibility["data_representation_required"], bool):
        _fail("invalid-boolean", "ir", "Expected a boolean.", field="ir.accessibility.data_representation_required")
    material_ids = {item_id for item_id, collection in collection_by_id.items() if collection != "data"}
    if set(reading_order) != material_ids:
        _fail("reading-order-incomplete", "ir", "Reading order must cover every material common-IR element exactly once.", field="ir.accessibility.reading_order")

    semantic_item_count = (
        sum(len(entities[name]) for name in COLLECTION_SPECS)
        + datum_count
        + len(member_owner)
        + distribution_sample_count
    )
    if semantic_item_count > SECURITY_LIMITS["semantic_items"]:
        _fail("semantic-items-over-limit", "ir", "Semantic item count exceeds the approved security ceiling.", field="ir")
    if len(entities["nodes"]) > SECURITY_LIMITS["nodes"]:
        _fail("nodes-over-limit", "ir", "Node count exceeds the approved security ceiling.", field="ir.nodes")
    if len(entities["edges"]) > SECURITY_LIMITS["edges"]:
        _fail("edges-over-limit", "ir", "Edge count exceeds the approved security ceiling.", field="ir.edges")

    text_scalars = 0
    stack: list[Any] = [ir]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            scalar_count = len(value)
            text_scalars += scalar_count
            if scalar_count > SECURITY_LIMITS["label_scalars"]:
                _fail("text-over-limit", "ir", "A normalized text value exceeds the approved scalar limit.", field="ir")
        elif isinstance(value, Mapping):
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
    if text_scalars > SECURITY_LIMITS["normalized_text_scalars"]:
        _fail("normalized-text-over-limit", "ir", "Cumulative normalized text exceeds the approved security ceiling.", field="ir")

    return ir


def plan_complexity(ir: Mapping[str, Any], normalized_request: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the approved common presentation budget without doing layout."""

    counts = {
        "items": len(ir["nodes"]),
        "relations": len(ir["edges"]),
        "groups_lanes": len(ir["groups"]) + len(ir["lanes"]),
        "chart_marks": sum(len(series["data"]) for series in ir["series"]),
    }

    def fits(budget_name: str) -> bool:
        budget = COMPLEXITY_BUDGETS[budget_name]
        return all(counts[key] <= budget[key] for key in counts)

    requested_size = normalized_request["size"]
    if requested_size == "fit":
        selected_budget = next(
            (budget for budget in ("compact", "standard", "wide") if fits(budget)),
            None,
        )
        if selected_budget is None:
            return {
                "fits": False,
                "requested_size": requested_size,
                "budget": "wide",
                "counts": counts,
                "resolution": "split-or-narrow",
            }
        return {
            "fits": True,
            "requested_size": requested_size,
            "budget": selected_budget,
            "counts": counts,
            "resolution": "use-smallest-readable-canvas",
        }

    selected_budget = SIZE_BUDGET[requested_size]
    if fits(selected_budget):
        return {
            "fits": True,
            "requested_size": requested_size,
            "budget": selected_budget,
            "counts": counts,
            "resolution": "retain-requested-size",
        }
    larger = [
        budget
        for budget in ("compact", "standard", "wide")
        if list(COMPLEXITY_BUDGETS).index(budget) > list(COMPLEXITY_BUDGETS).index(selected_budget)
        and fits(budget)
    ]
    return {
        "fits": False,
        "requested_size": requested_size,
        "budget": selected_budget,
        "counts": counts,
        "resolution": "offer-larger-size" if larger else "split-or-narrow",
        "compatible_budget": larger[0] if larger else None,
    }


def plan_pipeline(
    ir: Mapping[str, Any],
    normalized_request: Mapping[str, Any],
    capabilities: Iterable[str] = (),
) -> dict[str, Any]:
    """Resolve downstream handlers without invoking them."""

    available = set(capabilities)
    diagram_type = ir["diagram"]["type"]
    requested_format = normalized_request["format"]
    required = [
        f"grammar:{diagram_type}",
        f"layout:{diagram_type}",
        "renderer:static-svg",
        "validator:output",
    ]
    if requested_format == "html":
        required.append("exporter:html")
    elif requested_format == "svg":
        required.append("exporter:svg")
    elif requested_format == "png":
        required.extend(("rasterizer:png", "exporter:png"))
    else:
        required.extend(("exporter:html", "rasterizer:png", "exporter:png"))

    stages = [
        {"capability": capability, "available": capability in available}
        for capability in required
    ]
    missing = [stage["capability"] for stage in stages if not stage["available"]]
    fallback: dict[str, Any] | None = None
    if requested_format == "png" and "rasterizer:png" in missing:
        fallback = {
            "format": "svg",
            "required": ["exporter:svg"],
            "available": "exporter:svg" in available,
            "warning": "PNG is unavailable because no approved rasterizer is registered.",
        }
    elif requested_format == "html+png" and "rasterizer:png" in missing:
        fallback = {
            "format": "html",
            "required": ["exporter:html"],
            "available": "exporter:html" in available,
            "warning": "PNG is unavailable because no approved rasterizer is registered; HTML remains the core fallback.",
        }
    return {"stages": stages, "missing": missing, "fallback": fallback}


def _base_result(status: str, stage: str) -> dict[str, Any]:
    return {
        "status": status,
        "stage": stage,
        "issues": [],
        "warnings": [],
        "artifacts": [],
    }


def orchestrate(
    raw_request: Mapping[str, Any],
    parsed_model: Mapping[str, Any] | None = None,
    *,
    capabilities: Iterable[str] = (),
) -> dict[str, Any]:
    """Run P-04 stages and return a transparent downstream plan or failure."""

    try:
        request = normalize_request(raw_request)
        if parsed_model is None:
            result = _base_result("unsupported", "carrier-parser")
            result["normalized_request"] = request
            result["issues"].append(
                {
                    "code": f"parser-unavailable-{request['source']['kind']}",
                    "stage": "carrier-parser",
                    "message": "No bounded carrier parser was supplied for this source.",
                }
            )
            return result

        ir = build_ir(request, parsed_model)
        complexity = plan_complexity(ir, request)
        if not complexity["fits"]:
            result = _base_result("needs-clarification", "complexity")
            result["normalized_request"] = request
            result["ir"] = ir
            result["ir_hash"] = semantic_hash(ir)
            result["complexity"] = complexity
            result["issues"].append(
                {
                    "code": "complexity-budget-exceeded",
                    "stage": "complexity",
                    "message": "The semantic model exceeds the approved budget for the requested size.",
                    "question": "Should the output use a larger compatible size, split into overview/detail artifacts, or narrow the scope?",
                }
            )
            return result
        pipeline = plan_pipeline(ir, request, capabilities)
        missing = pipeline["missing"]
        fallback = pipeline["fallback"]

        if missing:
            conditional_only = set(missing) <= {"rasterizer:png", "exporter:png"}
            if conditional_only and fallback is not None and fallback["available"]:
                result = _base_result("ready-with-fallback", "exporter")
                result["warnings"].append(fallback["warning"])
            else:
                result = _base_result("unsupported", "downstream-capability")
                result["issues"].append(
                    {
                        "code": "downstream-capability-unavailable",
                        "stage": "downstream-capability",
                        "message": f"Required capability is unavailable: {missing[0]}.",
                    }
                )
        else:
            result = _base_result("ready", "downstream-capability")

        result["normalized_request"] = request
        result["ir"] = ir
        result["ir_hash"] = semantic_hash(ir)
        result["complexity"] = complexity
        result["pipeline"] = pipeline
        return result
    except CoreError as error:
        result = _base_result(error.status, error.stage)
        result["issues"].append(error.issue())
        return result


__all__ = [
    "CANONICAL_TYPES",
    "LEGACY_CANONICAL_TYPES",
    "NEW_VARIANT_PARENTS",
    "SCHEMA_VERSION",
    "CoreError",
    "build_ir",
    "canonical_json",
    "detect_language",
    "normalize_request",
    "orchestrate",
    "plan_complexity",
    "plan_pipeline",
    "select_type",
    "semantic_hash",
    "validate_common_ir",
]
