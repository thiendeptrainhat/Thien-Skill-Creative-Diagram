# P-02 behavior and test contract

**Contract ID:** `P02-TEST-1`  
**Status:** approved P-02 contract  
**Rule:** every public behavior has a success assertion, a failure assertion and a stable test-family mapping before implementation.

## 1. Test layers

1. Schema: request and IR structural validity.
2. Semantic: source facts, relations, type invariants and fidelity.
3. Security: inert input, resource caps, escaping and zero side effects.
4. Visual geometry: bounds, overlap, connector routing, typography and responsive/print.
5. Accessibility: naming, reading/focus order, contrast, static/reduced-motion and data representation.
6. Output: artifact parity, fallback and portability.
7. Platform: install, discovery, trigger, output and fallback on each matrix cell.
8. Benchmark: independent original tasks and owner-approved goldens/rubric.

Hard failures are never averaged into a visual score.

## 2. Request and routing mapping

| Behavior | Success assertion | Failure assertion | Test IDs |
|---|---|---|---|
| schema and enum validation | accepted request has no unknown/conflicting field | exact field error; no artifact | `T-REQ-SCHEMA-01..06` |
| auto type selection | selected canonical type records evidence and alternatives | low/material ambiguity asks; no guessed type | `T-ROUTE-AUTO-01..27`, `T-ROUTE-AMB-01..06` |
| manual type | compatible type retained | semantic mismatch asks change rather than force-fit | `T-ROUTE-MANUAL-01..27` |
| data-lake profile | routes to Medallion, DP integration or High-Level from meaning | ambiguous multi-story asks; never creates type 28 | `T-ROUTE-DATALAKE-01..04` |
| language | follows request/user language; Vietnamese preserved | unsupported/ambiguous language disclosed; no silent transliteration | `T-LANG-01..08` |
| audience | changes explanation depth only | fact/value/relation change fails | `T-AUD-01..06` |
| detail | applies declared keep/merge/drop rules | silent/material loss fails | `T-DETAIL-01..09` |
| size/complexity | readable result or disclosed split | shrink/clipping/hidden content fails | `T-CPLX-01..12` |

## 3. Canonical type coverage contract

Each row requires at least one original positive fixture, one boundary/negative fixture, semantic assertions and later render smoke evidence in every owner-approved static mode.

| Test family | Capability | Core semantic assertion |
|---|---|---|
| `T-TYPE-01-*` | `CAP-T01` Architecture | components, boundaries, edge endpoints |
| `T-TYPE-02-*` | `CAP-T02` IT current-state | groups, states, modernization handoffs |
| `T-TYPE-03-*` | `CAP-T03` Flowchart | branch/join reachability and outcomes |
| `T-TYPE-04-*` | `CAP-T04` Sequence | actor/message order and fragments |
| `T-TYPE-05-*` | `CAP-T05` State machine | valid transitions, guards, terminals |
| `T-TYPE-06-*` | `CAP-T06` ER/data model | entities, fields, cardinality |
| `T-TYPE-07-*` | `CAP-T07` Timeline | dates, timezone and order |
| `T-TYPE-08-*` | `CAP-T08` Swimlane | lane ownership, steps and handoffs |
| `T-TYPE-09-*` | `CAP-T09` Quadrant | axes, domains and coordinates |
| `T-TYPE-10-*` | `CAP-T10` Radar | common scale and exact series values |
| `T-TYPE-11-*` | `CAP-T11` Loop/Flywheel | cycle closure, station order, shared state |
| `T-TYPE-12-*` | `CAP-T12` Nested | containment and depth |
| `T-TYPE-13-*` | `CAP-T13` Tree | acyclic parent/child structure |
| `T-TYPE-14-*` | `CAP-T14` Org chart | reporting, ownership and escalation |
| `T-TYPE-15-*` | `CAP-T15` Layer stack | layer order and dependencies |
| `T-TYPE-16-*` | `CAP-T16` Venn | region membership and intersections |
| `T-TYPE-17-*` | `CAP-T17` Pyramid/Funnel | ordering and declared proportions |
| `T-TYPE-18-*` | `CAP-T18` Bar chart | values, unit, baseline and legend |
| `T-TYPE-19-*` | `CAP-T19` Line chart | values, order, gaps and units |
| `T-TYPE-20-*` | `CAP-T20` Gantt | start/end/duration/timezone/dependency |
| `T-TYPE-21-*` | `CAP-T21` Scatter | observation count and coordinates |
| `T-TYPE-22-*` | `CAP-T22` High-Level | stages, groups and cross-cutting concerns |
| `T-TYPE-23-*` | `CAP-T23` Process | actors, steps, artifacts and handoffs |
| `T-TYPE-24-*` | `CAP-T24` Medallion | tier order, policies and promotion |
| `T-TYPE-25-*` | `CAP-T25` Data flow | roles, steps, inputs/outputs and transfers |
| `T-TYPE-26-*` | `CAP-T26` DP integration | sources, platform boundary and consumers |
| `T-TYPE-27-*` | `CAP-T27` DP security matrix | every cell, permission state and legend |

## 4. Capability-class coverage

