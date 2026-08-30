# Hợp đồng dự án — Thien-Skill-Creative-Diagram

**Mã tài liệu:** PC-001  
**Phiên bản tài liệu:** 1.5-candidate  
**Ngày cập nhật candidate:** 2026-08-29  
**Chủ sở hữu:** Tran Ngoc Thien  
**Baseline yêu cầu:** Đã được chủ sở hữu duyệt ngày 2026-08-15  
**Thẩm quyền và trạng thái thực thi hiện tại:** xem `PLAN.md`

## 1. Vai trò và thứ tự thẩm quyền

File này là nguồn sự thật duy nhất cho câu hỏi **“dự án phải tạo ra cái gì và theo nguyên tắc nào?”**

Thứ tự thẩm quyền:

1. Chỉ dẫn mới nhất, rõ ràng của chủ sở hữu trong cuộc trò chuyện.
2. Quyết định đã duyệt trong mục 12 của file này.
3. Phạm vi và nguyên tắc trong file này.
4. Chuẩn chức năng tham khảo và tài liệu nền tảng chính thức.
5. Đề xuất kỹ thuật chưa được duyệt.

Khi có mâu thuẫn hoặc một điểm chưa rõ có thể thay đổi kết quả vật chất, không tự suy đoán. Phải hỏi chủ sở hữu và chỉ cập nhật hợp đồng sau khi có quyết định.

## 2. Mục tiêu

Tạo một skill duy nhất có khả năng thiết kế diagram chuyên nghiệp, sáng tạo, đẹp, chính xác về ngữ nghĩa và dùng được trên nhiều bề mặt Claude/OpenAI. Năng lực diagram lấy `diagram-design` làm nền chức năng chủ đạo; hệ thống được tái triển khai độc lập, có quy trình thiết kế và QA chuyên nghiệp, hỗ trợ tiếng Việt tốt và có ba gói phân phối từ một canonical source.

Tên hiển thị: `Thien-Skill-Creative-Diagram`  
Technical skill ID, folder name và plugin ID: `thien-skill-creative-diagram`  
Phiên bản đã phát hành và được bảo toàn: `1.0.0`  
Phiên bản maintenance mục tiêu hiện tại: `1.5.0` (source/gallery only; chưa phải release authorization)

## 3. Nguồn chức năng chủ đạo

Nguồn chính: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design).

Snapshot cụ thể phải được khóa ở Phase P-01 trước khi triển khai. Tại thời điểm lập kế hoạch, taxonomy chuẩn được hiểu là 27 visual type từ `SKILL.md` và các type reference của upstream; con số 29 trong phần mô tả repository không được dùng để tự suy ra thêm hai type.

### 3.1. Baseline v1.0.0 — 27 visual type đã phát hành

1. Architecture
2. IT current-state
3. Flowchart
4. Sequence
5. State machine
6. ER/data model
7. Timeline
8. Swimlane
9. Quadrant
10. Radar/Spider
11. Loop/Flywheel
12. Nested
13. Tree
14. Org chart
15. Layer stack
16. Venn
17. Pyramid/Funnel
18. Bar chart
19. Line chart
20. Gantt
21. Scatter plot
22. High-Level
23. Process
24. Medallion
25. Data flow
26. DP integration
27. DP security matrix

### 3.2. Capability bổ sung bắt buộc

Phạm vi còn bao gồm toàn bộ variant, specimen, semantic pattern, import và motion thuộc snapshot upstream đã khóa. Chúng phải được phân loại là capability/variant, không được tự nâng thành visual type mới. Mỗi capability trong inventory đã khóa phải có implementation mapping và ít nhất một contract/smoke test; chỉ việc phối hợp các chiều mới được giảm bằng pairwise coverage.

Bảy semantic pattern tối thiểu đã xác định:

- fan-in queue hoặc bottleneck;
- repeated stage slots;
- unstructured input thành structured artifact;
- paired policy traces;
- secure paved road;
- governance/control catalog;
- compensating security layers.

Motion dự kiến: `none`, `reveal`, `step`, `loop`; static luôn là mặc định và phải giữ đủ ý nghĩa.

### 3.3. Target v1.5.0 — upstream delta candidate

P-16 dùng exact upstream snapshot đã được duyệt `diagram-design@648c2a597839301e06df1e7434a08bde9f42eed3` để tái xét G-01/G-02 cho target `1.5.0`. Snapshot này bổ sung 12 canonical type vào baseline 27, tạo target 39 canonical type:

28. Polar chart — magnitude theo category tuần hoàn, angle mang category và radius mang giá trị.
29. Treemap — part-to-whole phân cấp, diện tích mang magnitude.
30. Sankey — quantitative flow tách/gộp theo stage, độ rộng band mang lượng.
31. Fishbone — các nhóm nguyên nhân hội tụ vào một effect cần phân tích.
32. Wardley map — value chain đặt trên trục evolution để hỗ trợ quyết định build/buy/move.
33. Kanban — work item theo trạng thái, WIP limit và blocked state.
34. User journey — stage, action, touchpoint và sentiment của một hành trình.
35. Deployment — zone, host, artifact, replica, port và quan hệ runtime.
36. Dependency graph — dependency tổng quát có fan-in, rank và cycle mà tree không biểu đạt được.
37. UML class — class, attribute, operation và typed relationship.
38. Story map — narrative backbone, story row, release slice và cut line.
39. Database schema — physical table, column, data type, constraint, index và column-level foreign key.

Bốn capability mới cũng nằm trong scope nhưng không tăng canonical count:

- `Dumbbell`, parent `Bar chart`: hai giá trị trên cùng scale cho mỗi category; khoảng cách là thông tin chính.
- `Slopegraph`, parent `Line chart`: nhiều series so sánh giữa đúng hai trạng thái, giữ direction/rank/crossing.
- `Ridgeline`, parent `Line chart`: một distribution cho mỗi series trên shared domain/amplitude contract.
- `Bubble`, parent `Scatter plot`: x/y cộng magnitude thứ ba; **area**, không phải radius, mang magnitude.

Exact contract cho G-01/G-02@1.5.0 đã được chủ sở hữu duyệt theo D-047 và được khóa theo frozen candidate manifest `evidence/p16/G02-1.5.0-CONTRACT-MANIFEST.json`: bộ P-02 đã duyệt được kế thừa byte-bound cho các điều không đổi, còn taxonomy, request enum, semantic IR, type-specific invariant và test mapping được amend bằng evidence P-16. Vì vậy các câu “27 type” trong hồ sơ P-02 là historical v1.0.0 baseline, không phải target v1.5.0. Ma trận requirement → nguồn trừu tượng → implementation độc lập dự kiến → test nằm tại `evidence/p16/CAPABILITY-PROVENANCE-MATRIX.md`.

P-17 đã triển khai contract semantic này theo D-048 và đóng với record `evidence/p17/P-17-EVIDENCE.md`; việc hoàn tất semantic source không cấp quyền tạo visual/gallery hoặc bắt đầu P-18/P-19.

Các feature upstream khác ngoài taxonomy/variant delta này — như onboarding, tải font/resource mạng, profile, doctor, command/prompt hoặc packaging surface mới — không được suy ra là scope v1.5.0. Muốn thêm phải có quyết định riêng của chủ sở hữu.

### 3.4. Gallery evidence target v1.5.0

