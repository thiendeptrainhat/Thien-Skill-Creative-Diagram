# Bar chart semantic grammar

**Canonical ID:** `bar-chart`  
**Capability:** `CAP-T18`  
**Family:** `categorical-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for categorical value comparison with a declared unit and baseline.

## Required semantics

- Preserve categories, series, values, zeros, negatives, missingness, and units.
- Use a zero baseline unless an explicit approved exception is recorded.

## Allowed abstract roles

- `category`
- `series`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no semantic connectors between bars.
- Keep grouped and stacked series identities explicit.

## Label rules

- Use exact category, series, and unit labels.
- Provide exact accessible data values.

## Complexity behavior

- Split categories or use a larger size before abbreviating material labels.
- Do not aggregate without approval.

## Semantic invariants

- `requires-categorical-x-linear-y`
- `requires-series`
- `bar-zero-baseline`
- `series-domain-consistency`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not truncate the baseline silently.
- Do not encode unrelated measures in one series.

## Coverage

- Positive semantic test: `T-TYPE-18-SEM`.
- Boundary mutation: `truncate-bar-baseline`.
- Later render smoke evidence remains required in each approved visual mode.
