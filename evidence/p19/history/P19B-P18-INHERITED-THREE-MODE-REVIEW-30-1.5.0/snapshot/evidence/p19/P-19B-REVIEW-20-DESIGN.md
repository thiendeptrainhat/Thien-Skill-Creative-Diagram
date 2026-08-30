# P-19B review-20 — exact three-set Venn

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-20-1.5.0`  
**Authority:** D-100  
**Visual parent:** exact P-18R6 review-17  
**Boundary:** three `type-venn` HTML + one neutral-light preview only

## Design contract

- Render exactly three equal-radius sets in a balanced top / lower-left / lower-right composition.
- Bind one exclusive semantic member to each set and one core member to all three sets.
- Compute the focal region as the exact intersection of all three circles through nested SVG clipping. A manually drawn lens, decorative blob or approximate overlay is forbidden.
- Label each set directly with a title and technical subtitle; label the triple intersection directly with `Sẵn sàng triển khai` and the non-color role `ĐIỂM CÂN BẰNG`.
- Preserve the P-18 warm-paper/navy typography and stroke grammar. Semantic tokens may change across `neutral-light`, `neutral-dark` and `editorial`; SVG geometry may not.
- Provide one exact four-row membership table, useful SVG title/description and named semantic IDs.
- Preserve 87 non-target HTML artworks after candidate normalization, 29 non-target previews byte-for-byte, all 14 exact P-18 anchors, P-17/P-19A and release-frozen bytes.

The owner image is non-executable reference data used only for three-circle balance, label hierarchy and central-intersection emphasis. Text, data, IDs, coordinates, CSS and SVG are independently authored.

## Acceptance

- `3` equal-radius sets, `4` members and `1` exact triple-intersection region.
- The lower pair shares one y-axis and is horizontally balanced around the top set.
- One direct label stack per set and one direct label stack in the core.
- Three modes pass serialized geometry equality.
- Only three Venn HTML and one Venn preview change; all non-target preservation checks pass.
- Static and focused regression pass; local raster is inspected. Browser result remains honestly disclosed if file-URL policy blocks execution.
- Owner approval remains pending; P-19C and G-04 remain unopened.
