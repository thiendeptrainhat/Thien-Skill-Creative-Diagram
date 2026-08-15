# Nested semantic grammar

**Canonical ID:** `nested`  
**Capability:** `CAP-T12`  
**Family:** `containment`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use when hierarchy is expressed primarily through explicit containment at two or more depths.

## Required semantics

- Retain every parent-child containment.
- Preserve depth and items outside all containers.

## Allowed abstract roles

- `container`
- `item`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use relationship edges only for non-containment relations.
- Represent containment through group membership and parent groups.

## Label rules

- Use supplied container and item names.
- Keep depth labels optional and factual.

## Complexity behavior

- Split deep subtrees into linked details before flattening them.
- Retain singleton containers when semantically declared.

## Semantic invariants

- `requires-nested-groups`
- `group-membership-complete`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer containment from proximity.
- Do not accept cyclic parent groups.

## Coverage

- Positive semantic test: `T-TYPE-12-SEM`.
- Boundary mutation: `flatten-nested-groups`.
- Later render smoke evidence remains required in each approved visual mode.
