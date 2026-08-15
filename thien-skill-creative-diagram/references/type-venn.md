# Venn semantic grammar

**Canonical ID:** `venn`  
**Capability:** `CAP-T16`  
**Family:** `set-membership`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for explicit membership across two or three sets, including intersections and items outside all sets.

## Required semantics

- Retain each set and every member's full membership vector.
- Keep outside items rather than dropping them.

## Allowed abstract roles

- `member`
- `outside-member`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use no connector to imply membership.
- Express membership through group member IDs.

## Label rules

- Use supplied set and member names.
- Label empty intersections when material.

## Complexity behavior

- Use an accessible membership table for dense sets.
- Split beyond three sets rather than drawing unreadable overlaps.

## Semantic invariants

- `minimum-two-groups`
- `allows-multi-group-membership`
- `preserves-outside-members`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer membership from location.
- Do not duplicate one member as separate copies in intersections.

## Coverage

- Positive semantic test: `T-TYPE-16-SEM`.
- Boundary mutation: `remove-set-groups`.
- Later render smoke evidence remains required in each approved visual mode.
