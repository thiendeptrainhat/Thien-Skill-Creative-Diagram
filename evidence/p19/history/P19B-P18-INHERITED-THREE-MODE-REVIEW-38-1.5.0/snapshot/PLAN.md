# Kế hoạch thực hiện — Thien-Skill-Creative-Diagram v1.0.0 baseline / v1.5.0 candidate

File này là nguồn sự thật duy nhất cho **cách thực hiện, quyền thực hiện và trạng thái phase**.

**Cập nhật:** 2026-08-30  
**Phạm vi được phép trong yêu cầu hiện tại:** D-118: sửa riêng connector continuity của P-19 `process`, dùng hai merge route vuông góc bo tròn có arrowhead rõ, giữ nguyên template/nội dung, exact P-18 anchor, 90 non-target P-19 artwork/30 preview cùng mọi frozen/release bytes; cập nhật gallery/trang tổng hợp/evidence/handoff.
**Phase đang thực hiện:** P-19B review-38 `in-progress`/owner-review-pending theo D-118, giữ scope D-084–D-117; exact review-37 archived; P-19 tổng thể `in-progress`; P-19C `not-started` và unauthorized
**Quyền triển khai skill/gallery:** chỉ sửa P-19B active source/gallery/evidence/governance để tạo candidate kế nhiệm; không sửa archived review-18, frozen P-18R5 review-04, historical P-18R6 review-01→review-16, exact P-18R6 review-17, exact P-19A candidate hoặc archived P-19B initial candidate; không chạy P-19C full QA/freeze/masked/owner review hoặc sửa package
**Quyền build/package/commit/push/tag/release:** không có; v1.0.0 và exact release artifacts phải giữ nguyên

Trạng thái hợp lệ: `not-started`, `authorized`, `in-progress`, `blocked`, `passed`.

## 1. Bảng trạng thái có thẩm quyền

| Phase | Tên | Trạng thái | Gate đóng góp | Ghi chú |
|---|---|---|---|---|
| P-00 | Governance lock | passed | G-00 | Chủ sở hữu đã duyệt bộ hồ sơ ngày 2026-08-15. |
| P-01 | Upstream baseline & provenance boundary | passed | G-01 | G-01 `PASS` theo phê duyệt của chủ sở hữu ngày 2026-08-15. |
| P-02 | Product, design & test contract | passed | G-02 | G-02 `PASS` theo phê duyệt owner và technical-review designation ngày 2026-08-15. |
| P-03 | Canonical skill scaffold | passed | G-03 | Exit criteria kỹ thuật đạt ngày 2026-08-15. |
| P-04 | Router, orchestration & IR contract | passed | G-03 | Exit criteria kỹ thuật đạt ngày 2026-08-15. |
| P-05 | Semantic grammars for 27 types | passed | G-03 | Exit criteria kỹ thuật đạt ngày 2026-08-15; evidence đã ghi; tại thời điểm đóng phase chưa mở P-06. |
| P-06 | Original visual system & pilot | passed | G-03 | Đóng theo quyết định D-025 ngày 2026-08-15. |
| P-07 | Full visual coverage & safe input/import | passed | G-04 | Exit criteria kỹ thuật đạt ngày 2026-08-15; evidence đã ghi; restriction về P-08 tại thời điểm đóng P-07 chỉ là hồ sơ lịch sử. |
| P-08 | Renderer, export & motion | passed | G-04 | Exit criteria kỹ thuật đạt ngày 2026-08-15; evidence đã ghi; restriction về P-09/P-11 tại thời điểm đóng P-08 chỉ là hồ sơ lịch sử. |
| P-09 | Brand asset derivatives | passed | G-06 | Đóng theo D-027 ngày 2026-08-15: Option A, ba full-crest family, minimum 64px; 32/48px QA-only; không simplified mark v1.0.0. |
| P-10 | License, notices & provenance manifests | passed | G-06 | Exact RC2 được owner duyệt theo D-029 và được Tran Ngoc Thien duyệt không điều kiện ở tư cách luật sư Việt Nam tự xác nhận theo D-030; candidate/version/hash và sáu artifact đều được khóa. Restriction về P-13 tại thời điểm đóng P-10 chỉ là hồ sơ lịch sử. |
| P-11 | Automated QA & golden infrastructure | passed | G-04 | Exit criteria kỹ thuật đạt ngày 2026-08-15; evidence đã ghi; restriction về P-09/P-12 tại thời điểm đóng P-11 chỉ là hồ sơ lịch sử. |
| P-12 | E2 benchmarks & independent forward tests | passed | G-04 | Đóng theo quyết định D-026 ngày 2026-08-15; exact fixtures/goldens và visual rubric đã được chủ sở hữu duyệt. |
| P-13 | Deterministic three-package build | passed | G-05 | Ba ZIP RC1 được sinh xác định từ một canonical source; 23/23 package checks và 127 regression test `PASS`; G-05 `PASS` theo D-033; P-14/P-15 sau đó đã hoàn tất. |
| P-14 | Owner release approval & private release | passed | G-07 | D-038: sanitized mirror commit/tag/push và private GitHub Release v1.0.0 hoàn tất; exact asset digests khớp; audit-closure commit không di chuyển tag. |
| P-15 | Maintenance & controlled updates | passed | Lặp gate theo release | Publication patch hoàn tất theo D-039/D-040; root license được GitHub nhận diện là custom `Other`, README hiển thị logo đã duyệt; package/tag/Release/version/legal wording/brand bytes không đổi. |
| P-16 | Upstream delta & contract lock | passed | G-01, G-02 repeat for v1.5.0 | Đóng theo D-047 ngày 2026-08-23; G-01@1.5.0 và G-02@1.5.0 `PASS`; P-17 sau đó được phép riêng theo D-048. |
| P-17 | Semantic expansion to 39 types | passed | G-04 repeat | Hoàn tất theo D-048 ngày 2026-08-23: 39 canonical type, bốn capability mới, 148/148 regression `PASS`; không gallery/build/Git/release. |
| P-18 | Visual vNext pilot & gallery approval | passed | G-03 repeat | Exact review-17 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`, đạt static `366/366`, browser `42/42`, regression `148/148`, masked recognition/five-second `14/14` và independent visual-craft `93/100`, minimum dimension `4/5`. Owner phê duyệt exact candidate, `G-03@1.5.0 PASS` và cho phép đóng P-18 theo D-077. |
| P-19 | Full 39-type source/gallery coverage | in-progress | G-04 repeat | P-19A `passed` theo D-078. P-19B remediation `in-progress` theo D-080; candidate đầu theo D-079 đạt technical QA nhưng bị owner bác bỏ về hướng thiết kế và đã archive historical. Candidate kế nhiệm phải kế thừa exact P-18 review-17 và dừng để owner review. P-19C chưa được phép. Target source/gallery only, không package/release. |

## 2. Bảng trạng thái gate có thẩm quyền — historical v1.0.0

| Gate | Result | Evidence/artifact | Approver/date |
|---|---|---|---|
| G-00 | PASS | `AGENTS.md`, `CLAUDE.md`, `PROJECT-CONTRACT.md`, `ROADMAP.md`, `PHASE-GATES.md`, `PLAN.md`; kiểm tra liên kết và phạm vi không phát hiện artifact triển khai. | Tran Ngoc Thien / 2026-08-15 |
| G-01 | PASS | `evidence/p01/G-01-EVIDENCE.md` SHA-256 `d93cb5c0832ab83252d0823d699132c5f5349670d110b2ff984af8841cd6f726`; bộ evidence P-01 được liệt kê và hash trong record. | Tran Ngoc Thien duyệt phạm vi và xác nhận technical review hiện tại là đủ / 2026-08-15. |
| G-02 | PASS | `evidence/p02/G-02-EVIDENCE.md` SHA-256 `899b5058b7a9205f3badadb9c75384748d446c5bc451d2c6e23d069d8a764fd8`; approved contract set và QA-only benchmark revision được liệt kê/hash trong record. | Tran Ngoc Thien duyệt contract/benchmark và xác nhận technical review hiện tại là đủ / 2026-08-15. |
| G-03 | PASS | P-03 evidence: `evidence/p03/P-03-EVIDENCE.md` SHA-256 `7a6ea1bc69e4c21b4f7a2ff9dacf31e897d5e81a2b949c8effa04252ac81bfa1`; P-04 evidence: `evidence/p04/P-04-EVIDENCE.md` SHA-256 `77aff01f97247a3d60cf272c2a109db46b1b9e64ea7cad6797bacc8dd69f4c0b`; P-05 evidence: `evidence/p05/P-05-EVIDENCE.md` SHA-256 `f8ad26b9d767ae46b80d729510e69c285b192f55c76a1900fe3bfa5424e64f0f`; approved P-06 evidence: `evidence/p06/P-06-EVIDENCE.md` SHA-256 `3994aa8f45d5061d7b6ce6c43d913a6ac28361ca6a8c08708af88be405a6f4eb`. | Tran Ngoc Thien duyệt golden direction, xác nhận technical/QA review hiện tại là đủ và phê duyệt G-03 `PASS` / 2026-08-15. |
| G-04 | PASS | `evidence/p12/G-04-EVIDENCE.md` SHA-256 `a45ce627f2f539ee956986bd20a9bf81359bb9d1783e1c687c6485591e512356`; approved fixture/golden manifests và P-07/P-08/P-11/P-12 evidence được hash trong record. | Tran Ngoc Thien duyệt exact candidate inputs, contact sheet/golden, visual rubric và xác nhận technical/QA review đủ / 2026-08-15. |
| G-05 | PASS | P-13 `passed`; exact candidate `TCD-PACKAGES-1.0.0-RC1` gồm Claude SHA-256 `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9`, OpenAI `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c`, Universal `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f`; 23/23 focused checks, Claude validator và 127 regression test `PASS`; 13 conditional/2 unsupported surface status được giữ nguyên, 0 supported claim. Gate record: `evidence/p13/G-05-EVIDENCE.md` SHA-256 `d5328c9665427b8f75e52dbe870076b6f1100b3171ac6670ebe17f979fd1fb1e`; phase record: `evidence/p13/P-13-EVIDENCE.md` SHA-256 `44a994da5f1c7a5ea310b1c0ea365d3dda01f9b0727552c7e6bd845aa6dde6a0`. | Tran Ngoc Thien xác nhận technical/QA review hiện tại là đủ và phê duyệt G-05 `PASS` theo D-033 / 2026-08-16 |
| G-06 | PASS | P-09 và P-10 đều `passed`; D-027/D-029/D-030 khóa brand và exact candidate `TCD-LEGAL-1.0.0-RC2`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6`. 29/29 focused checks và 127 regression test `PASS`; không có blocking failure. Gate record: `evidence/p10/G-06-EVIDENCE.md` SHA-256 `73c9732e82ceb9cb99cc86c2140c1916b11969ad5d45fb785ae539987ca166bb`; phase record: `evidence/p10/P-10-EVIDENCE.md` SHA-256 `36ec653200fe7ac588839bc684e16104474fa3d51113b889e7bcb177d91778a1`. | Tran Ngoc Thien phê duyệt G-06 `PASS` theo D-031 / 2026-08-15; Vietnamese-lawyer approval D-030 dựa trên professional-capacity self-attestation, không xác minh độc lập |
| G-07 | PASS | Exact candidate `TCD-RELEASE-1.0.0-RC1`; D-035/D-036 approvals, README/license, sanitized mirror, freeze/release 27/27, package 23/23 và regression 127/127 đều đạt. D-038 xác minh private `main`, annotated tag `v1.0.0`, GitHub Release và bốn remote asset digest đúng frozen candidate. Gate record: `evidence/p14/G-07-EVIDENCE.md` SHA-256 `f76441110b3a149771ff3d7608624aebd4c5ac29a278d1c8e64b9c7f54da3dc6`; phase record: `evidence/p14/P-14-EVIDENCE.md` SHA-256 `3ce5f34201bcebde991f46aa7fe2c16cc795be86c8f42192127698e69db53857`. | Tran Ngoc Thien phê duyệt G-07 `PASS` và exact release actions theo D-037 / 2026-08-16; D-038 execution verified |

