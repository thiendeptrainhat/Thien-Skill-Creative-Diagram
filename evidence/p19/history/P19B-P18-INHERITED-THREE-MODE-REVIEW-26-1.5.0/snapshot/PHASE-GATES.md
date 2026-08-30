# Phase gates — Thien-Skill-Creative-Diagram

File này là nguồn sự thật duy nhất cho tiêu chí `PASS / FAIL / DEFERRED` của milestone và phát hành. Dependency, authorization, exit criteria và trạng thái của từng phase nằm trong `PLAN.md`.

Gate assertion là cách kiểm chứng tối thiểu cho các quyết định trong `PROJECT-CONTRACT.md`, không phải nguồn yêu cầu sản phẩm thay thế. Các nhóm chính truy về D-004–D-009 (nguồn/phạm vi/sản phẩm), D-010–D-012 (package), D-013–D-018 và D-021 (brand/legal), D-019–D-020 (benchmark), D-041–D-050 (target v1.5.0/source-gallery/P-18) và D-051–D-103 (owner rejection, typography/visual-foundation relock, authorization/remediation P-18R4/P-18R5/P-18R6/P-19A/P-19B, exact owner approvals và G-03@1.5.0 closure).

## 1. Quy tắc chung

- Trạng thái gate chỉ có `NOT-EVALUATED`, `PASS`, `FAIL` hoặc `DEFERRED`. `NOT-EVALUATED` chỉ nghĩa là gate chưa được xét và không cho phép vượt gate.
- Gate instance là version-scoped, ví dụ `G-01@1.0.0` và `G-01@1.5.0`. Historical `PASS` của một version không tự thỏa gate cho version khác.
- D-058 chỉ đóng P-18R5 và phê duyệt exact Swimlane anchor/visual direction của subphase này; `G-03@1.5.0` vẫn `NOT-EVALUATED` cho đến khi có P-18R6 candidate theo contract và quyết định gate riêng của chủ sở hữu.
- D-059 authorize riêng P-18R6 để tạo đúng 14 anchor `neutral-light` và bằng chứng review; file/score nội bộ không tự làm P-18 `passed` hoặc `G-03@1.5.0` `PASS` trước owner approval của exact manifest.
- D-060 authorize remediation review-02 trong đúng P-18R6; review-01 phải giữ byte-bound historical, và năm geometry assertion mới phải được test trước owner review.
- D-061 authorize dependency-diagram remediation review-03 trong đúng P-18R6; review-02 phải giữ byte-bound historical, crossing/hop, balanced rank/corridor geometry và single chart-level corner style phải được test trước owner review.
- D-062 authorize containment/centering remediation review-04 trong đúng P-18R6; review-03 phải giữ byte-bound historical, diagram 01–03 phải có machine-checked parent/child containment + group centering, và diagram 01–04 phải chứng minh một whole-chart rounded/straight policy với explicit user choice precedence.
- D-063 authorize continuous-pyramid remediation review-05 riêng diagram 10 trong đúng P-18R6; review-04 phải giữ byte-bound historical, apex phải là true triangle, supporting layers phải tile cùng outer triangle bằng exact shared boundaries và toàn stack phải có machine-checked clearance với left leverage axis.
- D-064 authorize apex-text/annotation remediation review-06 riêng diagram 10 trong đúng P-18R6; review-05 phải giữ byte-bound historical, mọi layer text bbox phải nằm trong owning polygon với inset tối thiểu 8px, và right-side annotation rail phải có semantic cadence + geometry clearance binding.
- D-065 authorize equal-annotation-gap remediation review-07 riêng diagram 10 trong đúng P-18R6; review-06 phải giữ byte-bound historical, cả bốn note phải tính x từ cùng outer-triangle geometry với shared target 72px và automated tolerance tối đa 0.01px.
- D-066 authorize review-08 remediation riêng diagram 06/11 trong đúng P-18R6; review-07 phải giữ byte-bound historical, diagram 06 phải có sáu major phase cho sáu workflow step mà không sửa exact R5 parent, còn diagram 11 phải machine-check center alignment, endpoint, bottom padding và relationship-label corridor clearance.
- D-067 authorize review-09 remediation riêng diagram 12 trong đúng P-18R6; review-08 phải giữ byte-bound historical, bốn axis-direction annotation phải có đúng text/mũi tên/vị trí theo trục, measured alignment/clearance metadata và automated QA, trong khi scenario, dữ liệu, quadrant titles và focal item giữ nguyên.
- D-068 authorize review-10 remediation riêng diagram 12 trong đúng P-18R6; review-09 phải giữ byte-bound historical, focal region phải giữ coral fill nhưng không có stroke dưới bất kỳ dạng nào, còn trục, annotation, quadrant titles, sáu initiative, focal point và legend phải giữ nguyên.
- D-069 authorize review-11 remediation riêng diagram 11 trong đúng P-18R6; review-10 phải archive byte-bound trước mutation, `1`/`N` phải tách theo endpoint, tên quan hệ phải độc lập và ưu tiên above/right placement với measured clearance tối thiểu 8px.
- D-070 authorize review-12 remediation riêng diagram 11 trong đúng P-18R6; review-11 phải archive byte-bound trước mutation, `1`/`N` phải nằm đúng trên connector axis với measured canvas knockout, semantic line continuity và deterministic paint order, trong khi relationship-name placement và toàn bộ D-066 geometry phải giữ nguyên.
- D-071 authorize review-13 remediation riêng diagram 14 trong đúng P-18R6; review-12 phải archive byte-bound trước mutation, Sankey phải dùng shared value scale, 100% contiguous ribbon occupancy trên mọi applicable bar interface, label stack căn giữa phía trên với measured clearance tối thiểu 12px và square-corner bars không `rx`, trong khi scenario/value/palette/legend/semantic facts cùng 13 non-target anchor pair giữ nguyên.
- D-072 authorize review-14 remediation riêng diagram 14 trong đúng P-18R6; review-13 phải archive byte-bound trước mutation, ba upper-row bar phải cùng exact `top-y=210px` với max spread `0.01px`, source bar/ribbon intervals phải dịch đồng bộ, toàn bộ D-071 contract cùng 13 non-target anchor pair phải giữ nguyên.
- D-073 authorize review-15 remediation riêng diagrams 04/08/09 trong đúng P-18R6; review-14 phải archive byte-bound trước mutation, pale separators phải là semantic band boundaries, mọi card/icon phải căn giữa band, không separator nào giao/đè member, static/browser center tolerance lần lượt `0.01/0.75px`, canonical minimum clearance lần lượt `22/27/58px`, và 11 non-target anchor pair phải giữ nguyên review-14 ở mức byte.
- D-074 authorize review-16 remediation riêng diagram 13 trong đúng P-18R6; review-15 phải archive byte-bound trước mutation, cả hai quantitative axis phải là plain axis không marker ở serialized/computed output, origin/ticks/scales/grid/bubbles/direct labels/focal/legend/accessible data phải giữ nguyên, và 13 non-target anchor pair phải giữ nguyên review-15 ở mức byte.
- D-075 khóa owner visual approval `PASS` cho toàn bộ 14 diagram của exact review-16 manifest `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`; approval này không thay thế masked blind, five-second hoặc independent visual-craft gate và không tự làm G-03@1.5.0 `PASS`.
- D-076 cho phép sửa đúng two five-second findings của review-16 để tạo review-17: hierarchy phải hiển thị trực tiếp `1 / 4 / 5`, Sankey phải làm nổi focal rerun và ghi trực tiếp `1,000 / 12,000 · 8.3%`; review-16 phải archive byte-bound, 12 non-target pair phải byte-identical và exact review-17 phải qua masked→reveal independent review. Exact review-17 đã đạt independent aggregate `PASS`, nhưng owner approval review-17 và `G-03@1.5.0` vẫn cần quyết định riêng.
- D-077 phê duyệt exact review-17, đặt `G-03@1.5.0 PASS` và đóng P-18 `passed`. Quyết định này đồng thời giữ P-19 `not-started`/unauthorized; gate pass không tự authorize phase kế tiếp.
- D-078 là authorization riêng sau D-077 cho đúng P-19A. P-19A phải map đúng 39 canonical type + bốn capability vào exact 14 engine, có unique non-generic silhouette và deterministic engine-specific plan, giữ fail-closed trước render và không emit HTML/SVG/ba mode/gallery. P-19A `passed` không tự làm `G-04@1.5.0 PASS` và không authorize P-19B/P-19C.
- D-079 là authorization riêng cho P-19B. P-19B phải derive đúng ba mode trên exact P-19A adapter, tạo đúng 117 canonical + 12 capability standalone HTML cùng index/contact sheet, giữ scriptless/network-independent/machine-readable/named-SVG/alternative-table contract và focused static/browser evidence. P-19B `passed` không tự làm `G-04@1.5.0 PASS` và không authorize P-19C.
- D-080 supersede exact P-19B initial candidate cho mọi owner-approval/golden purpose sau khi owner xác định candidate không kế thừa đủ phong cách P-18. Remediation candidate phải byte-preserve archive ban đầu; bind trực tiếp exact P-18R6 review-17 candidate/manifest; neutral-light giữ warm-paper/coral/type/spacing/shape/connector grammar đã duyệt; neutral-dark/editorial chỉ đổi semantic tokens, không đổi geometry/IR; tự động fail nếu xuất hiện legacy blue-accent visual direction, thiếu lineage metadata hoặc khác geometry giữa ba mode. P-19B chỉ có thể trở lại `passed` sau technical verification và owner approval của exact candidate kế nhiệm; D-080 không authorize P-19C.
- D-081 giới hạn review-02 trong P-19B ở dp-integration containment/centering và swimlane continuous-path. Phải archive exact review-01 trước mutation; test serialized child bounds/center, một path liền mạch với rounded/straight corner và absence of erase overlay; chứng minh invariance qua ba mode, không đổi semantics/artwork ngoài hai target. Không tự mang forward visual PASS cũ, không tự duyệt owner/P-19C/G-04.
- D-082 yêu cầu review-03 chứng minh Gantt-only mutation: 3 phase/6 task/1 gate minh họa, shared timestamp scale với tháng đúng độ dài, exact dates/timezone và phase containment, ba mode cùng geometry. Archive review-02, không đổi P-18/P-19A và artwork ngoài Gantt. Local raster không thay thế browser/full P-19C hoặc owner approval.
- D-083 yêu cầu review-04 chứng minh flywheel-only mutation: sáu station đóng vòng đúng edge order, shared-state nằm ngoài cycle, sáu contribution có dữ liệu khai báo, continuous clockwise arcs và inward dashed spokes không xuyên card. Kiểm text/canvas/connector clearance, ba mode cùng geometry, bảo toàn Gantt và non-target artwork, archive exact review-03. Không tự carry forward owner/browser/full P-19C PASS.
- D-084/D-085 thay đổi riêng gallery evidence: giữ nguyên 14 P-18 anchor neutral-light và không tạo P-19 duplicate; kiểm union đúng 39 canonical type, bốn capability không bị loại theo parent, đúng 87 P-19 HTML/29 preview và 14 P-18 references. Withdrawal phải recoverable, 87 retained HTML chỉ đổi candidate metadata, 29 preview byte-identical; tuyệt đối không dùng P-18 light để claim dark/editorial. Các source/semantic/quality gate và owner/P-19C boundaries không đổi.
- D-086 giới hạn review-06 trong P-19B ở Fishbone: archive review-05 trước mutation; dữ liệu minh họa độc lập phải có đúng 5 nhóm, 10 nguyên nhân và 1 hệ quả; năm xương xen kẽ trên/dưới; mọi tick nguyên nhân chạm đúng xương sở hữu, mọi xương chạm trục chính, trục chính kết thúc tại thẻ hệ quả; semantic table chứa mọi node/group ID và ba mode dùng cùng geometry. Chỉ ba Fishbone HTML/preview được đổi artwork; 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-087 giới hạn review-07 trong P-19B ở dp-integration: archive review-06 trước mutation; exact detailed fixture phải có 11 node, 11 directed integration edge và một boundary chứa đúng ba core service. Mọi node/edge/group ID phải serialize; core nằm trong boundary, nguồn/consumer/service band nằm ngoài; mọi route là một continuous subpath với đúng endpoint, ba mode cùng geometry. Chỉ ba dp-integration HTML/preview được đổi artwork; 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-088 giới hạn review-08 trong P-19B ở bar-chart: archive review-07 trước mutation; exact fixture phải có một series/tám ordered sprint datum, hai axis, Y-domain 0–120, sáu tick và một annotation trỏ tới unique maximum Sprint 5. Mọi bar/value/category phải serialize, cùng zero-baseline và không axis arrow; record-high dùng redundant accent/direct-label/legend/table status. Ba mode cùng geometry; chỉ ba bar-chart HTML/preview đổi artwork, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-089 giới hạn review-09 trong P-19B ở dp-security-matrix: archive review-08 trước mutation; exact fixture phải có đủ 25 giao điểm cho 5 vai trò × 5 thành phần, header/group code và row/component code, mọi ô ghi trực tiếp Admin/Write/Read/None, trạng thái allow/deny phù hợp, cùng một partner-BI Read boundary có redundant coral/direct scope/legend/table encoding. Ba mode cùng geometry; chỉ ba dp-security-matrix HTML/preview đổi artwork, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-090 giới hạn review-10 trong P-19B ở er-data-model: archive review-09 trước mutation; exact fixture có 4 entity/19 field/3 quan hệ, đúng 1 aggregate root và 1 associative entity, PK/FK/cardinality được ghi trực tiếp, legend cùng exact alternative table đầy đủ. Ba mode cùng geometry; chỉ ba er-data-model HTML/preview đổi artwork, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-091 giới hạn review-11 trong P-19B ở vị trí sáu cardinality của er-data-model: mỗi `1/N` inline trên connector axis, sát đúng source/target endpoint, có canvas-fill/no-stroke knockout bind riêng theo P-18 với padding 8px dọc đường/4px vuông góc và tối thiểu 8px tới node; không đổi semantic model/path/name/legend/table. Archive review-10; ba mode cùng geometry; 84 non-target HTML giữ artwork và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-092 giới hạn review-12 trong P-19B ở high-level: thay bằng data-platform topology chi tiết nhưng độc lập, kế thừa visual grammar P-18; đúng 11 node/13 directed edge/2 boundary group. Mỗi connector là một orthogonal path liên tục, mọi góc 90° bo tròn mặc định bằng tangent join và chỉ thẳng khi explicit override; không dùng erase overlay. Archive review-11; ba mode cùng geometry; 84 non-target HTML giữ artwork và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-093 giới hạn review-13 trong P-19B ở it-current-state: thay bằng landscape hiện trạng ba miền độc lập, đúng 9 node/8 directed edge/3 boundary, 8 direct format label, 2 bottleneck, 2 pain path và 2 external path. Mọi node có state và nằm trọn trong boundary; connector dùng một continuous orthogonal path, rounded default/straight explicit theo P-18. Archive review-12; ba mode cùng geometry; 84 non-target HTML giữ artwork và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-094 giới hạn review-14 trong P-19B ở Kanban: đúng 4 cột, 11 item phân bố 3/4/2/2, một WIP breach `4/3`, một blocked, một waiting-external và hai done; state phải encode dư thừa bằng stroke/fill/rail/legend chữ, không chỉ màu. Giới hạn vận hành vượt mức dùng annotation target cột để giữ nguyên P-17 grammar frozen. Archive review-13; ba mode cùng geometry; 84 non-target HTML giữ artwork và 28 preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-095 giới hạn review-15 trong P-19B ở việc thêm presentation variant `layers` dưới parent `layer-stack`: đúng 5 dải L5→L1, một abstraction axis, một focal layer có non-color label/note, đủ bảng thay thế và ba mode cùng geometry. Archive review-14; 87 prior HTML giữ artwork, 29 prior preview byte-identical; thêm đúng 3 HTML + 1 preview để gallery có 90 HTML/30 preview và comparison có 104 diagram. P-17/P-19A frozen; không tự duyệt owner/P-19C/G-04.
- D-096 giới hạn review-16 trong P-19B ở `line-chart`: đúng 3 series × 8 tuần = 24 điểm, x ordinal, y linear 0–240 với 6 tick, plain arrow-free axes, một coral/circle/area focal series và hai comparison series có distinct dash+marker, direct endpoint labels, legend và exact 24-value table. Archive review-15; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical; ba mode cùng geometry. Không tự duyệt owner/P-19C/G-04.
- D-097 giới hạn review-17 trong P-19B ở `medallion`: đúng 5 ordered stage, 4 continuous directed promotion arc và 2 processing-path callout; mỗi stage có technical name/tool/format/writer/two examples; đúng một focal stage và một archive stage có direct tag/boundary non-color redundancy; exact five-row table và ba mode cùng geometry. Archive review-16; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-098 giới hạn review-18 trong P-19B ở `polar-chart`: đúng 1 series/8 ordered UTC window/8 common-origin spoke, radial scale 0–100% với ring 20/40/60/80/100, open endpoint marker, direct exact label và một unique maximum có non-color `ĐỈNH` redundancy; plain arrow-free spokes, không filled wedge, exact eight-row table và ba mode cùng geometry. Archive review-17; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-099 giới hạn review-19 trong P-19B ở `wardley-map`: đúng 8 component/9 dependency/2 normalized axis/4 evolution stage/3 boundary; visibility từ hạ tầng tới nhìn thấy bởi người dùng và evolution từ Khởi nguyên tới Hàng hóa. Axis/dependency không arrowhead; đúng 1 evolving component có coral open-circle + direct state label + dashed evolution arrow. Một exact alternative table chứa đủ 8 component và 9 dependency; ba mode cùng geometry. Archive review-18; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-100 giới hạn review-20 trong P-19B ở `venn`: đúng 3 tập equal-radius/4 member; mỗi tập có một member riêng và cùng chứa duy nhất member trung tâm. Vùng giao ba tập phải được tính chính xác bằng nested clip, có direct title + `ĐIỂM CÂN BẰNG`, không dùng shape ước lượng hoặc color-only encoding; ba tập có direct title/subtitle, exact membership table và ba mode cùng geometry. Archive review-19; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-101 giới hạn review-21 trong P-19B ở `treemap`: đúng 6 leaf/1 parent group, exact total reconciliation và 6 rectangle có area/value share bằng nhau theo tolerance deterministic. Chỉ một focal tile có non-color/direct-label redundancy; chỉ một compact-label tile có `i` marker cùng legend/table disclosure; exact six-row value/unit/share table và ba mode cùng geometry. Archive review-20; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-102 giới hạn review-22 trong P-19B ở paint treatment của `treemap`: giữ nguyên D-101 geometry/value/area/label/legend/table; mỗi tile có một canvas gutter under-stroke và visible outline, năm tile thường dùng connector stroke, tile focal dùng coral stroke. Sáu visible border/sáu gutter phải hiện diện ở cả ba mode. Archive review-21; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-103 giới hạn review-23 trong P-19B ở visible-cell geometry của `treemap`: retire under-stroke, giữ exact allocation-area/value encoding, inset mọi visible tile 4 unit ở đủ bốn cạnh để tạo gap thật 8 unit tại shared boundaries. Sáu tile phải khai báo đủ top/right/bottom/left border và cùng inset/gap ở ba mode. Archive review-22; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-104 giới hạn review-24 trong P-19B ở `uml-class`: đúng 7 container/17 member/5 relationship gồm 1 dependency, 2 realization, 1 composition, 1 association; interface phải có stereotype trực tiếp; composition/association có 4 cardinality inline; mọi semantic connector là một continuous path và association dùng rounded-orthogonal route theo P-18. Legend phải đủ 6 relation kind bằng marker/line semantics. Archive review-23; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- D-105 giới hạn review-25 trong P-19B ở global connector policy: một connector trên một cạnh phải ở midpoint; nhiều connector trên cùng cạnh phải dùng `i/(n+1)`; straight route là ưu tiên, orthogonal chỉ khi cần tránh va chạm/ambiguity, mặc định rounded và phải serialize exception reason. Đủ 90 SVG P-19 phải khai báo policy; UML proof phải có exact single-center, equal `360/360/360` multi-port intervals, 4 straight relation và 1 documented rounded-orthogonal exception. Archive review-24; giữ non-target artwork sau policy normalization. Không tự duyệt owner/P-19C/G-04.
- D-106 giới hạn review-26 trong P-19B ở `tree`: đúng 9 node/8 parent relation/3 tầng với 1 root, 3 branch, 5 leaf; root và mọi parent phải nằm đúng midpoint span child, sibling branch có khoảng cách đều, two-child groups có offset đối xứng và single-child dùng direct centered line. Multi-child fanout phải theo P-18 org-chart bằng centered trunk + shared bus + centered drops; không arrowhead, không curve, mọi attachment ở edge center. Ba mode cùng geometry. Archive review-25; chỉ 3 target HTML + 1 preview đổi artwork, 87 non-target HTML giữ artwork sau candidate normalization và 29 non-target preview byte-identical. Không tự duyệt owner/P-19C/G-04.
- `PASS` cần evidence có version/hash hoặc đường dẫn kiểm chứng được.
- `DEFERRED` không tương đương `PASS` và không cho phép vượt critical gate.
- Hard failure về security, semantic, numeric integrity, accessibility nghiêm trọng, provenance, package install hoặc pháp lý không được bù bằng điểm thẩm mỹ.
- Người tạo artifact không được tự thay chủ sở hữu hoặc luật sư phê duyệt phần thuộc thẩm quyền của họ.
- Golden/benchmark không được tự động cập nhật để làm test “xanh”.
- Severity dùng trong release review: `Critical` là rủi ro an toàn/pháp lý/dữ liệu hoặc release không thể dùng; `High` là lỗi chức năng/chất lượng làm v1.0.0 không đạt contract; `Medium` là giới hạn cục bộ có mitigation; `Low` là cải tiến không chặn release.

