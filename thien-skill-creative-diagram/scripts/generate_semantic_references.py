"""Generate deterministic P-05 references from the canonical semantic catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from semantic_catalog import CAPABILITY_MAP, SPECIMEN_GROUPS, TYPE_GRAMMARS, VARIANT_MAPPINGS


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"


def _bullets(values: tuple[str, ...] | list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def render_type_reference(diagram_type: str, grammar: dict[str, Any]) -> str:
    number = int(grammar['capability_id'][-2:])
    positive_id = f"T-TYPE-{number:02d}-POS-01" if number >= 28 else f"T-TYPE-{number:02d}-SEM"
    render_line = (
        "- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized."
        if number >= 28 else "- Later render smoke evidence remains required in each approved visual mode."
    )
    coverage_lines = [f"- Positive semantic test: `{positive_id}`."]
    if number >= 28:
        coverage_lines.append(f"- Stable boundary/hard/a11y families: `T-TYPE-{number:02d}-BOUND-01`, `T-TYPE-{number:02d}-HARD-01`, and `T-TYPE-{number:02d}-A11Y-01`.")
    coverage_lines.extend([f"- Boundary mutation: `{grammar['negative_mutation']}`.", render_line])
    coverage = "\n".join(coverage_lines)
    return f"""# {grammar['title']} semantic grammar

**Canonical ID:** `{diagram_type}`  
**Capability:** `{grammar['capability_id']}`  
**Family:** `{grammar['family']}`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

{grammar['use_when']}

## Required semantics

{_bullets(grammar['required_semantics'])}

## Allowed abstract roles

{_bullets(tuple(f'`{role}`' for role in grammar['roles']))}

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

{_bullets(grammar['edge_rules'])}

## Label rules

{_bullets(grammar['label_rules'])}

## Complexity behavior

{_bullets(grammar['complexity_rules'])}

## Semantic invariants

{_bullets(tuple(f'`{invariant}`' for invariant in grammar['invariants']))}

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

{_bullets(grammar['anti_patterns'])}

## Coverage