Khi xét gate, cập nhật result, artifact/version/hash, người duyệt và ngày trong bảng này. Tiêu chí của từng gate chỉ nằm trong `PHASE-GATES.md`.

### 2.1. Gate repeat cho target v1.5.0

Historical `PASS` của v1.0.0 không tự chuyển sang target v1.5.0. Mỗi dòng dưới đây là một gate instance version-scoped.

| Gate instance | Result | Evidence/artifact | Approver/date |
|---|---|---|---|
| G-01@1.5.0 | PASS | Gate record: `evidence/p16/G-01-1.5.0-EVIDENCE.md`, SHA-256 `d2adb35d8f60d925e2869236a473f6f41a0a4161c92f79d24b97bd8af436c0d7`; exact P-16 snapshot/provenance packet và 170-path ledger được duyệt theo D-047. | Tran Ngoc Thien / 2026-08-23 |
| G-02@1.5.0 | PASS | Gate record: `evidence/p16/G-02-1.5.0-EVIDENCE.md`, SHA-256 `ca43ab807eb6e70229b6be4ac2d6ec2b5868f526b3186240ea2652f99152830f`; frozen byte-bound candidate manifest `evidence/p16/G02-1.5.0-CONTRACT-MANIFEST.json` cùng exact 39+4/pilot/rubric/gallery workflow được duyệt theo D-047. | Tran Ngoc Thien / 2026-08-23 |
| G-03@1.5.0 | PASS | Exact review-17 manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`; static `366/366`, browser `42/42`, regression `148/148`, exactness `75/75`, masked recognition/five-second `14/14`, independent visual-craft `93/100`, minimum dimension `4/5`, owner approval theo D-077. Gate record: `evidence/p18/G-03-1.5.0-EVIDENCE.md`. | Tran Ngoc Thien / 2026-08-27 |
| G-04@1.5.0 | NOT-EVALUATED | P-17 semantic-source và P-19A 39+4 adapters đã `passed`; P-19B remediation theo D-080 đang `in-progress` sau khi owner bác bỏ visual direction của candidate đầu. P-19C full QA/freeze/masked/owner review chưa được phép, nên gate chưa được xét. | Chưa có |
| G-05@1.5.0 | NOT-EVALUATED | Ngoài source/gallery scope hiện tại; không có quyền build/rebuild package. | Chưa có |
| G-06@1.5.0 | NOT-EVALUATED | Ngoài source/gallery scope hiện tại; legal/brand v1.0.0 không đổi. | Chưa có |
| G-07@1.5.0 | NOT-EVALUATED | Ngoài source/gallery scope hiện tại; không có commit/push/tag/Release/release authorization. | Chưa có |

## 3. Quy tắc thẩm quyền và trạng thái phase

- Một yêu cầu sau này có thể cho phép thực hiện một hoặc nhiều phase liên tiếp; agent không phải hỏi lại ở mỗi phase nếu thẩm quyền đã rõ và không phát sinh quyết định vật chất mới.
- Gate yêu cầu phê duyệt trực tiếp của chủ sở hữu hoặc luật sư vẫn không được tự vượt.
- Khi một blocking condition xuất hiện, đánh dấu `blocked`, ghi evidence và hỏi đúng câu hỏi; không tự chọn phương án.
- Chỉ `PLAN.md` được cập nhật trạng thái. `ROADMAP.md` không quản lý tiến độ.
- Mỗi phase có exit criteria riêng trong mục `Verification`; đạt exit criteria mới được đổi sang `passed`.
- Gate trong `PHASE-GATES.md` đóng milestone tổng hợp từ nhiều phase; một phase có thể `passed` trước khi gate mà nó đóng góp được xét.

Các đoạn `Evidence hiện tại` trong P-00 đến P-15 dưới đây là **historical-at-phase-close**: chúng ghi trạng thái và restriction ở thời điểm phase đó đóng, không phải authority hiện hành. Bảng mục 1 và chỉ dẫn mới nhất của chủ sở hữu mới quyết định trạng thái/quyền hiện tại.

## P-00 — Governance lock

**Mục tiêu:** biến kế hoạch đã duyệt thành bộ nguồn sự thật trước khi tạo skill.

**Đầu vào:** quyết định của chủ sở hữu trong cuộc trò chuyện; phân tích read-only nguồn tham khảo; hướng dẫn `skill-creator`.

**Công việc được phép:**

- tạo `AGENTS.md`, `CLAUDE.md`, `PROJECT-CONTRACT.md`, `ROADMAP.md`, `PHASE-GATES.md`, `PLAN.md`;
- ghi quyết định, scope, boundary, phase, gate và điểm hoãn;
- kiểm tra liên kết và tính nhất quán.

**Không được phép:** scaffold `SKILL.md`, tạo script/reference/asset runtime, xử lý logo, soạn license phát hành, build ZIP, init Git, commit hoặc push.

**Deliverable:** sáu file quản trị ở root repository.

**Verification:**

- không có source-of-truth trùng nhau;
- tất cả quyết định đã khóa có ID;
- tất cả phase có dependency, deliverable và gate;
- workspace không có artifact triển khai do phase này tạo.

**Gate đóng góp:** G-00.  
**Người duyệt:** chủ sở hữu.  
**Evidence hiện tại:** sáu file tồn tại và đã được rà soát; kiểm tra read-only xác nhận không có artifact triển khai; chủ sở hữu Tran Ngoc Thien xác nhận duyệt bộ hồ sơ ngày 2026-08-15. P-00 `passed` và G-00 `PASS`.

## P-01 — Upstream baseline & provenance boundary

**Mục tiêu:** khóa bằng chứng chức năng trước mọi implementation.

**Dependency:** P-00 `passed` và G-00 `PASS`.

**Workstream:**

1. Chụp snapshot commit/tag/date của `diagram-design` và lưu inventory read-only.
2. Kiểm đủ 27 type từ canonical `SKILL.md`/type references; ghi rõ sai lệch metadata 29.
3. Liệt kê đầy đủ variant, specimen, semantic pattern, import, motion, output dial và failure behavior trong snapshot.
4. Chụp snapshot `Thien-UI-UX-Ultra`; ánh xạ chỉ các principle được phép học.
5. Xác minh tài liệu chính thức hiện hành của Claude, OpenAI/ChatGPT và Agent Skills.
6. Lập capability/provenance matrix và ranh giới independent reimplementation.
7. Thiết kế `SOURCE_MANIFEST` làm nguồn sự thật để notice được sinh/đối chiếu tự động.

**Deliverable dự kiến:** source snapshot record, taxonomy/capability matrix, provenance policy và draft source manifest schema.

**Verification:** mọi capability có phân loại và nguồn; không có code/text/template/asset upstream trong implementation area.

**Gate đóng góp:** G-01.

**Evidence hiện tại:** `evidence/p01/` chứa snapshot record, capability/provenance matrix, platform evidence inventory, provenance policy, draft `SOURCE_MANIFEST` schema và G-01 evidence record. Snapshot chức năng khóa tại `diagram-design@09df49d8d1a1c7fb2efdfcdc7a2a0713534350a6`; snapshot nguyên tắc khóa tại `Thien-UI-UX-Ultra@fb4e57758f525827e04004737d779f4c93b9b3a0` (`v2.0.0`). Kiểm tra read-only xác nhận 27 type, 97 specimen được kiểm kê, schema JSON hợp lệ và không có upstream implementation material trong workspace. Chủ sở hữu Tran Ngoc Thien đã duyệt phạm vi và xác nhận technical review hiện tại là đủ ngày 2026-08-15. P-01 `passed`; G-01 `PASS`; P-02 được phép bắt đầu.

## P-02 — Product, design & test contract

**Mục tiêu:** khóa hành vi và tiêu chí đánh giá trước khi nhân rộng code.

**Dependency:** G-01.

**Workstream:**

1. Định nghĩa request schema: type auto/manual, size, detail, audience, visual mode, language, format, motion.
2. Định nghĩa output/fallback contract cho HTML, SVG, PNG và HTML+PNG.
3. Định nghĩa semantic IR, preservation rules và complexity budget.
4. Định nghĩa visual contract: hierarchy, grid, spacing, typography, color, semantic shapes, connector routing, responsive và print.
5. Định nghĩa accessibility, Vietnamese typography và quantitative integrity contract.
6. Định nghĩa security/fidelity contract cho input/import không tin cậy.
7. Soạn benchmark manifest E2 candidate, gồm `REF-SWIMLANE-CASH-RECEIPTS-001`, rồi trình chủ sở hữu duyệt.
8. Lập surface × artifact × install method × trigger × output × fallback × support-status matrix cho toàn bộ surface tại mục 6.3 của `PROJECT-CONTRACT.md`.
9. Chốt naming của visual mode, threshold/rubric và unsupported behavior; không tự chọn nếu ảnh hưởng vật chất.

**Deliverable dự kiến:** product spec, design contract, IR schema, security contract, surface support matrix và benchmark manifest đã duyệt.

**Verification:** mọi hành vi public có expected result, failure mode và test mapping.

**Gate đóng góp:** G-02.

**Evidence hiện tại:** `evidence/p02/` chứa approved product/output contract, strict request schema, provider-neutral architecture và semantic IR schema, design/accessibility/quantitative contract, security/fidelity contract, test mapping, official-evidence record, surface support matrix, benchmark manifest và QA-only asset record. Benchmark R2 được lưu tại `evidence/p02/qa-only/REF-SWIMLANE-CASH-RECEIPTS-001-r2.png`, SHA-256 `a7dfa484b5d324dcb4269aec5dcae68154dec1947ab1b78c75b12f11a4fb6113`, và bị cấm khỏi package. JSON syntax checks đã pass; 27 canonical type, bảy semantic pattern và 15 surface row có mapping/status. Chủ sở hữu đã duyệt contract/benchmark, cho phép QA-only custody và xác nhận technical review hiện tại là đủ ngày 2026-08-15. P-02 `passed`; G-02 `PASS`; dependency của P-03 đã được đáp ứng.

## P-03 — Canonical skill scaffold

**Mục tiêu:** tạo cấu trúc skill canonical duy nhất, chưa tạo ba bản phân nhánh.

**Dependency:** G-02 và lệnh triển khai rõ ràng.

**Workstream:**

1. Dùng `skill-creator` và `init_skill.py` theo quy trình chính thức.
2. Tạo folder `thien-skill-creative-diagram` với `SKILL.md` và chỉ các resource directory thật sự cần.
3. Giữ frontmatter chỉ có `name` và `description`; kiểm giới hạn tương thích đa nền tảng tại thời điểm thực hiện.
4. Thiết kế progressive disclosure để `SKILL.md` gọn; 27 type/reference được route theo nhu cầu.
5. Tách platform overlay ra khỏi canonical core.

**Deliverable dự kiến:** canonical scaffold tối thiểu, validation pass, chưa có package ZIP.

**Verification:** name/folder/frontmatter đúng; không placeholder hoặc tài liệu thừa trong payload skill.

**Gate đóng góp:** G-03 readiness; G-02 phải `PASS` trước khi bắt đầu.

**Evidence hiện tại:** canonical scaffold tồn tại tại `thien-skill-creative-diagram/`; `SKILL.md` chỉ có frontmatter `name` và `description`; `agents/openai.yaml` được tách làm OpenAI overlay; không có `assets/`, placeholder hoặc tài liệu payload thừa. Kiểm tra YAML/scaffold tương đương đã `PASS`. Record: `evidence/p03/P-03-EVIDENCE.md`, SHA-256 `7a6ea1bc69e4c21b4f7a2ff9dacf31e897d5e81a2b949c8effa04252ac81bfa1`. P-03 `passed`; dependency của P-04 đã được đáp ứng.

## P-04 — Router, orchestration & IR contract

**Mục tiêu:** xây workflow cốt lõi trước renderer chi tiết.

**Dependency:** P-03.

**Workstream:**

1. Detect input và ngôn ngữ; phân biệt dữ liệu với chỉ dẫn.
2. Chọn type/variant bằng bằng chứng; hỏi khi lựa chọn làm thay đổi nghĩa.
3. Chuẩn hóa vào IR: nodes, edges, groups, lanes, series, annotations, sources và fidelity ledger.
4. Áp design/audience/detail/size contract.
5. Route đến type grammar, renderer, validator và exporter.
6. Tạo transparent fallback khi capability/renderer không có.

**Deliverable dự kiến:** router contract, IR implementation, validation schema và representative unit tests.

**Verification:** cùng một input semantic tạo IR ổn định; unsupported case thất bại rõ, không đoán.

**Gate đóng góp:** G-03 readiness.

**Evidence hiện tại:** canonical core có strict request normalization, instruction/data boundary, deterministic language resolution, evidence-based router cho đúng 27 canonical type, common semantic-IR builder/validator, fidelity reconciliation, security ceilings, complexity planning và downstream capability/fallback plan. Hai runtime schema giữ nguyên cấu trúc contract P-02; `SKILL.md` route progressive disclosure tới đúng reference/helper. Bộ 23 unit test P-04 tiếp tục `PASS`, gồm deterministic IR và unsupported/ambiguous failure không đoán. Record: `evidence/p04/P-04-EVIDENCE.md`, SHA-256 `77aff01f97247a3d60cf272c2a109db46b1b9e64ea7cad6797bacc8dd69f4c0b`. P-04 `passed`; G-03 vẫn `NOT-EVALUATED`.

## P-05 — Semantic grammars for 27 types

**Mục tiêu:** mã hóa cấu trúc và tính đúng đắn của 27 canonical type trước khi tối ưu thẩm mỹ.

**Dependency:** P-04.

**Workstream:**

1. Tạo reference/spec độc lập cho từng type: use case, required semantics, allowed shapes, edge rules, labels, complexity và anti-patterns.
2. Tách chart định lượng khỏi diagram quan hệ để không áp sai connector/layout rules.
3. Với từng variant, specimen và bảy semantic pattern trong inventory P-01: xác định canonical parent, hành vi cần triển khai, selector/trigger, fallback và ít nhất một contract/smoke test; không tăng type count.
4. Implement semantic transformation cần thiết cho từng semantic pattern, không chỉ lập mapping tài liệu.
5. Tạo semantic assertions và minimal fixtures nguyên bản cho từng type/capability.
6. Kiểm thử Vietnamese long labels, dense graph và ambiguous request.

**Deliverable dự kiến:** 27 type grammar/reference, selector mapping và semantic test suite.

**Verification:** 27/27 type và 100% capability inventory có implementation mapping cùng test tối thiểu; không có placeholder hoặc copied specimen.

**Gate đóng góp:** G-03.

**Evidence hiện tại:** 27/27 canonical type có reference và validator độc lập; 27 positive fixture và 27 boundary mutation được kiểm; bảy semantic pattern có transformation thực thi được và giữ nguyên canonical parent; exact inventory 95 capability/97 specimen có parent, owner phase, implementation disposition, selector, fallback, test ID và status. Bộ 37 test (gồm 23 regression P-04) `PASS`; generated-reference drift, AST, JSON, YAML tương đương và count checks đều `PASS`. Record: `evidence/p05/P-05-EVIDENCE.md`, SHA-256 `f8ad26b9d767ae46b80d729510e69c285b192f55c76a1900fe3bfa5424e64f0f`. P-05 `passed`; tại thời điểm đóng P-05, P-06 chưa được phép; G-03 vẫn `NOT-EVALUATED`.

## P-06 — Original visual system & pilot

**Mục tiêu:** tạo chất lượng hình ảnh chuyên nghiệp, nguyên bản và nhất quán.

**Dependency:** P-05.

**Workstream:**

1. Tạo token system trung tính cho ba static visual mode đã được duyệt ở G-02; tên candidate ban đầu có thể là light, dark và editorial.
2. Xây typography, spacing, hierarchy, shape, connector, legend, annotation và density rules.
3. Implement visual behavior cho pilot subset đại diện đã khóa ở G-02, gồm ít nhất một variant và một semantic pattern; chưa mở rộng toàn bộ visual inventory.
4. Xây layout/routing có kiểm tra geometry, không dựa vào một case hard-code.
5. Render pilot nhiều connector, chart định lượng và benchmark swimlane tiếng Việt.
6. Thực hiện render–inspect–revise–verify trên nhiều canvas/background.
7. Trình contact sheet/golden direction cho chủ sở hữu duyệt.

**Deliverable dự kiến:** original visual system, pilot renderer và approved pilot goldens.

**Verification:** các hard check G-03 đạt; thiết kế trung tính, không tự gắn TDTN brand.

**Gate đóng góp:** G-03.

**Evidence hiện tại:** canonical visual system có đúng ba mode `neutral-light`, `neutral-dark`, `editorial`; pilot subset gồm Architecture + `CAP-P05`, grouped Bar + `CAP-V05`, và grouped Vietnamese Swimlane benchmark. 18 HTML/SVG artifact được sinh xác định; 47 test `PASS`; toàn bộ chín HTML candidate qua browser audit, contact sheet có đủ chín card, và canvas 1024×768 không tràn ngang. Record đã duyệt: `evidence/p06/P-06-EVIDENCE.md`, SHA-256 `3994aa8f45d5061d7b6ce6c43d913a6ac28361ca6a8c08708af88be405a6f4eb`. Theo D-025, P-06 `passed` và G-03 `PASS`; P-07 chưa được phép tại thời điểm đóng P-06 và được cho phép sau đó theo bảng trạng thái hiện hành.

## P-07 — Full visual coverage & safe input/import

**Mục tiêu:** sau khi visual direction được duyệt, mở rộng renderer tới toàn bộ inventory rồi nhận input phong phú mà không thực thi nội dung không tin cậy hoặc làm mất semantics âm thầm.

**Dependency:** G-03.

**Workstream:**

1. Mở rộng visual behavior từ pilot tới 27/27 canonical type và 100% variant/specimen/semantic-pattern inventory; mỗi capability có smoke test riêng.
2. Parse natural language, pasted table, CSV và JSON vào IR.
3. Parse draw.io formats và multi-page theo contract.
4. Parse bốn grammar Mermaid v1 theo contract; redraw, không render Mermaid.
5. Sanitize mọi text field từ natural language, pasted table, CSV, JSON, draw.io và Mermaid; escape HTML/SVG/CSS context đúng cách.
6. Chặn prompt injection qua cell/label, script/event handler/URL/resource, XML/DOCTYPE/XXE, deep/oversized JSON, CSV formula payload, decompression abuse và path traversal.
7. Ghi fidelity ledger cho keep/merge/drop/source rot.
8. Báo rõ unsupported/image-only/malformed/oversized input và yêu cầu input phù hợp khi cần.

**Deliverable dự kiến:** full visual coverage, safe parsers, fidelity ledger, adversarial fixtures và import tests.

**Verification:** 27/27 type và 100% capability inventory có visual smoke evidence; zero side effect, zero invented content, mọi semantic loss được ghi.

**Gate đóng góp:** G-04 import/security section.

**Evidence hiện tại:** static coverage có 81/81 lượt 27 type × ba mode với hash xác định; 16/16 variant, 7/7 semantic pattern, 97/97 specimen và 95/95 capability có disposition visual/import/static-fallback. Bounded inert import hỗ trợ natural language, pasted table, CSV, JSON, draw.io XML/PNG/SVG/multi-page và bốn Mermaid subset; fidelity bắt buộc `source = kept + merged + dropped + source rot`, `invented_count = 0`. Bộ 75 test regression/adversarial `PASS`; JSON/manifest checks `PASS`. Browser local từ chối `file://` theo URL policy nên không có browser audit; contact sheet/SVG QA-only được giữ để manual inspection và automated SVG geometry/security checks vẫn `PASS`. Record: `evidence/p07/P-07-EVIDENCE.md`, SHA-256 `60b59e5301a61d8fdc2e5baae49367323306ce5c21615bac80e469f07dbb52ce`. P-07 `passed`; G-04 vẫn `NOT-EVALUATED`; P-08 `not-started` và chưa được phép.