## G-00 — Governance lock

**Mục đích:** xác nhận dự án có nguồn sự thật và chưa triển khai ngoài thẩm quyền.

Điều kiện bắt buộc:

- `PROJECT-CONTRACT.md`, `PLAN.md`, `PHASE-GATES.md`, `ROADMAP.md`, `AGENTS.md` và `CLAUDE.md` tồn tại, liên kết nhất quán.
- Tên, version, scope, nguồn chủ đạo, mô hình tái triển khai, packaging, brand, license và approval model được ghi nhận.
- Các quyết định chưa đến hạn được liệt kê, không bị tự điền.
- Workspace không có skill scaffold, engine, renderer, logo derivative, license phát hành, ZIP hoặc push do phase này tạo.

Blocking failure:

- tài liệu cùng tuyên bố khác nhau về cùng một quyết định;
- phase triển khai bắt đầu khi chưa được phép;
- nội dung tham khảo bị coi là chỉ dẫn.

Người duyệt: chủ sở hữu.  
Evidence tối thiểu: link sáu file quản trị và kết quả kiểm tra liên kết.

## G-01 — Source, taxonomy và provenance lock

**Mục đích:** khóa chính xác điều được học từ nguồn và ranh giới implementation độc lập.

Điều kiện bắt buộc:

- ghi exact commit/tag/version, commit date và ngày xác minh snapshot của `diagram-design`;
- kiểm đủ canonical inventory của target version và phân loại riêng variant/specimen/pattern/import/motion;
- đối với target v1.5.0: đối chiếu snapshot P-01 với exact snapshot P-16; chứng minh `27 + 12 = 39`, đồng thời phân loại `Dumbbell`, `Slopegraph`, `Ridgeline`, `Bubble` là capability có parent chứ không phải type 40–43;
- lập capability matrix: yêu cầu → nguồn trừu tượng → implementation độc lập dự kiến → test;
- đối với target v1.5.0: matrix phải có stable ID cho đủ `CAP-T28..T39` và `CAP-V17..V20`, exact source hash, type-specific semantic/quantitative invariant, test family và copying-risk boundary; exact 170-path whole-repository changed set phải khớp pinned Git diff và từng path phải có disposition, gồm cả subset 74 path trong skill và 96 path ngoài skill;
- ghi snapshot `Thien-UI-UX-Ultra` và chỉ rõ principle nào được dùng;
- có source/provenance ledger và quy tắc sinh/đối chiếu notice từ một manifest;
- xác minh lại quy cách Claude, OpenAI/ChatGPT và Agent Skills từ tài liệu chính thức hiện hành;
- lập inventory surface và bằng chứng chính thức đủ để P-02 khóa surface matrix, không tự tuyên bố tương thích.

