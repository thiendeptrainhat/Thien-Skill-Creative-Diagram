# P-18R6 evidence — fourteen-engine neutral-light review-17 candidate

**Date:** 2026-08-27  
**Authority:** D-051, D-052, D-058, D-059, D-060, D-061, D-062, D-063, D-064, D-065, D-066, D-067, D-068, D-069, D-070, D-071, D-072, D-073, D-074, D-075, D-076, D-077  
**Candidate:** `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`  
**Exact manifest SHA-256:** `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`  
**Disposition:** frozen owner-approved candidate; P-18 `passed`  
**Gate:** `G-03@1.5.0 PASS`

## Outcome

P-18R6 created exactly one `neutral-light` anchor for every one of the fourteen P-18R4 layout engines: fourteen standalone HTML files, fourteen matching SVGs, a labeled index, a masked review page, fourteen canonical PNG previews and labeled/masked PNG contact sheets. The exact owner-approved P-18R5 review-04 Swimlane source remains byte-identical and read-only; all prior review-16 contracts remain intact. Review-17 changes only diagram 09 and diagram 14 under D-076: hierarchy exposes `1 FRONT DOOR`, `4 DOMAINS`, `5 SPECIALIST PODS`; Sankey strengthens only the `unit-flaked` focal ribbon and directly annotates `1,000 / 12,000 MIN · 8.3% OF BUDGET` without changing values, scale, bar/ribbon geometry, conservation or interface occupancy. All twelve non-target anchor HTML/SVG pairs — 24 files — remain byte-identical to review-16.

The gallery is QA-only under `evidence/p18/r6/`. No canonical runtime, package, `dist/`, publication mirror, Git state, tag or Release was changed. P-19 was not started.

## Verification

