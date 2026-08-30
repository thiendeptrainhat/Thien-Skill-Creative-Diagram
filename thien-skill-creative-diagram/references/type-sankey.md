# Sankey semantic grammar

**Canonical ID:** `sankey`  
**Capability:** `CAP-T30`  
**Family:** `quantitative-flow`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for directed stage-to-stage flows where band width represents an exact non-negative amount.

## Required semantics

- Preserve source, target, amount, unit, and zero flows.
- Conserve same-unit totals at every node with both incoming and outgoing flow.

## Allowed abstract roles

- `source`
- `stage`
- `sink`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed flow edges with direct amount fields.
- Keep zero flows in the ledger while assigning zero data-bearing width.

## Label rules

- Use supplied stage, flow, amount, and unit labels.
- Provide an exact accessible flow ledger.

## Complexity behavior

- Split large stage sets without changing conservation.
- Never aggregate flows unless the source authorizes it.

## Semantic invariants

- `minimum-two-nodes`
- `minimum-one-edge`
- `directed-edges`
- `sankey-flow-conservation`
- `requires-accessible-data`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not accept negative or missing flow amounts.
- Do not mix or convert units implicitly.

## Coverage

- Positive semantic test: `T-TYPE-30-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-30-BOUND-01`, `T-TYPE-30-HARD-01`, and `T-TYPE-30-A11Y-01`.
- Boundary mutation: `break-sankey-conservation`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
