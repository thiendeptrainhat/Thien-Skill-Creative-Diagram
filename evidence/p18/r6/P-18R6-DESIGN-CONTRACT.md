# P-18R6 — Fourteen-engine neutral-light anchor contract

**Candidate:** `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`  
**Authority:** D-051, D-052, D-058, D-059, D-060, D-061, D-062, D-063, D-064, D-065, D-066, D-067, D-068, D-069, D-070, D-071, D-072, D-073, D-074, D-075, D-076  
**Status:** technical candidate; owner review pending  
**Scope boundary:** QA-only files under `evidence/p18/r6/`; no runtime, package, `dist/`, publication mirror, Git or Release mutation

## 1. Purpose

P-18R6 proves that the P-18R4 foundation and the owner-approved P-18R5 visual direction can produce a distinguishable `neutral-light` anchor for every locked layout engine before any P-19 adapter expansion. The exact candidate contains fourteen standalone HTML files and fourteen matching SVG files; `index.html`, `blind-review.html` and contact sheets are review surfaces, not extra specimens.

## 2. Locked engine-to-anchor assignment

| # | Layout engine | Anchor type | Primary silhouette |
|---:|---|---|---|
| 01 | `topology-and-zones` | Architecture | trust zones with a left-to-right focal origin |
| 02 | `integration-pipeline` | Data flow | collect/transform/serve stage convergence |
| 03 | `runtime-deployment` | Deployment | region → cluster → node-pool containment |
| 04 | `dependency-dag` | Dependency graph | ranked DAG with fan-in and one cycle back-edge |
| 05 | `directed-flow-state` | Flowchart | tall start/step/diamond/end branch flow |
| 06 | `lane-interaction` | Swimlane | D-066 phase-coverage extension over the exact owner-approved P-18R5 review-04 source |
| 07 | `time-planning` | Timeline | proportional horizontal time rail |
| 08 | `work-experience` | User journey | moments × action/thought/emotion grid |
| 09 | `hierarchy` | Org chart | root → domain → specialist tree |
| 10 | `containment-stack` | Pyramid/funnel | one continuous outer triangle partitioned into a true triangular apex and three supporting trapezoids |
| 11 | `compartment-model` | Database schema | entity compartments, keys and cardinality |
| 12 | `spatial-matrix` | Quadrant | effort × impact position field |
| 13 | `quantitative` | Scatter/bubble | exact x/y values plus area encoding |
| 14 | `special-geometry` | Sankey | conserved flow ribbons across three columns |

The assignment selects one representative type per engine; it does not claim P-19 coverage for all 39 canonical types plus four capabilities.

## 3. Shared visual foundation

- Neutral warm canvas, dark ink/slate structure and one coral focal signal.
- Default font direction remains Instrument Serif / Geist / Geist Mono; the generator resolves available local fallbacks through the frozen P-18R5 master kernel and records every fallback. An explicit user font request still outranks the default and must be resolved before measurement.
- Node titles use 24px; material text uses 16px or 18px; technical metadata uses 14–16px. No shrink-to-fit is allowed.
- Node width starts from measured title width plus padding. Authors choose a larger local width when the engine needs more horizontal breathing room.
- Every artboard is engine-specific and content-fit; no global scale/matrix transform is used as layout.
- A containment engine declares measurable parent and child boxes. Every direct child keeps the parent's declared minimum padding; the complete direct-child group is centered on both parent axes. Row children share one center-y, column children share one center-x, and a single child shares both parent center coordinates.
- Each SVG has one invisible accessible `<title>` and `<desc>`, one semantic field, one encoding legend, and no visible duplicate page title or evidence rail.
- The canonical screenshot is only `.artifact-frame`; page title, lede, font receipt and semantic projection remain outside it.

## 4. Connector and geometry rules