| Check | Result |
|---|---|
| Exact engine inventory | PASS — 14/14 unique locked engines |
| Standalone artifacts | PASS — 14 HTML + 14 SVG; no script/network/foreignObject dependency |
| Static semantic/typography/geometry/accessibility/security | PASS — 366/366 |
| Diagram 13 origin/axis marker contract | PASS — two declared quantitative axes; no `marker-start`, `marker-mid` or `marker-end` in serialized SVG or computed browser style |
| Quantitative ranges and Sankey conservation binding | PASS — stages `5,200 + 4,000 + 2,800 = 12,000`; outcomes `9,400 + 1,600 + 1,000 = 12,000` |
| Deterministic regeneration | PASS |
| P-18R5 parent manifest pin | PASS — `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8` |
| Exact P-18R5 Swimlane source preservation | PASS — byte identical; SHA-256 `a0d3949d177daebca0c84070b18d8366a025025261d03a7e03896550beb8253c` |
| Diagram 06 phase coverage | PASS — six ordered major phases cover all six workflow steps; `CHUẨN BỊ` precedes `NHẬN BỘ`; top rail and lower legend agree |
| Diagram 06 R6 extension boundary | PASS — R6 SVG intentionally differs from R5 only through the declared D-066 local phase layer; inherited hop/connector geometry remains unchanged |
| Diagram 11 entity/connector centering | PASS — top-row center-y `310px`; ORDER and ORDER_ITEM center-x `850px`; all three connectors terminate at centered boundaries |
| Diagram 11 content padding | PASS — measured bottom padding `32px` for every entity, above the `24px` minimum |
| Diagram 11 relationship/cardinality labels | PASS — names remain exactly `PLACES`, `PAID BY`, `CONTAINS`; six endpoint `1`/`N` labels sit inline on the relationship axes; each has an 8px along-line × 4px perpendicular canvas knockout, connector→knockout→label paint order, text/knockout node clearances `16/8px`, and emitted axis error ≤`0.06px` |
| Diagram 12 exact directional annotations | PASS — `↑ HIGH IMPACT`, `← LOW EFFORT`, `↓ LOW IMPACT`, `HIGH EFFORT →`; axis/direction/prefix-suffix bindings match D-067 |
| Diagram 12 measured placement | PASS — upper/lower notes share `24px` right-of-axis offset; left/right notes share `42px` below-axis baseline offset; measured axis clearances are `16/27/31/27px` against minimum `16px` |
| Diagram 12 semantic preservation | PASS — quadrant titles, six initiative positions and the single coral `Freeze contract` focal point are unchanged |
| Diagram 12 focal-region perimeter | PASS — pale coral fill retained; serialized/computed stroke is `none`; no transparent/zero-opacity/zero-width workaround; review-09 rectangle geometry preserved |
| Diagram 14 Sankey scale and occupancy | PASS — shared `0.025px/minute` scale; 7/7 node heights and 9/9 ribbon thicknesses bind to value; every applicable source/stage/outcome interface is tiled top-to-bottom with zero gap/overlap |
| Diagram 14 labels and bar geometry | PASS — every title/value stack is centered above its bar with ≥12px measured clearance; all bars are square-corner `<rect>` elements with no `rx` |
| Diagram 14 upper-row top alignment | PASS — `Monthly budget`, `Unit tests`, `Passed` all have exact top-y `210px`; max static/browser spread `0.00px` ≤ `0.01px` |
| Diagram 09 D-076 five-second hierarchy binding | PASS — visible `1 FRONT DOOR`, `4 DOMAINS`, `5 SPECIALIST PODS`; root subtitle repeats the `1 / 4 / 5` structure |
| Diagram 14 D-076 five-second focal binding | PASS — focal `unit-flaked` ribbon has stronger coral contrast and direct `FLAKED RERUNS · 1,000 / 12,000 MIN · 8.3% OF BUDGET` annotation; quantitative geometry remains review-16-identical |
| Structural silhouette signatures | PASS — at least 12/14 distinct coarse signatures |
| Diagram 04 crossing completeness | PASS — both remaining crossings use continuous shared-geometry hops; base routes precede both repaints |
| Diagrams 04/08/09 semantic band alignment | PASS — boundaries `40/280/520/760/1000`, `204/384/564/744`, `60/300/540/780`; every member center equals its band midpoint; minimum separator clearances `22/27/58px`; zero member/separator intersection |
| Diagram 04 rank/corridor balance | PASS — 240px rank step, 116px inter-rank gap; bridged lower corridors at y=`738/782` straddle rather than coincide with the y=`760` boundary |
| Diagrams 01–03 containment | PASS — every direct child is inside its parent with declared minimum padding |
| Diagrams 01–03 group centering | PASS — group bbox centered on both axes; row/column/single alignment contracts hold |
| Diagrams 01–04 corner-style contract | PASS — whole-chart `rounded` default; explicit-user `straight` serializer contains no rounded-corner command |
| Diagram 10 continuous pyramid geometry | PASS — one outer triangle; true three-vertex apex; three supporting trapezoids; exact shared endpoints; single-stroke seams |
| Diagram 10 axis clearance | PASS — measured 160px against declared minimum 140px; no polygon/arrow intersection |
| Diagram 10 real-font text containment | PASS — 8/8 title/metadata bboxes remain inside their owning polygons with declared minimum inset 8px; `Flagship decision` remains 24px |
| Diagram 10 right-side annotation rail | PASS — `THE APEX`, `~4 / YR`, `~12 / YR`, `~240 / YR` have semantic cadence binding, canvas fit and measured polygon clearance ≥56px |
| Diagram 10 equal annotation visual gap | PASS — `71.996px`, `72.003px`, `72.003px`, `72.002px`; max-minus-min spread `0.007px` ≤ `0.01px` |
| Local SVG rasterization and implementer visual inspection | PASS — 14/14 canonical Quick Look previews; diagrams 09/14 inspected after D-076 remediation |
| Full canonical regression | PASS — 148/148 |
| Implementer visual-craft precheck | PASS — 92.5/100; minimum dimension 4.5/5 |
| Browser QA | PASS — 42/42 engine × viewport cases; zero console error/external request; inherited assertions plus D-076 hierarchy/focal checks pass |
| Masked independent recognition | PASS — 14/14, target ≥12/14 |
| Independent five-second takeaway review | PASS — 14/14; both D-076 target findings resolved |
| Independent visual-craft gate | PASS — 93/100; minimum dimension 4.0/5 |
| Exact manifest review | PASS — independent reviewer verified 75/75 records by byte size and SHA-256 |
| Owner visual approval | PASS — Tran Ngoc Thien approved exact review-17 under D-077 |
| `G-03@1.5.0` | PASS — explicitly approved under D-077 |

