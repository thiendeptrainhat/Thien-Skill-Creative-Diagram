# Loop/Flywheel semantic grammar

**Canonical ID:** `loop-flywheel`  
**Capability:** `CAP-T11`  
**Family:** `cycle`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for a reinforcing or recurring cycle with ordered stations and optional shared state.

## Required semantics

- Preserve station order and explicit cycle closure.
- Retain any shared state without making it an extra station.

## Allowed abstract roles

- `station`
- `shared-state`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed cycle edges.
- Every station must participate in the same declared cycle.

## Label rules

- Use action or state labels supplied for each station.
- Explain the reinforcing outcome separately from edge labels.

## Complexity behavior

- Factor repeated detail into annotations.
- Split multiple independent cycles rather than joining them decoratively.

## Semantic invariants

- `minimum-three-nodes`
- `directed-edges`
- `requires-single-cycle`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not present an open chain as a flywheel.
- Do not claim causal reinforcement without source evidence.

## Coverage

- Positive semantic test: `T-TYPE-11-SEM`.
- Boundary mutation: `break-cycle`.
- Later render smoke evidence remains required in each approved visual mode.
