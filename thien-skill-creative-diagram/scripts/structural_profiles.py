"""Target-v2.1 structural-profile resolution and receipt validation.

The JSON registry is the only profile source.  This module validates and
materializes it before rendering, then verifies that an emitted SVG and its
ledger bind the same immutable record.  It does not claim that metadata alone
proves visual conformance.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Sequence

from diagram_core import CANONICAL_TYPES, NEW_VARIANT_PARENTS, normalize_request
from semantic_grammars import validate_semantics
from visual_adapters_v15 import (
    CAPABILITY_ADAPTERS,
    ENGINE_TYPES,
    TYPE_ADAPTERS,
    adapt_visual,
)


PROFILE_SCHEMA_VERSION = "2.1"
PROFILE_TARGET_VERSION = "2.1.0"
REGISTRY_RELATIVE_PATH = "references/structural-profiles.json"
REGISTRY_PATH = Path(__file__).resolve().parent.parent / REGISTRY_RELATIVE_PATH
PROFILE_TOKEN_RE = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
MODES = ("neutral-light", "neutral-dark", "editorial")
PROFILE_SIGNATURE_FIELDS = (
    "silhouette",
    "arrangement",
    "containment",
    "rank_order",
    "marks",
    "connectors",
    "reading_order",
    "reflow",
    "forbidden",
)
ENGINE_GRAMMAR_FIELDS = (
    "axis",
    "placement",
    "ports",
    "routes",
    "crossings_junctions",
    "reflow",
)
ARTIFACT_ATTRIBUTE_MAP = {
    "selected_profile": "data-selected-profile",
    "canonical_parent": "data-canonical-parent",
    "layout_engine": "data-layout-engine",
    "mode": "data-mode",
    "structural_override": "data-structural-override",
    "registry_sha256": "data-profile-registry-sha256",
    "profile_record_sha256": "data-profile-record-sha256",
}


class StructuralProfileError(ValueError):
    """Fail-closed profile error with a stable machine code."""

    def __init__(self, code: str, message: str, *, status: str = "invalid") -> None:
        super().__init__(message)
        self.code = code
        self.status = status


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise StructuralProfileError(code, message)


def _nonempty_text(record: Mapping[str, Any], field: str, *, scope: str) -> None:
    _require(
        isinstance(record.get(field), str) and bool(record[field].strip()),
        "profile-registry-invalid",
        f"{scope}.{field} must be non-empty text.",
    )


def load_profile_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    """Load and strictly validate the canonical registry without mutation."""

    source = Path(path)
    try:
        registry = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise StructuralProfileError(
            "profile-registry-unavailable",
            "The canonical structural-profile registry is unavailable or invalid JSON.",
        ) from error
    validate_profile_registry(registry)
    return registry


def validate_profile_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate exact 45-profile taxonomy, aliases, engines, and grammar."""

    _require(isinstance(registry, Mapping), "profile-registry-invalid", "Registry must be an object.")
    _require(registry.get("schema_version") == PROFILE_SCHEMA_VERSION, "profile-registry-version", "Registry schema version must be 2.1.")
    _require(registry.get("target_version") == PROFILE_TARGET_VERSION, "profile-registry-version", "Registry target version must be 2.1.0.")
    _require(registry.get("profile_count") == 45, "profile-registry-count", "Registry must declare exactly 45 profiles.")
    _require(registry.get("layout_engine_count") == 14, "profile-registry-count", "Registry must declare exactly 14 layout engines.")
    _require(tuple(registry.get("modes", ())) == MODES, "profile-registry-modes", "The three approved modes must remain equal and ordered.")

    engines = registry.get("engine_grammars")
    _require(isinstance(engines, list) and len(engines) == 14, "profile-registry-count", "Exactly 14 engine grammars are required.")
    engine_by_id: dict[str, Mapping[str, Any]] = {}
    for index, engine in enumerate(engines):
        _require(isinstance(engine, Mapping), "profile-registry-invalid", f"engine_grammars[{index}] must be an object.")
        engine_id = engine.get("engine_id")
        _require(isinstance(engine_id, str) and PROFILE_TOKEN_RE.fullmatch(engine_id) is not None, "profile-registry-invalid", "Every engine needs one safe engine_id.")
        _require(engine_id not in engine_by_id, "profile-registry-duplicate", f"Duplicate engine {engine_id!r}.")
        for field in ENGINE_GRAMMAR_FIELDS:
            _nonempty_text(engine, field, scope=f"engine:{engine_id}")
        engine_by_id[engine_id] = engine
    _require(set(engine_by_id) == set(ENGINE_TYPES), "profile-engine-drift", "Engine grammar IDs must match the frozen 14-engine adapter taxonomy.")

    profiles = registry.get("profiles")
    _require(isinstance(profiles, list) and len(profiles) == 45, "profile-registry-count", "Exactly 45 profile records are required.")
    by_id: dict[str, Mapping[str, Any]] = {}
    alias_owner: dict[str, str] = {}
    references: set[str] = set()
    class_counts: dict[str, int] = {}
    canonical_default_by_parent: dict[str, str] = {}
    for index, profile in enumerate(profiles):
        _require(isinstance(profile, Mapping), "profile-registry-invalid", f"profiles[{index}] must be an object.")
        profile_id = profile.get("profile_id")
        _require(isinstance(profile_id, str) and PROFILE_TOKEN_RE.fullmatch(profile_id) is not None, "profile-registry-invalid", "Every profile needs one safe profile_id.")
        _require(profile_id not in by_id, "profile-registry-duplicate", f"Duplicate profile {profile_id!r}.")
        profile_class = profile.get("profile_class")
        _require(profile_class in {"canonical-anchor", "canonical-type", "capability", "presentation"}, "profile-registry-invalid", f"Unsupported class for {profile_id!r}.")
        class_counts[profile_class] = class_counts.get(profile_class, 0) + 1
        parent = profile.get("canonical_parent")
        _require(parent in CANONICAL_TYPES, "profile-parent-invalid", f"Profile {profile_id!r} has an unsupported canonical parent.")
        engine_id = profile.get("layout_engine")
        _require(engine_id in engine_by_id, "profile-engine-invalid", f"Profile {profile_id!r} has an unsupported engine.")
        reference = profile.get("approved_reference_identity")
        _require(isinstance(reference, str) and bool(reference.strip()), "profile-registry-invalid", f"Profile {profile_id!r} needs a reference identity.")
        _require(reference not in references, "profile-registry-duplicate", f"Reference identity {reference!r} is duplicated.")
        references.add(reference)
        for field in PROFILE_SIGNATURE_FIELDS:
            _nonempty_text(profile, field, scope=f"profile:{profile_id}")
        aliases = profile.get("selector_aliases")
        _require(isinstance(aliases, list) and len(aliases) == len(set(aliases)), "profile-alias-invalid", f"Profile {profile_id!r} aliases must be a unique list.")
        for selector in [profile_id, *aliases]:
            _require(isinstance(selector, str) and PROFILE_TOKEN_RE.fullmatch(selector) is not None, "profile-alias-invalid", f"Profile {profile_id!r} has an unsafe selector alias.")
            _require(selector not in alias_owner, "profile-alias-conflict", f"Selector {selector!r} resolves to more than one profile.")
            alias_owner[selector] = profile_id

        if profile_class in {"canonical-anchor", "canonical-type"}:
            _require("capability_id" not in profile and "presentation_variant_id" not in profile, "profile-registry-invalid", f"Canonical profile {profile_id!r} has an invalid variant field.")
            _require(parent not in canonical_default_by_parent, "profile-parent-duplicate", f"Canonical parent {parent!r} has more than one default profile.")
            canonical_default_by_parent[parent] = profile_id
            _require(TYPE_ADAPTERS[parent].layout_engine == engine_id, "profile-engine-drift", f"Profile {profile_id!r} disagrees with the frozen adapter engine.")
        elif profile_class == "capability":
            capability_id = profile.get("capability_id")
            _require(capability_id in NEW_VARIANT_PARENTS, "profile-capability-invalid", f"Profile {profile_id!r} has an unsupported capability.")
            _require(NEW_VARIANT_PARENTS[capability_id] == parent, "profile-parent-invalid", f"Capability {capability_id!r} has the wrong parent.")
            _require(CAPABILITY_ADAPTERS[capability_id].layout_engine == engine_id, "profile-engine-drift", f"Capability {profile_id!r} disagrees with the frozen adapter engine.")
            _require("presentation_variant_id" not in profile, "profile-registry-invalid", f"Capability {profile_id!r} cannot be a presentation profile.")
        else:
            _require(profile.get("presentation_variant_id") == profile_id, "profile-presentation-invalid", f"Presentation profile {profile_id!r} needs its own variant ID.")
            _require("capability_id" not in profile, "profile-registry-invalid", f"Presentation profile {profile_id!r} cannot carry a capability.")
            _require(TYPE_ADAPTERS[parent].layout_engine == engine_id, "profile-engine-drift", f"Presentation {profile_id!r} disagrees with its parent engine.")
        by_id[profile_id] = profile

    _require(class_counts == {"canonical-anchor": 14, "canonical-type": 25, "capability": 4, "presentation": 2}, "profile-registry-count", "Profile classes must be exactly 14/25/4/2.")
    _require(set(canonical_default_by_parent) == set(CANONICAL_TYPES), "profile-parent-coverage", "Every canonical type needs exactly one default public profile.")
    _require({item.get("capability_id") for item in profiles if item.get("profile_class") == "capability"} == set(NEW_VARIANT_PARENTS), "profile-capability-coverage", "The exact four capabilities are required.")
    _require({item.get("profile_id") for item in profiles if item.get("profile_class") == "presentation"} == {"layers", "scatter-chart"}, "profile-presentation-coverage", "The exact two presentation profiles are required.")

    ledger = registry.get("ledger_contract")
    _require(isinstance(ledger, Mapping), "profile-ledger-contract-invalid", "Registry needs one ledger contract.")
    required_fields = ledger.get("required_fields")
    _require(isinstance(required_fields, list) and set(required_fields) == {"requested_selector", "selected_profile", "canonical_parent", "layout_engine", "mode", "structural_override", "fallback", "registry_sha256", "profile_record_sha256"}, "profile-ledger-contract-invalid", "Ledger required fields drifted.")
    return {"profiles": len(by_id), "engines": len(engine_by_id), "aliases": len(alias_owner), "classes": class_counts}