The independent result and owner approval are independently attributable: the reviewer established the technical/visual gates, and D-077 separately records owner acceptance and gate closure.

## Visual remediation trace

Review-02 resolved the five owner comments in D-060: diagrams 01–03 use the approved rounded-orthogonal connector grammar; diagram 04 received its first continuous shared-geometry hop; diagram 05 has equal `NO` spans and returns the second `NO` to `Validate evidence`; diagram 07 keeps `Contract v1` and `Anchor review` above the rail; and diagram 09 uses centered, preferentially straight parent-child connections.

Review-03 resolves D-061 for diagram 04. The four node ranks now advance in exact 220px steps with 96px inter-rank node gaps; corridor midpoints follow the same rhythm, and the lower fan-out corridors form a 20px ladder centered on y=694. Both remaining crossings have route-integrated hops with shared route/repaint geometry, crown-only underlay and zero-gap joins. All ten base routes paint before the two hop repaints. One whole-chart option controls every 90° turn: `rounded` is the default, while an explicit user request for `straight` overrides it and serializes all turns without `Q` corner commands.

Review-04 resolves D-062 for diagrams 01–03. Every direct child node or subcontainer now has machine-readable parent geometry and remains inside its parent with the declared minimum padding. The complete direct-child group is centered on both parent axes; row children share one center-y, column children share one center-x, and a single child shares the parent center. In diagram 01, `Astro origin` is fully inside `APPLICATION`; the `Cloud edge` + `Astro origin` row is centered, and the `MDX bundle` + `Media store` column is centered inside `CONTENT`. The same chart-level corner option now covers diagrams 01–04: `rounded` remains default, and explicit-user `straight` removes all rounded 90° commands without mixing styles.

Review-05 resolves D-063 for diagram 10. Four independently widened trapezoids were replaced with one common outer triangle partitioned by three horizontal cuts. `Flagship decision` is now a true triangle with three unique vertices and no top edge. The three supporting layers are trapezoids whose endpoints lie on the same apex-to-base side lines; adjacent layers share identical endpoint pairs and each seam renders exactly once over stroke-free fills. The leverage arrow sits outside the stack with a measured 160px gutter, exceeding the 140px declared minimum.

Review-06 resolves D-064 for diagram 10. The apex was enlarged locally and its content repositioned before considering wrap or font reduction; the 24px `Flagship decision` title and all seven remaining title/metadata bboxes now stay inside their owning polygons with at least 8px inset. A separate right-side annotation rail demonstrates annotation capability without contaminating the stack: `THE APEX` identifies the focal layer, while `~4 / YR`, `~12 / YR` and `~240 / YR` bind respectively to the existing quarterly, monthly and daily/workday semantics. Every note stays outside the polygons, inside the canvas and at least 56px from the stack.

Review-07 resolves D-065 for diagram 10. Review-06 used four independent x-offsets and measured `140.27px`, `82.63px`, `79.17px` and `72.45px` at the corresponding real-font bbox centers. Review-07 computes every x-coordinate from the same outer-triangle side equation plus one shared `72px` visual-gap target. Automated remeasurement reports `71.996px`, `72.003px`, `72.003px` and `72.002px`; the `0.007px` spread is below the `0.01px` limit, while all D-063/D-064 silhouette, text-containment, cadence, canvas-fit and minimum-clearance assertions remain `PASS`.

