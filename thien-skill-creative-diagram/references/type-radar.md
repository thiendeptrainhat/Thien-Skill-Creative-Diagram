# Radar/Spider semantic grammar

**Canonical ID:** `radar`  
**Capability:** `CAP-T10`  
**Family:** `multivariate-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for multiple series measured against at least three compatible criteria on one declared scale.

## Required semantics

- Declare every criterion and a common scale.
- Preserve all series values and normalization evidence.

## Allowed abstract roles

- `series`
- `criterion`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no semantic connectors between marks.
- Treat polygon closure as presentation, not an extra datum.

## Label rules

- Use exact criterion and series labels.
- State scale and unit in accessible data.

## Complexity behavior

- Limit criteria or split panels before labels collide.
- Never normalize incompatible scales without approval.

## Semantic invariants

- `minimum-three-axes`
- `requires-series`
- `common-axis-domain`
- `values-within-domain`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not compare incompatible units on one radial scale.
- Do not encode magnitude through polygon area alone.

## Coverage

- Positive semantic test: `T-TYPE-10-SEM`.
- Boundary mutation: `make-radar-domain-incompatible`.
- Later render smoke evidence remains required in each approved visual mode.