- Ports and corridors are assigned before paths are emitted.
- Diagrams 01–04 use one whole-chart `connector_corner_style`. The default is `rounded`, so every 90° turn uses the same controlled-radius corner and no broad decorative curve. If the user explicitly requests `straight`, that choice outranks the default and every 90° turn in the chart is serialized sharp; styles are never mixed within one chart.
- Diagrams 01–03 declare parent/child geometry in the SVG. Every direct child node or subcontainer is inside its parent with the declared minimum padding, and the child-group bounding box is centered on the parent in both axes. Row, column and single-child alignment follow the shared containment rule in section 3.
- Avoidable crossings are removed. Dependency diagram 04 has two remaining geometric crossings; both are explicit route-integrated bridge/hops using shared route/repaint geometry, crown-only underlay and zero-gap straight-to-hop continuity. All ten base routes are painted before either hop repaint.
- Diagram 04 normalizes all four node ranks to a 240px step and a 116px inter-rank node gap. Its semantic rank boundaries are `y=40/280/520/760/1000`, giving rank centers `y=160/400/640/880`; the lower bridged fan-out corridors use `y=738/782` around, rather than on, the `y=760` boundary.
- The exact frozen P-18R5 review-04 source remains byte-identical. Diagram 06 in R6 is intentionally not byte-identical because D-066 adds one local phase-coverage layer without editing the parent or changing its continuous bridge/hop paths.
- Diagram 06 exposes six ordered major phases for six workflow-step IDs: `CHUẨN BỊ`, `NHẬN BỘ`, `PHÂN LOẠI`, `GỬI NGÂN HÀNG`, `CẬP NHẬT NỢ`, `ĐĂNG SỔ`. The first phase is centered on `Chuẩn bị thanh toán`; the remaining phase centers retain the existing workflow rhythm. The lower handoff legend repeats the same ordered phase inventory.
- Diagram 05 keeps both `NO` branches at the same declared horizontal span; the second `NO` returns to the center-side entry of `Validate evidence` through a shared orthogonal return corridor.
- Timeline diagram 07 places top-event labels and metadata wholly above their leader endpoint and the time rail.
- Hierarchy diagram 09 prioritizes straight parent-child paths and terminates each applicable path at the horizontal center of both parent and child.
- Under D-076, diagram 09 keeps its exact review-16 node/connector geometry but exposes the visible hierarchy `1 FRONT DOOR`, `4 DOMAINS`, `5 SPECIALIST PODS`; the focal root subtitle repeats the same 1→4→5 count so a five-second reviewer need not infer or recount leaves.
- Containment-stack diagram 10 uses one outer triangle. `Flagship decision` is a true three-vertex apex; every supporting layer is a trapezoid whose outer endpoints lie on the same two apex-to-base side lines. Adjacent layers reuse identical horizontal boundary endpoints, while the three shared boundaries render once over stroke-free fills. The left leverage arrow remains outside all polygons with a declared minimum horizontal clearance of 140px; the canonical geometry provides 160px.
- All eight layer text elements in diagram 10 publish measured real-font bounding boxes. Each box stays inside its owning polygon with at least 8px inset; local apex height and label position expand before any shrink or wrap, and the 24px/16px type roles remain unchanged.
- Diagram 10 exposes a right-side annotation rail with `THE APEX`, `~4 / YR`, `~12 / YR` and `~240 / YR`. These notes bind respectively to apex, quarterly, monthly and workday cadence; each remains at least 56px outside the triangle, inside the artboard and vertically inside the corresponding layer band. Their horizontal visual gap is not independently positioned: every note derives its x-coordinate from the outer-triangle right edge at the vertical center of its measured real-font bbox plus one shared `72px` target, with automated tolerance at most `0.01px`.
- Diagram 11 places `CUSTOMER`, `ORDER` and `PAYMENT` on one measured center-y; its two horizontal relationships connect exact center-side boundaries. `ORDER_ITEM` shares ORDER's center-x and the vertical relationship connects exact center boundaries. Every entity field stack keeps 32px measured bottom padding, exceeding the 24px minimum. The three relationship-name labels are independent from cardinality: `PLACES` and `PAID BY` remain above horizontal lines, while `CONTAINS` remains right of the vertical line. Each relationship emits a separate source `1` and target `N` directly on the connector axis near its corresponding node boundary. A measured canvas-fill/no-stroke knockout is painted after the single semantic connector and before each cardinality, creating explicit white space behind the glyph without splitting relationship semantics. Knockout padding is 8px along the connector and 4px perpendicular to it; every knockout remains at least 8px outside its adjacent node, and rendered glyph-to-axis alignment error may not exceed 0.75px in browser QA.
- Diagram 12 exposes exactly four directional axis annotations: `↑ HIGH IMPACT` at the upper impact endpoint, `← LOW EFFORT` below the left effort endpoint, `↓ LOW IMPACT` below the lower impact endpoint and `HIGH EFFORT →` below the right effort endpoint. Upper/lower notes share a measured 24px x-offset to the right of the vertical axis; left/right notes share a measured 42px baseline offset below the horizontal axis and align to the corresponding field edge. All four use real-font bbox metadata, remain in canvas and keep at least 16px clearance from the axis endpoint/line. Quadrant titles, six initiatives and the single `Freeze contract` focal point remain unchanged from review-08.
- Diagram 12 uses one pale coral `DO FIRST` focal-region fill without a perimeter line. Its rectangle is serialized with `stroke:none`; a transparent, zero-opacity or zero-width coral stroke is not an acceptable substitute. The review-09 focal-region geometry (`x=190`, `y=120`, `width=590`, `height=319`) and every D-067 axis annotation, quadrant title, initiative, focal point and legend position remain unchanged.
- Diagram 14 uses one shared `0.025px/minute` scale for every node bar and ribbon. Each applicable source, stage and outcome interface is tiled from its exact top edge to its exact bottom edge by contiguous, non-overlapping ribbon intervals, so visual allocation occupies `100%` of every bar and both stage and outcome totals reconcile to `12,000` minutes. Every bar is a square-corner SVG rectangle with no `rx`; its title and value form a centered label stack wholly above the bar with at least 12px measured clearance. The scenario, values, palette, legend and semantic facts remain unchanged.
- Under D-072, diagram 14's upper source/stage/outcome bars — `Monthly budget`, `Unit tests` and `Passed` — share exact `top-y = 210px`. Static and browser geometry must report a maximum top-edge spread of at most `0.01px`. Only the source bar and its three outgoing source-side ribbon intervals move vertically; D-071 scale, ribbon thickness, gapless interface occupancy, labels, square corners, values, conservation, palette, legend and semantics remain unchanged.
- Under D-076, diagram 14 preserves every review-16 ribbon `d`, value, thickness, node scale and conservation fact. Only focal encoding changes: `unit-flaked` uses high-opacity coral while every non-focal ribbon is muted to at most `0.50`, and one direct annotation states `FLAKED RERUNS · 1,000 / 12,000 MIN · 8.3% OF BUDGET` with a coral leader. Position/thickness remain quantitative truth; contrast and annotation make the exception the immediate five-second takeaway.
- Under D-073, the pale horizontal lines in diagrams 04, 08 and 09 are semantic band boundaries, never row centerlines. Diagram 04 uses boundaries `40/280/520/760/1000` with centers `160/400/640/880`; diagram 08 uses boundaries `204/384/564/744` with centers `294/474/654`; diagram 09 uses boundaries `60/300/540/780` with centers `180/420/660`. Every member card or icon publishes its band binding and its bounding-box center-y must equal the corresponding band midpoint within `0.01px` in static QA and `0.75px` in browser QA. Separators may not intersect or render behind a member; the canonical minimum member-to-separator clearances are respectively `22px`, `27px` and `58px`. Connectors may cross a separator only to express a real cross-band relationship and may not use the separator as an ambiguous route rail.
- Under D-074, diagram 13 uses two plain axis lines with no `marker-start`, `marker-mid` or `marker-end`. In particular, the vertical `CONTROL CONFIDENCE` axis terminates cleanly at the shared `0,0` origin without the former downward arrowhead. Automation/control scales, zero labels, ticks, grid, five quantitative points, bubble areas, direct labels, focal encoding, legend and accessible exact-value table remain unchanged.
- Connector endpoints terminate on their semantic source/target boundary. Labels are kept off unrelated paths with at least the locked 8px declared clearance.
- No unrelated connector may pass through a node. No bubble, junction-like dot, mask-only fake hop or detached arc is accepted.

