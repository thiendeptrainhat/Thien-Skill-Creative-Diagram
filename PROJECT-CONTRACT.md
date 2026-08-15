# Hợp đồng dự án — Thien-Skill-Creative-Diagram

**Mã tài liệu:** PC-001  
**Phiên bản tài liệu:** 1.4  
**Ngày khóa kế hoạch:** 2026-08-15  
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
Phiên bản phát hành đầu tiên dự kiến: `1.0.0`

## 3. Nguồn chức năng chủ đạo

Nguồn chính: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design).

Snapshot cụ thể phải được khóa ở Phase P-01 trước khi triển khai. Tại thời điểm lập kế hoạch, taxonomy chuẩn được hiểu là 27 visual type từ `SKILL.md` và các type reference của upstream; con số 29 trong phần mô tả repository không được dùng để tự suy ra thêm hai type.

### 3.1. 27 visual type bắt buộc

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

Nguồn logo do chủ sở hữu cung cấp: `<OWNER_ASSET_SOURCE>/Logo TDTN.png`.

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

`<OWNER_LICENSE_TEMPLATE_SOURCE>/Tran-Ngoc-Thiens-Skills-Commercial-Source-Available-License-2.0.md`

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

Không thay đổi mục `LOCKED` nếu chưa có quyết định mới, rõ ràng của chủ sở hữu.

## 13. Quyết định được hoãn đến đúng phase

Các điểm sau không chặn phase tài liệu hiện tại và không được tự giả định khi đến phase liên quan:

- commit/tag upstream chính xác dùng làm snapshot;
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
