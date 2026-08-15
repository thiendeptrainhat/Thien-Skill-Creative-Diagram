# Process semantic grammar

**Canonical ID:** `process`  
**Capability:** `CAP-T23`  
**Family:** `artifact-process`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for multi-actor sequential or parallel work with artifacts and handoffs.

## Required semantics

- Retain actors, steps, artifacts, parallelism, and handoffs.
- Assign owned steps to lanes when ownership is supplied.

## Allowed abstract roles

- `start`
- `activity`
- `decision`
- `artifact`
- `terminal`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed flow and handoff edges with stable order where sequential.
- Keep parallel branches unordered relative to each other.

## Label rules

- Use action labels for work and noun labels for artifacts.
- Preserve supplied owner terminology.

## Complexity behavior

- Split by phase while retaining artifact lineage.
- Do not serialize parallel work for convenience.

## Semantic invariants

- `requires-activity`
- `requires-artifact`
- `requires-process-flow`
- `parallel-order-consistent`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not omit artifacts that carry state.
- Do not infer an owner from adjacency.

## Coverage

- Positive semantic test: `T-TYPE-23-SEM`.
- Boundary mutation: `remove-process-artifact`.
- Later render smoke evidence remains required in each approved visual mode.
