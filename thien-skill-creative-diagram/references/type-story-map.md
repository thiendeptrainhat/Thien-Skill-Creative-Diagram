# Story map semantic grammar

**Canonical ID:** `story-map`  
**Capability:** `CAP-T38`  
**Family:** `narrative-backlog`  
**Phase boundary:** semantic contract only; layout, visual tokens, rendering, and export are not defined here.

## Use case

Use for a narrative backbone with ordered stories, release slices, and an explicit cut status.

## Required semantics

- Preserve backbone and story order.
- Represent unassigned stories with a null release slice and unassigned cut status.

## Allowed abstract roles

- `backbone`
- `story`
- `release-slice`

Bind these roles to original visual shapes only in an authorized visual phase. Do not infer semantics from appearance.

## Edge rules

- Use containment for release-slice membership.
- Keep cut-line status distinct from story priority.

## Label rules

- Use exact backbone, story, and release labels.
- Name unassigned status explicitly.

## Complexity behavior

- Split dense slices without reassigning stories.
- Do not force an unassigned story into a release.

## Semantic invariants

- `story-map-valid`

Run `scripts/semantic_grammars.py::validate_typed_ir` after common IR validation. A failed invariant returns a named error and no artifact.

## Anti-patterns

- Do not accept inconsistent null/slice status pairs.
- Do not infer release scope from position.

## Coverage

- Positive semantic test: `T-TYPE-38-POS-01`.
- Stable boundary/hard/a11y families: `T-TYPE-38-BOUND-01`, `T-TYPE-38-HARD-01`, and `T-TYPE-38-A11Y-01`.
- Boundary mutation: `mismatch-story-release-pairing`.
- Render test remains deferred until the applicable P-18/P-19 visual phase is authorized.
