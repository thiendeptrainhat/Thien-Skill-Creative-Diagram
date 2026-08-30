# P-18 pilot gallery contract candidate

**Contract ID:** `P18-PILOT-1.5.0-CANDIDATE`  
**Prepared in:** P-16 only  
**Execution status:** not authorized; no HTML or gallery may be created in P-16  
**Approval required:** owner approval of this exact case set/rubric at `G-02@1.5.0`, then separate P-17/P-18 authorization and later owner visual approval of exact rendered manifest

## 1. Fixed output matrix

The pilot contains exactly 12 case families below. Each family must later produce one standalone self-contained HTML for each `neutral-light`, `neutral-dark` and `editorial`: `12 × 3 = 36` specimens. `index.html`/contact sheet is additional and excluded from the specimen count.

All cases use `motion=none`; HTML must contain a complete inline SVG, accessible name/description and exact data representation. All quantitative comparisons use `PRODUCT-ARCHITECTURE-TEST-DELTA.md` §4.1 without local reinterpretation. No required network resource, build step, local absolute path or copied upstream expression is permitted.

## 2. Exact case set

| Case ID | Type/capability | Original fixed input semantics | Mandatory assertions |
|---|---|---|---|
| `P18-C01-ARCH` | Architecture / `CAP-T01` | Vietnamese “Phê duyệt hồ sơ số”: zones `Công khai`, `Ứng dụng`, `Dữ liệu`, `Kiểm toán`; components `Người nộp`, `Cổng API`, `Dịch vụ định danh`, `Dịch vụ phê duyệt`, `Kho hồ sơ`, `Nhật ký bất biến`, `Dịch vụ thông báo`; directed relations Người nộp→Cổng API→Dịch vụ phê duyệt, Dịch vụ phê duyệt↔Dịch vụ định danh, Dịch vụ phê duyệt→Kho hồ sơ, Dịch vụ phê duyệt→Nhật ký, Dịch vụ phê duyệt→Dịch vụ thông báo. | Exact zones/endpoints/directions; trust-boundary crossings visible; no bypass edge invented; connector-heavy geometry; Vietnamese diacritics and read order exact. |
| `P18-C02-SWIM` | Swimlane / `CAP-T08` | Must-pass QA reference `REF-SWIMLANE-CASH-RECEIPTS-001` R2, SHA-256 `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113`. Semantic actors: Khách hàng, Phòng thư, Thu tiền, Phải thu, Sổ cái, Ngân hàng; grouped owners Thủ quỹ and Kế toán trưởng; artifacts séc, giấy báo chuyển tiền, bảng kê chuyển tiền, tệp phải thu, tệp sổ cái; handoff labels `(1)..(5)`. | Preserve actors/groups/artifact kinds/handoffs independently; do not trace reference pixels or reuse existing golden geometry; connectors do not cross unrelated nodes; legend and Vietnamese text remain exact. |
| `P18-C03-SANKEY` | Sankey / `CAP-T30` | Municipal water flow, unit `ML/day`: Intake→Pretreatment 92; Intake→Reject 8; Pretreatment→Filtration 88; Pretreatment→Washwater 4; Filtration→Distribution 84; Filtration→Sludge 4. | Intake total 100; conservation at Pretreatment 92=88+4 and Filtration 88=84+4 within `E`; all amounts/unit in accessible ledger; band-width ratio error ≤1% or absolute error ≤0.5 CSS px; no negative, missing or invented flow. |
| `P18-C04-TREEMAP` | Treemap / `CAP-T29` | Annual community grant allocation, total 100 units: Community 40 = Literacy 15 + Digital access 10 + Outreach 15; Environment 35 = Wetlands 20 + Urban trees 15; Mobility 25 = Walking paths 10 + Accessible stops 15. Every leaf binds to its named parent; each group stores the stated `declared_total` and unit. | Leaf/parent/total sums reconcile within `E`; leaf area-ratio error ≤2%; all hierarchy labels/values/units present in accessible data; zero silent remainder and no missing/negative leaf. |
| `P18-C05-WARDLEY` | Wardley map / `CAP-T32` | Public permit service coordinates `(evolution,value-chain)`: Resident portal `(0.35,0.95)`, Application processing `(0.45,0.75)`, Case workflow `(0.55,0.55)`, Identity `(0.70,0.40)`, Hosting `(0.82,0.20)`; dependencies Portal→Processing→Workflow, Workflow→Identity, Workflow→Hosting. | Coordinates within 0..1 and plotted on declared axes; exact endpoints/directions; label/point association; no strategic movement recommendation invented. |
| `P18-C06-DEPLOY` | Deployment / `CAP-T35` | Three zones: Edge has `gateway-a` running `api-gateway` replicas 2 port 443; App has `app-a` running `approval-service` replicas 3 port 8443 and `worker-a` running `document-worker` replicas 2; Data has `db-a` running `postgres` replicas 1 port 5432 and `store-a` running `object-store` replicas 2 port 9000. Runtime edges Gateway→Approval, Approval→Postgres, Approval→Object-store, Approval→Worker, Worker→Object-store. | Exact containment, replicas, ports and runtime endpoints; cross-zone boundaries visible; architecture abstraction cannot replace physical placement. |
| `P18-C07-JOURNEY` | User journey / `CAP-T34` | First-time public-library membership: Discover/action read eligibility/touchpoint website/sentiment `-0.1`; Prepare/gather ID/checklist/`0.2`; Apply/submit form/portal/`-0.4`; Verify/respond to question/email/`0.3`; Activate/receive card/app/`0.8`. Sentiment scale fixed `-1..1`. | Stage/action/touchpoint order exact; sentiment scale/values disclosed and non-color encoded; factual narrative remains readable without curve/color. |
| `P18-C08-FISH` | Fishbone / `CAP-T31` | Effect `Báo cáo mẫu xét nghiệm trễ`; cause groups: People=`Thiếu người ca tối`,`Bàn giao không rõ`; Process=`Ưu tiên mẫu chưa thống nhất`,`Duyệt hai lần`; Equipment=`Máy quét tem gián đoạn`,`Máy ly tâm chờ bảo trì`; Data=`Mã mẫu trùng`,`Thời gian nhận thiếu`; Environment=`Quãng đường chuyển mẫu dài`,`Nhiệt độ kho không ổn định`. | Exactly one effect; ten causes retain group membership and converge toward effect; no cause omitted; text states this is a cause-analysis hypothesis, not proven causation. |
| `P18-V17-DUMBBELL` | Dumbbell / `CAP-V17` parent Bar | Median response time, minutes, states Before/After: North `18/12`, Central `25/17`, South `20/15`, Remote `30/22`. | Exactly two values/category on shared zero-based domain; gaps `-6,-8,-5,-8`; endpoint error ≤0.5 CSS px and gap-ratio error ≤1% or absolute ≤0.5 CSS px; endpoint values/unit visible; no direction reversal or radius encoding. |
| `P18-V18-SLOPE` | Slopegraph / `CAP-V18` parent Line | Median processing days, Q1/Q2: Permits `9.2/7.4`, Records `5.8/6.1`, Grants `12.5/9.8`. | Exactly two states/series; shared day scale; endpoint error ≤0.5 CSS px; direction and rank exact; Records increase is not styled as improvement; crossings/ties preserved if present. |
| `P18-V19-RIDGE` | Ridgeline / `CAP-V19` parent Line | Call handling duration, minutes, shared domain `0..12`: Team A samples `[3,4,4,5,6,7]`; Team B `[4,5,6,6,7,8]`; Team C `[2,3,5,7,9,11]`. Transformation is histogram with common ordered edges `[0,2,4,6,8,10,12]`, `bin_count=6`, `bandwidth=null`, `shared_domain=true`, `shared_bins=true`, `amplitude_normalization=global-max`; bins follow the exact §4.1 boundary rule. | Six samples/series retained; bin counts/densities and global-max normalization recompute exactly; peak/amplitude ratio error ≤1% or absolute ≤0.5 CSS px; distribution height cannot imply different sample count; exact samples and transformation metadata supplied as accessible data. |
| `P18-V20-BUBBLE` | Bubble / `CAP-V20` parent Scatter | Project portfolio `(impact,effort,budget_M)`: Accessibility `(9,4,2.4)`, Search `(7,5,1.6)`, Migration `(8,9,5.2)`, Notifications `(5,3,0.9)`; x/y domains `0..10`. | Four observations; x/y coordinate error ≤0.5 CSS px; **bubble area-ratio error ≤2%** against budget; size unit/legend exact; no overlap hides a point; accessible table exposes all three values. |