## P-08 — Renderer, export & motion

**Mục tiêu:** hoàn thiện output portable và motion static-first.

**Dependency:** P-07.

**Workstream:**

1. Render HTML với inline SVG/CSS an toàn, không phụ thuộc resource mạng bắt buộc.
2. Export SVG diagram-only theo contract.
3. Detect renderer để export PNG/HTML+PNG; thiếu renderer thì fallback minh bạch.
4. Xử lý print, viewBox, responsive size và font fallback.
5. Implement các motion mode được G-02 duyệt; candidate ban đầu là `none`, `reveal`, `step`, `loop`, luôn có complete static/end frame.
6. Implement no-JS, reduced-motion, keyboard/focus và deterministic step order.

**Deliverable dự kiến:** renderer/exporter/motion modules và cross-browser representative tests.

**Verification:** HTML/SVG core luôn dùng được; PNG không kích hoạt auto-install; motion không làm mất nghĩa static.

**Gate đóng góp:** G-04 render/accessibility/motion sections.

**Evidence hiện tại:** 27/27 type qua standalone SVG và bốn HTML motion mode (`none`, `reveal`, `step`, `loop`) với 135/135 artifact hash xác định; chín size preset, 7/7 output capability, 12/12 motion capability và 6/6 failure capability thuộc P-08 có implementation/test mapping. Self-contained HTML, diagram-only accessible SVG, exact-data alternatives, localized keyboard controls, print/reduced-motion/no-JS complete state, safe explicit writer và artifact ledger đều qua test. Không có rasterizer được phê duyệt trong môi trường; không cài dependency, không tạo hoặc tuyên bố PNG thật; PNG→SVG và HTML+PNG→HTML fallback `PASS`, adapter path được kiểm bằng fixture PNG hợp lệ. Bộ 93 test `PASS`; JS syntax, JSON, frontmatter/link/drift/boundary checks `PASS`. Browser/cross-browser execution được ghi `blocked / not executable` vì browser URL policy từ chối local `file://`; không dùng workaround và không tuyên bố browser pass. Record: `evidence/p08/P-08-EVIDENCE.md`, SHA-256 `11bcdf85ec9b7a99e3ae1ad6583736e18d69ed4dd40dfa414a102cf6ce7c3bc6`. P-08 `passed`; G-04 vẫn `NOT-EVALUATED`; P-09 và P-11 `not-started` và chưa được phép.

