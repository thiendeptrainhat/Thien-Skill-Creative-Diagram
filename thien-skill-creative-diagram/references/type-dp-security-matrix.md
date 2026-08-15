# DP security matrix semantic grammar

**Canonical ID:** `dp-security-matrix`  
**Capability:** `CAP-T27`  
**Family:** `permission-matrix`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for complete role-by-component permission states with an explicit legend.

## Required semantics

- Represent every declared role-component intersection exactly once.
- Preserve allow, deny, conditional, and unknown states without inference.

## Allowed abstract roles

- `permission-cell`
- `role`
- `component`
- `legend`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no connector to imply permission.
- Represent escalation or inheritance separately from matrix cells.

## Label rules

- Encode each cell identity as role and component plus supplied state.
- Provide an accessible text table and legend.

## Complexity behavior

- Split large matrices by component domain while repeating the complete legend.
- Never omit unknown or deny cells to save space.

## Semantic invariants

- `requires-rectangular-permission-matrix`
- `permission-state-enum`
- `requires-accessible-data`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer missing permissions.
- Do not encode state only by color.

## Coverage

- Positive semantic test: `T-TYPE-27-SEM`.
- Boundary mutation: `remove-permission-cell`.
- Later render smoke evidence remains required in each approved visual mode.