Review-08 resolves D-066 for diagrams 06 and 11. Diagram 06 now exposes six major phases for six workflow steps, beginning with `0 · CHUẨN BỊ` centered over `Chuẩn bị thanh toán`; the top rail and lower handoff legend carry identical ordered phase IDs. The exact P-18R5 source remains byte-identical, while the R6 copy is explicitly marked as a local D-066 extension. Diagram 11 uses one measured center-y for CUSTOMER, ORDER and PAYMENT, centers ORDER_ITEM under ORDER, connects at exact center-side endpoints, derives node height from real-font field bounds plus `32px` bottom padding, and keeps every relationship-label bbox inside its inter-node corridor with at least `8px` clearance.

Review-09 resolves D-067 for diagram 12. The four plain axis labels are replaced by directional labels matching the owner reference at the four axis-end positions: `↑ HIGH IMPACT`, `← LOW EFFORT`, `↓ LOW IMPACT` and `HIGH EFFORT →`. Upper/lower notes reuse one `24px` x-offset from the vertical axis; left/right notes reuse one `42px` baseline offset below the horizontal axis and align to their respective field edges. The generator records real-font bboxes, endpoint coordinates, axis/direction, arrow placement and measured clearance. Static QA proves exact label semantics, shared offsets, canvas fit, clearance and preservation of the existing quadrant/data/focal field.

Review-10 resolves D-068 for diagram 12. The `DO FIRST` focal rectangle keeps the same `x=190`, `y=120`, `width=590`, `height=319` geometry and pale coral fill but now serializes `stroke:none`; no opacity or zero-width substitution is accepted. Static QA proves the no-outline contract and deterministic regeneration while preserving both axes, all four D-067 annotations, all quadrant titles, all six initiatives, the `Freeze contract` focal point and the legend. Canonical Quick Look inspection confirms that the redundant perimeter is absent without weakening the focal field.

Review-11 resolves D-069 for diagram 11. Each relationship now emits one independent semantic name and two endpoint cardinalities: source `1`, target `N`. `PLACES` and `PAID BY` are centered above their horizontal connectors; `CONTAINS` is on the right side of the vertical connector. Measured QA binds relationship ID, endpoint role, value, placement and bbox clearance, and proves all six cardinalities and all three names stay outside node boundaries and clear of their lines. D-066 entity centers, connector endpoints, field padding and semantics are unchanged; all thirteen non-target anchor HTML/SVG pairs are byte-identical to review-10.

Review-12 resolves D-070 for diagram 11. Review-11's above/right cardinality placement is retired, but its semantic separation and relationship-name positions remain. Every source `1` and target `N` now overlays the exact connector axis. A dedicated no-stroke canvas-fill knockout is painted between the single semantic connector and the text, using 8px padding along the line and 4px perpendicular padding. Static QA checks exact endpoint binding, measured axis alignment, knockout geometry/fill/node clearance and DOM paint order; Chrome rechecks actual rendered text/knockout bounds at canonical, desktop and mobile viewports. All 26 non-target anchor HTML/SVG files are byte-identical to review-11.

Review-13 resolves D-071 for diagram 14. A shared `0.025px/minute` scale now drives all seven bar heights and all nine ribbon thicknesses. The 12,000-minute intake splits into `5,200`, `4,000` and `2,800`; the same flow conserves to `9,400` passed, `1,600` failed and `1,000` flaked. Incoming/outgoing intervals tile each applicable node edge from exact top to exact bottom without gap or overlap. Each title and value is measured, centered above its bar and keeps at least 12px clearance; each bar is a raw square-corner rectangle with no `rx`. Static QA covers scale, totals, interval tiling, label bbox and serializer shape; Chrome repeats actual SVG geometry checks at three viewports. All 26 non-target anchor HTML/SVG files are byte-identical to review-12.