- Gallery là QA-only evidence trong `evidence/`, không phải runtime/package asset ở scope hiện tại.
- Mọi HTML, CSS, SVG, data, prose, layout và ví dụ phải được tự viết; không copy, dịch sát, trace hoặc chuyển đổi gallery/specimen upstream.
- P-18 phải tạo pilot gallery nguyên bản để chủ sở hữu duyệt visual direction trước khi nhân rộng.
- Exact P-18 pilot contract ban đầu gồm 12 family × ba mode = 36 standalone HTML, với case/data/assertion và rubric inheritance tại `evidence/p16/PILOT-GALLERY-CONTRACT.md`; contract được owner duyệt tại G-02@1.5.0 theo D-047 và được phép triển khai riêng theo D-049. Candidate đầu tiên bị supersede theo D-050; replacement freeze sau P-18R3 tiếp tục bị owner từ chối làm visual direction theo D-051. Cả hai candidate chỉ là historical evidence, không phải golden.
- Visual-foundation contract hiện hành cho candidate kế tiếp là `P18R4-VISUAL-FOUNDATION-1.5.0` tại `evidence/p18/P-18R4-VISUAL-FOUNDATION-CONTRACT.md` và machine-readable binding `evidence/p18/P-18R4-VISUAL-FOUNDATION.json`, khóa theo D-051/D-052. P-18R5 review-01/review-02/review-03 được giữ như historical evidence; review-03 đã đạt silhouette crossing nhưng owner còn thấy hairline gap tại hai tiếp điểm hop theo D-057. Exact review-04 `P18R5-MASTER-KERNEL-SWIMLANE-ANCHOR-REVIEW-04-1.5.0`, manifest SHA-256 `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8`, đã dùng shared hop geometry và crown-only underlay để connector liền mạch, được owner phê duyệt theo D-058 và đóng P-18R5 ở trạng thái `passed`. D-059 cho phép triển khai riêng P-18R6 để tạo đúng 14 anchor `neutral-light`, mỗi layout engine một anchor, dưới `evidence/p18/r6/`. Exact review-01 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-1.5.0`, manifest SHA-256 `fcdec11e49a00d89d82a3fafaba7cae2ac8e7c58908fa76cc2fa6eba383aad37`, review-02 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-02-1.5.0`, manifest SHA-256 `2f9c7aad3a2dd9d43d575ddfb864effa915df909134d5401dbb075ed6ea2cf7b`, review-03 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-03-1.5.0`, manifest SHA-256 `572de899399755268d63fa5cb49c598a6ee6c5d509418ed8d07484a750c62e54`, review-04 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-04-1.5.0`, manifest SHA-256 `6be1aa8894cf62d252c9cd890f14b4e825497b811046df57ccb301e84054f185`, review-05 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-05-1.5.0`, manifest SHA-256 `20b8f257b44d7f6c9fc0cbf7eed9b710778bdcebb142978b8f47aad61eab393b`, và review-06 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-06-1.5.0`, manifest SHA-256 `b1f934b5542079a93763b5ac0237dbdc2871dc6f97e8e4ea14adeb05536f844d`, đều đã frozen rồi chuyển historical byte-bound theo D-060–D-065. Exact review-07 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-07-1.5.0`, manifest SHA-256 `da2d8840b8bf009c54c10b72ccc7e9fbd2aedf6422acd2c822548f63a29b5290`, đã được freeze theo D-065 rồi archive historical byte-bound theo D-066; bốn right-side annotation vẫn dùng cùng geometry-derived `72px` visual-gap metric với spread `0.007px`. Exact review-08 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-08-1.5.0`, manifest SHA-256 `a5e58ccb47ea63b6904e84859aace63fb3f09b2cb3147e4a3a96ce41617eb7ec`, đã được archive historical byte-bound theo D-067 sau khi khóa six-phase coverage cho diagram 06 và schema geometry cho diagram 11. Exact review-09 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-09-1.5.0`, manifest SHA-256 `d7f7e9653d02b0b156c2aa144643047edb09fb970a5ae07e58f7b1cecbc44703`, đã archive historical byte-bound theo D-068 sau khi khóa bốn axis-direction annotation của diagram 12. Exact review-10 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-10-1.5.0`, manifest SHA-256 `9a1fe7282db733c8239a0daf4abddff984c2372bfb6bb82f759de94980adaf84`, đã frozen theo D-068: vùng `DO FIRST` giữ pale coral fill và review-09 geometry nhưng không còn perimeter stroke; mọi trục, annotation, quadrant title, initiative, focal point và legend giữ nguyên. Candidate này đã chuyển historical byte-bound; browser execution, masked independent recognition, five-second review, independent visual-craft gate và owner decision vẫn là gate riêng đối với current candidate. Trạng thái này không mở P-19A→P-19C và không cấp quyền runtime/package/release. Chỉ phase/subphase được owner cho phép rõ ràng mới được triển khai.
- D-069 cho phép tạo P-18R6 review-11 riêng diagram 11 sau khi archive exact review-10: cardinality `1` và `N` phải là hai nhãn endpoint độc lập cho từng quan hệ; `PLACES` và `PAID BY` nằm phía trên connector ngang, `CONTAINS` nằm bên phải connector dọc; mọi label giữ minimum clearance 8px, không tràn vào node và có machine-readable placement/endpoint binding. Exact review-11 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-11-1.5.0`, manifest SHA-256 `69b93b45fc852b9e9c1405b66fbb40dd10d964fa55f589b65a51984d5b3dccfc`, đã frozen với `322/322 PASS` rồi archive historical byte-bound theo D-070.
- D-070 khóa remediation review-12 riêng diagram 11: giữ ba relationship name ở vị trí above/right của review-11, nhưng đặt từng cardinality `1`/`N` đúng trên trục connector và tạo khoảng trắng bằng canvas-fill/no-stroke knockout được đo riêng phía sau glyph; connector vẫn là một semantic line liên tục với paint order connector → knockout → label. Exact review-12 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-12-1.5.0`, manifest SHA-256 `90de78337c49f1ee42aae8730bbf072eb8bf679388038041b793f943ddfcafb6`, đã frozen với static `325/325 PASS`, browser `42/42 PASS`, full regression `148/148 PASS`, 75/75 manifest records và 26/26 non-target anchor HTML/SVG file byte-identical với review-11, rồi archive historical byte-bound theo D-071.
- D-071 khóa remediation review-13 riêng diagram 14: mọi bar/ribbon dùng shared `0.025px/minute` scale, mỗi applicable incoming/outgoing bar interface được contiguous non-overlap ribbon intervals phủ đúng 100%, title/value stack căn giữa phía trên với measured clearance tối thiểu 12px và mọi bar là square-corner `<rect>` không `rx`. Exact review-13 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-13-1.5.0`, manifest SHA-256 `520c4ad74b944a218a576bdec7f100eb84054e712a066965417961fe97b91324`, đã frozen với static `332/332 PASS`, browser `42/42 PASS`, full regression `148/148 PASS`, 75/75 manifest records và 26/26 non-target anchor HTML/SVG file byte-identical với review-12, rồi archive historical byte-bound theo D-072.
- D-072 khóa remediation review-14 riêng diagram 14: ba upper-row bar `Monthly budget`, `Unit tests`, `Passed` phải align top tại exact `y=210px`, max top-edge spread `0.01px`; chỉ source bar và ba source-side ribbon interval được dịch đồng bộ, còn toàn bộ D-071 scale/occupancy/label/square-bar/value/conservation contract giữ nguyên. Exact review-14 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-14-1.5.0`, manifest SHA-256 `9e88febc31f895aaada5385f2b9fc3a3384b8ff607831ac4ad9e302165b36637`, đã frozen với static `333/333 PASS`, browser `42/42 PASS`, full regression `148/148 PASS`, 75/75 manifest records, 75/75 review-13 archive records và 26/26 non-target anchor HTML/SVG file byte-identical với review-13, rồi archive historical byte-bound theo D-073.
- D-073 khóa remediation review-15 riêng diagrams 04/08/09: pale horizontal line là semantic band boundary, mọi card/icon căn giữa trong band, không separator nào giao/đè member, static/browser center tolerance `0.01/0.75px`, canonical clearance `22/27/58px`, và connector không dùng separator làm route rail gây hiểu nhầm. Exact review-15 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-15-1.5.0`, manifest SHA-256 `0e2fcddc00a5b993fd34b4376c32e10a1ca0dd64013202e58ac35df801798a5b`, đã frozen với static `354/354 PASS`, browser `42/42 PASS`, full regression `148/148 PASS`, 75/75 current manifest records, 75/75 review-14 archive records và 22/22 non-target anchor HTML/SVG file byte-identical với review-14; hiện giữ historical byte-bound theo D-074.
- D-074 khóa remediation review-16 riêng diagram 13: bỏ arrowhead hướng xuống tại shared origin của trục định lượng; cả trục `AUTOMATION %` và `CONTROL CONFIDENCE` phải là plain axis, không serialize hoặc compute bất kỳ `marker-start`/`marker-mid`/`marker-end` nào. Origin, zero/tick labels, scale/grid, bubbles, direct labels, focal styling, legend và accessible quantitative data giữ nguyên review-15. Exact review-15 đã archive historical byte-bound; exact review-16 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-16-1.5.0`, manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`, đã frozen với static `359/359 PASS`, browser `42/42 PASS`, full regression `148/148 PASS`; 26/26 non-target anchor HTML/SVG file byte-identical review-15 và chỉ đúng diagram 13 HTML/SVG thay đổi. Candidate được owner-approved theo D-075 rồi archive historical byte-bound trước D-076 remediation; `G-03@1.5.0` vẫn `NOT-EVALUATED`.
- D-075 ghi nhận ngày 2026-08-25 chủ sở hữu Tran Ngoc Thien xác nhận toàn bộ 14 diagram của exact frozen P-18R6 review-16 đã đạt yêu cầu. Đây là owner visual approval gắn đúng manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`; trạng thái owner review của review-16 chuyển `PASS`. Tại thời điểm D-075, masked blind recognition, five-second takeaway và independent visual-craft vẫn là gate độc lập `PENDING`; approval này không tự áp dụng cho candidate kế nhiệm.
- D-076 tạo exact review-17 sau khi archive/verify review-16 `75/75`. Chỉ diagram 09/14 thay đổi; 24/24 non-target HTML/SVG file byte-identical review-16. Exact candidate `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`, đạt static `366/366`, browser `42/42`, Quick Look `14/14`, regression `148/148`, manifest `75/75`, masked recognition/five-second `14/14` và independent visual-craft `93/100` với minimum dimension `4/5`; independent aggregate `PASS`. Owner approval exact review-17 và `G-03@1.5.0` vẫn chờ quyết định riêng; P-19 chưa được phép.
- D-077 ghi nhận ngày 2026-08-27 chủ sở hữu Tran Ngoc Thien phê duyệt exact P-18R6 review-17, phê duyệt `G-03@1.5.0 PASS` và cho phép đóng P-18. Approval gắn đúng manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a` cùng independent aggregate `PASS`; P-18 chuyển `passed`. Chủ sở hữu đồng thời chỉ rõ chưa triển khai P-19, nên quyết định này không authorize P-19, runtime/package/`dist`/publication/Git/Release mutation.
- D-078 ghi nhận ngày 2026-08-27 chủ sở hữu chỉ dẫn rõ ràng “triển khai P-19A”, qua đó authorize riêng P-19A — 39+4 type/capability adapters. Thẩm quyền gồm canonical adapter source/reference/test, evidence/provenance/manifest và đồng bộ governance/handoff; phải giữ nguyên exact P-18R5 review-04 và P-18R6 review-17, không emit HTML/SVG gallery, không derive ba mode, không mở P-19B/P-19C, build/rebuild package, sửa `dist/`, publication mirror, commit, push, tag, Release hoặc phát hành. P-19A đã hoàn tất technical verification `14/14` focused và `162/162` full regression; P-19 chuyển `in-progress`, P-19A `passed`, còn P-19B/P-19C vẫn `not-started` và unauthorized.
- D-079 ghi nhận ngày 2026-08-27 chủ sở hữu chỉ dẫn rõ ràng “triển khai P-19B — three-mode derivation và exact 129 HTML”, qua đó authorize riêng P-19B. Thẩm quyền gồm canonical QA renderer/reference/test, đúng 117 canonical + 12 capability standalone HTML, index/contact sheet, preview SVG, focused static/browser evidence, provenance/manifest và đồng bộ governance/handoff; phải giữ nguyên exact P-18R5 review-04, P-18R6 review-17 và P-19A candidate. P-19B không được tự thực hiện P-19C full QA/freeze/masked/owner review, không làm `G-04@1.5.0 PASS`, không build/rebuild package, sửa `dist/`, publication mirror, commit, push, tag, Release hoặc phát hành.
- D-080 ghi nhận ngày 2026-08-27 chủ sở hữu bác bỏ hướng thiết kế của exact P-19B candidate đầu `P19B-THREE-MODE-EXACT-129-HTML-1.5.0` vì không kế thừa đủ phong cách P-18 đã duyệt. Candidate đầu vẫn là historical technical evidence, byte-bound bởi gallery manifest SHA-256 `ed6a14521a1277143bece89deac732cec607a9c5d1738d593e52498191a3b106`, plan manifest `59edd733dc180d8274a31ab91bc5f89b3450fefe9dc80c2101aa2ebee204b40f` và source manifest `44cdbe31b7aa715ff88d617274cf0e49cd6c9eb1aac8cb11fa46ce753fa3188c`, nhưng bị supersede cho mọi owner-approval/golden purpose. D-080 authorize remediation ngay trong P-19B để tạo lineage kế nhiệm kế thừa trực tiếp visual system/kernel của exact P-18R6 review-17: neutral-light phải giữ warm-paper/coral/type-role/spacing/shape/connector grammar đã duyệt; neutral-dark và editorial chỉ được derive bằng semantic role mapping trong cùng visual grammar; geometry/IR phải bất biến qua ba mode; exact 129 standalone HTML, contact sheet và focused evidence phải được tái sinh và kiểm chứng. P-19B trở lại `in-progress` cho đến khi candidate kế nhiệm được owner duyệt; P-19C vẫn chưa được phép; không sửa frozen P-18/P-19A, package, `dist/`, publication mirror, Git, Release hoặc phát hành.
- Gallery hiện hành theo D-084–D-093 dùng trực tiếp 14 anchor P-18 review-17 đã duyệt ở `neutral-light`, không tạo P-19 trùng loại. P-19 chỉ sinh 25 canonical type × ba mode = 75 HTML và bốn capability × ba mode = 12 HTML, tổng 87 specimen; trang tổng hợp có 14 + 87 = 101 diagram. D-086 sửa riêng Fishbone; D-087 sửa riêng dp-integration; D-088 sửa riêng bar-chart; D-089 sửa riêng dp-security-matrix; D-090/D-091 sửa er-data-model và cardinality; D-092 thay riêng high-level; D-093 thay riêng it-current-state bằng landscape ba miền chi tiết. Cả hai kế thừa P-18 và dùng connector orthogonal liên tục với góc 90° bo tròn mặc định, thẳng chỉ khi khai báo. Scope gallery và mọi diagram khác giữ nguyên. Yêu cầu 129 HTML P-19 trước đây là historical, đã được thay thế trong phạm vi gallery này; taxonomy/semantic source vẫn 39 type + bốn capability.
- Gallery phải dùng dữ liệu/scenario nguyên bản, nêu type/variant/mode, mở trực tiếp được không cần build, không phụ thuộc resource mạng bắt buộc và vẫn tuân thủ semantic, accessibility, quantitative, geometry và security contract.
- Gallery chỉ được coi là bằng chứng chất lượng sau owner visual approval; việc có file HTML không tự tạo golden hoặc tự làm gate `PASS`.

## 4. Nguyên tắc tái triển khai độc lập

Dự án áp dụng **clean-room-oriented independent reimplementation**:

- Được phép nghiên cứu taxonomy, hành vi, nguyên tắc trừu tượng, format, input/output và failure mode.
- Phải tự viết toàn bộ code, instruction, prose, CSS, template, visual system, asset và ví dụ.
- Không sao chép hoặc dịch sát code, prose, CSS, template, script, gallery, icon hay asset của upstream.
- Không trace hoặc tái tạo một specimen theo pixel.
- Mọi feature phải có mapping từ yêu cầu đến nguồn tham khảo, implementation độc lập và test.
- `SOURCE_MANIFEST.json` dự kiến là source of truth cho provenance; notice phải được sinh hoặc đối chiếu từ manifest để tránh tuyên bố mâu thuẫn.

`Thien-UI-UX-Ultra` chỉ được dùng để học nguyên tắc: design contract, progressive routing, render–inspect–revise–verify, accessibility và QA. Không sao chép code, script, template hoặc asset từ skill đó.

## 5. Hồ sơ sản phẩm v1.0.0

### 5.1. Input

- yêu cầu bằng ngôn ngữ tự nhiên;
- bảng được dán trực tiếp;
- CSV;
- JSON;
- draw.io: `.drawio`, `.drawio.xml`, `.drawio.png` có dữ liệu nhúng và `.drawio.svg`, gồm tài liệu nhiều trang;
- Mermaid: `.mmd`, `.mermaid` và fenced Mermaid trong Markdown; grammar v1 gồm flowchart/graph, sequence, state và ER.

Đầu vào nhập phải được parse thành intermediate representation rồi vẽ lại độc lập. Không render hoặc thực thi nội dung không tin cậy. Mọi mất mát/ngộ nhận khi import phải được ghi trong fidelity ledger.

### 5.2. Output

- HTML và SVG là output lõi, portable.
- PNG được tạo khi môi trường có renderer/browser phù hợp.
- HTML+PNG được tạo khi điều kiện cho phép.
- Khi thiếu renderer, phải báo fallback minh bạch; không tự cài Playwright, Chromium hoặc dependency ngoài phạm vi cho phép.

### 5.3. Hành vi và ngôn ngữ

- `SKILL.md` kỹ thuật dùng tiếng Anh để tương thích rộng.
- Nội dung diagram và phản hồi đầu ra theo ngôn ngữ người dùng.
- Tiếng Việt có dấu phải được giữ đúng, không cắt chữ và không đổi thuật ngữ nghiệp vụ nếu không được yêu cầu.
- Diagram mặc định dùng visual system trung tính, không gắn logo hoặc ép bảng màu thương hiệu.
- TDTN navy–gold chỉ dùng cho nhận diện skill, plugin, listing và package.
- Static-first, accessible-first, semantic-first; thẩm mỹ không được che lấp dữ liệu hoặc quan hệ.
- Chuẩn chất lượng hình ảnh hướng tới cảm giác chuyên nghiệp, biên tập chặt chẽ và rõ quan hệ mà chủ sở hữu đánh giá cao ở `diagram-design`; đây chỉ là quality outcome ở mức trừu tượng. Visual system, bố cục, token, shape, connector, prose và specimen của dự án phải nguyên bản, không tái tạo expression hoặc pixel của upstream.

### 5.4. Phụ thuộc

- Không có dependency bên ngoài bắt buộc để skill có thể hoạt động ở mức lõi.
- Capability phụ thuộc môi trường phải tự phát hiện và degrade an toàn.
- Không gọi mạng, tự tải font, tự cài package hoặc thực thi nguồn nhập nếu chưa được người dùng cho phép rõ ràng.

### 5.5. Visual foundation target v1.5.0

Theo D-051/D-052, visual implementation kế tiếp phải dùng một canonical pipeline theo thứ tự: resolve typography → load/validate font và glyph → measure thật → size primitive/node → chọn layout engine theo family → fit artboard → allocate port/obstacle → route/label/bridge → validate → emit. Không dùng fixed artboard/global transform, fixed card hoặc character-count wrapping để thay cho layout.

Contract chi tiết và exact 14-engine mapping cho 39 canonical type + bốn capability nằm tại `evidence/p18/P-18R4-VISUAL-FOUNDATION-CONTRACT.md` (SHA-256 `addf6793a9670d5a76b48c3835f2e2e08750b0bfca7cc27b210210acaa9f95a5`) và `evidence/p18/P-18R4-VISUAL-FOUNDATION.json` (SHA-256 `37e0c955cc814d10dc393f148a4a55c2d5ef141e547c370171d176cc2efd7be9`). Đây là clean-room-oriented independent reimplementation: không copy/reuse code, CSS, SVG, template, gallery, specimen, font file hoặc asset upstream.

Default typography direction là Instrument Serif cho display/editorial, Geist cho human-facing sans và Geist Mono cho technical metadata. Đây chỉ là default. Font hoặc typography profile được người dùng chọn rõ ràng phải được ưu tiên theo role trước default; mọi override phải được resolve trước measurement/layout và lặp geometry QA. Không được tải/cài/embed font ở P-18R4; embedding sau này chỉ được dùng font lấy độc lập từ official publisher với license/provenance và authorization phù hợp.

## 6. Kiến trúc và phân phối

Một canonical source duy nhất phải sinh ba ZIP riêng. Contract dưới đây là layout mục tiêu; schema/field nền tảng phải được xác minh lại bằng tài liệu chính thức ở P-01 và P-13.

### 6.1. Bốn inventory logic

1. **Runtime core dùng chung:** `SKILL.md`, `scripts/`, `references/` và runtime assets thật sự cần cho việc vẽ diagram.
2. **Legal/provenance bundle dùng chung:** `LICENSE.md`, `LICENSE-APPLICATION.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `SOURCE_MANIFEST.json` và `ASSET_MANIFEST.json`.
3. **Brand/presentation assets:** chỉ derivative đã duyệt; destination cụ thể được khai báo trong `ASSET_MANIFEST.json`.
4. **Platform overlay:** Claude manifest, OpenAI manifest và `agents/openai.yaml` khi host cần.

