# Wardley map semantic grammar

**Canonical ID:** `wardley-map`  
**Capability:** `CAP-T32`  
**Family:** `strategy-map`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for components placed by supplied value-chain position and evolution coordinates with explicit dependencies.

## Required semantics

- Preserve both normalized coordinates for every component.
- Retain dependency endpoints and direction.

## Allowed abstract roles

- `component`
- `dependency`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use directed dependency edges.
- Treat coordinates as supplied strategic evidence, not layout suggestions.

## Label rules

- Use exact component and annotation labels.
- Disclose both axis meanings and bounds.

## Complexity behavior

- Use labels or callouts for collisions without moving data positions.
- Split annotations before changing coordinates.

## Semantic invariants

- `wardley-coordinates-valid`
- `directed-edges`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not infer build, buy, or move decisions.
- Do not clamp an out-of-domain coordinate.

## Coverage

- Positive semantic test: `T-TYPE-32-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-32-BOUND-01`, `T-TYPE-32-HARD-01`, and `T-TYPE-32-A11Y-01`.
- Boundary mutation: `move-wardley-coordinate-outside-domain`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