def _registry_indexes(registry: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], dict[str, str], dict[str, Mapping[str, Any]]]:
    profiles = {item["profile_id"]: item for item in registry["profiles"]}
    aliases = {selector: item["profile_id"] for item in registry["profiles"] for selector in [item["profile_id"], *item["selector_aliases"]]}
    engines = {item["engine_id"]: item for item in registry["engine_grammars"]}
    return profiles, aliases, engines


def resolve_structural_profile(
    canonical_parent: str,
    *,
    requested_selector: str = "auto",
    capability_ids: Sequence[str] = (),
    mode: str = "neutral-light",
    structural_override: str = "none",
    override_reason: str | None = None,
    registry: Mapping[str, Any] | None = None,
    registry_path: str | Path = REGISTRY_PATH,
) -> dict[str, Any]:
    """Resolve exactly one public profile and return its pre-render binding."""

    active = dict(registry) if registry is not None else load_profile_registry(registry_path)
    validate_profile_registry(active)
    _require(canonical_parent in CANONICAL_TYPES, "profile-parent-invalid", "Resolve profiles only after canonical semantic routing.")
    _require(mode in MODES, "profile-mode-invalid", "Mode must be one of the three equal approved modes.")
    _require(structural_override in {"none", "custom-structure"}, "profile-override-invalid", "Structural override must be none or custom-structure.")
    if structural_override == "custom-structure":
        _require(isinstance(override_reason, str) and bool(override_reason.strip()), "profile-override-reason-missing", "Custom structure requires the trusted user's reason.")
    else:
        _require(override_reason in {None, ""}, "profile-override-invalid", "An override reason is only valid for custom-structure.")
    capabilities = tuple(capability_ids)
    _require(len(capabilities) == len(set(capabilities)) and len(capabilities) <= 1, "profile-capability-conflict", "At most one capability may own a profile.")
    _require(all(item in NEW_VARIANT_PARENTS for item in capabilities), "profile-capability-invalid", "Unsupported capability selector.")

    profiles, aliases, engines = _registry_indexes(active)
    if requested_selector == "auto":
        if capabilities:
            matches = [item for item in profiles.values() if item.get("capability_id") == capabilities[0]]
        else:
            matches = [item for item in profiles.values() if item["profile_class"] in {"canonical-anchor", "canonical-type"} and item["canonical_parent"] == canonical_parent]
        _require(len(matches) == 1, "profile-resolution-ambiguous", "Automatic resolution did not produce exactly one profile.")
        profile = matches[0]
    else:
        _require(isinstance(requested_selector, str) and PROFILE_TOKEN_RE.fullmatch(requested_selector) is not None, "profile-selector-invalid", "Profile selector is invalid.")
        _require(requested_selector in aliases, "profile-unsupported", "Requested structural profile is unsupported.")
        profile = profiles[aliases[requested_selector]]

    _require(profile["canonical_parent"] == canonical_parent, "profile-parent-mismatch", "Selected profile does not belong to the routed canonical type.")
    capability_id = profile.get("capability_id")
    if capability_id:
        _require(capabilities == (capability_id,), "profile-capability-mismatch", "Capability profile requires its exact semantic capability selection.")
    else:
        _require(not capabilities, "profile-capability-mismatch", "Selected capability requires its capability-owned profile.")

    engine = engines[profile["layout_engine"]]
    materialized_record = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "target_version": PROFILE_TARGET_VERSION,
        "profile": copy.deepcopy(profile),
        "engine_grammar": copy.deepcopy(engine),
        "customization_contract": copy.deepcopy(active["customization_contract"]),
    }
    source_path = Path(registry_path)
    registry_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest() if registry is None else _json_sha256(active)
    profile_record_sha256 = _json_sha256(materialized_record)
    binding = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "binding_stage": "pre-render",
        "requested_selector": requested_selector,
        "selected_profile": profile["profile_id"],
        "canonical_parent": canonical_parent,
        "layout_engine": profile["layout_engine"],
        "mode": mode,
        "structural_override": structural_override,
        "override_reason": override_reason if structural_override == "custom-structure" else None,
        "fallback": None,
        "registry_path": REGISTRY_RELATIVE_PATH,
        "registry_sha256": registry_sha256,
        "profile_record_sha256": profile_record_sha256,
        "profile_class": profile["profile_class"],
        "approved_reference_identity": profile["approved_reference_identity"],
        "conformance_scope": "outside-45-profile" if structural_override == "custom-structure" else "selected-profile",
    }
    return {"binding": binding, "materialized_record": materialized_record}


