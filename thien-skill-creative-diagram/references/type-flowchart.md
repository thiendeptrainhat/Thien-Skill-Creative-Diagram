# Flowchart semantic grammar

**Canonical ID:** `flowchart`  
**Capability:** `CAP-T03`  
**Family:** `decision-flow`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for decisions, branches, joins, and declared outcomes in a control flow.

## Required semantics

- Include at least one start and terminal.
- Make every decision outcome traceable to a declared terminal or next decision.

## Allowed abstract roles

- `start`
- `activity`
- `decision`
- `join`
- `terminal`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Direct all flow edges.
- Give every outgoing decision branch a non-empty guard label.

## Label rules

- Use action labels for activities and outcome labels for terminals.
- Keep branch guards distinct from node labels.

## Complexity behavior

- Split subflows rather than shrinking branch labels.
- Retain exception outcomes even when rare.

## Semantic invariants

- `requires-start`
- `requires-terminal`
- `requires-decision`
- `decision-guards`
- `all-nodes-reachable`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not invent a missing branch.
- Do not use a decorative diamond without decision semantics.

## Coverage

- Positive semantic test: `T-TYPE-03-SEM`.
- Boundary mutation: `remove-decision-guard`.
- Later render smoke evidence remains required in each approved visual mode.
