# P-19B review-32 — thin-stroke Treemap

## Route and design contract

- **Intent / scope:** reduce only the visible border weight of one P-19B identity (`treemap`).
- **Visual thesis:** retain the exact quantitative area hierarchy and complete separated tile boundaries, but bring their paint weight back into the quiet P-18-derived line system used by the surrounding diagrams.
- **Preserve:** D-101 values and allocation areas; D-103 four-edge outlines, 4-unit inset and 8-unit shared gaps; labels, legend, table, all geometry, three-mode derivation, D-111 and earlier scope, frozen P-17/P-19A/P-18.
- **Change:** regular tile outline `2.4 → 1.2`, focal tile outline `3.2 → 1.6`, footer rule `1.5 → 1.0`, focal legend swatch `2.5 → 1.6`, regular legend swatch `1.5 → 1.2`.
- **Hierarchy:** focal remains heavier than regular (`1.6 > 1.2`); every tile retains a real stroke and all four visible edges.
- **Verification:** exact review-31 archive; old/current target SVG geometry equality; three-mode geometry equality; 87 non-target HTML preserved after candidate normalization; 29 non-target previews byte-identical; neutral-light raster inspection.

## Boundary

This is owner-review material, not owner approval. Browser execution remains `BLOCKED_URL_POLICY`; local deterministic SVG raster inspection is retained. P-19C, G-04, package, `dist`, publication, Git and Release are not performed.