## 5. Review protocol

- Labeled review: `index.html` or `review/contact-sheet-labeled.png`.
- Masked recognition: `blind-review.html` or `review/contact-sheet-masked.png`; the deterministic card order differs from the engine order and the visible card text does not expose engine/type/file/evidence answers.
- Acceptance target for owner/independent blind review: at least 12/14 engines identified from silhouette.
- Five-second test: reviewer states one focal node/path or takeaway per card before reading the outer page lede.
- Visual-craft gate: at least 85/100, each dimension at least 4/5, from an independent reviewer. Implementer precheck is evidence only and cannot satisfy this gate.
- Semantic/quantitative/accessibility/security/static geometry must remain `PASS`.

## 6. Independent implementation and lineage

All P-18R6 prose, data, CSS, SVG and engine geometry are independently authored for this repository. No upstream code, CSS, SVG, template, screenshot or asset is copied or traced. Upstream comparison remains limited to abstract function/quality criteria. The exact P-18R5 Swimlane SVG is read only as an internal owner-approved parent artifact and is byte-checked against its frozen source; no R5 file is edited. The R6 diagram 06 phase rail is an explicitly recorded local extension, not a replacement of the parent. Review-01 through review-16 remain byte-bound at `history/review-01/` through `history/review-16/`; exact review-16 manifest SHA-256 is `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`. Review-17 supersedes review-16 only for the two D-076 five-second findings; all twelve non-target anchor HTML/SVG pairs remain byte-identical to review-16.

## 7. Stop condition

After technical freeze, P-18R6 remains `owner-review-pending`; P-18 remains `in-progress` and `G-03@1.5.0` remains `NOT-EVALUATED`. P-19A/B/C cannot start without exact owner approval, a separate G-03 decision and separate authorization.
