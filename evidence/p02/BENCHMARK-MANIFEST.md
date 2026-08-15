# P-02 E2 benchmark manifest

**Manifest ID:** `P02-E2-1`  
**Status:** approved benchmark contract; individual fixtures and goldens remain future gated artifacts  
**Reference dependency:** `REF-SWIMLANE-CASH-RECEIPTS-001` revision R2 is retained at `qa-only/REF-SWIMLANE-CASH-RECEIPTS-001-r2.png`, SHA-256 `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113`, and is excluded from every package/release payload.  
**Independence:** all task summaries below are original project scenarios; no upstream specimen, prose, dataset, layout or visual is reused.

## 1. Case record contract

Every executable case later contains:

- stable case ID and mapped `CAP-*` IDs;
- complete user input or a hash-addressed QA-only attachment;
- expected canonical type and allowed variants;
- semantic assertions and prohibited inventions;
- size, detail, audience, language, format, visual mode and motion;
- expected output/fallback;
- security/fidelity and accessibility assertions;
- hard-failure list and scored-rubric applicability;
- fixture/golden approval state and immutable hash.

No case may be converted into a golden until its raw input and assertions are approved by the owner.

## 2. Approved scoring rubric

Hard failures always result in case failure regardless of score. Approved weighted score:

| Dimension | Weight | Measures |
|---|---:|---|
| semantic correctness | 30 | entities, relationships, ordering, ownership, state and exceptions |
| security and fidelity | 20 | inert source, exact ledger, no invention or silent loss |
| quantitative/temporal integrity | 15 | values, scales, units, dates, missingness and accessible data; redistribute to semantics for non-quantitative cases |
| geometry and legibility | 15 | bounds, overlap, connector route, typography and density |
| accessibility | 10 | names, reading order, contrast, non-color meaning, keyboard/motion and data alternative |
| visual communication | 10 | hierarchy, consistency, restraint and audience fit after hard checks |

Approved pass threshold: at least 90/100 overall, at least 80% of each applicable dimension, and zero hard failure. `REF-SWIMLANE-CASH-RECEIPTS-001` is must-pass and additionally requires owner visual approval of the later original golden. The owner approved these weights and thresholds on 2026-08-15.

## 3. Universal hard failures

- wrong canonical type or materially wrong relation;
- invented business fact, value, actor, date, state or exception;
- silent semantic loss or fidelity reconciliation mismatch;
- any executed source instruction, external request, injection or unsafe path;
- value/scale/date/timezone distortion;
- clipping, unintended overlap, wrong connector endpoint or unreadable minimum text;
- inaccessible critical meaning, color-only state or motion-only meaning;
- copied/traced upstream or benchmark expression;
- hidden dependency, auto-install or unreported output fallback.

## 4. Approved canonical suite: 27 positive and 27 boundary cases

Default dials unless a row overrides: `doc-wide`, `balanced`, `mixed`, `neutral-light`, input language, `html`, `none`.

