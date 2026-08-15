# Swimlane semantic grammar

**Canonical ID:** `swimlane`  
**Capability:** `CAP-T08`  
**Family:** `owned-process`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for ordered work where actor or function ownership and cross-lane handoffs are material.

## Required semantics

- Assign each step to exactly one lane.
- Retain lane owner, step order, and cross-lane handoffs.

## Allowed abstract roles

- `start`
- `activity`
- `decision`
- `artifact`
- `terminal`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed handoff or flow edges.
- A cross-lane edge must connect members of different lanes.

## Label rules

- Use action labels for steps and stable owner labels for lanes.
- Preserve Vietnamese text and numbered handoffs when supplied.

## Complexity behavior

- Split long processes by phase while retaining lane identity.
- Do not merge owners to reduce width.

## Semantic invariants

- `minimum-two-lanes`
- `lane-membership-exact`
- `requires-cross-lane-handoff`
- `unique-edge-order`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer ownership from horizontal position.
- Do not duplicate a step into multiple lanes.

## Coverage

- Positive semantic test: `T-TYPE-08-SEM`.
- Boundary mutation: `remove-cross-lane-handoff`.
- Later render smoke evidence remains required in each approved visual mode.
