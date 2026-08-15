# High-Level semantic grammar

**Canonical ID:** `high-level`  
**Capability:** `CAP-T22`  
**Family:** `platform-overview`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for an end-to-end stage or platform overview with grouped cross-cutting concerns.

## Required semantics

- Retain stage order, groups, and cross-cutting control span.
- Keep overview semantics distinct from tier promotion and source-platform-consumer topology.

## Allowed abstract roles

- `stage`
- `capability`
- `cross-cutting-control`
- `boundary`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed progression or dependency edges when supplied.
- Express cross-cutting scope through explicit membership or targets.

## Label rules

- Use supplied stage and control labels.
- Do not add implementation details absent from the overview.

## Complexity behavior

- Split supporting capabilities into details while retaining the end-to-end story.
- Do not flatten cross-cutting concerns into one stage.

## Semantic invariants

- `requires-stage-groups`
- `requires-progression`
- `requires-cross-cutting-annotation`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not route tier promotion here when Medallion is dominant.
- Do not invent platform components.

## Coverage

- Positive semantic test: `T-TYPE-22-SEM`.
- Boundary mutation: `remove-high-level-groups`.
- Later render smoke evidence remains required in each approved visual mode.
