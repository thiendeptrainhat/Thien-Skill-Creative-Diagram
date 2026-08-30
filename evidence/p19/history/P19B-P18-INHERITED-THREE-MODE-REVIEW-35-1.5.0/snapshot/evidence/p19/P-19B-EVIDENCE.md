# P-19B review-35 — solid-line radar correction

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-35-1.5.0`  
**Authority:** D-115, retaining D-084–D-114 gallery scope  
**Status:** implementation and automated verification `PASS`; owner approval pending

## Outcome

Review-35 preserves the 14 exact P-18 anchors and the 93-file P-19 scope, then corrects only the canonical P-19 radar line treatment. All four closed profile polygons and all four legend samples now use continuous solid strokes, matching the supplied reference's profile treatment. Radar CSS and SVG contain no profile `stroke-dasharray`.

The five axes, common 0–10 domain, five rings, four profiles, twenty exact values, marker coordinates, labels, legend placement and exact twenty-row alternative table remain unchanged from review-34. The recommended profile remains coral with circular markers and direct `KHUYẾN NGHỊ` text. The other profiles remain distinguishable without line dashes through square, triangle and diamond markers plus direct legend labels.

## Preservation and verification

- Exact review-34 archive: 548 snapshot files verified.
- Protected corpus: 14117 files verified.
- Target mutation: 3 radar HTML + 1 neutral-light preview.
- Non-target preservation: 90 HTML artworks after candidate-ID normalization; 30 previews byte-identical.
- Gallery/comparison counts remain 93 P-19 HTML, 31 previews and 107 combined diagrams.
- Focused radar tests: `9/9 PASS`.
- Gallery-scope tests: `8/8 PASS`.
- Static verification: `34/34 PASS`.
- Full regression: `382/382 PASS`.
- Exact review-35 verification: `PASS` with `profile_line_style = solid-only`.
- Neutral-light 2000×1040 raster: locally inspected.

Browser execution remains `BLOCKED_URL_POLICY`; local raster inspection is not a browser PASS. P-19B review-35 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation is authorized.
