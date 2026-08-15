# P-01 capability and provenance matrix

**Matrix ID:** `P01-CAP-MATRIX-1`  
**Snapshot:** `diagram-design@09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6`  
**Interpretation rule:** each row captures an abstract requirement and future test intent only. It authorizes no implementation in P-01 and no copying from a specimen or reference.

Permanent source prefix: `https://github.com/cathrynlavery/diagram-design/blob/09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6/skills/diagram-design/`.

## 1. Canonical types

For every row below, the implementation boundary is the same: define an original semantic grammar and renderer later from first principles; do not reuse upstream prose, coordinates, formulas, SVG/CSS/HTML, templates, examples, labels, palettes or pixels. Planned evidence is an original semantic fixture, contract assertion and render smoke test, with quantitative source-to-render checks where applicable.

| Capability ID | Canonical class | Abstract functional requirement | Locked source | Planned test/evidence | Copying risk note |
|---|---|---|---|---|---|
| `CAP-T01` | Architecture | Components, boundaries and directed relationships in a system topology | `SKILL.md` §3; `references/type-architecture.md` | topology/endpoint/zone assertions | high: distinctive layout and connectors must be redesigned |
| `CAP-T02` | IT current-state | Legacy landscape grouped by organizational or modernization context | `SKILL.md` §3; `references/type-it-state.md` | group/state/handoff fixture | high: parametric formulas and specimen are excluded |
| `CAP-T03` | Flowchart | Decisions, branches, joins and terminal outcomes | `SKILL.md` §3; `references/type-flowchart.md` | branch coverage and reachability | medium |
| `CAP-T04` | Sequence | Time-ordered messages, actor lifelines and guarded fragments | `SKILL.md` §3; `references/type-sequence.md` | ordering, sync/async/return, fragment test | high: OAuth specimen excluded |
| `CAP-T05` | State machine | States, transitions, guards and terminal states | `SKILL.md` §3; `references/type-state.md` | transition/guard/reachability test | medium |
| `CAP-T06` | ER/data model | Entities, fields, relationships and cardinality | `SKILL.md` §3; `references/type-er.md` | entity/cardinality preservation | medium |
| `CAP-T07` | Timeline | Events ordered and positioned along time | `SKILL.md` §3; `references/type-timeline.md` | date/order/timezone assertions | medium |
| `CAP-T08` | Swimlane | Actors/lanes, ownership, ordered steps and cross-lane handoffs | `SKILL.md` §3; `references/type-swimlane.md` | grouped-lane and handoff trace | high: project benchmark must remain original |
| `CAP-T09` | Quadrant | Items positioned on two declared axes/scales | `SKILL.md` §3; `references/type-quadrant.md` | coordinate/axis/label assertions | high: consultant specimen excluded |
| `CAP-T10` | Radar/Spider | Multiple series across a declared common scale | `SKILL.md` §3; `references/type-radar.md` | scale, axis and series value checks | high: do not reuse upstream geometry |
| `CAP-T11` | Loop/Flywheel | Reinforcing cycle with ordered stations and optional shared state | `SKILL.md` §3; `references/type-loop.md` | closure/order/state assertions | high: geometry and terminal specimen excluded |
| `CAP-T12` | Nested | Hierarchy expressed by containment | `SKILL.md` §3; `references/type-nested.md` | containment/depth preservation | medium |
| `CAP-T13` | Tree | Parent-child hierarchy | `SKILL.md` §3; `references/type-tree.md` | acyclic parent/child and depth tests | medium |
| `CAP-T14` | Org chart | Ownership, reporting, routing and escalation | `SKILL.md` §3; `references/type-org-chart.md` | ownership/reporting/escalation test | medium |
| `CAP-T15` | Layer stack | Ordered abstraction/control layers | `SKILL.md` §3; `references/type-layers.md` | layer order and dependency test | medium |
| `CAP-T16` | Venn | Set membership and intersections | `SKILL.md` §3; `references/type-venn.md` | region membership assertions | medium |
| `CAP-T17` | Pyramid/Funnel | Ranked hierarchy or proportional conversion/drop-off | `SKILL.md` §3; `references/type-pyramid.md` | ordering plus proportional integrity | high: shape geometry must be original |
| `CAP-T18` | Bar chart | Categorical quantitative comparison | `SKILL.md` §3; `references/type-bar.md` | value/axis/baseline/legend checks | high: numeric integrity |
| `CAP-T19` | Line chart | Continuous trend series over an ordered domain | `SKILL.md` §3; `references/type-line.md` | values/order/gaps/unit checks | high: numeric integrity |
| `CAP-T20` | Gantt | Tasks/phases with start, end, duration and dependencies | `SKILL.md` §3; `references/type-gantt.md` | date/timezone/duration/order checks | high: temporal integrity |
| `CAP-T21` | Scatter plot | Paired quantitative observations and correlation context | `SKILL.md` §3; `references/type-scatter.md` | point count and coordinate checks | high: numeric integrity |
| `CAP-T22` | High-Level | End-to-end data/platform stack with grouped cross-cutting concerns | `SKILL.md` §3; `references/type-high-level.md` | stage/group/cross-cutting relation test | high: formulas and specimens excluded |
| `CAP-T23` | Process | Multi-actor sequential workflow with data handoffs | `SKILL.md` §3; `references/type-process.md` | step/lane/artifact/handoff trace | high: parametric formulas excluded |
| `CAP-T24` | Medallion | Ordered storage/quality tiers and promotion paths | `SKILL.md` §3; `references/type-medallion.md` | tier/order/policy/promotion checks | high: formulas and specimens excluded |
| `CAP-T25` | Data flow | Role-scoped pipeline steps, inputs/outputs and transfers | `SKILL.md` §3; `references/type-data-flow.md` | role/step/artifact/edge checks | high: parametric formulas excluded |
| `CAP-T26` | DP integration | Sources-to-platform-to-consumers integration topology | `SKILL.md` §3; `references/type-dp-integration.md` | boundary/source/core/consumer test | high: formulas and specimens excluded |
| `CAP-T27` | DP security matrix | Per-role/per-component permission states | `SKILL.md` §3; `references/type-dp-security-matrix.md` | every cell/state/legend assertion | high: matrix semantics and accessibility |

