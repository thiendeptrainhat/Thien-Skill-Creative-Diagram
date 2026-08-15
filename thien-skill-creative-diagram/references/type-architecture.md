# Architecture semantic grammar

**Canonical ID:** `architecture`  
**Capability:** `CAP-T01`  
**Family:** `topology`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for components placed inside explicit system or trust boundaries with directed dependencies.

## Required semantics

- Identify every component and boundary.
- Preserve dependency direction and boundary membership.

## Allowed abstract roles

- `system`
- `service`
- `actor`
- `data-store`
- `boundary`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed dependency or transfer edges.
- Keep cross-boundary edges explicit.

## Label rules

- Use supplied component and boundary names.
- Label denied or exceptional routes explicitly.

## Complexity behavior

- Split by subsystem before hiding a boundary.
- Retain shared services as shared rather than duplicating them.

## Semantic invariants

- `minimum-two-nodes`
- `minimum-one-edge`
- `requires-boundary`
- `directed-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer deployment topology from visual proximity.
- Do not place one component in two boundaries without explicit shared scope.

## Coverage

- Positive semantic test: `T-TYPE-01-SEM`.
- Boundary mutation: `remove-boundaries`.
- Later render smoke evidence remains required in each approved visual mode.