## P-09 — Brand asset derivatives

**Mục tiêu:** tạo bộ nhận diện package từ logo nguồn mà không thay đổi master hoặc áp brand vào diagram mặc định.

**Dependency:** visual/package requirements đã đủ rõ; có thể bắt đầu sau G-03.

**Workstream:**

1. Copy master vào asset source-of-truth khi được phép; xác minh hash và provenance.
2. Chuẩn hóa recipe sRGB/alpha/downsampling mà không sửa master.
3. Tạo candidate safe-area/padding/plate/outline và preview square/circle/squircle, light/dark, small sizes.
4. Chỉ tạo simplified candidate nếu full crest thất bại small-size QA.
5. Ghi transformation recipe, tool/version, dimensions, destination và derivative hash vào asset manifest.
6. Trình contact sheet cho chủ sở hữu; chỉ candidate được duyệt mới vào package.

**Deliverable dự kiến:** approved icon/logo derivatives và `ASSET_MANIFEST` candidate.

**Verification:** không crop sai, biến dạng, mất tương phản hoặc tuyên bố quyền vượt bằng chứng.

**Gate đóng góp:** phần brand của G-06.

**Evidence hiện tại:** logo master được lưu byte-identical trong QA evidence, SHA-256 `020a47a3c831664c700c9e4491c7ae00cf5a8f330e6c3c57422ee246df56d69e`; 22 full-crest file gồm transparent/light-plate/dark-plate tại 1024/512/400/256/128/64/48/32px theo family phù hợp, sinh xác định bằng proportional resize/padding/plate, không crop/recolor/trace/vectorize. 22/22 PNG qua hash, CRC, square, 8-bit RGBA, sRGB, metadata và safe-area checks; repeated build giữ hash; full regression 127 test `PASS`. Theo D-027/Option A, 16 file từ 64px trở lên được owner duyệt; sáu file 32/48px chỉ QA-only và bị loại khỏi v1.0.0; không tạo simplified mark cho v1.0.0. Transparent trên nền navy không phù hợp nên dark plate là mitigation. P-13 đã đóng gói đúng hai light-plate 64/400 cho OpenAI/Universal và không đóng brand asset trong Claude; các derivative còn lại giữ QA/provenance-only. Selection record: `evidence/p09/APPROVED-BRAND-SELECTION.json`, SHA-256 `b38a922d42cb21d20e9d5bc316d0d17fe368ed6080528868a3537ab691aa2437`; phase record: `evidence/p09/P-09-EVIDENCE.md`, SHA-256 `89ac01ae05b4ac541598510b52b486a099928215d0d10ac9462237eea4204eec`. P-09, P-10 và P-13 đều `passed`; G-05/G-06 `PASS`; P-14 đang chuẩn bị release candidate.

## P-10 — License, notices & provenance manifests

**Mục tiêu:** tạo legal candidate song ngữ, nhất quán và truy vết được.

**Dependency để bắt đầu draft:** G-01; đọc đầy đủ license template trước khi soạn.  
**Dependency để finalize P-10 và xét G-06:** P-09 `passed`.

**Workstream:**

1. Draft license theo đúng tên và template đã khóa; tiếng Việt kiểm soát khi mâu thuẫn.
2. Thể hiện grant chỉ qua paid order, written permission/email hoặc commercial agreement.
3. Tách quyền skill/code khỏi logo, brand và third-party material.
4. Tạo application declaration, NOTICE và third-party notices.
5. Hoàn thiện source/asset manifest làm nguồn sự thật; tự động đối chiếu notice.
6. Gắn version/hash cho legal candidate.
7. Chuyển đúng candidate cho luật sư Việt Nam; sửa theo ý kiến đã được chủ sở hữu chấp thuận.

**Deliverable dự kiến:** legal release candidate và provenance bundle.

**Verification:** không có claim mâu thuẫn; lawyer sign-off gắn đúng hash/version.

**Gate đóng góp:** phần legal/provenance của G-06.

**Evidence hiện tại:** D-028 đã giải quyết P10-OD-01/P10-OD-02. Exact six-file candidate `TCD-LEGAL-1.0.0-RC2`, version `1.0.0`, aggregate SHA-256 `8f16380761cd6026166daa12ee36227d96e0e3b92ce605f4d9057624de8292c6` đã được sinh xác định; license chỉ đổi `SKILLS` → `SKILL` tại hai dòng tiêu đề song ngữ theo phê duyệt, không đổi clause khác. 29/29 kiểm tra legal/provenance/sign-off và 127 regression test `PASS`; 16 derivative đã duyệt và 6 QA-only exclusion khớp hash; chỉ light-plate 64/400 nhắm OpenAI+Universal, 14 derivative còn lại provenance-only, Claude không có brand target. Owner đã duyệt exact RC2 theo D-029. Tran Ngoc Thien tự xác nhận là luật sư Việt Nam và duyệt không điều kiện đúng candidate/version/hash/sáu artifact theo D-030; project không xác minh độc lập danh tính/chứng chỉ hành nghề. Approval record: `evidence/p10/LAWYER-APPROVAL-RECORD.json`, SHA-256 `688a588587f4458baa8386f7e6af3507fce4a1dd3f6dc2d7ede57ef701714cd1`; phase record: `evidence/p10/P-10-EVIDENCE.md`, SHA-256 `36ec653200fe7ac588839bc684e16104474fa3d51113b889e7bcb177d91778a1`. P-10 và P-13 `passed`; G-06 `PASS` theo D-031; exact legal RC2 được giữ nguyên trong ba package; G-05 `PASS`; P-14 đang chuẩn bị release candidate.

## P-11 — Automated QA & golden infrastructure

**Mục tiêu:** biến contract thành kiểm thử lặp lại, có khả năng bắt lỗi thật.

**Dependency:** P-08.

**Workstream:**

1. Validate schema, reference links, type coverage và build determinism.
2. Tạo geometry checks: bounds, clipping, overlap, connector endpoint/crossing, shared attach point, duplicate ID.
3. Tạo accessibility, Vietnamese typography và contrast checks.
4. Tạo quantitative source-to-render assertions: cùng dataset từ pasted table/CSV/JSON phải sinh normalized IR tương đương; kiểm bốn chart lõi và conditional numeric/date assertions cho Gantt, Timeline, Quadrant, Pyramid/Funnel khi input chứa số/thời gian.
5. Tạo import security/fidelity, motion/reduced-motion và package hygiene tests.
6. Dùng mutation tests chứng minh validator bắt được lỗi dự kiến.
7. Thiết kế golden review không tự update.

**Deliverable dự kiến:** automated QA suite, mutation evidence và golden harness.

**Verification:** mỗi hard failure có ít nhất một test chứng minh khả năng phát hiện.

**Gate đóng góp:** G-04.

**Evidence hiện tại:** canonical QA layer kiểm schema/link/type coverage/determinism, geometry sâu, SVG/accessibility/Vietnamese/contrast, carrier-equivalence và source-to-render quantitative integrity, import/fidelity, motion và package inventory. Registry có 58/58 hard-failure family thuộc 12 category, mỗi family có detector, test ID và mutation test tồn tại; bộ 121 regression/mutation test `PASS`. 27/27 canonical SVG fixture và 8/8 conditional quantitative family qua direct QA. Golden harness chỉ compare, không có update operation; 18/18 owner-approved P-06 HTML/SVG hash khớp và `baseline_updated = false`. `quick_validate.py` không chạy được do thiếu PyYAML; không cài dependency và không tuyên bố pass, trong khi JSON/link/frontmatter conventions, deterministic generation và phase-specific checks đều pass. Browser/benchmark/forward-test được ghi `not run (out of scope)` vì thuộc P-12. Record: `evidence/p11/P-11-EVIDENCE.md`, SHA-256 `9f30df1a4efd34291b4a6b61837f222c5d14bfab879f1179240c117076a0ca9c`. P-11 `passed`; G-04 vẫn `NOT-EVALUATED`; P-09 và P-12 `not-started` và chưa được phép.