Runtime core và legal/provenance bundle phải có byte hash tương ứng giữa ba artifact. Brand asset có thể khác theo yêu cầu host nhưng phải truy được về cùng master/recipe trong asset manifest. Chỉ platform overlay **và brand destination mapping đã khai báo** được khác có chủ đích.

`ASSET_MANIFEST.json` là một superset byte-identical trong cả ba package. Mỗi entry phải có `package_targets`/scope rõ ràng. Validator chỉ yêu cầu asset hiện diện trong package được entry nhắm tới; entry dành cho package khác là thông tin provenance, không bị coi là dangling. Không tạo manifest riêng cho từng ZIP.

Nếu `init_skill.py` sinh `agents/openai.yaml`, file này được quản lý như OpenAI platform overlay, không phải provider-neutral runtime core. Nó được đưa vào OpenAI plugin và Universal package dành cho ChatGPT Desktop/Codex; không đưa vào Claude plugin.

### 6.2. Cây ZIP mục tiêu

Universal top-level folder là quyết định đã khóa. Với Claude/OpenAI, cây dưới đây khóa **content placement logic**; outer archive envelope có thể phải điều chỉnh theo official packaging requirement được xác minh và duyệt trong G-01/G-02/P-13. Không được dùng việc điều chỉnh envelope để làm lệch runtime core hoặc legal bundle.

**Claude plugin ZIP**

```text
thien-skill-creative-diagram/
├── .claude-plugin/plugin.json
├── assets/                     # brand/listing derivatives theo manifest
├── skills/
│   └── thien-skill-creative-diagram/
│       ├── SKILL.md
│       ├── scripts/            # khi thật sự cần
│       ├── references/         # khi thật sự cần
│       └── assets/             # runtime assets dùng chung
├── LICENSE.md
├── LICENSE-APPLICATION.md
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── SOURCE_MANIFEST.json
└── ASSET_MANIFEST.json
```

**OpenAI/ChatGPT plugin ZIP**

```text
thien-skill-creative-diagram/
├── .codex-plugin/plugin.json
├── assets/                     # brand/listing derivatives theo manifest
├── skills/
│   └── thien-skill-creative-diagram/
│       ├── SKILL.md
│       ├── scripts/
│       ├── references/
│       ├── assets/
│       └── agents/openai.yaml
├── LICENSE.md
├── LICENSE-APPLICATION.md
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── SOURCE_MANIFEST.json
└── ASSET_MANIFEST.json
```

**Universal raw skill ZIP**

```text
thien-skill-creative-diagram/
├── SKILL.md
├── scripts/
├── references/
├── assets/                     # runtime + approved local-listing assets
├── agents/openai.yaml
├── LICENSE.md
├── LICENSE-APPLICATION.md
├── NOTICE
├── THIRD_PARTY_NOTICES.md
├── SOURCE_MANIFEST.json
└── ASSET_MANIFEST.json
```

Universal ZIP có đúng một top-level folder và được giải nén vào `.agents/skills/` để tạo `.agents/skills/thien-skill-creative-diagram/SKILL.md`. Claude/OpenAI dùng một top-level folder như target mặc định, nhưng gate kiểm envelope theo official requirement đã được surface matrix phê duyệt.

### 6.3. Surface matrix bắt buộc

P-02 phải lập ma trận **surface × artifact × install method × trigger × output × fallback × support status**. Ma trận tối thiểu phải xem xét:

- Claude Code plugin;
- Claude Code personal/project raw skill;
- Claude web/Desktop/API custom-skill surface nếu tài liệu chính thức còn hỗ trợ;
- ChatGPT web/mobile qua OpenAI plugin/distribution surface được hỗ trợ;
- ChatGPT Desktop, Codex CLI và IDE qua plugin hoặc `.agents/skills` theo hỗ trợ chính thức.

Universal raw ZIP có thể làm artifact raw-skill cho Claude nếu envelope và cách cài được tài liệu chính thức xác nhận ở P-01; không tự tuyên bố tương thích. Mỗi cell phải ghi `supported`, `conditional` hoặc `unsupported` kèm bằng chứng. Release không được quảng bá một surface chưa smoke-test.

Ba package không được duy trì ba bản nội dung bằng tay. Core phải provider-neutral; platform khác biệt chỉ đến từ overlay và asset mapping đã khai báo.

Repository phát hành dự kiến là private: [thiendeptrainhat/Thien-Skill-Creative-Diagram](https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram).

## 7. Nhận diện và logo

Nguồn logo do chủ sở hữu cung cấp: `<OWNER_HOME>/Documents/Logo TDTN.png`.

Thông tin đã ghi nhận nhưng chưa xử lý:

- chủ sở hữu xác nhận logo thuộc sở hữu của mình;
- logo được tạo bằng AI;
- không có file vector;
- PNG 1100 × 1100, RGBA có alpha;
- SHA-256 nguồn: `020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e`.

Nguyên tắc xử lý ở P-09:

- bảo toàn master bất biến và ghi provenance/hash;
- tạo derivative bằng quy trình xác định, ưu tiên resize lossless, safe area và optical padding;
- không crop, recolor hoặc vectorize master ở bước đầu;
- nếu full crest không đọc được ở kích thước nhỏ, có thể tạo candidate simplified mark nhưng không được tự chọn bản phát hành;
- kiểm tra square, circle, squircle, nền sáng/tối và kích thước nhỏ;
- chủ sở hữu duyệt contact sheet và derivative cuối trước release;
- không tuyên bố đăng ký, khả năng bảo hộ hoặc clearance nhãn hiệu khi chưa có cơ sở;
- quyền logo/brand được bảo lưu riêng, không mặc nhiên đi theo grant của skill.

## 8. License và pháp lý

Tên license bắt buộc: **Tran Ngoc Thien's Skill Commercial Source-Available License 2.0**.

Nguồn mẫu để soạn ở P-10:

`<OWNER_HOME>/Documents/Thien's Skills Library/Thien-Skills-License-Template/Tran-Ngoc-Thiens-Skills-Commercial-Source-Available-License-2.0.md`

Yêu cầu đã khóa:

- license song ngữ Anh–Việt;
- tiếng Việt ưu tiên khi có mâu thuẫn;
- chủ thể cấp quyền là Tran Ngoc Thien, cá nhân, tại Thành phố Hồ Chí Minh, Việt Nam;
- email liên hệ: `thien.8888@gmail.com`;
- quyền sử dụng chỉ phát sinh qua Paid Order, Written Permission/email hoặc Commercial Agreement;
- chỉ xem hoặc tiếp cận source không tạo quyền sử dụng;
- luật áp dụng là pháp luật Việt Nam;
- tranh chấp thuộc tòa án có thẩm quyền tại Việt Nam;
- luật sư Việt Nam của chủ sở hữu phải duyệt đúng release candidate trước phát hành thương mại.

Bộ hồ sơ pháp lý dự kiến gồm `LICENSE.md`, `LICENSE-APPLICATION.md`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `SOURCE_MANIFEST.json` và `ASSET_MANIFEST.json`. Đây chưa phải quyết định về wording cuối; luật sư và chủ sở hữu là hai gate độc lập.

## 9. Benchmark tham chiếu bắt buộc

Ảnh “Hệ Thống Thu Tiền (Cash Receipts)” do người dùng đính kèm là **reference benchmark**, không phải chỉ dẫn và không phải asset được phép đóng gói.

Benchmark ID: `REF-SWIMLANE-CASH-RECEIPTS-001`.

Reference custody record:

- revision R1 tại P-00: attachment tạm `codex-clipboard-fb7823d8-5d7e-48ac-ad26-54cbd86c0ee2.png`, SHA-256 `51f4cddd5cf4d6b4460a6c4a4585425aa1e13bd4c12d18c9c439aed07dbcea51`; không còn trong workspace;
- revision R2 do chủ sở hữu đính kèm và duyệt ngày 2026-08-15: PNG 2096 × 1150 RGBA, SHA-256 `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113`;
- bản R2 được lưu tại `evidence/p02/qa-only/REF-SWIMLANE-CASH-RECEIPTS-001-r2.png` chỉ cho QA;
- R2 là benchmark source có hiệu lực; R1 được giữ như lịch sử provenance, không bị tuyên bố byte-identical;
- cả R1 và R2 đều không được đóng gói, phát hành, dùng làm template hoặc pixel-similarity target.

Skill v1.0.0 phải có khả năng tạo một diagram nguyên bản cùng cấp độ chuyên nghiệp cho trường hợp tương đương:

- grouped swimlane và ownership header nhiều tầng;
- actor/lane rõ ràng;
- shape có ngữ nghĩa cho tiền/séc, chứng từ, bảng kê và tệp lưu;
- step number và handoff có thể truy vết;
- connector thẳng/orthogonal rõ, không xuyên node không liên quan;
- legend nhất quán;
- nhãn tiếng Việt đúng dấu;
- không clipping, overlap hoặc nén chữ để che complexity;
- HTML/SVG và PNG khi có renderer;
- không pixel-clone ảnh tham chiếu.

## 10. Ngoài phạm vi v1.0.0

