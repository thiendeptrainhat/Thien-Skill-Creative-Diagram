# P-19B review-39 — thin-stroke process

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-39-1.5.0`  
**Authority:** D-119, retaining D-084–D-118 scope  
**Status:** implementation/verification candidate; owner approval separate

## Repair contract

- Preserve every D-118 node, route, label, position, document contact, arrowhead and template decision.
- Reduce regular node borders from `1.45` to `1.2` and focal node borders from `1.8` to `1.6`.
- Reduce straight connector strokes from `1.45` to `1.0` and merge connector strokes from `1.8` to `1.2`.
- Reduce document layer strokes to `1.0/1.2`, badge borders to `0.8` and the footer rule to `0.8`.
- Keep the paint hierarchy `connector < regular node < focal node` and preserve visible arrowheads.
- Change no geometry, content, palette, typography, spacing, route kind or connector endpoint.

## Verification

- Exact D-118 geometry and five continuous document-boundary contacts remain byte-equivalent after candidate normalization.
- Exact route inventory remains nine straight plus two rounded-orthogonal exceptions.
- Three modes share identical geometry.
- Ninety non-target HTML artworks and thirty non-target previews remain preserved.
