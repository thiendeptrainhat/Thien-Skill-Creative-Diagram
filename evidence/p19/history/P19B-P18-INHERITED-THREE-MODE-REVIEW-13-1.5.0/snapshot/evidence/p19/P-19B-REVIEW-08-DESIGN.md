# P-19B review-08 — D-088 bar-chart contract

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-08-1.5.0`  
**Authority:** D-088 — owner requested `bar-chart` to follow the supplied eight-column comparison reference  
**Status:** implementation candidate; owner review pending; P-19C unauthorized

## Design premise

Help a reviewer compare eight sprint outcomes in one glance while preserving exact-value lookup and making the record high unmistakable without relying on hue alone.

## Reference analysis and independent realization

Observed transferable traits: a wide categorical bar chart, common zero baseline, quiet horizontal grid, direct value labels, eight ordered categories, one accent record-high bar, and a compact legend below the plot. The attachment is a visual rubric/data source only. This implementation uses original Vietnamese labels, distinct synthetic values, independent coordinates, repository-native typography/tokens and newly authored SVG/CSS.

## Locked material and geometry

- One series `series-sprint-points`, eight ordered point IDs `sprint-01`…`sprint-08`.
- X axis `axis-sprint`; Y axis `axis-story-points`, linear 0–120, unit `điểm`.
- One explicit annotation `annotation-record-high` targeting only `sprint-05`; the target value must equal the unique maximum.
- Content-fit viewBox `1800 × 940`; eight equal-width bars aligned to the same zero baseline.
- Six grid/tick levels at 20-point intervals; axes never use arrow markers.
- Every bar carries a direct numeric label and category label. The focal bar repeats its meaning through accent fill/stroke, accent value/category label, legend text and alternative-table status.
- The chart owns its legend and alternative exact-value table. Neutral-light, neutral-dark and editorial share identical SVG geometry and semantics; only P-18-derived semantic color roles change.

## Preserve / repair / extend / retire

- **Preserve:** exact P-18 review-17 visual grammar; D-086 Fishbone; D-087 dp-integration; all other review-07 artwork; 87-HTML/29-preview scope.
- **Repair:** replace the two-column placeholder bar chart with an eight-category, direct-labelled, truthful-scale comparison.
- **Extend:** chart-specific layout, validation, semantic table, focused tests and three raster proofs.
- **Retire:** the review-07 bar-chart artwork only; review-07 remains recoverable byte-bound in history.

## Verification matrix

- Exact 8 bars, 2 axes, 6 ticks, 1 focal bar and all semantic IDs serialize.
- Zero baseline, 0–120 domain, numeric values, ordered categories and unique maximum fail closed under mutation.
- Three modes have identical SVG geometry and pass the serializer validator.
- Exactly three bar-chart HTML files change; 84 non-target HTML preserve artwork after candidate-ID normalization and 28 non-target previews remain byte-identical.
- Exact-value alternative table contains all eight point IDs.
- Render all three modes, inspect full-resolution raster, then run focused, scope, static and full regression checks.

Browser execution remains `blocked / not executable` under the existing local-file policy. This does not imply owner approval, P-19C, G-04, package, `dist`, publication, Git or Release authorization.
