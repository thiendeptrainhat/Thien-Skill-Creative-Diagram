# State machine semantic grammar

**Canonical ID:** `state-machine`  
**Capability:** `CAP-T05`  
**Family:** `state-transition`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for finite states, guarded transitions, initial entry, terminal states, and explicit reopen paths.

## Required semantics

- Include one initial state and at least one terminal state.
- Preserve transition guards and reachability.

## Allowed abstract roles

- `initial`
- `state`
- `terminal`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed transition edges.
- Require a guard when multiple transitions leave the same state for different conditions.

## Label rules

- Use state nouns or stable conditions.
- Use guard labels for transition predicates.

## Complexity behavior

- Split orthogonal state regions explicitly.
- Report unreachable states instead of hiding them.

## Semantic invariants

- `requires-initial`
- `requires-terminal`
- `transition-edges`
- `all-nodes-reachable`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not model activities as states without a stable condition.
- Do not create implicit transitions.

## Coverage

- Positive semantic test: `T-TYPE-05-SEM`.
- Boundary mutation: `remove-terminal-state`.
- Later render smoke evidence remains required in each approved visual mode.
