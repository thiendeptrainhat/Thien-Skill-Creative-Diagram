# P-19B review-36 — marker-free radar correction

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-36-1.5.0`  
**Authority:** D-116, retaining D-084–D-115 gallery scope  
**Status:** implementation and automated verification `PASS`; owner approval pending

## Outcome

Review-36 preserves the 14 exact P-18 anchors and the 93-file P-19 scope, then changes only the canonical P-19 radar. All circle, square, triangle and diamond data-point markers are removed from the plot in every mode. The previous center dot is also removed, so the plot interior contains no standalone marker shape. The four comparison profiles and legend samples remain continuous solid lines.

The five axes, common 0–10 domain, five rings, four profiles, twenty exact values, labels, legend placement and exact twenty-row alternative table remain unchanged. Compact shape swatches are retained only in the footer legend outside the plot so the four series remain distinguishable without relying on color alone.

## Preservation and verification

- Exact review-35 archive: 556 snapshot files verified.
- Protected corpus: 14666 files verified.
- Target mutation: 3 radar HTML + 1 neutral-light preview.
- Non-target preservation: 90 HTML artworks after candidate-ID normalization; 30 previews byte-identical.
- Gallery/comparison counts remain 93 P-19 HTML, 31 previews and 107 combined diagrams.
- Focused radar tests: `10/10 PASS`.
- Gallery-scope tests: `8/8 PASS`.
- Static verification: `34/34 PASS`.
- Full regression: `383/383 PASS`.
- Exact review-36 verification: `PASS`; `markers = 0`, `profile_line_style = solid-only`, `interior_center_marker = removed`.
- Neutral-light 2000×1040 raster: locally inspected.

Browser execution remains `BLOCKED_URL_POLICY`; local raster inspection is not a browser PASS. P-19B review-36 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation is authorized.
