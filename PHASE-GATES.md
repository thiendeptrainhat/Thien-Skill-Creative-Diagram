# Phase gates — Thien-Skill-Creative-Diagram

File này là nguồn sự thật duy nhất cho tiêu chí `PASS / FAIL / DEFERRED` của milestone và phát hành. Dependency, authorization, exit criteria và trạng thái của từng phase nằm trong `PLAN.md`.

Gate assertion là cách kiểm chứng tối thiểu cho các quyết định trong `PROJECT-CONTRACT.md`, không phải nguồn yêu cầu sản phẩm thay thế. Các nhóm chính truy về D-004–D-009 (nguồn/phạm vi/sản phẩm), D-010–D-012 (package), D-013–D-018 và D-021 (brand/legal), D-019–D-020 (benchmark).

## 1. Quy tắc chung

- Trạng thái gate chỉ có `NOT-EVALUATED`, `PASS`, `FAIL` hoặc `DEFERRED`. `NOT-EVALUATED` chỉ nghĩa là gate chưa được xét và không cho phép vượt gate.
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

- ghi commit/tag và ngày snapshot của `diagram-design`;
- kiểm đủ 27 canonical type và phân loại riêng variant/specimen/pattern/import/motion;
- lập capability matrix: yêu cầu → nguồn trừu tượng → implementation độc lập dự kiến → test;
- ghi snapshot `Thien-UI-UX-Ultra` và chỉ rõ principle nào được dùng;
- có source/provenance ledger và quy tắc sinh/đối chiếu notice từ một manifest;
- xác minh lại quy cách Claude, OpenAI/ChatGPT và Agent Skills từ tài liệu chính thức hiện hành;
- lập inventory surface và bằng chứng chính thức đủ để P-02 khóa surface matrix, không tự tuyên bố tương thích.

Blocking failure:

- dùng số 29 để tự tạo thêm type;
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

Blocking failure:

- bắt đầu nhân rộng 27 type khi chưa có semantic/visual/test contract;
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

Hard checks cho benchmark swimlane:

- lane/actor và grouped ownership header đúng;
- shape ngữ nghĩa cho tiền/séc, chứng từ, bảng kê và tệp lưu;
- step number/handoff có thể truy vết độc lập;
- connector không xuyên node không liên quan, không sai nguồn–đích;
- legend nhất quán;
- tiếng Việt giữ đúng dấu;
- không clipping, overlap hoặc nén chữ để che complexity;
- output là thiết kế nguyên bản, không pixel-clone ảnh tham chiếu.

Blocking failure:

- chủ sở hữu chưa duyệt visual direction/golden;
- renderer chỉ đẹp ở một case hard-code;
- semantic sai nhưng được chấp nhận vì hình đẹp.

Người duyệt: chủ sở hữu đối với golden; technical/QA reviewer đối với hard checks.

## G-04 — Functional completeness và quality

**Mục đích:** chứng minh toàn bộ phạm vi v1.0.0 hoạt động đáng tin cậy.

### Coverage bắt buộc

- 27/27 canonical type qua semantic và render checks.
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

### Geometry/render hard checks

- SVG/HTML hợp lệ; nội dung nằm trong viewBox/canvas.
- Không clipping, unintended overlap, duplicate ID hoặc phần tử ngoài canvas.
- Connector đúng endpoint, route rõ, không che label/node; crossing được tránh hoặc thể hiện có chủ đích.
- DOM/read order khớp narrative order.
- Font fallback hiển thị đúng tiếng Việt.
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

- Claude plugin ZIP, OpenAI/ChatGPT plugin ZIP và Universal raw skill ZIP cùng version `1.0.0`;
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

- G-00 đến G-06 đều `PASS`;
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