def build_profiled_plan(ir_value: Mapping[str, Any], raw_request: Mapping[str, Any]) -> dict[str, Any]:
    """Combine the frozen semantic adapter plan with one v2.1 profile record."""

    ir = validate_semantics(ir_value)
    request = normalize_request(raw_request)
    parent = ir["diagram"]["type"]
    if request["diagram_type"] not in {"auto", parent}:
        raise StructuralProfileError("profile-parent-mismatch", "The request type does not match the validated semantic IR.")
    if tuple(request["variant_ids"]) != tuple(ir["diagram"].get("variant_ids", ())):
        raise StructuralProfileError("profile-capability-mismatch", "The request capability does not match the validated semantic IR.")
    resolved = resolve_structural_profile(
        parent,
        requested_selector=request["structural_profile"],
        capability_ids=ir["diagram"].get("variant_ids", ()),
        mode=request["visual_mode"],
        structural_override=request["structural_override"]["status"],
        override_reason=request["structural_override"].get("reason"),
    )
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "target_version": PROFILE_TARGET_VERSION,
        "profile_binding": resolved["binding"],
        "structural_profile": resolved["materialized_record"],
        "semantic_adapter_plan": adapt_visual(ir),
    }


def artifact_binding_attributes(binding: Mapping[str, Any]) -> dict[str, str]:
    """Return exact SVG-root attributes a profile-aware renderer must emit."""

    return {attribute: str(binding[field]) for field, attribute in ARTIFACT_ATTRIBUTE_MAP.items()}


