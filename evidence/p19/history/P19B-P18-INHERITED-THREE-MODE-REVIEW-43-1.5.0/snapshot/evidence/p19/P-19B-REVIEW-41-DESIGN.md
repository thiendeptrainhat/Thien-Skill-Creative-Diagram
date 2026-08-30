# P-19B review-41 — slope-graph

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-41-1.5.0`  
**Authority:** D-121, retaining D-084–D-120  
**Status:** implementation and exact verification `PASS`; owner approval pending

## Design translation

The owner reference is treated only as an abstract slope-graph rubric: compare multiple named series at exactly two states, label both endpoints directly, preserve direction/rank/crossing, and disclose exact values. No source prose, data, logo, coordinates, CSS, SVG, template or asset is copied.

The independent implementation uses seven Vietnamese product groups on a common 0–100% scale. It emits 14 exact endpoints, five rises, two falls and nine rank-changing crossings. One focal series is identified redundantly by coral line, filled endpoints, direct labels and exact-table role. State axes are plain thin lines with no arrowheads. The approved P-18-derived shell, typography, palette, frame and three-mode system remain unchanged.

## Verification contract

- Display identity: `slope-graph`; internal capability: `CAP-V18`; canonical parent: `line-chart`.
- Exactly 7 series, 14 endpoints, 2 state axes, 6 scale ticks, 1 focal series and 7 alternative-table rows.
- Exactly two shared states for every series; one truthful linear 0–100% y scale.
- Direct label/value at both endpoints; machine-readable direction and left/right rank.
- At least one rise, one fall and one crossing; active fixture resolves to 5/2/9.
- Three modes share identical geometry.
- Review-40 archived before mutation; 90 non-target HTML preserved after candidate normalization and 30 non-target previews byte-identical.
- P-19C, package, `dist`, publication, Git and Release remain unauthorized.
