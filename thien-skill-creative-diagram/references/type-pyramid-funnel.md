# Pyramid/Funnel semantic grammar

**Canonical ID:** `pyramid-funnel`  
**Capability:** `CAP-T17`  
**Family:** `ordered-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for a ranked hierarchy or ordered conversion stages with declared values or proportions.

## Required semantics

- Preserve stage order, values, missingness, and supplied ratios.
- Allow honest increases in funnel stages.

## Allowed abstract roles

- `stage`
- `level`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use optional transition edges only when a process relation is supplied.
- Do not derive ratios from geometry.

## Label rules

- Use exact stage labels, values, and units.
- Disclose whether the variant is hierarchy or conversion.

## Complexity behavior

- Split long stage notes into annotations.
- Never narrow a stage solely to satisfy a funnel silhouette.

## Semantic invariants

- `requires-single-ordered-series`
- `preserves-nonmonotonic-values`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not fabricate monotonic decrease.
- Do not imply area is proportional unless the renderer proves it.

## Coverage

- Positive semantic test: `T-TYPE-17-SEM`.
- Boundary mutation: `remove-pyramid-series`.
- Later render smoke evidence remains required in each approved visual mode.
