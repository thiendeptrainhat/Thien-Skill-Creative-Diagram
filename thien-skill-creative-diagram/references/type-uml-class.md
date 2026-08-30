# UML class semantic grammar

**Canonical ID:** `uml-class`  
**Capability:** `CAP-T37`  
**Family:** `typed-structure`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for classes with structured attributes, operations, visibility, signatures, multiplicities, and typed relationships.

## Required semantics

- Preserve every supplied class member and signature.
- Retain relation kind, endpoint, direction, and multiplicity.

## Allowed abstract roles

- `class`
- `attribute`
- `operation`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use typed UML relations only when supplied.
- Anchor member-level relations to declared members.

## Label rules

- Use exact class, member, type, signature, and multiplicity labels.
- Do not shorten a signature by changing meaning.

## Complexity behavior

- Split large class compartments while preserving member ownership.
- Do not merge homonymous members.

## Semantic invariants

- `uml-class-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer inheritance from naming.
- Do not replace a typed relation with an unlabeled line.

## Coverage

- Positive semantic test: `T-TYPE-37-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-37-BOUND-01`, `T-TYPE-37-HARD-01`, and `T-TYPE-37-A11Y-01`.
- Boundary mutation: `remove-uml-relation-kind`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