| Positive ID | Type / capability | Original input summary | Core assertions | Boundary case |
|---|---|---|---|---|
| `E2-T01` | Architecture / `CAP-T01` | municipal incident platform: callers, dispatch, field units, identity and audit zones | boundaries, components and directed dependencies exact | `E2-B01`: shared service across two trust zones; no false containment |
| `E2-T02` | IT current-state / `CAP-T02` | regional retailer's legacy ordering landscape grouped by business unit and lifecycle state | ownership/state/handoff retained | `E2-B02`: duplicate system names with distinct owners remain distinct |
| `E2-T03` | Flowchart / `CAP-T03` | warranty eligibility with two decisions and three outcomes | every branch reaches a declared outcome | `E2-B03`: missing branch label requires clarification, not invention |
| `E2-T04` | Sequence / `CAP-T04` | mobile sign-in with retry, timeout and optional device verification | actors/messages/order/fragments exact | `E2-B04`: contradictory message ordering fails validation |
| `E2-T05` | State machine / `CAP-T05` | service ticket states from new through resolved/reopened | guards and terminal/reopen transitions exact | `E2-B05`: unreachable state reported |
| `E2-T06` | ER/data model / `CAP-T06` | library member, loan, copy and title entities | keys and cardinalities preserved | `E2-B06`: ambiguous many-to-many relation asks for junction semantics |
| `E2-T07` | Timeline / `CAP-T07` | product launch milestones across two timezones | timestamps/order/timezone preserved | `E2-B07`: duplicate local times remain distinguishable |
| `E2-T08` | Swimlane / `CAP-T08` | employee equipment request across employee, manager, IT and procurement | lanes, ownership, steps and handoffs traceable | `E2-B08`: long Vietnamese labels do not clip |
| `E2-T09` | Quadrant / `CAP-T09` | initiatives plotted by customer impact and delivery effort | axis direction/domain and coordinates exact | `E2-B09`: out-of-domain coordinate fails or expands visibly, never clamps silently |
| `E2-T10` | Radar / `CAP-T10` | two service vendors scored on five declared 0–10 criteria | shared scale and values disclosed | `E2-B10`: incompatible source scales require approved normalization |
| `E2-T11` | Loop/Flywheel / `CAP-T11` | support learning loop from issue capture to knowledge reuse | cycle closes and station order remains | `E2-B11`: broken cycle is not presented as reinforcing loop |
| `E2-T12` | Nested / `CAP-T12` | research portfolio, programs, projects and work packages | containment/depth exact | `E2-B12`: cyclic containment rejected |
| `E2-T13` | Tree / `CAP-T13` | decision tree for selecting a backup strategy | parent/child paths and leaf decisions exact | `E2-B13`: node with two parents reported as non-tree |
| `E2-T14` | Org chart / `CAP-T14` | customer operations reporting and escalation paths | reporting differs visibly from escalation | `E2-B14`: dotted-line relationship not mistaken for primary manager |
| `E2-T15` | Layer stack / `CAP-T15` | application, platform, data and governance layers | order/dependency/cross-cutting control exact | `E2-B15`: dependency that skips layers remains explicit |
| `E2-T16` | Venn / `CAP-T16` | memberships across trained, authorized and on-call responders | all region memberships exact | `E2-B16`: item in no set remains outside, not dropped |
| `E2-T17` | Pyramid/Funnel / `CAP-T17` | support ticket funnel from received to resolved within SLA | values/order/drop-off exact | `E2-B17`: increasing stage is shown honestly, not forced narrower |
| `E2-T18` | Bar chart / `CAP-T18` | quarterly incidents by severity with zero and negative adjustment | values/unit/zero baseline/legend exact | `E2-B18`: truncated baseline requires explicit visible exception |
| `E2-T19` | Line chart / `CAP-T19` | weekly response time with a missing week and two series | gaps and units retained | `E2-B19`: unsorted/duplicate dates normalized without loss |
| `E2-T20` | Gantt / `CAP-T20` | migration tasks with dependencies and UTC offsets | dates/durations/dependencies exact | `E2-B20`: end before start fails |
| `E2-T21` | Scatter / `CAP-T21` | latency versus throughput observations with duplicate points | point count/coordinates preserved | `E2-B21`: null coordinate remains missing, not zero |
| `E2-T22` | High-Level / `CAP-T22` | citizen-service data journey with cross-cutting privacy controls | stages/groups/control span exact | `E2-B22`: data-lake profile routes by dominant story or asks |
| `E2-T23` | Process / `CAP-T23` | purchase return with customer, store and finance artifacts | step/artifact/handoff trace exact | `E2-B23`: parallel steps remain parallel, not serialized |
| `E2-T24` | Medallion / `CAP-T24` | sensor records promoted through raw, validated and curated tiers | tiers/policies/promotion exact | `E2-B24`: rejected records remain exception path |
| `E2-T25` | Data flow / `CAP-T25` | grant applications transformed into review packets and decisions | role/input/output/transfer exact | `E2-B25`: fan-in queue capacity visible |
| `E2-T26` | DP integration / `CAP-T26` | branch systems and partner feeds into platform services and consumers | boundaries, sources, core and consumers exact | `E2-B26`: bidirectional integration direction preserved |
| `E2-T27` | DP security matrix / `CAP-T27` | roles versus platform components with allow, deny and conditional states | every cell/state/legend accessible | `E2-B27`: unknown permission stays unknown, never inferred |

## 5. Approved seven semantic-pattern cases

| Case | Capability / parent | Input | Assertions |
|---|---|---|---|
| `E2-P01` | `CAP-P01` / Data flow | five sensors enter a queue of capacity three feeding one verifier | fan-in, capacity, service direction and overflow state |
| `E2-P02` | `CAP-P02` / Process | four approval stages repeat owner/input/check/output slots | slot identity and stage order |
| `E2-P03` | `CAP-P03` / Data flow | interview notes become coded findings and a signed decision record | loose input, transformation and durable artifact |
| `E2-P04` | `CAP-P04` / Flowchart | current and proposed eligibility policies diverge at one condition | pass/fail/skipped/not-reached and first divergence |
| `E2-P05` | `CAP-P05` / Architecture | approved deployment path crosses build and production trust boundaries; direct bypass denied | boundaries, allow/deny and route |
| `E2-P06` | `CAP-P06` / Layer stack | controls grouped by endpoint, network, platform and application owner | owner/enforcement location/control grouping |
| `E2-P07` | `CAP-P07` / Layer stack | weak prevention offset by detection and recovery with residual exposure | gap, compensating control and residual risk propagation |