## P-12 — E2 benchmarks & independent forward tests

**Mục tiêu:** đánh giá độ tổng quát bằng benchmark đã được chủ sở hữu duyệt và agent sạch ngữ cảnh.

**Dependency:** P-11 và benchmark manifest approval tại G-02.

**Workstream:**

1. Chạy 27 canonical, boundary, semantic, quantitative, import, motion và trigger suites theo manifest đã duyệt.
2. Render base matrix và pairwise variations; không tự nhân scope ngoài contract.
3. Chạy `REF-SWIMLANE-CASH-RECEIPTS-001` như must-pass benchmark.
4. Forward-test trong fresh sessions chỉ với skill và raw task/artifact; không tiết lộ expected answer hoặc chẩn đoán.
5. So sánh semantic assertions trước visual golden.
6. Trình contact sheet và high-risk full-resolution goldens cho chủ sở hữu.
7. Sửa lỗi, chạy regression và ghi residual finding.

**Deliverable dự kiến:** benchmark report, approved goldens, forward-test evidence và residual risk log.

**Verification:** zero hard failure; ngưỡng rubric cuối do chủ sở hữu duyệt được đạt.

**Gate đóng góp:** G-04.

**Evidence hiện tại:** deterministic E2 runner đạt 27/27 canonical case, 81/81 base render, 27/27 boundary detection, 7/7 semantic pattern, 6/6 quantitative, 12/12 import outcome, 5/5 motion/export case và 36 pairwise case với zero uncovered pair; zero hard failure. Năm fresh-session forward run không thấy expected answer/chẩn đoán nội bộ: bốn final pass và một iteration đầu phát hiện lỗi negative-bar anchoring, sau đó fresh retest pass; funnel non-monotonic và bar zero-baseline đã được sửa với regression. Full suite 127 test `PASS`. Exact 27 fixture bytes và immutable 18-artifact HTML/SVG golden set đã được chủ sở hữu duyệt; comparator đạt 18/18 và `baseline_updated = false`. Browser local `file://` bị URL policy chặn nên trạng thái vẫn là `blocked / not executable`, không tuyên bố browser/cross-browser pass; PNG dùng fallback đã khai báo và không cài dependency. Record: `evidence/p12/P-12-EVIDENCE.md`, SHA-256 `a03ee9428e26c9bff704153aad71f510385e6dd23e71ed8a6d69d12528918599`; gate record `evidence/p12/G-04-EVIDENCE.md`, SHA-256 `a45ce627f2f539ee956986bd20a9bf81359bb9d1783e1c687c6485591e512356`. P-12 và P-13 `passed`; G-04/G-05 `PASS`; P-14 đang chuẩn bị release candidate.

## P-13 — Deterministic three-package build

**Mục tiêu:** sinh ba artifact độc lập từ cùng canonical source.

**Dependency:** G-04 và G-06 đều `PASS`.

**Workstream:**

1. Xác minh lại schema manifest và install surface chính thức.
2. Tạo Claude và OpenAI platform overlay; quản lý `agents/openai.yaml` theo mục 6.1 của `PROJECT-CONTRACT.md`; không sửa canonical runtime core.
3. Sinh ba ZIP theo content tree tại mục 6.2 của `PROJECT-CONTRACT.md`; dùng envelope Claude/OpenAI đã được surface matrix phê duyệt, gồm legal/provenance bundle byte-identical và brand asset theo manifest.
4. Sinh Universal ZIP với đúng top-level folder cho `.agents/skills`.
5. Chuẩn hóa archive order, timestamp, permissions, encoding và checksum.
6. Chặn absolute path, traversal, symlink, secret, cache và file thừa.
7. So sánh hash runtime core và legal bundle giữa ba package; kiểm declared brand/overlay differences.
8. Install/smoke test mọi cell `supported`. Với cell `conditional`, áp evidence rule đã được chủ sở hữu duyệt ở G-02; không được tính hoặc quảng bá là `supported`. Nếu điều kiện có thể đáp ứng trước release thì phải smoke-test, nếu không phải công bố giới hạn hoặc hạ thành `unsupported` cho v1.0.0.

**Deliverable dự kiến:** ba ZIP versioned, checksum manifest và install/smoke-test evidence.

**Verification:** functional parity trong giới hạn host; chỉ adapter khác nhau có chủ đích.

**Gate đóng góp:** G-05.

**Evidence hiện tại:** deterministic builder sinh exact package candidate `TCD-PACKAGES-1.0.0-RC1`, version `1.0.0`: Claude plugin SHA-256 `bba5b464322d8d50ec2f9b76e18581df3e5614004078ba40708f2c8cd1104fa9`, OpenAI plugin `7d7a33dbdecdd87e9f5237c3ab39b1416ba11c3b736424ba3eb0151c9d73893c`, Universal raw skill `4fcccc656008dd1caba8c1605b0523b0c041afaf216f739aba7373b5d5ac748f`. Runtime core và legal bundle có logical aggregate byte-identical trên ba target; exact G-06 legal RC2 và D-028 brand bytes không đổi. 23/23 package/parity/hygiene/smoke checks, Claude Code manifest validation và 127 regression test `PASS`; extracted runtime của cả ba target tạo HTML/SVG tiếng Việt và PNG→SVG fallback không cài dependency. P-02 surface matrix giữ 0 `supported`, 13 `conditional`, 2 `unsupported`; không claim compatibility vượt evidence. Record: `evidence/p13/P-13-EVIDENCE.md`, SHA-256 `44a994da5f1c7a5ea310b1c0ea365d3dda01f9b0727552c7e6bd845aa6dde6a0`; gate record: `evidence/p13/G-05-EVIDENCE.md`, SHA-256 `d5328c9665427b8f75e52dbe870076b6f1100b3171ac6670ebe17f979fd1fb1e`. P-13 `passed`; G-05 `PASS` theo D-033; P-14 `in-progress` theo D-034 nhưng chưa có G-07/release authorization.

## P-14 — Owner release approval & private release

**Mục tiêu:** phát hành v1.0.0 có kiểm soát, chỉ sau đủ thẩm quyền.

**Dependency:** G-00 đến G-06 đều `PASS`.

**Workstream:**

1. Freeze assembled release candidate và tính version/hash; không thay đổi legal/brand material đã qua G-06.
2. Đối chiếu evidence: owner approval cho benchmark/goldens/brand, lawyer sign-off cho legal hash, technical pass cho ba package.
3. Chủ sở hữu duyệt ba ZIP và toàn bộ release candidate, rồi ra release authorization riêng.
4. Nếu bất kỳ legal/brand byte nào đổi sau G-06, quay lại đúng gate để duyệt lại.
5. Kiểm tra repository/remote private và release target.
6. Chỉ khi có lệnh rõ ràng: init/commit/tag `v1.0.0`, push private repository và tạo release theo phạm vi được yêu cầu.
7. Ghi release evidence và checksum.

**Deliverable dự kiến:** private v1.0.0 release.

**Verification:** không artifact nào thay đổi sau approval; remote đúng và private.

**Gate đóng góp:** G-07.

**Evidence hiện tại:** exact release candidate `TCD-RELEASE-1.0.0-RC1` giữ nguyên ba ZIP/G-06 legal/brand bytes. Root `README.md` có hướng dẫn checksum, Claude Code, Codex raw skill, OpenAI local marketplace, limitations, license và provenance. Sanitized mirror release commit `1aae0a0073dd685af1341554f27554eb44c42f63` đã push lên private `main`; annotated tag `v1.0.0` peel về đúng commit; GitHub Release `v1.0.0` là non-draft/non-prerelease và bốn remote asset digest/size khớp frozen candidate. Mirror 5/5, freeze/release 27/27, package 23/23 và regression 127/127 `PASS`. P-14 `passed`; G-07 `PASS`; P-15 chưa được phép.

## P-15 — Maintenance & controlled updates

**Mục tiêu:** cập nhật có provenance và không làm suy giảm chất lượng. P-15 nằm ngoài completion scope của v1.0.0.

**Dependency:** v1.0.0 đã phát hành.

**Workstream:**

1. Theo dõi upstream theo snapshot mới; không tự merge hoặc copy.
2. Phân tích capability delta và xin duyệt scope/version.
3. Chạy full regression, benchmark/golden review và legal/provenance delta.
4. Áp semantic versioning và deterministic rebuild.
5. Không thay golden/license/brand do drift tự động.

**Deliverable dự kiến:** versioned maintenance releases với audit trail.

**Verification:** mọi thay đổi có decision, source mapping, test và approval tương ứng; mỗi maintenance release lặp G-01 đến G-07 theo phần bị ảnh hưởng và luôn lặp G-05 đến G-07.

**Publication patch đã hoàn tất:** D-039/D-040 giới hạn và đóng workstream ở root `LICENSE.md` byte-identical với exact legal candidate, logo 400px đã duyệt trên root `README.md`, evidence/governance và commit/push private `main`. Không có upstream capability delta, runtime/package rebuild, semantic-version change, retag hoặc GitHub Release mutation. Evidence: `evidence/p15/P-15-EVIDENCE.md`.

## P-16 — Upstream delta & contract lock

**Mục tiêu:** khóa một exact upstream snapshot, phân loại delta 27→39 và tạo contract/gate candidate cho target v1.5.0 trước khi sửa source hoặc gallery.

**Dependency:** v1.0.0/P-15 đã đóng; D-041–D-047; chỉ dẫn triển khai P-16 ngày 2026-08-22 và owner gate approval/closure ngày 2026-08-23.

**Công việc được phép:**

1. Xác minh read-only exact `diagram-design` commit/tag/version/date và license.
2. Đối chiếu với snapshot P-01, khóa 12 canonical addition và bốn capability mới ở mức taxonomy/hành vi trừu tượng.
3. Ghi provenance/copying boundary, upstream file hashes và gallery inventory factual.
4. Cập nhật `PROJECT-CONTRACT.md`, `PLAN.md`, `PHASE-GATES.md`, `ROADMAP.md` và evidence P-16.
5. Trình owner review cho gate instances G-01@1.5.0/G-02@1.5.0.

