# Gantt semantic grammar

**Canonical ID:** `gantt`  
**Capability:** `CAP-T20`  
**Family:** `temporal-dependency`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for tasks or milestones with start/end times, durations, and dependencies.

## Required semantics

- Preserve start, end, timezone, order, and dependency facts.
- Reject an end before its start.

## Allowed abstract roles

- `task`
- `milestone`
- `phase`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed dependency edges.
- Reject dependency cycles unless the source explicitly describes an unresolved error.

## Label rules

- Use exact task, phase, date, and timezone labels.
- Do not infer duration from visual width.

## Complexity behavior

- Split by phase while retaining cross-phase dependencies.
- Do not move dates to avoid overlap.

## Semantic invariants

- `requires-task-times`
- `end-not-before-start`
- `dependency-acyclic`
- `timezone-required`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not fabricate missing dates.
- Do not hide a dependency cycle.

## Coverage

- Positive semantic test: `T-TYPE-20-SEM`.
- Boundary mutation: `set-end-before-start`.
- Later render smoke evidence remains required in each approved visual mode.