## 6. Approved quantitative suite

| Case | Inputs | Expected | Hard assertions |
|---|---|---|---|
| `E2-Q01` | equivalent pasted table, CSV and JSON incident counts | Bar | normalized IR equivalence; exact zeros/negatives/unit |
| `E2-Q02` | weekly duration series with null and duplicate date | Line | explicit gap and duplicate-date treatment |
| `E2-Q03` | 250 paired observations including duplicate coordinates | Scatter | exact count and positions; no sampling |
| `E2-Q04` | two 1–5 maturity series plus an incompatible percentage series | Radar | reject mixed scale until normalization approved |
| `E2-Q05` | timezone-aware tasks and milestone dependencies | Gantt | exact dates, duration, order and timezone |
| `E2-Q06` | funnel stages with one increase and one missing value | Pyramid/Funnel | honest non-monotonic stage and disclosed missingness |

## 7. Approved import, motion and trigger suites

Original raw fixtures are created only in implementation/test phases and must be hash-addressed.

| Group | Candidate cases | Required behavior |
|---|---|---|
| draw.io | normal XML, multi-page, embedded PNG/SVG model, missing model, malformed XML, DTD/XXE, oversized/compression bomb | safe parse/redraw, page selection, zero execution/network, exact fidelity ledger |
| Mermaid | four supported grammars, multiple fenced blocks, unsupported kind, directive/click/HTML label, malformed/deep/oversized | inert independent parse, explicit boundary, no Mermaid render |
| motion | `none`, `reveal`, `step`, `loop`, no-JS, reduced-motion, print/SVG/PNG | deterministic complete static semantics |
| trigger | direct invocation, 27 positive intents, adjacent non-diagram requests, ambiguous diagram request | activate precisely; negative cases do not trigger |

## 8. Must-pass reference benchmark

| Field | Candidate value |
|---|---|
| Case ID | `REF-SWIMLANE-CASH-RECEIPTS-001` |
| Source | owner-provided revision R2 PNG, SHA-256 `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113`; historical unavailable R1 hash `51f4cddd5cf4d6b4460a6c4a4585425aa1e13bd4c12d18c9c439aed07dbcea51` retained for provenance only |
| Current custody | `qa-only/REF-SWIMLANE-CASH-RECEIPTS-001-r2.png`; owner-authorized QA-only, never packaged |
| Expected type | Swimlane with grouped ownership headers |
| Input language | Vietnamese |
| Approved dials | `slide-16x9`, `faithful`, `mixed`, all three approved static modes, `html+png`, `none` |
| Semantic assertions | actors/lanes; money/check, document, listing and archive-file roles; numbered traceable steps/handoffs; consistent legend |
| Geometry assertions | orthogonal clear connectors, no unrelated-node crossing, no clipping/overlap or compressed text |
| Independence | original layout, prose, tokens and shapes; no pixel clone or bundled reference image |
| Output | HTML/SVG and PNG when renderer exists; renderer-absent fallback separately tested |
| Approval | benchmark record/assertions approved 2026-08-15; later original golden direction still requires owner approval |

The reference image is used only to validate capability level and semantics. It is never packaged and never used as a pixel-similarity target.

R2 semantic inventory, recorded as data rather than visual instructions:

- six actor/functional lanes: Khách hàng, Phòng thư, Thu tiền, Phải thu, Sổ cái and Ngân hàng;
- grouped ownership headers: Thủ quỹ over Phòng thư/Thu tiền, and Kế toán trưởng over Phải thu/Sổ cái;
- artifact roles include Séc, Giấy báo chuyển tiền, Bảng kê chuyển tiền, Tệp phải thu and Tệp sổ cái;
- handoffs are numbered from (1) through (5) and must remain independently traceable;
- legend semantics distinguish money/check, reconciliation document, stored file and listing;
- only these semantic facts and the approved hard checks may guide the future original output; coordinates, colors, exact geometry and pixels are excluded.

## 9. Approval record

Tran Ngoc Thien approved the case inventory, must-pass designation, rubric weights and thresholds, benchmark dials, and QA-only custody of revision R2 on 2026-08-15. This approval locks the benchmark contract but does not pre-approve any future rendered golden; P-06/P-12 owner review remains mandatory.