**Không được phép:** sửa bất kỳ file nào dưới `thien-skill-creative-diagram/`; tạo gallery HTML; build/rebuild ZIP; sửa `dist/`; thay golden/benchmark/license/logo/release; commit, push, tag hoặc tạo/sửa Release.

**Deliverable:** dưới `evidence/p16/`: factual manifest `UPSTREAM-DELTA.json`; 16-row capability/provenance matrix; exact 170-path whole-repository delta ledger plus 74-path skill-subset analysis; official platform revalidation; exact request/IR/product-test/pilot candidate; byte-bound `G02-1.5.0-CONTRACT-MANIFEST.json`; remediation/review/verification records. Các governance/handoff candidate được cập nhật tại đúng file root `PROJECT-CONTRACT.md`, `PLAN.md`, `PHASE-GATES.md`, `ROADMAP.md`, `HANDOFF-CURRENT.md`.

**Verification:**

- exact upstream `main` trỏ tới commit đã ghi và snapshot file hashes khớp;
- `27 + 12 = 39`; bốn capability mới có parent và không bị đếm thành type;
- 12 canonical addition + bốn capability có requirement → exact abstract source/hash → independent implementation plan → stable test family;
- toàn bộ 170 changed upstream path khớp exact Git diff và được disposition; subset 74 skill path/96 ngoài skill cùng cross-cutting import/output/motion/pattern delta không tạo scope ngầm;
- request/IR 1.5 schema hợp lệ, có 39 type; Sankey amount/unit, Bubble x/y/size, Treemap hierarchy totals, Ridgeline transformation, Story-map unassigned và DB index structure có binding trực tiếp; numeric/unit/geometry/boundary policy cùng stable test IDs đã khóa; P-02 inheritance + P-16 delta được hash-bound;
- platform matrix được revalidate từ official docs nhưng không có support-status promotion;
- exact 12-family/36-HTML pilot contract và rubric inheritance được khóa để owner xét, chưa tạo gallery;
- target/version/name/gallery boundary khớp D-041–D-047;
- runtime canonical aggregate, 82 runtime file và aggregate của `dist/` giữ nguyên trước/sau P-16;
- không có HTML/gallery/runtime/package/release artifact mới ngoài evidence/governance scope;
- owner và technical reviewer chưa được thay thế bằng self-approval.

**Gate đóng góp:** G-01@1.5.0 và G-02@1.5.0.  
**Trạng thái hiện tại:** `passed` theo D-047 ngày 2026-08-23; remediation và independent agent re-review hoàn tất với zero open finding, owner phê duyệt `G-01@1.5.0`/`G-02@1.5.0` `PASS` và cho phép đóng P-16. P-17 sau đó đã được phép riêng theo D-048 và hoàn tất.

## P-17 — Semantic expansion to 39 types

**Mục tiêu:** mở rộng canonical source từ 27 lên 39 type và implement contract cho `Dumbbell`, `Slopegraph`, `Ridgeline`, `Bubble` mà chưa nhân rộng gallery.

**Dependency:** P-16 `passed`, G-01@1.5.0 và G-02@1.5.0 `PASS`, cùng authorization riêng.

**Workstream đã hoàn tất:**

1. Cập nhật một canonical taxonomy/router/IR/schema duy nhất cho 12 type mới.
2. Tạo semantic grammar/reference nguyên bản và validator/test mapping cho 12 type cùng bốn capability mới.
3. Giữ numeric/date/category integrity đặc thù: polar radius, treemap area, Sankey flow conservation, bubble area, dumbbell shared scale, slopegraph two-state consistency và ridgeline shared domain/amplitude.
4. Mở rộng security, accessibility, Vietnamese, fidelity, coverage registry và mutation tests; giữ mọi regression v1.0.0.
5. Không copy upstream prose/code/formula/template/specimen hoặc dữ liệu ví dụ.

**Deliverable:** source/reference/schema/test update cho 39 canonical type và bốn capability, chưa có full gallery.

**Verification:** 39/39 grammar/router/schema coverage; bốn capability có parent/disposition/test riêng; 148/148 full regression và 20/20 focused P-17 test `PASS`; v1.0.0 golden, legal, brand, package và release artifact không đổi. Evidence: `evidence/p17/P-17-EVIDENCE.md`, SHA-256 `506cbd0603f38f90200c807d1c14a4ef554bba05583ea0bef582f537f3a4890b`.

**Gate đóng góp:** chỉ G-04@1.5.0 readiness. G-02@1.5.0 phải được khóa và duyệt xong trong P-16 trước khi phase này có thể bắt đầu.  
**Trạng thái:** `passed` ngày 2026-08-23 theo D-048. Tại thời điểm đóng P-17, P-18/P-19 chưa được phép; P-18 sau đó được phép riêng theo D-049.

## P-18 — Visual vNext pilot & gallery approval

**Mục tiêu:** chứng minh visual quality v1.5.0 bằng HTML gallery nguyên bản trước khi mở rộng renderer/gallery ra toàn bộ inventory.

**Dependency:** P-17 `passed` và authorization riêng.

**Pilot contract đã được owner duyệt tại G-02@1.5.0 và được phép triển khai riêng theo D-049:**

Exact case/data/assertion/rubric nằm duy nhất tại `evidence/p16/PILOT-GALLERY-CONTRACT.md` và được duyệt theo D-047; danh sách dưới đây chỉ là summary, không phải nguồn quyết định song song.

- tám canonical family đại diện: Architecture, Swimlane, Sankey, Treemap, Wardley map, Deployment, User journey và Fishbone;
- bốn capability mới: Dumbbell, Slopegraph, Ridgeline và Bubble;
- ba mode `neutral-light`, `neutral-dark`, `editorial` cho mỗi family, tức 36 standalone HTML candidate, cộng một `index.html`/contact sheet không tính là specimen;
- scenario/data/prose/layout/CSS/SVG nguyên bản; gồm benchmark tiếng Việt, connector-heavy, quantitative, strategic, technical và human-experience cases.

**Workstream remediation lịch sử theo D-050:**

1. `P-18R0` — amend design contract, acceptance rubric và candidate lineage; không đổi exact case/data matrix.
2. `P-18R1` — xây renderer foundation, semantic primitives, measured text, connector routing/anchor/bridge và chứng minh trên Architecture, Swimlane, Sankey; khóa `neutral-light` trước khi derive hai mode còn lại.
3. `P-18R2` — tái sinh exact 12 family × ba mode = 36 standalone HTML cùng index/contact sheets; không dùng anchor proof để tăng specimen count.
4. `P-18R3` — lặp semantic/quantitative/security/geometry/browser/regression QA, chấm visual-craft độc lập, chạy blind silhouette và five-second takeaway review, freeze replacement manifest để owner duyệt.

P-18R0→P-18R3 đã hoàn tất về mặt kỹ thuật, nhưng owner từ chối replacement visual direction theo D-051. Kết quả/score cũ chỉ là historical evidence và không đáp ứng owner-approval condition của G-03@1.5.0.

**Structural remediation sequence đã khóa theo D-051/D-052:**

1. `P-18R4` — relock contract và visual foundation cho toàn bộ 39 canonical type + bốn capability: typography precedence/default, real-font measurement, intrinsic sizing, content-fit artboard, 14 layout engine, primitive/node/interface contract, obstacle-aware connector routing và QA protocol. Exact contract nằm tại `evidence/p18/P-18R4-VISUAL-FOUNDATION-CONTRACT.md` và machine binding cùng basename `.json`.
2. `P-18R5` — implement canonical visual kernel và một Swimlane `neutral-light` anchor; review-01/review-02/review-03 được bảo toàn lịch sử, exact review-04 đã frozen sau khi sửa continuity giữa straight shoulder và shared-geometry hop theo D-057, được owner phê duyệt và phase `passed` theo D-058.
3. `P-18R6` — implement 14-engine `neutral-light` anchor gallery; review-01→review-16 được bảo toàn lịch sử byte-bound. Exact review-17 đã frozen theo D-076 sau remediation five-second cho hierarchy/Sankey; static/browser/regression, masked recognition, five-second và independent visual-craft đều `PASS`. Owner phê duyệt exact review-17 và `G-03@1.5.0 PASS` theo D-077; P-18 đã đóng.
4. `P-19A` — 39+4 type/capability adapters, đã hoàn tất theo D-078; `P-19B` — remediation theo D-084–D-106 đang `in-progress`, kết hợp 14 P-18 anchor với 90 P-19 HTML sau owner rejection của candidate đầu; `P-19C` — full QA/freeze/owner review, chưa được phép và vẫn cần authorization riêng.

**P-18R4 verification:** exactly 14 engine assignments cover 39 unique canonical type + four unique capability; eventual count `39×3 + 4×3 = 129`; default font direction and explicit-user-font precedence are machine-bound; retired foundation choices and no-global-transform/no-shrink/no-silent-font-substitution rules are explicit; governance/handoff agree that only P-18R4 was authorized; no runtime/renderer/gallery/package/`dist/`/Git/release mutation.

**Future candidate verification:** zero hard failure; all inherited technical gates `PASS`; real requested/default font and glyph/containment checks `PASS`; visual-craft ≥85/100 and no dimension below 4/5; masked blind review and uncontaminated five-second review `PASS`; exact manifest owner-approved before P-19.

**Gate đóng góp:** G-03@1.5.0.  
**Trạng thái:** P-18 `passed` ngày 2026-08-27 theo D-077. P-18R4 `passed` theo D-053; exact P-18R5 review-04 được owner phê duyệt và P-18R5 `passed` theo D-058. Review-16 manifest SHA-256 `abdc0e9d7413b65f715c12a535b12abfaf33793e97f8f221e70a8d3ac58cc835` được archive byte-bound trước D-076 remediation. Exact review-17 `P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0`, manifest SHA-256 `7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a`, đạt toàn bộ technical/independent gate và được owner phê duyệt; `G-03@1.5.0 PASS`. D-078 đóng P-19A; D-079 candidate đầu của P-19B là historical technical PASS nhưng đã bị owner bác bỏ về hướng thiết kế theo D-080. Active P-19B successor đang `in-progress` chờ owner visual review; P-19C chưa được phép.

## P-19 — Full 39-type source/gallery coverage

