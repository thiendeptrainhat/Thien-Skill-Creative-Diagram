# Sequence semantic grammar

**Canonical ID:** `sequence`  
**Capability:** `CAP-T04`  
**Family:** `ordered-interaction`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for time-ordered messages among actors or systems, including optional guarded fragments.

## Required semantics

- Identify every participant.
- Preserve total message order and guarded fragment membership.

## Allowed abstract roles

- `actor`
- `system`
- `participant`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed message edges with unique non-negative order.
- Distinguish request, response, asynchronous, and return kinds when supplied.

## Label rules

- Use supplied participant names and message verbs.
- Keep guards on fragment or message semantics.

## Complexity behavior

- Split long exchanges at a stable semantic checkpoint.
- Never reorder messages to reduce crossings.

## Semantic invariants

- `minimum-two-nodes`
- `message-edges`
- `unique-edge-order`
- `contiguous-edge-order`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer a response that is absent.
- Do not encode time order through vertical position alone.

## Coverage

- Positive semantic test: `T-TYPE-04-SEM`.
- Boundary mutation: `duplicate-message-order`.
- Later render smoke evidence remains required in each approved visual mode.
