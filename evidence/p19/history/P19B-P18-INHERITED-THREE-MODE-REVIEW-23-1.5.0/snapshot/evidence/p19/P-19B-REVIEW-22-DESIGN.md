# P-19B review-22 — bordered exact-area Treemap

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-22-1.5.0`  
**Authority:** D-102, retaining D-084–D-101  
**Status:** implementation evidence; owner approval pending

## Design contract

- **Outcome:** make every Treemap region visibly bounded like the owner reference while preserving exact area/value encoding.
- **Preserve:** six-leaf hierarchy, exact 8.10B total, all tile coordinates and areas, five direct labels, the compact Oceania marker, exact-value table, three-mode geometry and all non-target artwork.
- **Repair:** review-21 used a canvas-colored stroke as a separation gutter; this created spacing but did not visibly outline non-focal tiles.
- **Implementation:** retain an 8px canvas-colored under-stroke as the gutter, then draw a 2.4px connector border on every ordinary tile and a 3.2px coral border on the focal Asia tile.
- **Accessibility:** borders, direct labels, position and the exact-value table make boundaries and focus non-color-dependent.
- **Verification:** six visible tile borders and six gutters in each mode; exact areas unchanged; review-21 archive/protected bytes verified; 87 non-target HTML artworks and 29 non-target previews preserved.

The supplied screenshot is used only as a QA reference for visible boundary treatment. No prose, code, coordinates, CSS, template or asset is copied.
