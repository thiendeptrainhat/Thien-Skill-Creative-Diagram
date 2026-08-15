# P-02 design, accessibility and quantitative contract

**Contract ID:** `P02-DESIGN-1`  
**Status:** approved P-02 contract  
**Principle influence:** only the permitted abstract workflow from the locked Thien-UI-UX-Ultra snapshot: contract first, progressive routing, render–inspect–revise–verify, accessibility and evidence retention. All rules and values below are original project rules.

## 1. Design objective

Each diagram must communicate the supplied structure before adding decoration. Visual hierarchy must expose title/context, primary narrative, supporting detail, legend/notes and provenance in that order. Neutral diagrams must not contain TDTN brand marks or navy–gold styling by default.

Per `PROJECT-CONTRACT.md` D-022, the owner expects the professional/editorial clarity they value in `diagram-design`, interpreted only as an outcome: disciplined hierarchy, clean grouping, readable connectors, restrained styling and polished delivery. This is not a license to reuse its visual system, layout, tokens, shapes, CSS, prose, specimen geometry or pixels. Originality review is a hard prerequisite for every future golden.

## 2. Approved canvas presets

| Size | Candidate logical canvas | Primary use | Minimum body text |
|---|---:|---|---:|
| `doc-inline` | 960 × 720 | embedded document column | 13 px |
| `doc-wide` | 1440 × 900 | wide document/report | 14 px |
| `slide-16x9` | 1600 × 900 | presentation | 20 px |
| `slide-4x3` | 1600 × 1200 | legacy presentation | 20 px |
| `social-og` | 1200 × 630 | link/social preview | 18 px |
| `social-square` | 1080 × 1080 | square post | 18 px |
| `print-a4-landscape` | 297 × 210 mm | print | 9 pt |
| `print-letter-landscape` | 11 × 8.5 in | print | 9 pt |
| `fit` | derived within 640–2400 px per dimension | smallest readable canvas | 13 px screen equivalent |

Canvas values and mode names were approved by the owner on 2026-08-15. SVG always uses a viewBox and preserves aspect ratio. HTML may scale down responsively but must offer scroll/zoom or a larger artifact before text crosses the minimum.

## 3. Layout system

- Use an 8-unit base spacing rhythm with 4-unit micro-adjustments.
- Keep outer safe area at least 32 units on screen canvases; print safe area at least 10 mm.
- Node internal padding is at least 12 horizontal and 8 vertical units.
- Peer nodes align to a shared grid unless semantic ordering requires offset.
- Groups and lanes have explicit boundaries, labels and ownership; containment cannot rely on color alone.
- Reading order follows the declared narrative and matches DOM order.
- Dense labels wrap at semantic phrase boundaries. Ellipsis is prohibited for material content.

## 4. Typography

- Use a local/system font stack with reliable Vietnamese glyph coverage; do not fetch fonts.
- Preserve Unicode text and normalization intent. Never strip Vietnamese diacritics or transliterate silently.
- Use at most three typographic roles in the diagram body: heading, label and annotation/data.
- Minimum line height is 1.25 for display labels and 1.4 for multiline body text.
- Do not use condensed text, artificial horizontal scaling or font sizes below the preset minimum to make content fit.
- A font substitution is recorded in the artifact ledger when metrics materially change wrapping.

## 5. Color and modes

Approved modes:

- `neutral-light`: light neutral background, dark text, restrained semantic accents.
- `neutral-dark`: dark neutral background, light text, equivalent hierarchy and semantics.
- `editorial`: complete diagram plus an original title/context/annotation composition; the diagram itself remains independently exportable.

State is encoded by at least two channels among label, shape, pattern, border and color. Normal text contrast is at least 4.5:1; large text and meaningful non-text graphics are at least 3:1. Focus indication is visible against adjacent colors. Decorative colors never create an implied quantitative scale.

## 6. Semantic shapes

Each type grammar will bind abstract roles to a small, consistent shape vocabulary. Until P-05, the contract is limited to these invariants:

- the same shape cannot mean contradictory roles within one artifact;
- start/end, decision, state, data/document, actor/system and boundary roles are distinguishable without color;
- icon use is optional and supplementary; every icon has an accessible text equivalent and approved provenance;
- quantitative marks are data-bound and cannot be resized for aesthetics independently of their value.

## 7. Connector routing

- Every connector has a declared source, target, direction and semantic kind in IR.
- Default routes are orthogonal for process/topology families and direct/curved only where the type contract justifies them.
- Maintain at least 12 px between a route and unrelated node bounds, 8 px between parallel routes, and 16 px between a route and unrelated text.
- Connectors may cross only after routing alternatives fail; crossings must be visually explicit and never look like a join.
- Arrowheads cannot cover node borders or labels. Shared attachment points are allowed only when the shared junction is semantic.
- Labels attach to their edge and remain unambiguous at responsive and print sizes.

## 8. Approved complexity budget

Complexity is measured before render; the renderer cannot solve excess complexity by shrinking text or overlapping geometry.

| Budget | Structural items | Relations | Groups/lanes | Labeled chart marks | Intended canvases |
|---|---:|---:|---:|---:|---|
| `compact` | ≤18 | ≤24 | ≤4 | ≤24 | doc-inline, social-square |
| `standard` | ≤36 | ≤60 | ≤8 | ≤60 | doc-wide, slides, social-og |
| `wide` | ≤64 | ≤110 | ≤12 | ≤120 | print landscape, fit |

An item is a visible semantic node, state, event, task or entity; a relation is an edge, message, transition or dependency. Matrix cells and scatter points are counted separately: approved limits are 400 meaningful matrix cells and 1,000 scatter points, subject to legibility and exact-value preservation.

Over-budget resolution order:

1. choose a larger compatible preset;
2. remove only non-semantic decoration;
3. factor repeated wording into a legend without losing association;
4. split into an overview plus numbered detail artifacts with cross-links;
5. ask the user to narrow scope.

Aggregation of quantitative data is forbidden unless the user approves the method and the artifact states it. The owner approved these numeric thresholds on 2026-08-15; later type-specific validation still applies.

## 9. Responsive, print and export

- Responsive scaling preserves relative positions and never reorders semantics silently.
- Below the minimum readable width, use horizontal scrolling, zoom or a separately laid-out compact artifact; do not clip.
- Print removes controls and motion, uses the complete static frame and preserves legend/source notes.
- Diagram-only SVG excludes surrounding editorial panels unless explicitly requested.
- HTML, SVG and PNG from one request must derive from the same normalized IR and validation record.

## 10. Accessibility contract

- SVG root has a concise accessible name and a longer description when relationships are not obvious from the name.
- IDs are unique and deterministic within an artifact.
- DOM/read order matches the narrative order; decorative elements are hidden from assistive technology.
- Keyboard users can reach every interactive control; focus order follows reading order.
- `prefers-reduced-motion` disables non-essential motion and presents the complete state.
- Quantitative charts include an accessible data representation containing exact labels, values, units and missing-value status.
- Error, warning, success, policy and permission states are not color-only.
- Vietnamese labels are tested with long words, mixed Latin abbreviations, punctuation and diacritics.

## 11. Quantitative integrity

- Normalize pasted table, CSV and JSON representations of the same dataset to equivalent IR.
- Preserve values, series, units, dates, timezones, ordering, zeros, negatives, nulls, NaN status and duplicate dates explicitly.
- Bar charts start at zero unless a declared analytical reason and visible break/disclosure are approved.
- Line gaps remain gaps; interpolation is never invented.
- Scatter renders the exact observation count and coordinates unless an approved aggregation is disclosed.
- Radar publishes its domain and normalization; incompatible scales cannot share an axis without explicit normalization.
- Gantt and Timeline preserve start/end/duration/timezone. Quadrant preserves axis/domain and coordinates. Pyramid/Funnel preserves order and declared values/ratios.
- Rounding is display-only; the accessible data representation retains source precision.

## 12. Render–inspect–revise–verify evidence

Every golden candidate later must retain: request/IR hash, renderer/version, canvas/mode, automated semantic/geometry/accessibility results, inspection notes, revision reason and final approval. Visual inspection cannot waive a semantic or security failure.