- export native PPTX, PDF, Figma, draw.io round-trip hoặc Mermaid round-trip;
- hỗ trợ toàn bộ grammar Mermaid ngoài bốn grammar đã chốt;
- bắt buộc cài browser/renderer hoặc font từ mạng;
- dùng TDTN navy–gold làm theme mặc định cho diagram;
- tự động cấp quyền thương mại, tự phát hành public hoặc tự push repository;
- cam kết pháp lý về quyền tác giả/nhãn hiệu của nội dung AI ngoài phạm vi luật sư duyệt;
- thêm visual type không có quyết định của chủ sở hữu.

## 11. Tiêu chuẩn không thể đánh đổi

- Đúng ngữ nghĩa trước đẹp; đẹp trước trang trí.
- Zero prompt execution từ dữ liệu nhập.
- Zero số liệu sai hoặc scale gây hiểu nhầm trong chart định lượng.
- Zero nội dung quan trọng bị mất mà không có fidelity ledger.
- Zero hard failure về clipping, connector sai đích, accessibility nghiêm trọng, package không cài được hoặc provenance mơ hồ.
- Critical gate không được bù bằng điểm thẩm mỹ trung bình.
- Golden, logo derivative, benchmark set, license và release candidate đều cần người phê duyệt đã xác định.

## 12. Sổ quyết định đã duyệt

