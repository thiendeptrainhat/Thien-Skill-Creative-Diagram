# P-19B review-18 — D-098 polar-chart remediation

Status: `implemented; automated verification PASS; owner review pending`

## Owner direction

Replace only the P-19 `polar-chart` with a detailed radial-spoke design comparable in information density and hierarchy to the supplied image. The image is a visual rubric, not an implementation source.

## Independent design contract

- One original illustrative series with eight ordered UTC windows.
- One common origin and eight straight radial spokes; radius is proportional to the exact value on a linear `0–100%` scale.
- Five concentric rings at `20 / 40 / 60 / 80 / 100`.
- Every window has a direct category label, an exact percentage and an open endpoint marker.
- The unique maximum is redundant without color: coral stroke, increased stroke width, coral endpoint, direct `ĐỈNH` label and `Đỉnh ngày` table role.
- Axes/spokes have no arrowheads and there are no filled wedge marks.
- Neutral-light, neutral-dark and editorial reuse the same semantic material and exact geometry; only P-18 semantic color roles vary.
- The accessible alternative contains exactly eight data rows.

## Scope lock

The exact review-17 candidate was archived before mutation. Only three `polar-chart` HTML specimens and one neutral-light preview may change. The other 87 HTML specimens and 29 previews must remain identical after candidate-ID normalization. P-18, P-19A, package, `dist`, publication mirrors, Release and P-19C remain outside this change.

## Provenance

All fixture values, Vietnamese prose, IDs, geometry, CSS and SVG are original to this repository. No code, coordinates, prose, CSS, SVG or template was copied from the attached image.