Review-14 resolves D-072 for diagram 14. `Monthly budget`, `Unit tests` and `Passed` now share exact `top-y=210px`, with measured spread `0.00px`. The source bar moves from y=250 to y=210 and its three source intervals move from `250/380/480` to `210/340/440`; target intervals and all D-071 values/thicknesses remain unchanged. Static QA adds an exact alignment assertion, Chrome verifies actual bar bboxes at three viewports, and canonical raster inspection confirms one visual top edge. All 26 non-target anchor HTML/SVG files are byte-identical to review-13.

Review-15 resolves D-073 for diagrams 04, 08 and 09. Pale horizontal rules now delimit rank, experience and hierarchy bands instead of passing through their visual centers. Diagram 04 uses boundaries `40/280/520/760/1000` and centers `160/400/640/880`; diagram 08 uses `204/384/564/744` and `294/474/654`; diagram 09 uses `60/300/540/780` and `180/420/660`. Every card/icon publishes a band binding; static center error is at most `0.01px`, browser center error at most `0.75px`, minimum separator clearances are `22/27/58px`, and no separator intersects a member. Diagram 04 retains both continuous hops while routing its lower corridors above/below the rank boundary. All 22 non-target anchor HTML/SVG files are byte-identical to review-14.

Review-16 resolves D-074 for diagram 13. The vertical axis no longer serializes the `marker-end` that produced a downward arrowhead at the shared origin; both horizontal and vertical axes now publish explicit `data-origin-arrowhead="none"` bindings and contain no marker attribute. Chrome confirms computed `markerStart`, `markerMid` and `markerEnd` are all `none`. The origin, zero/tick labels, scales, grid, bubbles, direct labels, recommendation styling, legend and accessible table remain unchanged. Exactly the diagram 13 HTML/SVG pair differs from review-15; all 26 non-target anchor files are byte-identical.

D-075 records owner visual approval for the exact review-16 manifest: Tran Ngoc Thien confirmed that all fourteen diagrams meet the required visual standard. This closes only the owner-review condition. Masked recognition, five-second takeaway and independent visual-craft remain explicitly pending and are not inferred from owner approval.

Review-17 resolves D-076 for diagrams 09 and 14. Diagram 09 adds visible structural counts to the three hierarchy bands and root metadata without moving any node or connector. Diagram 14 preserves every review-16 bar/ribbon path, value, thickness, scale and conservation binding while increasing focal contrast only for `unit-flaked` and adding one direct coral exception annotation. Static `366/366`, browser `42/42`, canonical raster `14/14`, deterministic regeneration, full regression `148/148`, review-16 archive integrity `75/75`, current manifest integrity `75/75` and 24-file non-target byte identity all pass. The independent masked checkpoint then achieved recognition/five-second `14/14`; after reveal, visual-craft scored `93/100` with no dimension below `4/5` and aggregate `PASS`.

D-077 records Tran Ngoc Thien's explicit approval of the exact review-17 manifest, `G-03@1.5.0 PASS` and permission to close P-18. The same instruction explicitly withholds P-19 implementation authority; no P-19, runtime, package, `dist`, publication, Git or release change follows from this closure.

Review-01 through review-09 remain preserved byte-bound in their corresponding `evidence/p18/r6/history/review-XX/` archives with the exact hashes recorded in the current manifest lineage.

