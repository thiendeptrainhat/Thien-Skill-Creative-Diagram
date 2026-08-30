# Fishbone semantic grammar

**Canonical ID:** `fishbone`  
**Capability:** `CAP-T31`  
**Family:** `cause-analysis`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use to organize supplied cause categories and causes that converge on one declared effect.

## Required semantics

- Declare exactly one effect.
- Assign every cause to exactly one explicit cause category.

## Allowed abstract roles

- `cause`
- `effect`
- `cause-category`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Direct every cause relation toward the effect.
- Do not encode an unprovided causal strength.

## Label rules

- Use supplied cause, category, and effect labels.
- Distinguish analysis structure from proof of causation.

## Complexity behavior

- Split long cause lists within their category.
- Never merge categories to simplify geometry.

## Semantic invariants

- `fishbone-structure-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not leave orphan causes.
- Do not present the arrangement as causal proof.

## Coverage

- Positive semantic test: `T-TYPE-31-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-31-BOUND-01`, `T-TYPE-31-HARD-01`, and `T-TYPE-31-A11Y-01`.
- Boundary mutation: `orphan-fishbone-cause`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