| ID | Quyết định | Trạng thái |
|---|---|---|
| D-001 | Display name là `Thien-Skill-Creative-Diagram`. | LOCKED |
| D-002 | Technical ID/folder/plugin ID là `thien-skill-creative-diagram`. | LOCKED |
| D-003 | Phiên bản phát hành đầu tiên là `1.0.0`. | LOCKED |
| D-004 | `diagram-design` là nguồn chức năng chủ đạo. | LOCKED |
| D-005 | Phạm vi là 27 canonical type cộng mọi variant/specimen/pattern/import/motion của snapshot; capability bổ sung không tính thành type mới. | LOCKED |
| D-006 | Tái triển khai độc lập; không sao chép code/text/CSS/template/script/asset upstream. | LOCKED |
| D-007 | `Thien-UI-UX-Ultra` chỉ cung cấp nguyên tắc và workflow. | LOCKED |
| D-008 | Profile là portable professional: HTML/SVG core, PNG có điều kiện, không dependency ngoài bắt buộc. | LOCKED |
| D-009 | Diagram mặc định trung tính; TDTN navy–gold chỉ nhận diện package/skill. | LOCKED |
| D-010 | Một canonical source sinh ba ZIP Claude, OpenAI/ChatGPT và Universal `.agents/skills`. | LOCKED |
| D-011 | Mỗi ZIP là artifact riêng. | LOCKED |
| D-012 | Repository đích là GitHub private đã nêu tại mục 6. | LOCKED |
| D-013 | Tên license là `Tran Ngoc Thien's Skill Commercial Source-Available License 2.0`. | LOCKED |
| D-014 | License song ngữ, tiếng Việt ưu tiên; luật và tòa án Việt Nam. | LOCKED |
| D-015 | Phải trả tiền hoặc được cấp quyền qua email/văn bản/thỏa thuận thương mại. | LOCKED |
| D-016 | Chủ sở hữu xác nhận sở hữu logo; logo do AI tạo, không có vector. | LOCKED |
| D-017 | Chủ sở hữu ủy quyền chọn quy trình xử lý logo phù hợp nhưng vẫn duyệt derivative cuối. | LOCKED |
| D-018 | Luật sư Việt Nam duyệt license/release candidate pháp lý. | LOCKED |
| D-019 | Bộ benchmark do dự án đề xuất trước và chủ sở hữu phê duyệt trước khi dùng làm golden. | LOCKED |
| D-020 | `REF-SWIMLANE-CASH-RECEIPTS-001` là must-pass benchmark. | LOCKED |
| D-021 | Chủ thể cấp quyền là Tran Ngoc Thien tại Thành phố Hồ Chí Minh, Việt Nam; email liên hệ `thien.8888@gmail.com`. | LOCKED |
| D-022 | Chất lượng hình ảnh hướng tới cảm giác chuyên nghiệp/editorial mà chủ sở hữu đánh giá cao ở `diagram-design`, nhưng chỉ ở mức quality outcome; mọi expression, visual system, bố cục, prose, code và asset phải được tái triển khai độc lập. | LOCKED |
| D-023 | Chủ sở hữu duyệt toàn bộ contract candidate P-02 ngày 2026-08-15, gồm visual-mode names/defaults, canvas/complexity/security limits, surface statuses/evidence rule và benchmark rubric; exact approved bytes/hash được ghi tại G-02 record trong `PLAN.md`. | LOCKED |
| D-024 | `REF-SWIMLANE-CASH-RECEIPTS-001` revision R2 là QA-only benchmark source có hiệu lực; được lưu trong repository evidence và bị loại tuyệt đối khỏi package/release payload. | LOCKED |
| D-025 | Chủ sở hữu duyệt P-06 golden direction gắn với `evidence/p06/P-06-EVIDENCE.md` SHA-256 `3994aa8f45d5061d7b6ce6c43d913a6ac28361ca6a8c08708af88be405a6f4eb`, xác nhận technical/QA review hiện tại là đủ và phê duyệt G-03 `PASS` ngày 2026-08-15; quyết định này không cấp quyền bắt đầu P-07. | LOCKED |
| D-026 | Chủ sở hữu duyệt exact 27 P-12 implementation fixtures, contact sheet và immutable 18-artifact golden set; xác nhận visual communication đạt rubric, technical/QA review hiện tại là đủ và phê duyệt G-04 `PASS` ngày 2026-08-15. Quyết định này không cấp quyền bắt đầu P-09, P-13 hoặc phase khác. | LOCKED |
| D-027 | Chủ sở hữu chọn phương án A cho P-09 ngày 2026-08-15: duyệt ba family full-crest transparent/light-plate/dark-plate với kích thước tối thiểu 64px; 32/48px chỉ QA-only và bị loại khỏi release v1.0.0; không tạo simplified mark cho v1.0.0. Quyết định này không cấp quyền bắt đầu P-10/P-13. | LOCKED |
| D-028 | Chủ sở hữu giải quyết P10-OD-01/P10-OD-02 ngày 2026-08-15: tên kiểm soát chính xác dùng số ít `Tran Ngoc Thien's Skill Commercial Source-Available License 2.0`, cho phép sửa `SKILLS` thành `SKILL` tại cả hai dòng tiêu đề song ngữ của bản lấy từ template mà không sửa phần còn lại; package scope v1.0.0 chỉ chọn light-plate 64px và 400px cho OpenAI plugin và Universal raw skill tại `assets/brand/`, không chọn brand asset cho Claude, các derivative owner-approved còn lại chỉ giữ provenance và không đóng gói v1.0.0. P-13 chỉ được xác minh field host hiện hành, copy đúng byte khai báo, tạo overlay và smoke-test sau khi được cho phép; thay đổi manifest làm G-06 phải duyệt lại. | LOCKED |
| D-029 | Chủ sở hữu phê duyệt P-10 exact candidate `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6` ngày 2026-08-15 ở tư cách owner. Phê duyệt này không thay thế D-018/lawyer sign-off, không tự làm P-10 hoặc G-06 `PASS`, và không cấp quyền bắt đầu P-13. | LOCKED |
| D-030 | Tran Ngoc Thien tự xác nhận là luật sư Việt Nam và, ở tư cách luật sư đồng thời là chủ sở hữu, phê duyệt không điều kiện exact legal release candidate `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6` ngày 2026-08-15. Record này đáp ứng D-018 trong phạm vi bằng chứng dự án dựa trên xác nhận nghề nghiệp rõ ràng của người dùng; danh tính/chứng chỉ hành nghề không được xác minh độc lập. Quyết định làm P-10 đủ điều kiện `passed` nhưng không tự phê duyệt G-06 và không cấp quyền bắt đầu P-13. | LOCKED |
| D-031 | Chủ sở hữu phê duyệt G-06 `PASS` ngày 2026-08-15 cho brand selection đã khóa theo D-027 và exact legal release candidate đã khóa theo D-029/D-030: `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`. Quyết định này đóng G-06 nhưng không tự cấp quyền bắt đầu P-13, không cho phép build ZIP và không phải G-07/release authorization. | LOCKED |
| D-032 | Chủ sở hữu cho phép bắt đầu và chỉ thực hiện P-13 ngày 2026-08-15. Thẩm quyền gồm xác minh schema/install surface chính thức hiện hành, tạo platform overlay cần thiết, sinh và kiểm ba ZIP xác định, checksum, install/smoke-test evidence và hồ sơ G-05; không cho phép bắt đầu P-14, init/commit/tag/push Git, phát hành hoặc thay đổi legal/brand bytes đã qua G-06. | LOCKED |
| D-033 | Chủ sở hữu xác nhận technical/QA review hiện tại là đủ và phê duyệt G-05 `PASS` ngày 2026-08-16 cho exact package candidate `TCD-PACKAGES-1.0.0-RC1`: Claude SHA-256 `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9`, OpenAI SHA-256 `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c`, Universal SHA-256 `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f`. Quyết định này đóng G-05 nhưng không cấp quyền bắt đầu P-14, không phải G-07/release authorization và không cho phép init/commit/tag/push Git hoặc phát hành. | LOCKED |
| D-034 | Chủ sở hữu cho phép bắt đầu P-14 ngày 2026-08-16. Thẩm quyền hiện tại gồm freeze và đối chiếu exact release candidate, kiểm tra read-only repository/remote/private target, lập release-approval packet, residual-risk record và hồ sơ G-07; chưa phải phê duyệt ba ZIP/toàn bộ release candidate, chưa phải G-07 `PASS` hoặc release authorization, và chưa cho phép init/commit/tag/push Git hay tạo release. | LOCKED |
| D-035 | Chủ sở hữu phê duyệt ngày 2026-08-16 toàn bộ exact release candidate `TCD-RELEASE-1.0.0-RC1` và ba ZIP đã freeze theo D-033; chấp nhận rõ hai Medium residual risks `P14-R01` và `P14-R02`; chọn publication scope A — full private audit repository, loại `.DS_Store`, cache và transient file; đồng thời xác nhận target URL `https://github.com/thiendeptrainhat/Thien-Skill-Creative-Diagram`. Quyết định này chưa tự chứng minh target tồn tại/private, chưa giải quyết xung đột nếu audit corpus chứa đường dẫn máy cá nhân bị cấm trong release payload, chưa phải G-07 `PASS` hoặc release authorization và chưa cho phép init/commit/tag/push Git hay tạo release. | LOCKED |
| D-036 | Chủ sở hữu chọn phương án A1 ngày 2026-08-16: tạo publication mirror xác định cho scope A, giữ nguyên local audit corpus, thay riêng đường dẫn máy cá nhân bằng placeholder ổn định, ghi repo-relative file identity cùng before/after hash mà không ghi lại giá trị đường dẫn nhạy cảm, giữ nguyên regex/fixture bảo mật tổng quát và chạy verification/re-binding bị ảnh hưởng. Quyết định này cho phép chuẩn bị sanitized mirror và evidence trong P-14 nhưng chưa phải G-07 `PASS` hoặc release authorization, và không cho phép init/commit/tag/push Git hay tạo release. | LOCKED |
| D-037 | Chủ sở hữu phê duyệt G-07 `PASS` ngày 2026-08-16 và cấp release authorization cụ thể cho sanitized publication mirror: init Git, commit vào `main`, tạo tag `v1.0.0`, push `main` và tag tới private repository đã xác minh, rồi tạo GitHub Release `v1.0.0` kèm đúng ba ZIP đã freeze và `SHA256SUMS.txt`. Repository được push phải có README hướng dẫn cài đặt chi tiết và thông tin license. Quyết định này không cho phép đổi ba ZIP, legal/brand bytes, target, visibility, version/tag hoặc bắt đầu P-15; thao tác remote chỉ được thực hiện qua phiên GitHub đã xác thực hợp lệ. | LOCKED |
| D-038 | P-14 release execution hoàn tất ngày 2026-08-16 theo D-037: sanitized mirror được commit tại `1aae0a0073dd685af1341554f27554eb44c42f63`, push lên `main`; annotated tag `v1.0.0` object `c91194cb454e7e04eafd2636f98a87a6b32fe24f` peel về đúng release commit; GitHub Release `v1.0.0` được tạo ở private target với ba ZIP và `SHA256SUMS.txt`, và GitHub-reported digest/size khớp exact candidate. Audit-closure commit sau release chỉ cập nhật governance/evidence trên `main`, không di chuyển tag hoặc thay release asset. P-15 vẫn chưa được phép. | LOCKED |
| D-039 | Chủ sở hữu cho phép P-15 publication patch ngày 2026-08-16: tạo `LICENSE.md` tại root repository với nội dung byte-identical `thien-skill-creative-diagram/LICENSE.md`, hiển thị logo derivative 400px đã duyệt trong root `README.md`, cập nhật governance/evidence, commit và push trực tiếp `main`. Không được đổi ba ZIP, tag hoặc GitHub Release `v1.0.0`, version, legal wording hay brand bytes; không rebuild package. | LOCKED |
| D-040 | P-15 publication patch hoàn tất ngày 2026-08-16 theo D-039: publication commit `9fdf15a5e140b5a366a415b59195de23be77ea3a` đã push lên private `main`; GitHub nhận diện root `LICENSE.md` là custom license `Other` với SPDX `NOASSERTION`, README tham chiếu đúng logo derivative 400px đã duyệt, và root/canonical license byte-identical. Tag object `c91194cb454e7e04eafd2636f98a87a6b32fe24f`, GitHub Release `v1.0.0` và bốn Release asset digest không đổi; không rebuild package hoặc thay version/legal wording/brand bytes. | LOCKED |
| D-041 | Chủ sở hữu quyết định giữ nguyên display name `Thien-Skill-Creative-Diagram` và technical ID/folder/plugin ID `thien-skill-creative-diagram` cho workstream maintenance mới. | LOCKED |
| D-042 | Chủ sở hữu khóa target maintenance version là `1.5.0`; release/tag/package `v1.0.0` đã phát hành phải được bảo toàn nguyên trạng trừ khi có authorization riêng. | LOCKED |
| D-043 | Chủ sở hữu đưa toàn bộ upstream visual delta đã phân tích vào scope target `1.5.0`: 12 canonical type bổ sung để đạt 39, cùng bốn capability `Dumbbell`, `Slopegraph`, `Ridgeline`, `Bubble`; bốn capability này không làm tăng canonical count. | LOCKED |
| D-044 | Chủ sở hữu chọn mô hình gallery được khuyến nghị: HTML gallery là QA-only evidence trong dự án, dùng để duyệt visual quality trước và không vào package ở scope hiện tại; toàn bộ expression phải là independent reimplementation theo D-006/D-022. | LOCKED |
| D-045 | Chủ sở hữu khóa giới hạn hiện tại của target `1.5.0` ở source/gallery qua P-19; chưa cho phép package build/rebuild, commit, push, tag, thay Release hoặc phát hành `v1.5.0`. | LOCKED |
| D-046 | Ngày 2026-08-22, chủ sở hữu chỉ cho phép triển khai P-16 — Upstream delta & contract lock. Quyền này chỉ bao gồm snapshot/delta evidence và governance/contract candidate để owner xét G-01/G-02; không cấp quyền bắt đầu P-17, sửa runtime/gallery, build, commit, push, tag hoặc release. | LOCKED |
| D-047 | Ngày 2026-08-23, chủ sở hữu Tran Ngoc Thien phê duyệt `G-01@1.5.0` và `G-02@1.5.0` `PASS` cho exact P-16 snapshot/evidence/contract candidate sau independent agent re-review không còn finding, đồng thời cho phép đóng P-16. Phê duyệt G-02 bao gồm exact scope 39 canonical type + bốn capability, exact 12-family pilot/rubric và QA-only three-mode gallery workflow. Quyết định này không cho phép bắt đầu P-17/P-18/P-19, không cho phép sửa runtime/gallery, build/rebuild package, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-048 | Ngày 2026-08-23, chủ sở hữu cho phép triển khai riêng P-17 — Semantic expansion to 39 types. Thẩm quyền gồm cập nhật canonical source/taxonomy/router/IR/schema/reference/validator/test cho 39 canonical type và bốn capability `Dumbbell`, `Slopegraph`, `Ridgeline`, `Bubble` theo exact contract G-02@1.5.0 đã khóa; không cho phép bắt đầu P-18/P-19, tạo gallery HTML, build/rebuild package, sửa `dist/`, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-049 | Ngày 2026-08-23, chủ sở hữu cho phép triển khai riêng P-18 — Visual vNext pilot & gallery approval. Thẩm quyền gồm visual-system/pilot-renderer source, exact 12-family × ba-mode = 36 standalone self-contained HTML cùng `index.html`/contact sheet QA-only dưới `evidence/p18/`, provenance/manifest/test và render–inspect–revise–verify theo contract đã duyệt tại D-047; không cho phép bắt đầu P-19, build/rebuild package, sửa `dist/`, commit, push, tag, thay Release hoặc phát hành. Owner visual approval của exact rendered manifest vẫn là gate riêng trước P-19. | LOCKED |
| D-050 | Ngày 2026-08-23, chủ sở hữu phê duyệt giải pháp remediation P-18 và cho phép triển khai tuần tự P-18R0→P-18R1→P-18R2→P-18R3. Exact 12-family × ba-mode vẫn giữ nguyên; visual acceptance bổ sung nằm tại `evidence/p18/VISUAL-CRAFT-RUBRIC.md`, gồm semantic field + type legend chiếm ít nhất 75% chiều cao artboard, không duplicate title/evidence rail trong SVG, cỡ chữ tối thiểu, geometry/connector clearance và bridge/hop, silhouette/blind test, five-second focal-path test, visual-craft gate độc lập ≥85/100 không dimension nào dưới 4/5, đồng thời giữ toàn bộ semantic/quantitative/security gate hiện hữu. So sánh upstream chỉ bằng rubric trừu tượng, không pixel similarity hoặc tái sử dụng expression. Quyết định này supersede candidate P-18 đầu tiên cho mục đích owner review nhưng không tự duyệt G-03@1.5.0, không cho phép P-19, build/rebuild package, sửa `dist/`, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-051 | Ngày 2026-08-24, chủ sở hữu xác định frozen replacement `P18-PILOT-1.5.0-VISUAL-CRAFT-REPLACEMENT` vẫn chưa đạt visual quality mong muốn; candidate này bị supersede cho mọi owner-approval/golden purpose nhưng được giữ nguyên như historical evidence. Chủ sở hữu đồng ý giải pháp structural remediation cho toàn bộ 39 canonical type + bốn capability: canonical visual kernel, 14 layout engine, family-specific silhouette/interface, real-font measurement, intrinsic node sizing, obstacle-aware connector routing và sequence P-18R4→P-18R5→P-18R6→P-19A→P-19B→P-19C. Quyết định đồng ý sequence không tự authorize subphase kế tiếp. | LOCKED |
| D-052 | Ngày 2026-08-24, chủ sở hữu khóa default typography direction giống quality profile đã nêu: Instrument Serif cho display/editorial, Geist cho human-facing sans và Geist Mono cho technical metadata; khi người dùng chọn font khác, explicit user choice luôn ưu tiên theo role trước skill default. Font phải resolve/load/measure trước layout; không silent substitution/mixing khi thiếu font hoặc Vietnamese glyph; thay font phải lặp sizing/layout/routing/QA. Font asset nếu dùng sau này phải được lấy độc lập từ official publisher với license/provenance, không reuse upstream font file. | LOCKED |
| D-053 | Ngày 2026-08-24, chủ sở hữu cho phép triển khai riêng P-18R4 — Contract và visual foundation relock. Thẩm quyền gồm tạo contract/machine binding/evidence P-18R4 và cập nhật governance/handoff nhất quán; không cho phép triển khai renderer/kernel/anchor/gallery P-18R5/P-18R6, không cho phép P-19A/B/C, build/rebuild package, sửa `dist/`, refresh publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-054 | Ngày 2026-08-24, chủ sở hữu cho phép triển khai riêng P-18R5 — Master visual kernel + Swimlane anchor. Thẩm quyền gồm canonical visual-kernel source QA-only mới, đúng một Swimlane `neutral-light` anchor ở HTML/SVG, render/browser/semantic/typography/geometry/accessibility/security/provenance evidence và đồng bộ governance/handoff; phải dừng để owner review. Không cho phép P-18R6, P-19A/B/C, sửa candidate P-18R3 đã bị từ chối, build/rebuild package, sửa `dist/`, refresh publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-055 | Ngày 2026-08-24, sau review exact P-18R5 candidate đầu tiên, chủ sở hữu xác định hai blocking visual finding và cho phép remediation ngay trong P-18R5: crossing bất khả tránh phải dùng bridge/hop thật, không tạo bubble/junction giả; node phải mở rộng theo measured title và local horizontal budget trước khi wrap, tránh orphan line khi còn chỗ. Remediation phải tái sinh đúng một Swimlane `neutral-light` anchor, lặp toàn bộ QA/freeze và dừng để owner review. Không cho phép P-18R6/P-19, runtime/package/`dist`/publication/Git/Release mutation. | LOCKED |
| D-056 | Ngày 2026-08-24, chủ sở hữu xác nhận review-02 đã đạt các phần khác nhưng crossing vẫn không đạt yêu cầu. Review-02 được bảo toàn như historical evidence; remediation tiếp tục trong đúng P-18R5/D-055. Technical acceptance được làm rõ: bridge/hop phải là geometry liên tục của chính connector, không phải straight path cộng mask/overlay giả; crossing trên cùng segment phải có khoảng tách thị giác, nếu quá sát router phải tái phân corridor thay vì tạo double-hump/compound wave. Phải tái sinh đúng một Swimlane `neutral-light` review-03, lặp QA/freeze và dừng để owner review; không mở P-18R6/P-19 hoặc runtime/package/`dist`/publication/Git/Release mutation. | LOCKED |
| D-057 | Ngày 2026-08-24, chủ sở hữu xác nhận review-03 đã đạt silhouette crossing nhưng hai tiếp điểm giữa vòng cung và đoạn thẳng vẫn có hairline gap, đồng thời yêu cầu nối liền mạch. Review-03 được bảo toàn như historical evidence. Remediation tiếp tục đúng một Swimlane `neutral-light` trong P-18R5: route-integrated hop và repaint phải dùng cùng một geometry; underlay chỉ được che crown trung tâm, không được xóa vai nối; phải có assertion structural/browser cho join continuity, tái sinh/freeze review-04 và dừng để owner review. Không mở P-18R6/P-19 hoặc runtime/package/`dist`/publication/Git/Release mutation. | LOCKED |
| D-058 | Ngày 2026-08-24, chủ sở hữu Tran Ngoc Thien phê duyệt exact frozen review-04 `P18R5-MASTER-KERNEL-SWIMLANE-ANCHOR-REVIEW-04-1.5.0`, manifest SHA-256 `7725a03c82c370f6d9bb984b0d6e50c585efb07529a47f2c3dfad45877c1cca8`, bao gồm kết quả crossing/hop và straight-to-hop continuity đã remediate theo D-055–D-057. Quyết định này đóng P-18R5 ở trạng thái `passed` và khóa candidate làm Swimlane anchor/visual direction của P-18R5. Đây không phải phê duyệt `G-03@1.5.0`, không authorize P-18R6/P-19A/B/C, không cho phép sửa frozen candidate, build/rebuild package, sửa `dist/`, refresh publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-059 | Ngày 2026-08-24, chủ sở hữu cho phép triển khai riêng P-18R6 — 14-engine `neutral-light` anchor gallery. Thẩm quyền gồm source QA-only mới dưới `evidence/p18/r6/`, đúng 14 standalone HTML/SVG anchor tương ứng đúng 14 layout engine của P-18R4, index/contact sheet, semantic/quantitative/typography/geometry/accessibility/security/browser/visual-craft/blind-recognition/five-second evidence, provenance và manifest; phải bảo toàn byte-level exact frozen P-18R5 review-04 và dừng để owner review cùng quyết định `G-03@1.5.0` riêng. Không cho phép P-19A/B/C, sửa runtime/package hoặc candidate lịch sử, build/rebuild package, sửa `dist/`, refresh publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-060 | Ngày 2026-08-24, chủ sở hữu yêu cầu remediation exact P-18R6 review-01 và cho phép sửa năm nhóm geometry trong đúng P-18R6: (1) diagram 01–03 đổi broad curved connector thành rounded orthogonal routing theo visual grammar của owner-approved Swimlane; (2) diagram 04 dùng route-integrated shared-geometry bridge/hop cùng continuity contract như Swimlane; (3) diagram 05 làm hai nhánh `NO` bằng chiều rộng và đưa `NO` từ `Control effective?` trở lại `Validate evidence`; (4) diagram 07 đặt `Contract v1` và `Anchor review` hoàn toàn phía trên timeline/leader, không đè line; (5) diagram 09 nối mọi child connector vào đúng node center và ưu tiên đường thẳng. Review-01 manifest SHA-256 `fcdec11e49a00d89d82a3fafaba7cae2ac8e7c58908fa76cc2fa6eba383aad37` phải được bảo toàn như historical evidence; remediation phải tạo/freeze review-02, lặp QA/evidence và dừng để owner review. Không mở P-19 hoặc runtime/package/`dist`/publication/Git/Release mutation. | LOCKED |
| D-061 | Ngày 2026-08-24, chủ sở hữu xác định dependency diagram 04 của exact P-18R6 review-02 vẫn còn crossing chưa có bridge/hop đúng, corridor height giữa các rank chưa cân và chart đang trộn góc 90° sắc với bo cong. Review-02 manifest SHA-256 `2f9c7aad3a2dd9d43d575ddfb864effa915df909134d5401dbb075ed6ea2cf7b` phải được bảo toàn historical byte-bound. Remediation review-03 trong đúng P-18R6 phải: loại crossing tránh được; mọi crossing còn lại dùng route-integrated shared-geometry hop với crown-only underlay và zero join gap; chuẩn hóa khoảng cách rank và corridor ladder cân đối; dùng một `connector_corner_style` duy nhất cho toàn chart, mặc định `rounded`, còn explicit user choice `straight` phải thắng default và làm mọi góc 90° trong chart thành góc thẳng. Phải lặp QA/render/freeze và dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-062 | Ngày 2026-08-24, chủ sở hữu xác nhận explicit `straight` corner style được áp dụng cho các diagram khác khi người dùng yêu cầu và yêu cầu remediation diagram 01–03 trong đúng P-18R6. Review-03 manifest SHA-256 `572de899399755268d63fa5cb49c598a6ee6c5d509418ed8d07484a750c62e54` phải được bảo toàn historical byte-bound. Review-04 phải: (1) mở rộng chart-level `connector_corner_style` cho diagram 01–03 cùng diagram 04, vẫn mặc định `rounded`, còn explicit user choice `straight` phải serialize mọi góc 90° tương ứng thành góc thẳng mà không trộn style trong cùng chart; (2) bảo đảm mọi direct child node/subcontainer của diagram 01–03 nằm trọn trong parent với minimum padding được khai báo; (3) căn giữa cả cụm child theo cả hai trục của parent, đồng thời row child dùng cùng center-y, column child dùng cùng center-x và single child trùng center parent; (4) kiểm các invariant này bằng machine-readable geometry metadata và automated QA trước khi render/freeze. Phải dừng để owner review; không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-063 | Ngày 2026-08-24, chủ sở hữu yêu cầu remediation diagram 10 trong đúng P-18R6. Review-04 manifest SHA-256 `6be1aa8894cf62d252c9cd890f14b4e825497b811046df57ccb301e84054f185` phải được bảo toàn historical byte-bound. Review-05 phải: (1) tạo đúng một outer triangular silhouette liên tục, không còn stepped shoulder hoặc gap giữa các layer; (2) apex `Flagship decision` là tam giác thật với đúng ba đỉnh phân biệt và không có top edge; (3) ba supporting layer là hình thang, các cạnh ngoài nằm trên cùng hai side-line của outer triangle và hai layer kề nhau dùng chung chính xác toàn bộ biên ngang; (4) layer fill không tạo double-stroke tại shared boundary; (5) trục/mũi tên leverage bên trái không giao hoặc bị bất kỳ polygon nào đè lên và có minimum horizontal clearance được khai báo, kiểm bằng machine-readable geometry metadata và automated QA. So sánh reference chỉ ở mức rubric/silhouette trừu tượng, không copy pixel/code/CSS/SVG/template. Phải render/freeze review-05 rồi dừng để owner review; không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-064 | Ngày 2026-08-24, chủ sở hữu xác nhận review-05 đã cải thiện nhưng yêu cầu tiếp tục remediation diagram 10 trong đúng P-18R6. Review-05 manifest SHA-256 `20b8f257b44d7f6c9fc0cbf7eed9b710778bdcebb142978b8f47aad61eab393b` phải được bảo toàn historical byte-bound. Review-06 phải: (1) đo real-font bounding box của mọi title/metadata trong bốn layer và bảo đảm toàn bộ bbox nằm trong owning polygon với minimum inset tối thiểu 8px, đặc biệt `Flagship decision` không được vượt hai cạnh chéo của apex; (2) ưu tiên tăng local apex height/reposition text trước shrink hoặc wrap; font-size contract hiện hành không được giảm; (3) thêm đúng một right-side annotation rail để chứng minh khả năng thêm ghi chú, gồm `THE APEX` và cadence note cho ba supporting layer; cadence phải khớp semantic hiện có (`quarterly ≈4/yr`, `monthly ≈12/yr`, `daily/workdays ≈240/yr`), không sao chép nguyên scenario/prose upstream; (4) annotation phải nằm ngoài polygon, trong canvas, có clearance đo được và không chạm/đè layer text hoặc divider; (5) kiểm tất cả bằng machine-readable geometry metadata và automated QA. Phải render/freeze review-06 rồi dừng để owner review; không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-065 | Ngày 2026-08-24, chủ sở hữu xác nhận review-06 đã đạt các yêu cầu khác nhưng yêu cầu kiểm tra và, nếu không đều, cân lại khoảng cách thị giác giữa bốn right-side note với hình tháp. Đo geometry xác nhận khoảng cách hiện tại tại tâm dọc real-font bbox lần lượt là `140.27px`, `82.63px`, `79.17px`, `72.45px`, nên review-06 manifest SHA-256 `b1f934b5542079a93763b5ac0237dbdc2871dc6f97e8e4ea14adeb05536f844d` phải được bảo toàn historical byte-bound và review-07 được phép remediation riêng diagram 10. Review-07 phải: (1) định nghĩa một `visual annotation gap` chung là khoảng ngang từ cạnh phải outer triangle đến mép trái bbox tại tâm dọc bbox; (2) tính x của cả bốn note từ geometry với target đúng `72px`, tolerance automated tối đa `0.01px`, không dùng bốn offset độc lập; (3) giữ nguyên note text/semantic cadence, text containment, canvas fit và minimum polygon clearance của D-064; (4) render/freeze review-07 rồi dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-066 | Ngày 2026-08-24, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 cho diagram 06 và 11. Exact review-07 manifest SHA-256 `da2d8840b8bf009c54c10b72ccc7e9fbd2aedf6422acd2c822548f63a29b5290` phải được bảo toàn historical byte-bound. Review-08 phải: (1) bổ sung phase lớn đầu tiên `CHUẨN BỊ` trước `NHẬN BỘ` trong diagram 06 để sáu workflow step có đủ sáu major phase theo thứ tự `CHUẨN BỊ`, `NHẬN BỘ`, `PHÂN LOẠI`, `GỬI NGÂN HÀNG`, `CẬP NHẬT NỢ`, `ĐĂNG SỔ`; thay đổi này chỉ là local R6 extension và không được sửa exact owner-approved P-18R5 review-04; (2) căn cùng center-y cho ba entity hàng trên của diagram 11 và cho hai connector ngang đi đúng qua center-y, đồng thời căn ORDER_ITEM và connector dọc theo center-x của ORDER; (3) đo và khóa nội dung mỗi entity với bottom padding tối thiểu 24px, không nhỏ hơn top/side spacing một cách thị giác; (4) đặt toàn bộ bbox của label quan hệ trong inter-node corridor với minimum clearance 8px khỏi cả hai node kề bên, không để `1 · PLACES · N` hay `1 · PAID BY · N` tràn vào ô; (5) thêm machine-readable geometry metadata và automated QA cho phase coverage, centering, endpoint, padding và label corridor. Phải render/freeze review-08 rồi dừng để owner review; không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-067 | Ngày 2026-08-24, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 riêng diagram 12. Exact review-08 manifest SHA-256 `a5e58ccb47ea63b6904e84859aace63fb3f09b2cb3147e4a3a96ce41617eb7ec` phải được bảo toàn historical byte-bound. Review-09 phải thay bốn nhãn trục hiện tại bằng đúng bốn annotation có hướng: `↑ HIGH IMPACT` ngay trên và lệch phải có kiểm soát so với đầu trên trục dọc, `← LOW EFFORT` ngay dưới đầu trái trục ngang, `↓ LOW IMPACT` ngay dưới và lệch phải cùng offset với đầu dưới trục dọc, và `HIGH EFFORT →` ngay dưới đầu phải trục ngang. Nhãn trên/dưới phải dùng cùng fixed x-offset từ trục dọc; nhãn trái/phải phải dùng cùng fixed y-offset dưới trục ngang, lần lượt khóa theo mép trái/phải của field như ảnh tham khảo. Ký hiệu mũi tên là một phần của nhãn và chỉ đúng hướng tăng/giảm tương ứng. Các nhãn phải nằm trong canvas, không chạm line/điểm/quadrant title/legend, giữ cùng typography role và có machine-readable binding cho axis, direction, arrow placement, measured bbox, alignment error/offset và clearance. Scenario, dữ liệu, quadrant titles, focal item và visual system còn lại phải giữ nguyên. Phải render/freeze review-09 rồi dừng để owner review; không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-068 | Ngày 2026-08-25, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 riêng diagram 12: vùng focal coral `DO FIRST` không được có line/outline cam bao quanh. Exact review-09 manifest SHA-256 `d7f7e9653d02b0b156c2aa144643047edb09fb970a5ae07e58f7b1cecbc44703` phải được bảo toàn historical byte-bound. Review-10 phải giữ nguyên nền coral nhạt, trục effort/impact, bốn annotation D-067, quadrant titles, sáu initiative, một focal point `Freeze contract`, legend, typography và mọi geometry khác; chỉ stroke của focal-region rectangle phải là `none`, không được dùng transparent/zero-opacity orange stroke để giả loại bỏ. Phải có machine-readable binding và automated QA xác nhận focal region còn fill nhưng không có stroke, deterministic regeneration và semantic preservation; render/freeze review-10 rồi dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-069 | Ngày 2026-08-25, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 riêng diagram 11. Exact review-10 manifest SHA-256 `9a1fe7282db733c8239a0daf4abddff984c2372bfb6bb82f759de94980adaf84` phải được archive historical byte-bound trước mutation. Review-11 phải: (1) tách `1` và `N` thành hai text element độc lập, mỗi element gắn rõ source/target endpoint và nằm gần đúng node boundary tương ứng; (2) tên quan hệ không chứa cardinality hay separator; `PLACES` và `PAID BY` ưu tiên phía trên connector ngang, `CONTAINS` ưu tiên bên phải connector dọc; (3) mọi measured bbox nằm ngoài node, không đè connector và giữ clearance tối thiểu 8px; (4) giữ nguyên center alignment, exact connector endpoint, entity geometry, bottom padding và semantic facts đã khóa ở D-066; (5) thêm machine-readable relationship/cardinality/placement binding và automated QA, deterministic regeneration, render/freeze review-11 rồi dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-070 | Ngày 2026-08-25, chủ sở hữu xác định placement cardinality của exact P-18R6 review-11 chưa đạt và yêu cầu `1`/`N` phải nằm đè đúng trên connector với khoảng trắng như hình tham khảo trước đó. Exact review-11 manifest SHA-256 `69b93b45fc852b9e9c1405b66fbb40dd10d964fa55f589b65a51984d5b3dccfc` phải được archive historical byte-bound trước mutation. Review-12 riêng diagram 11 phải: (1) giữ mỗi `1`/`N` là endpoint label độc lập và đặt tâm glyph đúng trên trục line ngang/dọc tương ứng; (2) đặt một measured knockout màu canvas, không stroke, phía sau từng glyph với padding 8px dọc connector và 4px vuông góc, clearance tới node tối thiểu 8px; (3) giữ connector là một semantic line duy nhất, không cắt thành hai segment, và khóa paint order connector → knockout → label; (4) giữ `PLACES`/`PAID BY` phía trên line ngang, `CONTAINS` bên phải line dọc cùng toàn bộ D-066 entity/endpoint/padding geometry; (5) static emitted-axis error tối đa 0.06px, browser actual-bbox axis error tối đa 0.75px, deterministic regeneration và automated QA; (6) toàn bộ 13 non-target anchor pair phải byte-identical review-11. Phải render/freeze review-12 rồi dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-071 | Ngày 2026-08-25, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 riêng diagram 14 Sankey. Exact review-12 manifest SHA-256 `90de78337c49f1ee42aae8730bbf072eb8bf679388038041b793f943ddfcafb6` phải được archive historical byte-bound trước mutation. Review-13 phải: (1) dùng một shared quantitative scale để bar height và ribbon thickness cùng biểu diễn giá trị, đồng thời mọi applicable incoming/outgoing node interface phải được ribbon intervals liên tiếp phủ đúng 100% từ top edge đến bottom edge, không gap/overlap và stage/outcome đều reconcile đúng 12,000 phút; (2) đặt title/value của từng bar thành stack căn giữa phía trên bar với measured clearance tối thiểu 12px; (3) dùng bar góc vuông thật, không `rx`, không rounded-corner workaround; (4) giữ nguyên scenario, values, palette, legend và semantic facts; (5) static và browser QA phải kiểm scale, conservation, exact interface tiling, label placement và square-corner serialization; (6) toàn bộ 13 non-target anchor pair phải byte-identical review-12. Phải render/freeze review-13 rồi dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-072 | Ngày 2026-08-25, sau khi xác nhận diagram 14 review-13 đã đạt các yêu cầu D-071, chủ sở hữu yêu cầu các thanh ở trên cùng phải `align top`. Exact review-13 manifest SHA-256 `520c4ad74b944a218a576bdec7f100eb84054e712a066965417961fe97b91324` phải được archive historical byte-bound trước mutation. Review-14 riêng diagram 14 phải: (1) đặt top edge của `Monthly budget`, `Unit tests` và `Passed` cùng exact `y=210px`, với static/browser max spread không quá `0.01px`; (2) chỉ dịch source `Monthly budget` và ba source-side ribbon interval tương ứng cùng `-40px`, không đổi target interval; (3) giữ nguyên shared `0.025px/minute` scale, mọi value/thickness, 100% contiguous interface occupancy, label-above clearance, square-corner bars, conservation, scenario, palette, legend và semantic facts của D-071; (4) toàn bộ 13 non-target anchor pair phải byte-identical review-13; (5) render/inspect, static/browser QA, regression, manifest verification và deterministic regeneration phải `PASS`, rồi freeze review-14 và dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-073 | Ngày 2026-08-25, chủ sở hữu yêu cầu kiểm tra và remediation tiếp theo trong đúng P-18R6 riêng diagrams 04, 08 và 09 vì các line mờ đang quá sát hoặc bị ô/icon đè lên, dễ gây hiểu nhầm. Exact review-14 manifest SHA-256 `9e88febc31f895aaada5385f2b9fc3a3384b8ff607831ac4ad9e302165b36637` phải được archive historical byte-bound trước mutation. Review-15 phải: (1) coi pale horizontal line là semantic band boundary — rank 0/1/2/3 của diagram 04, action/thought/emotion của diagram 08, command/domains/pods của diagram 09 — không phải row centerline; (2) dịch boundary và member để bbox center-y của mọi card/icon trùng band midpoint, static tolerance tối đa `0.01px`, browser actual-bbox tolerance tối đa `0.75px`; (3) không separator nào được giao, chạy sau hoặc bị member đè lên; canonical minimum member-to-separator clearance lần lượt là `22px`, `27px`, `58px`; (4) connector chỉ được cắt separator để biểu diễn quan hệ cross-band thật và không được trùng separator như một route rail gây hiểu nhầm; diagram 04 phải giữ route-integrated continuous hop và one-chart corner policy; (5) toàn bộ 11 non-target anchor HTML/SVG pair phải byte-identical review-14; (6) render/inspect, static/browser QA, regression, manifest verification và deterministic regeneration phải `PASS`, rồi freeze review-15 và dừng để owner review. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-074 | Ngày 2026-08-25, chủ sở hữu yêu cầu remediation tiếp theo trong đúng P-18R6 riêng diagram 13: bỏ dấu mũi tên hướng xuống tại origin được khoanh trong scatter plot. Exact review-15 manifest SHA-256 `0e2fcddc00a5b993fd34b4376c32e10a1ca0dd64013202e58ac35df801798a5b` phải được archive historical byte-bound trước mutation. Review-16 phải: (1) giữ hai trục định lượng là plain axis, không có `marker-start`, `marker-mid` hoặc `marker-end` ở serialized SVG hay computed browser style; (2) giữ nguyên origin, zero/tick labels, scales, grid, point/bubble geometry, direct labels, focal recommendation, legend và accessible quantitative data; (3) chỉ diagram 13 HTML/SVG được khác review-15, toàn bộ 13 non-target anchor pair phải byte-identical; (4) deterministic regeneration, static/browser QA, canonical raster inspection, full regression và manifest/archive verification phải `PASS`; (5) freeze review-16 rồi dừng để owner/independent review, giữ `G-03@1.5.0` `NOT-EVALUATED`. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-075 | Ngày 2026-08-25, chủ sở hữu Tran Ngoc Thien xác nhận “tất cả 14 diagram đã đạt yêu cầu”, qua đó phê duyệt owner visual review cho exact frozen candidate `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-16-1.5.0`, manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835`. Phê duyệt này khóa visual direction của cả 14 engine anchor và đóng riêng owner-review condition; không tự thay thế masked blind recognition, five-second takeaway hoặc independent visual-craft gate đang `PENDING`, không tự làm P-18 `passed`, không phải quyết định `G-03@1.5.0`, không authorize P-19, runtime/package/`dist`/publication/Git/Release mutation và không cho phép sửa exact frozen candidate. | LOCKED |
| D-076 | Ngày 2026-08-27, chủ sở hữu cho phép remediation đúng hai finding five-second của independent review trên exact review-16 để tạo candidate `review-17`, rồi giao exact manifest mới cho agent độc lập review lại. Review-16 manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835` phải được archive và kiểm byte-bound trước mutation. Phạm vi thay đổi chỉ gồm diagram 09 hierarchy và diagram 14 Sankey: (1) hierarchy giữ nguyên một root, bốn domain và năm specialist pod nhưng phải hiển thị trực tiếp count/hierarchy `1 FRONT DOOR`, `4 DOMAINS`, `5 SPECIALIST PODS` để takeaway không thể bị đếm nhầm; (2) Sankey giữ nguyên toàn bộ value, scale, node/ribbon geometry, conservation và 100% interface occupancy, nhưng tăng focal contrast của đúng ribbon `unit-flaked` và thêm direct focal annotation `FLAKED RERUNS · 1,000 / 12,000 MIN · 8.3% OF BUDGET` để exception được nhận ra trong năm giây; (3) thêm machine-readable binding cùng static/browser QA; (4) 12 non-target anchor pair phải byte-identical review-16; (5) deterministic regeneration, render inspection, static/browser QA, regression, manifest/archive verification phải `PASS` trước khi freeze review-17; (6) independent agent phải review exact review-17 theo thứ tự masked recognition trước mapping, five-second takeaway và visual-craft rubric độc lập. Hai advisory không blocking về mixed-language `lang` và mobile scale không thuộc remediation này. Không mở P-19 hoặc sửa runtime/package/`dist`/publication/Git/Release. | LOCKED |
| D-077 | Ngày 2026-08-27, chủ sở hữu Tran Ngoc Thien phê duyệt exact frozen candidate `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`, sau khi independent review đạt exactness `75/75`, masked recognition/five-second `14/14`, visual-craft `93/100` với minimum dimension `4/5` và aggregate `PASS`. Quyết định này phê duyệt `G-03@1.5.0 PASS` và đóng P-18 ở trạng thái `passed`. Chủ sở hữu chỉ rõ “Chưa triển khai P-19”; do đó P-19 giữ `not-started` và unauthorized. Không sửa exact frozen review-17, không mở runtime/package/`dist`/publication/Git/Release, build, commit, push, tag hoặc phát hành. | LOCKED |
| D-078 | Ngày 2026-08-27, chủ sở hữu chỉ dẫn rõ ràng “triển khai P-19A”, qua đó authorize riêng P-19A — 39+4 type/capability adapters trên exact P-18R4/P-18R5/P-18R6 foundation đã duyệt. Thẩm quyền gồm canonical adapter source/reference/test, evidence/provenance/manifest và đồng bộ governance/handoff. P-19A phải tạo đúng 39 canonical adapter + bốn capability adapter, map đúng 14 engine, giữ unique family-specific silhouette và fail-closed trước render; không emit HTML/SVG, derive ba mode, tạo gallery 129 file hoặc mở P-19B/P-19C. P-19A hoàn tất với focused `14/14 PASS`, full regression `162/162 PASS`, zero HTML/SVG/CSS và exact P-18R5/P-18R6 manifest cùng `dist/` giữ nguyên. P-19 chuyển `in-progress`, P-19A `passed`; P-19B/P-19C vẫn `not-started` và unauthorized. Không build/rebuild package, sửa `dist/`/publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-079 | Ngày 2026-08-27, chủ sở hữu chỉ dẫn rõ ràng “triển khai P-19B — three-mode derivation và exact 129 HTML”, qua đó authorize riêng P-19B trên exact passed P-19A candidate. Thẩm quyền gồm canonical `gallery_renderer_v15.py`, generated renderer registry, focused tests, đúng `39×3=117` canonical + `4×3=12` capability standalone HTML, một `index.html` contact sheet không tính specimen, 43 local preview SVG, inventory/manifest, static/browser evidence, provenance và đồng bộ governance/handoff. Mọi specimen phải scriptless, network-independent, machine-labelled, có named inline SVG và alternative semantic-ID table; geometry/IR phải giữ nguyên qua ba mode. P-19B hoàn tất với focused unit `11/11 PASS`, static `22/22 PASS`, desktop browser `129/129 PASS`, mobile engine-mode matrix `42/42 PASS`, contact sheet `43` card/`129` link/zero console finding, và full regression `173/173 PASS`. P-19B chuyển `passed`; P-19C vẫn `not-started` và unauthorized; `G-04@1.5.0` vẫn `NOT-EVALUATED`. Không thực hiện P-19C full QA/freeze/masked/owner review, build/rebuild package, sửa `dist/`/publication mirror, commit, push, tag, thay Release hoặc phát hành. | LOCKED |
| D-080 | Ngày 2026-08-27, chủ sở hữu xác định P-19 đang đi sai hướng thiết kế và yêu cầu phải kế thừa phong cách P-18 đã duyệt. Exact P-19B candidate đầu `P19B-THREE-MODE-EXACT-129-HTML-1.5.0` với gallery/plan/source manifest lần lượt `ed6a14521a1277143bece89deac732cec607a9c5d1738d593e52498191a3b106`, `59edd733dc180d8274a31ab91bc5f89b3450fefe9dc80c2101aa2ebee204b40f`, `44cdbe31b7aa715ff88d617274cf0e49cd6c9eb1aac8cb11fa46ce753fa3188c` phải được giữ byte-bound làm historical technical evidence nhưng bị supersede cho owner-approval/golden purpose. D-080 authorize P-19B remediation candidate kế nhiệm: kế thừa trực tiếp exact P-18R6 review-17 manifest `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`; neutral-light giữ visual grammar đã duyệt, neutral-dark/editorial derive bằng semantic roles mà không đổi geometry/IR; tái sinh đúng 129 standalone HTML, 43 preview và contact sheet; thêm automated inheritance/drift assertions, static/browser/regression evidence và dừng để owner review. P-19B trở lại `in-progress`; P-19C vẫn `not-started`/unauthorized, `G-04@1.5.0` vẫn `NOT-EVALUATED`; không sửa frozen P-18/P-19A, package, `dist/`, publication mirror, Git, Release hoặc phát hành. | LOCKED |

