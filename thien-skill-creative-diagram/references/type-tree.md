# Tree semantic grammar

**Canonical ID:** `tree`  
**Capability:** `CAP-T13`  
**Family:** `hierarchy`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for one-root parent-child hierarchy where every non-root item has exactly one parent.

## Required semantics

- Identify one root and preserve every parent-child relation.
- Retain leaf decisions or outcomes.

## Allowed abstract roles

- `root`
- `branch`
- `leaf`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed parent-to-child edges.
- Require exactly n-1 hierarchy edges for n nodes.

## Label rules

- Use supplied item labels.
- Put branch conditions on edges when applicable.

## Complexity behavior

- Split at a stable subtree boundary.
- Never duplicate a multi-parent node to force tree validity.

## Semantic invariants

- `requires-tree`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not accept cycles or multiple roots.
- Do not hide a second parent.

## Coverage

- Positive semantic test: `T-TYPE-13-SEM`.
- Boundary mutation: `add-second-parent`.
- Later render smoke evidence remains required in each approved visual mode.