## 2. Variants and reusable primitives

| Capability ID | Class | Abstract functional requirement | Locked source | Independent implementation boundary | Planned test/evidence |
|---|---|---|---|---|---|
| `CAP-V01` | static variant | neutral light presentation | `SKILL.md` §10; 27 base light specimens | create original tokens/templates; no upstream visual system | 27-type light smoke matrix |
| `CAP-V02` | static variant | neutral dark presentation with equivalent semantics | `SKILL.md` §10; 27 base dark specimens | create original dark tokens; do not invert upstream values | 27-type dark smoke matrix + contrast |
| `CAP-V03` | static variant | editorial presentation around a complete diagram | `SKILL.md` §10; 27 base full specimens | original composition and copy | 27-type editorial smoke matrix |
| `CAP-V04` | Quadrant variant | named-cell two-by-two scenario matrix | `type-quadrant.md`; `example-quadrant-consultant.html` | extract scenario-matrix behavior only; no styling/layout reuse | cell/axis/scenario assertion |
| `CAP-V05` | Bar variant | grouped series comparison | `type-bar.md` “Variants” | original chart construction | grouped values/legend smoke |
| `CAP-V06` | Bar variant | stacked parts-to-total comparison | `type-bar.md` “Variants” | original chart construction | segment/total/proportion smoke |
| `CAP-V07` | Pyramid variant | apex-oriented hierarchy | `type-pyramid.md` | original geometry | order and hierarchy smoke |
| `CAP-V08` | Funnel variant | narrowing conversion/drop-off | `type-pyramid.md` | original geometry | count/ratio/drop-off integrity |
| `CAP-V09` | Sequence variant | `alt`, `opt`, and `loop` guarded fragments | `type-sequence.md` | implement semantic operators independently | operator/region/order smoke |
| `CAP-V10` | High-Level variant | alternate vertical/parametric arrangement | `type-high-level.md`; three `example-high-level-vertical*` specimens | behavior only; no formulas or coordinates | equivalent-IR alternate-layout smoke |
| `CAP-V11` | data-lake specimen family | data-platform pipeline/storage/analytics story represented by an existing grammar | three `example-datalake*` gallery specimens | preserve as specimen requirement; map to an existing canonical parent later, never create type 28 | semantic inventory test after parent mapping |
| `CAP-V12` | sketchy presentation | optional hand-drawn treatment without changing semantics | `primitive-sketchy.md` | devise an original effect; do not copy filter/template | static equivalence and legibility smoke |
| `CAP-V13` | terminal presentation | optional CLI-window presentation | `primitive-terminal.md`; `example-loop-terminal.html` | original presentation; no template/specimen reuse | static equivalence and contrast smoke |
| `CAP-V14` | annotation primitive | editorial side annotation linked to a target | `primitive-annotation.md` | original callout grammar and styling | association/reading-order smoke |
| `CAP-V15` | icon primitive | optional semantic monochrome symbols | `primitive-icons.md` | use only independently licensed/original future assets; never copy upstream icon markup | manifest/license/a11y/symbol smoke |
| `CAP-V16` | sequence specimen | bearer-call refresh branch as a combined-fragment case | three `example-sequence-oauth*` specimens | test idea only; create original scenario/data | fragment semantics smoke |