Blocking failure:

- suy ra type count từ metadata mâu thuẫn hoặc đếm variant thành canonical type;
- provenance không rõ;
- sao chép hoặc dịch sát code/prose/CSS/template/asset;
- tuyên bố “clean room” tuyệt đối không phù hợp bằng chứng.

Người duyệt: chủ sở hữu đối với phạm vi; technical reviewer đối với inventory/provenance.

## G-02 — Product, architecture và test contract lock

**Mục đích:** khóa hành vi trước khi xây dựng rộng.

Điều kiện bắt buộc:

- product contract xác định input, output, dials, error/fallback và out-of-scope;
- design contract xác định hierarchy, grid, spacing, typography, color, connector, complexity budget, responsive/export và accessibility;
- canonical architecture xác định router, IR, renderer, validator và platform overlay;
- security contract coi mọi input/import là dữ liệu không tin cậy;
- surface matrix xác định từng surface, artifact, install method, trigger, output, fallback và `supported / conditional / unsupported`;
- chủ sở hữu duyệt support status và evidence rule cho cell `conditional`; technical reviewer xác minh chúng dựa trên tài liệu chính thức;
- benchmark manifest E2 được đề xuất với input, expected type, semantic assertions, size/detail/audience/format, hard failure và rubric;
- chủ sở hữu phê duyệt benchmark manifest trước khi biến nó thành golden contract.
- đối với target v1.5.0: gallery contract phải khóa ranh giới QA-only/non-package, ba visual mode, count rule, originality rule, pilot set và owner-review workflow trước khi P-18 nhân rộng visual implementation.
- đối với target v1.5.0: exact byte-bound contract packet phải liệt kê/hash toàn bộ P-02 inheritance và P-16 delta; request/IR candidate phải enumerate 39 type và biểu diễn trực tiếp Sankey `amount/unit`, Bubble `x/y/size`, Treemap parent/declared-total, Ridgeline transformation, Story-map unassigned và physical-index order/uniqueness; numeric/unit/geometry/boundary policy cùng stable positive/boundary/hard test IDs phải được khóa khách quan;
- `G-02@1.5.0` phải được khóa và duyệt hoàn toàn trong P-16; P-17 chỉ triển khai contract đã duyệt và đóng góp evidence cho G-04, không được dùng để hoàn thiện ngược G-02.