{coverage}
"""


def render_index() -> str:
    lines = [
        "# Semantic grammar index",
        "",
        "Load only the selected canonical type reference. The registry contains exactly 39 types; variants and patterns never add another type.",
        "",
        "| Type | Capability | Family | Reference |",
        "|---|---|---|---|",
    ]
    for diagram_type, grammar in TYPE_GRAMMARS.items():
        lines.append(
            f"| `{diagram_type}` | `{grammar['capability_id']}` | `{grammar['family']}` | "
            f"[type-{diagram_type}.md](type-{diagram_type}.md) |"
        )
    lines.extend(
        [
            "",
            "The four P-17 quantitative variants remain capabilities under existing parents; see [variants-v15.md](variants-v15.md).",
            "",
            "Use `scripts/semantic_grammars.py` for deterministic validation and `scripts/semantic_patterns.py` for pattern transformation. Use `capability-map.json` to resolve phase ownership, selector, fallback, implementation mapping, and test ID for every locked capability.",
            "",
        ]
    )
    return "\n".join(lines)


def render_v15_variants() -> str:
    rows = [
        ("CAP-V17", "Dumbbell", "bar-chart", "Exactly two finite values per category on one shared linear domain; signed gap is second minus first."),
        ("CAP-V18", "Slopegraph", "line-chart", "Every series has the same two distinct states; direction, rank, ties, and crossings derive from source values."),
        ("CAP-V19", "Ridgeline", "line-chart", "Every series supplies finite samples plus one shared histogram or explicit-bandwidth Gaussian KDE contract with global-max amplitude normalization."),
        ("CAP-V20", "Bubble", "scatter-plot", "Every observation has finite x, y, and non-negative size; data-bearing area, not radius, represents size."),
    ]
    lines = [
        "# P-17 quantitative capability variants",
        "",
        "These are capabilities, not canonical types 40–43. Validate the canonical parent first, then the named variant handler. Unit comparison uses Unicode NFC plus outer trimming, is case-sensitive, and performs no implicit conversion.",
        "",
        "| Capability | Name | Parent | Semantic contract | Stable tests |",
        "|---|---|---|---|---|",
    ]
    for capability_id, name, parent, contract in rows:
        lines.append(
            f"| `{capability_id}` | {name} | `{parent}` | {contract} | "
            f"`T-VAR-{capability_id}-POS-01`, `T-VAR-{capability_id}-BOUND-01`, `T-VAR-{capability_id}-HARD-01`, `T-VAR-{capability_id}-HARD-PARENT-01`, `T-VAR-{capability_id}-A11Y-01` |"
        )
    lines.extend([
        "",
        "Quantitative checks use `T-QUANT-DUMBBELL-*`, `T-QUANT-SLOPE-*`, `T-QUANT-RIDGE-*`, and `T-QUANT-BUBBLE-*`. Render tests remain deferred to the authorized visual phases.",
        "",
    ])
    return "\n".join(lines)


def semantic_v15_coverage() -> dict[str, Any]:
    quantitative_tokens = {
        "CAP-T28": "POLAR", "CAP-T29": "TREEMAP", "CAP-T30": "SANKEY",
        "CAP-T32": "WARDLEY", "CAP-T34": "JOURNEY",
        "CAP-V17": "DUMBBELL", "CAP-V18": "SLOPE", "CAP-V19": "RIDGE", "CAP-V20": "BUBBLE",
    }
    capabilities: dict[str, Any] = {}
    for capability_id in [f"CAP-T{i:02d}" for i in range(28, 40)] + [f"CAP-V{i:02d}" for i in range(17, 21)]:
        if capability_id.startswith("CAP-T"):
            number = int(capability_id[-2:])
            prefix = f"T-TYPE-{number:02d}"
            parents = CAPABILITY_MAP[capability_id]["parents"]
        else:
            prefix = f"T-VAR-{capability_id}"
            parents = VARIANT_MAPPINGS[capability_id]["parents"]
        test_ids = [
            f"{prefix}-POS-01", f"{prefix}-BOUND-01", f"{prefix}-HARD-01",
            f"{prefix}-RENDER-01", f"{prefix}-A11Y-01",
        ]
        if capability_id.startswith("CAP-V"):
            test_ids.append(f"{prefix}-HARD-PARENT-01")
        if capability_id in quantitative_tokens:
            test_ids.append(f"T-QUANT-{quantitative_tokens[capability_id]}-QUANT-01")
        capabilities[capability_id] = {
            "parents": parents,
            "semantic_status": "implemented-p17",
            "render_status": "deferred-to-p18-or-p19",
            "test_ids": test_ids,
            "test_status": {
                test_id: ("deferred-to-p18-or-p19" if "-RENDER-" in test_id else "implemented-p17")
                for test_id in test_ids
            },
        }
    return {"schema_version": "1.0", "target_version": "1.5.0", "canonical_additions": 12, "new_variants": 4, "capabilities": capabilities}


def generated_files() -> dict[Path, str]:
    files = {
        REFERENCE_DIR / f"type-{diagram_type}.md": render_type_reference(diagram_type, grammar)
        for diagram_type, grammar in TYPE_GRAMMARS.items()
    }
    files[REFERENCE_DIR / "type-index.md"] = render_index()
    files[REFERENCE_DIR / "variants-v15.md"] = render_v15_variants()
    files[REFERENCE_DIR / "capability-map.json"] = json.dumps(
        CAPABILITY_MAP,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    files[REFERENCE_DIR / "specimen-map.json"] = json.dumps(
        list(SPECIMEN_GROUPS),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    files[REFERENCE_DIR / "semantic-v15-coverage-map.json"] = json.dumps(
        semantic_v15_coverage(),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated references differ.")
    args = parser.parse_args()
    mismatches: list[str] = []
    for path, content in generated_files().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                mismatches.append(path.name)
        else:
            path.write_text(content, encoding="utf-8")
    if mismatches:
        print("semantic reference drift: " + ", ".join(sorted(mismatches)))
        return 1
    print("semantic references: PASS" if args.check else "semantic references generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