| D-081 | Ngày 2026-08-27, chủ sở hữu yêu cầu sửa hai lỗi của P-19B: `dp-integration` phải có ô API nằm trọn, căn giữa trong ô nền ngoài; `swimlane` phải có connector liền mạch qua góc bo hoặc góc thẳng 90°. Thẩm quyền giới hạn ở P-19B remediation review-02: archive byte-bound exact review-01 trước mutation; sửa canonical renderer theo nguyên tắc containment/centering và continuous-path, kiểm cả ba mode cùng rounded/straight geometry, thêm regression/mutation assertions và cập nhật gallery/trang đối chiếu/evidence/handoff. Giữ nguyên dữ liệu, visual grammar P-18 và artwork của 41 type/capability còn lại; mọi thay đổi metadata candidate phải minh bạch. Không sửa frozen P-18/P-19A hoặc archived candidate, không mở P-19C, package/`dist`/publication/Git/Release; owner approval vẫn là quyết định riêng. | LOCKED |

| D-082 | Ngày 2026-08-29, sau yêu cầu Gantt theo hình tham khảo, chủ sở hữu trả lời “đồng ý” cho đề xuất tạo riêng dữ liệu minh họa gồm 3 giai đoạn, 6 công việc và 1 gate trên 3 tháng. Cho phép P-19B review-03 sửa riêng Gantt: lịch tháng phía trên, nhãn trái, vùng giai đoạn bao trọn hàng, thanh công việc trung tính và gate cam, legend tương ứng; tự viết dữ liệu/code, dùng tham khảo ở mức nguyên tắc, giữ visual grammar P-18. Tính geometry từ timestamp trên một thang thời gian chung, giữ timezone và exact-date alternative; gate minh họa là cửa sổ duyệt có thời lượng được khai báo. Archive exact review-02 trước mutation; không sửa minimal fixture/frozen P-19A; chứng minh ba mode cùng geometry và các diagram khác giữ nguyên ngoài metadata candidate; tái sinh exact 129 HTML/trang đối chiếu/evidence/handoff. Không mở P-19C, không sửa P-18/history/package/dist/publication/Git/Release; đây không phải owner approval của candidate mới. | LOCKED |