**Mục tiêu:** nhân visual implementation đã duyệt ra toàn bộ target và bàn giao full HTML gallery để owner duyệt, vẫn dừng trước packaging/release.

**Dependency:** P-18 `passed`, G-03@1.5.0 `PASS`, cùng authorization riêng.

**Workstream chia theo D-051/D-078:**

1. `P-19A` — `passed`: hoàn thiện type/capability adapters cho đủ 39 canonical type và bốn capability mới trên foundation đã được owner duyệt. Canonical module `scripts/visual_adapters_v15.py`, generated registry `references/visual-adapters-v15.json`, exact 43 plan hashes và evidence nằm tại `evidence/p19/`; focused `14/14 PASS`, full regression `162/162 PASS`, zero HTML/SVG/CSS.
2. `P-19B` — remediation `in-progress` theo D-084–D-118: dùng trực tiếp 14 exact P-18R6 review-17 anchor, không tái sinh duplicate; 25 canonical type, bốn capability và hai presentation variant `layers`/`scatter-chart` có ba mode, tổng 93 HTML/31 preview. Active review-38 giữ toàn bộ remediation trước và sửa riêng connector continuity của `process`; comparison có 107 diagram, 90 non-target HTML/30 preview được bảo toàn.
3. `P-19C`: chạy full semantic, typography/glyph/containment, geometry, accessibility, quantitative, security, determinism, pairwise và regression checks; thực hiện masked visual review.
4. So sánh visual quality bằng rubric đã được owner duyệt, không bằng pixel similarity với upstream.
5. Freeze exact source/gallery candidate bằng manifest/hash cho owner review; không build package.

**Verification dự kiến:** theo D-085/D-095–D-118, union 14 P-18 canonical + 25 P-19 canonical phải đúng 39 và không trùng; P-19 có 75 canonical + 12 capability + 3 `layers` + 3 `scatter-chart` variant HTML, 31 preview, đủ ba mode cho 31 identity. Đủ 93 SVG phải khai báo D-105; mọi detailed artifact D-086–D-117 phải được giữ. `Process` phải giữ đúng năm loại ô/11 node/11 directed route, gồm 9 straight + 2 symmetric rounded-orthogonal merge route; 5 document-bound connector chạm visible boundary, hai inlet x=920/1080, exact node/edge table và geometry ba mode. Radar/scatter-chart/Treemap contract trước vẫn giữ. P-18 phải giữ exact bytes/hash ở neutral-light, không claim ba-mode coverage cho 14 anchor này. Kiểm absence of withdrawn files, links, deterministic generation, retained artwork và recoverable custody; owner vẫn phải duyệt exact current gallery.

**Checkpoint D-081:** exact `P19B-P18-INHERITED-THREE-MODE-REVIEW-02-1.5.0`, gallery manifest SHA-256 `6bd265fbfe1bb06b7d2d15ea1f432b3282e03efa838b8ce10773b09025046df1`. Focused `24/24`, static `29/29`, regression `186/186`, sáu target mode geometry và ba straight proof đạt; chín local SVG raster đã inspect đúng hai lỗi. Review-01 archive `199/199`, protected corpus `1954/1954` hash khớp; 123 non-target HTML chỉ đổi candidate ID, 41 non-target preview SVG byte-identical. Browser vẫn `blocked / not executable`; không mang forward broad visual PASS của review-01 sau khi owner chỉ ra hai lỗi bị bỏ sót. P-19B giữ `in-progress`, chưa owner-approved. Evidence chi tiết: `evidence/p19/P-19B-EVIDENCE.md` và `evidence/p19/P-19B-REVIEW-02-VERIFICATION.json`.

**Gate đóng góp:** G-04@1.5.0.  
**Trạng thái:** P-19 `in-progress`; P-19A `passed` theo D-078; P-19B remediation `in-progress` theo D-080, candidate đầu theo D-079 là historical owner-rejected visual direction; P-19C `not-started`, chưa được phép. G-04@1.5.0 vẫn `NOT-EVALUATED`; G-05/G-06/G-07@1.5.0 và mọi packaging/release phase nằm ngoài current scope.

**Checkpoint D-082:** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0`; Gantt-only three-mode remediation, 38/38 focused tests, 29/29 static checks, 200/200 canonical regression. Ba local Gantt raster đã inspect; 126 non-Gantt HTML chỉ khác candidate ID, 42 non-Gantt preview byte-identical; 223 archived và 2345 protected files khớp hash. Exact hashes theo `evidence/p19/P-19B-PLAN-MANIFEST.json` và `P-19B-SOURCE-MANIFEST.json`; chi tiết `P-19B-REVIEW-03-VERIFICATION.json`. Browser vẫn blocked; owner approval pending, P-19C unauthorized, G-04 chưa đánh giá.

**Checkpoint D-083:** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-04-1.5.0`; 52/52 focused tests, 29/29 static checks, 214/214 regression; ba local flywheel raster đã inspect. 126 non-target HTML chỉ khác candidate ID, 42 non-target preview byte-identical, gồm Gantt. Archive 238 files và protected corpus 2569 files khớp hash. Exact hashes theo plan/source manifests; chi tiết `evidence/p19/P-19B-REVIEW-04-VERIFICATION.json`. Browser vẫn blocked, owner approval pending; P-19C unauthorized và G-04 NOT-EVALUATED.

**Checkpoint D-084/D-085:** active candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-05-1.5.0`. 42 duplicate HTML và 14 preview đã chuyển vào `evidence/p19/withdrawn/review05-duplicates/`, có receipt để khôi phục. Exact review-04 được archive 253 files; 2808 protected hashes khớp. P-19 còn 87 HTML/29 preview; 87 HTML chỉ đổi candidate ID, 29 preview byte-identical. Dùng trực tiếp 14 P-18 anchor pairs theo hash gốc. Focused static 32/32, scope tests 8/8; chi tiết `evidence/p19/P-19B-REVIEW-05-VERIFICATION.json`. Exact hashes tại active plan/source manifests. Browser blocked; owner approval pending, P-19C unauthorized, G-04 NOT-EVALUATED.

**Checkpoint D-086:** active candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0`. Review-05 đã archive 207 files; protected corpus 3128 files khớp hash. Chỉ 3 Fishbone HTML và preview Fishbone thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. Fishbone có đúng 5 nhóm/10 nguyên nhân/1 hệ quả, alternating bones, continuous tick→bone→spine→effect geometry, đủ semantic table và bất biến hình học qua ba mode. Focused renderer/Fishbone/Gantt/Flywheel tests 60/60, gallery-scope 8/8, static 32/32 và full regression 222/222; local neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-06-VERIFICATION.json`; browser vẫn blocked, owner approval pending, P-19C unauthorized, G-04 NOT-EVALUATED.

**Checkpoint D-087 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-07-1.5.0`. Review-06 đã archive 216 files; protected corpus 3336 files khớp hash. Chỉ 3 dp-integration HTML và preview dp-integration thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. DP integration có đúng 11 node/11 directed edge/1 platform group, core containment, source/consumer fan-in/out, continuous routes, semantic table và geometry bất biến ba mode. Focused tests 68/68, gallery-scope 8/8, static 32/32 và full regression 230/230; ba local raster đã inspect và sửa clipping trước PASS. Chi tiết `evidence/p19/P-19B-REVIEW-07-VERIFICATION.json`; browser vẫn blocked; candidate này đã chuyển historical trước D-088.

**Checkpoint D-088 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-08-1.5.0`. Review-07 đã archive 230 files; protected corpus 3553 files khớp hash. Chỉ 3 bar-chart HTML và preview bar-chart thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. Bar chart có đúng 8 bar/2 axis/6 tick/1 focal, zero-baseline 0–120, direct labels, redundant record-high legend/table encoding và geometry bất biến ba mode. Focused tests 75/75, gallery-scope 8/8, static 32/32 và full regression 237/237; ba local raster đã inspect trước PASS. Chi tiết `evidence/p19/P-19B-REVIEW-08-VERIFICATION.json`; candidate này đã chuyển historical trước D-089.

**Checkpoint D-089 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-09-1.5.0`. Review-08 đã archive 244 files; protected corpus 3784 files khớp hash. Chỉ 3 dp-security-matrix HTML và preview dp-security-matrix thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. Security matrix có đúng 25 cell/5 role/5 component/1 focal partner-BI boundary, direct Admin/Write/Read/None labels, codes, legend, exact alternative table và geometry bất biến ba mode. Focused tests 82/82, gallery-scope 8/8, static 32/32 và full regression 244/244; ba local raster đã inspect trước PASS. Chi tiết `evidence/p19/P-19B-REVIEW-09-VERIFICATION.json`; candidate này đã chuyển historical trước D-090.

**Checkpoint D-090 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-10-1.5.0`. Review-09 đã archive 258 files; protected corpus 4029 files khớp hash. Chỉ 3 er-data-model HTML và preview er-data-model thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. ER data model có đúng 4 entity/19 member/3 relationship/1 aggregate root/1 associative entity, direct PK/FK/cardinality labels, legend, exact alternative table và geometry bất biến ba mode. Focused 89/89, gallery-scope 8/8, static 32/32 và full regression 251/251 PASS; candidate này đã chuyển historical trước D-091.

**Checkpoint D-091:** active candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-11-1.5.0`. Review-10 đã archive 272 files; protected corpus 4288 files khớp hash. Chỉ 3 er-data-model HTML và preview er-data-model thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. Sáu cardinality nằm inline trên connector axis sát endpoint, có sáu canvas knockout đúng P-18 padding/binding; D-090 model và geometry ba mode được giữ. Focused 90/90, scope 8/8, static 32/32 và full regression 252/252 PASS; ba raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-11-VERIFICATION.json`; browser blocked, owner approval pending, P-19C unauthorized, G-04 NOT-EVALUATED.

**Checkpoint D-118:** active candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-38-1.5.0`. Exact review-37 đã archive 575 files; protected corpus 15788 files khớp hash. `Process` giữ 11 node/11 edge và năm loại ô; 5 connector document-bound chạm visible boundary, hai merge route đối xứng dùng rounded-orthogonal `Q` corner + dedicated arrowhead, chín route còn lại thẳng. Giữ 90 non-target HTML/30 preview; tổng vẫn 93/31 và comparison 107. Focused 11/11, scope 8/8, static 34/34, full regression 394/394 và exact review verification PASS; neutral-light raster đã inspect. Owner approval pending, P-19C unauthorized, G-04 NOT-EVALUATED.

**Checkpoint D-117 (historical):** candidate review-37 five-shape process đã archive trước connector-continuity repair D-118.

