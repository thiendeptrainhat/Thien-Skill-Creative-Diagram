# P-18R6 — Fourteen-engine neutral-light anchor contract

**Candidate:** `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-07-1.5.0`  
**Authority:** D-051, D-052, D-058, D-059, D-060, D-061, D-062, D-063, D-064, D-065  
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
| 06 | `lane-interaction` | Swimlane | exact owner-approved P-18R5 review-04 SVG |
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
- Diagram 04 normalizes all four node ranks to a 220px step and a 96px inter-rank node gap. Its inter-rank corridor midpoints advance by the same 220px step; the three lower fan-out corridors use a 20px ladder centered on y=694.
- The exact frozen Swimlane review-04 remains byte-identical and retains the same continuous bridge/hop contract.
- Diagram 05 keeps both `NO` branches at the same declared horizontal span; the second `NO` returns to the center-side entry of `Validate evidence` through a shared orthogonal return corridor.
- Timeline diagram 07 places top-event labels and metadata wholly above their leader endpoint and the time rail.
- Hierarchy diagram 09 prioritizes straight parent-child paths and terminates each applicable path at the horizontal center of both parent and child.
- Containment-stack diagram 10 uses one outer triangle. `Flagship decision` is a true three-vertex apex; every supporting layer is a trapezoid whose outer endpoints lie on the same two apex-to-base side lines. Adjacent layers reuse identical horizontal boundary endpoints, while the three shared boundaries render once over stroke-free fills. The left leverage arrow remains outside all polygons with a declared minimum horizontal clearance of 140px; the canonical geometry provides 160px.
- All eight layer text elements in diagram 10 publish measured real-font bounding boxes. Each box stays inside its owning polygon with at least 8px inset; local apex height and label position expand before any shrink or wrap, and the 24px/16px type roles remain unchanged.
- Diagram 10 exposes a right-side annotation rail with `THE APEX`, `~4 / YR`, `~12 / YR` and `~240 / YR`. These notes bind respectively to apex, quarterly, monthly and workday cadence; each remains at least 56px outside the triangle, inside the artboard and vertically inside the corresponding layer band. Their horizontal visual gap is not independently positioned: every note derives its x-coordinate from the outer-triangle right edge at the vertical center of its measured real-font bbox plus one shared `72px` target, with automated tolerance at most `0.01px`.
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

All P-18R6 prose, data, CSS, SVG and engine geometry are independently authored for this repository. No upstream code, CSS, SVG, template, screenshot or asset is copied or traced. Upstream comparison remains limited to abstract function/quality criteria. The exact P-18R5 Swimlane SVG is reused only as an internal owner-approved parent artifact and is byte-checked against its frozen source; no R5 file is edited. Review-01 through review-06 remain byte-bound at `history/review-01/` through `history/review-06/`. Review-07 supersedes review-06 only for owner review; its lineage records review-06 manifest SHA-256 `b1f934b5542079a93763b5ac0237dbdc2871dc6f97e8e4ea14adeb05536f844d` together with the earlier historical manifests.

## 7. Stop condition

After technical freeze, P-18R6 remains `owner-review-pending`; P-18 remains `in-progress` and `G-03@1.5.0` remains `NOT-EVALUATED`. P-19A/B/C cannot start without exact owner approval, a separate G-03 decision and separate authorization.
