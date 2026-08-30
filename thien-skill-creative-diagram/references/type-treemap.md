# Treemap semantic grammar

**Canonical ID:** `treemap`  
**Capability:** `CAP-T29`  
**Family:** `hierarchical-quantitative`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for a rooted part-to-whole hierarchy whose leaf magnitude is encoded by area.

## Required semantics

- Bind every quantitative leaf to exactly one parent group.
- Reconcile every group child sum to its declared total and unit.

## Allowed abstract roles

- `leaf`
- `group`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use containment rather than relationship edges for hierarchy.
- Keep cross-hierarchy relations outside the area encoding.

## Label rules

- Use exact group, leaf, value, and unit labels.
- Keep zero leaves in the accessible hierarchy.

## Complexity behavior

- Split deep or dense branches without flattening ancestry.
- Never drop a zero-valued leaf to save space.

## Semantic invariants

- `treemap-hierarchy-reconciles`
- `requires-accessible-data`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not accept a cyclic or multi-root hierarchy.
- Do not infer a missing total or unit conversion.

## Coverage

- Positive semantic test: `T-TYPE-29-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-29-BOUND-01`, `T-TYPE-29-HARD-01`, and `T-TYPE-29-A11Y-01`.
- Boundary mutation: `break-treemap-total`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
