# P-01 source snapshot record

**Record ID:** `P01-SNAPSHOT-2026-08-15`  
**Captured:** 2026-08-15, Asia/Ho_Chi_Minh  
**Purpose:** read-only evidence for G-01; this file is not implementation material.  
**Authority:** scope and requirements remain in `PROJECT-CONTRACT.md`; status remains in `PLAN.md`.

## 1. Functional source: diagram-design

| Field | Locked value |
|---|---|
| Repository | `https://github.com/cathrynlavery/diagram-design` |
| Branch resolved | `main` |
| Commit | `09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6` |
| Commit time | `2026-08-14T14:28:44-07:00` |
| Commit subject | `Add named client profiles (#61)` |
| Exact tag at commit | none |
| Upstream plugin metadata version | `2.4.0` |
| Git tree | `aa59393dfabbbcbb4bcb62a7cf9f43c1ce26c9c2` |
| SHA-256 of sorted recursive `git ls-tree` output | `6092dc41f39e3ff4638f783d66b75ad1a4073874f4bf540c60bd331f3e3db804` |
| Files in snapshot | 320 |
| Snapshot acquisition | exact-commit shallow fetch into `/private/tmp`; no upstream file copied into this workspace |
| Declared repository license | MIT; `LICENSE` SHA-256 `bb7e12e91fecef43024111123ff784cec6c485585561d8b552557c0173b3ed29` |
| Upstream third-party ledger | `THIRD_PARTY_LICENSES.md` SHA-256 `22f5afcea56373e84d7f7eff93d8d4d6e4b81c5375bb1c996e78b91e53fa0b37` |

### Files used as functional evidence

| File at locked commit | SHA-256 | Evidence role |
|---|---|---|
| `README.md` | `12d51301d2204fac89375768b7ada26abc6282b324e36fb47543c1a7e802c88b` | repository claims, gallery and surface description |
| `skills/diagram-design/SKILL.md` | `8366ef4d11c3a9591556deb55320ea3521c138ccdad834eb087b8062f41d93a1` | canonical 27-type selection table and top-level behavior |
| `skills/diagram-design/references/semantic-patterns.md` | `6df3d41cafea6a0f16f8921a50af732e34f6172d4ba6fb9f05ec8f92bc27e472` | seven behavior patterns |
| `skills/diagram-design/references/animation.md` | `24ce83341aee976680cb69d43b2afab40efcfa97edcd394e5b17183eb58fc94a` | static-first motion modes and primitives |
| `skills/diagram-design/references/import-drawio.md` | `106d29f5501fe39d423f9145c04ab1e1ffa747d6cd453ee8ffa58a604413c4c5` | draw.io input behavior and failures |
| `skills/diagram-design/references/import-mermaid.md` | `491ff83440fc995401b5ba20f63325f976732bf1669003c1840b4137072cc274` | Mermaid input behavior and failures |
| `skills/diagram-design/references/output-spec.md` | `d8fa916f523b99ada083a652f4440d3f0d086a8af61ae333bac50153338f42a3` | format, size, detail, audience and fidelity dials |
| `skills/diagram-design/references/type-*.md` | 27 files, bound by the locked Git tree | canonical type-specific functional evidence |
| `skills/diagram-design/assets/example-*.html` | 97 files, bound by the locked Git tree | specimen presence only; no visual/code material may be reused |

Permanent source URLs use the locked commit, for example:

- `https://github.com/cathrynlavery/diagram-design/blob/09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6/skills/diagram-design/SKILL.md`
- `https://github.com/cathrynlavery/diagram-design/tree/09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6/skills/diagram-design/references`
- `https://github.com/cathrynlavery/diagram-design/tree/09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6/skills/diagram-design/assets`

## 2. Canonical taxonomy lock

The canonical selection table contains exactly 27 entries, and the snapshot contains exactly 27 `type-*.md` references.

| ID | Canonical type | Locked reference |
|---|---|---|
| `TYPE-01` | Architecture | `type-architecture.md` |
| `TYPE-02` | IT current-state | `type-it-state.md` |
| `TYPE-03` | Flowchart | `type-flowchart.md` |
| `TYPE-04` | Sequence | `type-sequence.md` |
| `TYPE-05` | State machine | `type-state.md` |
| `TYPE-06` | ER/data model | `type-er.md` |
| `TYPE-07` | Timeline | `type-timeline.md` |
| `TYPE-08` | Swimlane | `type-swimlane.md` |
| `TYPE-09` | Quadrant | `type-quadrant.md` |
| `TYPE-10` | Radar/Spider | `type-radar.md` |
| `TYPE-11` | Loop/Flywheel | `type-loop.md` |
| `TYPE-12` | Nested | `type-nested.md` |
| `TYPE-13` | Tree | `type-tree.md` |
| `TYPE-14` | Org chart | `type-org-chart.md` |
| `TYPE-15` | Layer stack | `type-layers.md` |
| `TYPE-16` | Venn | `type-venn.md` |
| `TYPE-17` | Pyramid/Funnel | `type-pyramid.md` |
| `TYPE-18` | Bar chart | `type-bar.md` |
| `TYPE-19` | Line chart | `type-line.md` |
| `TYPE-20` | Gantt | `type-gantt.md` |
| `TYPE-21` | Scatter plot | `type-scatter.md` |
| `TYPE-22` | High-Level | `type-high-level.md` |
| `TYPE-23` | Process | `type-process.md` |
| `TYPE-24` | Medallion | `type-medallion.md` |
| `TYPE-25` | Data flow | `type-data-flow.md` |
| `TYPE-26` | DP integration | `type-dp-integration.md` |
| `TYPE-27` | DP security matrix | `type-dp-security-matrix.md` |

