# Polar chart semantic grammar

**Canonical ID:** `polar-chart`  
**Capability:** `CAP-T28`  
**Family:** `cyclic-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for non-negative magnitudes arranged across a supplied cyclic category order.

## Required semantics

- Preserve category order, value, unit, zero, and explicit missingness.
- Declare one angular category axis and one non-negative radial domain.

## Allowed abstract roles

- `series`
- `category`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no semantic connectors between radial marks.
- A missing observation remains a disclosed gap.

## Label rules

- Use exact category, series, axis, and unit labels.
- Provide an accessible value ledger including zero and missing entries.

## Complexity behavior

- Split dense category sets before labels collide.
- Never reorder categories to improve the silhouette.

## Semantic invariants

- `requires-polar-axes`
- `polar-series-valid`
- `requires-accessible-data`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not map category to radius.
- Do not coerce missing values to zero or interpolate them.

## Coverage

- Positive semantic test: `T-TYPE-28-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-28-BOUND-01`, `T-TYPE-28-HARD-01`, and `T-TYPE-28-A11Y-01`.
- Boundary mutation: `make-polar-radius-negative`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
