# Kanban semantic grammar

**Canonical ID:** `kanban`  
**Capability:** `CAP-T33`  
**Family:** `work-state`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for work items assigned to ordered state columns with WIP limits and explicit blocked state.

## Required semantics

- Assign every work item to one column and stable item order.
- Enforce supplied WIP limits and preserve blocked state.

## Allowed abstract roles

- `work-item`
- `column`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no connector to imply column membership.
- Represent workflow relations separately when supplied.

## Label rules

- Use exact column and work-item labels.
- Expose blocked state through structured semantics, not color alone.

## Complexity behavior

- Split or scroll dense boards without hiding cards.
- Do not move a card to satisfy a limit.

## Semantic invariants

- `kanban-board-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer work state from horizontal position.
- Do not silently accept WIP overflow.

## Coverage

- Positive semantic test: `T-TYPE-33-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-33-BOUND-01`, `T-TYPE-33-HARD-01`, and `T-TYPE-33-A11Y-01`.
- Boundary mutation: `exceed-kanban-wip-limit`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