Review-10 remains preserved byte-bound at `evidence/p18/r6/history/review-10/`, exact manifest SHA-256 `9a1fe7282db733c8239a0daf4abddff984c2372bfb6bb82f759de94980adaf84`. Review-11 remains preserved byte-bound at `evidence/p18/r6/history/review-11/`, exact manifest SHA-256 `69b93b45fc852b9e9c1405b66fbb40dd10d964fa55f589b65a51984d5b3dccfc`. Review-12 remains preserved byte-bound at `evidence/p18/r6/history/review-12/`, exact manifest SHA-256 `90de78337c49f1ee42aae8730bbf072eb8bf679388038041b793f943ddfcafb6`. Review-13 remains preserved byte-bound at `evidence/p18/r6/history/review-13/`, exact manifest SHA-256 `520c4ad74b944a218a576bdec7f100eb84054e712a066965417961fe97b91324`. Review-14 remains preserved byte-bound at `evidence/p18/r6/history/review-14/`, exact manifest SHA-256 `9e88febc31f895aaada5385f2b9fc3a3384b8ff607831ac4ad9e302165b36637`. Review-15 remains preserved byte-bound at `evidence/p18/r6/history/review-15/`, exact manifest SHA-256 `0e2fcddc00a5b993fd34b4376c32e10a1ca0dd64013202e58ac35df801798a5b`. Review-16 is preserved byte-bound at `evidence/p18/r6/history/review-16/`, exact manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`. Review-17 records all sixteen historical lineages and supersedes review-16 only as the current exact candidate.

## Review entry points

- Labeled HTML gallery: `evidence/p18/r6/index.html`
- Masked HTML review: `evidence/p18/r6/blind-review.html`
- Labeled contact sheet: `evidence/p18/r6/review/contact-sheet-labeled.png`
- Masked contact sheet: `evidence/p18/r6/review/contact-sheet-masked.png`
- Exact inventory: `evidence/p18/r6/P-18R6-INVENTORY.json`
- Design contract: `evidence/p18/r6/P-18R6-DESIGN-CONTRACT.md`
- Visual review record: `evidence/p18/r6/P-18R6-VISUAL-REVIEW.md`
- Verification: `evidence/p18/r6/P-18R6-VERIFICATION.json`
- Build receipt: `evidence/p18/r6/P-18R6-BUILD-RECEIPT.json`
- Frozen manifest: `evidence/p18/r6/P-18R6-MANIFEST.json`
- Independent review record: `evidence/p18/P-18R6-REVIEW-17-INDEPENDENT-REVIEW.md`
- Historical review-01 archive: `evidence/p18/r6/history/review-01/`
- Historical review-02 archive: `evidence/p18/r6/history/review-02/`
- Historical review-03 archive: `evidence/p18/r6/history/review-03/`
- Historical review-04 archive: `evidence/p18/r6/history/review-04/`
- Historical review-05 archive: `evidence/p18/r6/history/review-05/`
- Historical review-06 archive: `evidence/p18/r6/history/review-06/`
- Historical review-07 archive: `evidence/p18/r6/history/review-07/`
- Historical review-08 archive: `evidence/p18/r6/history/review-08/`
- Historical review-09 archive: `evidence/p18/r6/history/review-09/`
- Historical review-10 archive: `evidence/p18/r6/history/review-10/`
- Historical review-11 archive: `evidence/p18/r6/history/review-11/`
- Historical review-12 archive: `evidence/p18/r6/history/review-12/`
- Historical review-13 archive: `evidence/p18/r6/history/review-13/`
- Historical review-14 archive: `evidence/p18/r6/history/review-14/`
- Historical review-15 archive: `evidence/p18/r6/history/review-15/`
- Historical review-16 archive: `evidence/p18/r6/history/review-16/`
- Static QA detail: `evidence/p18/r6/review/static-verification.json`
- Quick Look raster receipt: `evidence/p18/r6/review/quicklook-verification.json`
- Reproducible browser QA: `evidence/p18/r6/source/p18r6_browser_qa.js`

## Stop condition

P-18R6 review-17 is owner-approved; P-18 is `passed`; `G-03@1.5.0` is `PASS`. P-19A/B/C remain `not-started` and unauthorized until a separate owner instruction grants implementation authority.