### 27/29 discrepancy

- At capture time, GitHub's live repository description said “29 editorial diagram types.” Repository descriptions are mutable metadata outside the Git tree.
- The locked `SKILL.md`, `README.md`, contribution checks and 27 type-reference files all say or enforce 27 visual types.
- The gallery also contains non-canonical specimens and variants. Their presence does not create new canonical types.
- Result: `27` is locked. No two additional types are inferred from the number `29`.

## 3. Specimen inventory

The snapshot contains 97 `example-*.html` files. They are evidence of behaviors and coverage only. Their HTML, SVG, CSS, text, layout and pixels are prohibited source material.

### Base static specimens: 81

Each of these 27 stems has exactly three files: `example-<stem>.html`, `example-<stem>-dark.html`, and `example-<stem>-full.html`.

`architecture`, `it-state`, `flowchart`, `sequence`, `state`, `er`, `timeline`, `swimlane`, `quadrant`, `radar`, `loop`, `nested`, `tree`, `org-chart`, `layers`, `venn`, `pyramid`, `bar`, `line`, `gantt`, `scatter`, `high-level`, `process`, `medallion`, `data-flow`, `dp-integration`, `dp-security-matrix`.

### Additional specimens: 16

| Files | Classification | Canonical effect |
|---|---|---|
| `example-datalake{,-dark,-full}.html` | gallery specimen family; nearest existing architecture/data-platform grammar to be mapped later | no new type |
| `example-high-level-vertical{,-dark,-full}.html` | High-Level parametric/orientation variant | no new type |
| `example-sequence-oauth{,-dark,-full}.html` | Sequence combined-fragment specimen | no new type |
| `example-import-drawio.html` | import specimen | no new type |
| `example-import-mermaid.html` | import specimen | no new type |
| `example-quadrant-consultant.html` | Quadrant presentation variant | no new type |
| `example-loop-terminal.html` | Loop with terminal presentation variant | no new type |
| `example-policy-trace-animated.html` | paired policy-trace semantic/motion specimen | no new type |
| `example-queue-animated.html` | fan-in queue semantic/motion specimen | no new type |
| `example-paved-road-animated.html` | secure paved-road semantic/motion specimen | no new type |

`example-datalake*` is deliberately not assigned a new canonical parent in P-01. The locked source does not provide a separate type reference for it; P-02/P-05 must map its abstract behavior without increasing the type count.

## 4. Principle source: Thien-UI-UX-Ultra

| Field | Locked value |
|---|---|
| Local repository | `<LOCAL_REFERENCE_REPOSITORY>/Thien-UI-UX-Ultra` |
| Commit | `fb4e57758f525827e04004737d779f4c93b9b3a0` |
| Tag | `v2.0.0` |
| Commit time | `2026-08-10T04:32:48+07:00` |
| Git tree | `96e55f4693b81af594cfb9190fc66321a3b5fecb` |
| Role | principle/workflow source only; never an implementation donor |

| File | SHA-256 | Permitted abstract learning |
|---|---|---|
| `dev/principles-2.0.0.md` | `73aae6e31b767e9fcccde8902cb98309317ea44f3cf6da0686276afdb2a5dddc` | evidence honesty, source rights, data/accessibility priority, dependency discipline |
| `src/thien-skill-ui-ux-ultra/SKILL.md` | `d016a43b99173b5736f0e0f5e050841e9b748d115f23583c79cb068d709084d4` | staged design and real-output verification workflow |
| `references/design-contract.md` | `a5deaa23591e75c8f419519d6bca5d4975748b9a861b29e1b03a69a8e229eab2` | compact pre-production design contract |
| `references/routing.md` | `896b35adff3b64ba6c194ea6ee517ad509e3f08cccca579b667847113b585ed6` | smallest-complete progressive routing and risk gates |
| `references/delivery-and-handoff.md` | `92c04015ce914add9d71784c112ea7b7ab51526f1621799f4defb9d57569f44d` | render/inspect/revise/verify and retained evidence |

No code, script, template, prose, data row, asset, token value or test fixture from this repository is authorized for reuse.

## 5. Custody and contamination check

- Upstream checkout exists only in the temporary acquisition location and is excluded from deliverables.
- This workspace contains governance and P-01 evidence documents only.
- No upstream HTML, SVG, CSS, JavaScript, Python, template, icon, image, gallery or specimen was copied into the workspace.
- P-01 records names, counts, hashes, abstract behaviors and permanent source locators. These are provenance evidence, not implementation.
