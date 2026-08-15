"""Generate deterministic P-05 references from the canonical semantic catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from semantic_catalog import CAPABILITY_MAP, SPECIMEN_GROUPS, TYPE_GRAMMARS


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"


def _bullets(values: tuple[str, ...] | list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def render_type_reference(diagram_type: str, grammar: dict[str, Any]) -> str:
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

- Positive semantic test: `T-TYPE-{int(grammar['capability_id'][-2:]):02d}-SEM`.
- Boundary mutation: `{grammar['negative_mutation']}`.
- Later render smoke evidence remains required in each approved visual mode.
"""


def render_index() -> str:
    lines = [
        "# Semantic grammar index",
        "",
        "Load only the selected canonical type reference. The registry contains exactly 27 types; variants and patterns never add another type.",
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
            "Use `scripts/semantic_grammars.py` for deterministic validation and `scripts/semantic_patterns.py` for pattern transformation. Use `capability-map.json` to resolve phase ownership, selector, fallback, implementation mapping, and test ID for every locked capability.",
            "",
        ]
    )
    return "\n".join(lines)


def generated_files() -> dict[Path, str]:
    files = {
        REFERENCE_DIR / f"type-{diagram_type}.md": render_type_reference(diagram_type, grammar)
        for diagram_type, grammar in TYPE_GRAMMARS.items()
    }
    files[REFERENCE_DIR / "type-index.md"] = render_index()
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
