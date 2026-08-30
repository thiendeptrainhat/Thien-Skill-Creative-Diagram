# P-18R6 — Fourteen-engine neutral-light anchor contract

**Candidate:** `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-1.5.0`  
**Authority:** D-051, D-052, D-058, D-059  
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
| 10 | `containment-stack` | Pyramid/funnel | four tapering leverage layers |
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
- Each SVG has one invisible accessible `<title>` and `<desc>`, one semantic field, one encoding legend, and no visible duplicate page title or evidence rail.
- The canonical screenshot is only `.artifact-frame`; page title, lede, font receipt and semantic projection remain outside it.

## 4. Connector and geometry rules

- Ports and corridors are assigned before paths are emitted.
- Avoidable crossings are removed. The dependency anchor uses independent corridors rather than shared/ambiguous junction buses.
- The only unavoidable crossing in this exact gallery is inherited from the exact frozen Swimlane review-04; its bridge/hop uses shared route geometry and crown-only underlay, preserving straight-to-hop continuity.
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

All P-18R6 prose, data, CSS, SVG and engine geometry are independently authored for this repository. No upstream code, CSS, SVG, template, screenshot or asset is copied or traced. Upstream comparison remains limited to abstract function/quality criteria. The exact P-18R5 Swimlane SVG is reused only as an internal owner-approved parent artifact and is byte-checked against its frozen source; no R5 file is edited.

## 7. Stop condition

After technical freeze, P-18R6 remains `owner-review-pending`; P-18 remains `in-progress` and `G-03@1.5.0` remains `NOT-EVALUATED`. P-19A/B/C cannot start without exact owner approval, a separate G-03 decision and separate authorization.
