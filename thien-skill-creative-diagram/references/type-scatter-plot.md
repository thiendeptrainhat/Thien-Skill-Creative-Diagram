# Scatter plot semantic grammar

**Canonical ID:** `scatter-plot`  
**Capability:** `CAP-T21`  
**Family:** `paired-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for paired observations on two declared quantitative axes.

## Required semantics

- Preserve exact point count, coordinates, duplicates, and missingness.
- Declare both axis domains and units.

## Allowed abstract roles

- `observation`
- `series`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no relationship edges between observations unless source data supplies one.
- Do not connect points merely by input order.

## Label rules

- Use exact series and axis labels.
- Provide an accessible coordinate table.

## Complexity behavior

- Retain up to the approved point ceiling without silent sampling.
- Use density treatment only after exact data remains accessible.

## Semantic invariants

- `requires-x-y-linear-axes`
- `numeric-coordinate-series`
- `scatter-missingness-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not replace null coordinates with zero.
- Do not claim correlation as causation.

## Coverage

- Positive semantic test: `T-TYPE-21-SEM`.
- Boundary mutation: `set-scatter-null-as-present`.
- Later render smoke evidence remains required in each approved visual mode.
