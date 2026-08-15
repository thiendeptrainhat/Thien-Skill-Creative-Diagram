# Layer stack semantic grammar

**Canonical ID:** `layer-stack`  
**Capability:** `CAP-T15`  
**Family:** `ordered-layers`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for ordered abstraction, enforcement, or control layers with explicit dependencies.

## Required semantics

- Represent each layer as an ordered lane.
- Preserve dependencies that skip layers and cross-cutting controls.

## Allowed abstract roles

- `layer-item`
- `control`
- `cross-cutting-control`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed dependency, enforcement, or compensation edges.
- Never imply adjacency is a dependency.

## Label rules

- Use supplied layer, owner, and control names.
- Label skipped-layer dependencies explicitly.

## Complexity behavior

- Split control catalogs by owner while retaining layer order.
- Do not merge layers with different enforcement locations.

## Semantic invariants

- `minimum-two-layers`
- `unique-layer-order`
- `requires-layer-members`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer a maturity ranking from vertical position.
- Do not hide cross-layer dependencies.

## Coverage

- Positive semantic test: `T-TYPE-15-SEM`.
- Boundary mutation: `duplicate-layer-order`.
- Later render smoke evidence remains required in each approved visual mode.
