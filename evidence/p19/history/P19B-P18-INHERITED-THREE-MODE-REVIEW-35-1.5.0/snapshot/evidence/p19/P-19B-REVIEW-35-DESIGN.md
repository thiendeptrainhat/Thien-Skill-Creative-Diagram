# P-19B review-35 — solid-line radar correction

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-35-1.5.0`  
**Authority:** D-115, retaining D-084–D-114 scope

## Owner correction

The owner rejected the dashed comparison profiles in review-34 and required the radar to follow the supplied reference more closely: every profile boundary must use a continuous solid stroke.

## Locked implementation

- Preserve the five axes, common 0–10 scale, five rings, four profiles, twenty values, marker positions, labels, legend placement and exact alternative table from review-34.
- Render all four closed profile polygons and all four legend samples with solid lines; no radar profile or radar legend sample may declare `stroke-dasharray`.
- Retain non-color differentiation through four distinct marker shapes, direct legend labels and the focal `KHUYẾN NGHỊ` role. Color remains supplemental.
- Preserve identical geometry across neutral-light, neutral-dark and editorial modes.
- Mutate only the three radar HTML files and one radar preview beyond candidate metadata; preserve 90 non-target HTML artworks and 30 non-target previews.

The owner reference is a structural and visual rubric only. Data, labels, semantic IDs, CSS, SVG and coordinates remain independently authored.