No case is derived from an upstream gallery scenario. The swimlane reference is a project-owned, owner-authorized QA-only benchmark and remains excluded from packages.

## 3. Inherited exact rubric

The scoring contract is inherited without amendment from `evidence/p02/BENCHMARK-MANIFEST.md`, SHA-256 `333afc1b66c238e41276274dfc4317a1b1d472e27b0a9be0bdfd38073cbebc0b`:

| Dimension | Weight |
|---|---:|
| Semantic correctness | 30 |
| Security and fidelity | 20 |
| Quantitative/temporal integrity | 15 |
| Geometry and legibility | 15 |
| Accessibility | 10 |
| Visual communication | 10 |

Pass requires at least 90/100 overall, at least 80% of every applicable dimension and zero hard failure. For a non-quantitative case, the approved rubric reallocates the quantitative weight to semantics. Hard failures include wrong type/relation, invention or silent loss, executed input/external request, quantitative distortion, clipping/overlap/wrong endpoint/unreadable text, inaccessible critical meaning, copied/traced expression, hidden dependency or undisclosed fallback.

## 4. Originality and visual-quality review

The intended quality outcome is polished editorial clarity comparable in professionalism to the user's reference repository, assessed by this rubric and owner judgment—not by pixel, template or style similarity. Each specimen must have:

- original tokens, composition, shape grammar, connector treatment, typography hierarchy, example prose and SVG/CSS;
- a provenance receipt naming its case ID, source fixture hash, generator/source hash and confirmation that no upstream gallery/code/template was used;
- semantic, quantitative, geometry, accessibility, security and standalone-file checks;
- a visible type/variant/mode label outside the data-bearing diagram without adding brand identity to the diagram itself.

## 5. Owner workflow and freeze rule

1. Owner first approves or changes this candidate at G-02; absent approval, P-18 cannot use it.
2. After separate P-17/P-18 authorization, implementation creates the 36 HTML files and index/contact sheet under `evidence/p18/` only.
3. QA freezes an exact pilot manifest containing every case/mode path, SHA-256, source hash and check result.
4. Owner reviews the contact sheet and representative standalone files and approves the exact manifest or requests revision.
5. P-19 cannot start until that exact owner visual approval is recorded. Updating any approved specimen byte invalidates the approval for the affected manifest.

P-16 performs step 1 preparation only and produces no gallery artifact.
