# Line chart semantic grammar

**Canonical ID:** `line-chart`  
**Capability:** `CAP-T19`  
**Family:** `ordered-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for one or more quantitative series over an ordered or temporal domain.

## Required semantics

- Preserve domain order, values, units, gaps, and duplicate dates.
- Keep missing values as explicit gaps.

## Allowed abstract roles

- `series`
- `observation`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no semantic connector beyond the declared series progression.
- Do not interpolate missing observations.

## Label rules

- Use exact series, axis, unit, and date labels.
- Provide exact accessible data.

## Complexity behavior

- Split incompatible units into panels.
- Never sample away material points without approval.

## Semantic invariants

- `requires-ordered-x-linear-y`
- `requires-series`
- `domain-order-valid`
- `missing-values-explicit`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not smooth or interpolate without authorization.
- Do not silently deduplicate dates.

## Coverage

- Positive semantic test: `T-TYPE-19-SEM`.
- Boundary mutation: `reverse-line-domain`.
- Later render smoke evidence remains required in each approved visual mode.
