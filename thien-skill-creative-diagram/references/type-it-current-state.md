# IT current-state semantic grammar

**Canonical ID:** `it-current-state`  
**Capability:** `CAP-T02`  
**Family:** `landscape`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for an existing technology landscape grouped by owner, business area, lifecycle, or modernization state.

## Required semantics

- Retain owner and lifecycle state for each system.
- Preserve modernization handoffs and duplicate names as distinct IDs.

## Allowed abstract roles

- `system`
- `integration`
- `data-store`
- `owner`
- `boundary`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use handoff or integration edges with direction.
- Do not turn shared ownership into containment.

## Label rules

- Show system name plus supplied state.
- Keep owner labels separate from system labels.

## Complexity behavior

- Split by business area when the landscape exceeds the selected budget.
- Never collapse systems solely because labels match.

## Semantic invariants

- `minimum-two-nodes`
- `requires-group`
- `requires-node-state`
- `requires-handoff`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not present a target-state proposal as current state.
- Do not omit legacy or exception paths.

## Coverage

- Positive semantic test: `T-TYPE-02-SEM`.
- Boundary mutation: `remove-node-state`.
- Later render smoke evidence remains required in each approved visual mode.