## 3. Semantic patterns

All seven source rows come from `references/semantic-patterns.md`. Patterns select behavior and then route to an existing layout grammar; none adds a visual type.

| Capability ID | Abstract functional requirement | Planned canonical parent | Independent implementation boundary | Planned test/evidence |
|---|---|---|---|---|
| `CAP-P01` | many producers converge on a finite queue/bottleneck with capacity and service behavior | Data flow | original primitives, labels and example | queue count/capacity/fan-in assertions |
| `CAP-P02` | repeated stages expose consistent semantic slots | Process | original stage/slot grammar | slot presence and order assertions |
| `CAP-P03` | loose/unstructured input becomes a durable structured artifact | Data flow | original transformation example | input/transformation/output assertions |
| `CAP-P04` | two policy traces expose state and first divergence | Flowchart | original policy example | pass/fail/skipped/not-reached/divergence |
| `CAP-P05` | approved route crosses trust boundaries while bypass paths are denied | Architecture | original security scenario | boundary/allow/deny assertions |
| `CAP-P06` | controls are grouped by enforcement location or owner | Layer stack | original control catalog | control/owner/enforcement assertions |
| `CAP-P07` | later safeguards compensate for earlier gaps and leave explicit residual risk | Layer stack | original risk scenario | gap/control/residual-risk propagation |

## 4. Import and fidelity

| Capability ID | Class | Abstract functional requirement | Locked source | Independent boundary | Planned test/evidence |
|---|---|---|---|---|---|
| `CAP-I01` | draw.io carrier | accept `.drawio` and `.drawio.xml` as untrusted data | `import-drawio.md` | independent bounded parser; never run upstream script | normal/malformed/oversized fixtures |
| `CAP-I02` | draw.io carrier | extract embedded models from `.drawio.png` | `import-drawio.md` | independent decoding with caps; no image interpretation fallback | embedded/missing/corrupt fixtures |
| `CAP-I03` | draw.io carrier | extract embedded models from `.drawio.svg` | `import-drawio.md` | independent XML/data handling with XXE/resource bans | embedded/missing/adversarial fixtures |
| `CAP-I04` | draw.io document | preserve independent pages or selected page | `import-drawio.md` | original IR and page routing | multipage/all/selection fixtures |
| `CAP-I05` | Mermaid carrier | accept `.mmd` and `.mermaid` as inert text | `import-mermaid.md` | independent grammar parser; never render Mermaid | normal/malformed/adversarial fixtures |
| `CAP-I06` | Mermaid carrier | discover one or more fenced Mermaid blocks in Markdown | `import-mermaid.md` | original bounded fence scanner | zero/one/multi-block fixtures |
| `CAP-I07` | Mermaid grammar | flowchart/graph semantics | `import-mermaid.md` | original parser, no upstream code/grammar text | nodes/edges/groups/directions test |
| `CAP-I08` | Mermaid grammar | sequenceDiagram semantics | `import-mermaid.md` | original parser | actor/order/message/fragment test |
| `CAP-I09` | Mermaid grammar | stateDiagram-v2 semantics | `import-mermaid.md` | original parser | state/guard/terminal test |
| `CAP-I10` | Mermaid grammar | erDiagram semantics | `import-mermaid.md` | original parser | entity/field/cardinality test |
| `CAP-I11` | safe redraw | retain content semantics but discard source layout/style/executable directives | both import references | independent normalized IR and renderer | no execution/network/style carry-over |
| `CAP-I12` | fidelity ledger | account for source items kept, merged, dropped with reason, or identified as source rot | both import references; `output-spec.md` | original ledger schema and wording | reconciliation equality assertion |