Blocking failure:

- bắt đầu nhân rộng canonical inventory của target version khi chưa có semantic/visual/test contract;
- tự cài dependency hoặc giả định capability host;
- benchmark thiếu expected semantics hoặc cho phép tự sáng tác dữ liệu.

Người duyệt: chủ sở hữu đối với benchmark và visual direction; technical reviewer đối với architecture/security.

## G-03 — Pilot và visual golden

**Mục đích:** chứng minh visual direction và renderer pilot có thể tạo output chuyên nghiệp trước khi mở rộng visual implementation ra toàn bộ inventory.

Pilot phải phủ ít nhất:

- một diagram nhiều connector;
- một chart định lượng;
- một grouped swimlane/process/data-flow tiếng Việt theo `REF-SWIMLANE-CASH-RECEIPTS-001`;
- đủ ba static visual mode đã được chủ sở hữu duyệt ở G-02;
- HTML và SVG; PNG khi renderer khả dụng.

Đối với repeat `G-03@1.5.0`, P-18 phải bổ sung:

- exact pilot manifest/hash và gallery index/contact sheet QA-only;
- tám canonical family candidate trong `PLAN.md` cùng cả bốn capability mới, mỗi family đủ ba mode đã khóa, trừ khi owner duyệt một pilot set khác tại G-02@1.5.0;
- scenario/data/prose/layout/CSS/SVG độc lập và provenance receipt; không specimen nào là pixel/template derivative của upstream;
- HTML mở trực tiếp, self-contained, không build step hoặc external resource bắt buộc;
- owner visual approval gắn với exact pilot manifest trước khi P-19 bắt đầu.
- replacement candidate sau D-050 phải đạt toàn bộ visual-craft acceptance trong `evidence/p18/VISUAL-CRAFT-RUBRIC.md`: ≥85/100, không dimension nào dưới 4/5, blind silhouette aggregate ≥10/12 và five-second takeaway/focal-path `PASS`;
- visual-craft gate là bổ sung độc lập, không được bù hoặc thay thế semantic, quantitative, accessibility, geometry, security, standalone và provenance hard checks hiện hữu;
- upstream chỉ được dùng làm chuẩn trừu tượng qua rubric/provenance review; pixel similarity, tracing và tái sử dụng code/CSS/SVG/template/asset là blocking failure.
- replacement freeze sau P-18R3 là historical rejected evidence theo D-051 và không được dùng làm golden/baseline cho candidate kế tiếp;
- visual implementation kế tiếp phải conform exact P-18R4 contract/machine binding: 14 layout engine phủ đúng 39 canonical type + bốn capability, typography được resolve/load/measure trước sizing/layout, node có intrinsic size, artboard fit theo family, connector route theo port/obstacle và không dùng global transform để giả layout;
- explicit user-selected font/profile phải thắng skill default theo role; default direction là Instrument Serif/Geist/Geist Mono theo D-052, nhưng font file không được copy từ upstream và mọi embedding phải có official-source license/provenance;
- P-18R5 phải chứng minh một Swimlane `neutral-light` anchor với node anatomy, top/lane/interface chrome, measured Vietnamese text và rounded orthogonal routing; P-18R6 phải chứng minh một `neutral-light` anchor cho đủ 14 engine trước owner review;
- sau D-055, unavoidable crossing trong P-18R5 phải có exactly one true bridge/hop, không bubble/junction giả hoặc straight chord nằm dưới hop; node phải dùng measured ideal title width và local horizontal budget trước khi wrap, đồng thời tránh orphan line khi còn đủ chỗ;
- sau D-056, hop phải được tích hợp vào connector path geometry; mask/overlay không được dùng để giả việc loại straight chord. Hai hop trên cùng segment phải cách nhau ít nhất tổng hai radius cộng 12px; nếu không đạt, router phải tách corridor trước emit, không render double-hump/compound wave;
- sau D-057, route-integrated hop và repaint phải dùng cùng exact geometry; underlay chỉ được che central crown và không được mở rộng tới hai join. Browser/structural QA phải chứng minh zero shoulder-to-hop gap ở cả ba crossing;
- P-18R6 masked blind engine recognition phải đạt ít nhất 12/14; five-second review không được nhìn thấy intent sentence, family/type legend, file name hoặc evidence rail tiết lộ đáp án;
- P-18R6 review-02 phải chứng minh diagram 01–03 dùng rounded orthogonal routing thay broad Bézier; diagram 04 dùng route-integrated shared-geometry hop với crown-only underlay và zero join gap; diagram 05 có hai nhánh `NO` bằng chiều rộng cùng quay về `Validate evidence`; diagram 07 giữ top labels hoàn toàn phía trên leader/timeline; diagram 09 nối child vào đúng center và ưu tiên straight connector;
- P-18R6 review-03 phải chứng minh riêng diagram 04 không còn crossing giả junction; mọi crossing còn lại có route-integrated hop liên tục; bốn rank có cùng inter-rank gap và corridor ladder cân quanh midpoint; toàn chart khai báo một `connector_corner_style`, mặc định `rounded`, trong khi explicit user override `straight` serialize mọi góc 90° không có `Q`/curve command;
- P-18R6 review-04 phải chứng minh diagram 01–03: mọi direct child node/subcontainer nằm trong parent với minimum padding được khai báo; bounding box của cả cụm child trùng tâm parent trên hai trục; row child cùng center-y, column child cùng center-x và single child trùng center parent; root SVG khai báo chart-level `connector_corner_style`, mặc định `rounded`, còn explicit user override `straight` loại toàn bộ rounded-corner `Q` khỏi các route 90° của diagram 01–03 mà không ảnh hưởng semantics. Diagram 04 tiếp tục giữ cùng option và toàn bộ D-061 hop/corridor assertion;
- P-18R6 review-05 phải chứng minh diagram 10 là một continuous outer triangle: apex là true triangle, ba supporting layer là trapezoid dùng chung side-line và exact horizontal boundary, seam chỉ stroke một lần, còn leverage axis bên trái giữ measured clearance tối thiểu đã khai báo;
- P-18R6 review-06 phải chứng minh cả tám real-font title/metadata bbox của diagram 10 nằm trọn trong owning polygon với minimum inset 8px mà không giảm font-size contract; right-side annotation rail phải gồm đúng apex note và ba cadence note có semantic binding, nằm ngoài polygon, trong canvas và đạt measured clearance tối thiểu đã khai báo;
- P-18R6 review-07 phải tái đo horizontal visual gap từ cạnh phải outer triangle đến bbox-left tại tâm dọc của từng annotation; cả bốn giá trị phải đạt target 72px trong tolerance 0.01px, max-minus-min spread không quá 0.01px, đồng thời mọi assertion D-063/D-064 tiếp tục `PASS`;
- P-18R6 review-08 phải chứng minh diagram 06 có đúng sáu major phase theo thứ tự đã khóa và mapping một-một với sáu workflow step, trong khi exact P-18R5 review-04 vẫn byte-identical; diagram 11 phải đặt ba entity hàng trên cùng center-y, ORDER_ITEM cùng center-x với ORDER, connector terminate đúng boundary/center axis, measured bottom padding tối thiểu 24px và toàn bộ relationship-label bbox nằm trong inter-node corridor với ít nhất 8px clearance khỏi node;
- P-18R6 review-09 phải chứng minh diagram 12 có đúng bốn annotation `↑ HIGH IMPACT`, `← LOW EFFORT`, `↓ LOW IMPACT`, `HIGH EFFORT →`; annotation trên/dưới dùng cùng fixed x-offset bên phải trục dọc, annotation trái/phải dùng cùng fixed y-offset dưới trục ngang và khóa theo hai field edge tương ứng, arrow glyph nằm đúng prefix/suffix và đúng hướng, mọi measured bbox nằm trong canvas với clearance khỏi axis/quadrant content/legend, đồng thời scenario/data/quadrant titles/focal item giữ nguyên review-08;
- P-18R6 review-10 phải chứng minh focal-region rectangle của diagram 12 giữ đúng coral fill nhưng computed/serialized stroke là `none`, không có stroke-width/opacity workaround; mọi D-067 axis annotation và toàn bộ scenario/data/quadrant/focal/legend geometry phải giữ nguyên review-09;
- P-18R6 review-11 phải chứng minh diagram 11 có đúng ba relationship-name label `PLACES`, `PAID BY`, `CONTAINS` và sáu cardinality label độc lập (`1` tại source, `N` tại target); label ngang nằm phía trên line, label dọc nằm bên phải line, bbox không vào node/đè line và đạt tối thiểu 8px clearance, trong khi mọi D-066 center/endpoint/padding geometry và toàn bộ diagram khác giữ nguyên review-10;
- P-18R6 review-12 phải giữ đúng ba relationship-name của review-11 ở vị trí above/right, nhưng đặt cả sáu cardinality `1`/`N` đúng trên trục connector; mỗi glyph phải có một canvas-fill/no-stroke knockout riêng với padding 8px dọc line, 4px vuông góc và node clearance tối thiểu 8px. Connector phải còn đúng một semantic line với paint order connector → knockout → label; static axis error tối đa 0.06px, browser actual-bbox axis error tối đa 0.75px; mọi D-066 geometry và 13 non-target anchor pair giữ nguyên review-11 ở mức byte;
- P-18R6 review-13 phải chứng minh diagram 14 dùng cùng shared scale cho mọi bar/ribbon, mọi applicable incoming/outgoing node interface được các ribbon interval contiguous/non-overlap phủ đúng 100% và hai tổng stage/outcome đều reconcile 12,000 phút; mọi title/value stack căn giữa phía trên bar với measured clearance tối thiểu 12px; mọi bar là square-corner `<rect>` không `rx`; static/browser QA phải kiểm geometry runtime và 13 non-target anchor pair giữ nguyên review-12 ở mức byte;
- P-18R6 review-14 phải chứng minh `Monthly budget`, `Unit tests`, `Passed` cùng exact top edge `y=210px` và static/browser max spread không quá `0.01px`; source bar cùng ba source-side ribbon interval được dịch đồng bộ mà không đổi target interval, scale, value, thickness, conservation, 100% interface tiling, above-bar label, square-corner shape, palette, legend hoặc semantic facts; 13 non-target anchor pair giữ nguyên review-13 ở mức byte;
- P-18R6 review-15 phải chứng minh pale horizontal line của diagram 04/08/09 là band boundary thay vì row centerline; mọi card/icon bbox center-y trùng band midpoint với static tolerance tối đa `0.01px`, browser actual-bbox tolerance tối đa `0.75px`; separator không giao/đè member, canonical clearance tối thiểu lần lượt `22/27/58px`; connector chỉ được cắt separator khi biểu diễn quan hệ cross-band thật và không dùng separator làm route rail gây hiểu nhầm; 11 non-target anchor pair giữ nguyên review-14 ở mức byte;
- P-18R6 review-16 phải chứng minh diagram 13 không còn arrowhead tại shared origin: cả hai axis có explicit no-marker binding và không chứa/computed `marker-start`, `marker-mid`, `marker-end`; origin, zero/tick labels, scales, grid, bubble geometry, direct labels, focal styling, legend và accessible quantitative table giữ nguyên review-15; chỉ diagram 13 HTML/SVG được khác và 13 non-target anchor pair giữ nguyên review-15 ở mức byte;
- P-18R6 review-17 phải chứng minh diagram 09 hiển thị trực tiếp hierarchy/count `1 FRONT DOOR`, `4 DOMAINS`, `5 SPECIALIST PODS`; diagram 14 phải giữ nguyên quantitative geometry nhưng tăng contrast đúng ribbon `unit-flaked` và có direct annotation `FLAKED RERUNS · 1,000 / 12,000 MIN · 8.3% OF BUDGET`; 12 non-target anchor pair giữ nguyên review-16 ở mức byte;
- exact review-17 manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a` đạt masked recognition/five-second `14/14`, independent visual-craft `93/100` với minimum dimension `4/5`, cùng exactness `75/75`; owner phê duyệt exact candidate và `G-03@1.5.0 PASS` theo D-077.
- G-03@1.5.0 closure không tự authorize P-19. D-078 đóng P-19A; D-079 candidate đầu của P-19B đã bị supersede cho owner-approval/golden purpose theo D-080. Active P-19B remediation chưa được owner duyệt; P-19C vẫn cần authorization riêng.

Hard checks cho benchmark swimlane:

- lane/actor và grouped ownership header đúng;
- shape ngữ nghĩa cho tiền/séc, chứng từ, bảng kê và tệp lưu;
- step number/handoff có thể truy vết độc lập;
- connector không xuyên node không liên quan, không sai nguồn–đích;
- legend nhất quán;
- tiếng Việt giữ đúng dấu;
- không clipping, overlap hoặc nén chữ để che complexity;
- font được resolve/load/measure trước layout; mọi material text nằm trong owning node/region với padding đã khai báo, không shrink-to-fit dưới minimum;
- output là thiết kế nguyên bản, không pixel-clone ảnh tham chiếu.

Blocking failure:

- chủ sở hữu chưa duyệt visual direction/golden;
- renderer chỉ đẹp ở một case hard-code;
- semantic sai nhưng được chấp nhận vì hình đẹp.

Người duyệt: chủ sở hữu đối với golden; technical/QA reviewer đối với hard checks.

## G-04 — Functional completeness và quality

**Mục đích:** chứng minh toàn bộ phạm vi của target version hoạt động đáng tin cậy.

### Coverage bắt buộc

- v1.0.0 historical: 27/27 canonical type qua semantic và render checks.
- target v1.5.0: 39/39 canonical type qua semantic/render checks; 12/12 canonical addition và 4/4 capability mới có mapping/test riêng.
- 100% variant/specimen/pattern/import/motion trong inventory P-01 có implementation mapping và ít nhất một contract/smoke test riêng; không capability nào chỉ tồn tại trên giấy.
- Pairwise coverage cho size × detail × audience × format × ngôn ngữ.
- Positive trigger, negative trigger và direct invocation.

Candidate benchmark matrix cho P-12, chỉ có hiệu lực sau khi chủ sở hữu duyệt:

- 27 canonical case và 27 boundary case;
- 7 semantic-pattern case;
- quantitative suite cho Bar, Line, Scatter và Radar;
- normal, multi-page/block, malformed và adversarial import cho draw.io/Mermaid;
- `none`, `reveal`, `step`, `loop`, no-JS, reduced-motion và print/export;
- 27 type × 3 static visual mode đã duyệt = 81 base render, cộng pairwise case thay vì nhân toàn bộ tổ hợp.

Full source/gallery matrix cho P-19, chỉ có hiệu lực sau G-02@1.5.0 và G-03@1.5.0:

- P-19A readiness phải có đúng 39 canonical adapter + bốn capability adapter, map đủ/duy nhất vào 14 engine đã khóa, mỗi adapter có silhouette declaration riêng và không generic/unknown/card fallback; adapter plan chưa phải rendered evidence và không được tính vào 129 HTML;
- Theo D-085: 14 canonical type dùng trực tiếp exact P-18 neutral-light anchor; 25 canonical type còn lại × 3 mode = 75 standalone P-19 HTML;
- 4 capability mới × 3 static visual mode = 12 standalone P-19 HTML, giữ cả Bubble dù parent scatter-plot nằm trong P-18;
- Theo D-095/D-096/D-097, giữ presentation identity `layers` kế thừa semantic parent `layer-stack`, detailed three-series `line-chart` và detailed five-stage `medallion` ở đủ ba mode; tổng 90 P-19 specimen HTML + 14 P-18 anchor = 104 diagram tổng hợp; không tính index/contact sheet;
- 90/90 P-19 file phải có semantic fixture ID, type/parent/mode metadata, exact hash và automated check disposition; 14 P-18 anchor phải có exact source/hash binding và không đổi byte;
- generator không tái sinh 14 duplicate canonical type; không sửa P-19A registry/taxonomy để đạt gallery count và không nâng 14 P-18 light thành ba-mode proof;
- 39/39 canonical type và 4/4 capability phải route qua layout engine đã khóa, có type/capability silhouette declaration và không fallback sang generic unknown/card template;
- confusing within-engine clusters phải qua masked blind review với aggregate recognition ít nhất 85%; type legend, file name, intent prose và evidence rail không được tiết lộ đáp án;
- mọi explicit user-font fixture phải chứng minh precedence, computed family, required glyph coverage, measured wrapping và text containment trước geometry approval;
- gallery remains QA-only/non-package trong current scope và cần owner approval gắn exact manifest.

### Geometry/render hard checks

- SVG/HTML hợp lệ; nội dung nằm trong viewBox/canvas.
- Không clipping, unintended overlap, duplicate ID hoặc phần tử ngoài canvas.
- Connector đúng endpoint, route rõ, không che label/node; crossing được tránh hoặc thể hiện có chủ đích.
- DOM/read order khớp narrative order.
- Font fallback hiển thị đúng tiếng Việt.
- Font precedence khớp D-052; computed family/glyph coverage được kiểm, user-selected font không bị silent substitution.
- Card/node size xuất phát từ measured content; 100% material text nằm trong owning node/region ở canonical và responsive checks.
- Không dùng global post-layout transform để vượt containment, occupancy hoặc artboard-fit assertion.
- Build/render lặp lại phải ổn định trong cùng môi trường.

### Accessibility hard checks

- SVG có tên/mô tả truy cập được và ID duy nhất.
- Không truyền trạng thái chỉ bằng màu.
- Contrast, keyboard/focus và motion control đạt contract đã duyệt.
- `prefers-reduced-motion`, no-JS, print và static export giữ đủ ý nghĩa.
- Chart định lượng có dữ liệu dạng text/table hoặc representation có thể kiểm chứng.

### Quantitative integrity hard checks

- Cùng dataset semantic từ pasted table, CSV và JSON phải sinh normalized IR tương đương trước render.
- Giá trị, series, unit, axis/domain/tick/legend đúng dữ liệu nguồn.
- Không âm thầm bỏ missing/null/NaN, số âm, 0 hoặc duplicate date.
- Bar mặc định bắt đầu từ 0; ngoại lệ phải được nêu rõ.
- Scatter giữ đúng số điểm và tọa độ tương đối.
- Radar công khai scale/normalization và không trộn thang không tương thích.
- Gantt/Timeline phải giữ đúng date, timezone, order và duration; Quadrant giữ đúng tọa độ/scale; Pyramid/Funnel giữ đúng giá trị, tỷ lệ và thứ tự khi input chứa số.
- Không làm tròn hoặc scale gây hiểu nhầm.

### Import/security hard checks

- Fidelity ledger thỏa: nguồn = giữ lại + gộp + lược bỏ có giải thích + source rot.
- Không tự sáng tác thành phần hoặc im lặng làm mất semantics.
- Natural language, pasted table, CSV, JSON, draw.io và Mermaid đều được coi là dữ liệu không tin cậy; mọi label/cell/value phải được escape đúng HTML/SVG/CSS context.
- Không thực thi prompt nhúng, Mermaid, JavaScript, URL, event handler, external resource hoặc CSV formula payload.
- HTML/SVG/CSS injection, XML/DOCTYPE/XXE, deep/oversized JSON, malformed input, decompression abuse, oversized source và path traversal thất bại an toàn.
- Không có network side effect.

### Motion hard checks

- Static là mặc định và chứa đủ ý nghĩa.
- Step order xác định; pause/resume/replay không đổi kết quả cuối.
- Loop chỉ dùng cho decorative token, không mang thông tin semantic duy nhất.
- SVG/PNG/print là complete static frame.

Blocking failure:

- bất kỳ hard check nào thất bại;
- golden tự cập nhật mà không duyệt;
- forward test nhìn thấy đáp án kỳ vọng hoặc chẩn đoán nội bộ.

Người duyệt: QA reviewer đối với hard checks; chủ sở hữu đối với golden/contact sheet và benchmark rubric cuối.

## G-05 — Packaging và cross-platform

**Mục đích:** xác nhận ba artifact được sinh từ một source và cài đúng.

Điều kiện bắt buộc:

- Claude plugin ZIP, OpenAI/ChatGPT plugin ZIP và Universal raw skill ZIP cùng target version đã được chủ sở hữu cho phép;
- package tuân thủ cây và bốn inventory logic tại mục 6.1–6.2 của `PROJECT-CONTRACT.md`;
- runtime core và legal/provenance bundle có checksum tương ứng; chỉ declared brand mapping và platform overlay được khác;
- `SKILL.md` viết hoa, frontmatter hợp lệ, name khớp folder;
- Universal có đúng một top-level folder; Claude/OpenAI có envelope đúng official requirement và surface matrix đã duyệt, với một top-level folder là target mặc định;
- Universal giải nén vào `.agents/skills/` cho ra đường dẫn chuẩn;
- cả ba ZIP chứa đủ `LICENSE.md`, `LICENSE-APPLICATION.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `SOURCE_MANIFEST.json` và `ASSET_MANIFEST.json` ở vị trí theo contract;
- Claude package loại `agents/openai.yaml`; OpenAI và Universal package chứa đúng OpenAI metadata overlay đã xác minh;
- không absolute path, traversal, symlink nguy hiểm, `.DS_Store`, cache, log, secret hoặc file phát triển thừa;
- build xác định: thứ tự, timestamp, permission và encoding được chuẩn hóa;
- reference link và manifest schema hợp lệ;
- từng cell `supported` có install, trigger, representative output và fallback evidence;
- cell `conditional` có external condition, official documentary evidence, owner-approved limitation và không được đếm/quảng bá là `supported`; khi điều kiện khả dụng trước release phải smoke-test, nếu không phải giữ nhãn `conditional` rõ hoặc hạ thành `unsupported`;
- cell `unsupported` được công bố rõ, không bị bỏ khỏi matrix;
- capability thiếu ở host degrade minh bạch.

