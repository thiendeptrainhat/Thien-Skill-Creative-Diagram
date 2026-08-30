# P-19B review-23 — complete borders and uniform real gaps

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-23-1.5.0`  
**Authority:** D-103, retaining D-084–D-102  
**Status:** implementation evidence; owner approval pending

## Design contract

- **Outcome:** every Treemap region must show an uninterrupted four-edge border and equal physical spacing from adjacent regions, matching the owner reference's boundary rhythm.
- **Preserve:** six-leaf values and hierarchy, exact allocation-area/value shares, 8.10B total, five direct labels, compact Oceania marker, focal Asia treatment, exact-value table and three-mode geometry.
- **Retire:** review-22's canvas-colored under-stroke, because the visible tile outlines still occupied shared allocation boundaries and did not create true geometric separation.
- **Repair:** inset every visible rectangle by 4 SVG units from all four allocation edges. Two adjacent regions therefore produce a real 8-unit gap. Each visible rectangle has its own complete connector outline; Asia uses its own complete coral outline.
- **Quantitative integrity:** invisible allocation coordinates remain exact and are serialized as `data-allocation-*`; visible cell inset is disclosed separately and never substituted for the value encoding.
- **Accessibility:** complete borders, physical spacing, direct labels and the exact-value table redundantly distinguish cells without relying on fill color.
- **Verification:** six four-edge declarations, six uniform insets, 8-unit shared gaps, exact allocation-area reconciliation and identical geometry across three modes; review-22 archive/protected bytes and all 87/29 non-target artifacts preserved.

The supplied screenshot is used only as a QA reference for complete boundary and spacing principles. No prose, CSS, SVG, coordinates, template or asset is copied.
