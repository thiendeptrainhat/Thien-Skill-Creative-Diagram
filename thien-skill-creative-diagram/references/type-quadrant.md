# Quadrant semantic grammar

**Canonical ID:** `quadrant`  
**Capability:** `CAP-T09`  
**Family:** `quantitative-position`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for items positioned by two declared dimensions, directions, and domains.

## Required semantics

- Declare x and y axes with domains.
- Preserve every item coordinate and out-of-domain condition.

## Allowed abstract roles

- `observation`
- `scenario`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no relationship edge unless source data explicitly includes one.
- Do not connect items merely because they share a quadrant.

## Label rules

- Use supplied item labels and axis meanings.
- Name cell scenarios only when they are supplied or explicitly authorized.

## Complexity behavior

- Use labels or an accessible table when points overlap.
- Expand or reject out-of-domain values; never clamp silently.

## Semantic invariants

- `requires-x-y-axes`
- `numeric-coordinate-series`
- `coordinates-within-domain`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer rank from area or color.
- Do not reverse an axis to improve appearance.

## Coverage

- Positive semantic test: `T-TYPE-09-SEM`.
- Boundary mutation: `move-coordinate-outside-domain`.
- Later render smoke evidence remains required in each approved visual mode.
