# Medallion semantic grammar

**Canonical ID:** `medallion`  
**Capability:** `CAP-T24`  
**Family:** `tier-promotion`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for records promoted through named quality or storage tiers under explicit policies.

## Required semantics

- Represent tiers as ordered lanes.
- Preserve promotion, rejection, and exception paths.

## Allowed abstract roles

- `dataset`
- `policy`
- `exception`
- `tier-item`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed promotion or rejection edges.
- Do not imply all records advance successfully.

## Label rules

- Use supplied tier, dataset, policy, and rejection labels.
- Keep quality claims source-backed.

## Complexity behavior

- Split details within tiers without changing tier order.
- Retain rejected-record destinations.

## Semantic invariants

- `minimum-two-tiers`
- `unique-layer-order`
- `requires-promotion-edge`
- `preserves-exception-path`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not invent bronze/silver/gold names.
- Do not route a generic source-platform-consumer topology here.

## Coverage

- Positive semantic test: `T-TYPE-24-SEM`.
- Boundary mutation: `remove-promotion-edge`.
- Later render smoke evidence remains required in each approved visual mode.
