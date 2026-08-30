# P-19B review-43 — ridgeline

**Candidate:** `P19B-P18-INHERITED-THREE-MODE-REVIEW-43-1.5.0`  
**Authority:** D-123, retaining D-084–D-122 gallery scope  
**Status:** implementation and exact verification `PASS`; owner approval pending

## Outcome

Review-43 preserves the 14 exact P-18 anchors, the 93-file P-19 scope and every D-086–D-122 remediation. It changes only the three CAP-V19 specimens and one preview: display identity is now `ridgeline`, while internal ID `CAP-V19` and parent `line-chart` remain stable.

The new chart has twelve density rows on one shared 0–120 ms linear domain and one global-max amplitude contract. Every row uses the same twenty-point Gaussian-KDE grid and bandwidth 7 ms, with nested 50/80/95% quantile bands plus a median dot. One shared-median reference and one coral/direct-labelled focal row provide context. Exact per-row quantiles are exposed in a twelve-row alternative table. The approved P-18-derived template is unchanged.

## Preservation and verification

- Exact review-42 archive: 624 snapshot files verified.
- Protected corpus: 18757 files verified.
- Target mutation: 3 CAP-V19 HTML replaced by 3 `ridgeline` HTML + 1 neutral-light preview.
- Non-target preservation: 90 HTML artworks after candidate-ID normalization; 30 previews byte-identical.
- Gallery/comparison counts remain 93 P-19 HTML, 31 previews and 107 combined diagrams.
- Focused ridgeline/gallery/scope regression: `35/35 PASS`; P-19B static verification: `34/34 PASS`; full script regression: `406/406 PASS`.
- Exact review-43 verification: `PASS`; 12 ridges, 12 medians, 36 quantile bands, 1 shared reference, 1 axis, 7 ticks, 1 focal, 228 curved profile segments, twelve-row table and three-mode geometry verified.
- Neutral-light 2000×1180 raster: locally inspected.

Browser execution remains `BLOCKED_URL_POLICY`; local raster inspection is not a browser PASS. P-19B review-43 is not owner-approved. P-19C remains not-started/unauthorized; G-04@1.5.0 remains NOT-EVALUATED. No package build, `dist`/publication mutation, commit, push, tag or Release operation is authorized.

---

# Historical: P-19B review-42 — dumbbell

Review-42 changed only CAP-V17 to display identity `dumbbell`, retaining internal `CAP-V17` and parent `bar-chart`. It passed exact verification with twelve pairs, twenty-four endpoints, shared scale/statistical bands and an exact twelve-row table before being archived byte-bound as the predecessor of D-123.

---

# Historical: P-19B review-41 — slope-graph

Review-41 changed only CAP-V18 to display identity `slope-graph`, retaining internal `CAP-V18` and parent `line-chart`. It passed exact verification with seven series, fourteen endpoints and an exact seven-row table before being archived byte-bound as the predecessor of D-122.

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
