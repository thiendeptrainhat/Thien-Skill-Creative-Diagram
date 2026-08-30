# P-19B review-40 — Bubble chart

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-40-1.5.0`  
**Authority:** D-120, retaining D-084–D-119  
**Status:** implemented and exactly verified; owner approval pending

## Identity contract

- Public/display identity: `bubble`.
- Stable internal capability ID: `CAP-V20`.
- Canonical parent: `scatter-plot`.
- The three modes are `neutral-light`, `neutral-dark` and `editorial`; only semantic tokens may differ. SVG geometry must remain identical.

## Visual and data contract

Render one independent 2000×1040 Bubble chart inside the existing P-18-derived template. It contains exactly seven observations divided across three series, two arrow-free linear axes, eight x ticks, nine y ticks, fine grid lines, one size axis and one focal observation.

Bubble radius is `68 × sqrt(value / 80)`, so visible area is proportional to the encoded magnitude. Every bubble carries its exact value. The focal observation is redundantly identified by coral boundary, soft coral fill, direct label and the exact alternative table; color is never the sole signal.

Preserve the approved warm-paper/navy/coral palette, typography roles, artifact frame, spacing system, thin stroke hierarchy, legend rail, exact table and three-mode system. Do not reproduce the reference image's dark panel, prose, data, coordinates, CSS, SVG, template or assets.

## Scope and verification

Only the three `cap-cap-v20-bubble` specimens and their neutral-light preview may change. Review-39 must be archived before mutation. Ninety non-target HTML artworks must remain equal after candidate normalization and thirty non-target previews must remain byte-identical.

Verification must assert: seven bubbles, three series, two plain axes, eight x ticks, nine y ticks, one focal bubble, seven exact table rows, constant `radius²/value`, no overlap, direct values, stable internal ID/parent binding, and geometry identity across all three modes. P-19C, G-04, package, `dist`, publication, Git and Release remain outside authority.