## 5. Output dials and export behavior

| Capability ID | Class | Options observed | Abstract requirement | Source | Planned test/evidence |
|---|---|---|---|---|---|
| `CAP-O01` | format | `html`, `svg`, `png`, `html+png` | explicit deliverable choice with transparent renderer fallback | `output-spec.md`; `export.md` | output/fallback contract tests |
| `CAP-O02` | size | `doc-inline`, `doc-wide`, `slide-16x9`, `slide-4x3`, `social-og`, `social-square`, `print-a4-landscape`, `print-letter-landscape`, `fit` | destination-aware canvas and readability | `output-spec.md` | preset/bounds/typography smoke |
| `CAP-O03` | detail | `faithful`, `balanced`, `simplified` | deterministic preservation/degrade policy with ledger | `output-spec.md` | boundary/pairwise/fidelity tests |
| `CAP-O04` | audience | `engineer`, `mixed`, `executive` | change wording granularity without inventing facts | `output-spec.md` | same-IR audience transformations |
| `CAP-O05` | export | diagram-only SVG extraction | portable static vector output | `export.md` | validity/font/final-state checks |
| `CAP-O06` | export | PNG rasterization only when a renderer exists | conditional raster output, no auto-install | `export.md` | renderer present/absent tests |
| `CAP-O07` | accessibility | complete SVG accessible name/description and unique IDs | `SKILL.md` QA checklist | independent accessible SVG contract | automated name/ID/read-order checks |

## 6. Motion modes and primitives

All rows come from `references/animation.md`. The source's controller/script is explicitly excluded; later implementation must be original.

| Capability ID | Class | Abstract requirement | Planned test/evidence |
|---|---|---|---|
| `CAP-M01` | mode `none` | complete static, script-free default | no-JS/static/print/export equality |
| `CAP-M02` | mode `reveal` | one deterministic ordered reveal ending complete | one-run/end-state/determinism test |
| `CAP-M03` | mode `step` | user-controlled deterministic semantic states | keyboard/control/order test |
| `CAP-M04` | mode `loop` | decorative repetition that carries no unique meaning | semantic-equivalence/reduced-motion test |
| `CAP-M05` | primitive | bounded path draw over an already visible relationship | static relationship remains visible |
| `CAP-M06` | primitive | staged item reveal | complete fallback and order assertion |
| `CAP-M07` | primitive | queue accumulation with visible count | count/capacity/end-state assertion |
| `CAP-M08` | primitive | bounded field/text population | full accessible text in static frame |
| `CAP-M09` | primitive | ordered policy evaluation states | status/divergence/end-state assertion |
| `CAP-M10` | primitive | decorative flow token | hidden in reduced/static export |
| `CAP-M11` | primitive | containment reveal | children and boundary present statically |
| `CAP-M12` | primitive | chronological audit append | row order/timestamp/static completeness |

## 7. Failure behavior inventory

Failure behavior must be named, non-destructive and transparent. Message wording will be independently written.