| P-01 class | Contract mapping | Minimum evidence rule |
|---|---|---|
| `CAP-V01..V16` variants/primitives | `T-VAR-<CAP-ID>-*` | one semantic equivalence test and one later visual smoke per distinct variant; 81 base static specimens remain 27 × three modes |
| `CAP-P01..P07` patterns | `T-PAT-<CAP-ID>-*` | exact pattern assertions plus existing canonical parent; no added type |
| `CAP-I01..I12` import/fidelity | `T-IMP-<CAP-ID>-*` | positive, malformed and adversarial carrier/grammar cases plus reconciliation |
| `CAP-O01..O07` output dials | `T-OUT-<CAP-ID>-*` | requested result, conditional capability and failure/fallback case |
| `CAP-M01..M12` motion | `T-MOT-<CAP-ID>-*` | complete static equality, deterministic order, reduced-motion/no-JS |
| `CAP-F01..F14` failures | `T-FAIL-<CAP-ID>-*` | named non-destructive error; no guessed artifact or side effect |

No upstream specimen is a fixture or golden. Test data, prose, geometry and expected output are written independently.

## 5. Output and parity mapping

| Behavior | Success assertion | Failure/fallback assertion | Test IDs |
|---|---|---|---|
| HTML | self-contained, valid, inline complete SVG | motion/script failure leaves static output | `T-OUT-HTML-01..05` |
| SVG | diagram-only, accessible and portable | ambiguous multiple target asks | `T-OUT-SVG-01..06` |
| PNG | matches validated static IR when renderer exists | absent renderer returns SVG + warning, no install | `T-OUT-RASTER-01..05` |
| HTML+PNG | both derive from same IR/static frame | HTML delivered with precise missing-PNG warning | `T-OUT-COMBO-01..04` |
| print/no-JS/reduced motion | complete semantic final state | unique information hidden by motion fails | `T-OUT-STATIC-01..08` |
| deterministic repeat | equal normalized request/version/environment gives equal IR and normalized SVG | unexplained drift fails | `T-DET-01..04` |

## 6. Geometry and accessibility mapping

| Behavior | Hard assertions | Test IDs |
|---|---|---|
| bounds/overlap | all material bounds inside canvas; no unintended overlap | `T-GEO-BOUNDS-01..06` |
| connectors | valid endpoints, clear route/label, crossing not confused with join | `T-GEO-EDGE-01..09` |
| typography | preset minimum, Vietnamese glyphs, no ellipsis of material text | `T-TYPEFACE-01..08` |
| responsive/print | no clipping/reorder; complete print frame | `T-RESP-01..08` |
| accessible name/order | name/description, unique IDs, DOM/read order | `T-A11Y-STRUCT-01..08` |
| contrast/non-color | approved contrast threshold and redundant state encoding | `T-A11Y-COLOR-01..06` |
| controls/motion | keyboard/focus and reduced-motion complete state | `T-A11Y-MOTION-01..08` |
| chart alternative | exact accessible table/representation | `T-A11Y-DATA-01..06` |

## 7. Quantitative integrity mapping

| Behavior | Hard assertions | Test IDs |
|---|---|---|
| carrier equivalence | pasted table, CSV and JSON normalize to equivalent IR | `T-QUANT-NORM-01..04` |
| values and missingness | exact value/unit/zero/negative/null/NaN/duplicate-date state | `T-QUANT-VALUE-01..10` |
| Bar/Line/Scatter/Radar | baseline; gaps; point coordinates/count; published radar normalization | `T-QUANT-CORE-01..16` |
| Gantt/Timeline | dates, timezone, duration, dependencies and order | `T-QUANT-TIME-01..10` |
| Quadrant/Pyramid/Funnel | coordinates/domain; values/ratios/order | `T-QUANT-OTHER-01..10` |
| display rounding | source precision retained in accessible data | `T-QUANT-ROUND-01..04` |

## 8. Security, fidelity and platform mapping

Security and fidelity test IDs are normative in `SECURITY-FIDELITY-CONTRACT.md`. Each `SUR-*` matrix row receives:

- `T-SUR-<ID>-INSTALL`
- `T-SUR-<ID>-DISCOVER`
- `T-SUR-<ID>-DIRECT`
- `T-SUR-<ID>-POSITIVE`
- `T-SUR-<ID>-NEGATIVE`
- `T-SUR-<ID>-OUTPUT`
- `T-SUR-<ID>-FALLBACK`

An `unsupported` row passes only when the limitation is documented and no package advertises or attempts the unsupported route.

## 9. Combination strategy

Base evidence is exhaustive where meaning differs: 27 types, every variant/pattern/import/motion class and every failure class. Cross-dimensional combinations use a deterministic pairwise set over size × detail × audience × format × language after each individual value has a direct test. Security, fidelity and quantitative hard cases are never reduced by pairwise sampling.

## 10. Gate acceptance

G-02 review checks contract completeness and testability, not implementation pass rates. P-02 can pass only when:

- both JSON schemas are syntactically valid and all contract links resolve;
- every public behavior/failure maps to a test family;
- owner approved the modes, defaults, thresholds, surface statuses/evidence rule and benchmark manifest/rubric on 2026-08-15;
- owner designated the current architecture, IR and security technical review as sufficient on 2026-08-15;
- missing benchmark reference handling is resolved without substitution.
