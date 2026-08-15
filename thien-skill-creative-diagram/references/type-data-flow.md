# Data flow semantic grammar

**Canonical ID:** `data-flow`  
**Capability:** `CAP-T25`  
**Family:** `data-movement`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for role-scoped inputs, transformations, stores, outputs, and transfers.

## Required semantics

- Retain every data input, transformation, store, output, and role.
- Preserve fan-in, fan-out, capacity, and transfer direction when supplied.

## Allowed abstract roles

- `source`
- `queue`
- `transform`
- `store`
- `sink`
- `artifact`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed transfer edges.
- Distinguish control flow from data transfer.

## Label rules

- Use noun labels for data and verb labels for transformations.
- State queue capacity and overflow behavior when supplied.

## Complexity behavior

- Split by pipeline segment while preserving lineage.
- Do not aggregate records or flows without approval.

## Semantic invariants

- `requires-source-transform-sink`
- `directed-edges`
- `data-lineage-connected`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not show an activity-only workflow without data artifacts.
- Do not omit a bottleneck or queue capacity.

## Coverage

- Positive semantic test: `T-TYPE-25-SEM`.
- Boundary mutation: `remove-data-sink`.
- Later render smoke evidence remains required in each approved visual mode.