def validate_artifact_binding(svg: str, binding: Mapping[str, Any]) -> dict[str, str]:
    """Verify SVG/profile identity; leave geometry verdict explicitly unevaluated."""

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise StructuralProfileError("profile-artifact-invalid", "Profiled artifact is not valid SVG XML.") from error
    _require(root.tag.rsplit("}", 1)[-1] == "svg", "profile-artifact-invalid", "Profiled artifact needs an SVG root.")
    for attribute, expected in artifact_binding_attributes(binding).items():
        _require(root.get(attribute) == expected, "profile-artifact-binding-mismatch", f"SVG root attribute {attribute!r} does not match the pre-render binding.")
    _require(root.get("data-structural-conformance") != "pass", "profile-claim-unsupported", "Artifact metadata cannot self-award structural conformance.")
    return {"profile_binding": "pass", "structural_conformance": "not-evaluated"}


def profile_binding_for_ledger(binding: Mapping[str, Any]) -> dict[str, Any]:
    """Create a detached ledger binding with every required field present."""

    required = load_profile_registry()["ledger_contract"]["required_fields"]
    _require(all(field in binding for field in required), "profile-ledger-binding-invalid", "Pre-render binding is incomplete.")
    return copy.deepcopy(dict(binding))


def validate_profile_binding(binding: Mapping[str, Any]) -> dict[str, str]:
    """Re-resolve a receipt from the canonical registry and compare every field."""

    _require(isinstance(binding, Mapping), "profile-binding-invalid", "Profile binding must be an object.")
    for field in ("requested_selector", "selected_profile", "canonical_parent", "layout_engine", "mode", "structural_override", "fallback", "registry_sha256", "profile_record_sha256"):
        _require(field in binding, "profile-binding-invalid", f"Profile binding field {field!r} is missing.")
    registry = load_profile_registry()
    profiles, _, _ = _registry_indexes(registry)
    selected = binding["selected_profile"]
    _require(selected in profiles, "profile-binding-invalid", "Selected profile is not in the canonical registry.")
    capability_id = profiles[selected].get("capability_id")
    expected = resolve_structural_profile(
        str(binding["canonical_parent"]),
        requested_selector=str(binding["requested_selector"]),
        capability_ids=(capability_id,) if capability_id else (),
        mode=str(binding["mode"]),
        structural_override=str(binding["structural_override"]),
        override_reason=binding.get("override_reason"),
    )["binding"]
    _require(dict(binding) == expected, "profile-binding-mismatch", "Profile binding does not match canonical pre-render resolution.")
    return {"profile_binding": "pass", "binding_stage": "pre-render"}