Blocking failure:

- ba bản runtime core hoặc legal bundle lệch nội dung ngoài khác biệt cho phép;
- package không cài/trigger được;
- payload phụ thuộc đường dẫn máy phát triển hoặc dependency ngầm;
- spec nền tảng chưa được xác minh ở thời điểm build.

Người duyệt gate kỹ thuật: technical/QA reviewer. Chủ sở hữu duyệt artifact phát hành tại G-07.

## G-06 — Brand, provenance và legal

**Mục đích:** khóa đúng asset và legal bytes trước khi build package phát hành.

Điều kiện bắt buộc:

- master logo không đổi; source hash và AI provenance được ghi;
- derivative có recipe/hash và vượt test mask, nền, kích thước nhỏ;
- chủ sở hữu duyệt contact sheet và derivative cuối;
- logo/brand được carve out khỏi grant chung theo wording luật sư duyệt;
- license có đúng tên, song ngữ và quy tắc tiếng Việt ưu tiên;
- quyền chỉ phát sinh qua paid order, written permission/email hoặc commercial agreement;
- luật Việt Nam và tòa án có thẩm quyền tại Việt Nam;
- `LICENSE.md`, `LICENSE-APPLICATION.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `SOURCE_MANIFEST.json`, `ASSET_MANIFEST.json` nhất quán;
- lawyer sign-off gắn với version/hash của đúng legal release candidate.

Blocking failure:

- quyền logo hoặc thành phần bên thứ ba chưa rõ;
- notice mâu thuẫn manifest;
- tuyên bố quyền tác giả/nhãn hiệu/clean-room vượt bằng chứng;
- legal wording chưa được luật sư duyệt.

Người duyệt: chủ sở hữu đối với brand derivative; luật sư Việt Nam đối với legal release candidate. G-06 không thay thế owner release authorization ở G-07.

## G-07 — Release authorization

**Mục đích:** ngăn phát hành hoặc push ngoài thẩm quyền.

Điều kiện bắt buộc:

- G-00 đến G-06 của cùng target version đều `PASS`;
- không còn finding `Critical` hoặc `High`; finding `Medium` còn lại phải được ghi nhận, có mitigation/limit và được chủ sở hữu chấp thuận rõ;
- version, checksum, provenance, package và legal candidate khớp nhau;
- owner approval của goldens/benchmark/brand và lawyer sign-off của legal bytes vẫn khớp artifact đã đóng gói;
- chủ sở hữu duyệt ba ZIP và toàn bộ release candidate, rồi cấp release authorization riêng;
- nếu legal byte thay đổi sau lawyer sign-off hoặc brand byte thay đổi sau owner approval, G-06 trở lại `FAIL` cho đến khi duyệt lại;
- người dùng ra lệnh rõ ràng cho commit/tag/push/release trong yêu cầu đang hoạt động;
- remote private và target repository được kiểm tra lại trước push.

Blocking failure:

- chỉ có “kế hoạch đã duyệt” nhưng không có lệnh release;
- bất kỳ artifact nào đổi sau approval mà chưa duyệt lại;
- push public hoặc sai repository.

Người duyệt: chủ sở hữu; luật sư cho phần pháp lý.

## Mẫu gate record

```text
Gate ID:
Artifact/version/hash:
Result: NOT-EVALUATED | PASS | FAIL | DEFERRED
Evidence:
Open findings:
Approved by:
Approval date:
Notes/limits:
```