| D-083 | Ngày 2026-08-29, chủ sở hữu yêu cầu loop-flywheel theo hình tham khảo và xác nhận “đồng ý, làm đi” cho bộ dữ liệu minh họa mới 6 bước + 1 ô “Tri thức chung”, áp dụng cả ba mode và giữ phong cách P-18. Cho phép P-19B review-04 sửa riêng loop-flywheel: sáu ô chữ nhật bo nhẹ trên vòng, mũi tên cong liên tục theo chiều kim đồng hồ, shared-state nền đậm ở giữa (không phải bước thứ bảy), sáu nhánh nét đứt vào trung tâm và một bước quyết định cam; dữ liệu/code được viết độc lập. Giữ cycle order/closure và contribution semantics khai báo trong dữ liệu, bảo đảm card/connector/text clearance; không tự suy diễn quan hệ từ bố cục. Archive exact review-03 trước mutation, giữ Gantt và diagram khác ngoài metadata candidate; tái sinh exact 129 HTML/trang đối chiếu/evidence/handoff và kiểm ba mode. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; approval kết quả vẫn phải riêng. | LOCKED |

| D-084 | Ngày 2026-08-29, chủ sở hữu chỉ dẫn “bỏ sankey P-19,lấy sankey P-18”. Cho phép rút Sankey P-19 khỏi gallery hiện hành và dùng trực tiếp exact Sankey thuộc P-18R6 review-17 đã được D-077 duyệt; không vẽ lại, đổi dữ liệu hoặc sửa frozen P-18. Review-04 phải được bảo toàn; bản triển khai thay thế chưa hoàn tất không được xem là approved candidate. Không mở P-19C, package/dist/publication/Git/Release. | LOCKED |

