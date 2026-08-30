# Dependency graph semantic grammar

**Canonical ID:** `dependency-graph`  
**Capability:** `CAP-T36`  
**Family:** `general-dependency`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for general directed dependencies where fan-in, disconnected components, rank, or cycles may be material.

## Required semantics

- Preserve every dependency endpoint and direction.
- Retain cycles and fan-in rather than coercing the graph to a tree.

## Allowed abstract roles

- `component`
- `dependency`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed dependency edges.
- Keep strongly connected components explicit when present.

## Label rules

- Use supplied item and relationship labels.
- Disclose cycles without treating them as invalid by default.

## Complexity behavior

- Split disconnected components without dropping relations.
- Never duplicate a multi-parent node to imitate a tree.

## Semantic invariants

- `dependency-graph-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not reject a supplied cycle merely for layout convenience.
- Do not infer dependency rank as business priority.

## Coverage

- Positive semantic test: `T-TYPE-36-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-36-BOUND-01`, `T-TYPE-36-HARD-01`, and `T-TYPE-36-A11Y-01`.
- Boundary mutation: `remove-dependency-edge`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
