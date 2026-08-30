# P-18R4 visual-foundation relock

**Contract ID:** `P18R4-VISUAL-FOUNDATION-1.5.0`  
**Date:** 2026-08-24  
**Authority:** D-051, D-052 and D-053  
**Machine-readable binding:** `evidence/p18/P-18R4-VISUAL-FOUNDATION.json`  
**Applies to:** P-18R5, P-18R6 and the later P-19A→P-19C source/gallery work  
**Boundary:** contract and visual-foundation specification only; no renderer/gallery regeneration, package, `dist/`, Git or release action

## 1. Relock outcome

The frozen `P18-PILOT-1.5.0-VISUAL-CRAFT-REPLACEMENT` remains historical evidence but is rejected as the visual direction for G-03@1.5.0. Its technical and internal visual scores are not owner acceptance and must not be reused as a golden.

The next candidate must be produced by a new canonical visual kernel. The renderer may reuse locked semantic IR, case data, quantitative assertions and security boundaries, but must not carry forward these rejected foundation choices:

- one fixed 1440×900 composition for every family;
- a global SVG/body transform used as a substitute for layout;
- character-count or heuristic-only text measurement;
- fixed-size cards that require text compression, clipping or overflow;
- one generic page/card template for unrelated diagram families;
- hand-authored connector coordinates without obstacle-aware routing;
- type labels, legends or intent prose that leak the answer into blind/five-second review;
- an internal score treated as a substitute for owner visual approval.

P-18R4 does not modify the 39 canonical type semantics, the four capability semantics, the three visual-mode names, the exact P-18 data matrix, or the existing semantic/quantitative/security gates.

## 2. Canonical rendering pipeline

Every future visual candidate must follow this order:

```text
locked semantic IR
  → visual intent and declared focal path
  → typography resolution by precedence
  → font availability and glyph validation
  → real font metrics and line breaking
  → primitive and node intrinsic sizing
  → family layout-engine selection
  → content-fit artboard and safe-area planning
  → port allocation and obstacle map
  → connector routing, labels and bridge/hop pass
  → semantic / quantitative / geometry / accessibility / security QA
  → standalone HTML/SVG emission
  → visual-craft and owner review
```

No font, scale, transform or theme may be swapped after layout without repeating measurement, sizing, layout, routing and affected QA.

## 3. Typography contract

### 3.1 Precedence

Typography is resolved per role using this strict order:

1. explicit font or role mapping selected by the user for the current request;
2. a user-selected brand/client typography profile;
3. the source-diagram font only when the user explicitly requests source-font fidelity and the font can be used lawfully and safely;
4. the skill default profile;
5. a disclosed system fallback.

An explicit user choice always overrides the skill default for the roles it covers. A request such as “use font X for everything” applies X to display, human-facing and technical roles only after glyph and metric validation. A role-specific choice changes only that role. Request-scoped choices do not silently become the new global default.

### 3.2 Default direction

The default profile is:

| Role | Preferred family | Purpose |
|---|---|---|
| Display/editorial | Instrument Serif | page titles and editorial callouts only |
| Human-facing sans | Geist | node titles, lane names, legends and explanatory labels |
| Technical mono | Geist Mono | metadata, tags, ports, axes, connector labels and tabular values |

These font families are a user-approved default direction, not copied font assets. Any later local embedding must be independently sourced from the official publisher, license/provenance recorded, subset deterministically if needed, and kept self-contained. P-18R4 performs no download, install or font bundling.

If the preferred default is unavailable in a target environment, the renderer must disclose the resolved fallback. If a user-selected font is unavailable or lacks required Vietnamese glyphs, do not silently mix or replace it; report the issue and ask for a fallback decision unless the user already supplied one.

### 3.3 Measurement and overflow

- Wait for the selected font faces before measuring or rendering.
- Use actual font metrics for each role, weight and size; heuristic width may be a conservative preflight only.
- Validate Vietnamese diacritics, combining marks, punctuation, digits and the material glyph set before layout.
- Wrap by measured width with explicit line boxes. Never use character count as the final line-break rule.
- Grow the owning node, change the grid, reduce non-material detail or split the artifact when content does not fit. Never shrink material text below the locked minimum to hide overflow.
- Re-run containment and routing checks after any font, weight, tracking, line-height or content change.

Canonical defaults are display 48px, node/stage title 24px, material label/body 16px and technical mono 16px. D-050 minima remain blocking: display 40–48px, node/stage title 20–24px, material text at least 16px and mono metadata/value/tick 14–16px.

## 4. Artboard and interface contract

The artboard is selected from semantic content and family engine, not forced into one universal ratio. The layout engine may choose:

- wide rail/lane compositions in the 2.20–2.45 aspect-ratio range;
- landscape network/data compositions in the 1.75–2.10 range;
- balanced matrix/hierarchy compositions in the 1.45–1.75 range;
- tall directed-flow compositions in the 1.00–1.35 range.

The renderer computes the final viewBox from measured content, a 48px minimum safe area and a reserved legend band where a legend is semantically necessary. A global post-layout transform is forbidden. Semantic field plus type legend must still occupy at least 75% of artboard height under D-050.

The default interface direction is a restrained technical-editorial surface: warm/neutral paper, low-contrast grid or dot field when useful, precise hairlines, high-contrast ink, one focal accent and compact semantic legends. This is a quality and role contract, not permission to trace or reproduce an upstream screenshot/template.