| D-085 | Ngày 2026-08-29, chủ sở hữu mở rộng D-084: các loại `architecture`, `data-flow`, `deployment`, `dependency-graph`, `flowchart`, `swimlane`, `timeline`, `user-journey`, `org-chart`, `pyramid-funnel`, `database-schema`, `quadrant`, `scatter-plot` đã có trong P-18 thì bỏ khỏi P-19. Đây là thay đổi phạm vi gallery, không xóa năng lực/semantic type khỏi source. Cùng Sankey là đúng 14 anchor P-18: giữ nguyên bản gốc neutral-light đã duyệt, bỏ 42 duplicate HTML và 14 preview P-19 khỏi active gallery theo cách có thể khôi phục, generator không tái sinh duplicate. P-19 còn 25 type + bốn capability × ba mode = 87 HTML; gallery/trang đối chiếu dùng 14 P-18 + 87 P-19 = 101 diagram. Không tự derive dark/editorial cho các anchor P-18, không tính một bản light thành bằng chứng ba mode. Giữ nguyên Gantt, loop-flywheel, dp-integration, bốn capability và artwork còn lại; không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release, không tự duyệt candidate/G-04. | LOCKED |

| D-086 | Ngày 2026-08-29, chủ sở hữu yêu cầu Fishbone chi tiết như hình tham khảo và xác nhận “đồng ý” cho đề xuất triển khai dữ liệu minh họa độc lập gồm 5 nhóm × 2 nguyên nhân quanh hệ quả “Hồ sơ xử lý trễ”, áp dụng cả ba mode và giữ phong cách P-18. Cho phép P-19B review-06 sửa riêng Fishbone: một trục nguyên nhân→hệ quả liên tục; năm xương nhóm xen kẽ trên/dưới; mỗi nhóm có đúng hai nhánh nguyên nhân chi tiết chạm xương sở hữu; thẻ hệ quả coral; legend và bảng thay thế mang đủ semantic ID. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép text/code/CSS/SVG/template/asset; dữ liệu và renderer phải tự viết. Archive exact review-05 trước mutation; chứng minh ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 non-target preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval của exact review-06 vẫn là quyết định riêng. | LOCKED |

| D-087 | Ngày 2026-08-29, chủ sở hữu yêu cầu `dp-integration` theo hình tham khảo chi tiết. Cho phép P-19B review-07 sửa riêng dp-integration bằng dữ liệu minh họa độc lập: ba nguồn bên trái, platform boundary ở giữa chứa orchestration rail + kho đối tượng + dịch vụ truy vấn, ba consumer bên phải và hai service band định danh/quan sát phía dưới; mọi component/route/label phải có semantic IR tương ứng. Primary data path dùng coral, control/service route có stroke semantics riêng, mọi route là một continuous subpath và endpoint ở card edge; đủ type-key legend và native alternative table. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép English labels/exact coordinates/icon/CSS/SVG/template/asset. Archive exact review-06 trước mutation; giữ D-086 Fishbone, chứng minh ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 non-target preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval của exact review-07 vẫn là quyết định riêng. | LOCKED |

| D-088 | Ngày 2026-08-29, chủ sở hữu yêu cầu `bar-chart` theo hình tham khảo tám cột. Cho phép P-19B review-08 sửa riêng bar-chart bằng dữ liệu minh họa độc lập: đúng tám sprint theo thứ tự, một series điểm, trục Y tuyến tính 0–120 với zero-baseline, sáu tick 20 điểm, direct value/category labels, một record-high duy nhất và legend. Record-high phải được encode dư thừa bằng coral fill/stroke, value/category label, legend text và trạng thái trong alternative table; trục không có arrow marker. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép exact value/coordinates/CSS/SVG/template/asset. Archive exact review-07 trước mutation; giữ D-086 Fishbone và D-087 dp-integration, chứng minh ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 non-target preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval của exact review-08 vẫn là quyết định riêng. | LOCKED |

| D-089 | Ngày 2026-08-29, chủ sở hữu yêu cầu `dp-security-matrix` sửa theo hình tham khảo. Cho phép P-19B review-09 sửa riêng dp-security-matrix bằng dữ liệu minh họa độc lập: đúng 5 vai trò × 5 thành phần = 25 permission cell, header vai trò kèm group code, row thành phần kèm code, mọi ô ghi trực tiếp một trong `Admin`/`Write`/`Read`/`None`, và đúng một External Partner × BI Read boundary có coral stroke/fill cùng scope text `Dashboard được chia sẻ`. Trạng thái semantic phải trung thực: quyền được cấp dùng `allow`, `None` dùng `deny`; không dùng màu thay thế nhãn chữ. Có legend và alternative table đủ 25 giao điểm. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép English prose/exact coordinates/CSS/SVG/template/asset. Archive exact review-08 trước mutation; giữ D-086–D-088, chứng minh ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 non-target preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval của exact review-09 vẫn là quyết định riêng. | LOCKED |
| D-090 | Ngày 2026-08-29, chủ sở hữu yêu cầu `er-data-model` giống hình tham khảo. Cho phép P-19B review-10 sửa riêng er-data-model bằng dữ liệu minh họa độc lập: đúng bốn entity Author/Article/Tag/ArticleTag, Article là aggregate root duy nhất, ArticleTag là associative entity duy nhất, đủ 19 field có tên/kiểu, ký hiệu trực tiếp `#` cho primary key và `→` cho foreign key, cùng đúng ba quan hệ một-nhiều có nhãn và cardinality `1`/`N`. Article dùng focal coral restrained; ArticleTag dùng dashed boundary; legend và alternative table phải chứa toàn bộ member/relationship. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép exact prose/coordinates/CSS/SVG/template/asset. Archive exact review-09 trước mutation; giữ D-086–D-089, chứng minh ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 non-target preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval của exact review-10 vẫn là quyết định riêng. | LOCKED |
| D-091 | Ngày 2026-08-29, chủ sở hữu yêu cầu `1` và `N` của er-data-model phải ở vị trí như database-schema P-18. Cho phép P-19B review-11 sửa riêng sáu cardinality label của ba quan hệ D-090: mỗi source `1` và target `N` nằm trực tiếp trên connector axis, sát endpoint entity tương ứng; sau relationship path phải vẽ một canvas-fill/no-stroke knockout riêng rồi mới vẽ glyph, dùng đúng 8px padding dọc đường, 4px vuông góc và tối thiểu 8px tới node như exact P-18R6 review-17 contract. Áp dụng cho đường ngang, rounded-orthogonal và dọc; không đổi entity/field/PK/FK/path/name/legend/table/scenario. Archive exact review-10 trước mutation; chứng minh sáu binding/knockout, ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval review-11 vẫn riêng. | LOCKED |
| D-092 | Ngày 2026-08-29, chủ sở hữu yêu cầu thay riêng P-19 `high-level` theo cấu trúc data-platform chi tiết của ảnh tham chiếu và giữ nguyên connector policy đã duyệt tại P-18: orthogonal một path liên tục, góc 90° mặc định bo tròn hoặc chỉ thẳng khi được khai báo rõ. Cho phép P-19B review-12 dùng dữ liệu/geometry độc lập gồm năm phase chevron, bốn nguồn ngoài, các stage thu nhận/truy vấn/lưu trữ/mô hình/phục vụ, orchestration và identity cross-cutting; giữ exact P-18 review-17 palette/typography/frame/connector grammar, không sao chép logo/product/prose/CSS/SVG/asset từ ảnh. Phải bind đúng 11 node, 13 directed edge, hai boundary group; archive exact review-11 trước mutation; chứng minh 13 route liên tục, rounded-default/straight-explicit, ba mode cùng geometry, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval review-12 vẫn riêng. | LOCKED |
| D-093 | Ngày 2026-08-29, chủ sở hữu yêu cầu P-19 `it-current-state` theo landscape hiện trạng ba miền của ảnh tham chiếu. Cho phép P-19B review-13 sửa riêng it-current-state bằng dữ liệu/geometry độc lập: ba boundary Thu thập/Xử lý/Phân phối; đúng chín node, tám handoff/integration edge có direct format label, hai bottleneck coral, hai pain path và hai external dashed path. Mọi node phải khai báo state; card phải nằm trọn trong boundary sở hữu; mọi connector là một orthogonal path liên tục, góc 90° bo tròn mặc định theo P-18 và chỉ thẳng khi explicit override. Hình tham khảo chỉ là dữ liệu/rubric, không sao chép prose/product/logo/icon/exact coordinate/CSS/SVG/template/asset. Archive exact review-12 trước mutation; chứng minh ba mode cùng geometry, exact alternative table, 84 non-target HTML giữ artwork ngoài candidate metadata và 28 preview byte-identical. Không sửa frozen P-18/P-19A/history, không mở P-19C hoặc package/dist/publication/Git/Release; owner approval review-13 vẫn riêng. | LOCKED |

Không thay đổi mục `LOCKED` nếu chưa có quyết định mới, rõ ràng của chủ sở hữu.

## 13. Quyết định được hoãn đến đúng phase

Các điểm sau không chặn phase tài liệu hiện tại và không được tự giả định khi đến phase liên quan:

- authorization riêng để bắt đầu P-19C sau khi P-19B đủ điều kiện; P-19A/P-19B pass không thay thế full QA/freeze/owner review;
- owner approval cho full gallery/contact sheet P-19;
- alt text song ngữ, kích thước icon và field marketplace theo schema hiện hành;
- wording cuối của license và carve-out logo sau rà soát luật sư;
- metadata release, support/privacy/terms URL nếu nền tảng yêu cầu.

Mỗi điểm phải được đề xuất bằng bằng chứng và chuyển cho đúng người duyệt; không tự lấp bằng giả định.

## 14. Phân quyền tài liệu

| Câu hỏi | Nguồn sự thật |
|---|---|
| Xây cái gì, nguyên tắc nào, quyết định nào đã khóa? | `PROJECT-CONTRACT.md` |
| Làm như thế nào, phase nào đang được phép, trạng thái ra sao? | `PLAN.md` |
| Điều kiện nào quyết định pass/fail? | `PHASE-GATES.md` |
| Các milestone liên hệ thế nào? | `ROADMAP.md` |
| Agent phải vận hành thế nào? | `AGENTS.md` |
| Claude bắt đầu đọc từ đâu? | `CLAUDE.md` |

Không sao chép nguyên khối một quyết định có thẩm quyền sang file khác. `PLAN.md` được phép mô tả công việc tạo bằng chứng; `PHASE-GATES.md` được phép nhắc lại assertion tối thiểu cần kiểm chứng, nhưng phải truy được về section/decision ID của hợp đồng và không được tạo yêu cầu sản phẩm thay thế.
