# P-19B review-41 — slope-graph

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-41-1.5.0`  
**Authority:** D-121, retaining D-084–D-120 gallery scope  
**Status:** implementation and exact verification `PASS`; owner approval pending

## Outcome

Review-41 preserves the 14 exact P-18 anchors, the 93-file P-19 scope and every D-086–D-120 remediation. It changes only the three CAP-V18 specimens and one preview: display identity is now `slope-graph`, while internal ID `CAP-V18` and parent `line-chart` remain stable.

The new chart has seven independent series at exactly two states on one 0–100% scale, 14 directly labelled endpoints, five rises, two falls, nine rank-changing crossings and one coral/direct-labelled focal series. Endpoint value, direction and rank are exposed both visually and in an exact seven-row alternative table. The approved P-18-derived template is unchanged.

## Preservation and verification

- Exact review-40 archive: 602 snapshot files verified.
- Protected corpus: 17540 files verified.
- Target mutation: 3 slopegraph HTML replaced by 3 `slope-graph` HTML + 1 neutral-light preview.
- Non-target preservation: 90 HTML artworks after candidate-ID normalization; 30 previews byte-identical.
- Gallery/comparison counts remain 93 P-19 HTML, 31 previews and 107 combined diagrams.
- Exact review-41 verification: `PASS`; 7 series, 14 endpoints, 2 state axes, 6 ticks, 5 rises, 2 falls, 9 crossings, 1 focal, seven-row table and three-mode geometry verified.
- Focused slope/scope tests: `11/11 PASS`; static verification: `34/34 PASS`; full regression: `400/400 PASS`.
- Neutral-light 2000×980 raster: locally inspected.

Browser execution remains `BLOCKED_URL_POLICY`; local raster inspection is not a browser PASS. P-19B review-41 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation is authorized.

---

# Historical: P-19B review-40 — Bubble chart

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-40-1.5.0`  
**Authority:** D-120, retaining D-084–D-119 gallery scope  
**Status:** implementation and exact verification `PASS`; owner approval pending

## Outcome

Review-40 preserves the 14 exact P-18 anchors, the 93-file P-19 scope and every D-086–D-119 remediation. It changes only the three CAP-V20 specimens and one preview: display identity is now `bubble`, while internal ID `CAP-V20` and parent `scatter-plot` remain stable.

The new chart has seven independent observations in three series, two arrow-free linear axes, eight x ticks, nine y ticks, exact values inside each bubble, and one coral/direct-labelled focal observation. Bubble radius uses a square-root scale, producing a constant `radius²/value = 57.8`; visible area therefore represents magnitude correctly. The approved P-18-derived template is unchanged.

## Preservation and verification

- Exact review-39 archive: 591 snapshot files verified.
- Protected corpus: 16948 files verified.
- Target mutation: 3 Bubble HTML + 1 neutral-light preview.
- Non-target preservation: 90 HTML artworks after candidate-ID normalization; 30 previews byte-identical.
- Gallery/comparison counts remain 93 P-19 HTML, 31 previews and 107 combined diagrams.
- Focused Bubble and gallery-scope tests: `11/11 PASS`.
- Static verification: `34/34 PASS`.
- Full regression: `397/397 PASS`.
- Exact review-40 verification: `PASS`; seven bubbles, three series, two axes, 8/9 ticks, one focal, seven-row table, area scale and three-mode geometry all verified.
- Neutral-light 2000×1040 raster: locally inspected.

Browser execution remains `BLOCKED_URL_POLICY`; local raster inspection is not a browser PASS. P-19B review-40 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation is authorized.
