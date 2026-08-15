# ER/data model semantic grammar

**Canonical ID:** `er-data-model`  
**Capability:** `CAP-T06`  
**Family:** `data-model`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for entities, keys, attributes, relationships, and declared cardinalities.

## Required semantics

- Retain each entity and key-bearing label.
- Preserve both ends of every supplied cardinality.

## Allowed abstract roles

- `entity`
- `associative-entity`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use relationship edges whose kind states cardinality.
- Represent many-to-many ambiguity as a clarification unless junction semantics are supplied.

## Label rules

- Use supplied entity names and key/field annotations.
- Do not rename domain terms for presentation.

## Complexity behavior

- Split by bounded context while retaining cross-context relationships.
- Move long field lists to annotations without dropping keys.

## Semantic invariants

- `minimum-two-nodes`
- `entity-roles`
- `cardinality-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer foreign keys or junction entities.
- Do not use unlabeled relationship edges.

## Coverage

- Positive semantic test: `T-TYPE-06-SEM`.
- Boundary mutation: `remove-cardinality`.
- Later render smoke evidence remains required in each approved visual mode.