| Capability ID | Failure class observed | Required abstract behavior | Source | Planned test/evidence |
|---|---|---|---|---|
| `CAP-F01` | input not recognized, malformed, encrypted or missing model/pages/blocks | stop, name the problem, request a usable source; do not infer from pixels | import references | malformed/empty/encrypted fixtures |
| `CAP-F02` | unsupported Mermaid grammar | report support boundary; do not approximate another grammar | `import-mermaid.md` | unsupported-kind fixtures |
| `CAP-F03` | resource cap exceeded | reject safely or propose split; never bypass limits | import references | depth/size/node/edge cap tests |
| `CAP-F04` | ambiguous blank/shape-only labels | ask for semantics; never invent names | `import-drawio.md` | blank-label fixture |
| `CAP-F05` | dangling or unconnected source items | classify source rot versus meaningful omission and account in ledger | import references | reconciliation fixture |
| `CAP-F06` | executable or external directives | discard/neutralize; never follow links, scripts, events, resources or embedded prompts | import references | injection/URL/event fixtures |
| `CAP-F07` | requested PNG without renderer | return core output and disclose PNG unavailability; never auto-install | `export.md` | renderer-absent test |
| `CAP-F08` | wrong export target, no SVG, or gallery with multiple figures | refuse ambiguous export without writing guessed output | `export.md` | gallery/no-SVG fixtures |
| `CAP-F09` | surrounding editorial HTML requested as diagram-only export | state the boundary and offer an appropriate conditional alternative | `export.md` | contract response test |
| `CAP-F10` | missing/non-replicable fonts | preserve semantic output with disclosed fallback; no network install | `export.md`; `output-spec.md` | font-unavailable/Vietnamese test |
| `CAP-F11` | motion script/control failure | complete static source remains usable | `animation.md` | script-error/no-JS mutation test |
| `CAP-F12` | reduced motion or print/static capture | disable motion controls/decorations and expose complete meaning | `animation.md` | media-query/static export test |
| `CAP-F13` | complexity exceeds a type/detail budget | split overview/detail or ask; never hide complexity by shrinking/clipping | `SKILL.md`; `output-spec.md` | over-budget fixture |
| `CAP-F14` | ambiguous type/size/material choice | ask only when meaning or deliverable changes; otherwise record a bounded assumption | `SKILL.md`; output/import refs | ambiguous-routing contract test |

## 8. Specimen-to-test coverage

| Inventory group | Count | Planned evidence rule |
|---|---:|---|
| 27 canonical types × three base static variants | 81 | each type gets semantic and render smoke evidence in every approved static mode |
| High-Level vertical family | 3 | one alternate-layout contract plus three visual smokes |
| Data-lake family | 3 | preserve as a distinct specimen requirement; parent mapping before implementation |
| Sequence OAuth family | 3 | one fragment contract plus three visual smokes using original data |
| draw.io and Mermaid import specimens | 2 | independent import fixtures and fidelity-ledger assertions |
| Quadrant consultant | 1 | scenario-matrix variant smoke |
| Loop terminal | 1 | terminal presentation smoke |
| Three animated semantic specimens | 3 | individual semantic pattern + motion-mode smokes using original scenarios |
| **Total** | **97** | no upstream specimen becomes a golden or bundled asset |

## 9. Observed upstream features outside the locked D-005 classes

The snapshot also contains brand onboarding, named client profiles, a mutable style guide, commands/prompts and an icon library. They are recorded so provenance is complete, but P-01 does not add them to project scope:

| Observed feature | Source | P-01 classification |
|---|---|---|
| URL/skill/folder brand extraction and style-guide mutation | `onboarding.md`, `style-guide.md` | ancillary upstream feature; not imported; project D-008/D-009/D-010 and no-network rule control future behavior |
| Named client profiles and project marker | `profiles.md` | ancillary 2.4 feature; not a required D-005 class |
| Upstream commands/prompts and provider manifests | repository root | upstream packaging material; no copying and no authority over this project's packages |
| Upstream icon markup/assets | `primitive-icons.md`, third-party ledger | excluded material; any future icon set requires independent source/license/asset manifest |

No support-status or scope expansion is inferred from these observations.