The SVG contains one diagram field and only diagram-native interface chrome. The outer HTML may contain the evidence ledger and provenance, but those sections are excluded from the canonical screenshot, blind review and five-second review. No duplicate visible title or QA/evidence rail is allowed inside the SVG.

## 5. Primitive and node contract

The canonical primitive library must define measurable, role-bearing primitives rather than generic cards alone:

- node/card, zone/lane, stage rail, legend band and annotation plate;
- actor/service/host/package/document/file/database/data-store and state/decision shapes;
- plot axes, scales, bands, areas, points, intervals and quantitative labels;
- declared ports, arrowheads, bridge/hop marks and label masks.

For process and swimlane families, the default node anatomy supports role badge, primary title, state transition or concise metadata, system/location line and optional edge-aligned data-type tags. Intrinsic size is computed from measured content and padding; text must remain inside its owning node at all tested widths.

Primitive reuse must not erase family identity. Each canonical type keeps an explicit silhouette contract, type-native marks and type-native legend.

## 6. Layout-engine map for all 39 canonical types plus four capabilities

| Engine | Canonical types | Capability variants |
|---|---|---|
| `topology-and-zones` | Architecture; IT current-state; High-Level | — |
| `integration-pipeline` | Data flow; DP integration | — |
| `runtime-deployment` | Deployment | — |
| `dependency-dag` | Dependency graph | — |
| `directed-flow-state` | Flowchart; Process; State machine | — |
| `lane-interaction` | Swimlane; Sequence | — |
| `time-planning` | Timeline; Gantt | — |
| `work-experience` | Kanban; User journey; Story map | — |
| `hierarchy` | Tree; Org chart | — |
| `containment-stack` | Nested; Layer stack; Medallion; Pyramid/Funnel | — |
| `compartment-model` | ER/data model; Database schema; UML class | — |
| `spatial-matrix` | Quadrant; DP security matrix; Wardley map; Venn | — |
| `quantitative` | Bar chart; Line chart; Scatter plot; Radar; Polar chart; Treemap | Dumbbell; Slopegraph; Ridgeline; Bubble |
| `special-geometry` | Loop/Flywheel; Sankey; Fishbone | — |

The machine-readable contract must prove exactly 39 unique canonical type assignments and four unique capability assignments. One engine may share measurement or routing utilities with another, but no type may fall back to a generic unknown diagram.

## 7. Connector and label contract

- Allocate ports before routing; fan shared ports when several edges converge.
- Route against measured node, lane, zone, label and legend obstacles.
- Prefer short orthogonal routes with consistent rounded bends for technical/process diagrams; use curves only where the type grammar calls for them.
- A connector terminates on its declared source/destination boundary or port and never inside the wrong node.
- Keep at least 8px between connector ink and unrelated text/labels.
- Label masks must be opaque enough for the active mode and reserve measured clearance.
- Avoid crossings; when unavoidable, render a visible bridge/hop and preserve narrative direction.
- Arrowhead scale, stroke weight and port treatment are tokenized and visually stable at canonical and responsive render sizes.

## 8. Mode derivation

`neutral-light` is the geometry and typography anchor. `neutral-dark` and `editorial` are derived only after the anchor passes. Modes share semantics and port topology, but may adjust role-appropriate surface, ink, grid, line and display treatment; they may not be mere global recolors when a mode needs different contrast or typographic craft.

Changing mode cannot move data points, reverse reading order, change node ownership or alter quantitative scale. Any mode-specific font metric change triggers full remeasurement and geometry QA.

## 9. Validation and review

The existing semantic, quantitative, accessibility, security, standalone and provenance checks remain blocking. The new foundation adds these mandatory checks:

- requested/default font loaded and computed family verified before layout;
- required glyph coverage verified, including Vietnamese stress strings;
- 100% material text contained in its owning node/region with declared padding;
- no shrink-to-fit below D-050 minima;
- no global-transform substitute for layout;
- no node/text/label/legend overlap and no connector through an unrelated obstacle;
- endpoint, port, label-clearance and bridge/hop assertions;
- family-specific silhouette declaration and clean blind review without type legend, file name or intent prose;
- five-second review without a sentence that states the intended answer;
- visual-craft score at least 85/100, every dimension at least 4/5, plus explicit owner approval of the exact manifest.

For the 14-engine neutral-light anchor gallery in P-18R6, blind engine recognition must be at least 12/14. For full P-19 coverage, every canonical type must declare a type-specific silhouette; confusing within-engine clusters receive masked blind review and must meet an aggregate 85% recognition threshold.

Image comparison with upstream remains rubric-only. Pixel similarity, overlay, tracing and reuse/adaptation of upstream code, prose, CSS, SVG, icons, templates, gallery assets or font files are blocking failures.

## 10. Authorized sequence after this relock

- `P-18R4` — this contract/foundation relock and governance/evidence synchronization.
- `P-18R5` — implement the canonical kernel and one `neutral-light` Swimlane anchor; stop for owner review.
- `P-18R6` — implement one `neutral-light` anchor per 14 layout engines; stop for owner review and G-03@1.5.0 decision.
- `P-19A` — implement 39+4 type/capability adapters only after P-18 passes, G-03@1.5.0 is `PASS` and authorization is explicit.
- `P-19B` — derive three modes and produce the exact 129 standalone HTML gallery only after P-19A verification.
- `P-19C` — run full QA, masked review, freeze and owner approval workflow.

Only P-18R4 is authorized by D-053. This sequence is a dependency map, not authorization for P-18R5, P-18R6 or any P-19 subphase.