def validate_profile_ledger(ledger: Mapping[str, Any], expected_binding: Mapping[str, Any]) -> dict[str, str]:
    """Verify ledger identity without treating the receipt as visual QA."""

    actual = ledger.get("structural_profile")
    _require(isinstance(actual, Mapping), "profile-ledger-binding-missing", "Ledger needs a structural_profile binding.")
    required = load_profile_registry()["ledger_contract"]["required_fields"]
    for field in required:
        _require(field in actual, "profile-ledger-binding-missing", f"Ledger structural_profile.{field} is missing.")
        _require(actual[field] == expected_binding[field], "profile-ledger-binding-mismatch", f"Ledger structural_profile.{field} does not match the pre-render binding.")
    _require(actual.get("binding_stage") == "pre-render", "profile-ledger-binding-invalid", "Profile binding must occur before rendering.")
    _require(ledger.get("profile_binding") == "pass", "profile-ledger-binding-invalid", "Ledger must record the validated binding check.")
    _require(ledger.get("structural_conformance") in {"not-evaluated", "pass", "fail"}, "profile-ledger-binding-invalid", "Ledger needs an explicit structural-conformance disposition.")
    return {"profile_binding": "pass", "structural_conformance": str(ledger["structural_conformance"])}


__all__ = [
    "ARTIFACT_ATTRIBUTE_MAP",
    "PROFILE_SCHEMA_VERSION",
    "PROFILE_TARGET_VERSION",
    "REGISTRY_PATH",
    "REGISTRY_RELATIVE_PATH",
    "StructuralProfileError",
    "artifact_binding_attributes",
    "build_profiled_plan",
    "canonical_json",
    "load_profile_registry",
    "profile_binding_for_ledger",
    "resolve_structural_profile",
    "validate_artifact_binding",
    "validate_profile_binding",
    "validate_profile_ledger",
    "validate_profile_registry",
]
