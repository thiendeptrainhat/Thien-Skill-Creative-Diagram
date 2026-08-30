# Database schema semantic grammar

**Canonical ID:** `database-schema`  
**Capability:** `CAP-T39`  
**Family:** `physical-data-model`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for physical tables with columns, SQL data types, constraints, ordered indexes, and column-level foreign keys.

## Required semantics

- Preserve column and index membership under each table.
- Keep ordered index column IDs, uniqueness, and foreign-key member endpoints exact.

## Allowed abstract roles

- `table`
- `column`
- `index`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use foreign-key edges anchored to source and target columns.
- Keep physical schema semantics distinct from conceptual ER relationships.

## Label rules

- Use exact table, column, data type, constraint, and index labels.
- Expose index order in accessible text.

## Complexity behavior

- Split dense schemas by bounded context while retaining cross-schema keys.
- Do not hide composite index order.

## Semantic invariants

- `database-schema-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer a key from a naming convention.
- Do not accept a foreign or non-column index member.

## Coverage

- Positive semantic test: `T-TYPE-39-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-39-BOUND-01`, `T-TYPE-39-HARD-01`, and `T-TYPE-39-A11Y-01`.
- Boundary mutation: `reorder-database-index`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
