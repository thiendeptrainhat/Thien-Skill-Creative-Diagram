# User journey semantic grammar

**Canonical ID:** `user-journey`  
**Capability:** `CAP-T34`  
**Family:** `experience-sequence`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for an ordered journey whose stages retain actions, touchpoints, and optional declared sentiment.

## Required semantics

- Preserve stage order, action, and touchpoint.
- Preserve supplied normalized numeric sentiment or exact categorical sentiment; never convert between them.

## Allowed abstract roles

- `stage`
- `action`
- `touchpoint`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use progression edges only when explicitly supplied.
- Do not infer causality from sentiment changes.

## Label rules

- Use exact stage, action, and touchpoint labels.
- Provide a text equivalent for sentiment.

## Complexity behavior

- Split long narratives by stage without reordering them.
- Never replace narrative facts with a sentiment curve.

## Semantic invariants

- `user-journey-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not invent a missing touchpoint.
- Do not encode sentiment only by color.

## Coverage

- Positive semantic test: `T-TYPE-34-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-34-BOUND-01`, `T-TYPE-34-HARD-01`, and `T-TYPE-34-A11Y-01`.
- Boundary mutation: `duplicate-journey-stage-order`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