**Checkpoint D-116 (historical):** candidate review-36 marker-free radar đã archive trước detailed-process correction D-117.

**Checkpoint D-115 (historical):** candidate review-35 solid-line radar đã archive trước marker-free correction D-116.

**Checkpoint D-114 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-34-1.5.0`; detailed radar dùng dashed comparison profiles đã bị owner yêu cầu sửa tại D-115. Candidate đã archive trước review-35.

**Checkpoint D-113 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-33-1.5.0`; scatter-chart addition PASS. Candidate đã chuyển historical trước D-114.

**Checkpoint D-112 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-32-1.5.0`; thin-stroke Treemap PASS. Candidate đã chuyển historical trước D-113.

**Checkpoint D-111 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-31-1.5.0`; detailed sequence PASS. Candidate đã chuyển historical trước D-112 theo yêu cầu giảm viền `treemap`.

**Checkpoint D-110 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-30-1.5.0`; detailed state machine PASS. Candidate đã chuyển historical trước D-111 theo yêu cầu thay `sequence`.

**Checkpoint D-109 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-29-1.5.0`; detailed story map PASS. Candidate đã chuyển historical trước D-110 theo yêu cầu thay `state-machine`.

**Checkpoint D-108 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-28-1.5.0`; ultra-thin centered tree pass. Candidate đã chuyển historical trước D-109 theo yêu cầu thay `story-map`.

**Checkpoint D-107 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-27-1.5.0`; first thin-stroke pass. Candidate đã chuyển historical trước D-108 vì owner xác định vẫn còn đậm.

**Checkpoint D-106 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-26-1.5.0`. Tree có 9 node/8 relation/3 tầng/14 straight connector primitive; root và bốn parent đúng midpoint child span, branch interval `640/640`, two-child offset `−150/+150`, single-child direct centered. Candidate đã chuyển historical trước D-107.

**Checkpoint D-105 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-25-1.5.0`. Review-24 đã archive 440 files; protected corpus 9253 files khớp hash. Đủ 90 P-19 SVG khai báo policy `D-105-centered-even-straight-first`. UML proof có dependency đơn vào exact center, hai realization port chia cạnh interface thành ba khoảng `360/360/360`, bốn straight relation và một documented rounded-orthogonal exception. Candidate đã chuyển historical trước D-106.

**Checkpoint D-104 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-24-1.5.0`. Review-23 đã archive 428 files; protected corpus 8824 files khớp hash. Chỉ 3 UML-class HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. UML-class có đúng 7 container/17 member/5 continuous relationship; kind mix 1 dependency, 2 realization, 1 composition, 1 association; 4 cardinality inline, one rounded association route và legend đủ 6 loại. Focused 183/183, scope 8/8, static 34/34 và full regression 345/345 PASS; candidate đã chuyển historical trước D-105.

**Checkpoint D-103 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-23-1.5.0`. Review-22 đã archive 419 files; protected corpus 8404 files khớp hash. Chỉ 3 Treemap HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Treemap giữ đúng 6 leaf/6 exact allocation-area tile; sáu visible rectangle inset 4 unit ở đủ bốn cạnh nên mọi shared boundary có real gap 8 unit và mọi outline hiện đủ. Focused 176/176, scope 8/8, static 34/34 và full regression 338/338 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-23-VERIFICATION.json`; candidate đã chuyển historical trước D-104.

**Checkpoint D-102 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-22-1.5.0`. Review-21 đã archive 410 files; protected corpus 7993 files khớp hash. Chỉ 3 Treemap HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Treemap giữ đúng 6 leaf/6 exact-area tile và có 6 visible outline/6 separation gutter ở cả ba mode; focal coral outline, compact label, legend và exact table vẫn nguyên. Focused 175/175, scope 8/8, static 34/34 và full regression 337/337 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-22-VERIFICATION.json`; candidate đã chuyển historical trước D-103.

**Checkpoint D-101 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-21-1.5.0`. Review-20 đã archive 398 files; protected corpus 7594 files khớp hash. Chỉ 3 Treemap HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Treemap có đúng 6 leaf/6 exact-area tile, exact hierarchy total, một focal tile, một compact-label tile, direct/legend/table redundancy và geometry ba mode. Focused 174/174, scope 8/8, static 34/34 và full regression 336/336 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-21-VERIFICATION.json`; candidate đã chuyển historical trước D-102.

**Checkpoint D-100 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-20-1.5.0`. Review-19 đã archive 386 files; protected corpus 7207 files khớp hash. Chỉ 3 Venn HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Venn có đúng 3 equal-radius set/4 member/1 exact nested-clipped triple intersection, lower-pair geometry cân đối, direct set/core labels, exact membership table và geometry ba mode. Focused 166/166, scope 8/8, static 34/34 và full regression 328/328 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-20-VERIFICATION.json`; candidate đã chuyển historical trước D-101.

**Checkpoint D-099 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-19-1.5.0`. Review-18 đã archive 374 files; protected corpus 6832 files khớp hash. Chỉ 3 wardley-map HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Wardley map có đúng 8 component/9 dependency/2 normalized axis/4 stage/3 boundary/1 evolving component, arrow-free axis/dependency, một dashed evolution arrow, direct labels, exact component/dependency table và geometry ba mode. Focused 158/158, scope 8/8, static 34/34 và full regression 320/320 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-19-VERIFICATION.json`; candidate đã chuyển historical trước D-100.

**Checkpoint D-098 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-18-1.5.0`. Review-17 đã archive 362 files; protected corpus 6469 files khớp hash. Chỉ 3 polar-chart HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Polar chart có đúng 1 series/8 UTC window/8 common-origin spoke/8 endpoint/5 radial ring/1 unique peak, arrow-free proportional geometry, non-color peak redundancy, exact eight-window table và geometry ba mode. Focused 149/149, scope 8/8, static 34/34 và full regression 311/311 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-18-VERIFICATION.json`; candidate đã chuyển historical trước D-099.

**Checkpoint D-097 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-17-1.5.0`. Review-16 đã archive 350 files; protected corpus 6118 files khớp hash. Chỉ 3 medallion HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Medallion có đúng 5 stage/4 continuous directed promotion/2 processing path/1 focal/1 archive, per-stage tool/format/writer/examples, non-color state redundancy, exact five-stage table và geometry ba mode. Focused 140/140, scope 8/8, static 34/34 và full regression 302/302 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-17-VERIFICATION.json`; candidate đã chuyển historical trước D-098.

**Checkpoint D-096 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-16-1.5.0`. Review-15 đã archive 338 files; protected corpus 5779 files khớp hash. Chỉ 3 line-chart HTML và một preview thay artwork; 87 non-target HTML giữ nguyên sau candidate-ID normalization, 29 non-target preview byte-identical. Line chart có đúng 3 series/24 điểm/2 arrow-free axis/6 tick/1 focal area, non-color line+marker redundancy, direct endpoint labels, exact 24-value table và geometry ba mode. Focused 132/132, scope 8/8, static 34/34 và full regression 294/294 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-16-VERIFICATION.json`; candidate đã chuyển historical trước D-097.

**Checkpoint D-095 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-15-1.5.0`. Review-14 đã archive 322 files; protected corpus 5456 files khớp hash. Thêm đúng 3 Layers HTML và một preview; 87 prior HTML giữ nguyên sau candidate-ID normalization, 29 prior preview byte-identical. Layers có đúng 5 dải L5→L1, một abstraction axis, một focal layer được encode bằng coral boundary/fill + nhãn `TRỌNG TÂM` + note chữ, exact alternative table và geometry ba mode được giữ. Focused 124/124, scope 8/8, static 34/34 và full regression 286/286 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-15-VERIFICATION.json`; candidate đã chuyển historical trước D-096.

**Checkpoint D-094 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-14-1.5.0`. Review-13 đã archive 311 files; protected corpus 5143 files khớp hash. Chỉ 3 Kanban HTML và preview Kanban thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. Kanban có đúng 4 cột/11 item theo 3/4/2/2, một WIP breach `4/3`, một blocked, một waiting-external và hai done; state có non-color encoding, card containment và exact alternative table; geometry ba mode được giữ. Focused 116/116, scope 8/8, static 32/32 và full regression 278/278 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-14-VERIFICATION.json`; candidate đã chuyển historical trước D-095.

**Checkpoint D-093 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-13-1.5.0`. Review-12 đã archive 297 files; protected corpus 4845 files khớp hash. Chỉ 3 it-current-state HTML và preview it-current-state thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. It-current-state có đúng 9 node/8 directed edge/3 boundary group, 8 direct format label, 2 bottleneck, 2 pain path và 2 external path; mỗi connector là một path liên tục, mọi bend 90° dùng rounded join theo mặc định và straight chỉ qua explicit override; geometry ba mode được giữ. Focused 108/108, scope 8/8, static 32/32 và full regression 270/270 PASS; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-13-VERIFICATION.json`; candidate đã chuyển historical trước D-094.

**Checkpoint D-092 (historical):** candidate `P19B-P18-INHERITED-THREE-MODE-REVIEW-12-1.5.0`. Review-11 đã archive 283 files; protected corpus 4561 files khớp hash. Chỉ 3 high-level HTML và preview high-level thay artwork; 84 non-target HTML giữ nguyên sau candidate-ID normalization, 28 non-target preview byte-identical. High-level có đúng 11 node/13 directed edge/2 boundary group; cả 13 connector là một path liên tục, mọi bend 90° dùng quadratic rounded join theo mặc định và straight chỉ qua explicit override; geometry ba mode được giữ. Focused 99/99, scope 8/8, static 32/32 và full regression 261/261 PASS sau transient-cache cleanup; neutral-light raster đã inspect. Chi tiết `evidence/p19/P-19B-REVIEW-12-VERIFICATION.json`; candidate đã chuyển historical trước D-093.

## 3. Change-control record

Khi có quyết định mới:

1. Ghi chỉ dẫn nguyên văn/tóm tắt có kiểm chứng.
2. Cập nhật decision ID trong `PROJECT-CONTRACT.md`.
3. Cập nhật task/status trong file này nếu cần.
4. Cập nhật gate chỉ khi tiêu chí phê duyệt thật sự thay đổi.
5. Không sửa `ROADMAP.md` trừ khi quan hệ milestone thay đổi.

Không có câu hỏi mở nào chặn P-00. Các quyết định hoãn đã được liệt kê tại mục 13 của `PROJECT-CONTRACT.md` và phải được hỏi ở phase tương ứng.
